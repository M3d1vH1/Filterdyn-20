from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_babel import _, get_locale
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from models import User, Customer, Product, ProductCategory, Quote, QuoteItem, Order, OrderItem, Task
from app import db
from forms import CustomerForm, ProductForm, ProductCategoryForm, QuoteForm, OrderForm, TaskForm
from utils import admin_required, manager_required, generate_pdf_quote
import json

main_bp = Blueprint('main', __name__)

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
    view = request.args.get('view', 'list')
    
    if view == 'kanban':
        return redirect(url_for('main.tasks_kanban'))
    
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


@main_bp.route('/tasks/kanban')
@login_required
def tasks_kanban():
    """Kanban board view for tasks"""
    query = Task.query.filter_by(tenant_id=current_user.tenant_id)
    
    # Filter by user role
    if current_user.role == 'user':
        query = query.filter(
            db.or_(
                Task.created_by == current_user.id,
                Task.assigned_to == current_user.id
            )
        )
    
    # Get tasks grouped by status
    statuses = ['pending', 'in_progress', 'completed', 'cancelled']
    kanban_data = {}
    
    for status in statuses:
        tasks = query.filter_by(status=status).order_by(Task.created_at.desc()).all()
        kanban_data[status] = tasks
    
    # Get all users for assignment dropdown
    users = User.query.filter_by(tenant_id=current_user.tenant_id).all()
    
    return render_template('tasks/kanban.html', kanban_data=kanban_data, users=users, statuses=statuses)

def _ensure_daily_board_exists(tenant_id, target_date):
    """Ensure daily board exists and carry forward open tasks if needed"""
    from datetime import datetime, timedelta
    
    # Get or create board for target date
    daily_board = DailyBoard.get_or_create_for_date(tenant_id, target_date)
    
    # Check if we need to carry forward tasks from previous day
    prev_date = target_date - timedelta(days=1)
    
    # Only carry forward if this is a new board (no tasks yet)
    existing_tasks = Task.query.filter_by(
        tenant_id=tenant_id,
        board_date=target_date
    ).count()
    
    if existing_tasks == 0 and target_date >= datetime.now().date():
        # Find open tasks from previous day to carry forward
        prev_tasks = Task.query.filter_by(
            tenant_id=tenant_id,
            board_date=prev_date
        ).filter(Task.status.in_(['pending', 'in_progress'])).all()
        
        carried_count = 0
        for task in prev_tasks:
            # Create a new task entry for the new date
            task.carry_forward_to_date(target_date)
            carried_count += 1
        
        # Update board metrics
        daily_board.carried_forward = carried_count
        daily_board.total_tasks = carried_count
        
        if carried_count > 0:
            db.session.commit()

@main_bp.route('/tasks/kanban/quick-add', methods=['POST'])
@login_required
def kanban_quick_add():
    """Quick add task to current kanban board"""
    data = request.get_json()
    
    task = Task(
        tenant_id=current_user.tenant_id,
        title=data.get('title', ''),
        description=data.get('description', ''),
        priority=data.get('priority', 'medium'),
        status='pending',
        created_by=current_user.id,
        assigned_to=data.get('assigned_to', current_user.id),
        board_date=datetime.strptime(data.get('date'), '%Y-%m-%d').date() if data.get('date') else datetime.now().date()
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({'success': True, 'task_id': task.id})


@main_bp.route('/tasks/update_status', methods=['POST'])
@login_required
def update_task_status():
    """Update task status via AJAX for kanban board"""
    task_id = request.json.get('task_id')
    new_status = request.json.get('status')
    
    task = Task.query.filter_by(id=task_id, tenant_id=current_user.tenant_id).first()
    
    if not task:
        return jsonify({'success': False, 'message': 'Task not found'}), 404
    
    # Check permissions
    if current_user.role == 'user':
        if task.created_by != current_user.id and task.assigned_to != current_user.id:
            return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    # Update status
    task.status = new_status
    if new_status == 'completed':
        task.completed_at = datetime.now(timezone.utc)
    else:
        task.completed_at = None
    
    task.updated_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Task status updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# AI Assistant Routes
@main_bp.route('/ai-assistant')
@login_required
def ai_assistant():
    """AI Assistant Dashboard"""
    if current_user.role not in ['admin', 'superadmin']:
        flash(_('Access denied'), 'error')
        return redirect(url_for('main.dashboard'))
    
    stats = {
        'total_emails': 50,
        'emails_processed': 35,
        'ai_responses': 20,
        'accuracy_rate': 85
    }
    
    return render_template('ai_assistant/dashboard.html', stats=stats)

@main_bp.route('/ai-assistant/gmail')
@login_required
def gmail_inbox():
    """Gmail Inbox Integration"""
    if current_user.role not in ['admin', 'superadmin']:
        flash(_('Access denied'), 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('ai_assistant/gmail_setup.html')

@main_bp.route('/ai-assistant/learning')
@login_required
def ai_learning_dashboard():
    """AI Learning Statistics Dashboard"""
    if current_user.role not in ['admin', 'superadmin']:
        flash(_('Access denied'), 'error')
        return redirect(url_for('main.dashboard'))
    
    learning_stats = {
        'total_interactions': 150,
        'successful_responses': 128,
        'user_corrections': 22,
        'learning_accuracy': 85.3,
        'recent_improvements': [
            {'area': 'Email Classification', 'improvement': '+12%'},
            {'area': 'Response Quality', 'improvement': '+8%'},
            {'area': 'Context Understanding', 'improvement': '+15%'}
        ]
    }
    
    return render_template('ai_assistant/learning.html', stats=learning_stats)

@main_bp.route('/tasks/<int:id>/edit', methods=['GET', 'POST'])
@login_required  
def edit_task(id):
    """Edit task"""
    task = Task.query.filter_by(
        id=id,
        tenant_id=current_user.tenant_id
    ).first_or_404()
    
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.priority = request.form.get('priority')
        task.status = request.form.get('status')
        task.assigned_to = request.form.get('assigned_to') or None
        task.customer_id = request.form.get('customer_id') or None
        
        due_date_str = request.form.get('due_date')
        if due_date_str:
            from timezone_utils import parse_user_datetime
            task.due_date = parse_user_datetime(due_date_str, '%Y-%m-%dT%H:%M')
        else:
            task.due_date = None
        
        db.session.commit()
        flash(_('Task updated successfully'), 'success')
        return redirect(url_for('main.tasks'))
    
    # For GET request, populate form choices
    users = User.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    customers = Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    
    return render_template('tasks/edit.html', task=task, users=users, customers=customers)

@main_bp.route('/tasks/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_task():
    form = TaskForm()
    form.assigned_to.choices = [
        (u.id, u.full_name) for u in User.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    ]
    form.customer_id.choices = [(0, _('Select Customer'))] + [
        (c.id, c.name) for c in Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    ]
    
    if form.validate_on_submit():
        assigned_user = User.query.filter_by(id=form.assigned_to.data, tenant_id=current_user.tenant_id, is_active=True).first()
        if not assigned_user:
            flash(_('Invalid assignee. Please select an active user in your organization.'), 'error')
            return redirect(url_for('main.tasks'))
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
    task = Task.query.filter_by(id=id, tenant_id=current_user.tenant_id).first_or_404()
    # Check permissions
    if current_user.role == 'user' and task.assigned_to != current_user.id:
        flash(_('You can only complete tasks assigned to you.'), 'error')
        return redirect(url_for('main.tasks'))
    if task.status == 'completed':
        flash(_('Task is already completed.'), 'info')
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
