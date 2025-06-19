# Filterdyn Operations Suite

A comprehensive multi-tenant business management platform designed specifically for water treatment solutions companies. Built with Flask and PostgreSQL, providing complete customer relationship management, product catalog management, quote generation, order processing, and task management capabilities.

## 🌟 Features

### Core Business Management
- **Customer Relationship Management** - Complete customer profiles with contact management
- **Product Catalog** - Hierarchical product organization with multilingual support
- **Quote Generation** - Professional PDF quotes with approval workflows
- **Order Processing** - Seamless quote-to-order conversion with delivery tracking
- **Task Management** - Team task assignment with priority and deadline tracking

### Technical Capabilities
- **Multi-tenant Architecture** - Complete data isolation for multiple businesses
- **Internationalization** - English and Greek language support with Flask-Babel
- **Role-based Access Control** - Four-tier permission system (superadmin, admin, manager, user)
- **Timezone Handling** - Robust UTC storage with local display (Europe/Athens default)
- **PDF Generation** - Professional quotes and invoices with custom branding
- **Responsive Design** - Mobile-first Bootstrap 5 interface

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/M3d1vH1/Filterdyn-20.git
   cd Filterdyn-20
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/filterdyn"
   export SESSION_SECRET="your-secret-key-here"
   ```

4. **Initialize the database**
   ```bash
   flask db upgrade
   ```

5. **Run the application**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

6. **Access the application**
   - Open your browser to `http://localhost:5000`
   - Default login: `superadmin` / `admin123`

## 🏗️ Architecture

### Backend Stack
- **Flask 3.1.1** - Web application framework
- **SQLAlchemy 2.0+** - Database ORM with declarative base
- **PostgreSQL** - Primary database (supports Neon.tech hosting)
- **Flask-Login** - User session management
- **Flask-Babel** - Internationalization support
- **FPDF2** - PDF generation for documents

### Frontend Stack
- **Bootstrap 5.3.0** - Responsive CSS framework
- **Feather Icons** - Consistent iconography
- **Vanilla JavaScript** - Interactive functionality
- **Jinja2** - Server-side templating

### Database Design
```
Users (Multi-tenant)
├── Customers
├── Products
│   └── Categories
├── Quotes
│   └── Quote Items
├── Orders
│   └── Order Items
└── Tasks
```

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `SESSION_SECRET` - Flask session encryption key
- `MAIL_SERVER` - SMTP server for notifications (optional)
- `MAIL_USERNAME` - Email username (optional)
- `MAIL_PASSWORD` - Email password (optional)

### Timezone Configuration
The application uses robust timezone handling:
- All datetimes stored in UTC
- User display in Europe/Athens timezone (configurable per user)
- Automatic conversion between UTC and local time

## 📊 Database Schema

### Key Models
- **Tenant** - Multi-tenant organization isolation
- **User** - Authentication with role-based permissions
- **Customer** - Client company information and contacts
- **Product** - Catalog items with multilingual descriptions
- **Quote** - Sales quotations with approval workflow
- **Order** - Purchase orders with delivery tracking
- **Task** - Team task management with assignments

### Relationships
- One-to-many: Tenant → Users, Customers, Products
- Many-to-many: Quotes ↔ Products (via QuoteItems)
- Hierarchical: ProductCategories with parent-child structure

## 🌍 Internationalization

### Supported Languages
- **English (en)** - Default language
- **Greek (el)** - Full translation support

### Adding New Languages
1. Extract translatable strings:
   ```bash
   pybabel extract -F babel.cfg -k _l -o messages.pot .
   ```

2. Create new language:
   ```bash
   pybabel init -i messages.pot -d translations -l [language_code]
   ```

3. Compile translations:
   ```bash
   pybabel compile -d translations
   ```

## 🔐 Security Features

- **CSRF Protection** - Flask-WTF token validation
- **SQL Injection Prevention** - SQLAlchemy ORM parameterized queries
- **Password Hashing** - Werkzeug secure password storage
- **Session Security** - Secure cookie configuration
- **Role-based Access** - Granular permission control

## 📁 Project Structure

```
filterdyn/
├── static/
│   ├── css/          # Custom stylesheets
│   ├── js/           # JavaScript files
│   └── img/          # Images and logos
├── templates/
│   ├── auth/         # Authentication pages
│   ├── customers/    # Customer management
│   ├── products/     # Product catalog
│   ├── quotes/       # Quote generation
│   ├── orders/       # Order processing
│   ├── tasks/        # Task management
│   └── base.html     # Base template
├── translations/     # i18n translation files
├── app.py           # Application factory
├── models.py        # Database models
├── routes.py        # URL routes and views
├── forms.py         # WTForms definitions
├── config.py        # Configuration settings
└── timezone_utils.py # Timezone handling utilities
```

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

Test timezone functionality:
```bash
python -c "from timezone_utils import *; print('Timezone utilities working')"
```

## 🚀 Deployment

### Production Setup
1. **Configure environment**
   ```bash
   export FLASK_ENV=production
   export DATABASE_URL="your-production-db-url"
   ```

2. **Run with Gunicorn**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
   ```

### Replit Deployment
The application is configured for Replit Autoscale:
- Uses `.replit` configuration
- Automatic SSL and domain management
- Built-in PostgreSQL database support

## 📈 Recent Updates

### June 2025 - Timezone Implementation
- ✅ Comprehensive timezone handling system
- ✅ UTC storage with local display conversion
- ✅ Eliminated naive/aware datetime comparison errors
- ✅ Europe/Athens default timezone support
- ✅ User-configurable timezone preferences

### Features Added
- Gmail AI integration with OAuth authentication
- Smart email replies and learning dashboard
- Enhanced audit system with modular testing
- Robust error handling and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit: `git commit -m "Add feature"`
5. Push: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is proprietary software for Filterdyn water treatment solutions.

## 🆘 Support

For technical support or feature requests:
- Create an issue on GitHub
- Contact the development team
- Check the documentation in `replit.md`

## 🔧 Development

### Local Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run in debug mode
export FLASK_ENV=development
flask run --debug

# Database migrations
flask db init
flask db migrate -m "Description"
flask db upgrade
```

### Code Style
- Follow PEP 8 standards
- Use meaningful variable names
- Comment complex business logic
- Maintain test coverage above 80%

---

**Filterdyn Operations Suite** - Streamlining water treatment business operations with modern technology.