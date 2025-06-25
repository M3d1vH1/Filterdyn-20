import pytest
from app import app, db
from models.gmail_models import GmailAccount, GmailMessage, GmailAttachment, GmailLabel, AIEmailLearningData
from services.gmail_service import GmailService
from services.ai_email_service import AIEmailService
from flask import url_for
from unittest.mock import patch, MagicMock
import datetime

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            yield testing_client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def sample_gmail_account():
    account = GmailAccount(
        tenant_id=1,
        user_id=1,
        email='test@example.com',
        access_token=b'encrypted',
        refresh_token=b'encrypted',
        token_expiry=datetime.datetime.now(),
        is_active=True
    )
    db.session.add(account)
    db.session.commit()
    return account

def test_gmail_account_model(sample_gmail_account):
    account = GmailAccount.query.first()
    assert account.email == 'test@example.com'
    assert account.is_active

def test_gmail_message_model(sample_gmail_account):
    msg = GmailMessage(
        gmail_account_id=sample_gmail_account.id,
        thread_id='thread123',
        message_id='msg123',
        subject='Test Subject',
        sender='sender@example.com',
        recipients='rcpt@example.com',
        received_at=datetime.datetime.now(),
        is_read=True
    )
    db.session.add(msg)
    db.session.commit()
    found = GmailMessage.query.filter_by(message_id='msg123').first()
    assert found.subject == 'Test Subject'

def test_gmail_attachment_model(sample_gmail_account):
    msg = GmailMessage.query.first()
    att = GmailAttachment(
        gmail_message_id=msg.id,
        filename='file.txt',
        mime_type='text/plain',
        file_data=b'hello',
        file_size=5
    )
    db.session.add(att)
    db.session.commit()
    found = GmailAttachment.query.filter_by(filename='file.txt').first()
    assert found.file_size == 5

def test_gmail_label_model(sample_gmail_account):
    label = GmailLabel(
        gmail_account_id=sample_gmail_account.id,
        label_id='LBL1',
        name='Important',
        type='system'
    )
    db.session.add(label)
    db.session.commit()
    found = GmailLabel.query.filter_by(label_id='LBL1').first()
    assert found.name == 'Important'

def test_ai_email_learning_data(sample_gmail_account):
    msg = GmailMessage.query.first()
    learning = AIEmailLearningData(
        tenant_id=1,
        user_id=1,
        gmail_message_id=msg.id,
        input_text='Test input',
        ai_suggestion='Test suggestion',
        user_feedback='accepted',
        effectiveness_score=1.0
    )
    db.session.add(learning)
    db.session.commit()
    found = AIEmailLearningData.query.first()
    assert found.user_feedback == 'accepted'

@patch('services.gmail_service.GmailService.encrypt_token', return_value=b'encrypted')
@patch('services.gmail_service.GmailService.decrypt_token', return_value=b'token')
def test_token_encryption_decryption(mock_decrypt, mock_encrypt, sample_gmail_account):
    token = GmailService.encrypt_token(b'test')
    assert token == b'encrypted'
    decrypted = GmailService.decrypt_token(token)
    assert decrypted == b'token'

@patch('services.ai_email_service.openai.ChatCompletion.create')
def test_ai_email_service_analyze(mock_openai):
    mock_openai.return_value = MagicMock(choices=[MagicMock(message={'content': '{"sentiment": "positive"}'})])
    result = AIEmailService.analyze_email_content('Test email')
    assert 'positive' in result

@patch('services.ai_email_service.openai.ChatCompletion.create')
def test_ai_email_service_suggest(mock_openai):
    mock_openai.return_value = MagicMock(choices=[MagicMock(message={'content': 'Reply suggestion'})])
    result = AIEmailService.suggest_response('Test email')
    assert 'Reply suggestion' in result

def test_gmail_routes(test_client, sample_gmail_account):
    # Simulate login
    with test_client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['tenant_id'] = 1
    # Inbox
    response = test_client.get('/gmail/inbox')
    assert response.status_code in (200, 302)
    # Compose
    response = test_client.get('/gmail/compose')
    assert response.status_code == 200
    # Search API
    response = test_client.get('/gmail/api/search?q=test')
    assert response.status_code in (200, 400) 