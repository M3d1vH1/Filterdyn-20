
from datetime import datetime, timezone, timedelta
from models import Task, User, Asset, WaterQualityReading
from app import db
import json

class AutomationService:
    
    @staticmethod
    def check_business_hours():
        """Check if current time is within business hours (9 AM - 5 PM weekdays)"""
        now = datetime.now()
        if now.weekday() >= 5:  # Weekend
            return False
        if now.hour < 9 or now.hour >= 17:  # Outside 9-5
            return False
        return True
    
    @staticmethod
    def create_service_reminders():
        """Create automated service reminders for assets"""
        from models_extended import Asset
        
        today = datetime.now(timezone.utc).date()
        upcoming_services = Asset.query.filter(
            Asset.next_service_date <= today + timedelta(days=7),
            Asset.status == 'active'
        ).all()
        
        for asset in upcoming_services:
            # Check if reminder already exists
            existing_task = Task.query.filter_by(
                tenant_id=asset.tenant_id,
                category='service_reminder',
                customer_id=asset.customer_id
            ).filter(
                Task.title.like(f'%{asset.serial_number}%')
            ).first()
            
            if not existing_task:
                task = Task(
                    tenant_id=asset.tenant_id,
                    created_by=1,  # System user
                    title=f'Service Due: {asset.model} ({asset.serial_number})',
                    description=f'Scheduled service for {asset.model} at {asset.customer.name}. '
                               f'Location: {asset.location}. Last service: {asset.last_service_date}',
                    category='service_reminder',
                    priority='high',
                    customer_id=asset.customer_id,
                    due_date=asset.next_service_date,
                    is_automated=True,
                    business_hours_only=True,
                    auto_assign_role='manager'
                )
                
                # Auto-assign to a manager
                manager = User.query.filter_by(
                    tenant_id=asset.tenant_id,
                    role='manager',
                    is_active=True
                ).first()
                
                if manager:
                    task.assigned_to = manager.id
                
                db.session.add(task)
        
        db.session.commit()
    
    @staticmethod
    def check_water_quality_alerts():
        """Check for water quality readings that exceed limits"""
        from models_extended import WaterQualityReading, Asset
        
        # Get recent readings that might be problematic
        recent_readings = WaterQualityReading.query.filter(
            WaterQualityReading.reading_date >= datetime.now(timezone.utc) - timedelta(days=1),
            WaterQualityReading.is_alarm == False
        ).all()
        
        for reading in recent_readings:
            alerts = []
            
            # Check conductivity against asset limit
            if (reading.conductivity and reading.asset.conductivity_limit and 
                reading.conductivity > reading.asset.conductivity_limit):
                alerts.append(f'Conductivity exceeded limit: {reading.conductivity} μS/cm')
            
            # Check pH levels
            if reading.ph_level:
                if reading.ph_level < 6.5 or reading.ph_level > 8.5:
                    alerts.append(f'pH out of range: {reading.ph_level}')
            
            if alerts:
                task = Task(
                    tenant_id=reading.tenant_id,
                    created_by=1,  # System user
                    assigned_to=reading.recorded_by,
                    title=f'Water Quality Alert: {reading.asset.serial_number}',
                    description=f'Quality issues detected at {reading.asset.customer.name}:\n' + 
                               '\n'.join(alerts) + f'\n\nReading taken: {reading.reading_date}',
                    category='automated_reminder',
                    priority='urgent',
                    customer_id=reading.asset.customer_id,
                    due_date=datetime.now(timezone.utc) + timedelta(hours=4),
                    is_automated=True,
                    business_hours_only=True
                )
                
                db.session.add(task)
                reading.is_alarm = True
        
        db.session.commit()
    
    @staticmethod
    def process_automated_tasks():
        """Main automation processor - call this from a scheduler"""
        if AutomationService.check_business_hours():
            AutomationService.create_service_reminders()
            AutomationService.check_water_quality_alerts()
