"""Pytest configuration and fixtures.

This module provides shared fixtures for all tests.
"""

import pytest
import os
from flask import Flask
from dotenv import load_dotenv

from app import app as flask_app
from database import db, init_db
from models import ApprovalRequest

load_dotenv()


@pytest.fixture
def app():
    """Create Flask application for testing.

    :return: Flask application instance
    :rtype: Flask
    """
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'TEST_DATABASE_URL',
        'postgresql://localhost/test_approval_hub'
    )
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['SLACK_BOT_TOKEN'] = 'xoxb-test-token'
    flask_app.config['SLACK_SIGNING_SECRET'] = 'test-signing-secret'

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()


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
        return request



