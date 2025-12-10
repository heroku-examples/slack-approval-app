"""Database configuration and initialization module.

This module handles database connection setup, SQLAlchemy initialization,
and pgvector extension support.
"""

import logging
from typing import Optional
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

logger = logging.getLogger(__name__)

# Initialize SQLAlchemy
db = SQLAlchemy()


def init_db(app: Flask) -> None:
    """Initialize database connection and extensions.

    :param app: Flask application instance
    :type app: Flask
    """
    db.init_app(app)

    with app.app_context():
        # Enable pgvector extension
        try:
            db.session.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
            db.session.commit()
            logger.info('pgvector extension enabled')
        except Exception as e:
            logger.warning(f'Could not enable pgvector extension: {e}')
            db.session.rollback()

        # Create all tables
        db.create_all()
        logger.info('Database tables created/verified')


def get_db_connection():
    """Get raw database connection for direct SQL operations.

    :return: Database connection object
    :rtype: Optional[Connection]
    """
    return db.engine.connect()



