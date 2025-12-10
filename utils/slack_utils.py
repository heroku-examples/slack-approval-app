"""Slack utility functions.

This module provides helper functions for Slack API interactions.
"""

import logging
from typing import Dict, Any
from flask import current_app
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from routes.slack_routes import build_home_tab_view

logger = logging.getLogger(__name__)


def publish_home_tab(user_id: str) -> None:
    """Publish Home Tab view to Slack for a user.

    :param user_id: Slack User ID
    :type user_id: str
    :raises SlackApiError: If API call fails
    """
    bot_token = current_app.config.get('SLACK_BOT_TOKEN')
    if not bot_token:
        logger.warning('SLACK_BOT_TOKEN not configured')
        return

    client = WebClient(token=bot_token)

    try:
        view = build_home_tab_view(user_id)
        client.views_publish(user_id=user_id, view=view)
        logger.info(f'Published home tab for user {user_id}')
    except SlackApiError as e:
        logger.error(f'Error publishing home tab: {e}')
        raise

