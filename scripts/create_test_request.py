"""Create a test approval request for testing the approval flow.

This script can be run locally or on Heroku to create test approval requests
without needing to connect to external systems.
"""

import os
import sys
import json
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from dotenv import load_dotenv

from app import app
from database import db
from models import ApprovalRequest
from utils.heroku_inference import get_embedding, generate_summary_and_risk_score
from utils.semantic_search import vector_to_string
from utils.slack_utils import publish_home_tab

load_dotenv()


def create_test_request(
    request_source: str,
    requester_name: str,
    approver_id: str,
    justification_text: str,
    metadata: Optional[dict] = None
) -> ApprovalRequest:
    """Create a test approval request.

    :param request_source: Source system (Workday, Concur, Salesforce)
    :type request_source: str
    :param requester_name: Name of the requester
    :type requester_name: str
    :param approver_id: Slack User ID of the approver
    :type approver_id: str
    :param justification_text: Justification for the request
    :type justification_text: str
    :param metadata: Optional metadata dictionary
    :type metadata: Optional[dict]
    :return: Created ApprovalRequest instance
    :rtype: ApprovalRequest
    """
    with app.app_context():
        # Generate embedding if justification text exists
        search_vector = None
        if justification_text:
            embedding = get_embedding(justification_text)
            if embedding:
                search_vector = vector_to_string(embedding)

        # Generate summary and risk score
        ai_analysis = generate_summary_and_risk_score(justification_text)
        final_metadata = metadata.copy() if metadata else {}
        if ai_analysis.get('summary'):
            final_metadata['ai_summary'] = ai_analysis['summary']
        if ai_analysis.get('risk_score') is not None:
            final_metadata['risk_score'] = ai_analysis['risk_score']

        # Create approval request
        approval_request = ApprovalRequest(
            request_source=request_source,
            requester_name=requester_name,
            approver_id=approver_id,
            justification_text=justification_text,
            metadata_json=final_metadata,
            search_vector=search_vector
        )

        db.session.add(approval_request)
        db.session.commit()

        print(f'✅ Created approval request #{approval_request.id}')
        print(f'   Source: {request_source}')
        print(f'   Requester: {requester_name}')
        print(f'   Approver: {approver_id}')

        # Update Slack Home Tab
        try:
            publish_home_tab(approver_id)
            print(f'✅ Updated Slack Home Tab for approver')
        except Exception as e:
            print(f'⚠️  Warning: Could not update Slack Home Tab: {e}')

        return approval_request


def create_sample_requests(approver_id: str) -> None:
    """Create a set of sample requests for testing.

    :param approver_id: Slack User ID of the approver
    :type approver_id: str
    """
    print(f'Creating sample requests for approver: {approver_id}\n')

    # Workday PTO request
    create_test_request(
        request_source='Workday',
        requester_name='Alice Johnson',
        approver_id=approver_id,
        justification_text='I need to take time off for a family vacation to Hawaii. We have been planning this trip for months and have already booked flights and hotels.',
        metadata={
            'date_range': '2024-02-15 to 2024-02-22',
            'days_requested': 5,
            'remaining_pto': 10
        }
    )

    # Concur expense request
    create_test_request(
        request_source='Concur',
        requester_name='Bob Smith',
        approver_id=approver_id,
        justification_text='Business trip to San Francisco for client meeting. Expenses include flights, hotel, meals, and transportation. All receipts attached.',
        metadata={
            'amount': 2450.75,
            'currency': 'USD',
            'trip_dates': '2024-02-05 to 2024-02-07',
            'pdf_url': 'https://example.com/receipts/expense_001.pdf',
            'category': 'Travel'
        }
    )

    # Salesforce deal request
    create_test_request(
        request_source='Salesforce',
        requester_name='Carol Williams',
        approver_id=approver_id,
        justification_text='Large enterprise deal with TechCorp Inc. This is a strategic account with high revenue potential. Customer has requested special pricing terms and extended payment schedule.',
        metadata={
            'customer_name': 'TechCorp Inc.',
            'deal_value': 250000.00,
            'currency': 'USD',
            'close_date': '2024-03-31',
            'stage': 'Negotiation'
        }
    )

    print('\n✨ Sample requests created! Check your Slack Home Tab.')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Create test approval requests')
    parser.add_argument(
        '--approver-id',
        type=str,
        help='Slack User ID of the approver (starts with U)',
        default=os.environ.get('SLACK_TEST_APPROVER_ID')
    )
    parser.add_argument(
        '--source',
        type=str,
        choices=['Workday', 'Concur', 'Salesforce'],
        help='Request source system'
    )
    parser.add_argument(
        '--requester',
        type=str,
        help='Requester name'
    )
    parser.add_argument(
        '--justification',
        type=str,
        help='Justification text'
    )
    parser.add_argument(
        '--metadata',
        type=str,
        help='Metadata as JSON string'
    )
    parser.add_argument(
        '--samples',
        action='store_true',
        help='Create a set of sample requests'
    )

    args = parser.parse_args()

    if not args.approver_id:
        print('❌ Error: --approver-id is required')
        print('   Set SLACK_TEST_APPROVER_ID environment variable or use --approver-id')
        print('   To find your Slack User ID:')
        print('   1. Open your Slack profile')
        print('   2. Click "More" → "Copy member ID"')
        sys.exit(1)

    if args.samples:
        create_sample_requests(args.approver_id)
    elif args.source and args.requester and args.justification:
        metadata = json.loads(args.metadata) if args.metadata else {}
        create_test_request(
            request_source=args.source,
            requester_name=args.requester,
            approver_id=args.approver_id,
            justification_text=args.justification,
            metadata=metadata
        )
    else:
        print('❌ Error: Either use --samples or provide --source, --requester, and --justification')
        parser.print_help()
        sys.exit(1)

