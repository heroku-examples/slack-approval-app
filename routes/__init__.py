"""Routes package for API and Slack endpoints."""

from routes.api_routes import api_bp
from routes.slack_routes import slack_bp
from routes.web_routes import web_bp

__all__ = ['api_bp', 'slack_bp', 'web_bp']



