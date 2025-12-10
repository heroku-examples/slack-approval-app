# Setup Instructions

## Environment Variables

Create a `.env` file in the project root with the following variables:

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

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Set up database: `python scripts/setup_db.py`
3. Seed sample data: `python scripts/seed_data.py`
4. Run application: `python app.py`

See README.md for detailed instructions.



