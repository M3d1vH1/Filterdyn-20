#!/usr/bin/env python3
"""
Operational Suite V2 - Installation Script
==========================================

Automated installation script for the multi-agent system features.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version {sys.version.split()[0]} is compatible")
    return True


def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Check if pip is available
    if not shutil.which('pip'):
        print("❌ pip is not available. Please install pip first.")
        return False
    
    # Install dependencies
    requirements_file = Path(__file__).parent / 'requirements.txt'
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    success = run_command(f"pip install -r {requirements_file}", "Installing Python dependencies")
    return success


def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        'instance',
        'email_templates',
        'scheduled_emails',
        'exports',
        'reports',
        'logs'
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"ℹ️ Directory already exists: {directory}")
    
    return True


def create_env_template():
    """Create .env template file"""
    print("⚙️ Creating environment template...")
    
    env_template = """# Operational Suite V2 - Environment Configuration
# =====================================================

# Database Configuration
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

# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
FLASK_ENV=development

# Agent Configuration
AGENT_LOG_LEVEL=INFO
AGENT_AUTO_START=True
"""
    
    env_file = Path('.env.template')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_template)
        print("✅ Created .env.template file")
        print("📝 Please copy .env.template to .env and configure your settings")
    else:
        print("ℹ️ .env.template already exists")
    
    return True


def check_dependencies():
    """Check if all dependencies are installed correctly"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask',
        'google-auth',
        'openai',
        'pandas',
        'numpy',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed correctly")
    return True


def run_tests():
    """Run basic tests to verify installation"""
    print("🧪 Running basic tests...")
    
    try:
        # Test importing agents
        from agents.communication_ai import CommunicationAIAgent
        from agents.operations_data import OperationsDataAgent
        from agents.platform_integration import PlatformIntegrationAgent
        from agents.coordinator import get_coordinator
        
        print("✅ Agent imports successful")
        
        # Test configuration
        from config.config_template import get_config
        config = get_config('development')
        print("✅ Configuration loading successful")
        
        # Test basic agent initialization
        ops_agent = OperationsDataAgent()
        print("✅ Operations agent initialization successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def show_next_steps():
    """Show next steps after installation"""
    print("\n" + "="*60)
    print("🎉 INSTALLATION COMPLETED SUCCESSFULLY!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Configure your environment:")
    print("   cp .env.template .env")
    print("   # Edit .env with your API keys and settings")
    
    print("\n2. Set up Gmail API (for email features):")
    print("   - Go to Google Cloud Console")
    print("   - Enable Gmail API")
    print("   - Create OAuth 2.0 credentials")
    print("   - Download as credentials.json")
    
    print("\n3. Set up OpenAI API (for AI features):")
    print("   - Get API key from https://platform.openai.com")
    print("   - Add to .env file")
    
    print("\n4. Run the demo:")
    print("   python launch.py --mode demo")
    
    print("\n5. Launch all agents:")
    print("   python launch.py --mode all")
    
    print("\n6. Start API server:")
    print("   python launch.py --mode api --port 5000")
    
    print("\n📚 Documentation:")
    print("   - README.md - Complete guide")
    print("   - docs/SETUP_GUIDE.md - Detailed setup")
    print("   - docs/project_board.md - Feature status")
    
    print("\n🚀 Happy automating!")


def main():
    """Main installation function"""
    print("🚀 Operational Suite V2 - Installation Script")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("❌ Failed to create directories")
        sys.exit(1)
    
    # Create environment template
    if not create_env_template():
        print("❌ Failed to create environment template")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed")
        sys.exit(1)
    
    # Run tests
    if not run_tests():
        print("❌ Tests failed")
        sys.exit(1)
    
    # Show next steps
    show_next_steps()


if __name__ == "__main__":
    main() 