# Operational Suite V2 - Multi-Agent System Features

## 🚀 Overview

This package contains the complete multi-agent system for the Filterdyn Operations Suite V2. It includes all the advanced features for automation, AI-powered communication, analytics, and integrations.

## 📦 Package Contents

```
operational_suite_features/
├── agents/                    # Multi-agent system
│   ├── __init__.py           # Agent package initialization
│   ├── communication_ai.py   # Gmail API & AI email features
│   ├── operations_data.py    # Service reminders & data analysis
│   ├── platform_integration.py # APIs & analytics dashboard
│   ├── coordinator.py        # Agent coordination & management
│   └── testing_quality/      # Testing & quality assurance
├── config/                   # Configuration templates
│   └── config_template.py    # Complete configuration system
├── docs/                     # Documentation
│   ├── SETUP_GUIDE.md       # Detailed setup instructions
│   └── project_board.md     # Feature status & roadmap
├── examples/                 # Example scripts
│   └── demo_features.py     # Feature demonstration
├── launch.py                 # Main launcher script
├── requirements.txt          # Dependencies
└── README.md                # This file
```

## 🎯 Features Implemented

### 🤖 Communication & AI Agent
- **Gmail API Integration** - Send emails programmatically
- **AI-Powered Email Generation** - Automatic content creation using Gemini (Google Generative AI)
- **Email Templates** - Context-aware templates for different scenarios
- **Email Scheduling** - Automated email scheduling system
- **Service Reminder Emails** - Automatic maintenance reminders
- **Water Quality Alert Emails** - Urgent notifications

### ⚙️ Operations & Data Agent
- **Asset Tracking** - Complete equipment management
- **Water Quality Monitoring** - Real-time parameter tracking
- **Service Report Templates** - Automated report generation
- **Automated Reminders** - Smart reminder system
- **Performance Analysis** - Equipment performance tracking
- **Data Export** - CSV/JSON export capabilities

### 🌐 Platform & Integration Agent
- **Analytics Dashboard** - Comprehensive business intelligence
- **Grandstream Integration** - Device management
- **Website Contact Form** - API for contact submissions
- **API Framework** - Complete REST API
- **Performance Monitoring** - System health tracking
- **Data Visualization** - Charts and analytics

### 🧪 Testing & Quality Agent
- **Test Automation** - Automated test discovery and running
- **Quality Assurance** - Comprehensive testing framework
- **Test Reporting** - Detailed results and analysis

### 🎮 Agent Coordinator
- **Unified Management** - Central coordination of all agents
- **Automated Workflows** - Cross-agent automation
- **System Health Monitoring** - Real-time system status
- **Agent Status Tracking** - Individual agent monitoring

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd operational_suite_features
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Create a `.env` file in the package directory:
```env
# Gemini API (for AI email generation)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
GEMINI_MAX_TOKENS=1000
GEMINI_TEMPERATURE=0.7
GEMINI_TOP_P=0.8
GEMINI_TOP_K=40

# Gmail API (for email sending)
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json

# Grandstream Integration (optional)
GRANDSTREAM_URL=https://your-grandstream-server.com
GRANDSTREAM_USERNAME=admin
GRANDSTREAM_PASSWORD=your_password

# Database
DATABASE_URL=sqlite:///instance/test.db
```

### 3. Run the Demo
```bash
python launch.py --mode demo
```

### 4. Launch All Agents
```bash
python launch.py --mode all
```

### 5. Start API Server
```bash
python launch.py --mode api --port 5000
```

## 🛠️ Usage Examples

### Launch Specific Agents
```bash
# Launch only Communication & AI Agent
python launch.py --mode communication

# Launch only Operations & Data Agent
python launch.py --mode operations

# Launch only Platform & Integration Agent
python launch.py --mode platform

# Launch only Agent Coordinator
python launch.py --mode coordinator
```

### API Endpoints
Once the API server is running, you can access:

- `GET /health` - Health check
- `GET /api/v1/equipment` - Equipment list
- `GET /api/v1/equipment/{id}/status` - Equipment status
- `POST /api/v1/water-quality` - Submit water quality data
- `GET /api/v1/analytics/dashboard` - Analytics dashboard
- `POST /api/v1/website/contact` - Contact form handling

### Example API Usage
```bash
# Get equipment list
curl http://localhost:5000/api/v1/equipment

# Submit water quality data
curl -X POST http://localhost:5000/api/v1/water-quality \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id": 1,
    "conductivity": 5.2,
    "ph": 7.1,
    "temperature": 25.0
  }'

# Get analytics dashboard
curl http://localhost:5000/api/v1/analytics/dashboard
```

## 🔧 Configuration

### Using Configuration Template
```python
from config.config_template import get_config

# Get development configuration
config = get_config('development')

# Access specific agent configurations
comm_config = config['communication_ai']
ops_config = config['operations_data']
platform_config = config['platform_integration']
```

### Environment-Specific Configurations
- **Development**: Debug mode, detailed logging
- **Production**: Optimized for performance
- **Testing**: Test-specific settings

## 📊 Analytics Dashboard

The analytics dashboard provides:
- **Overview**: Total equipment, customers, recent activity
- **Equipment Metrics**: Performance, service compliance
- **Customer Metrics**: Engagement, top customers
- **Service Metrics**: Recent services, types, duration
- **Water Quality**: Trends, alerts, measurements

## 🔄 Automated Workflows

The system automatically:
1. **Service Reminders**: Checks equipment schedules and sends reminders
2. **Water Quality Alerts**: Monitors parameters and sends alerts
3. **Performance Analysis**: Analyzes trends and generates reports
4. **System Health**: Monitors agent status and system performance

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=agents
```

### Quality Checks
```bash
# Code formatting
black agents/

# Linting
flake8 agents/

# Type checking
mypy agents/
```

## 📈 Performance Optimization

### Database Optimization
- Use indexes on frequently queried columns
- Implement connection pooling
- Regular maintenance

### API Performance
- Implement caching for analytics data
- Use pagination for large datasets
- Optimize database queries

### Email Optimization
- Batch email sending
- Implement rate limiting
- Use email templates

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

## 🐛 Troubleshooting

### Common Issues

#### Gmail API Authentication
- Ensure `credentials.json` is in the package directory
- Check that Gmail API is enabled in Google Cloud Console
- Verify OAuth consent screen is configured

#### Gemini API
- Verify API key is set in environment variables
- Check API key has sufficient credits
- Ensure internet connection for API calls

#### Database Issues
- Ensure SQLite database exists
- Check database permissions
- Verify table structure matches models

#### Agent Initialization
- Check all required dependencies are installed
- Verify configuration in `.env` file
- Review agent status in coordinator

### Debug Mode
```bash
# Enable debug logging
python launch.py --mode all --log-level DEBUG

# Save logs to file
python launch.py --mode all --log-level DEBUG --log-file debug.log
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the demo script: `python launch.py --mode demo`
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

## 📄 License

This package is part of the Filterdyn Operations Suite V2.

## 🤝 Contributing

To contribute to this package:
1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Follow security best practices

---

**Happy automating! 🚀** 