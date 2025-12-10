# Universal Approval Hub

A Proof of Concept (POC) application that demonstrates how Slack, integrated with Heroku, can act as a Universal Approval Hub, centralizing approval requests from various Systems of Record (e.g., Workday, Concur, Salesforce).

## Features

- **Slack Home Tab Dashboard**: Personalized approval dashboard for managers
- **Multi-Source Support**: Handles approval requests from Workday, Concur, and Salesforce
- **Semantic Search**: Natural language search using Heroku Managed Inference and pgvector
- **AI-Powered Analysis**: Automatic summarization and risk scoring using Claude
- **Real-Time Updates**: Instant UI updates when approvals are processed
- **Secure Webhooks**: Slack request verification and secure API endpoints

## Architecture

- **Backend**: Flask (Python 3.11)
- **Database**: Heroku Postgres (or Heroku Postgres Advanced) with pgvector extension
- **AI/ML**: Heroku Managed Inference (Cohere embeddings, Claude chat completions)
- **Deployment**: Heroku with Gunicorn
- **Integration**: Slack Events API, Interactive Components, Home Tab

> **Note**: This application is designed for Heroku deployment and uses Heroku Postgres. For production workloads requiring high performance and scale, consider [Heroku Postgres Advanced](https://www.heroku.com/blog/introducing-the-next-generation-of-heroku-postgres/), the next generation of Heroku Postgres with enhanced performance, scalability, and zero-friction operations.

## Prerequisites

- Python 3.11+
- Heroku account (for deployment)
- Heroku Postgres add-on (automatically configured via `DATABASE_URL`)
- Slack App with appropriate OAuth scopes
- Heroku Managed Inference add-on (optional, for AI features)

> **For Local Development Only**: PostgreSQL 12+ with pgvector extension (see Local Development Setup below)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd UniversalApprovalHub
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL with pgvector

#### Using Homebrew (macOS):

```bash
brew install postgresql@14
brew install pgvector
```

#### Using Docker:

```bash
docker run -d \
  --name approval-hub-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=approval_hub \
  -p 5432:5432 \
  pgvector/pgvector:pg14
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/approval_hub

# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_APP_ID=your-app-id

# Heroku Managed Inference (when add-on is provisioned)
HEROKU_MANAGED_INFERENCE_API_URL=https://api.heroku.com/managed-inference/v1
HEROKU_MANAGED_INFERENCE_API_KEY=your-api-key

# Logging
LOG_LEVEL=INFO
```

### 6. Initialize Database

```bash
python scripts/setup_db.py
```

### 7. Seed Sample Data

```bash
python scripts/seed_data.py
```

### 8. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Slack App Configuration

### Required OAuth Scopes

- `app_mentions:read`
- `channels:history`
- `chat:write`
- `commands`
- `users:read`
- `users:read.email`

### Event Subscriptions

Configure the following events:
- `app_home_opened`

### Interactive Components

Enable Interactive Components and set the Request URL to:
```
https://your-app.herokuapp.com/slack/interactive
```

### Slash Commands (Optional)

No slash commands are required for this POC.

## API Endpoints

### Health Check

```
GET /health
```

Returns application health status.

### Create Approval Request

```
POST /api/new-approval
Content-Type: application/json

{
  "request_source": "Workday|Concur|Salesforce",
  "requester_name": "John Doe",
  "approver_id": "U123456",
  "justification_text": "Request justification...",
  "metadata": {
    "date_range": "2024-01-01 to 2024-01-05",
    "amount": 500.00,
    ...
  }
}
```

### Slack Events

```
POST /slack/events
```

Handles Slack Events API callbacks.

### Slack Interactive Components

```
POST /slack/interactive
```

Handles button clicks and other interactive components.

### Slack Home Tab

```
POST /slack/home
```

Returns Home Tab view for a user.

## Database Schema

### approval_requests

| Field | Type | Description |
|-------|------|-------------|
| id | SERIAL | Primary key |
| request_source | VARCHAR(50) | Source system (Workday, Concur, Salesforce) |
| requester_name | VARCHAR(100) | Employee name |
| approver_id | VARCHAR(50) | Slack User ID of approver |
| status | VARCHAR(20) | Pending, Approved, Rejected |
| justification_text | TEXT | Request justification |
| metadata_json | JSONB | Source-specific metadata |
| search_vector | VECTOR(1024) | Embedding vector for semantic search |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=. --cov-report=html
```

## Deployment to Heroku

This application is designed to run on Heroku with Heroku Postgres. The `DATABASE_URL` environment variable is automatically set when you attach a Postgres add-on to your Heroku app.

### 1. Create Heroku App

```bash
heroku create your-app-name
```

### 2. Add Heroku Postgres Add-on

For standard workloads:
```bash
heroku addons:create heroku-postgresql:mini
```

For high-performance, scalable workloads, consider **Heroku Postgres Advanced** (pilot program):
- Sign up for the [Heroku Postgres Advanced pilot](https://www.heroku.com/blog/introducing-the-next-generation-of-heroku-postgres/)
- Provides 4X+ throughput, 200TB+ storage, and zero-downtime scaling
- Once available, provision via Heroku dashboard or CLI

> **Note**: Heroku Postgres Advanced will eventually replace Standard, Premium, Private, and Shield tiers. The application automatically detects and uses the `DATABASE_URL` provided by any Heroku Postgres add-on.

### 3. Add Heroku Managed Inference (Optional)

```bash
heroku addons:create heroku-managed-inference:starter
```

### 4. Set Environment Variables

```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set SLACK_BOT_TOKEN=xoxb-your-token
heroku config:set SLACK_SIGNING_SECRET=your-signing-secret
heroku config:set SLACK_APP_ID=your-app-id
```

> **Note**: `DATABASE_URL` is automatically set by Heroku when you attach a Postgres add-on. You do not need to set it manually.

### 5. Deploy

```bash
git push heroku main
```

### 6. Initialize Database

The application will automatically:
- Enable the pgvector extension
- Create all required tables
- Set up the database schema

You can also manually run the setup script:
```bash
heroku run python scripts/setup_db.py
```

### 7. Seed Data (Optional)

```bash
heroku run python scripts/seed_data.py
```

### 8. Verify Deployment

Check that your app is running:
```bash
heroku open
```

View logs:
```bash
heroku logs --tail
```

## Project Structure

```
UniversalApprovalHub/
├── app.py                 # Main Flask application
├── config.py             # Configuration classes
├── database.py            # Database initialization
├── models.py              # SQLAlchemy models
├── requirements.txt       # Python dependencies
├── Procfile              # Heroku process definition
├── .python-version       # Python version specification
├── routes/
│   ├── __init__.py
│   ├── api_routes.py     # External API endpoints
│   └── slack_routes.py   # Slack integration routes
├── utils/
│   ├── __init__.py
│   ├── logging_config.py # Logging setup
│   ├── heroku_inference.py # AI/ML integration
│   ├── semantic_search.py # Vector search utilities
│   └── slack_utils.py    # Slack helper functions
├── migrations/
│   └── 001_initial_schema.sql # Database schema
├── scripts/
│   ├── setup_db.py       # Database setup script
│   └── seed_data.py      # Sample data seeding
└── tests/
    ├── conftest.py       # Pytest fixtures
    ├── test_api_routes.py
    ├── test_slack_routes.py
    └── test_models.py
```

## Environment Variables Reference

| Variable | Description | Required | Set By |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Flask secret key | Yes | Manual |
| `DATABASE_URL` | PostgreSQL connection string | Yes | **Heroku (auto)** |
| `SLACK_BOT_TOKEN` | Slack Bot User OAuth Token | Yes | Manual |
| `SLACK_SIGNING_SECRET` | Slack Signing Secret | Yes | Manual |
| `SLACK_APP_ID` | Slack App ID | Yes | Manual |
| `HEROKU_MANAGED_INFERENCE_API_URL` | Managed Inference API URL | No | **Heroku (auto)** |
| `HEROKU_MANAGED_INFERENCE_API_KEY` | Managed Inference API Key | No | **Heroku (auto)** |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No | Manual |

> **Important**: `DATABASE_URL` is automatically configured by Heroku when you attach a Postgres add-on. The application handles both `postgres://` and `postgresql://` connection strings and configures SSL automatically for Heroku Postgres.

## Troubleshooting

### Database Connection Issues

**On Heroku:**
- Verify Postgres add-on is attached: `heroku addons`
- Check `DATABASE_URL` is set: `heroku config:get DATABASE_URL`
- The application automatically enables pgvector extension on first run
- View database logs: `heroku logs --ps postgres`

**Local Development:**
- Ensure PostgreSQL is running locally
- Verify `DATABASE_URL` in `.env` file is correct
- Check that pgvector extension is installed: `CREATE EXTENSION vector;`

### Slack Integration Issues

- Verify all OAuth scopes are granted
- Check that Event Subscriptions URL is correct
- Ensure signing secret matches Slack app configuration

### Heroku Managed Inference

- Verify add-on is provisioned: `heroku addons`
- Check environment variables are set: `heroku config`
- Review logs: `heroku logs --tail`

## Contributing

1. Follow PEP 8 style guidelines
2. Include docstrings for all functions and classes
3. Write tests for new features
4. Update documentation as needed

## License

[Specify your license here]

## Support

For issues and questions, please [create an issue](link-to-issues) or contact the development team.



