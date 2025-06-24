from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, Tenant
from app import db
from forms import LoginForm, UserForm
from utils import admin_required, manager_required
import os
import requests
from urllib.parse import urlencode

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Find user by username
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=form.remember_me.data)
            
            # Update last login
            from datetime import datetime, timezone
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/google/login')
def google_login():
    """Initiate Google OAuth login"""
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    if not client_id:
        return "Google OAuth is not configured. Please contact your administrator.", 500
    
    # Get the current domain dynamically - use external domain for Replit
    if 'replit.dev' in request.host or 'kirk.replit.dev' in request.host:
        redirect_uri = f"https://{request.host}/auth/google/callback"
    else:
        redirect_uri = request.url_root.rstrip('/') + '/auth/google/callback'
    
    # Google OAuth parameters
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/userinfo.email',
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode(params)
    return redirect(auth_url)

@auth_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        flash(f'Google authentication failed: {error}', 'error')
        return redirect(url_for('main.ai_assistant'))
    
    if not code:
        flash('No authorization code received from Google', 'error')
        return redirect(url_for('main.ai_assistant'))
    
    # Exchange code for tokens
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        flash('Google OAuth credentials not configured', 'error')
        return redirect(url_for('main.ai_assistant'))
    
    redirect_uri = request.url_root.rstrip('/') + '/auth/google/callback'
    
    token_data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    try:
        # Get access token
        token_response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        # Store tokens in session (in production, store in database)
        session['google_access_token'] = tokens.get('access_token')
        session['google_refresh_token'] = tokens.get('refresh_token')
        
        # Get user info
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        user_response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        session['google_email'] = user_info.get('email')
        session['google_connected'] = True
        
        # Check if user is logged in, if not redirect to login with success message
        from flask_login import current_user
        if current_user.is_authenticated:
            flash(f'Successfully connected Gmail account: {user_info.get("email")}', 'success')
            return redirect(url_for('main.gmail_inbox'))
        else:
            flash(f'Gmail connected: {user_info.get("email")}. Please log in to continue.', 'success')
            return redirect(url_for('auth.login'))
        
    except requests.exceptions.RequestException as e:
        return f'Failed to connect Gmail: {str(e)}', 500

@auth_bp.route('/google/disconnect')
@login_required
def google_disconnect():
    """Disconnect Google account"""
    session.pop('google_access_token', None)
    session.pop('google_refresh_token', None)
    session.pop('google_email', None)
    session.pop('google_connected', None)
    
    flash('Gmail account disconnected successfully', 'info')
    return redirect(url_for('main.ai_assistant'))

@auth_bp.route('/change-language/<language>')
def change_language(language):
    session['language'] = language
    return redirect(request.referrer or url_for('main.dashboard'))

@auth_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('users/index.html', users=users)

@auth_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = UserForm()
    
    if form.validate_on_submit():
        # Check if username already exists in tenant
        existing_user = User.query.filter_by(
            tenant_id=current_user.tenant_id,
            username=form.username.data
        ).first()
        
        if existing_user:
            flash('Username already exists', 'error')
            return render_template('users/edit.html', form=form, user=None)
        
        user = User(
            tenant_id=current_user.tenant_id,
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            is_active=form.is_active.data
        )
        
        db.session.add(user)
        db.session.commit()
        flash('User created successfully', 'success')
        return redirect(url_for('auth.users'))
    
    return render_template('users/edit.html', form=form, user=None)

@auth_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.filter_by(id=user_id, tenant_id=current_user.tenant_id).first_or_404()
    form = UserForm(obj=user)
    
    if form.validate_on_submit():
        # Check if username already exists in tenant (excluding current user)
        existing_user = User.query.filter_by(
            tenant_id=current_user.tenant_id,
            username=form.username.data
        ).filter(User.id != user.id).first()
        
        if existing_user:
            flash('Username already exists', 'error')
            return render_template('users/edit.html', form=form, user=user)
        
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.phone = form.phone.data
        user.is_active = form.is_active.data
        
        # Update password if provided
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('auth.users'))
    
    return render_template('users/edit.html', form=form, user=user)

@auth_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id, tenant_id=current_user.tenant_id).first_or_404()
    
    # Prevent self-deletion
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('auth.users'))
    
    # Prevent deletion of last admin
    if user.role == 'admin':
        admin_count = User.query.filter_by(tenant_id=current_user.tenant_id, role='admin', is_active=True).count()
        if admin_count <= 1:
            flash('Cannot delete the last admin user', 'error')
            return redirect(url_for('auth.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('auth.users'))
