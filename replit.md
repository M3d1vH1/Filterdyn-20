# Filterdyn Operations Suite - Multi-Tenant Business Management Platform

## Overview

The Filterdyn Operations Suite is a comprehensive multi-tenant business management platform specifically designed for water treatment solutions companies. Built with Flask and PostgreSQL, it provides complete customer relationship management, product catalog management, quote generation, order processing, and task management capabilities with bilingual support (English/Greek).

## System Architecture

### Backend Architecture
- **Framework**: Flask 3.1.1 with modular blueprint structure
- **Database**: PostgreSQL with SQLAlchemy ORM and Flask-Migrate for schema management
- **Authentication**: Flask-Login with role-based access control (superadmin, admin, manager, user)
- **Multi-tenancy**: Complete tenant isolation using tenant_id foreign keys across all models
- **Internationalization**: Flask-Babel with English/Greek language support

### Frontend Architecture
- **UI Framework**: Bootstrap 5.3.0 with custom Filterdyn theming
- **Icons**: Feather Icons for consistent iconography
- **JavaScript**: Vanilla JS with Bootstrap components for interactivity
- **Templates**: Jinja2 with template inheritance and internationalization

### Data Storage
- **Primary Database**: PostgreSQL with connection pooling and pre-ping configuration
- **Session Management**: Server-side sessions with secure configuration
- **File Storage**: Local file system with configurable upload directory

## Key Components

### 1. Multi-Agent System
- **Communication & AI Agent**: Gmail API integration, AI-powered email generation with OpenAI
- **Operations & Data Agent**: Service reminders, water quality monitoring, automated alerts
- **Platform & Integration Agent**: Analytics dashboard, API endpoints, external integrations
- **Testing & Quality Agent**: Automated testing, quality assurance, test reporting
- **Agent Coordinator**: Unified management, system health monitoring, automated workflows

### 2. Multi-Tenant User Management
- Tenant isolation with subdomain-based access
- Four-tier role system with granular permissions
- User profile management with contact information
- Session management with remember-me functionality

### 2. Customer Relationship Management
- Complete customer profiles with company and contact information
- Industry classification and tax information
- Customer search and pagination
- Activity tracking and notes

### 3. Product Catalog System
- Hierarchical product categories with multilingual names
- Detailed product information (codes, descriptions, pricing)
- Multilingual product data (English/Greek)
- Product search and filtering by category

### 4. Quote Management System
- Professional quote generation with sequential numbering
- Multi-line item quotes with quantity and pricing calculations
- Quote approval workflow (draft → pending → approved → sent)
- PDF generation with company branding
- Quote status tracking and expiration management

### 5. Order Processing
- Order creation from approved quotes or standalone
- Order status tracking (pending → processing → shipped → delivered)
- Delivery date management and customer notifications
- Order history and search functionality

### 6. Task Management
- Task assignment and tracking system
- Priority levels (low, medium, high, urgent)
- Due date management with overdue notifications
- Task status workflow (pending → in_progress → completed)

## Data Flow

### Authentication Flow
1. User login via username/password
2. Role-based access validation
3. Tenant context establishment
4. Session creation with security headers

### Quote Generation Flow
1. Customer selection and basic information entry
2. Product line item addition with pricing
3. Automatic calculations (subtotals, taxes, totals)
4. Quote approval workflow
5. PDF generation for customer delivery

### Order Processing Flow
1. Order creation (from quote or standalone)
2. Inventory considerations and scheduling
3. Status updates throughout fulfillment
4. Customer communication and delivery tracking

## External Dependencies

### Runtime Dependencies
- **Flask Ecosystem**: Flask, Flask-SQLAlchemy, Flask-Login, Flask-Migrate, Flask-Babel, Flask-WTF
- **Database**: psycopg2-binary for PostgreSQL connectivity
- **PDF Generation**: fpdf2 for professional document creation
- **Forms**: WTForms with email validation
- **Server**: Gunicorn for production deployment

### Development Tools
- **Migration**: Alembic through Flask-Migrate
- **Internationalization**: Babel for message extraction and compilation
- **Security**: Werkzeug for password hashing and security utilities

## Deployment Strategy

### Development Environment
- SQLite fallback for local development
- Debug mode with hot reloading
- Development server on port 5000

### Production Environment
- PostgreSQL with Neon cloud hosting
- Gunicorn WSGI server with autoscaling
- Proxy fix middleware for proper header handling
- Session security with secure cookies
- Environment-based configuration management

### Database Configuration
- Connection pooling with 300-second recycle
- Pre-ping health checks
- Automatic migration support
- Multi-tenant data isolation

## Changelog

- June 18, 2025: Initial setup and multi-agent system integration
  - Integrated comprehensive multi-agent system with Gmail API, Google Gemini, and analytics
  - Added Communication & AI Agent for email automation and AI-powered content generation using Gemini
  - Added Operations & Data Agent for service reminders and water quality monitoring
  - Added Platform & Integration Agent for analytics dashboard and API endpoints
  - Added Testing & Quality Agent for automated testing and quality assurance
  - Created agent coordination system with unified management interface
  - Built Flask routes and templates for agent system UI integration
  - Migrated AI provider from OpenAI to Google Gemini API for improved performance
  - Installed dependencies: Google APIs, Gemini AI, pandas, numpy, matplotlib, seaborn

## User Preferences

Preferred communication style: Simple, everyday language.