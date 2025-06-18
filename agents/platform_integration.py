"""
Platform & Integration Agent
===========================

Handles APIs, analytics dashboard, Grandstream integration, website contact forms,
and other platform integrations.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass
import sqlite3
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS

try:
    import pandas as pd
    import numpy as np
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False


@dataclass
class AnalyticsMetric:
    """Analytics metric data structure"""
    name: str
    value: Union[int, float, str]
    unit: str
    trend: str  # increasing, decreasing, stable
    change_percent: float
    period: str


@dataclass
class GrandstreamDevice:
    """Grandstream device data structure"""
    device_id: str
    name: str
    ip_address: str
    status: str  # online, offline, error
    last_seen: datetime
    device_type: str
    firmware_version: str


class PlatformIntegrationAgent:
    """Agent for handling platform integrations, APIs, and analytics"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.db_path = self.config.get('db_path', os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/filterdyn'))
        self.grandstream_config = self.config.get('grandstream', {})
        self.api_keys = self.config.get('api_keys', {})
        
    def create_analytics_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive analytics dashboard data"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get basic statistics
            stats = self._get_basic_statistics(conn)
            
            # Get equipment performance metrics
            equipment_metrics = self._get_equipment_metrics(conn)
            
            # Get customer engagement metrics
            customer_metrics = self._get_customer_metrics(conn)
            
            # Get service metrics
            service_metrics = self._get_service_metrics(conn)
            
            # Get water quality trends
            quality_trends = self._get_water_quality_trends(conn)
            
            conn.close()
            
            dashboard = {
                'generated_at': datetime.now().isoformat(),
                'overview': stats,
                'equipment': equipment_metrics,
                'customers': customer_metrics,
                'services': service_metrics,
                'water_quality': quality_trends,
                'alerts': self._get_current_alerts()
            }
            
            return dashboard
            
        except Exception as e:
            print(f"❌ Error creating analytics dashboard: {e}")
            return {'error': str(e)}
    
    def _get_basic_statistics(self, conn) -> Dict[str, Any]:
        """Get basic business statistics"""
        cursor = conn.cursor()
        
        # Count equipment by status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM equipment
            GROUP BY status
        """)
        equipment_by_status = dict(cursor.fetchall())
        
        # Count customers
        cursor.execute("SELECT COUNT(*) FROM customers WHERE is_active = 1")
        total_customers = cursor.fetchone()[0]
        
        # Count recent quotes and orders
        cursor.execute("""
            SELECT COUNT(*) FROM quotes 
            WHERE created_at >= datetime('now', '-30 days')
        """)
        recent_quotes = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM orders 
            WHERE created_at >= datetime('now', '-30 days')
        """)
        recent_orders = cursor.fetchone()[0]
        
        return {
            'total_equipment': sum(equipment_by_status.values()),
            'active_equipment': equipment_by_status.get('active', 0),
            'maintenance_equipment': equipment_by_status.get('maintenance', 0),
            'total_customers': total_customers,
            'recent_quotes_30d': recent_quotes,
            'recent_orders_30d': recent_orders
        }
    
    def _get_equipment_metrics(self, conn) -> Dict[str, Any]:
        """Get equipment performance metrics"""
        cursor = conn.cursor()
        
        # Equipment by type
        cursor.execute("""
            SELECT equipment_type, COUNT(*) as count
            FROM equipment
            WHERE status = 'active'
            GROUP BY equipment_type
        """)
        equipment_by_type = dict(cursor.fetchall())
        
        # Equipment requiring service
        cursor.execute("""
            SELECT COUNT(*) FROM equipment
            WHERE last_service_date IS NULL 
            OR last_service_date <= datetime('now', '-90 days')
        """)
        equipment_needing_service = cursor.fetchone()[0]
        
        # Average equipment age
        cursor.execute("""
            SELECT AVG(JULIANDAY('now') - JULIANDAY(installation_date)) as avg_age_days
            FROM equipment
            WHERE installation_date IS NOT NULL
        """)
        avg_age_result = cursor.fetchone()
        avg_age_days = avg_age_result[0] if avg_age_result[0] else 0
        
        return {
            'by_type': equipment_by_type,
            'needing_service': equipment_needing_service,
            'average_age_days': round(avg_age_days, 1),
            'service_compliance_rate': self._calculate_service_compliance_rate(conn)
        }
    
    def _get_customer_metrics(self, conn) -> Dict[str, Any]:
        """Get customer engagement metrics"""
        cursor = conn.cursor()
        
        # New customers this month
        cursor.execute("""
            SELECT COUNT(*) FROM customers
            WHERE created_at >= datetime('now', 'start of month')
        """)
        new_customers_month = cursor.fetchone()[0]
        
        # Customers with active equipment
        cursor.execute("""
            SELECT COUNT(DISTINCT customer_id) FROM equipment
            WHERE status = 'active'
        """)
        customers_with_equipment = cursor.fetchone()[0]
        
        # Top customers by equipment count
        cursor.execute("""
            SELECT c.name, COUNT(e.id) as equipment_count
            FROM customers c
            JOIN equipment e ON c.id = e.customer_id
            WHERE e.status = 'active'
            GROUP BY c.id, c.name
            ORDER BY equipment_count DESC
            LIMIT 5
        """)
        top_customers = cursor.fetchall()
        
        return {
            'new_customers_month': new_customers_month,
            'customers_with_equipment': customers_with_equipment,
            'top_customers': [{'name': name, 'equipment_count': count} for name, count in top_customers]
        }
    
    def _get_service_metrics(self, conn) -> Dict[str, Any]:
        """Get service and maintenance metrics"""
        cursor = conn.cursor()
        
        # Recent service reports
        cursor.execute("""
            SELECT COUNT(*) FROM service_reports
            WHERE service_date >= datetime('now', '-30 days')
        """)
        recent_services = cursor.fetchone()[0]
        
        # Service types breakdown
        cursor.execute("""
            SELECT service_type, COUNT(*) as count
            FROM service_reports
            WHERE service_date >= datetime('now', '-90 days')
            GROUP BY service_type
        """)
        service_types = dict(cursor.fetchall())
        
        # Average service duration
        cursor.execute("""
            SELECT AVG(estimated_duration) as avg_duration
            FROM equipment_maintenance
            WHERE status = 'completed' AND actual_duration IS NOT NULL
        """)
        avg_duration_result = cursor.fetchone()
        avg_duration = avg_duration_result[0] if avg_duration_result[0] else 0
        
        return {
            'recent_services_30d': recent_services,
            'service_types_90d': service_types,
            'average_service_duration_hours': round(avg_duration, 1)
        }
    
    def _get_water_quality_trends(self, conn) -> Dict[str, Any]:
        """Get water quality trends and statistics"""
        cursor = conn.cursor()
        
        # Recent measurements count
        cursor.execute("""
            SELECT COUNT(*) FROM water_quality_data
            WHERE measurement_date >= datetime('now', '-7 days')
        """)
        recent_measurements = cursor.fetchone()[0]
        
        # Average conductivity trend
        cursor.execute("""
            SELECT AVG(conductivity) as avg_conductivity
            FROM water_quality_data
            WHERE measurement_date >= datetime('now', '-7 days')
            AND conductivity IS NOT NULL
        """)
        avg_conductivity_result = cursor.fetchone()
        avg_conductivity = avg_conductivity_result[0] if avg_conductivity_result[0] else 0
        
        # Quality status breakdown
        cursor.execute("""
            SELECT quality_status, COUNT(*) as count
            FROM water_quality_data
            WHERE measurement_date >= datetime('now', '-30 days')
            AND quality_status IS NOT NULL
            GROUP BY quality_status
        """)
        quality_status = dict(cursor.fetchall())
        
        return {
            'recent_measurements_7d': recent_measurements,
            'average_conductivity_7d': round(avg_conductivity, 2),
            'quality_status_30d': quality_status
        }
    
    def _calculate_service_compliance_rate(self, conn) -> float:
        """Calculate service compliance rate"""
        cursor = conn.cursor()
        
        # Count equipment that should have been serviced
        cursor.execute("""
            SELECT COUNT(*) FROM equipment
            WHERE last_service_date IS NULL 
            OR last_service_date <= datetime('now', '-90 days')
        """)
        overdue_equipment = cursor.fetchone()[0]
        
        # Total active equipment
        cursor.execute("SELECT COUNT(*) FROM equipment WHERE status = 'active'")
        total_equipment = cursor.fetchone()[0]
        
        if total_equipment == 0:
            return 100.0
        
        compliance_rate = ((total_equipment - overdue_equipment) / total_equipment) * 100
        return round(compliance_rate, 1)
    
    def _get_current_alerts(self) -> Dict[str, Any]:
        """Get current system alerts"""
        # This would integrate with the OperationsDataAgent
        return {
            'service_reminders': 0,  # Placeholder
            'water_quality_alerts': 0,  # Placeholder
            'equipment_issues': 0  # Placeholder
        }
    
    def setup_grandstream_integration(self) -> bool:
        """Setup Grandstream device integration"""
        try:
            # Grandstream API configuration
            base_url = self.grandstream_config.get('base_url')
            username = self.grandstream_config.get('username')
            password = self.grandstream_config.get('password')
            
            if not all([base_url, username, password]):
                print("⚠️ Grandstream configuration incomplete")
                return False
            
            # Test connection
            test_url = f"{base_url}/api/v1/devices"
            response = requests.get(test_url, auth=(username, password), timeout=10)
            
            if response.status_code == 200:
                print("✅ Grandstream integration successful")
                return True
            else:
                print(f"❌ Grandstream connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Grandstream integration error: {e}")
            return False
    
    def get_grandstream_devices(self) -> List[GrandstreamDevice]:
        """Get list of Grandstream devices"""
        devices = []
        
        try:
            base_url = self.grandstream_config.get('base_url')
            username = self.grandstream_config.get('username')
            password = self.grandstream_config.get('password')
            
            if not all([base_url, username, password]):
                return devices
            
            # Get devices from Grandstream API
            response = requests.get(
                f"{base_url}/api/v1/devices",
                auth=(username, password),
                timeout=10
            )
            
            if response.status_code == 200:
                device_data = response.json()
                
                for device in device_data.get('devices', []):
                    devices.append(GrandstreamDevice(
                        device_id=device.get('id'),
                        name=device.get('name', 'Unknown'),
                        ip_address=device.get('ip_address'),
                        status=device.get('status', 'unknown'),
                        last_seen=datetime.fromisoformat(device.get('last_seen', datetime.now().isoformat())),
                        device_type=device.get('type', 'unknown'),
                        firmware_version=device.get('firmware_version', 'unknown')
                    ))
            
        except Exception as e:
            print(f"❌ Error fetching Grandstream devices: {e}")
        
        return devices
    
    def create_api_endpoints(self, app: Flask) -> None:
        """Create REST API endpoints for external integrations"""
        
        # Enable CORS for API endpoints
        CORS(app, resources={r"/api/*": {"origins": "*"}})
        
        @app.route('/api/v1/equipment', methods=['GET'])
        def api_get_equipment():
            """Get equipment list"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT e.id, e.equipment_number, e.equipment_type, e.status,
                           c.name as customer_name
                    FROM equipment e
                    JOIN customers c ON e.customer_id = c.id
                    WHERE e.status = 'active'
                """)
                
                equipment = []
                for row in cursor.fetchall():
                    equipment.append({
                        'id': row[0],
                        'equipment_number': row[1],
                        'equipment_type': row[2],
                        'status': row[3],
                        'customer_name': row[4]
                    })
                
                conn.close()
                return jsonify({'equipment': equipment})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/v1/equipment/<int:equipment_id>/status', methods=['GET'])
        def api_get_equipment_status(equipment_id):
            """Get equipment status and recent measurements"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get equipment details
                cursor.execute("""
                    SELECT e.*, c.name as customer_name
                    FROM equipment e
                    JOIN customers c ON e.customer_id = c.id
                    WHERE e.id = ?
                """, (equipment_id,))
                
                equipment_data = cursor.fetchone()
                if not equipment_data:
                    return jsonify({'error': 'Equipment not found'}), 404
                
                # Get recent water quality data
                cursor.execute("""
                    SELECT measurement_date, conductivity, resistivity, ph, temperature, tds
                    FROM water_quality_data
                    WHERE equipment_id = ?
                    ORDER BY measurement_date DESC
                    LIMIT 5
                """, (equipment_id,))
                
                recent_measurements = []
                for row in cursor.fetchall():
                    recent_measurements.append({
                        'measurement_date': row[0],
                        'conductivity': row[1],
                        'resistivity': row[2],
                        'ph': row[3],
                        'temperature': row[4],
                        'tds': row[5]
                    })
                
                conn.close()
                
                return jsonify({
                    'equipment_id': equipment_id,
                    'equipment_number': equipment_data[2],
                    'status': equipment_data[8],
                    'customer_name': equipment_data[-1],
                    'recent_measurements': recent_measurements
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/v1/water-quality', methods=['POST'])
        def api_post_water_quality():
            """Post water quality measurement data"""
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                # Validate required fields
                required_fields = ['equipment_id', 'conductivity', 'ph']
                for field in required_fields:
                    if field not in data:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Insert water quality data
                cursor.execute("""
                    INSERT INTO water_quality_data 
                    (tenant_id, equipment_id, recorded_by, measurement_date, 
                     conductivity, resistivity, ph, temperature, tds, turbidity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    1,  # Default tenant_id
                    data['equipment_id'],
                    1,  # Default user_id
                    datetime.now().isoformat(),
                    data.get('conductivity'),
                    data.get('resistivity'),
                    data.get('ph'),
                    data.get('temperature'),
                    data.get('tds'),
                    data.get('turbidity')
                ))
                
                conn.commit()
                conn.close()
                
                return jsonify({'message': 'Water quality data recorded successfully'})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/v1/analytics/dashboard', methods=['GET'])
        def api_get_dashboard():
            """Get analytics dashboard data"""
            try:
                dashboard_data = self.create_analytics_dashboard()
                return jsonify(dashboard_data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/v1/website/contact', methods=['POST'])
        def api_website_contact():
            """Handle website contact form submissions"""
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                # Validate required fields
                required_fields = ['name', 'email', 'message']
                for field in required_fields:
                    if field not in data:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                
                # Process contact form (save to database, send notification, etc.)
                contact_data = {
                    'name': data['name'],
                    'email': data['email'],
                    'phone': data.get('phone', ''),
                    'company': data.get('company', ''),
                    'message': data['message'],
                    'submitted_at': datetime.now().isoformat(),
                    'source': 'website_contact_form'
                }
                
                # Save to database (implement as needed)
                # self._save_contact_submission(contact_data)
                
                # Send notification email (implement as needed)
                # self._send_contact_notification(contact_data)
                
                return jsonify({'message': 'Contact form submitted successfully'})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def create_website_contact_form(self) -> str:
        """Generate HTML for website contact form"""
        return """
        <div class="contact-form">
            <h3>Contact Filterdyn Operations</h3>
            <form id="contactForm" onsubmit="submitContactForm(event)">
                <div class="form-group">
                    <label for="name">Name *</label>
                    <input type="text" id="name" name="name" required>
                </div>
                
                <div class="form-group">
                    <label for="email">Email *</label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label for="phone">Phone</label>
                    <input type="tel" id="phone" name="phone">
                </div>
                
                <div class="form-group">
                    <label for="company">Company</label>
                    <input type="text" id="company" name="company">
                </div>
                
                <div class="form-group">
                    <label for="message">Message *</label>
                    <textarea id="message" name="message" rows="5" required></textarea>
                </div>
                
                <button type="submit" class="btn btn-primary">Send Message</button>
            </form>
        </div>
        
        <script>
        async function submitContactForm(event) {
            event.preventDefault();
            
            const formData = new FormData(event.target);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/api/v1/website/contact', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    alert('Thank you for your message. We will get back to you soon!');
                    event.target.reset();
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Error submitting form: ' + error.message);
            }
        }
        </script>
        """
    
    def generate_performance_report(self, report_type: str = 'comprehensive') -> Dict[str, Any]:
        """Generate performance reports for different stakeholders"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            if report_type == 'executive':
                report = self._generate_executive_report(conn)
            elif report_type == 'technical':
                report = self._generate_technical_report(conn)
            elif report_type == 'customer':
                report = self._generate_customer_report(conn)
            else:
                report = self._generate_comprehensive_report(conn)
            
            conn.close()
            return report
            
        except Exception as e:
            print(f"❌ Error generating performance report: {e}")
            return {'error': str(e)}
    
    def _generate_executive_report(self, conn) -> Dict[str, Any]:
        """Generate executive summary report"""
        cursor = conn.cursor()
        
        # Key performance indicators
        cursor.execute("SELECT COUNT(*) FROM equipment WHERE status = 'active'")
        active_equipment = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM customers WHERE is_active = 1")
        total_customers = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM quotes 
            WHERE created_at >= datetime('now', '-30 days')
        """)
        monthly_quotes = cursor.fetchone()[0]
        
        return {
            'report_type': 'executive',
            'generated_at': datetime.now().isoformat(),
            'kpis': {
                'active_equipment': active_equipment,
                'total_customers': total_customers,
                'monthly_quotes': monthly_quotes,
                'service_compliance_rate': self._calculate_service_compliance_rate(conn)
            },
            'summary': 'Executive summary of operations performance'
        }
    
    def _generate_technical_report(self, conn) -> Dict[str, Any]:
        """Generate technical detailed report"""
        cursor = conn.cursor()
        
        # Equipment performance analysis
        cursor.execute("""
            SELECT equipment_type, COUNT(*) as count, AVG(JULIANDAY('now') - JULIANDAY(installation_date)) as avg_age
            FROM equipment
            WHERE status = 'active'
            GROUP BY equipment_type
        """)
        equipment_analysis = cursor.fetchall()
        
        # Water quality statistics
        cursor.execute("""
            SELECT AVG(conductivity) as avg_conductivity, AVG(resistivity) as avg_resistivity
            FROM water_quality_data
            WHERE measurement_date >= datetime('now', '-30 days')
        """)
        quality_stats = cursor.fetchone()
        
        return {
            'report_type': 'technical',
            'generated_at': datetime.now().isoformat(),
            'equipment_analysis': [
                {
                    'type': row[0],
                    'count': row[1],
                    'average_age_days': round(row[2], 1) if row[2] else 0
                }
                for row in equipment_analysis
            ],
            'water_quality_stats': {
                'average_conductivity': round(quality_stats[0], 2) if quality_stats[0] else 0,
                'average_resistivity': round(quality_stats[1], 2) if quality_stats[1] else 0
            }
        }
    
    def _generate_customer_report(self, conn) -> Dict[str, Any]:
        """Generate customer-focused report"""
        cursor = conn.cursor()
        
        # Customer satisfaction metrics
        cursor.execute("""
            SELECT c.name, COUNT(e.id) as equipment_count,
                   COUNT(sr.id) as service_count
            FROM customers c
            LEFT JOIN equipment e ON c.id = e.customer_id AND e.status = 'active'
            LEFT JOIN service_reports sr ON e.id = sr.equipment_id 
                AND sr.service_date >= datetime('now', '-90 days')
            WHERE c.is_active = 1
            GROUP BY c.id, c.name
            ORDER BY equipment_count DESC
        """)
        customer_metrics = cursor.fetchall()
        
        return {
            'report_type': 'customer',
            'generated_at': datetime.now().isoformat(),
            'customer_metrics': [
                {
                    'name': row[0],
                    'equipment_count': row[1],
                    'recent_services': row[2]
                }
                for row in customer_metrics
            ]
        }
    
    def _generate_comprehensive_report(self, conn) -> Dict[str, Any]:
        """Generate comprehensive report combining all aspects"""
        return {
            'report_type': 'comprehensive',
            'generated_at': datetime.now().isoformat(),
            'executive': self._generate_executive_report(conn),
            'technical': self._generate_technical_report(conn),
            'customer': self._generate_customer_report(conn)
        }


# Configuration example
DEFAULT_CONFIG = {
    'db_path': 'instance/test.db',
    'grandstream': {
        'base_url': 'https://your-grandstream-server.com',
        'username': 'admin',
        'password': 'password'
    },
    'api_keys': {
        'external_service_1': 'your_api_key_here',
        'external_service_2': 'your_api_key_here'
    }
} 