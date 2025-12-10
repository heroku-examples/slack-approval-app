"""Tests for API routes.

This module contains tests for the external system integration API endpoints.
"""

import pytest
import json
from flask import Flask

from models import ApprovalRequest
from database import db


def test_health_check(client):
    """Test health check endpoint.

    :param client: Flask test client
    :type client: FlaskClient
    """
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'


def test_new_approval_missing_fields(client):
    """Test new approval endpoint with missing required fields.

    :param client: Flask test client
    :type client: FlaskClient
    """
    response = client.post('/api/new-approval', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_new_approval_success(client, app):
    """Test successful creation of approval request.

    :param client: Flask test client
    :type client: FlaskClient
    :param app: Flask application fixture
    :type app: Flask
    """
    with app.app_context():
        payload = {
            'request_source': 'Workday',
            'requester_name': 'John Doe',
            'approver_id': 'U123456',
            'justification_text': 'Need time off for vacation',
            'metadata': {
                'date_range': '2024-01-01 to 2024-01-05'
            }
        }

        response = client.post('/api/new-approval', json=payload)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'created'
        assert 'id' in data

        # Verify request was created in database
        request = ApprovalRequest.query.get(data['id'])
        assert request is not None
        assert request.request_source == 'Workday'
        assert request.requester_name == 'John Doe'


def test_new_approval_different_sources(client, app):
    """Test creating approval requests from different sources.

    :param client: Flask test client
    :type client: FlaskClient
    :param app: Flask application fixture
    :type app: Flask
    """
    sources = ['Workday', 'Concur', 'Salesforce']

    with app.app_context():
        for source in sources:
            payload = {
                'request_source': source,
                'requester_name': 'Test User',
                'approver_id': 'U123456',
                'justification_text': f'Test {source} request',
                'metadata': {}
            }

            response = client.post('/api/new-approval', json=payload)
            assert response.status_code == 201

        # Verify all requests were created
        requests = ApprovalRequest.query.all()
        assert len(requests) == len(sources)



