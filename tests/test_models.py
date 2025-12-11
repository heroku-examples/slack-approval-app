"""Tests for database models.

This module contains tests for the ApprovalRequest model.
"""

import pytest
from datetime import datetime

from models import ApprovalRequest
from database import db


def test_approval_request_creation(app):
    """Test creating an approval request.

    :param app: Flask application fixture
    :type app: Flask
    """
    with app.app_context():
        request = ApprovalRequest(
            request_source='Workday',
            requester_name='Test User',
            approver_id='U123456',
            justification_text='Test justification',
            metadata_json={'key': 'value'}
        )

        assert request.status == 'Pending'
        assert request.request_source == 'Workday'
        assert request.requester_name == 'Test User'


def test_approval_request_to_dict(app, sample_approval_request):
    """Test converting approval request to dictionary.

    :param app: Flask application fixture
    :type app: Flask
    :param sample_approval_request: Sample approval request fixture
    :type sample_approval_request: ApprovalRequest
    """
    with app.app_context():
        # Re-query to get fresh instance in this session
        request = ApprovalRequest.query.get(sample_approval_request.id)
        data = request.to_dict()
        assert 'id' in data
        assert 'request_source' in data
        assert 'requester_name' in data
        assert 'status' in data
        assert data['status'] == 'Pending'


def test_approval_request_status_update(app, sample_approval_request):
    """Test updating approval request status.

    :param app: Flask application fixture
    :type app: Flask
    :param sample_approval_request: Sample approval request fixture
    :type sample_approval_request: ApprovalRequest
    """
    with app.app_context():
        # Re-query to get fresh instance in this session
        request = ApprovalRequest.query.get(sample_approval_request.id)
        request.status = 'Approved'
        db.session.commit()

        updated = ApprovalRequest.query.get(sample_approval_request.id)
        assert updated.status == 'Approved'



