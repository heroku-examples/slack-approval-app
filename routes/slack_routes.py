"""Slack integration routes.

This module handles Slack events, interactive components, and Home Tab views
with proper request verification.
"""

import logging
import json
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, current_app
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier

from database import db
from models import ApprovalRequest
from utils.semantic_search import semantic_search
from utils.heroku_inference import get_embedding

logger = logging.getLogger(__name__)

slack_bp = Blueprint('slack', __name__)


def verify_slack_request() -> bool:
    """Verify Slack request signature.

    :return: True if signature is valid, False otherwise
    :rtype: bool
    """
    signing_secret = current_app.config.get('SLACK_SIGNING_SECRET')
    if not signing_secret:
        logger.warning('SLACK_SIGNING_SECRET not configured')
        return False

    verifier = SignatureVerifier(signing_secret)
    timestamp = request.headers.get('X-Slack-Request-Timestamp', '')
    signature = request.headers.get('X-Slack-Signature', '')

    body = request.get_data(as_text=True)
    return verifier.is_valid(timestamp=timestamp, body=body, signature=signature)


def get_slack_client() -> Optional[WebClient]:
    """Get configured Slack WebClient.

    :return: WebClient instance or None if not configured
    :rtype: Optional[WebClient]
    """
    bot_token = current_app.config.get('SLACK_BOT_TOKEN')
    if not bot_token:
        logger.warning('SLACK_BOT_TOKEN not configured')
        return None
    return WebClient(token=bot_token)


@slack_bp.route('/events', methods=['POST'])
def slack_events() -> tuple[Dict[str, Any], int]:
    """Handle Slack Events API requests.

    Processes URL verification challenges and event callbacks.

    :return: JSON response for Slack
    :rtype: tuple[Dict[str, Any], int]
    """
    if not verify_slack_request():
        return jsonify({'error': 'Invalid signature'}), 401

    data = request.get_json()

    # URL verification challenge
    if data.get('type') == 'url_verification':
        return jsonify({'challenge': data.get('challenge')}), 200

    # Event callback
    if data.get('type') == 'event_callback':
        event = data.get('event', {})
        event_type = event.get('type')

        if event_type == 'app_home_opened':
            user_id = event.get('user')
            if user_id:
                try:
                    from utils.slack_utils import publish_home_tab
                    publish_home_tab(user_id)
                except Exception as e:
                    logger.error(f'Error publishing home tab: {e}')

        return jsonify({'status': 'ok'}), 200

    return jsonify({'status': 'ok'}), 200


@slack_bp.route('/interactive', methods=['POST'])
def slack_interactive() -> tuple[Dict[str, Any], int]:
    """Handle Slack interactive component callbacks (button clicks).

    Processes approval/rejection actions and updates database and UI.

    :return: JSON response for Slack
    :rtype: tuple[Dict[str, Any], int]
    """
    if not verify_slack_request():
        return jsonify({'error': 'Invalid signature'}), 401

    try:
        payload = json.loads(request.form.get('payload', '{}'))
        action = payload.get('actions', [{}])[0]
        action_id = action.get('action_id')
        user_id = payload.get('user', {}).get('id')

        if not user_id:
            return jsonify({'error': 'User ID missing'}), 400

        # Handle approve/reject actions
        if action_id in ['approve', 'reject']:
            request_id = int(action.get('value', 0))
            new_status = 'Approved' if action_id == 'approve' else 'Rejected'

            # Update database
            approval_request = ApprovalRequest.query.get(request_id)
            if not approval_request:
                return jsonify({'error': 'Request not found'}), 404

            if approval_request.approver_id != user_id:
                return jsonify({'error': 'Unauthorized'}), 403

            approval_request.status = new_status
            db.session.commit()

            logger.info(f'Request {request_id} {new_status.lower()} by {user_id}')

            # Update Home Tab
            from utils.slack_utils import publish_home_tab
            publish_home_tab(user_id)

            # Send confirmation message (simulated - in real app, would DM requester)
            client = get_slack_client()
            if client:
                try:
                    client.chat_postMessage(
                        channel=user_id,
                        text=f'You {new_status.lower()} the request from {approval_request.requester_name}'
                    )
                except SlackApiError as e:
                    logger.warning(f'Failed to send confirmation message: {e}')

            return jsonify({'status': 'ok'}), 200

        return jsonify({'error': 'Unknown action'}), 400

    except Exception as e:
        logger.error(f'Error handling interactive component: {e}')
        return jsonify({'error': 'Internal server error'}), 500


@slack_bp.route('/home', methods=['POST'])
def slack_home() -> tuple[Dict[str, Any], int]:
    """Handle Slack Home Tab view requests.

    Returns the Home Tab view with pending approval requests.

    :return: JSON response with Home Tab view
    :rtype: tuple[Dict[str, Any], int]
    """
    if not verify_slack_request():
        return jsonify({'error': 'Invalid signature'}), 401

    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'User ID missing'}), 400

        view = build_home_tab_view(user_id)
        return jsonify(view), 200

    except Exception as e:
        logger.error(f'Error building home tab view: {e}')
        return jsonify({'error': 'Internal server error'}), 500


def build_home_tab_view(user_id: str, source_filter: Optional[str] = None,
                        search_query: Optional[str] = None) -> Dict[str, Any]:
    """Build Slack Home Tab view with approval requests.

    :param user_id: Slack User ID of the approver
    :type user_id: str
    :param source_filter: Optional filter by request source
    :type source_filter: Optional[str]
    :param search_query: Optional semantic search query
    :type search_query: Optional[str]
    :return: Slack Block Kit view dictionary
    :rtype: Dict[str, Any]
    """
    # Query pending requests
    query = ApprovalRequest.query.filter_by(
        approver_id=user_id,
        status='Pending'
    )

    if source_filter:
        query = query.filter_by(request_source=source_filter)

    # Handle semantic search
    request_ids = None
    if search_query:
        query_vector = get_embedding(search_query)
        if query_vector:
            request_ids = semantic_search(user_id, query_vector)
            if request_ids:
                query = query.filter(ApprovalRequest.id.in_(request_ids))
            else:
                query = query.filter(False)  # No results

    requests = query.order_by(ApprovalRequest.created_at.desc()).limit(20).all()

    # Build blocks
    blocks = [
        {
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': '📋 Approval Requests'
            }
        },
        {
            'type': 'divider'
        }
    ]

    # Add filter controls
    blocks.append({
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': '*Filter by Source:*'
        },
        'accessory': {
            'type': 'static_select',
            'placeholder': {
                'type': 'plain_text',
                'text': 'Select source...'
            },
            'options': [
                {'text': {'type': 'plain_text', 'text': 'All'}, 'value': 'all'},
                {'text': {'type': 'plain_text', 'text': 'Workday'}, 'value': 'Workday'},
                {'text': {'type': 'plain_text', 'text': 'Concur'}, 'value': 'Concur'},
                {'text': {'type': 'plain_text', 'text': 'Salesforce'}, 'value': 'Salesforce'}
            ],
            'action_id': 'filter_source'
        }
    })

    # Add search input
    blocks.append({
        'type': 'input',
        'element': {
            'type': 'plain_text_input',
            'action_id': 'semantic_search',
            'placeholder': {
                'type': 'plain_text',
                'text': 'Search by natural language...'
            }
        },
        'label': {
            'type': 'plain_text',
            'text': 'Semantic Search'
        }
    })

    blocks.append({'type': 'divider'})

    # Add approval request cards
    if not requests:
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*No pending approval requests* ✅'
            }
        })
    else:
        for req in requests:
            card_blocks = build_approval_card(req)
            blocks.extend(card_blocks)
            blocks.append({'type': 'divider'})

    return {
        'type': 'home',
        'blocks': blocks
    }


def build_approval_card(request: ApprovalRequest) -> list[Dict[str, Any]]:
    """Build Block Kit card for an approval request.

    :param request: Approval request model instance
    :type request: ApprovalRequest
    :return: List of Block Kit blocks for the card
    :rtype: list[Dict[str, Any]]
    """
    metadata = request.metadata_json or {}
    source = request.request_source

    # Build card based on source type
    if source == 'Workday':
        # PTO request
        date_range = metadata.get('date_range', 'N/A')
        card_text = f"*{request.requester_name}* requested PTO\n📅 *Date Range:* {date_range}"
    elif source == 'Concur':
        # Expense request
        amount = metadata.get('amount', 0)
        card_text = f"*{request.requester_name}* submitted expense\n💰 *Amount:* ${amount:,.2f}"
        if metadata.get('pdf_url'):
            card_text += f"\n📄 [View PDF]({metadata.get('pdf_url')})"
    elif source == 'Salesforce':
        # Deal request
        customer = metadata.get('customer_name', 'N/A')
        deal_value = metadata.get('deal_value', 0)
        risk_score = metadata.get('risk_score', 0)
        card_text = f"*{request.requester_name}* submitted deal\n👤 *Customer:* {customer}\n💵 *Deal Value:* ${deal_value:,.2f}\n⚠️ *Risk Score:* {risk_score}/10"
    else:
        card_text = f"*{request.requester_name}* submitted a {source} request"

    # Add AI summary if available
    if metadata.get('ai_summary'):
        card_text += f"\n\n*Summary:* {metadata.get('ai_summary')}"

    # Add justification if available
    if request.justification_text:
        justification = request.justification_text[:200] + '...' if len(request.justification_text) > 200 else request.justification_text
        card_text += f"\n\n*Justification:* {justification}"

    blocks = [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': card_text
            }
        },
        {
            'type': 'actions',
            'elements': [
                {
                    'type': 'button',
                    'text': {
                        'type': 'plain_text',
                        'text': '✅ Approve'
                    },
                    'style': 'primary',
                    'action_id': 'approve',
                    'value': str(request.id)
                },
                {
                    'type': 'button',
                    'text': {
                        'type': 'plain_text',
                        'text': '❌ Reject'
                    },
                    'style': 'danger',
                    'action_id': 'reject',
                    'value': str(request.id)
                }
            ]
        }
    ]

    return blocks



