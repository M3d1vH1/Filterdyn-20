
#!/usr/bin/env python3
import os
from app import app

# Set development environment variables if not already set
if not os.environ.get('SESSION_SECRET'):
    os.environ['SESSION_SECRET'] = 'dev-secret-key-12345'

if not os.environ.get('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'sqlite:///filterdyn.db'

if __name__ == '__main__':
    print("Starting Filterdyn application in development mode...")
    print(f"Database: {os.environ.get('DATABASE_URL')}")
    app.run(host='0.0.0.0', port=5000, debug=True)
