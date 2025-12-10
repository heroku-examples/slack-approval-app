"""Tests for Slack integration routes.

This module contains tests for Slack events, interactive components,
and Home Tab functionality.
"""

import pytest
import json
import hmac
import hashlib
import time
from flask import Flask

from models import ApprovalRequest
from database import db


def generate_slack_signature(timestamp: str, body: str, secret: str) -> str:
    """Generate Slack request signature for testing.

    :param timestamp: Request timestamp
    :type timestamp: str
    :param body: Request body
    :type body: str
    :param secret: Signing secret
    :type secret: str
    :return: Signature string
    :rtype: str
    """
    sig_basestring = f'v0:{timestamp}:{body}'
    signature = hmac.new(
        secret.encode('utf-8'),
        sig_basestring.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f'v0={signature}'


def test_slack_url_verification(client):
    """Test Slack URL verification challenge.

    :param client: Flask test client
    :type client: FlaskClient
    """
    timestamp = str(int(time.time()))
    challenge = 'test_challenge_token'
    body = json.dumps({
        'type': 'url_verification',
        'challenge': challenge
    })
    signature = generate_slack_signature(timestamp, body, 'test-signing-secret')

    response = client.post(
        '/slack/events',
        data=body,
        content_type='application/json',
        headers={
            'X-Slack-Request-Timestamp': timestamp,
            'X-Slack-Signature': signature
        }
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['challenge'] == challenge


def test_slack_events_invalid_signature(client):
    """Test Slack events endpoint with invalid signature.

    :param client: Flask test client
    :type client: FlaskClient
    """
    response = client.post(
        '/slack/events',
        data=json.dumps({'type': 'event_callback'}),
        content_type='application/json',
        headers={
            'X-Slack-Request-Timestamp': str(int(time.time())),
            'X-Slack-Signature': 'invalid_signature'
        }
    )

    assert response.status_code == 401


def test_slack_home_tab(client, app, sample_approval_request):
    """Test Slack Home Tab view generation.

    :param client: Flask test client
    :type client: FlaskClient
    :param app: Flask application fixture
    :type app: Flask
    :param sample_approval_request: Sample approval request fixture
    :type sample_approval_request: ApprovalRequest
    """
    timestamp = str(int(time.time()))
    body = json.dumps({'user_id': 'U123456'})
    signature = generate_slack_signature(timestamp, body, 'test-signing-secret')

    response = client.post(
        '/slack/home',
        data=body,
        content_type='application/json',
        headers={
            'X-Slack-Request-Timestamp': timestamp,
            'X-Slack-Signature': signature
        }
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'blocks' in data
    assert data['type'] == 'home'



