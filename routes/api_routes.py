"""API routes for external system integration.

This module provides REST API endpoints for external systems to submit
approval requests via webhook.
"""

import logging
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError

from database import db
from models import ApprovalRequest
from utils.heroku_inference import get_embedding, generate_summary_and_risk_score
from utils.semantic_search import vector_to_string
from utils.slack_utils import publish_home_tab

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)


@api_bp.route('/new-approval', methods=['POST'])
def new_approval() -> tuple[Dict[str, Any], int]:
    """Create a new approval request from external system webhook.

    Accepts JSON payload with approval request data, generates embeddings
    and summary, stores in database, and updates Slack Home Tab.

    Expected JSON payload:
    {
        "request_source": "Workday|Concur|Salesforce",
        "requester_name": "John Doe",
        "approver_id": "U123456",
        "justification_text": "Request justification...",
        "metadata": {
            "date_range": "2024-01-01 to 2024-01-05",
            "amount": 500.00,
            ...
        }
    }

    :return: JSON response with request ID and status
    :rtype: tuple[Dict[str, Any], int]
    :raises: 400 for invalid input, 500 for server errors
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        # Validate required fields
        required_fields = ['request_source', 'requester_name', 'approver_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        request_source = data['request_source']
        requester_name = data['requester_name']
        approver_id = data['approver_id']
        justification_text = data.get('justification_text', '')
        metadata = data.get('metadata', {})

        # Generate embedding if justification text exists
        search_vector = None
        if justification_text:
            embedding = get_embedding(justification_text)
            if embedding:
                search_vector = vector_to_string(embedding)

        # Generate summary and risk score
        ai_analysis = generate_summary_and_risk_score(justification_text)
        if ai_analysis.get('summary'):
            metadata['ai_summary'] = ai_analysis['summary']
        if ai_analysis.get('risk_score') is not None:
            metadata['risk_score'] = ai_analysis['risk_score']

        # Create approval request
        approval_request = ApprovalRequest(
            request_source=request_source,
            requester_name=requester_name,
            approver_id=approver_id,
            justification_text=justification_text,
            metadata_json=metadata,
            search_vector=search_vector
        )

        db.session.add(approval_request)
        db.session.commit()

        logger.info(f'Created approval request {approval_request.id} from {request_source}')

        # Update Slack Home Tab for the approver
        try:
            publish_home_tab(approver_id)
        except Exception as e:
            logger.warning(f'Failed to update Slack Home Tab: {e}')

        return jsonify({
            'id': approval_request.id,
            'status': 'created',
            'message': 'Approval request created successfully'
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f'Database error creating approval request: {e}')
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        logger.error(f'Unexpected error creating approval request: {e}')
        return jsonify({'error': 'Internal server error'}), 500



