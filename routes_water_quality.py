"""
Water Quality Management Routes
==============================

Flask routes for water quality data entry and monitoring.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc
from datetime import datetime, timedelta
from app import db
from models import WaterQualityData, Equipment, Customer, Tenant
from forms_water_quality import WaterQualityDataForm
from flask_babel import gettext as _

water_quality_bp = Blueprint('water_quality', __name__, url_prefix='/water-quality')

@water_quality_bp.route('/')
@login_required
def index():
    """Water quality dashboard"""
    # Get recent measurements
    recent_measurements = WaterQualityData.query.filter_by(
        tenant_id=current_user.tenant_id
    ).order_by(desc(WaterQualityData.sample_date)).limit(10).all()
    
    # Get equipment with alerts
    alerts = []
    for measurement in recent_measurements:
        if measurement.alert_triggered:
            alerts.append(measurement)
    
    return render_template('water_quality/dashboard.html',
                         recent_measurements=recent_measurements,
                         alerts=alerts)

@water_quality_bp.route('/data-entry', methods=['GET', 'POST'])
@login_required
def data_entry():
    """Water quality data entry form"""
    form = WaterQualityDataForm()
    
    # Populate equipment choices
    equipment_choices = [(0, _('Select Equipment'))]
    equipment_list = Equipment.query.filter_by(
        tenant_id=current_user.tenant_id,
        is_active=True
    ).all()
    
    for equipment in equipment_list:
        customer = Customer.query.get(equipment.customer_id)
        label = f"{equipment.equipment_number} - {customer.name if customer else 'Unknown'}"
        equipment_choices.append((equipment.id, label))
    
    form.equipment_id.choices = equipment_choices
    
    if form.validate_on_submit():
        # Create new water quality data record
        measurement = WaterQualityData(
            tenant_id=current_user.tenant_id,
            customer_id=Equipment.query.get(form.equipment_id.data).customer_id,
            equipment_id=form.equipment_id.data,
            sample_date=form.measurement_date.data,
            ph_level=form.ph.data,
            conductivity=form.conductivity.data,
            temperature=form.temperature.data,
            turbidity=form.turbidity.data,
            analyzed_by=current_user.username,
            notes=form.notes.data if hasattr(form, 'notes') else None
        )
        
        # Check for alerts based on thresholds
        measurement.alert_triggered = _check_quality_thresholds(measurement)
        
        db.session.add(measurement)
        db.session.commit()
        
        flash(_('Water quality data recorded successfully'), 'success')
        return redirect(url_for('water_quality.index'))
    
    return render_template('water_quality/data_entry.html', form=form)

@water_quality_bp.route('/measurements')
@login_required
def measurements():
    """List all water quality measurements"""
    page = request.args.get('page', 1, type=int)
    equipment_id = request.args.get('equipment_id', type=int)
    
    query = WaterQualityData.query.filter_by(tenant_id=current_user.tenant_id)
    
    if equipment_id:
        query = query.filter_by(equipment_id=equipment_id)
    
    measurements = query.order_by(desc(WaterQualityData.sample_date)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get equipment list for filter
    equipment_list = Equipment.query.filter_by(
        tenant_id=current_user.tenant_id,
        is_active=True
    ).all()
    
    return render_template('water_quality/measurements.html',
                         measurements=measurements,
                         equipment_list=equipment_list,
                         selected_equipment=equipment_id)

@water_quality_bp.route('/alerts')
@login_required
def alerts():
    """View water quality alerts"""
    alert_measurements = WaterQualityData.query.filter_by(
        tenant_id=current_user.tenant_id,
        alert_triggered=True
    ).order_by(desc(WaterQualityData.sample_date)).limit(50).all()
    
    return render_template('water_quality/alerts.html',
                         alert_measurements=alert_measurements)

@water_quality_bp.route('/api/equipment/<int:equipment_id>/recent')
@login_required
def api_recent_measurements(equipment_id):
    """API endpoint for recent measurements of specific equipment"""
    measurements = WaterQualityData.query.filter_by(
        tenant_id=current_user.tenant_id,
        equipment_id=equipment_id
    ).order_by(desc(WaterQualityData.sample_date)).limit(10).all()
    
    data = []
    for m in measurements:
        data.append({
            'date': m.sample_date.isoformat(),
            'ph': float(m.ph_level) if m.ph_level else None,
            'conductivity': float(m.conductivity) if m.conductivity else None,
            'temperature': float(m.temperature) if m.temperature else None,
            'turbidity': float(m.turbidity) if m.turbidity else None,
            'alert': m.alert_triggered
        })
    
    return jsonify(data)

def _check_quality_thresholds(measurement):
    """Check if measurement values exceed quality thresholds"""
    alert_triggered = False
    
    # pH thresholds (6.5-8.5 normal range)
    if measurement.ph_level:
        if measurement.ph_level < 6.0 or measurement.ph_level > 9.0:
            alert_triggered = True
    
    # Conductivity thresholds (equipment-specific)
    if measurement.conductivity:
        equipment = Equipment.query.get(measurement.equipment_id)
        if equipment and equipment.equipment_type == 'deionization_column':
            # For deionization columns, conductivity should be very low
            if measurement.conductivity > 10.0:  # μS/cm
                alert_triggered = True
    
    # Turbidity thresholds
    if measurement.turbidity:
        if measurement.turbidity > 1.0:  # NTU
            alert_triggered = True
    
    return alert_triggered