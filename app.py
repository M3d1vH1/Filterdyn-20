import os
import logging
from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel, get_locale
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
babel = Babel()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["LANGUAGES"] = {
        'en': 'English',
        'el': 'Ελληνικά'
    }
    app.config["BABEL_DEFAULT_LOCALE"] = 'en'
    app.config["BABEL_DEFAULT_TIMEZONE"] = 'Europe/Athens'
    
    # Proxy fix for production
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app)
    migrate.init_app(app, db)
    
    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Babel locale selector
    @babel.localeselector
    def get_locale():
        # 1. Check if language is set in session
        if 'language' in session:
            return session['language']
        # 2. Check if language is in URL parameters
        if request.args.get('lang'):
            session['language'] = request.args.get('lang')
            return session['language']
        # 3. Use browser's preferred language
        return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or 'en'
    
    # Register blueprints
    from routes import main_bp
    from auth import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    
    # Context processors
    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        return {
            'current_user': current_user,
            'current_locale': get_locale()
        }
    
    # Create tables
    with app.app_context():
        import models
        db.create_all()
        
        # Create superadmin if it doesn't exist
        from models import User, Tenant
        from werkzeug.security import generate_password_hash
        
        superadmin = User.query.filter_by(username='superadmin').first()
        if not superadmin:
            # Create default tenant
            default_tenant = Tenant(
                name='Filterdyn',
                subdomain='filterdyn',
                is_active=True
            )
            db.session.add(default_tenant)
            db.session.commit()
            
            # Create superadmin user
            superadmin = User(
                username='superadmin',
                email='admin@filterdyn.com',
                password_hash=generate_password_hash('admin123'),
                role='superadmin',
                tenant_id=default_tenant.id,
                is_active=True
            )
            db.session.add(superadmin)
            db.session.commit()
            print("Created superadmin user: superadmin / admin123")
    
    return app

app = create_app()
