"""
Water Quality and Asset Management Forms
=======================================
"""

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, TextAreaField, DateTimeField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from flask_babel import lazy_gettext as _l
from datetime import datetime


class WaterQualityDataForm(FlaskForm):
    """Form for water quality data entry"""
    equipment_id = SelectField(_l('Equipment'), coerce=int, validators=[DataRequired()])
    measurement_date = DateTimeField(_l('Measurement Date'), 
                                   validators=[DataRequired()], 
                                   default=datetime.now,
                                   format='%Y-%m-%dT%H:%M')
    
    # Water quality parameters
    conductivity = FloatField(_l('Conductivity (μS/cm)'), 
                            validators=[Optional(), NumberRange(min=0, max=1000)],
                            render_kw={'step': '0.01'})
    
    resistivity = FloatField(_l('Resistivity (MΩ·cm)'), 
                           validators=[Optional(), NumberRange(min=0, max=100)],
                           render_kw={'step': '0.01'})
    
    ph = FloatField(_l('pH Level'), 
                   validators=[Optional(), NumberRange(min=0, max=14)],
                   render_kw={'step': '0.1'})
    
    temperature = FloatField(_l('Temperature (°C)'), 
                           validators=[Optional(), NumberRange(min=-10, max=100)],
                           render_kw={'step': '0.1'})
    
    tds = FloatField(_l('TDS (mg/L)'), 
                    validators=[Optional(), NumberRange(min=0, max=1000)],
                    render_kw={'step': '0.1'})
    
    turbidity = FloatField(_l('Turbidity (NTU)'), 
                         validators=[Optional(), NumberRange(min=0, max=100)],
                         render_kw={'step': '0.01'})
    
    chlorine = FloatField(_l('Chlorine (mg/L)'), 
                        validators=[Optional(), NumberRange(min=0, max=10)],
                        render_kw={'step': '0.01'})
    
    pressure = FloatField(_l('Pressure (bar)'), 
                        validators=[Optional(), NumberRange(min=0, max=50)],
                        render_kw={'step': '0.1'})
    
    flow_rate = FloatField(_l('Flow Rate (L/min)'), 
                         validators=[Optional(), NumberRange(min=0, max=1000)],
                         render_kw={'step': '0.1'})
    
    # Additional fields
    notes = TextAreaField(_l('Notes'), validators=[Optional(), Length(max=500)])
    alert_threshold_exceeded = BooleanField(_l('Alert Threshold Exceeded'))
    measured_by = StringField(_l('Measured By'), validators=[Optional(), Length(max=100)])


class EquipmentForm(FlaskForm):
    """Enhanced form for equipment/asset management"""
    customer_id = SelectField(_l('Customer'), coerce=int, validators=[DataRequired()])
    equipment_number = StringField(_l('Equipment Number'), 
                                 validators=[DataRequired(), Length(max=50)])
    
    equipment_type = SelectField(_l('Equipment Type'), choices=[
        ('deionization_column', _l('Deionization Column')),
        ('reverse_osmosis', _l('Reverse Osmosis System')),
        ('water_softener', _l('Water Softener')),
        ('filtration_system', _l('Filtration System')),
        ('uv_sterilizer', _l('UV Sterilizer')),
        ('pressure_vessel', _l('Pressure Vessel')),
        ('pump_system', _l('Pump System')),
        ('control_panel', _l('Control Panel')),
        ('other', _l('Other'))
    ], validators=[DataRequired()])
    
    # Asset tracking details
    serial_number = StringField(_l('Serial Number'), validators=[Optional(), Length(max=100)])
    manufacturer = StringField(_l('Manufacturer'), validators=[Optional(), Length(max=100)])
    model = StringField(_l('Model'), validators=[Optional(), Length(max=100)])
    manufacture_date = DateTimeField(_l('Manufacture Date'), validators=[Optional()], format='%Y-%m-%d')
    installation_date = DateTimeField(_l('Installation Date'), validators=[Optional()], format='%Y-%m-%d')
    warranty_expiry = DateTimeField(_l('Warranty Expiry'), validators=[Optional()], format='%Y-%m-%d')
    
    # Operational details
    capacity = FloatField(_l('Capacity'), validators=[Optional(), NumberRange(min=0)])
    capacity_unit = SelectField(_l('Capacity Unit'), choices=[
        ('L/h', _l('Liters per Hour')),
        ('m3/h', _l('Cubic Meters per Hour')),
        ('L/min', _l('Liters per Minute')),
        ('GPM', _l('Gallons per Minute')),
        ('kg', _l('Kilograms')),
        ('L', _l('Liters'))
    ], validators=[Optional()])
    
    operating_pressure = FloatField(_l('Operating Pressure (bar)'), 
                                  validators=[Optional(), NumberRange(min=0, max=100)])
    
    # Service intervals
    preventive_maintenance_interval = IntegerField(_l('Preventive Maintenance (days)'), 
                                                 validators=[Optional(), NumberRange(min=1, max=3650)],
                                                 default=90)
    
    filter_replacement_interval = IntegerField(_l('Filter Replacement (days)'), 
                                             validators=[Optional(), NumberRange(min=1, max=365)],
                                             default=180)
    
    resin_replacement_interval = IntegerField(_l('Resin Replacement (days)'), 
                                            validators=[Optional(), NumberRange(min=1, max=3650)],
                                            default=365)
    
    # Status and location
    status = SelectField(_l('Status'), choices=[
        ('active', _l('Active')),
        ('maintenance', _l('Under Maintenance')),
        ('offline', _l('Offline')),
        ('decommissioned', _l('Decommissioned'))
    ], validators=[DataRequired()], default='active')
    
    location = StringField(_l('Location'), validators=[Optional(), Length(max=200)])
    room = StringField(_l('Room/Area'), validators=[Optional(), Length(max=100)])
    
    # Documentation
    specifications = TextAreaField(_l('Technical Specifications'), validators=[Optional()])
    notes = TextAreaField(_l('Notes'), validators=[Optional(), Length(max=1000)])


class ServiceReportForm(FlaskForm):
    """Form for creating service reports"""
    equipment_id = SelectField(_l('Equipment'), coerce=int, validators=[DataRequired()])
    service_type = SelectField(_l('Service Type'), choices=[
        ('preventive_maintenance', _l('Preventive Maintenance')),
        ('corrective_maintenance', _l('Corrective Maintenance')),
        ('emergency_repair', _l('Emergency Repair')),
        ('installation', _l('Installation')),
        ('commissioning', _l('Commissioning')),
        ('inspection', _l('Inspection')),
        ('filter_replacement', _l('Filter Replacement')),
        ('resin_replacement', _l('Resin Replacement')),
        ('calibration', _l('Calibration')),
        ('upgrade', _l('Upgrade'))
    ], validators=[DataRequired()])
    
    service_date = DateTimeField(_l('Service Date'), 
                               validators=[DataRequired()], 
                               default=datetime.now,
                               format='%Y-%m-%dT%H:%M')
    
    technician_name = StringField(_l('Technician Name'), 
                                validators=[DataRequired(), Length(max=100)])
    
    # Service details
    work_performed = TextAreaField(_l('Work Performed'), 
                                 validators=[DataRequired(), Length(max=2000)])
    
    parts_replaced = TextAreaField(_l('Parts Replaced'), 
                                 validators=[Optional(), Length(max=1000)])
    
    next_service_date = DateTimeField(_l('Next Service Date'), 
                                    validators=[Optional()], 
                                    format='%Y-%m-%d')
    
    # Water quality measurements before/after service
    conductivity_before = FloatField(_l('Conductivity Before (μS/cm)'), 
                                   validators=[Optional(), NumberRange(min=0)])
    conductivity_after = FloatField(_l('Conductivity After (μS/cm)'), 
                                  validators=[Optional(), NumberRange(min=0)])
    
    resistivity_before = FloatField(_l('Resistivity Before (MΩ·cm)'), 
                                  validators=[Optional(), NumberRange(min=0)])
    resistivity_after = FloatField(_l('Resistivity After (MΩ·cm)'), 
                                 validators=[Optional(), NumberRange(min=0)])
    
    # Service outcome
    service_status = SelectField(_l('Service Status'), choices=[
        ('completed', _l('Completed Successfully')),
        ('partial', _l('Partially Completed')),
        ('failed', _l('Failed')),
        ('requires_parts', _l('Requires Additional Parts')),
        ('requires_followup', _l('Requires Follow-up'))
    ], validators=[DataRequired()], default='completed')
    
    customer_signature = BooleanField(_l('Customer Signature Obtained'))
    
    recommendations = TextAreaField(_l('Recommendations'), 
                                  validators=[Optional(), Length(max=1000)])
    
    notes = TextAreaField(_l('Additional Notes'), 
                        validators=[Optional(), Length(max=1000)])


class TenderDossierForm(FlaskForm):
    """Form for Greek public tender management"""
    tender_number = StringField(_l('Tender Number'), 
                              validators=[DataRequired(), Length(max=100)])
    
    contracting_authority = StringField(_l('Contracting Authority'), 
                                      validators=[DataRequired(), Length(max=200)])
    
    tender_title = StringField(_l('Tender Title'), 
                             validators=[DataRequired(), Length(max=300)])
    
    tender_type = SelectField(_l('Tender Type'), choices=[
        ('open', _l('Open Procedure')),
        ('restricted', _l('Restricted Procedure')),
        ('negotiated', _l('Negotiated Procedure')),
        ('competitive_dialogue', _l('Competitive Dialogue')),
        ('innovation_partnership', _l('Innovation Partnership'))
    ], validators=[DataRequired()])
    
    cpv_code = StringField(_l('CPV Code'), validators=[Optional(), Length(max=50)])
    
    estimated_value = FloatField(_l('Estimated Value (€)'), 
                               validators=[Optional(), NumberRange(min=0)])
    
    submission_deadline = DateTimeField(_l('Submission Deadline'), 
                                      validators=[DataRequired()], 
                                      format='%Y-%m-%dT%H:%M')
    
    opening_date = DateTimeField(_l('Opening Date'), 
                               validators=[Optional()], 
                               format='%Y-%m-%dT%H:%M')
    
    # Technical requirements
    technical_requirements = TextAreaField(_l('Technical Requirements'), 
                                         validators=[Optional(), Length(max=5000)])
    
    # Documentation checklist
    technical_offer_required = BooleanField(_l('Technical Offer Required'), default=True)
    financial_offer_required = BooleanField(_l('Financial Offer Required'), default=True)
    guarantee_required = BooleanField(_l('Participation Guarantee Required'))
    certificates_required = TextAreaField(_l('Required Certificates'), 
                                        validators=[Optional(), Length(max=1000)])
    
    # Our response
    participation_status = SelectField(_l('Participation Status'), choices=[
        ('considering', _l('Considering')),
        ('preparing', _l('Preparing Offer')),
        ('submitted', _l('Offer Submitted')),
        ('declined', _l('Declined')),
        ('won', _l('Won')),
        ('lost', _l('Lost'))
    ], validators=[DataRequired()], default='considering')
    
    assigned_team = StringField(_l('Assigned Team'), validators=[Optional(), Length(max=200)])
    
    our_offer_value = FloatField(_l('Our Offer Value (€)'), 
                               validators=[Optional(), NumberRange(min=0)])
    
    notes = TextAreaField(_l('Notes'), validators=[Optional(), Length(max=2000)])