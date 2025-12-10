"""Database models for the Universal Approval Hub.

This module defines the SQLAlchemy models for approval requests,
including support for pgvector semantic search.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from database import db


class ApprovalRequest(db.Model):
    """Approval request model.

    Stores approval requests from various systems (Workday, Concur, Salesforce)
    with support for semantic search via vector embeddings.

    :attr id: Primary key identifier
    :attr request_source: Source system (Workday, Concur, Salesforce)
    :attr requester_name: Name of the employee making the request
    :attr approver_id: Slack User ID of the manager who should approve
    :attr status: Current status (Pending, Approved, Rejected)
    :attr justification_text: Text justification for the request
    :attr metadata_json: Flexible JSON storage for source-specific data
    :attr search_vector: Vector embedding for semantic search
    :attr created_at: Timestamp when request was created
    :attr updated_at: Timestamp when request was last updated
    """

    __tablename__ = 'approval_requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_source = Column(String(50), nullable=False, index=True)
    requester_name = Column(String(100), nullable=False)
    approver_id = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False, default='Pending', index=True)
    justification_text = Column(Text, nullable=True)
    metadata_json = Column(JSONB, nullable=True)
    # Note: search_vector is stored as vector(1024) in database
    # SQLAlchemy doesn't have native pgvector support, so we use Text
    # and handle casting in SQL queries
    search_vector = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    def __init__(self, request_source: str, requester_name: str, approver_id: str,
                 justification_text: Optional[str] = None,
                 metadata_json: Optional[Dict[str, Any]] = None,
                 search_vector: Optional[str] = None):
        """Initialize a new approval request.

        :param request_source: Source system identifier
        :type request_source: str
        :param requester_name: Name of the requester
        :type requester_name: str
        :param approver_id: Slack User ID of approver
        :type approver_id: str
        :param justification_text: Optional justification text
        :type justification_text: Optional[str]
        :param metadata_json: Optional metadata dictionary
        :type metadata_json: Optional[Dict[str, Any]]
        :param search_vector: Optional vector embedding as string
        :type search_vector: Optional[str]
        """
        self.request_source = request_source
        self.requester_name = requester_name
        self.approver_id = approver_id
        self.justification_text = justification_text
        self.metadata_json = metadata_json or {}
        self.search_vector = search_vector
        self.status = 'Pending'

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary.

        :return: Dictionary representation of the approval request
        :rtype: Dict[str, Any]
        """
        return {
            'id': self.id,
            'request_source': self.request_source,
            'requester_name': self.requester_name,
            'approver_id': self.approver_id,
            'status': self.status,
            'justification_text': self.justification_text,
            'metadata_json': self.metadata_json,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        """String representation of the model.

        :return: String representation
        :rtype: str
        """
        return f'<ApprovalRequest {self.id}: {self.request_source} - {self.status}>'

