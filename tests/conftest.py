"""Pytest configuration and fixtures.

This module provides shared fixtures for all tests.
"""

import pytest
import os
from flask import Flask
from dotenv import load_dotenv

# Set test database URI before importing app (must be before any imports that use Config)
test_db_uri = os.environ.get('TEST_DATABASE_URL', 'sqlite:///:memory:')
os.environ['DATABASE_URL'] = test_db_uri

from database import db
from models import ApprovalRequest
from routes import api_bp, slack_bp
from routes.web_routes import web_bp
from utils.logging_config import setup_logging

load_dotenv()


@pytest.fixture
def app():
    """Create Flask application for testing.

    :return: Flask application instance
    :rtype: Flask
    """
    # Create a fresh Flask app for testing
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    test_app.config['SECRET_KEY'] = 'test-secret-key'
    # Use SQLite for testing (no PostgreSQL required)
    test_app.config['SQLALCHEMY_DATABASE_URI'] = test_db_uri
    test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    test_app.config['WTF_CSRF_ENABLED'] = False
    test_app.config['SLACK_BOT_TOKEN'] = 'xoxb-test-token'
    test_app.config['SLACK_SIGNING_SECRET'] = 'test-signing-secret'
    
    # For SQLite in-memory, use StaticPool to keep connections alive
    if test_db_uri.startswith('sqlite'):
        from sqlalchemy.pool import StaticPool
        test_app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'poolclass': StaticPool,
            'connect_args': {'check_same_thread': False}
        }
    else:
        test_app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
    
    # Initialize database with test app
    db.init_app(test_app)
    
    # Register blueprints
    test_app.register_blueprint(api_bp, url_prefix='/api')
    test_app.register_blueprint(slack_bp, url_prefix='/slack')
    test_app.register_blueprint(web_bp)
    
    # Setup logging
    setup_logging('INFO')
    
    # Add health check route
    @test_app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'universal-approval-hub'}, 200

    with test_app.app_context():
        # Drop all tables and recreate for clean test state
        try:
            db.drop_all()
        except Exception:
            pass  # Ignore if tables don't exist
        db.create_all()
        yield test_app
        try:
            db.drop_all()
        except Exception:
            pass


@pytest.fixture
def client(app):
    """Create test client.

    :param app: Flask application fixture
    :type app: Flask
    :return: Flask test client
    :rtype: FlaskClient
    """
    return app.test_client()


@pytest.fixture
def sample_approval_request(app):
    """Create a sample approval request for testing.

    :param app: Flask application fixture
    :type app: Flask
    :return: ApprovalRequest instance
    :rtype: ApprovalRequest
    """
    with app.app_context():
        request = ApprovalRequest(
            request_source='Workday',
            requester_name='Test User',
            approver_id='U123456',
            justification_text='Test justification',
            metadata_json={'date_range': '2024-01-01 to 2024-01-05'}
        )
        db.session.add(request)
        db.session.commit()
        # Refresh to ensure object is attached to session
        db.session.refresh(request)
        yield request
        # Clean up
        db.session.delete(request)
        db.session.commit()



