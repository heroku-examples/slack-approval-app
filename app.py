"""Main Flask application entry point.

This module initializes the Flask application, configures database connections,
sets up logging, and registers all blueprints.
"""

import os
import logging
from flask import Flask, render_template
from dotenv import load_dotenv
from flasgger import Swagger

from config import Config
from database import db, init_db
from routes import api_bp, slack_bp
from routes.web_routes import web_bp
from utils.logging_config import setup_logging

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Configure Swagger/OpenAPI documentation
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api-docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Universal Approval Hub API",
        "description": "REST API for the Universal Approval Hub - a centralized approval system that integrates with Slack. This API accepts approval requests from external systems (Workday, Concur, Salesforce) and manages the approval workflow.",
        "version": "1.0.0",
        "contact": {
            "name": "API Support",
            "email": "support@example.com"
        },
        "license": {
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
        }
    },
    "host": os.environ.get('SWAGGER_HOST', 'localhost:5000'),
    "basePath": "/",
    "schemes": ["http", "https"],
    "tags": [
        {
            "name": "Health",
            "description": "Health check endpoints"
        },
        {
            "name": "Approval Requests",
            "description": "Endpoints for managing approval requests"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

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
app.register_blueprint(web_bp)


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
    
    ---
    tags:
      - Health
    responses:
      200:
        description: Service is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            service:
              type: string
              example: universal-approval-hub
    """
    return {'status': 'healthy', 'service': 'universal-approval-hub'}, 200


@app.route('/')
def index() -> str:
    """Landing page with link to create test requests.

    :return: HTML response with landing page
    :rtype: str
    """
    return render_template('index.html')


@app.route('/create-request')
def create_request() -> str:
    """Page for creating test approval requests.

    :return: HTML response with request creation form
    :rtype: str
    """
    return render_template('create_request.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', False))

