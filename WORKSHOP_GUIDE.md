# Universal Approval Hub - Zero to Hero(ku) Workshop Guide

Welcome to the Universal Approval Hub workshop! This comprehensive guide will take you from zero to a fully deployed application on Heroku with Slack integration. Follow along step-by-step to build your own approval hub.

## Workshop Overview

**Duration**: 
- **With Pre-Workshop Setup**: 40-60 minutes (hands-on coding and deployment)
- **Without Pre-Workshop Setup**: 60-90 minutes (includes installation and setup)

**Goal**: Deploy a fully functional approval hub that integrates Slack with Heroku, demonstrating AI-powered approval workflows

> **💡 Pro Tip**: Complete the **Pre-Workshop Setup** section below before the workshop to save 20-30 minutes and focus on the fun parts!

**What You'll Build**:
- A Flask application deployed on Heroku
- Slack app with Home Tab interface
- PostgreSQL database with pgvector for semantic search
- AI-powered features using Heroku Managed Inference
- Web interface for creating and viewing approval requests

> **Note**: This is a demonstration application. The Workday, Concur, and Salesforce integrations are **mocked** - requests are created through a web form that simulates webhooks from these systems. In a production implementation, the app would connect to the actual Workday, Concur, and Salesforce APIs to receive real approval requests.

## Prerequisites

Before starting, ensure you have:

- ✅ A computer with internet access
- ✅ A GitHub account (free)
- ✅ A Heroku account - See [this article](https://basecamp.salesforce.com/content/techforce-heroku-for-sfdc-employees) on BaseCamp
- ✅ A Slack account (we'll create a Sandbox workspace)
- ✅ Git installed on your computer
- ✅ Heroku CLI installed ([download here](https://devcenter.heroku.com/articles/heroku-cli))
- ✅ Basic familiarity with command line (help will be provided)

## Pre-Workshop Setup

> **📋 Important**: Please complete the **[PRE_WORKSHOP_SETUP.md](PRE_WORKSHOP_SETUP.md)** guide before the workshop!

**⏱️ Time Savings: 20-30 minutes** - Completing the pre-workshop setup will allow you to focus on the exciting parts: building and deploying your application!

The pre-workshop setup guide covers:
- Account creation and verification (GitHub, Heroku, Slack)
- Software installation (Git, Heroku CLI, Python)
- Heroku CLI login and verification
- Repository cloning
- Optional Slack Sandbox workspace creation
- Complete verification checklist

**After completing the pre-workshop setup, the workshop will take 40-60 minutes** (instead of 60-90 minutes).

If you haven't completed the pre-workshop setup, don't worry! The workshop will include time for these steps, but you'll have less time for hands-on coding and exploration.

## Part 1: Set Up Slack Sandbox Workspace (10 minutes)

> **⏭️ Skip if you completed Pre-Workshop Setup**: If you already created a Slack Sandbox workspace, skip to Step 2.

### Step 1: Create a Slack Sandbox Workspace (if not done already)

1. **Go to Slack Developer Portal**:
   - Visit [the Slack Developer Program](https://api.slack.com/developer-program)
   - Click **"Get Started"** or **"Sign In"**

2. **Create a Sandbox Workspace**:
   - If you don't have a workspace, Slack will prompt you to create one
   - Click **"Create a Slack Workspace"**
   - Follow the prompts to create your workspace
   - **Workspace name suggestion**: "Approval Hub Workshop" or "Demo Workspace"

3. **Verify Your Workspace**:
   - You should see your workspace in Slack
   - Note your workspace URL (e.g., `your-workspace.slack.com`)

### Step 2: Create a Slack App

1. **Navigate to Slack Apps**:
   - Go to [api.slack.com/apps](https://api.slack.com/apps)
   - Click **"Create New App"**

2. **Create App from Scratch**:
   - Select **"From scratch"**
   - **App Name**: `Universal Approval Hub` (or `Sample Approval App`)
   - **Pick a workspace**: Select your Sandbox workspace
   - Click **"Create App"**

3. **Note Your App Credentials**:
   - You'll be taken to the app's Basic Information page
   - Keep this page open - you'll need information from here later

## Part 2: Configure Slack App (20 minutes)

### Step 3: Enable Home Tab

1. **Open App Home Settings**:
   - In the left sidebar, click **"App Home"** (under **Features**)

2. **Enable Home Tab**:
   - Under **"Home Tab"**, toggle the switch to **ON**
   - Under **"Show Tabs"**, ensure **"Home Tab"** is checked
   - **Important**: Set Home Tab to **"Publishable"** (not "Read-only")
   - Click **"Save Changes"**

### Step 4: Configure OAuth & Permissions

1. **Open OAuth & Permissions**:
   - Click **"OAuth & Permissions"** in the left sidebar (under **Features**)

2. **Add Bot Token Scopes**:
   - Scroll down to **"Scopes"** → **"Bot Token Scopes"**
   - Click **"Add New Scope"** and add each of these:
     - `chat:write` - Required for publishing Home Tab views and sending messages
     - `users:read` - Required for reading user information
     - `users:read.email` - Optional, for reading user emails

3. **Install App to Workspace**:
   - Scroll to the top of the page
   - Click **"Install to Workspace"**
   - Review the permissions and click **"Allow"**

4. **Copy Bot Token**:
   - After installation, you'll see **"Bot User OAuth Token"** at the top
   - **Copy this token** (starts with `xoxb-`) - you'll need it later
   - Save it somewhere safe (we'll add it to Heroku)

### Step 5: Get Signing Secret

1. **Open Basic Information**:
   - Click **"Basic Information"** in the left sidebar

2. **Copy Signing Secret**:
   - Scroll down to **"App Credentials"**
   - Under **"Signing Secret"**, click **"Show"**
   - **Copy the secret** - you'll need it later
   - Save it somewhere safe

### Step 6: Configure Event Subscriptions

1. **Open Event Subscriptions**:
   - Click **"Event Subscriptions"** in the left sidebar (under **Features**)

2. **Enable Events**:
   - Toggle **"Enable Events"** to **ON**

3. **Set Request URL** (We'll come back to this):
   - For now, leave this blank
   - We'll set it after deploying to Heroku
   - The URL will be: `https://your-app.herokuapp.com/slack/events`

4. **Subscribe to Bot Events**:
   - Scroll down to **"Subscribe to bot events"**
   - Click **"Add Bot User Event"**
   - Add: `app_home_opened`
   - Click **"Save Changes"**

### Step 7: Configure Interactive Components

1. **Open Interactivity**:
   - Click **"Interactivity"** in the left sidebar (under **Features**)

2. **Enable Interactivity**:
   - Toggle **"Interactivity"** to **ON**

3. **Set Request URL** (We'll come back to this):
   - For now, leave this blank
   - We'll set it after deploying to Heroku
   - The URL will be: `https://your-app.herokuapp.com/slack/interactive`

4. **Save Changes**:
   - Click **"Save Changes"**

> **Note**: We'll complete the Request URLs after deploying to Heroku. Keep the Slack app configuration page open.

## Part 3: Set Up Local Development Environment (5 minutes)

> **⏭️ Skip if you completed Pre-Workshop Setup**: If you already installed Git, Heroku CLI, Python, and cloned the repository, you can skip to Part 4.

### Step 8: Verify Prerequisites

1. **Verify Git Installation**:
   ```bash
   git --version
   ```
   - If not installed, download from [git-scm.com](https://git-scm.com/downloads)

2. **Verify Heroku CLI Installation**:
   ```bash
   heroku --version
   ```
   - If not installed, download from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)

3. **Verify Python Installation**:
   ```bash
   python3 --version
   ```
   - Should show 3.11 or higher
   - If not installed, download from [python.org](https://www.python.org/downloads/)

### Step 9: Clone the Repository (if not done already)

1. **Get the Repository URL**:
   - Ask your facilitator for the GitHub repository URL
   - Or use: `https://github.com/your-org/UniversalApprovalHub.git`

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-org/UniversalApprovalHub.git
   cd UniversalApprovalHub
   ```

3. **Verify Files**:
   ```bash
   ls -la
   ```
   You should see files like `app.py`, `requirements.txt`, `Procfile`, etc.

## Part 4: Deploy to Heroku (15 minutes)

> **⏭️ Skip if you completed Pre-Workshop Setup**: If you already logged in to Heroku CLI, skip Step 10.

### Step 10: Log In to Heroku (if not done already)

1. **Log In via CLI**:
   ```bash
   heroku login
   ```
   - This will open a browser window
   - Click **"Log in"** in the browser
   - Return to the terminal

2. **Verify Login**:
   ```bash
   heroku auth:whoami
   ```
   - Should display your Heroku email

### Step 11: Create Heroku App

1. **Create App**:
   ```bash
   heroku create your-app-name
   ```
   - Replace `your-app-name` with your desired name (must be unique)
   - Example: `heroku create approval-hub-workshop-2025-username`
   - Note the app URL (e.g., `https://your-app-name.herokuapp.com`)

2. **Verify App Created**:
   ```bash
   heroku apps:info
   ```

### Step 12: Add Heroku Postgres

1. **Add Postgres Add-on**:
   ```bash
   heroku addons:create heroku-postgresql:essential-0 --app your-app-name
   ```
   - Replace `your-app-name` with your actual app name
   - This automatically sets `DATABASE_URL` environment variable

2. **Verify Database**:
   ```bash
   heroku addons --app your-app-name
   ```
   - You should see `heroku-postgresql:essential-0` listed

### Step 13: Add Heroku Managed Inference (Optional but Recommended)

1. **Add Managed Inference Add-on**:
   ```bash
   heroku addons:create heroku-managed-inference:starter --app your-app-name
   ```
   - This enables AI features (semantic search, summaries, risk scoring)
   - The app works without it, but AI features will be disabled

2. **Get API Credentials**:
   ```bash
   heroku config --app your-app-name | grep INFERENCE
   ```
   - Note the `HEROKU_MANAGED_INFERENCE_API_URL` and `HEROKU_MANAGED_INFERENCE_API_KEY`
   - These are automatically set by the add-on

### Step 14: Set Environment Variables

1. **Set Slack Configuration**:
   ```bash
   heroku config:set SLACK_BOT_TOKEN=xoxb-your-token-here --app your-app-name
   heroku config:set SLACK_SIGNING_SECRET=your-signing-secret-here --app your-app-name
   ```
   - Replace with the values you copied from Slack earlier

2. **Set Secret Key**:
   ```bash
   heroku config:set SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))') --app your-app-name
   ```

3. **Verify All Config Vars**:
   ```bash
   heroku config --app your-app-name
   ```
   - You should see:
     - `DATABASE_URL` (automatically set)
     - `SLACK_BOT_TOKEN`
     - `SLACK_SIGNING_SECRET`
     - `SECRET_KEY`
     - `HEROKU_MANAGED_INFERENCE_API_URL` (if add-on added)
     - `HEROKU_MANAGED_INFERENCE_API_KEY` (if add-on added)

### Step 15: Deploy to Heroku

1. **Deploy Application**:
   ```bash
   git push heroku main
   ```
   - Or if your default branch is `master`: `git push heroku master`
   - This will build and deploy your application

2. **Watch the Build**:
   - You'll see build output in the terminal
   - Wait for "Build succeeded" message

3. **Verify Deployment**:
   ```bash
   heroku open --app your-app-name
   ```
   - Should open your app in the browser
   - You should see the landing page

4. **Check Health**:
   ```bash
   curl https://your-app-name.herokuapp.com/health
   ```
   - Should return: `{"status":"healthy","service":"universal-approval-hub"}`

### Step 16: Complete Slack Configuration

Now that your app is deployed, complete the Slack configuration:

1. **Update Event Subscriptions URL**:
   - Go back to [api.slack.com/apps](https://api.slack.com/apps)
   - Select your app
   - Click **"Event Subscriptions"**
   - Set **Request URL** to: `https://your-app-name.herokuapp.com/slack/events`
   - Slack will verify the URL - you should see a green checkmark ✅
   - Click **"Save Changes"**

2. **Update Interactive Components URL**:
   - Click **"Interactivity"**
   - Set **Request URL** to: `https://your-app-name.herokuapp.com/slack/interactive`
   - Click **"Save Changes"**

## Part 5: Test the Application (10 minutes)

### Step 17: Test Slack Integration

1. **Open Slack**:
   - Go to your Sandbox workspace
   - In the left sidebar, find **"Universal Approval Hub"** under **Apps**
   - Click on the app name

2. **Verify Home Tab**:
   - You should see the Home Tab with "📋 Approval Requests"
   - It may be empty initially (no requests yet)

3. **Find Your Slack User ID**:
   - Click on your profile picture/name
   - Click **"More"** → **"Copy member ID"**
   - Save this ID (starts with `U`) - you'll need it to create test requests

### Step 18: Create Test Request via Web Interface

1. **Open Web Interface**:
   - Go to: `https://your-app-name.herokuapp.com/create-request`

2. **Fill Out the Form**:
   - **Request Source**: Select "Workday"
   - **Requester Name**: Enter your name
   - **Approver Slack User ID**: Paste your Slack User ID (from Step 17)
   - **Justification**: Enter "Test PTO request for workshop"
   - **Metadata**: Click "Fill Sample Data" to auto-fill, or enter manually
     - Date Range: `2024-02-15 to 2024-02-22`

3. **Create Request**:
   - Click **"Create Request"**
   - You'll be redirected to the Status Dashboard
   - The request should appear with "Pending" status

4. **Check Slack**:
   - Go back to Slack
   - Open the Universal Approval Hub app Home Tab
   - You should see your request!

### Step 19: Test Approval Flow

1. **Approve in Slack**:
   - In the Slack Home Tab, find your test request
   - Click **"✅ Approve"** button
   - The request should disappear from the pending list
   - You'll receive a confirmation DM

2. **Check Status Dashboard**:
   - Go to: `https://your-app-name.herokuapp.com/status`
   - You should see the request status changed to "Approved"
   - The dashboard auto-refreshes every 10 seconds

3. **Create More Test Requests**:
   - Create requests from different sources (Concur, Salesforce)
   - Test filtering and semantic search
   - Try rejecting a request

## Part 6: Explore Features (15 minutes)

### Step 20: Explore the Web Interface

1. **Landing Page** (`/`):
   - Overview of the application
   - Links to create requests and view dashboard

2. **Create Request** (`/create-request`):
   - Try creating different types of requests
   - Use "Fill Sample Data" for quick testing
   - Notice how metadata fields change based on source

3. **Status Dashboard** (`/status`):
   - View all requests and their statuses
   - Try filtering by status, source, or approver
   - Watch real-time updates

### Step 21: Explore Slack Features

1. **Home Tab**:
   - Filter by source (Workday, Concur, Salesforce)
   - Try semantic search (if Managed Inference is configured)
   - Approve/reject requests

2. **Real-Time Updates**:
   - Create a request in the web interface
   - Watch it appear in Slack Home Tab
   - Approve it in Slack
   - Watch it update in the Status Dashboard

### Step 22: Test AI Features (If Managed Inference Added)

1. **Semantic Search**:
   - In Slack Home Tab, use the semantic search field
   - Try queries like:
     - "vacation requests"
     - "high-value expenses"
     - "urgent deals"

2. **AI Summaries**:
   - Create requests with different justifications
   - Check the AI-generated summaries in the request cards
   - Notice risk scores for Salesforce deals

## Troubleshooting

### App Won't Deploy

**Check build logs**:
```bash
heroku logs --tail --app your-app-name
```

**Common issues**:
- Missing `requirements.txt` or `Procfile`
- Python version mismatch (check `runtime.txt`)
- Build timeout (try again)

### Slack Home Tab Not Showing

1. **Verify Home Tab is enabled**:
   - Go to Slack app settings → App Home
   - Ensure Home Tab is ON and Publishable

2. **Check Heroku logs**:
   ```bash
   heroku logs --tail --app your-app-name
   ```
   - Look for errors about `SLACK_BOT_TOKEN` or signature verification

3. **Verify environment variables**:
   ```bash
   heroku config --app your-app-name
   ```

### Database Errors

1. **Check database connection**:
   ```bash
   heroku pg:info --app your-app-name
   ```

2. **Verify DATABASE_URL is set**:
   ```bash
   heroku config:get DATABASE_URL --app your-app-name
   ```

3. **Check logs for database errors**:
   ```bash
   heroku logs --tail --app your-app-name | grep -i database
   ```

### Web Interface Not Loading

1. **Check app status**:
   ```bash
   heroku ps --app your-app-name
   ```

2. **Restart the app**:
   ```bash
   heroku restart --app your-app-name
   ```

3. **Check logs**:
   ```bash
   heroku logs --tail --app your-app-name
   ```

## Workshop Checklist

Use this checklist to track your progress:

### Slack Setup
- [ ] Created Slack Sandbox workspace
- [ ] Created Slack app
- [ ] Enabled Home Tab (Publishable)
- [ ] Added Bot Token Scopes (`chat:write`, `users:read`)
- [ ] Installed app to workspace
- [ ] Copied Bot Token (`xoxb-...`)
- [ ] Copied Signing Secret
- [ ] Configured Event Subscriptions (URL set after deployment)
- [ ] Configured Interactive Components (URL set after deployment)

### Local Setup
- [ ] Installed Git
- [ ] Installed Heroku CLI
- [ ] Installed Python 3.11+
- [ ] Cloned repository
- [ ] Verified files are present

### Heroku Deployment
- [ ] Logged in to Heroku
- [ ] Created Heroku app
- [ ] Added Heroku Postgres add-on
- [ ] Added Heroku Managed Inference add-on (optional)
- [ ] Set SLACK_BOT_TOKEN
- [ ] Set SLACK_SIGNING_SECRET
- [ ] Set SECRET_KEY
- [ ] Deployed application
- [ ] Verified deployment (health check passes)

### Slack Configuration (Post-Deployment)
- [ ] Set Event Subscriptions Request URL
- [ ] Verified Event Subscriptions URL (green checkmark)
- [ ] Set Interactive Components Request URL
- [ ] Saved all changes

### Testing
- [ ] Opened Slack Home Tab
- [ ] Found Slack User ID
- [ ] Created test request via web interface
- [ ] Verified request appears in Slack
- [ ] Approved/rejected a request in Slack
- [ ] Verified status updates in dashboard
- [ ] Tested filtering and search features

## Next Steps

After completing the workshop:

1. **Explore the Code**:
   - Review `app.py` to understand the Flask application
   - Check `routes/` to see API and Slack endpoints
   - Look at `models.py` to understand the data structure

2. **Customize**:
   - Modify request types
   - Add new metadata fields
   - Customize the UI colors and branding

3. **Extend**:
   - Review `EXTENDING.md` to learn how to integrate with real services
   - Add webhook handlers for Workday, Concur, or Salesforce
   - Implement additional features

4. **Share**:
   - Share your app URL with others
   - Demonstrate the approval flow
   - Discuss use cases and improvements

## Resources

- **Slack API Documentation**: [api.slack.com](https://api.slack.com)
- **Heroku Documentation**: [devcenter.heroku.com](https://devcenter.heroku.com)
- **Flask Documentation**: [flask.palletsprojects.com](https://flask.palletsprojects.com)
- **Project README**: See `README.md` for detailed documentation
- **Architecture Guide**: See `ARCHITECTURE.md` for technical details

## Workshop Summary

Congratulations! You've successfully:

✅ Set up a Slack Sandbox workspace  
✅ Created and configured a Slack app  
✅ Deployed a Flask application to Heroku  
✅ Connected PostgreSQL database  
✅ Integrated Slack with your application  
✅ Tested the complete approval workflow  

You now have a fully functional approval hub that demonstrates:
- Multi-source approval centralization
- AI-powered features (semantic search, summaries, risk scoring)
- Real-time updates between Slack and web interface
- Modern web UI with Bootstrap
- Production-ready deployment on Heroku

## Questions and Discussion

Take time to discuss:

1. **Architecture**: How does the application work? What are the key components?
2. **AI Features**: How do embeddings and semantic search work?
3. **Integration**: How would you extend this to real Workday/Concur/Salesforce?
4. **Use Cases**: Where could this pattern be applied in your organization?
5. **Improvements**: What features would make this more useful?

Enjoy your new approval hub! 🎉
