"""Main Flask application entry point.

This module initializes the Flask application, configures database connections,
sets up logging, and registers all blueprints.
"""

import os
import logging
from flask import Flask
from dotenv import load_dotenv

from config import Config
from database import db, init_db
from routes import api_bp, slack_bp
from utils.logging_config import setup_logging

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Setup logging
setup_logging(app.config.get('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

# Initialize database (with error handling for Heroku)
try:
    init_db(app)
except Exception as e:
    logger.error(f'Database initialization failed: {e}')
    logger.warning(
        'Application will start but database features may not work. '
        'Ensure DATABASE_URL is set or attach a Heroku Postgres add-on.'
    )

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(slack_bp, url_prefix='/slack')


@app.errorhandler(404)
def not_found(error) -> tuple[dict, int]:
    """Handle 404 Not Found errors.

    :param error: Error object
    :type error: Exception
    :return: JSON error response and HTTP 404
    :rtype: tuple[dict, int]
    """
    return {'error': 'Not found'}, 404


@app.errorhandler(500)
def internal_error(error) -> tuple[dict, int]:
    """Handle 500 Internal Server errors.

    :param error: Error object
    :type error: Exception
    :return: JSON error response and HTTP 500
    :rtype: tuple[dict, int]
    """
    logger.error(f'Internal server error: {error}')
    return {'error': 'Internal server error'}, 500


@app.errorhandler(400)
def bad_request(error) -> tuple[dict, int]:
    """Handle 400 Bad Request errors.

    :param error: Error object
    :type error: Exception
    :return: JSON error response and HTTP 400
    :rtype: tuple[dict, int]
    """
    return {'error': 'Bad request'}, 400


@app.route('/health')
def health_check() -> tuple[dict, int]:
    """Health check endpoint for monitoring.

    :return: JSON response with status and HTTP 200
    :rtype: tuple[dict, int]
    """
    return {'status': 'healthy', 'service': 'universal-approval-hub'}, 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', False))

