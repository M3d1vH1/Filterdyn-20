from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_babel import _, get_locale
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from models import User, Customer, Product, ProductCategory, Quote, QuoteItem, Order, OrderItem, Task, TaskBoard, TaskBoardMember, TaskColumn, TaskCard, TaskComment
from app import db
from forms import CustomerForm, ProductForm, ProductCategoryForm, QuoteForm, OrderForm, TaskForm, TaskBoardForm, TaskCardForm
from utils import admin_required, manager_required, generate_pdf_quote
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/ai')
@login_required
@admin_required
def ai_assistant():
    """AI Assistant main interface"""
    # Get customers for email generation
    customers = Customer.query.filter_by(tenant_id=current_user.tenant_id).order_by(Customer.name).all()
    return render_template('ai_assistant/assistant.html', customers=customers)



@main_bp.route('/')
@login_required
def dashboard():
    # Get dashboard statistics
    stats = {}

    # Tasks
    my_tasks = Task.query.filter_by(
        tenant_id=current_user.tenant_id,
        assigned_to=current_user.id,
        status='pending'
    ).order_by(Task.due_date.asc()).limit(5).all()

    overdue_tasks = Task.query.filter(
        Task.tenant_id == current_user.tenant_id,
        Task.assigned_to == current_user.id,
        Task.status == 'pending',
        Task.due_date < datetime.now(timezone.utc)
    ).count()

    # Quotes
    pending_quotes = Quote.query.filter_by(
        tenant_id=current_user.tenant_id,
        status='pending_approval'
    ).count()

    active_quotes = Quote.query.filter(
        Quote.tenant_id == current_user.tenant_id,
        Quote.status.in_(['draft', 'pending_approval', 'approved', 'sent'])
    ).count()

    # Orders
    pending_orders = Order.query.filter_by(
        tenant_id=current_user.tenant_id,
        status='pending'
    ).count()

    # Recent activity
    recent_quotes = Quote.query.filter_by(
        tenant_id=current_user.tenant_id
    ).order_by(Quote.created_at.desc()).limit(5).all()

    recent_orders = Order.query.filter_by(
        tenant_id=current_user.tenant_id
    ).order_by(Order.created_at.desc()).limit(5).all()

    stats = {
        'my_tasks': my_tasks,
        'overdue_tasks': overdue_tasks,
        'pending_quotes': pending_quotes,
        'active_quotes': active_quotes,
        'pending_orders': pending_orders,
        'recent_quotes': recent_quotes,
        'recent_orders': recent_orders
    }

    return render_template('dashboard.html', stats=stats)

# Customer routes
@main_bp.route('/customers')
@login_required
def customers():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    query = Customer.query.filter_by(tenant_id=current_user.tenant_id)

    if search:
        query = query.filter(
            db.or_(
                Customer.name.ilike(f'%{search}%'),
                Customer.contact_person.ilike(f'%{search}%'),
                Customer.email.ilike(f'%{search}%')
            )
        )

    customers = query.order_by(Customer.name.asc()).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template('customers/index.html', customers=customers, search=search)

@main_bp.route('/customers/create', methods=['GET', 'POST'])
@login_required
def create_customer():
    form = CustomerForm()

    if form.validate_on_submit():
        customer = Customer(
            tenant_id=current_user.tenant_id,
            name=form.name.data,
            contact_person=form.contact_person.data,
            email=form.email.data,
            phone=form.phone.data,
            mobile=form.mobile.data,
            address=form.address.data,
            city=form.city.data,
            postal_code=form.postal_code.data,
            country=form.country.data,
            tax_number=form.tax_number.data,
            industry=form.industry.data,
            notes=form.notes.data
        )

        db.session.add(customer)
        db.session.commit()
        flash(_('Customer created successfully'), 'success')
        return redirect(url_for('main.customers'))

    return render_template('customers/edit.html', form=form, customer=None)

@main_bp.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    customer = Customer.query.filter_by(id=customer_id, tenant_id=current_user.tenant_id).first_or_404()
    form = CustomerForm(obj=customer)

    if form.validate_on_submit():
        customer.name = form.name.data
        customer.contact_person = form.contact_person.data
        customer.email = form.email.data
        customer.phone = form.phone.data
        customer.mobile = form.mobile.data
        customer.address = form.address.data
        customer.city = form.city.data
        customer.postal_code = form.postal_code.data
        customer.country = form.country.data
        customer.tax_number = form.tax_number.data
        customer.industry = form.industry.data
        customer.notes = form.notes.data

        db.session.commit()
        flash(_('Customer updated successfully'), 'success')
        return redirect(url_for('main.customers'))

    return render_template('customers/edit.html', form=form, customer=customer)

@main_bp.route('/customers/<int:customer_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_customer(customer_id):
    customer = Customer.query.filter_by(id=customer_id, tenant_id=current_user.tenant_id).first_or_404()

    # Check if customer has quotes or orders
    if customer.quotes or customer.orders:
        flash(_('Cannot delete customer with existing quotes or orders'), 'error')
        return redirect(url_for('main.customers'))

    db.session.delete(customer)
    db.session.commit()
    flash(_('Customer deleted successfully'), 'success')
    return redirect(url_for('main.customers'))

# Product routes
@main_bp.route('/products')
@login_required
def products():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', 0, type=int)
    search = request.args.get('search', '')

    query = Product.query.filter_by(tenant_id=current_user.tenant_id)

    if category_id:
        query = query.filter_by(category_id=category_id)

    if search:
        query = query.filter(
            db.or_(
                Product.code.ilike(f'%{search}%'),
                Product.name_en.ilike(f'%{search}%'),
                Product.name_el.ilike(f'%{search}%')
            )
        )

    products = query.order_by(Product.code.asc()).paginate(
        page=page, per_page=20, error_out=False
    )

    categories = ProductCategory.query.filter_by(tenant_id=current_user.tenant_id).all()

    return render_template('products/index.html', products=products, categories=categories, 
                         selected_category=category_id, search=search)

@main_bp.route('/products/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_product():
    form = ProductForm()
    form.category_id.choices = [
        (c.id, c.name_en if get_locale() == 'en' else c.name_el) 
        for c in ProductCategory.query.filter_by(tenant_id=current_user.tenant_id).all()
    ]

    if form.validate_on_submit():
        product = Product(
            tenant_id=current_user.tenant_id,
            category_id=form.category_id.data,
            code=form.code.data,
            name_en=form.name_en.data,
            name_el=form.name_el.data,
            description_en=form.description_en.data,
            description_el=form.description_el.data,
            unit_price=form.unit_price.data,
            cost_price=form.cost_price.data,
            unit=form.unit.data,
            specifications=json.loads(form.specifications.data) if form.specifications.data else {}
        )

        db.session.add(product)
        db.session.commit()
        flash(_('Product created successfully'), 'success')
        return redirect(url_for('main.products'))

    return render_template('products/edit.html', form=form, product=None)

@main_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.filter_by(id=product_id, tenant_id=current_user.tenant_id).first_or_404()
    form = ProductForm(obj=product)
    form.category_id.choices = [
        (c.id, c.name_en if get_locale() == 'en' else c.name_el) 
        for c in ProductCategory.query.filter_by(tenant_id=current_user.tenant_id).all()
    ]

    if request.method == 'GET':
        form.specifications.data = json.dumps(product.specifications or {}, indent=2)

    if form.validate_on_submit():
        product.category_id = form.category_id.data
        product.code = form.code.data
        product.name_en = form.name_en.data
        product.name_el = form.name_el.data
        product.description_en = form.description_en.data
        product.description_el = form.description_el.data
        product.unit_price = form.unit_price.data
        product.cost_price = form.cost_price.data
        product.unit = form.unit.data
        product.specifications = json.loads(form.specifications.data) if form.specifications.data else {}

        db.session.commit()
        flash(_('Product updated successfully'), 'success')
        return redirect(url_for('main.products'))

    return render_template('products/edit.html', form=form, product=product)

# Quote routes
@main_bp.route('/quotes')
@login_required
def quotes():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    search = request.args.get('search', '')

    query = Quote.query.filter_by(tenant_id=current_user.tenant_id)

    # Filter by user role
    if current_user.role == 'user':
        query = query.filter_by(created_by=current_user.id)

    if status:
        query = query.filter_by(status=status)

    if search:
        query = query.join(Customer).filter(
            db.or_(
                Quote.quote_number.ilike(f'%{search}%'),
                Quote.title.ilike(f'%{search}%'),
                Customer.name.ilike(f'%{search}%')
            )
        )

    quotes = query.order_by(Quote.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template('quotes/index.html', quotes=quotes, status=status, search=search)

@main_bp.route('/quotes/create', methods=['GET', 'POST'])
@login_required
def create_quote():
    form = QuoteForm()
    form.customer_id.choices = [
        (c.id, c.name) for c in Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    ]

    if form.validate_on_submit():
        # Generate quote number
        last_quote = Quote.query.filter_by(tenant_id=current_user.tenant_id).order_by(Quote.id.desc()).first()
        quote_number = f"Q{datetime.now().year}{(last_quote.id + 1) if last_quote else 1:04d}"

        quote = Quote(
            tenant_id=current_user.tenant_id,
            customer_id=form.customer_id.data,
            created_by=current_user.id,
            quote_number=quote_number,
            quote_type=form.quote_type.data,
            title=form.title.data,
            description=form.description.data,
            validity_days=form.validity_days.data,
            delivery_days=form.delivery_days.data,
            payment_terms=form.payment_terms.data,
            tax_rate=form.tax_rate.data
        )

        db.session.add(quote)
        db.session.commit()
        flash(_('Quote created successfully'), 'success')
        return redirect(url_for('main.edit_quote', quote_id=quote.id))

    return render_template('quotes/create.html', form=form)

@main_bp.route('/quotes/<int:quote_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_quote(quote_id):
    quote = Quote.query.filter_by(id=quote_id, tenant_id=current_user.tenant_id).first_or_404()

    # Check permissions
    if current_user.role == 'user' and quote.created_by != current_user.id:
        flash(_('You can only edit your own quotes'), 'error')
        return redirect(url_for('main.quotes'))

    if quote.status in ['approved', 'sent', 'accepted']:
        flash(_('Cannot edit approved or sent quotes'), 'error')
        return redirect(url_for('main.quotes'))

    form = QuoteForm(obj=quote)
    form.customer_id.choices = [
        (c.id, c.name) for c in Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    ]

    if form.validate_on_submit():
        quote.customer_id = form.customer_id.data
        quote.quote_type = form.quote_type.data
        quote.title = form.title.data
        quote.description = form.description.data
        quote.validity_days = form.validity_days.data
        quote.delivery_days = form.delivery_days.data
        quote.payment_terms = form.payment_terms.data
        quote.tax_rate = form.tax_rate.data

        # Recalculate totals
        subtotal = sum(item.line_total for item in quote.items)
        tax_amount = subtotal * (quote.tax_rate / 100)
        total_amount = subtotal + tax_amount

        quote.subtotal = subtotal
        quote.tax_amount = tax_amount
        quote.total_amount = total_amount

        db.session.commit()
        flash(_('Quote updated successfully'), 'success')
        return redirect(url_for('main.quotes'))

    return render_template('quotes/edit.html', form=form, quote=quote)

@main_bp.route('/quotes/<int:quote_id>/submit', methods=['POST'])
@login_required
def submit_quote(quote_id):
    quote = Quote.query.filter_by(id=quote_id, tenant_id=current_user.tenant_id).first_or_404()

    # Check permissions
    if current_user.role == 'user' and quote.created_by != current_user.id:
        flash(_('You can only submit your own quotes'), 'error')
        return redirect(url_for('main.quotes'))

    if quote.status != 'draft':
        flash(_('Quote is not in draft status'), 'error')
        return redirect(url_for('main.quotes'))

    if not quote.items:
        flash(_('Cannot submit quote without items'), 'error')
        return redirect(url_for('main.edit_quote', quote_id=quote.id))

    quote.status = 'pending_approval'
    db.session.commit()
    flash(_('Quote submitted for approval'), 'success')
    return redirect(url_for('main.quotes'))

@main_bp.route('/quotes/<int:quote_id>/approve', methods=['GET', 'POST'])
@login_required
@manager_required
def approve_quote(quote_id):
    quote = Quote.query.filter_by(id=quote_id, tenant_id=current_user.tenant_id).first_or_404()

    if quote.status != 'pending_approval':
        flash(_('Quote is not pending approval'), 'error')
        return redirect(url_for('main.quotes'))

    if request.method == 'POST':
        action = request.form.get('action')
        notes = request.form.get('notes', '')

        if action == 'approve':
            quote.status = 'approved'
            quote.approved_by = current_user.id
            quote.approved_at = datetime.now(timezone.utc)
            flash(_('Quote approved successfully'), 'success')
        elif action == 'reject':
            quote.status = 'rejected'
            quote.notes = notes
            flash(_('Quote rejected'), 'info')

        db.session.commit()
        return redirect(url_for('main.quotes'))

    return render_template('quotes/approve.html', quote=quote)

# Order routes
@main_bp.route('/orders')
@login_required
def orders():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Base query filtered by tenant
    query = Order.query.filter_by(tenant_id=current_user.tenant_id)

    # Filter by status if provided
    status = request.args.get('status')
    if status and status != 'all':
        query = query.filter_by(status=status)

    # Search functionality
    search = request.args.get('search', '').strip()
    if search:
        query = query.join(Customer).filter(
            db.or_(
                Order.order_number.ilike(f'%{search}%'),
                Order.title.ilike(f'%{search}%'),
                Customer.name.ilike(f'%{search}%')
            )
        )

    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('orders/index.html', orders=orders, search=search, status=status)

@main_bp.route('/orders/create', methods=['GET', 'POST'])
@login_required
def create_order():
    form = OrderForm()

    # Populate dropdowns
    form.customer_id.choices = [(c.id, c.name) for c in Customer.query.filter_by(tenant_id=current_user.tenant_id).all()]
    form.quote_id.choices = [(0, _('None'))] + [(q.id, f"{q.quote_number} - {q.title}") for q in Quote.query.filter_by(tenant_id=current_user.tenant_id, status='approved').all()]

    if form.validate_on_submit():
        order = Order(
            tenant_id=current_user.tenant_id,
            customer_id=form.customer_id.data,
            quote_id=form.quote_id.data if form.quote_id.data != 0 else None,
            order_type=form.order_type.data,
            title=form.title.data,
            description=form.description.data,
            delivery_address=form.delivery_address.data,
            delivery_date=form.delivery_date.data,
            delivery_notes=form.delivery_notes.data,
            status='pending',
            created_by=current_user.id,
            created_at=datetime.now(timezone.utc)
        )

        # Generate order number
        order.order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{Order.query.filter_by(tenant_id=current_user.tenant_id).count() + 1:04d}"

        db.session.add(order)
        db.session.commit()

        flash(_('Order created successfully'), 'success')
        return redirect(url_for('main.orders'))

    return render_template('orders/create.html', form=form)

@main_bp.route('/orders/<int:order_id>')
@login_required
def view_order(order_id):
    order = Order.query.filter_by(id=order_id, tenant_id=current_user.tenant_id).first_or_404()
    return render_template('orders/view.html', order=order)

@main_bp.route('/orders/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_order(order_id):
    order = Order.query.filter_by(id=order_id, tenant_id=current_user.tenant_id).first_or_404()
    form = OrderForm(obj=order)

    # Populate dropdowns
    form.customer_id.choices = [(c.id, c.name) for c in Customer.query.filter_by(tenant_id=current_user.tenant_id).all()]
    form.quote_id.choices = [(0, _('None'))] + [(q.id, f"{q.quote_number} - {q.title}") for q in Quote.query.filter_by(tenant_id=current_user.tenant_id, status='approved').all()]

    if form.validate_on_submit():
        form.populate_obj(order)
        order.quote_id = form.quote_id.data if form.quote_id.data != 0 else None
        db.session.commit()

        flash(_('Order updated successfully'), 'success')
        return redirect(url_for('main.view_order', order_id=order.id))

    return render_template('orders/edit.html', form=form, order=order)

# Settings routes
@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    if request.method == 'POST':
        section = request.form.get('section')

        if section == 'company':
            current_user.tenant.name = request.form.get('company_name')
            current_user.tenant.company_email = request.form.get('company_email')
            current_user.tenant.company_phone = request.form.get('company_phone')
            current_user.tenant.logo_url = request.form.get('logo_url')
            current_user.tenant.company_address = request.form.get('company_address')

        elif section == 'branding':
            current_user.tenant.primary_color = request.form.get('primary_color')
            current_user.tenant.secondary_color = request.form.get('secondary_color')

        db.session.commit()
        flash(_('Settings updated successfully'), 'success')
        return redirect(url_for('main.settings'))

    return render_template('settings/index.html')

# Task routes
@main_bp.route('/tasks')
@login_required
def tasks():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')

    query = Task.query.filter_by(tenant_id=current_user.tenant_id)

    # Filter by user role
    if current_user.role == 'user':
        query = query.filter(
            db.or_(
                Task.created_by == current_user.id,
                Task.assigned_to == current_user.id
            )
        )

    if status:
        query = query.filter_by(status=status)

    if priority:
        query = query.filter_by(priority=priority)

    tasks = query.order_by(Task.due_date.asc().nullslast()).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template('tasks/index.html', tasks=tasks, status=status, priority=priority)

@main_bp.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    form = TaskForm()
    form.assigned_to.choices = [
        (u.id, u.full_name) for u in User.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    ]
    form.customer_id.choices = [(0, _('Select Customer'))] + [
        (c.id, c.name) for c in Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    ]

    if form.validate_on_submit():
        task = Task(
            tenant_id=current_user.tenant_id,
            created_by=current_user.id,
            assigned_to=form.assigned_to.data,
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            category=form.category.data,
            customer_id=form.customer_id.data if form.customer_id.data else None,
            due_date=form.due_date.data
        )

        db.session.add(task)
        db.session.commit()
        flash(_('Task created successfully'), 'success')
        return redirect(url_for('main.tasks'))

    return render_template('tasks/create.html', form=form)

@main_bp.route('/tasks/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.filter_by(id=task_id, tenant_id=current_user.tenant_id).first_or_404()

    # Check permissions
    if current_user.role == 'user' and task.assigned_to != current_user.id:
        flash(_('You can only complete tasks assigned to you'), 'error')
        return redirect(url_for('main.tasks'))

    task.status = 'completed'
    task.completed_at = datetime.now(timezone.utc)
    task.notes = request.form.get('notes', task.notes)

    db.session.commit()
    flash(_('Task completed successfully'), 'success')
    return redirect(url_for('main.tasks'))

# API endpoints for dynamic forms
@main_bp.route('/api/products/search')
@login_required
def api_search_products():
    search = request.args.get('q', '')
    products = Product.query.filter_by(tenant_id=current_user.tenant_id).filter(
        db.or_(
            Product.code.ilike(f'%{search}%'),
            Product.name_en.ilike(f'%{search}%'),
            Product.name_el.ilike(f'%{search}%')
        )
    ).limit(10).all()

    return jsonify([{
        'id': p.id,
        'code': p.code,
        'name': p.name_en if get_locale() == 'en' else p.name_el,
        'price': float(p.unit_price or 0),
        'unit': p.unit
    } for p in products])

@main_bp.route('/api/quote-items/<int:quote_id>', methods=['POST'])
@login_required
def api_add_quote_item(quote_id):
    quote = Quote.query.filter_by(id=quote_id, tenant_id=current_user.tenant_id).first_or_404()

    data = request.get_json()
    item = QuoteItem(
        quote_id=quote.id,
        product_id=data.get('product_id'),
        description=data['description'],
        quantity=Decimal(str(data['quantity'])),
        unit_price=Decimal(str(data['unit_price'])),
        line_total=Decimal(str(data['quantity'])) * Decimal(str(data['unit_price']))
    )

    db.session.add(item)

    # Update quote totals
    subtotal = sum(item.line_total for item in quote.items) + item.line_total
    tax_amount = subtotal * (quote.tax_rate / 100)
    total_amount = subtotal + tax_amount

    quote.subtotal = subtotal
    quote.tax_amount = tax_amount
    quote.total_amount = total_amount

    db.session.commit()

    return jsonify({'success': True, 'item_id': item.id})

@main_bp.route('/api/quote-items/<int:item_id>', methods=['DELETE'])
@login_required
def api_delete_quote_item(item_id):
    item = QuoteItem.query.join(Quote).filter(
        QuoteItem.id == item_id,
        Quote.tenant_id == current_user.tenant_id
    ).first_or_404()

    quote = item.quote
    db.session.delete(item)

    # Update quote totals
    subtotal = sum(i.line_total for i in quote.items if i.id != item.id)
    tax_amount = subtotal * (quote.tax_rate / 100)
    total_amount = subtotal + tax_amount

    quote.subtotal = subtotal
    quote.tax_amount = tax_amount
    quote.total_amount = total_amount

    db.session.commit()

    return jsonify({'success': True})

# AI Agents routes
@main_bp.route('/agents')
@login_required
@admin_required
def agents_dashboard():
    """AI Agents Dashboard - Main landing page for all AI agents"""
    return render_template('agents/dashboard.html')

@main_bp.route('/agents/communication')
@login_required
@admin_required
def agents_communication():
    """Communication & AI Agent interface"""
    return render_template('agents/communication.html')

@main_bp.route('/agents/operations')
@login_required
@admin_required
def agents_operations():
    """Operations & Data Agent interface"""
    return render_template('agents/operations.html')

@main_bp.route('/agents/analytics')
@login_required
@admin_required
def agents_analytics():
    """Platform Integration Agent - Analytics Dashboard"""
    return render_template('agents/analytics.html')

# Enhanced Task routes with RBAC
@main_bp.route('/tasks/kanban')
@login_required
def kanban_board():
    """Main Kanban board view"""
    board_id = request.args.get('board_id', type=int)

    # Get user's boards
    if current_user.role in ['admin', 'manager']:
        # Managers can see all boards
        boards = TaskBoard.query.filter_by(tenant_id=current_user.tenant_id).all()
        if not board_id and boards:
            board_id = boards[0].id
    else:
        # Regular users can only see boards they're members of
        user_boards = TaskBoardMember.query.filter_by(user_id=current_user.id).all()
        boards = [member.board for member in user_boards]
        if not board_id and boards:
            board_id = boards[0].id

    if not board_id:
        # Create default personal board if none exists
        default_board = TaskBoard(
            tenant_id=current_user.tenant_id,
            created_by=current_user.id,
            name=f"{current_user.full_name}'s Tasks",
            board_type='personal',
            is_default=True
        )
        db.session.add(default_board)
        db.session.commit()

        # Add default columns
        columns = [
            ('To Do', 'pending', '#6c757d'),
            ('Acknowledged', 'acknowledged', '#17a2b8'),
            ('In Progress', 'in_progress', '#ffc107'),
            ('Review', 'review', '#fd7e14'),
            ('Done', 'completed', '#28a745')
        ]

        for i, (name, status, color) in enumerate(columns):
            column = TaskColumn(
                board_id=default_board.id,
                name=name,
                position=i,
                color=color,
                auto_assign_status=status
            )
            db.session.add(column)

        db.session.commit()
        board_id = default_board.id

    board = TaskBoard.query.get_or_404(board_id)

    # Check permissions
    if current_user.role not in ['admin', 'manager']:
        member = TaskBoardMember.query.filter_by(board_id=board_id, user_id=current_user.id).first()
        if not member:
            flash(_('You do not have access to this board'), 'error')
            return redirect(url_for('main.tasks'))

    # Get columns and cards
    columns = board.columns
    cards_by_column = {}

    for column in columns:
        if current_user.role in ['admin', 'manager']:
            cards = TaskCard.query.filter_by(column_id=column.id).order_by(TaskCard.position).all()
        else:
            # Users can only see cards assigned to them or created by them
            cards = TaskCard.query.filter(
                TaskCard.column_id == column.id,
                db.or_(
                    TaskCard.assigned_to == current_user.id,
                    TaskCard.created_by == current_user.id
                )
            ).order_by(TaskCard.position).all()

        cards_by_column[column] = cards

    # Get available users for assignment
    if current_user.role in ['admin', 'manager']:
        available_users = User.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    else:
        available_users = [current_user]

    return render_template('tasks/kanban.html', 
                         board=board, 
                         columns=columns, 
                         cards_by_column=cards_by_column,
                         available_users=available_users,
                         boards=boards)

@main_bp.route('/tasks/boards/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_board():
    """Create a new task board"""
    form = TaskBoardForm()

    if form.validate_on_submit():
        board = TaskBoard(
            tenant_id=current_user.tenant_id,
            created_by=current_user.id,
            name=form.name.data,
            description=form.description.data,
            board_type=form.board_type.data,
            is_public=form.is_public.data,
            color_scheme=form.color_scheme.data,
            auto_archive_days=form.auto_archive_days.data
        )

        db.session.add(board)
        db.session.commit()

        # Add creator as owner
        member = TaskBoardMember(
            board_id=board.id,
            user_id=current_user.id,
            role='owner',
            can_create_cards=True,
            can_move_cards=True,
            can_edit_cards=True,
            can_delete_cards=True,
            can_manage_board=True
        )
        db.session.add(member)

        # Create default columns
        columns = [
            ('To Do', 'pending', '#6c757d'),
            ('Acknowledged', 'acknowledged', '#17a2b8'),
            ('In Progress', 'in_progress', '#ffc107'),
            ('Review', 'review', '#fd7e14'),
            ('Done', 'completed', '#28a745')
        ]

        for i, (name, status, color) in enumerate(columns):
            column = TaskColumn(
                board_id=board.id,
                name=name,
                position=i,
                color=color,
                auto_assign_status=status
            )
            db.session.add(column)

        db.session.commit()
        flash(_('Board created successfully'), 'success')
        return redirect(url_for('main.kanban_board', board_id=board.id))

    return render_template('tasks/create_board.html', form=form)

@main_bp.route('/tasks/cards/create', methods=['GET', 'POST'])
@login_required
def create_card():
    """Create a new task card"""
    board_id = request.args.get('board_id', type=int)
    column_id = request.args.get('column_id', type=int)

    if not board_id:
        flash(_('Board ID is required'), 'error')
        return redirect(url_for('main.kanban_board'))

    # Check permissions
    if current_user.role not in ['admin', 'manager']:
        member = TaskBoardMember.query.filter_by(board_id=board_id, user_id=current_user.id).first()
        if not member or not member.can_create_cards:
            flash(_('You do not have permission to create cards on this board'), 'error')
            return redirect(url_for('main.kanban_board', board_id=board_id))

    form = TaskCardForm()
    form.assigned_to.choices = [
        (u.id, u.full_name) for u in User.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    ]
    form.customer_id.choices = [(0, _('Select Customer'))] + [
        (c.id, c.name) for c in Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    ]

    if form.validate_on_submit():
        # Get target column
        if column_id:
            column = TaskColumn.query.get_or_404(column_id)
        else:
            # Get first column (To Do)
            column = TaskColumn.query.filter_by(board_id=board_id).order_by(TaskColumn.position).first()

        # Get next position
        max_position = db.session.query(db.func.max(TaskCard.position)).filter_by(column_id=column.id).scalar() or 0

        # Process labels and tags
        labels = [label.strip() for label in form.labels.data.split(',')] if form.labels.data else []
        tags = [tag.strip() for tag in form.tags.data.split(',')] if form.tags.data else []

        card = TaskCard(
            board_id=board_id,
            column_id=column.id,
            created_by=current_user.id,
            assigned_to=form.assigned_to.data,
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            category=form.category.data,
            customer_id=form.customer_id.data if form.customer_id.data else None,
            due_date=form.due_date.data,
            time_estimate=form.time_estimate.data,
            story_points=form.story_points.data,
            labels=labels,
            tags=tags,
            position=max_position + 1
        )

        db.session.add(card)

        # Add system comment
        comment = TaskComment(
            card_id=card.id,
            user_id=current_user.id,
            content=f"Task created by {current_user.full_name}",
            is_system_comment=True,
            comment_type='system'
        )
        db.session.add(comment)

        db.session.commit()
        flash(_('Task created successfully'), 'success')
        return redirect(url_for('main.kanban_board', board_id=board_id))

    return render_template('tasks/create_card.html', form=form, board_id=board_id)

@main_bp.route('/tasks/cards/<int:card_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_card(card_id):
    """Edit a task card"""
    card = TaskCard.query.get_or_404(card_id)

    # Check permissions
    if current_user.role not in ['admin', 'manager']:
        if card.created_by != current_user.id and card.assigned_to != current_user.id:
            flash(_('You can only edit tasks you created or are assigned to'), 'error')
            return redirect(url_for('main.kanban_board', board_id=card.board_id))

    form = TaskCardForm(obj=card)
    form.assigned_to.choices = [
        (u.id, u.full_name) for u in User.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    ]
    form.customer_id.choices = [(0, _('Select Customer'))] + [
        (c.id, c.name) for c in Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    ]

    # Set current values for labels and tags
    if card.labels:
        form.labels.data = ', '.join(card.labels)
    if card.tags:
        form.tags.data = ', '.join(card.tags)

    if form.validate_on_submit():
        card.title = form.title.data
        card.description = form.description.data
        card.priority = form.priority.data
        card.category = form.category.data
        card.assigned_to = form.assigned_to.data
        card.customer_id = form.customer_id.data if form.customer_id.data else None
        card.due_date = form.due_date.data
        card.time_estimate = form.time_estimate.data
        card.story_points = form.story_points.data

        # Process labels and tags
        card.labels = [label.strip() for label in form.labels.data.split(',')] if form.labels.data else []
        card.tags = [tag.strip() for tag in form.tags.data.split(',')] if form.tags.data else []

        db.session.commit()
        flash(_('Task updated successfully'), 'success')
        return redirect(url_for('main.kanban_board', board_id=card.board_id))

    return render_template('tasks/edit_card.html', form=form, card=card)

@main_bp.route('/tasks/cards/<int:card_id>/status', methods=['POST'])
@login_required
def update_card_status(card_id):
    """Update task status with RBAC workflow"""
    card = TaskCard.query.get_or_404(card_id)
    new_status = request.json.get('status')

    if not new_status:
        return jsonify({'success': False, 'error': 'Status is required'})

    # Check permissions based on current status and user role
    can_update = False

    if current_user.role in ['admin', 'manager']:
        can_update = True
    elif card.assigned_to == current_user.id:
        # Assigned user can update status following workflow
        status_workflow = {
            'pending': ['acknowledged', 'in_progress'],
            'acknowledged': ['in_progress', 'pending'],
            'in_progress': ['review', 'completed', 'acknowledged'],
            'review': ['completed', 'in_progress'],
            'completed': ['in_progress'],  # Can reopen
            'cancelled': ['pending']  # Can reactivate
        }

        current_status = card.status
        allowed_transitions = status_workflow.get(current_status, [])
        can_update = new_status in allowed_transitions

    if not can_update:
        return jsonify({'success': False, 'error': 'You do not have permission to update this task status'})

    old_status = card.status
    card.status = new_status

    # Handle status-specific actions
    if new_status == 'acknowledged' and old_status == 'pending':
        card.acknowledged_at = datetime.now(timezone.utc)
        card.acknowledged_by = current_user.id
    elif new_status == 'in_progress' and old_status in ['pending', 'acknowledged']:
        card.started_at = datetime.now(timezone.utc)
    elif new_status == 'completed' and old_status in ['in_progress', 'review']:
        card.completed_at = datetime.now(timezone.utc)

    # Add system comment
    status_messages = {
        'acknowledged': f"Task acknowledged by {current_user.full_name}",
        'in_progress': f"Task started by {current_user.full_name}",
        'review': f"Task moved to review by {current_user.full_name}",
        'completed': f"Task completed by {current_user.full_name}",
        'cancelled': f"Task cancelled by {current_user.full_name}"
    }

    if new_status in status_messages:
        comment = TaskComment(
            card_id=card.id,
            user_id=current_user.id,
            content=status_messages[new_status],
            is_system_comment=True,
            comment_type='system'
        )
        db.session.add(comment)

    db.session.commit()

    return jsonify({
        'success': True, 
        'status': new_status,
        'progress': card.progress,
        'message': f'Task status updated to {new_status}'
    })

@main_bp.route('/tasks/cards/<int:card_id>/move', methods=['POST'])
@login_required
def move_card(card_id):
    """Move card between columns (drag and drop)"""
    card = TaskCard.query.get_or_404(card_id)
    new_column_id = request.json.get('column_id')
    new_position = request.json.get('position', 0)

    if not new_column_id:
        return jsonify({'success': False, 'error': 'Column ID is required'})

    # Check permissions
    if current_user.role not in ['admin', 'manager']:
        member = TaskBoardMember.query.filter_by(board_id=card.board_id, user_id=current_user.id).first()
        if not member or not member.can_move_cards:
            return jsonify({'success': False, 'error': 'You do not have permission to move cards'})

    new_column = TaskColumn.query.get_or_404(new_column_id)

    # Update card position and column
    old_column_id = card.column_id
    card.column_id = new_column_id
    card.position = new_position

    # Update status based on column auto_assign_status
    if new_column.auto_assign_status and new_column.auto_assign_status != card.status:
        old_status = card.status
        card.status = new_column.auto_assign_status

        # Handle status-specific actions
        if card.status == 'acknowledged' and old_status == 'pending':
            card.acknowledged_at = datetime.now(timezone.utc)
            card.acknowledged_by = current_user.id
        elif card.status == 'in_progress' and old_status in ['pending', 'acknowledged']:
            card.started_at = datetime.now(timezone.utc)
        elif card.status == 'completed' and old_status in ['in_progress', 'review']:
            card.completed_at = datetime.now(timezone.utc)

    # Reorder other cards in the target column
    other_cards = TaskCard.query.filter(
        TaskCard.column_id == new_column_id,
        TaskCard.id != card.id
    ).order_by(TaskCard.position).all()

    for i, other_card in enumerate(other_cards):
        if i >= new_position:
            other_card.position = i + 1
        else:
            other_card.position = i

    db.session.commit()

    return jsonify({
        'success': True,
        'status': card.status,
        'progress': card.progress
    })

@main_bp.route('/tasks/cards/<int:card_id>/comments', methods=['POST'])
@login_required
def add_comment(card_id):
    """Add a comment to a task card"""
    card = TaskCard.query.get_or_404(card_id)
    content = request.json.get('content')

    if not content:
        return jsonify({'success': False, 'error': 'Comment content is required'})

    # Check permissions
    if current_user.role not in ['admin', 'manager']:
        if card.created_by != current_user.id and card.assigned_to != current_user.id:
            return jsonify({'success': False, 'error': 'You can only comment on tasks you created or are assigned to'})

    comment = TaskComment(
        card_id=card.id,
        user_id=current_user.id,
        content=content
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify({
        'success': True,
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'user_name': comment.user.full_name,
            'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M')
        }
    })

@main_bp.route('/tasks/team')
@login_required
@manager_required
def team_tasks():
    """Manager view of all team tasks"""
    team_members = User.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    team_tasks = {}

    for member in team_members:
        tasks = TaskCard.query.filter_by(
            board_id=current_user.tenant_id,  # This should be board-specific
            assigned_to=member.id
        ).order_by(TaskCard.due_date.asc()).all()
        team_tasks[member] = tasks

    # Calculate team metrics
    total_tasks = sum(len(tasks) for tasks in team_tasks.values())
    completed_tasks = sum(len([t for t in tasks if t.status == 'completed']) for tasks in team_tasks.values())
    overdue_tasks = sum(len([t for t in tasks if t.is_overdue]) for tasks in team_tasks.values())

    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    return render_template('tasks/team.html', 
                         team_tasks=team_tasks,
                         total_tasks=total_tasks,
                         completed_tasks=completed_tasks,
                         overdue_tasks=overdue_tasks,
                         completion_rate=completion_rate)

@main_bp.route('/tasks/reports')
@login_required
@manager_required
def task_reports():
    """Generate task analytics and reports"""
    from sqlalchemy import func

    # Get all tasks for the tenant
    tasks = TaskCard.query.join(TaskBoard).filter(TaskBoard.tenant_id == current_user.tenant_id).all()

    # Calculate metrics
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == 'completed'])
    overdue_tasks = len([t for t in tasks if t.is_overdue])

    # Status distribution
    status_counts = {}
    for task in tasks:
        status_counts[task.status] = status_counts.get(task.status, 0) + 1

    # Priority distribution
    priority_counts = {}
    for task in tasks:
        priority_counts[task.priority] = priority_counts.get(task.priority, 0) + 1

    # User performance
    user_performance = {}
    for task in tasks:
        if task.assigned_to:
            assignee = task.assignee
            if assignee.id not in user_performance:
                user_performance[assignee.id] = {
                    'user': assignee,
                    'total': 0,
                    'completed': 0,
                    'overdue': 0
                }

            user_performance[assignee.id]['total'] += 1
            if task.status == 'completed':
                user_performance[assignee.id]['completed'] += 1
            if task.is_overdue:
                user_performance[assignee.id]['overdue'] += 1

    return render_template('tasks/reports.html',
                         total_tasks=total_tasks,
                         completed_tasks=completed_tasks,
                         overdue_tasks=overdue_tasks,
                         status_counts=status_counts,
                         priority_counts=priority_counts,
                         user_performance=user_performance)
