# Universal Approval Hub - Workshop Attendee Guide

Welcome to the Universal Approval Hub workshop! This guide will walk you through how to use the application and what to expect.

## What is the Universal Approval Hub?

The Universal Approval Hub is a proof-of-concept application that centralizes approval requests from multiple enterprise systems (Workday, Concur, Salesforce) into a single Slack interface. It uses AI-powered features like semantic search and automatic summarization to help managers make faster, more informed decisions.

## Prerequisites

Before you begin, ensure you have:

- ✅ Access to the Slack workspace where the app is installed
- ✅ The Universal Approval Hub Slack app added to your workspace
- ✅ A Slack account with appropriate permissions (the app should appear in your Apps section)

## Getting Started

### Step 1: Open the Slack App Home Tab

1. Open Slack in your browser or desktop app
2. In the left sidebar, find **"Universal Approval Hub"** under **Apps** (or search for it)
3. Click on the app name to open it
4. You should see the **Home Tab** with the approval dashboard

**What you'll see:**
- A header saying "📋 Approval Requests"
- Filter controls to filter by source system (Workday, Concur, Salesforce)
- A semantic search input field
- Approval request cards (if any are pending)

### Step 2: Understanding the Interface

The Home Tab displays:

- **Filter by Source**: A dropdown to filter requests by system (All, Workday, Concur, Salesforce)
- **Semantic Search**: A text input where you can search using natural language (e.g., "vacation requests" or "high-value deals")
- **Approval Cards**: Each card shows:
  - Requester name
  - Request type and details (varies by source)
  - AI-generated summary (if available)
  - Justification text
  - Approve/Reject buttons

## Creating Test Requests

Before you can test the approval flow, you'll need to create some test approval requests. The easiest way is through the web interface:

1. **Open your browser** and go to:
   ```
   https://your-app.herokuapp.com/create-request
   ```
   (Ask your facilitator for the exact URL)

2. **Fill out the form:**
   - Select a request source (Workday, Concur, or Salesforce)
   - Enter a requester name
   - Enter your Slack User ID (to find it: click your profile → More → Copy member ID)
   - Add justification text
   - Optionally click "Fill Sample Data" to auto-fill example data

3. **Click "Create Request"** - the request will appear in your Slack Home Tab!

You can create multiple requests to test different scenarios. Each request type (Workday, Concur, Salesforce) displays different information in the approval cards.

## Trying Out the Application

### Scenario 1: Viewing Approval Requests

1. **Open the Home Tab** (as described in Step 1)
2. If there are pending requests, you'll see them as cards
3. Each card shows different information based on the source:
   - **Workday**: PTO requests with date ranges
   - **Concur**: Expense requests with amounts and PDF links
   - **Salesforce**: Deal requests with customer names, deal values, and risk scores

**What to look for:**
- Request details are clearly displayed
- AI summaries provide quick context
- Risk scores help identify high-priority items

### Scenario 2: Filtering Requests

1. In the Home Tab, find the **"Filter by Source"** dropdown
2. Select a specific source (e.g., "Workday")
3. The list will update to show only requests from that source
4. Select "All" to see all requests again

**Expected behavior:**
- The list updates immediately
- Only requests matching the selected source are shown

### Scenario 3: Semantic Search

1. In the Home Tab, find the **"Semantic Search"** input field
2. Type a natural language query, such as:
   - "vacation requests"
   - "high-value expenses"
   - "urgent deals"
   - "requests from last month"
3. The list will update to show matching requests based on semantic similarity

**What to expect:**
- The search uses AI to understand the meaning of your query
- Results are ranked by relevance, not just keyword matching
- You can search for concepts, not just exact words

**Note:** Semantic search requires the Heroku Managed Inference add-on to be configured. If it's not available, the search may not work, but the rest of the app will function normally.

### Scenario 4: Approving a Request

1. Find an approval request card in the Home Tab
2. Review the request details, AI summary, and justification
3. Click the **"✅ Approve"** button (green button)
4. The request will be marked as approved
5. The Home Tab will refresh automatically
6. You'll receive a confirmation message in Slack

**What happens:**
- The request status changes to "Approved" in the database
- The request disappears from the pending list
- A confirmation message appears in your Slack DMs

### Scenario 5: Rejecting a Request

1. Find an approval request card
2. Review the request details
3. Click the **"❌ Reject"** button (red button)
4. The request will be marked as rejected
5. The Home Tab will refresh automatically
6. You'll receive a confirmation message

**What happens:**
- The request status changes to "Rejected" in the database
- The request disappears from the pending list
- A confirmation message appears in your Slack DMs

## Understanding Request Types

### Workday Requests (PTO)

**What you'll see:**
- Requester name
- Date range for the PTO request
- AI summary of the request
- Justification text

**Example:**
```
John Doe requested PTO
📅 Date Range: 2024-01-15 to 2024-01-19
Summary: Employee requesting 5 days of vacation for personal time
Justification: Need to take time off for family event
```

### Concur Requests (Expenses)

**What you'll see:**
- Requester name
- Expense amount
- Link to PDF receipt (if available)
- AI summary
- Justification text

**Example:**
```
Jane Smith submitted expense
💰 Amount: $1,250.00
📄 View PDF
Summary: Business travel expense for client meeting
Justification: Travel and accommodation for Q1 planning meeting
```

### Salesforce Requests (Deals)

**What you'll see:**
- Requester name
- Customer name
- Deal value
- Risk score (0-10)
- AI summary
- Justification text

**Example:**
```
Bob Johnson submitted deal
👤 Customer: Acme Corporation
💵 Deal Value: $50,000.00
⚠️ Risk Score: 3/10
Summary: Standard enterprise deal with established customer
Justification: Renewal contract with existing client, low risk
```

## Troubleshooting

### I don't see the app in Slack

**Solution:**
- Check if the app has been installed in your workspace
- Ask your workshop facilitator to verify the app installation
- Try searching for "Universal Approval Hub" in Slack

### The Home Tab is empty

**Possible reasons:**
- There are no pending approval requests assigned to you
- The app may need sample data to be created
- Ask your facilitator to create a test request

**Solution:**
- Ask your facilitator to submit a test approval request via the API
- Check if you're logged in as the correct user (requests are assigned by Slack User ID)

### Semantic search isn't working

**Possible reasons:**
- Heroku Managed Inference add-on may not be configured
- The search feature requires the add-on to generate embeddings

**Solution:**
- The app will still work without semantic search
- You can still filter by source and approve/reject requests
- Ask your facilitator if the add-on is configured

### Buttons don't respond

**Possible reasons:**
- Network connectivity issues
- The app may be experiencing errors

**Solution:**
- Refresh the Home Tab
- Check the browser console for errors (if using web Slack)
- Ask your facilitator to check the application logs

### I see an error message

**What to do:**
- Note the error message text
- Try refreshing the Home Tab
- If the error persists, inform your facilitator
- Common errors:
  - "Invalid signature" - Slack verification issue (contact facilitator)
  - "Request not found" - Request may have been deleted
  - "Unauthorized" - You're not the assigned approver for this request

## What to Expect During the Workshop

### Initial Setup (5 minutes)

- Facilitator will ensure the app is installed
- Sample data may be created
- You'll be guided to open the Home Tab

### Exploration Phase (10-15 minutes)

- Try opening the Home Tab
- Explore the interface
- Review any sample approval requests
- Try filtering by source

### Interactive Phase (10-15 minutes)

- Try semantic search (if available)
- Approve or reject a test request
- Observe the real-time updates
- Check your Slack DMs for confirmation messages

### Discussion Phase (10 minutes)

- Share your experience with the group
- Discuss the AI features (semantic search, summaries, risk scores)
- Provide feedback on the user experience

## Key Features to Explore

1. **Multi-Source Integration**: See how requests from different systems appear in one place
2. **AI Summarization**: Notice how AI provides quick context for each request
3. **Risk Scoring**: Understand how risk scores help prioritize decisions
4. **Semantic Search**: Experience natural language search capabilities
5. **Real-Time Updates**: See how the interface updates immediately after actions
6. **Slack Integration**: Experience how Slack becomes a unified approval interface

## Tips for Best Experience

- **Use semantic search creatively**: Try different phrasings to see how AI understands your intent
- **Compare request types**: Notice how different sources (Workday, Concur, Salesforce) display different information
- **Check AI summaries**: Read the AI-generated summaries to see how they help you understand requests quickly
- **Look at risk scores**: For Salesforce deals, use risk scores to identify high-priority items
- **Test real-time updates**: Approve or reject a request and watch the Home Tab update automatically

## Questions to Consider

As you explore the application, think about:

1. **User Experience**: How intuitive is the interface? What would make it better?
2. **AI Features**: How useful are the AI summaries and risk scores? Do they help you make decisions faster?
3. **Semantic Search**: How well does natural language search work? Can you find what you're looking for?
4. **Integration**: How valuable is having all approvals in one place vs. checking multiple systems?
5. **Real-World Application**: How would this work in your organization? What challenges might you face?

## Next Steps

After the workshop, you can:

- **Provide Feedback**: Share your thoughts with the facilitator
- **Explore Further**: Ask questions about the architecture and implementation
- **Consider Use Cases**: Think about how this could apply to your organization
- **Review Documentation**: Check the ARCHITECTURE.md document for technical details

## Support

If you encounter any issues during the workshop:

1. **Check this guide** for troubleshooting steps
2. **Ask your facilitator** for assistance
3. **Check the application logs** (if you have access)
4. **Review the README.md** for technical setup information

## Summary

The Universal Approval Hub demonstrates how modern AI and integration technologies can transform enterprise workflows. By centralizing approvals in Slack and using AI to provide context, managers can make faster, more informed decisions while staying in their primary communication tool.

Enjoy exploring the application, and don't hesitate to ask questions!

