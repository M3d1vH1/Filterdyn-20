# Filterdyn Operations Suite

## Overview

The Filterdyn Operations Suite is a comprehensive multi-tenant business management platform designed specifically for water treatment solutions companies. Built with Flask and PostgreSQL, the system provides complete customer relationship management, product catalog management, quote generation, order processing, and task management capabilities with full internationalization support for English and Greek.

## System Architecture

### Frontend Architecture
- **Framework**: Flask with Jinja2 templating
- **UI Framework**: Bootstrap 5.3.0 with custom Filterdyn branding
- **Icons**: Feather Icons for consistent visual elements
- **Responsive Design**: Mobile-first approach with responsive layouts
- **Internationalization**: Flask-Babel with English/Greek language support
- **JavaScript**: Vanilla JavaScript for interactive features

### Backend Architecture
- **Framework**: Flask 3.1.1 with modular blueprint structure
- **Database ORM**: SQLAlchemy 2.0+ with declarative base
- **Authentication**: Flask-Login with role-based access control
- **Form Handling**: WTForms with Flask-WTF integration
- **Migration System**: Flask-Migrate for database schema management
- **PDF Generation**: FPDF2 for professional quote documents

### Multi-Tenant Design
- **Tenant Isolation**: Complete data separation using tenant_id foreign keys
- **User Management**: Four-tier role system (superadmin, admin, manager, user)
- **Branding Support**: Customizable logos, colors, and company information per tenant
- **Scalable Architecture**: Designed to support multiple businesses on single platform

## Key Components

### 1. User Management & Authentication
- **Role-Based Access Control**: Four permission levels with appropriate restrictions
- **Session Management**: Secure session handling with configurable timeouts
- **Password Security**: Werkzeug password hashing with salt
- **Last Login Tracking**: User activity monitoring

### 2. Customer Relationship Management
- **Complete Customer Profiles**: Company information, contacts, addresses
- **Search & Filtering**: Advanced search capabilities with pagination
- **Industry Categorization**: Business type classification
- **Communication History**: Notes and interaction tracking

### 3. Product Catalog Management
- **Hierarchical Categories**: Organized product structure
- **Multilingual Support**: Product names and descriptions in English/Greek
- **Pricing Management**: Cost and selling price tracking
- **Inventory Awareness**: Stock level monitoring

### 4. Quote Generation System
- **Professional PDF Output**: Branded quote documents
- **Line Item Management**: Detailed product/service breakdowns
- **Approval Workflow**: Multi-stage approval process
- **Status Tracking**: Complete quote lifecycle management
- **Customer Communication**: Email integration capabilities

### 5. Order Processing
- **Quote to Order Conversion**: Seamless workflow from quotes
- **Order Status Management**: Complete order lifecycle tracking
- **Delivery Management**: Shipping and delivery coordination
- **Invoice Generation**: Professional invoice creation

### 6. Task Management
- **Assignment System**: Task delegation to team members
- **Priority Management**: Four-level priority system
- **Due Date Tracking**: Deadline monitoring and alerts
- **Status Updates**: Progress tracking and completion monitoring

## Data Flow

### 1. Authentication Flow
```
User Login -> Role Verification -> Tenant Assignment -> Session Creation -> Dashboard Access
```

### 2. Quote Generation Flow
```
Customer Selection -> Product Addition -> Line Item Creation -> Approval Workflow -> PDF Generation -> Customer Delivery
```

### 3. Order Processing Flow
```
Quote Acceptance -> Order Creation -> Item Verification -> Processing -> Shipping -> Delivery -> Completion
```

### 4. Multi-Tenant Data Access
```
User Request -> Tenant Verification -> Data Filtering by tenant_id -> Response Delivery
```

## External Dependencies

### Core Dependencies
- **Flask 3.1.1**: Web application framework
- **SQLAlchemy 2.0+**: Database ORM and migrations
- **PostgreSQL**: Primary database system (Neon.tech hosted)
- **Gunicorn**: WSGI HTTP Server for production deployment

### Authentication & Security
- **Flask-Login 0.6.3**: User session management
- **Werkzeug**: Password hashing and security utilities
- **Flask-WTF**: CSRF protection and form handling

### Internationalization
- **Flask-Babel 4.0.0**: Multi-language support
- **Babel**: Translation file management

### Document Generation
- **FPDF2 2.8.3**: PDF generation for quotes and invoices

### Frontend Libraries (CDN)
- **Bootstrap 5.3.0**: CSS framework
- **Feather Icons**: Icon library

## Deployment Strategy

### Production Environment
- **Platform**: Replit Autoscale deployment
- **Web Server**: Gunicorn with multiple workers
- **Database**: PostgreSQL on Neon.tech with SSL
- **Static Files**: Served through Flask in production
- **Session Security**: Secure cookies with HTTPOnly flags

### Environment Configuration
- **Database URL**: Configured via environment variables
- **Session Secrets**: Environment-based security keys
- **Email Configuration**: SMTP settings for notifications (optional)
- **Babel Settings**: Locale and timezone configuration

### Security Measures
- **CSRF Protection**: Flask-WTF token validation
- **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries
- **Session Security**: Secure cookie configuration
- **Password Hashing**: Werkzeug secure password storage
- **Proxy Headers**: ProxyFix middleware for production deployment

## Changelog

Changelog:
- June 18, 2025. Initial setup
- June 18, 2025. Redesigned AI interface from technical "agents dashboard" to user-friendly "AI Assistant" focused on practical email support and business communications
- June 19, 2025. Set up git workflow structure for collaboration between Cursor IDE and Replit Agent, including branching strategy and conflict prevention guidelines
- June 19, 2025. Integrated comprehensive Kanban task management system with drag & drop functionality, role-based permissions, multiple boards, and auto-membership for board creators
- June 19, 2025. Conducted comprehensive CTO technical review and fixed critical agent dashboard template issues that were causing 500 errors

## User Preferences

Preferred communication style: Simple, everyday language.