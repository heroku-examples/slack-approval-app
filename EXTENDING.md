# Extending the Universal Approval Hub

This document explains how to extend the Universal Approval Hub to integrate with real external systems (Workday, Concur, Salesforce) instead of using mocked requests.

## Current Implementation

Currently, the application accepts approval requests through:
- **Web Form** (`/create-request`) - For testing and workshops
- **REST API** (`POST /api/new-approval`) - Accepts requests with a `request_source` field

The `request_source` field can be "Workday", "Concur", or "Salesforce", but the application does not actually connect to these services. It simply accepts requests that claim to be from these sources.

## Extending to Real Integrations

To integrate with actual Workday, Concur, or Salesforce systems, you would need to:

### 1. Add Service-Specific Webhook Handlers

Create dedicated endpoints for each service that handle their specific webhook formats:

```python
# routes/webhook_routes.py

@webhook_bp.route('/webhooks/workday', methods=['POST'])
def workday_webhook():
    """Handle Workday webhook for PTO requests."""
    # Verify Workday webhook signature
    # Parse Workday-specific payload format
    # Map to ApprovalRequest model
    # Call existing create_approval_request() function
    pass

@webhook_bp.route('/webhooks/concur', methods=['POST'])
def concur_webhook():
    """Handle Concur webhook for expense requests."""
    # Verify Concur webhook signature
    # Parse Concur-specific payload format
    # Map to ApprovalRequest model
    # Call existing create_approval_request() function
    pass

@webhook_bp.route('/webhooks/salesforce', methods=['POST'])
def salesforce_webhook():
    """Handle Salesforce webhook for deal approval requests."""
    # Verify Salesforce webhook signature
    # Parse Salesforce-specific payload format
    # Map to ApprovalRequest model
    # Call existing create_approval_request() function
    pass
```

### 2. Implement Service Authentication

Each service will have its own authentication mechanism:

- **Workday**: OAuth 2.0, API keys, or webhook signatures
- **Concur**: OAuth 2.0 with client credentials flow
- **Salesforce**: OAuth 2.0 with JWT bearer token flow

### 3. Map Service-Specific Data Formats

Each service has its own data structure. You'll need to map them to the unified `ApprovalRequest` model:

```python
def map_workday_to_approval_request(workday_payload):
    """Map Workday PTO request to ApprovalRequest."""
    return {
        'request_source': 'Workday',
        'requester_name': workday_payload['employee']['name'],
        'approver_id': get_slack_user_id(workday_payload['manager']['email']),
        'justification_text': workday_payload['time_off_request']['reason'],
        'metadata': {
            'date_range': f"{workday_payload['start_date']} to {workday_payload['end_date']}",
            'days_requested': workday_payload['days'],
            'workday_request_id': workday_payload['id']
        }
    }
```

### 4. Handle Service-Specific Features

Each service may have unique features:

- **Workday**: May need to handle approval chains, delegation, calendar integration
- **Concur**: May need to handle receipt attachments, expense categories, policy validation
- **Salesforce**: May need to handle opportunity stages, approval processes, territory rules

### 5. Implement Error Handling and Retries

Real integrations need robust error handling:

```python
def handle_webhook_with_retry(webhook_handler, max_retries=3):
    """Handle webhook with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            return webhook_handler()
        except ServiceUnavailableError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
```

### 6. Add Status Callbacks

After approval/rejection in Slack, you may need to notify the source system:

```python
def notify_workday_approval(request_id, status):
    """Notify Workday of approval decision."""
    approval_request = ApprovalRequest.query.get(request_id)
    workday_api.update_request_status(
        approval_request.metadata_json['workday_request_id'],
        status
    )
```

## Example: Workday Integration

Here's a more complete example for Workday:

```python
import requests
from flask import Blueprint, request, jsonify
from hmac import compare_digest
import hashlib

workday_bp = Blueprint('workday', __name__)

@workday_bp.route('/webhooks/workday', methods=['POST'])
def workday_webhook():
    """Handle Workday webhook for PTO requests."""
    
    # 1. Verify webhook signature
    signature = request.headers.get('X-Workday-Signature')
    if not verify_workday_signature(request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # 2. Parse Workday payload
    payload = request.get_json()
    
    # 3. Map to ApprovalRequest
    approval_data = {
        'request_source': 'Workday',
        'requester_name': payload['employee']['fullName'],
        'approver_id': get_slack_user_id_from_email(payload['manager']['email']),
        'justification_text': payload['timeOffRequest']['reason'],
        'metadata': {
            'date_range': f"{payload['startDate']} to {payload['endDate']}",
            'days_requested': payload['days'],
            'workday_request_id': payload['id'],
            'employee_id': payload['employee']['id']
        }
    }
    
    # 4. Create approval request using existing function
    from routes.api_routes import create_approval_request
    result = create_approval_request(approval_data)
    
    return jsonify(result), 201

def verify_workday_signature(payload, signature):
    """Verify Workday webhook signature."""
    secret = current_app.config.get('WORKDAY_WEBHOOK_SECRET')
    expected = hashlib.sha256(payload + secret.encode()).hexdigest()
    return compare_digest(signature, expected)
```

## Configuration

Add service-specific configuration:

```python
# config.py

class Config:
    # Workday
    WORKDAY_API_URL = os.environ.get('WORKDAY_API_URL')
    WORKDAY_CLIENT_ID = os.environ.get('WORKDAY_CLIENT_ID')
    WORKDAY_CLIENT_SECRET = os.environ.get('WORKDAY_CLIENT_SECRET')
    WORKDAY_WEBHOOK_SECRET = os.environ.get('WORKDAY_WEBHOOK_SECRET')
    
    # Concur
    CONCUR_API_URL = os.environ.get('CONCUR_API_URL')
    CONCUR_CLIENT_ID = os.environ.get('CONCUR_CLIENT_ID')
    CONCUR_CLIENT_SECRET = os.environ.get('CONCUR_CLIENT_SECRET')
    
    # Salesforce
    SALESFORCE_INSTANCE_URL = os.environ.get('SALESFORCE_INSTANCE_URL')
    SALESFORCE_CLIENT_ID = os.environ.get('SALESFORCE_CLIENT_ID')
    SALESFORCE_CLIENT_SECRET = os.environ.get('SALESFORCE_CLIENT_SECRET')
    SALESFORCE_USERNAME = os.environ.get('SALESFORCE_USERNAME')
    SALESFORCE_PASSWORD = os.environ.get('SALESFORCE_PASSWORD')
```

## Testing Real Integrations

1. **Use Service Sandboxes**: Most services provide sandbox/test environments
2. **Mock Services**: Use tools like WireMock or MockServer to simulate services
3. **Integration Tests**: Create test suites that verify webhook handling
4. **Webhook Testing Tools**: Use services like ngrok to test webhooks locally

## Security Considerations

When integrating with real services:

1. **Webhook Verification**: Always verify webhook signatures
2. **HTTPS Only**: Use HTTPS for all webhook endpoints
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Idempotency**: Handle duplicate webhooks gracefully
5. **Secrets Management**: Store API keys and secrets securely (use Heroku config vars)

## Next Steps

1. Review the service-specific API documentation:
   - [Workday API Documentation](https://doc.workday.com/)
   - [Concur API Documentation](https://developer.concur.com/)
   - [Salesforce API Documentation](https://developer.salesforce.com/docs/apis)

2. Set up service accounts and obtain API credentials

3. Implement webhook handlers following the patterns above

4. Test with service sandboxes before production deployment

5. Monitor and log all webhook activity for debugging

## Summary

The current application provides a solid foundation with:
- Unified data model (`ApprovalRequest`)
- Slack integration
- AI-powered features
- Web interface for testing

To extend to real integrations, you primarily need to:
- Add service-specific webhook handlers
- Implement authentication for each service
- Map service data formats to the unified model
- Add status callbacks to notify source systems

The existing architecture makes this extension straightforward - you're essentially adding translation layers between external services and the existing approval workflow.

