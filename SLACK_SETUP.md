# Slack App Configuration Guide

This guide provides step-by-step instructions for configuring your Slack app to enable the Home Tab interface.

## Prerequisites

- A Slack workspace where you have admin permissions (or app management permissions)
- Your Heroku app URL (e.g., `https://your-app.herokuapp.com`)
- Access to [api.slack.com/apps](https://api.slack.com/apps)

## Step-by-Step Configuration

### 1. Create or Select Your Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click **"Create New App"** or select your existing app
3. If creating new, choose **"From scratch"**
4. Enter app name: **"Universal Approval Hub"** (or "Sample Approval App")
5. Select your workspace
6. Click **"Create App"**

### 2. Enable Home Tab Feature

**This is the critical step that's likely missing!**

1. In your app's settings, click **"App Home"** in the left sidebar (under **Features**)
2. Under **"Home Tab"**, ensure the toggle is **ON** (enabled)
3. Under **"Show Tabs"**, make sure **"Home Tab"** is checked
4. **Important**: The Home Tab should be set to **"Publishable"** (not "Read-only")
   - This allows your app to publish views using `views.publish()`
5. Scroll down and click **"Save Changes"**

### 3. Configure Event Subscriptions

1. Click **"Event Subscriptions"** in the left sidebar (under **Features**)
2. Toggle **"Enable Events"** to **ON**
3. Set the **Request URL** to:
   ```
   https://your-app.herokuapp.com/slack/events
   ```
   Replace `your-app` with your actual Heroku app name
4. Slack will verify the URL - you should see a green checkmark ✅
5. Scroll down to **"Subscribe to bot events"**
6. Click **"Add Bot User Event"**
7. Add the following event:
   - `app_home_opened` - This triggers when a user opens the Home Tab
8. Click **"Save Changes"**

### 4. Configure Interactive Components

1. Click **"Interactivity"** in the left sidebar (under **Features**)
2. Toggle **"Interactivity"** to **ON**
3. Set the **Request URL** to:
   ```
   https://your-app.herokuapp.com/slack/interactive
   ```
4. Click **"Save Changes"**

### 5. Configure OAuth & Permissions

1. Click **"OAuth & Permissions"** in the left sidebar (under **Features**)
2. Scroll down to **"Scopes"** → **"Bot Token Scopes"**
3. Add the following scopes (click **"Add New Scope"** for each):
   - `chat:write` - Required for publishing Home Tab views and sending messages
   - `users:read` - Required for reading user information
   - `users:read.email` - Optional, for reading user emails
4. Scroll to the top and click **"Install to Workspace"** (or **"Reinstall to Workspace"** if already installed)
5. Review permissions and click **"Allow"**
6. **Copy the Bot User OAuth Token** (starts with `xoxb-`)
7. Set this as `SLACK_BOT_TOKEN` in your Heroku config vars:
   ```bash
   heroku config:set SLACK_BOT_TOKEN=xoxb-your-token-here --app your-app-name
   ```

### 6. Get Your Signing Secret

1. Click **"Basic Information"** in the left sidebar
2. Scroll down to **"App Credentials"**
3. Under **"Signing Secret"**, click **"Show"** and copy the secret
4. Set this as `SLACK_SIGNING_SECRET` in your Heroku config vars:
   ```bash
   heroku config:set SLACK_SIGNING_SECRET=your-signing-secret-here --app your-app-name
   ```

### 7. Verify Environment Variables

Ensure all required environment variables are set in Heroku:

```bash
heroku config --app your-app-name
```

You should see:
- `SLACK_BOT_TOKEN` (starts with `xoxb-`)
- `SLACK_SIGNING_SECRET` (a long string)
- `DATABASE_URL` (automatically set by Heroku Postgres)

### 8. Test the Home Tab

1. Open Slack in your browser or desktop app
2. In the left sidebar, find your app under **"Apps"** (or search for it)
3. Click on the app name
4. You should see the **Home Tab** with the approval dashboard

**If you still don't see the interface:**

1. **Check Heroku logs** for errors:
   ```bash
   heroku logs --tail --app your-app-name
   ```
   Look for:
   - Errors about `SLACK_BOT_TOKEN` not configured
   - Errors about signature verification
   - Errors about publishing Home Tab

2. **Verify the event is firing:**
   - Open the Home Tab in Slack
   - Check Heroku logs - you should see a log entry about `app_home_opened` event
   - You should see: `"Published home tab for user U..."`

3. **Manually trigger Home Tab publish:**
   - You can test by opening the Home Tab again
   - The `app_home_opened` event should trigger and publish the view

## Troubleshooting

### Home Tab is empty or shows "No pending approval requests"

This is normal if there are no approval requests in the database. To test:

1. Create a test approval request via the API:
   ```bash
   curl -X POST https://your-app.herokuapp.com/api/new-approval \
     -H "Content-Type: application/json" \
     -d '{
       "request_source": "Workday",
       "requester_name": "Test User",
       "approver_id": "YOUR_SLACK_USER_ID",
       "justification_text": "Test PTO request",
       "metadata": {
         "date_range": "2024-01-15 to 2024-01-19"
       }
     }'
   ```
   Replace `YOUR_SLACK_USER_ID` with your actual Slack User ID (starts with `U`)

2. To find your Slack User ID:
   - Go to your Slack profile
   - Click "More" → "Copy member ID"
   - Or use the Slack API: `https://api.slack.com/methods/users.identity`

3. After creating the request, refresh the Home Tab in Slack

### "Invalid signature" errors

- Verify `SLACK_SIGNING_SECRET` is set correctly in Heroku
- Ensure the signing secret matches what's in your Slack app settings
- Check that your Heroku app URL is accessible (not behind a firewall)

### "SLACK_BOT_TOKEN not configured" warnings

- Verify `SLACK_BOT_TOKEN` is set in Heroku config vars
- Ensure the token starts with `xoxb-`
- Make sure you reinstalled the app after adding scopes

### Home Tab doesn't update when opening

- Check that `app_home_opened` event is subscribed in Event Subscriptions
- Verify the Events API Request URL is correct and verified
- Check Heroku logs for errors when opening the Home Tab

### Buttons don't work

- Verify Interactive Components are enabled
- Check that the Interactive Components Request URL is correct
- Ensure `SLACK_SIGNING_SECRET` is configured correctly

## Quick Checklist

Before testing, verify:

- [ ] Home Tab feature is enabled in "App Home" settings
- [ ] Home Tab is set to "Publishable" (not read-only)
- [ ] Event Subscriptions enabled with `app_home_opened` event
- [ ] Events API Request URL is verified (green checkmark)
- [ ] Interactive Components enabled with Request URL set
- [ ] Bot Token Scopes include `chat:write` and `users:read`
- [ ] App is installed/reinstalled to workspace after adding scopes
- [ ] `SLACK_BOT_TOKEN` is set in Heroku config vars
- [ ] `SLACK_SIGNING_SECRET` is set in Heroku config vars
- [ ] Heroku app is running and accessible

## Additional Resources

- [Slack App Home Documentation](https://api.slack.com/surfaces/tabs/using)
- [Slack Events API Documentation](https://api.slack.com/events-api)
- [Slack Interactive Components Documentation](https://api.slack.com/interactivity)

## Need Help?

If you're still experiencing issues:

1. Check the Heroku logs for specific error messages
2. Verify all configuration steps above
3. Test the endpoints directly:
   - Health check: `GET https://your-app.herokuapp.com/health`
   - Events endpoint: Check if it responds to Slack verification challenges

The most common issue is that the **Home Tab feature is not enabled** in the "App Home" settings. Make sure to enable it and set it to "Publishable"!

