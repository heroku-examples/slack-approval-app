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

    ---
    tags:
      - Approval Requests
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: approval_request
        description: Approval request data
        required: true
        schema:
          type: object
          required:
            - request_source
            - requester_name
            - approver_id
          properties:
            request_source:
              type: string
              enum: [Workday, Concur, Salesforce]
              description: Source system identifier
              example: Workday
            requester_name:
              type: string
              description: Name of the employee making the request
              example: John Doe
            approver_id:
              type: string
              description: Slack User ID of the manager who should approve
              example: U123456
            justification_text:
              type: string
              description: Text justification for the request
              example: Need time off for family vacation
            metadata:
              type: object
              description: Source-specific metadata (varies by request_source)
              properties:
                date_range:
                  type: string
                  description: Date range (for Workday PTO requests)
                  example: "2024-01-01 to 2024-01-05"
                days_requested:
                  type: integer
                  description: Number of days requested (for Workday)
                  example: 5
                amount:
                  type: number
                  description: Expense amount (for Concur)
                  example: 1250.75
                trip_dates:
                  type: string
                  description: Trip dates (for Concur)
                  example: "2024-02-05 to 2024-02-07"
                customer_name:
                  type: string
                  description: Customer name (for Salesforce)
                  example: TechCorp Inc.
                deal_value:
                  type: number
                  description: Deal value (for Salesforce)
                  example: 250000.00
    responses:
      201:
        description: Approval request created successfully
        schema:
          type: object
          properties:
            id:
              type: integer
              description: ID of the created approval request
              example: 1
            status:
              type: string
              example: created
            message:
              type: string
              example: Approval request created successfully
      400:
        description: Bad request - missing required fields or invalid data
        schema:
          type: object
          properties:
            error:
              type: string
              example: Missing required field: request_source
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: Internal server error
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



