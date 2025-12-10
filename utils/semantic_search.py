"""Semantic search utility using pgvector.

This module provides functions for performing semantic search on approval
requests using vector embeddings and cosine similarity.
"""

import logging
from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import db

logger = logging.getLogger(__name__)


def semantic_search(approver_id: str, query_vector: List[float], limit: int = 10,
                    threshold: float = 0.7) -> List[int]:
    """Perform semantic search on approval requests.

    Uses pgvector cosine similarity operator (<=>) to find similar requests.

    :param approver_id: Slack User ID of the approver
    :type approver_id: str
    :param query_vector: Vector embedding of the search query
    :type query_vector: List[float]
    :param limit: Maximum number of results to return
    :type limit: int
    :param threshold: Minimum similarity threshold (0-1)
    :type threshold: float
    :return: List of approval request IDs matching the search
    :rtype: List[int]
    """
    if not query_vector:
        logger.warning('Empty query vector provided')
        return []

    try:
        # Convert vector list to PostgreSQL vector format
        vector_str = '[' + ','.join(map(str, query_vector)) + ']'

        # SQL query using cosine similarity (<=> operator)
        # Lower distance means higher similarity
        query = text("""
            SELECT id, 
                   (search_vector::vector <=> :query_vector::vector) as distance
            FROM approval_requests
            WHERE approver_id = :approver_id
              AND status = 'Pending'
              AND search_vector IS NOT NULL
              AND (search_vector::vector <=> :query_vector::vector) <= :threshold
            ORDER BY distance ASC
            LIMIT :limit
        """)

        result = db.session.execute(
            query,
            {
                'approver_id': approver_id,
                'query_vector': vector_str,
                'threshold': 1.0 - threshold,  # Convert similarity to distance
                'limit': limit
            }
        )

        request_ids = [row[0] for row in result.fetchall()]
        logger.info(f'Semantic search found {len(request_ids)} matching requests')
        return request_ids

    except Exception as e:
        logger.error(f'Error performing semantic search: {e}')
        return []


def vector_to_string(vector: List[float]) -> str:
    """Convert vector list to PostgreSQL vector string format.

    :param vector: List of float values
    :type vector: List[float]
    :return: PostgreSQL vector string format
    :rtype: str
    """
    return '[' + ','.join(map(str, vector)) + ']'



