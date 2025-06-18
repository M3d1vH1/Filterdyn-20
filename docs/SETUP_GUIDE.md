# Operational Suite V2 - Setup Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Create or update your `.env` file:

```env
# Database
DATABASE_URL=sqlite:///instance/test.db

# OpenAI API (for AI email generation)
OPENAI_API_KEY=your_openai_api_key_here

# Gmail API (for email sending)
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json

# Grandstream Integration (optional)
GRANDSTREAM_URL=https://your-grandstream-server.com
GRANDSTREAM_USERNAME=admin
GRANDSTREAM_PASSWORD=your_password

# External API Keys (optional)
EXTERNAL_API_KEY_1=your_api_key_1
EXTERNAL_API_KEY_2=your_api_key_2
```

### 3. Set Up Gmail API (for email features)

#### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API

#### Step 2: Create Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application"
4. Download the credentials file as `credentials.json`

#### Step 3: Authenticate
```python
from agents.communication_ai import CommunicationAIAgent

config = {
    'gmail_credentials_path': 'credentials.json',
    'gmail_token_path': 'token.json',
    'openai_api_key': 'your_openai_api_key'
}

agent = CommunicationAIAgent(config)
agent.authenticate_gmail()  # This will open browser for authentication
```

### 4. Run the Demo
```bash
python demo_features.py
```

### 5. Start the Application
```bash
python app.py
```

## 🔧 Feature Configuration

### Communication & AI Agent

#### Email Templates
The agent automatically generates email content for:
- Service reminders
- Water quality alerts
- Quote follow-ups
- General communications

#### AI Configuration
```python
# Customize AI prompts
context = {
    'type': 'service_reminder',
    'customer_name': 'Customer Name',
    'equipment_number': 'EQ-001',
    'service_type': 'preventive_maintenance',
    'days_until_due': 7
}

email_content = agent.generate_ai_email_content(context)
```

### Operations & Data Agent

#### Service Reminders
Automatically generates reminders based on:
- Equipment type (deionization columns, RO systems, filters)
- Last service date
- Equipment-specific maintenance schedules

#### Water Quality Monitoring
Monitors parameters:
- Conductivity (μS/cm)
- Resistivity (MΩ·cm)
- pH levels
- Temperature (°C)
- TDS (mg/L)
- Turbidity (NTU)

#### Performance Analysis
```python
# Analyze equipment performance
analysis = agent.analyze_equipment_performance(equipment_id=1, days=30)
print(analysis)
```

### Platform & Integration Agent

#### Analytics Dashboard
Access via API:
```bash
curl http://localhost:5000/api/v1/analytics/dashboard
```

#### API Endpoints
All endpoints are available at `/api/v1/`:
- `GET /equipment` - List all equipment
- `GET /equipment/{id}/status` - Equipment status
- `POST /water-quality` - Submit water quality data
- `GET /analytics/dashboard` - Analytics data
- `POST /website/contact` - Contact form

#### Grandstream Integration
```python
# Configure Grandstream
config = {
    'grandstream': {
        'base_url': 'https://your-server.com',
        'username': 'admin',
        'password': 'password'
    }
}

agent = PlatformIntegrationAgent(config)
devices = agent.get_grandstream_devices()
```

## 📊 Using the Analytics Dashboard

### Access Dashboard
1. Start the application: `python app.py`
2. Navigate to: `http://localhost:5000/api/v1/analytics/dashboard`

### Dashboard Features
- **Overview**: Total equipment, customers, recent activity
- **Equipment Metrics**: Performance, service compliance
- **Customer Metrics**: Engagement, top customers
- **Service Metrics**: Recent services, types, duration
- **Water Quality**: Trends, alerts, measurements

## 🔄 Automated Workflows

### Service Reminders
The system automatically:
1. Checks equipment service schedules
2. Generates reminders for due services
3. Sends AI-generated emails to customers
4. Tracks email delivery status

### Water Quality Alerts
The system automatically:
1. Monitors water quality measurements
2. Detects parameter violations
3. Generates alerts for critical issues
4. Sends notification emails

### Performance Monitoring
The system automatically:
1. Analyzes equipment performance trends
2. Generates performance reports
3. Identifies maintenance needs
4. Provides operational insights

## 🛠️ API Integration Examples

### Submit Water Quality Data
```bash
curl -X POST http://localhost:5000/api/v1/water-quality \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id": 1,
    "conductivity": 5.2,
    "ph": 7.1,
    "temperature": 25.0,
    "tds": 8.5
  }'
```

### Get Equipment Status
```bash
curl http://localhost:5000/api/v1/equipment/1/status
```

### Handle Contact Form
```bash
curl -X POST http://localhost:5000/api/v1/website/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "message": "I need information about your services"
  }'
```

## 🔍 Troubleshooting

### Common Issues

#### Gmail API Authentication
- Ensure `credentials.json` is in the project root
- Check that Gmail API is enabled in Google Cloud Console
- Verify OAuth consent screen is configured

#### Database Issues
- Ensure SQLite database exists: `instance/test.db`
- Check database permissions
- Verify table structure matches models

#### OpenAI API
- Verify API key is set in environment variables
- Check API key has sufficient credits
- Ensure internet connection for API calls

#### Agent Initialization
- Check all required dependencies are installed
- Verify configuration in `.env` file
- Review agent status in coordinator

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Optimization

### Database Optimization
- Use indexes on frequently queried columns
- Implement database connection pooling
- Regular database maintenance

### API Performance
- Implement caching for analytics data
- Use pagination for large datasets
- Optimize database queries

### Email Optimization
- Batch email sending
- Implement rate limiting
- Use email templates for consistency

## 🔐 Security Considerations

### API Security
- Implement authentication for API endpoints
- Use HTTPS in production
- Validate all input data

### Email Security
- Secure Gmail API credentials
- Implement email rate limiting
- Validate email addresses

### Data Protection
- Encrypt sensitive data
- Implement access controls
- Regular security audits

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the demo script: `python demo_features.py`
3. Check agent status via coordinator
4. Review logs for error messages

## 🎯 Next Steps

After setup:
1. Configure your specific equipment types
2. Set up customer data
3. Customize email templates
4. Configure water quality thresholds
5. Set up automated workflows
6. Integrate with external systems

---

**Happy automating! 🚀** 