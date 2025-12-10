"""Application configuration module.

This module defines the configuration classes for different environments
(development, staging, production) and loads settings from environment variables.
"""

import os
from typing import Optional


class Config:
    """Base configuration class.

    Contains common configuration settings used across all environments.
    """

    # Flask configuration
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG: bool = os.environ.get('FLASK_ENV') == 'development'

    # Database configuration
    # Heroku provides DATABASE_URL automatically when Postgres add-on is attached
    # Convert postgres:// to postgresql:// for SQLAlchemy 2.0+ compatibility
    _database_url = os.environ.get('DATABASE_URL')
    
    # On Heroku, DATABASE_URL should be set automatically
    # For local development, default to localhost
    if not _database_url:
        # Check if we're on Heroku (DYNO env var is set)
        if os.environ.get('DYNO'):
            # On Heroku without DATABASE_URL - this is an error
            raise ValueError(
                'DATABASE_URL is not set on Heroku. '
                'Attach a Postgres add-on: heroku addons:create heroku-postgresql:mini'
            )
        else:
            # Local development - use default
            _database_url = 'postgresql://localhost/approval_hub'
    
    if _database_url.startswith('postgres://'):
        _database_url = _database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI: str = _database_url
    
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    
    # Optimized for Heroku Postgres with connection pooling and SSL
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'connect_args': {
            'sslmode': 'require' if os.environ.get('DATABASE_URL') else 'prefer',
            'connect_timeout': 10
        }
    }

    # Slack configuration
    SLACK_BOT_TOKEN: Optional[str] = os.environ.get('SLACK_BOT_TOKEN')
    SLACK_SIGNING_SECRET: Optional[str] = os.environ.get('SLACK_SIGNING_SECRET')
    SLACK_APP_ID: Optional[str] = os.environ.get('SLACK_APP_ID')

    # Heroku Managed Inference configuration
    HEROKU_MANAGED_INFERENCE_API_URL: Optional[str] = os.environ.get(
        'HEROKU_MANAGED_INFERENCE_API_URL'
    )
    HEROKU_MANAGED_INFERENCE_API_KEY: Optional[str] = os.environ.get(
        'HEROKU_MANAGED_INFERENCE_API_KEY'
    )

    # Logging configuration
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')

    # Vector embedding dimension (Cohere embed-english-v3.0 uses 1024)
    VECTOR_DIMENSION: int = 1024


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG: bool = True
    LOG_LEVEL: str = 'DEBUG'


class ProductionConfig(Config):
    """Production environment configuration for Heroku deployment."""

    DEBUG: bool = False
    LOG_LEVEL: str = 'INFO'

    @property
    def SQLALCHEMY_ENGINE_OPTIONS(self) -> dict:
        """Production database engine options optimized for Heroku Postgres.

        Configures SSL requirement, connection pooling, and timeout settings
        suitable for Heroku Postgres and Heroku Postgres Advanced.

        :return: Database engine options dictionary
        :rtype: dict
        """
        options = super().SQLALCHEMY_ENGINE_OPTIONS.copy()
        # Heroku Postgres requires SSL connections
        options['connect_args']['sslmode'] = 'require'
        # Optimize pool settings for production workloads
        options['pool_size'] = 20
        options['max_overflow'] = 40
        return options



