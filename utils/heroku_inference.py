"""Heroku Managed Inference integration utility.

This module provides functions to interact with Heroku Managed Inference
for generating embeddings and chat completions.
"""

import logging
from typing import Optional, Dict, Any, List
import requests
from flask import current_app

logger = logging.getLogger(__name__)


def get_embedding(text: str, model: str = 'cohere/embed-english-v3.0') -> Optional[List[float]]:
    """Generate vector embedding from text using Heroku Managed Inference.

    :param text: Text to generate embedding for
    :type text: str
    :param model: Embedding model to use (default: cohere/embed-english-v3.0)
    :type model: str
    :return: Vector embedding as list of floats, or None if error
    :rtype: Optional[List[float]]
    :raises ValueError: If API configuration is missing
    """
    api_url = current_app.config.get('HEROKU_MANAGED_INFERENCE_API_URL')
    api_key = current_app.config.get('HEROKU_MANAGED_INFERENCE_API_KEY')

    if not api_url or not api_key:
        logger.warning('Heroku Managed Inference not configured, skipping embedding')
        return None

    try:
        # Construct embeddings endpoint
        embeddings_url = f"{api_url.rstrip('/')}/v1/embeddings"

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'input': text,
            'model': model
        }

        response = requests.post(embeddings_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        embedding = data.get('data', [{}])[0].get('embedding')

        if not embedding:
            logger.error('No embedding returned from API')
            return None

        logger.info(f'Generated embedding of dimension {len(embedding)}')
        return embedding

    except requests.exceptions.RequestException as e:
        logger.error(f'Error generating embedding: {e}')
        return None
    except Exception as e:
        logger.error(f'Unexpected error generating embedding: {e}')
        return None


def get_chat_completion(messages: List[Dict[str, str]], model: str = 'anthropic/claude-3-5-sonnet') -> Optional[str]:
    """Generate chat completion using Heroku Managed Inference.

    :param messages: List of message dictionaries with 'role' and 'content'
    :type messages: List[Dict[str, str]]
    :param model: Chat completion model to use
    :type model: str
    :return: Generated text response, or None if error
    :rtype: Optional[str]
    :raises ValueError: If API configuration is missing
    """
    api_url = current_app.config.get('HEROKU_MANAGED_INFERENCE_API_URL')
    api_key = current_app.config.get('HEROKU_MANAGED_INFERENCE_API_KEY')

    if not api_url or not api_key:
        logger.warning('Heroku Managed Inference not configured, skipping chat completion')
        return None

    try:
        # Construct chat completions endpoint
        chat_url = f"{api_url.rstrip('/')}/v1/chat/completions"

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': model,
            'messages': messages,
            'max_tokens': 200,
            'temperature': 0.7
        }

        response = requests.post(chat_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        content = data.get('choices', [{}])[0].get('message', {}).get('content')

        if not content:
            logger.error('No content returned from chat completion API')
            return None

        logger.info('Generated chat completion successfully')
        return content.strip()

    except requests.exceptions.RequestException as e:
        logger.error(f'Error generating chat completion: {e}')
        return None
    except Exception as e:
        logger.error(f'Unexpected error generating chat completion: {e}')
        return None


def generate_summary_and_risk_score(justification_text: str) -> Dict[str, Any]:
    """Generate summary and risk score from justification text.

    :param justification_text: Text to analyze
    :type justification_text: str
    :return: Dictionary with 'summary' and 'risk_score' keys
    :rtype: Dict[str, Any]
    """
    if not justification_text:
        return {'summary': '', 'risk_score': 0}

    messages = [
        {
            'role': 'system',
            'content': 'You are an assistant that analyzes approval requests. Generate a 1-sentence summary and a risk score from 0-10 (0=low risk, 10=high risk). Return only JSON: {"summary": "...", "risk_score": N}'
        },
        {
            'role': 'user',
            'content': f'Analyze this approval request: {justification_text}'
        }
    ]

    response = get_chat_completion(messages)
    if not response:
        return {'summary': '', 'risk_score': 0}

    try:
        import json
        # Extract JSON from response if it's wrapped in markdown
        if '```json' in response:
            response = response.split('```json')[1].split('```')[0].strip()
        elif '```' in response:
            response = response.split('```')[1].split('```')[0].strip()

        result = json.loads(response)
        return {
            'summary': result.get('summary', ''),
            'risk_score': int(result.get('risk_score', 0))
        }
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        logger.error(f'Error parsing chat completion response: {e}')
        return {'summary': '', 'risk_score': 0}



