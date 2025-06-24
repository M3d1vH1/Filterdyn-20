# Filterdyn Gmail & AI Integration

## Overview
This project extends Filterdyn with a full-featured Gmail interface and AI-powered email automation. It enables users to:
- Connect personal or Workspace Gmail accounts (OAuth2)
- View, search, and manage emails and threads
- Compose, send, and reply to emails with attachments
- Link emails to customers, orders, quotes, and tasks
- Use AI to analyze emails, extract key info, and suggest smart replies
- Store all email data and attachments securely in PostgreSQL
- Integrate seamlessly with the Filterdyn UI (Bootstrap 5.3)

## Features
- Multi-account, multi-tenant Gmail support
- Secure OAuth2 token storage (encrypted)
- Real-time and bi-directional Gmail sync
- Full inbox, message, and compose UI
- AI-powered content analysis, intent/sentiment/entity extraction
- Smart response and template suggestions (OpenAI)
- Business logic integration (customers, orders, quotes, tasks)
- GDPR-compliant data handling

## Setup Instructions

### 1. Python & Dependencies
- Python 3.9+
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
  Or, if using Poetry:
  ```bash
  poetry install
  ```
- Required packages include: Flask, Flask-Login, Flask-Babel, Flask-SQLAlchemy, psycopg2-binary, openai, google-api-python-client, google-auth, google-auth-oauthlib, cryptography, pytest, etc.

### 2. Google OAuth Setup
- Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- Create OAuth 2.0 credentials (Web application)
- Add authorized redirect URI: `https://<your-domain>/gmail/oauth2callback` (or `http://localhost:5000/gmail/oauth2callback` for local)
- Download the `client_secret.json` and place it in your project root
- Set environment variables:
  - `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` (from Google Cloud)
  - `GOOGLE_CLIENT_SECRET_FILE` (path to your `client_secret.json`)
  - `GMAIL_TOKEN_KEY` (random 32-byte base64 string for encryption)
  - `OPENAI_API_KEY` (your OpenAI key)

### 3. Environment Variables Example
```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_CLIENT_SECRET_FILE=client_secret.json
GMAIL_TOKEN_KEY=your-32-byte-base64-key
OPENAI_API_KEY=your-openai-key
FLASK_ENV=development
DATABASE_URL=postgresql://user:password@localhost:5432/filterdyn
```

### 4. Database Migration
- Ensure PostgreSQL is running and the `DATABASE_URL` is set
- Run:
  ```bash
  flask db upgrade
  ```
  Or, if not using Flask-Migrate, run:
  ```bash
  python
  >>> from app import db
  >>> db.create_all()
  ```

### 5. Running Locally
- Start the Flask app:
  ```bash
  flask run
  ```
- Or, for Replit:
  - Upload all files and set environment variables in the Replit Secrets panel
  - Click "Run"

### 6. Usage Guide
- Log in to Filterdyn
- Click the AI Assistant floating button
- In Quick Actions, click "Gmail Inbox" to open the Gmail interface
- Connect your Gmail account (OAuth2 flow)
- View, search, and manage emails
- Click an email to read, reply, or analyze with AI
- Use the compose button to send new emails (with attachments)
- Use AI buttons for smart suggestions and analysis

### 7. Security Notes
- OAuth tokens are encrypted at rest using `GMAIL_TOKEN_KEY`
- Email content and attachments are stored securely in PostgreSQL
- Role-based access controls are enforced
- All email operations are audit-logged
- GDPR compliance: you can configure retention and deletion policies

### 8. Testing
- Run all tests with:
  ```bash
  pytest
  ```
- Tests cover models, services, routes, and AI features

### 9. Troubleshooting & FAQ
- **OAuth errors:** Check your Google Cloud credentials and redirect URIs
- **Email not syncing:** Ensure tokens are valid and Gmail API is enabled
- **AI not working:** Check your OpenAI API key and usage limits
- **Database issues:** Verify `DATABASE_URL` and PostgreSQL status
- **Replit issues:** Ensure all secrets are set and files are uploaded

---

For further help, see the code comments or contact the Filterdyn development team. 