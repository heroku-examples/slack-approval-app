"""Web interface routes for the approval hub.

This module provides web pages for creating and viewing approval requests,
designed for workshop and demo environments.
"""

import logging
from typing import Dict, Any
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import or_

from database import db
from models import ApprovalRequest

logger = logging.getLogger(__name__)

web_bp = Blueprint('web', __name__)


@web_bp.route('/status')
def status_dashboard() -> str:
    """Display status dashboard showing all approval requests.

    Shows pending, approved, and rejected requests with filtering options.

    :return: HTML response with status dashboard
    :rtype: str
    """
    return render_template('status_dashboard.html')


@web_bp.route('/api/requests')
def get_requests() -> tuple[Dict[str, Any], int]:
    """API endpoint to get all approval requests with optional filtering.

    Query parameters:
    - status: Filter by status (Pending, Approved, Rejected)
    - source: Filter by request source (Workday, Concur, Salesforce)
    - approver_id: Filter by approver Slack User ID

    :return: JSON response with list of requests
    :rtype: tuple[Dict[str, Any], int]
    """
    try:
        query = ApprovalRequest.query

        # Apply filters
        status_filter = request.args.get('status')
        if status_filter:
            query = query.filter_by(status=status_filter)

        source_filter = request.args.get('source')
        if source_filter:
            query = query.filter_by(request_source=source_filter)

        approver_filter = request.args.get('approver_id')
        if approver_filter:
            query = query.filter_by(approver_id=approver_filter)

        # Order by most recent first
        requests = query.order_by(ApprovalRequest.created_at.desc()).limit(100).all()

        # Convert to dictionaries
        requests_data = [req.to_dict() for req in requests]

        return jsonify({
            'requests': requests_data,
            'count': len(requests_data)
        }), 200

    except Exception as e:
        logger.error(f'Error fetching requests: {e}')
        return jsonify({'error': 'Internal server error'}), 500

