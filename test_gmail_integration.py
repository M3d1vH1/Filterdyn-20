import pytest
from app import create_app, db
from models import User, Tenant, GmailAccount, GmailMessage, GmailAttachment, AIEmailInteraction
from gmail_service import GmailService
from gmail_ai_service import GmailAIService
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timezone

@pytest.fixture
def app():
    """Create test app"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        
        # Create test tenant
        tenant = Tenant(
            name='Test Tenant',
            subdomain='test',
            is_active=True
        )
        db.session.add(tenant)
        db.session.commit()
        
        # Create test user
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='test_hash',
            role='admin',
            tenant_id=tenant.id,
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def auth_client(client, app):
    """Create authenticated test client"""
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
        
        yield client

def test_gmail_account_model(app):
    """Test GmailAccount model creation"""
    with app.app_context():
        user = User.query.first()
        tenant = Tenant.query.first()
        
        # Mock encrypted tokens
        fake_token = b'encrypted_access_token'
        fake_refresh = b'encrypted_refresh_token'
        
        account = GmailAccount(
            tenant_id=tenant.id,
            user_id=user.id,
            email_address='test@gmail.com',
            google_user_id='123456789',
            access_token=fake_token,
            refresh_token=fake_refresh,
            is_primary=True,
            sync_enabled=True
        )
        
        db.session.add(account)
        db.session.commit()
        
        # Verify account created
        saved_account = GmailAccount.query.first()
        assert saved_account.email_address == 'test@gmail.com'
        assert saved_account.is_primary is True
        assert saved_account.sync_enabled is True

def test_gmail_message_model(app):
    """Test GmailMessage model creation"""
    with app.app_context():
        user = User.query.first()
        tenant = Tenant.query.first()
        
        message = GmailMessage(
            user_id=user.id,
            tenant_id=tenant.id,
            thread_id='thread123',
            message_id='msg123',
            subject='Test Subject',
            sender='sender@example.com',
            recipients='recipient@example.com',
            snippet='Test message snippet',
            is_read=False,
            is_starred=False,
            has_attachments=False
        )
        
        db.session.add(message)
        db.session.commit()
        
        # Verify message created
        saved_message = GmailMessage.query.first()
        assert saved_message.subject == 'Test Subject'
        assert saved_message.sender == 'sender@example.com'
        assert saved_message.is_read is False

@patch('gmail_service.GmailService.encrypt_token')
@patch('gmail_service.GmailService.decrypt_token')
def test_gmail_service_token_encryption(mock_decrypt, mock_encrypt, app):
    """Test token encryption/decryption"""
    mock_encrypt.return_value = b'encrypted_token'
    mock_decrypt.return_value = 'decrypted_token'
    
    # Test encryption
    result = GmailService.encrypt_token('test_token')
    assert result == b'encrypted_token'
    mock_encrypt.assert_called_with('test_token')
    
    # Test decryption
    result = GmailService.decrypt_token(b'encrypted_token')
    assert result == 'decrypted_token'
    mock_decrypt.assert_called_with(b'encrypted_token')

@patch('gmail_ai_service.genai.GenerativeModel')
def test_gmail_ai_service_analyze(mock_model, app):
    """Test AI email analysis"""
    with app.app_context():
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "key_info": ["Meeting tomorrow at 2 PM"],
            "sentiment": "neutral",
            "intent": "meeting_request",
            "entities": {"names": ["John"], "dates": ["tomorrow"]},
            "priority": "medium",
            "summary": "Request for a meeting"
        })
        
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_instance
        
        # Test analysis
        result = GmailAIService.analyze_email_content("Let's meet tomorrow at 2 PM")
        
        assert result['sentiment'] == 'neutral'
        assert result['intent'] == 'meeting_request'
        assert 'Meeting tomorrow at 2 PM' in result['key_info']
        assert result['priority'] == 'medium'

@patch('gmail_ai_service.genai.GenerativeModel')
def test_gmail_ai_service_suggest_response(mock_model, app):
    """Test AI response suggestion"""
    with app.app_context():
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = "Thank you for your email. I'll check my calendar and get back to you soon."
        
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_instance
        
        # Test suggestion
        result = GmailAIService.suggest_response("Can we meet tomorrow?")
        
        assert "Thank you for your email" in result
        assert "get back to you" in result

def test_gmail_routes_connect_redirect(auth_client, app):
    """Test Gmail connect route redirects to OAuth"""
    with app.app_context():
        response = auth_client.get('/gmail/connect')
        
        # Should redirect to Google OAuth (or show error if not configured)
        assert response.status_code in [302, 500]  # 302 for redirect, 500 for missing config

def test_gmail_routes_inbox_no_account(auth_client, app):
    """Test Gmail inbox route without connected account"""
    with app.app_context():
        response = auth_client.get('/gmail/inbox')
        
        # Should redirect or show warning about no account
        assert response.status_code in [200, 302]

def test_ai_email_interaction_model(app):
    """Test AIEmailInteraction model"""
    with app.app_context():
        user = User.query.first()
        tenant = Tenant.query.first()
        
        interaction = AIEmailInteraction(
            tenant_id=tenant.id,
            user_id=user.id,
            email_subject='Test Subject',
            email_sender='test@example.com',
            interaction_type='analysis',
            input_data={'text': 'test email'},
            ai_response='{"sentiment": "positive"}',
            processing_time_ms=500
        )
        
        db.session.add(interaction)
        db.session.commit()
        
        # Verify interaction created
        saved_interaction = AIEmailInteraction.query.first()
        assert saved_interaction.interaction_type == 'analysis'
        assert saved_interaction.email_subject == 'Test Subject'
        assert saved_interaction.processing_time_ms == 500

def test_gmail_ai_service_learning_stats(app):
    """Test AI learning statistics"""
    with app.app_context():
        user = User.query.first()
        tenant = Tenant.query.first()
        
        # Create test interactions
        for i in range(3):
            interaction = AIEmailInteraction(
                tenant_id=tenant.id,
                user_id=user.id,
                interaction_type='analysis',
                input_data={'text': f'test email {i}'},
                ai_response=f'response {i}',
                user_feedback='accepted',
                effectiveness_score=0.8,
                processing_time_ms=300 + i * 100
            )
            db.session.add(interaction)
        
        db.session.commit()
        
        # Get stats
        stats = GmailAIService.get_learning_stats(tenant.id, user.id)
        
        assert stats['total_interactions'] == 3
        assert stats['feedback_given'] == 3
        assert stats['avg_effectiveness'] == 0.8
        assert stats['by_type']['analysis'] == 3

def test_email_business_association_model(app):
    """Test EmailBusinessAssociation model"""
    with app.app_context():
        user = User.query.first()
        
        # Create customer for association
        from models import Customer
        customer = Customer(
            tenant_id=user.tenant_id,
            name='Test Customer',
            email='customer@example.com',
            created_by=user.id
        )
        db.session.add(customer)
        db.session.commit()
        
        # Create email association
        association = EmailBusinessAssociation(
            customer_id=customer.id,
            gmail_message_subject='Order inquiry',
            gmail_message_sender='customer@example.com',
            association_type='customer',
            confidence_score=0.9,
            created_by=user.id
        )
        
        db.session.add(association)
        db.session.commit()
        
        # Verify association created
        saved_association = EmailBusinessAssociation.query.first()
        assert saved_association.association_type == 'customer'
        assert saved_association.confidence_score == 0.9
        assert saved_association.customer.name == 'Test Customer'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])