"""Database configuration and initialization module.

This module handles database connection setup, SQLAlchemy initialization,
and pgvector extension support.
"""

import logging
from typing import Optional
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError

logger = logging.getLogger(__name__)

# Initialize SQLAlchemy
db = SQLAlchemy()


def init_db(app: Flask) -> None:
    """Initialize database connection and extensions.

    Initializes the database connection and sets up tables/extensions.
    On Heroku, this will use the DATABASE_URL environment variable automatically.

    :param app: Flask application instance
    :type app: Flask
    :raises Exception: If database connection fails and DATABASE_URL is set
    """
    import os
    
    db.init_app(app)
    
    # Check if DATABASE_URL is set (required on Heroku)
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.warning(
            'DATABASE_URL not set. Database operations will fail. '
            'On Heroku, attach a Postgres add-on: heroku addons:create heroku-postgresql:mini'
        )

    with app.app_context():
        try:
            # Test database connection
            db.engine.connect()
            logger.info('Database connection established')
            
            # Enable pgvector extension
            try:
                db.session.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
                db.session.commit()
                logger.info('pgvector extension enabled')
            except Exception as e:
                logger.warning(f'Could not enable pgvector extension: {e}')
                db.session.rollback()

            # Create all tables
            # Handle race condition when multiple workers start simultaneously
            try:
                db.create_all()
                logger.info('Database tables created/verified')
            except IntegrityError as e:
                # Handle race condition: if tables/sequences already exist from another worker
                # This can happen when multiple gunicorn workers start at the same time
                error_str = str(e).lower()
                if 'already exists' in error_str or 'duplicate key' in error_str or 'unique constraint' in error_str:
                    logger.info(
                        'Database tables/sequences already exist '
                        '(likely created by another worker during startup)'
                    )
                    # Verify tables exist by checking if we can query metadata
                    try:
                        from sqlalchemy import inspect
                        inspector = inspect(db.engine)
                        tables = inspector.get_table_names()
                        if 'approval_requests' in tables:
                            logger.info('Database tables verified - all tables exist')
                        else:
                            # If table doesn't exist, this is a real problem
                            logger.error('Table does not exist despite sequence error - this is unexpected')
                            raise
                    except Exception as verify_error:
                        # If verification fails, log but don't crash - tables likely exist
                        logger.warning(f'Could not verify table existence: {verify_error}')
                else:
                    # Re-raise if it's a different integrity error
                    raise
            except OperationalError as e:
                # Re-raise operational errors (connection issues)
                raise
            
        except Exception as e:
            # If DATABASE_URL is explicitly set, this is a real error
            if database_url:
                logger.error(
                    f'Failed to connect to database at {database_url[:20]}... '
                    f'Error: {e}'
                )
                raise
            else:
                # If DATABASE_URL is not set, log warning but don't crash
                logger.warning(
                    f'Database not available (DATABASE_URL not set). '
                    f'Some features may not work. Error: {e}'
                )


def get_db_connection():
    """Get raw database connection for direct SQL operations.

    :return: Database connection object
    :rtype: Optional[Connection]
    """
    return db.engine.connect()



