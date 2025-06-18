
from app import db
from datetime import datetime, timezone
from models import Tenant, User, Customer

class AssetCategory(db.Model):
    __tablename__ = 'asset_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
class Asset(db.Model):
    __tablename__ = 'assets'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('asset_categories.id'), nullable=False)
    
    # Asset identification
    serial_number = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    
    # Location and status
    location = db.Column(db.String(200))
    status = db.Column(db.String(50), default='active')  # active, maintenance, retired
    
    # Installation and service
    installation_date = db.Column(db.DateTime)
    last_service_date = db.Column(db.DateTime)
    next_service_date = db.Column(db.DateTime)
    
    # Water quality specific fields
    capacity_liters = db.Column(db.Numeric(10, 2))
    resin_type = db.Column(db.String(100))
    conductivity_limit = db.Column(db.Numeric(10, 4))
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    customer = db.relationship('Customer', backref='assets')
    category = db.relationship('AssetCategory', backref='assets')
    
class WaterQualityReading(db.Model):
    __tablename__ = 'water_quality_readings'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Water quality parameters
    conductivity = db.Column(db.Numeric(10, 4))  # μS/cm
    ph_level = db.Column(db.Numeric(4, 2))
    tds = db.Column(db.Numeric(10, 2))  # Total dissolved solids
    chlorine = db.Column(db.Numeric(6, 3))
    temperature = db.Column(db.Numeric(5, 2))
    
    # Reading metadata
    reading_date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)
    is_alarm = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    asset = db.relationship('Asset', backref='quality_readings')
    recorder = db.relationship('User', backref='quality_readings')
