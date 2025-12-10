"""Seed database with sample approval requests.

This script creates sample approval requests from different sources
(Workday, Concur, Salesforce) for testing and demonstration.
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from dotenv import load_dotenv

from app import app
from database import db, init_db
from models import ApprovalRequest
from utils.heroku_inference import get_embedding, generate_summary_and_risk_score
from utils.semantic_search import vector_to_string

load_dotenv()


def seed_approval_requests() -> None:
    """Seed database with sample approval requests.

    Creates sample requests from Workday, Concur, and Salesforce
    with appropriate metadata and embeddings.
    """
    with app.app_context():
        # Clear existing data (optional - comment out to keep existing data)
        # ApprovalRequest.query.delete()
        # db.session.commit()

        # Sample approver ID (replace with actual Slack User ID for testing)
        approver_id = os.environ.get('SLACK_TEST_APPROVER_ID', 'U1234567890')

        # Sample Workday PTO requests
        workday_requests = [
            {
                'requester_name': 'Alice Johnson',
                'justification_text': 'I need to take time off for a family vacation to Hawaii. We have been planning this trip for months and have already booked flights and hotels.',
                'metadata': {
                    'date_range': '2024-02-15 to 2024-02-22',
                    'days_requested': 5,
                    'remaining_pto': 10
                }
            },
            {
                'requester_name': 'Bob Smith',
                'justification_text': 'Requesting time off for medical appointment and recovery. Doctor recommended taking a few days to rest after the procedure.',
                'metadata': {
                    'date_range': '2024-02-10 to 2024-02-12',
                    'days_requested': 2,
                    'remaining_pto': 8
                }
            }
        ]

        # Sample Concur expense requests
        concur_requests = [
            {
                'requester_name': 'Carol Williams',
                'justification_text': 'Business trip to San Francisco for client meeting. Expenses include flights, hotel, meals, and transportation. All receipts attached.',
                'metadata': {
                    'amount': 2450.75,
                    'currency': 'USD',
                    'trip_dates': '2024-02-05 to 2024-02-07',
                    'pdf_url': 'https://example.com/receipts/expense_001.pdf',
                    'category': 'Travel'
                }
            },
            {
                'requester_name': 'David Brown',
                'justification_text': 'Team dinner with new clients to discuss partnership opportunities. Restaurant bill for 8 people including drinks and tip.',
                'metadata': {
                    'amount': 485.50,
                    'currency': 'USD',
                    'date': '2024-02-08',
                    'pdf_url': 'https://example.com/receipts/expense_002.pdf',
                    'category': 'Entertainment'
                }
            }
        ]

        # Sample Salesforce deal requests
        salesforce_requests = [
            {
                'requester_name': 'Emma Davis',
                'justification_text': 'Large enterprise deal with TechCorp Inc. This is a strategic account with high revenue potential. Customer has requested special pricing terms and extended payment schedule.',
                'metadata': {
                    'customer_name': 'TechCorp Inc.',
                    'deal_value': 250000.00,
                    'currency': 'USD',
                    'close_date': '2024-03-31',
                    'stage': 'Negotiation'
                }
            },
            {
                'requester_name': 'Frank Miller',
                'justification_text': 'Standard SMB deal with StartupXYZ. Customer is a new company with limited credit history. Requesting approval for standard terms.',
                'metadata': {
                    'customer_name': 'StartupXYZ',
                    'deal_value': 15000.00,
                    'currency': 'USD',
                    'close_date': '2024-02-28',
                    'stage': 'Proposal'
                }
            }
        ]

        # Create Workday requests
        for req_data in workday_requests:
            justification = req_data['justification_text']
            
            # Generate embedding
            embedding = get_embedding(justification)
            search_vector = vector_to_string(embedding) if embedding else None
            
            # Generate summary and risk score
            ai_analysis = generate_summary_and_risk_score(justification)
            metadata = req_data['metadata'].copy()
            if ai_analysis.get('summary'):
                metadata['ai_summary'] = ai_analysis['summary']
            if ai_analysis.get('risk_score') is not None:
                metadata['risk_score'] = ai_analysis['risk_score']

            approval = ApprovalRequest(
                request_source='Workday',
                requester_name=req_data['requester_name'],
                approver_id=approver_id,
                justification_text=justification,
                metadata_json=metadata,
                search_vector=search_vector
            )
            db.session.add(approval)

        # Create Concur requests
        for req_data in concur_requests:
            justification = req_data['justification_text']
            
            # Generate embedding
            embedding = get_embedding(justification)
            search_vector = vector_to_string(embedding) if embedding else None
            
            # Generate summary and risk score
            ai_analysis = generate_summary_and_risk_score(justification)
            metadata = req_data['metadata'].copy()
            if ai_analysis.get('summary'):
                metadata['ai_summary'] = ai_analysis['summary']
            if ai_analysis.get('risk_score') is not None:
                metadata['risk_score'] = ai_analysis['risk_score']

            approval = ApprovalRequest(
                request_source='Concur',
                requester_name=req_data['requester_name'],
                approver_id=approver_id,
                justification_text=justification,
                metadata_json=metadata,
                search_vector=search_vector
            )
            db.session.add(approval)

        # Create Salesforce requests
        for req_data in salesforce_requests:
            justification = req_data['justification_text']
            
            # Generate embedding
            embedding = get_embedding(justification)
            search_vector = vector_to_string(embedding) if embedding else None
            
            # Generate summary and risk score
            ai_analysis = generate_summary_and_risk_score(justification)
            metadata = req_data['metadata'].copy()
            if ai_analysis.get('summary'):
                metadata['ai_summary'] = ai_analysis['summary']
            if ai_analysis.get('risk_score') is not None:
                metadata['risk_score'] = ai_analysis['risk_score']

            approval = ApprovalRequest(
                request_source='Salesforce',
                requester_name=req_data['requester_name'],
                approver_id=approver_id,
                justification_text=justification,
                metadata_json=metadata,
                search_vector=search_vector
            )
            db.session.add(approval)

        # Commit all requests
        db.session.commit()
        print(f'✅ Seeded {len(workday_requests) + len(concur_requests) + len(salesforce_requests)} approval requests')


if __name__ == '__main__':
    print('🌱 Seeding database with sample approval requests...')
    seed_approval_requests()
    print('✨ Seeding complete!')



