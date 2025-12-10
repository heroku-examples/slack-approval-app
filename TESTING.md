# Testing Guide - Mocking Approval Requests

This guide shows you how to create test approval requests to try out the approval flow without connecting to external systems (Workday, Concur, Salesforce).

## Quick Start

### Option 1: Web Interface (Recommended for Workshops/Demos) 🌟

**The easiest way to create test requests is through the web interface!**

1. **Open your browser** and navigate to:
   ```
   https://your-app.herokuapp.com/create-request
   ```
   Or locally:
   ```
   http://localhost:5000/create-request
   ```

2. **Fill out the form:**
   - Select request source (Workday, Concur, or Salesforce)
   - Enter requester name
   - Enter your Slack User ID (as approver)
   - Add justification text
   - Fill in metadata (optional, fields appear based on source)

3. **Click "Fill Sample Data"** to auto-fill example data, or enter your own

4. **Click "Create Request"** - the request will appear in your Slack Home Tab!
5. **You'll be automatically redirected to the Status Dashboard** where you can see all requests and their statuses

This is perfect for workshops and demos - no command line needed!

**Status Dashboard:**
After creating a request, you'll be redirected to `/status` where you can:
- View all requests (pending, approved, rejected)
- See statistics and counts
- Filter by status, source, or approver
- Watch real-time updates (auto-refreshes every 10 seconds)

### Option 2: Create Sample Requests (Script)

Run the script to create a set of sample requests:

**On Heroku:**
```bash
heroku run python scripts/create_test_request.py --samples --approver-id YOUR_SLACK_USER_ID --app your-app-name
```

**Locally:**
```bash
export SLACK_TEST_APPROVER_ID=YOUR_SLACK_USER_ID
python scripts/create_test_request.py --samples
```

Replace `YOUR_SLACK_USER_ID` with your actual Slack User ID (starts with `U`).

### Option 2: Use the API Endpoint

You can create requests directly via the API using `curl` or any HTTP client:

```bash
curl -X POST https://your-app.herokuapp.com/api/new-approval \
  -H "Content-Type: application/json" \
  -d '{
    "request_source": "Workday",
    "requester_name": "John Doe",
    "approver_id": "YOUR_SLACK_USER_ID",
    "justification_text": "I need to take time off for a family vacation.",
    "metadata": {
      "date_range": "2024-02-15 to 2024-02-22",
      "days_requested": 5
    }
  }'
```

## Finding Your Slack User ID

To find your Slack User ID:

1. **In Slack Desktop/Web:**
   - Click on your profile picture/name
   - Click **"More"** → **"Copy member ID"**
   - The ID starts with `U` (e.g., `U01234ABCD`)

2. **Using Slack API:**
   - Visit: `https://api.slack.com/methods/users.identity`
   - Or use: `https://slack.com/api/users.identity` with your token

## Creating Test Requests

### Using the Script

#### Create a Single Request

```bash
python scripts/create_test_request.py \
  --approver-id YOUR_SLACK_USER_ID \
  --source Workday \
  --requester "Alice Johnson" \
  --justification "I need time off for vacation" \
  --metadata '{"date_range": "2024-02-15 to 2024-02-22"}'
```

#### Create Sample Requests

```bash
python scripts/create_test_request.py \
  --samples \
  --approver-id YOUR_SLACK_USER_ID
```

### Using the API

#### Workday PTO Request

```bash
curl -X POST https://your-app.herokuapp.com/api/new-approval \
  -H "Content-Type: application/json" \
  -d '{
    "request_source": "Workday",
    "requester_name": "Alice Johnson",
    "approver_id": "YOUR_SLACK_USER_ID",
    "justification_text": "I need to take time off for a family vacation to Hawaii. We have been planning this trip for months.",
    "metadata": {
      "date_range": "2024-02-15 to 2024-02-22",
      "days_requested": 5,
      "remaining_pto": 10
    }
  }'
```

#### Concur Expense Request

```bash
curl -X POST https://your-app.herokuapp.com/api/new-approval \
  -H "Content-Type: application/json" \
  -d '{
    "request_source": "Concur",
    "requester_name": "Bob Smith",
    "approver_id": "YOUR_SLACK_USER_ID",
    "justification_text": "Business trip to San Francisco for client meeting. Expenses include flights, hotel, meals, and transportation.",
    "metadata": {
      "amount": 2450.75,
      "currency": "USD",
      "trip_dates": "2024-02-05 to 2024-02-07",
      "pdf_url": "https://example.com/receipts/expense_001.pdf",
      "category": "Travel"
    }
  }'
```

#### Salesforce Deal Request

```bash
curl -X POST https://your-app.herokuapp.com/api/new-approval \
  -H "Content-Type: application/json" \
  -d '{
    "request_source": "Salesforce",
    "requester_name": "Carol Williams",
    "approver_id": "YOUR_SLACK_USER_ID",
    "justification_text": "Large enterprise deal with TechCorp Inc. This is a strategic account with high revenue potential.",
    "metadata": {
      "customer_name": "TechCorp Inc.",
      "deal_value": 250000.00,
      "currency": "USD",
      "close_date": "2024-03-31",
      "stage": "Negotiation"
    }
  }'
```

## Request Types and Metadata

### Workday (PTO Requests)

**Required fields:**
- `request_source`: `"Workday"`
- `requester_name`: Employee name
- `approver_id`: Slack User ID
- `justification_text`: Reason for PTO

**Optional metadata:**
```json
{
  "date_range": "2024-02-15 to 2024-02-22",
  "days_requested": 5,
  "remaining_pto": 10
}
```

### Concur (Expense Requests)

**Required fields:**
- `request_source`: `"Concur"`
- `requester_name`: Employee name
- `approver_id`: Slack User ID
- `justification_text`: Expense justification

**Optional metadata:**
```json
{
  "amount": 2450.75,
  "currency": "USD",
  "trip_dates": "2024-02-05 to 2024-02-07",
  "pdf_url": "https://example.com/receipts/expense_001.pdf",
  "category": "Travel"
}
```

### Salesforce (Deal Requests)

**Required fields:**
- `request_source`: `"Salesforce"`
- `requester_name`: Employee name
- `approver_id`: Slack User ID
- `justification_text`: Deal justification

**Optional metadata:**
```json
{
  "customer_name": "TechCorp Inc.",
  "deal_value": 250000.00,
  "currency": "USD",
  "close_date": "2024-03-31",
  "stage": "Negotiation"
}
```

## Testing the Approval Flow

1. **Create a test request** using one of the methods above
2. **You'll be redirected to the Status Dashboard** - you can see the request with "Pending" status
3. **Open Slack** and navigate to the Universal Approval Hub app
4. **Open the Home Tab** - you should see your test request
5. **Click "✅ Approve" or "❌ Reject"** to test the approval flow
6. **Check your Slack DMs** for confirmation messages
7. **Return to the Status Dashboard** - you'll see the status update to "Approved" or "Rejected" (auto-refreshes every 10 seconds)

## Using the Seed Script

The `seed_data.py` script can also create multiple sample requests:

**On Heroku:**
```bash
heroku run python scripts/seed_data.py --app your-app-name
```

**Locally:**
```bash
export SLACK_TEST_APPROVER_ID=YOUR_SLACK_USER_ID
python scripts/seed_data.py
```

This creates:
- 2 Workday PTO requests
- 2 Concur expense requests
- 2 Salesforce deal requests

## Testing Semantic Search

After creating requests, you can test semantic search in the Home Tab:

1. Open the Home Tab in Slack
2. Use the "Semantic Search" input field
3. Try queries like:
   - "vacation requests"
   - "high-value expenses"
   - "urgent deals"
   - "business travel"

The search uses AI to understand the meaning of your query and find relevant requests.

## Troubleshooting

### Requests don't appear in Home Tab

- **Check approver_id**: Make sure you're using your actual Slack User ID
- **Refresh the Home Tab**: Close and reopen the app in Slack
- **Check Heroku logs**: Look for errors when creating requests
  ```bash
  heroku logs --tail --app your-app-name
  ```

### AI features not working

- **Heroku Managed Inference**: Ensure the add-on is provisioned
- **Check config vars**: Verify `HEROKU_MANAGED_INFERENCE_API_URL` and `HEROKU_MANAGED_INFERENCE_API_KEY` are set
- **App still works**: The app functions without AI, but summaries and semantic search won't work

### Script errors

- **Database connection**: Ensure `DATABASE_URL` is set (automatically set on Heroku)
- **Slack token**: Ensure `SLACK_BOT_TOKEN` is configured
- **Import errors**: Make sure you're running from the project root directory

## Example Workflow

Here's a complete example workflow:

```bash
# 1. Find your Slack User ID (see instructions above)
# Let's say it's U01234ABCD

# 2. Create sample requests on Heroku
heroku run python scripts/create_test_request.py \
  --samples \
  --approver-id U01234ABCD \
  --app your-app-name

# 3. Open Slack and check the Home Tab
# You should see 3 requests (Workday, Concur, Salesforce)

# 4. Test approving a request
# Click "✅ Approve" on one of the requests

# 5. Test rejecting a request
# Click "❌ Reject" on another request

# 6. Test semantic search
# Type "vacation" in the search box
```

## Next Steps

- Try creating requests with different metadata
- Test the filtering by source (Workday, Concur, Salesforce)
- Experiment with semantic search queries
- Review the approval flow in the Home Tab

For more information, see:
- [WORKSHOP_GUIDE.md](WORKSHOP_GUIDE.md) - User guide for workshop attendees
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture documentation
- [README.md](README.md) - Main project documentation

