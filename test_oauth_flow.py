#!/usr/bin/env python3
"""
Test script to verify Google OAuth configuration and workflow
"""
import os
import requests
from urllib.parse import urlencode

def test_oauth_setup():
    """Test the complete OAuth setup"""
    print("=== Google OAuth Configuration Test ===")
    
    # 1. Check environment variables
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    print(f"1. Client ID configured: {'Yes' if client_id else 'No'}")
    print(f"2. Client Secret configured: {'Yes' if client_secret else 'No'}")
    
    if not client_id or not client_secret:
        print("❌ Missing OAuth credentials")
        return False
    
    # 2. Test redirect URI generation
    base_url = "https://3a93bf2d-ac70-4b89-a836-7f93c476d323-00-2h1i3co16z5af.kirk.replit.dev"
    redirect_uri = f"{base_url}/auth/google/callback"
    print(f"3. Redirect URI: {redirect_uri}")
    
    # 3. Test OAuth URL generation
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/userinfo.email',
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode(params)
    print(f"4. OAuth URL generated successfully")
    print(f"   Length: {len(auth_url)} characters")
    
    # 5. Test application routes
    try:
        response = requests.get(f"{base_url}/ai-assistant/gmail", timeout=5)
        print(f"5. Gmail route status: {response.status_code}")
        if response.status_code == 302:
            print(f"   Redirects to: {response.headers.get('Location', 'Unknown')}")
    except Exception as e:
        print(f"5. Gmail route error: {str(e)}")
    
    print("\n=== OAuth URL for Manual Testing ===")
    print(auth_url)
    print("\n=== Instructions ===")
    print("1. Copy the OAuth URL above")
    print("2. Add this redirect URI to Google Cloud Console:")
    print(f"   {redirect_uri}")
    print("3. Paste the OAuth URL in your browser to test")
    
    return True

if __name__ == "__main__":
    test_oauth_setup()