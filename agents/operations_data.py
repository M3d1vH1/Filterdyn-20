"""
Operations & Data Agent
======================

Handles service reports, automated reminders, data analysis, and operational insights.
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import sqlite3
import psycopg2
from urllib.parse import urlparse
import csv

try:
    import pandas as pd
    import numpy as np
    from matplotlib import pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False


@dataclass
class ServiceReminder:
    """Service reminder data structure"""
    equipment_id: int
    equipment_number: str
    customer_name: str
    customer_email: str
    last_service_date: datetime
    next_service_date: datetime
    service_type: str
    priority: str  # low, medium, high, urgent
    days_until_due: int


@dataclass
class WaterQualityAlert:
    """Water quality alert data structure"""
    equipment_id: int
    equipment_number: str
    customer_name: str
    parameter: str
    value: float
    threshold: float
    alert_type: str  # warning, critical
    timestamp: datetime


class OperationsDataAgent:
    """Agent for handling operations data, service reports, and automated reminders"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/filterdyn')
        self.reminder_config = self._load_reminder_config()
        self.quality_thresholds = self._load_quality_thresholds()
    
    def _load_reminder_config(self) -> Dict[str, Any]:
        """Load reminder configuration"""
        return {
            'deionization_column': {
                'preventive_maintenance_days': 90,
                'resin_replacement_days': 365,
                'regeneration_reminder_days': 30
            },
            'ro_system': {
                'preventive_maintenance_days': 180,
                'membrane_replacement_days': 730,
                'filter_replacement_days': 90
            },
            'filter': {
                'preventive_maintenance_days': 60,
                'filter_replacement_days': 180
            },
            'general': {
                'preventive_maintenance_days': 90
            }
        }
    
    def _load_quality_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Load water quality thresholds"""
        return {
            'conductivity': {
                'warning': 10.0,  # μS/cm
                'critical': 50.0
            },
            'resistivity': {
                'warning': 0.1,  # MΩ·cm
                'critical': 0.05
            },
            'ph': {
                'warning_low': 6.5,
                'warning_high': 8.5,
                'critical_low': 6.0,
                'critical_high': 9.0
            },
            'tds': {
                'warning': 10.0,  # mg/L
                'critical': 50.0
            },
            'turbidity': {
                'warning': 1.0,  # NTU
                'critical': 5.0
            }
        }
    
    def generate_service_reminders(self) -> List[ServiceReminder]:
        """Generate service reminders for all equipment"""
        reminders = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all active equipment with their last service dates
            query = """
            SELECT 
                e.id, e.equipment_number, e.equipment_type, e.last_service_date,
                c.name as customer_name, c.email as customer_email
            FROM equipment e
            JOIN customers c ON e.customer_id = c.id
            WHERE e.status = 'active'
            """
            
            cursor.execute(query)
            equipment_list = cursor.fetchall()
            
            for equipment in equipment_list:
                equipment_id, equipment_number, equipment_type, last_service_date, customer_name, customer_email = equipment
                
                # Parse last service date
                if last_service_date:
                    last_service = datetime.fromisoformat(last_service_date.replace('Z', '+00:00'))
                else:
                    # If no service history, use installation date
                    cursor.execute("SELECT installation_date FROM equipment WHERE id = ?", (equipment_id,))
                    install_date = cursor.fetchone()[0]
                    if install_date:
                        last_service = datetime.fromisoformat(install_date.replace('Z', '+00:00'))
                    else:
                        continue
                
                # Get reminder configuration for this equipment type
                config = self.reminder_config.get(equipment_type, self.reminder_config['general'])
                
                # Calculate next service dates
                pm_days = config.get('preventive_maintenance_days', 90)
                next_pm_date = last_service + timedelta(days=pm_days)
                days_until_due = (next_pm_date - datetime.now()).days
                
                if days_until_due <= 30:  # Only include reminders within 30 days
                    priority = 'urgent' if days_until_due <= 7 else 'high' if days_until_due <= 14 else 'medium'
                    
                    reminder = ServiceReminder(
                        equipment_id=equipment_id,
                        equipment_number=equipment_number,
                        customer_name=customer_name,
                        customer_email=customer_email,
                        last_service_date=last_service,
                        next_service_date=next_pm_date,
                        service_type='preventive_maintenance',
                        priority=priority,
                        days_until_due=days_until_due
                    )
                    reminders.append(reminder)
                
                # Check for resin replacement (deionization columns)
                if equipment_type == 'deionization_column':
                    resin_days = config.get('resin_replacement_days', 365)
                    next_resin_date = last_service + timedelta(days=resin_days)
                    resin_days_until_due = (next_resin_date - datetime.now()).days
                    
                    if resin_days_until_due <= 60:
                        priority = 'urgent' if resin_days_until_due <= 30 else 'high'
                        
                        reminder = ServiceReminder(
                            equipment_id=equipment_id,
                            equipment_number=equipment_number,
                            customer_name=customer_name,
                            customer_email=customer_email,
                            last_service_date=last_service,
                            next_service_date=next_resin_date,
                            service_type='resin_replacement',
                            priority=priority,
                            days_until_due=resin_days_until_due
                        )
                        reminders.append(reminder)
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error generating service reminders: {e}")
        
        return reminders
    
    def check_water_quality_alerts(self) -> List[WaterQualityAlert]:
        """Check for water quality alerts based on recent measurements"""
        alerts = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent water quality measurements (last 24 hours)
            query = """
            SELECT 
                wqd.equipment_id, wqd.measurement_date,
                wqd.conductivity, wqd.resistivity, wqd.ph, wqd.tds, wqd.turbidity,
                e.equipment_number, c.name as customer_name
            FROM water_quality_data wqd
            JOIN equipment e ON wqd.equipment_id = e.id
            JOIN customers c ON e.customer_id = c.id
            WHERE wqd.measurement_date >= datetime('now', '-1 day')
            ORDER BY wqd.measurement_date DESC
            """
            
            cursor.execute(query)
            measurements = cursor.fetchall()
            
            for measurement in measurements:
                equipment_id, measurement_date, conductivity, resistivity, ph, tds, turbidity, equipment_number, customer_name = measurement
                
                # Check conductivity
                if conductivity:
                    if conductivity > self.quality_thresholds['conductivity']['critical']:
                        alerts.append(WaterQualityAlert(
                            equipment_id=equipment_id,
                            equipment_number=equipment_number,
                            customer_name=customer_name,
                            parameter='conductivity',
                            value=conductivity,
                            threshold=self.quality_thresholds['conductivity']['critical'],
                            alert_type='critical',
                            timestamp=datetime.fromisoformat(measurement_date.replace('Z', '+00:00'))
                        ))
                    elif conductivity > self.quality_thresholds['conductivity']['warning']:
                        alerts.append(WaterQualityAlert(
                            equipment_id=equipment_id,
                            equipment_number=equipment_number,
                            customer_name=customer_name,
                            parameter='conductivity',
                            value=conductivity,
                            threshold=self.quality_thresholds['conductivity']['warning'],
                            alert_type='warning',
                            timestamp=datetime.fromisoformat(measurement_date.replace('Z', '+00:00'))
                        ))
                
                # Check resistivity
                if resistivity:
                    if resistivity < self.quality_thresholds['resistivity']['critical']:
                        alerts.append(WaterQualityAlert(
                            equipment_id=equipment_id,
                            equipment_number=equipment_number,
                            customer_name=customer_name,
                            parameter='resistivity',
                            value=resistivity,
                            threshold=self.quality_thresholds['resistivity']['critical'],
                            alert_type='critical',
                            timestamp=datetime.fromisoformat(measurement_date.replace('Z', '+00:00'))
                        ))
                    elif resistivity < self.quality_thresholds['resistivity']['warning']:
                        alerts.append(WaterQualityAlert(
                            equipment_id=equipment_id,
                            equipment_number=equipment_number,
                            customer_name=customer_name,
                            parameter='resistivity',
                            value=resistivity,
                            threshold=self.quality_thresholds['resistivity']['warning'],
                            alert_type='warning',
                            timestamp=datetime.fromisoformat(measurement_date.replace('Z', '+00:00'))
                        ))
                
                # Check pH
                if ph:
                    if ph < self.quality_thresholds['ph']['critical_low'] or ph > self.quality_thresholds['ph']['critical_high']:
                        alerts.append(WaterQualityAlert(
                            equipment_id=equipment_id,
                            equipment_number=equipment_number,
                            customer_name=customer_name,
                            parameter='ph',
                            value=ph,
                            threshold=self.quality_thresholds['ph']['critical_low'] if ph < self.quality_thresholds['ph']['critical_low'] else self.quality_thresholds['ph']['critical_high'],
                            alert_type='critical',
                            timestamp=datetime.fromisoformat(measurement_date.replace('Z', '+00:00'))
                        ))
                    elif ph < self.quality_thresholds['ph']['warning_low'] or ph > self.quality_thresholds['ph']['warning_high']:
                        alerts.append(WaterQualityAlert(
                            equipment_id=equipment_id,
                            equipment_number=equipment_number,
                            customer_name=customer_name,
                            parameter='ph',
                            value=ph,
                            threshold=self.quality_thresholds['ph']['warning_low'] if ph < self.quality_thresholds['ph']['warning_low'] else self.quality_thresholds['ph']['warning_high'],
                            alert_type='warning',
                            timestamp=datetime.fromisoformat(measurement_date.replace('Z', '+00:00'))
                        ))
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error checking water quality alerts: {e}")
        
        return alerts
    
    def generate_service_report_template(self, equipment_id: int, service_type: str) -> Dict[str, Any]:
        """Generate a service report template for specific equipment"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get equipment details
            cursor.execute("""
                SELECT e.*, c.name as customer_name, c.address as customer_address
                FROM equipment e
                JOIN customers c ON e.customer_id = c.id
                WHERE e.id = ?
            """, (equipment_id,))
            
            equipment_data = cursor.fetchone()
            if not equipment_data:
                return {}
            
            # Get recent water quality data
            cursor.execute("""
                SELECT measurement_date, conductivity, resistivity, ph, temperature, tds
                FROM water_quality_data
                WHERE equipment_id = ?
                ORDER BY measurement_date DESC
                LIMIT 5
            """, (equipment_id,))
            
            recent_measurements = cursor.fetchall()
            
            # Get service history
            cursor.execute("""
                SELECT service_date, service_type, service_description, next_service_date
                FROM service_reports
                WHERE equipment_id = ?
                ORDER BY service_date DESC
                LIMIT 3
            """, (equipment_id,))
            
            service_history = cursor.fetchall()
            
            conn.close()
            
            # Generate template
            template = {
                'equipment_info': {
                    'equipment_number': equipment_data[2],
                    'equipment_type': equipment_data[3],
                    'model': equipment_data[5],
                    'serial_number': equipment_data[6],
                    'manufacturer': equipment_data[7],
                    'installation_location': equipment_data[9],
                    'installation_date': equipment_data[10]
                },
                'customer_info': {
                    'name': equipment_data[-2],
                    'address': equipment_data[-1]
                },
                'service_details': {
                    'service_type': service_type,
                    'service_date': datetime.now().strftime('%Y-%m-%d'),
                    'technician': 'To be filled',
                    'work_performed': '',
                    'parts_replaced': '',
                    'consumables_used': '',
                    'recommendations': '',
                    'next_service_date': ''
                },
                'measurements': {
                    'pre_service': {
                        'conductivity': '',
                        'resistivity': '',
                        'ph': '',
                        'temperature': '',
                        'tds': ''
                    },
                    'post_service': {
                        'conductivity': '',
                        'resistivity': '',
                        'ph': '',
                        'temperature': '',
                        'tds': ''
                    }
                },
                'recent_measurements': recent_measurements,
                'service_history': service_history
            }
            
            return template
            
        except Exception as e:
            print(f"❌ Error generating service report template: {e}")
            return {}
    
    def analyze_equipment_performance(self, equipment_id: int, days: int = 30) -> Dict[str, Any]:
        """Analyze equipment performance over a specified period"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get water quality data
            query = """
            SELECT measurement_date, conductivity, resistivity, ph, temperature, tds, turbidity
            FROM water_quality_data
            WHERE equipment_id = ? AND measurement_date >= datetime('now', '-{} days')
            ORDER BY measurement_date
            """.format(days)
            
            df = pd.read_sql_query(query, conn, params=(equipment_id,))
            
            if df.empty:
                return {'error': 'No data available for analysis'}
            
            # Convert measurement_date to datetime
            df['measurement_date'] = pd.to_datetime(df['measurement_date'])
            
            # Calculate statistics
            analysis = {
                'period_days': days,
                'total_measurements': len(df),
                'date_range': {
                    'start': df['measurement_date'].min().strftime('%Y-%m-%d'),
                    'end': df['measurement_date'].max().strftime('%Y-%m-%d')
                },
                'parameters': {}
            }
            
            # Analyze each parameter
            parameters = ['conductivity', 'resistivity', 'ph', 'temperature', 'tds', 'turbidity']
            
            for param in parameters:
                if param in df.columns and df[param].notna().any():
                    param_data = df[param].dropna()
                    if len(param_data) > 0:
                        analysis['parameters'][param] = {
                            'count': len(param_data),
                            'mean': float(param_data.mean()),
                            'std': float(param_data.std()),
                            'min': float(param_data.min()),
                            'max': float(param_data.max()),
                            'trend': self._calculate_trend(param_data)
                        }
            
            conn.close()
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing equipment performance: {e}")
            return {'error': str(e)}
    
    def _calculate_trend(self, data: pd.Series) -> str:
        """Calculate trend direction for a parameter"""
        if len(data) < 2:
            return 'insufficient_data'
        
        # Simple linear trend calculation
        x = np.arange(len(data))
        slope = np.polyfit(x, data, 1)[0]
        
        if slope > 0.01:
            return 'increasing'
        elif slope < -0.01:
            return 'decreasing'
        else:
            return 'stable'
    
    def generate_performance_report(self, equipment_id: int, output_format: str = 'json') -> str:
        """Generate a comprehensive performance report"""
        analysis = self.analyze_equipment_performance(equipment_id)
        
        if output_format == 'csv':
            return self._export_to_csv(analysis, equipment_id)
        elif output_format == 'json':
            return json.dumps(analysis, indent=2, default=str)
        else:
            return str(analysis)
    
    def _export_to_csv(self, analysis: Dict[str, Any], equipment_id: int) -> str:
        """Export analysis to CSV format"""
        try:
            filename = f"performance_report_equipment_{equipment_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Equipment Performance Report'])
                writer.writerow(['Equipment ID', equipment_id])
                writer.writerow(['Period (days)', analysis.get('period_days', 'N/A')])
                writer.writerow(['Total Measurements', analysis.get('total_measurements', 'N/A')])
                writer.writerow([])
                
                # Write parameter data
                writer.writerow(['Parameter', 'Count', 'Mean', 'Std Dev', 'Min', 'Max', 'Trend'])
                
                for param, stats in analysis.get('parameters', {}).items():
                    writer.writerow([
                        param,
                        stats.get('count', 'N/A'),
                        f"{stats.get('mean', 0):.2f}",
                        f"{stats.get('std', 0):.2f}",
                        f"{stats.get('min', 0):.2f}",
                        f"{stats.get('max', 0):.2f}",
                        stats.get('trend', 'N/A')
                    ])
            
            return filename
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return ""
    
    def create_automated_reminder_schedule(self) -> Dict[str, Any]:
        """Create a schedule for automated reminders"""
        reminders = self.generate_service_reminders()
        alerts = self.check_water_quality_alerts()
        
        schedule = {
            'generated_at': datetime.now().isoformat(),
            'service_reminders': {
                'total': len(reminders),
                'urgent': len([r for r in reminders if r.priority == 'urgent']),
                'high': len([r for r in reminders if r.priority == 'high']),
                'medium': len([r for r in reminders if r.priority == 'medium']),
                'reminders': [
                    {
                        'equipment_number': r.equipment_number,
                        'customer_name': r.customer_name,
                        'customer_email': r.customer_email,
                        'service_type': r.service_type,
                        'priority': r.priority,
                        'days_until_due': r.days_until_due,
                        'next_service_date': r.next_service_date.isoformat()
                    }
                    for r in reminders
                ]
            },
            'water_quality_alerts': {
                'total': len(alerts),
                'critical': len([a for a in alerts if a.alert_type == 'critical']),
                'warning': len([a for a in alerts if a.alert_type == 'warning']),
                'alerts': [
                    {
                        'equipment_number': a.equipment_number,
                        'customer_name': a.customer_name,
                        'parameter': a.parameter,
                        'value': a.value,
                        'threshold': a.threshold,
                        'alert_type': a.alert_type,
                        'timestamp': a.timestamp.isoformat()
                    }
                    for a in alerts
                ]
            }
        }
        
        return schedule 