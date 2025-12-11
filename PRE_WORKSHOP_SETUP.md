# Pre-Workshop Setup Guide

**⏱️ Time Savings: 20-30 minutes** - Complete these steps before the workshop to maximize hands-on coding time!

This guide will help you prepare your development environment before the workshop begins. Completing these steps ahead of time will allow you to focus on the exciting parts: building and deploying your application!

## Prerequisites Checklist

Before starting, ensure you have:

- ✅ A computer with internet access
- ✅ A GitHub account (free)
- ✅ A Heroku account - See [this article](https://basecamp.salesforce.com/content/techforce-heroku-for-sfdc-employees) on BaseCamp for Salesforce employees
- ✅ A Slack account (we'll create a Sandbox workspace during the workshop)
- ✅ Basic familiarity with command line (help will be provided during the workshop)

## Account Setup (5 minutes)

### 1. Create/Verify Accounts

1. **GitHub Account**:
   - Create account at [github.com](https://github.com) if you don't have one
   - Verify you can log in and access your account

2. **Heroku Account**:
   - Create account at [heroku.com](https://heroku.com) if you don't have one
   - **Salesforce Employees**: Use your Salesforce employee account (see [BaseCamp article](https://basecamp.salesforce.com/content/techforce-heroku-for-sfdc-employees))
   - Verify you can access [dashboard.heroku.com](https://dashboard.heroku.com)

3. **Slack Account**:
   - Create account at [slack.com](https://slack.com) if you don't have one
   - You'll create a Sandbox workspace during the workshop, but having an account ready helps

## Software Installation (10 minutes)

### 2. Install Git

**Verify if already installed**:
```bash
git --version
```

If not installed, download and install:

- **Windows**: Download from [git-scm.com/downloads](https://git-scm.com/downloads)
- **Mac**: 
  - Using Homebrew: `brew install git`
  - Or download from [git-scm.com/downloads](https://git-scm.com/downloads)
- **Linux**: 
  - Ubuntu/Debian: `sudo apt-get install git`
  - Or use your distribution's package manager

**Verify installation**:
```bash
git --version
# Should display something like: git version 2.40.0
```

### 3. Install Heroku CLI

**Verify if already installed**:
```bash
heroku --version
```

If not installed, download and install:

- **All Platforms**: Download from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
- **Mac (Homebrew)**: 
  ```bash
  brew tap heroku/brew && brew install heroku
  ```
- **Windows**: Download the installer from the link above

**Verify installation**:
```bash
heroku --version
# Should display something like: heroku/8.0.0
```

### 4. Install Python 3.11+

**Verify if already installed**:
```bash
python3 --version
```

If not installed or version is below 3.11, download and install:

- **All Platforms**: Download from [python.org/downloads](https://www.python.org/downloads/)
- **Mac (Homebrew)**: 
  ```bash
  brew install python@3.11
  ```
- **Linux**: 
  - Ubuntu/Debian: `sudo apt-get install python3.11`
  - Or use your distribution's package manager

**Verify installation**:
```bash
python3 --version
# Should display: Python 3.11.x or higher
```

## Heroku Setup (5 minutes)

### 5. Log In to Heroku CLI

1. **Log In**:
   ```bash
   heroku login
   ```
   - This will open a browser window for authentication
   - Click **"Log in"** in the browser
   - Return to the terminal

2. **Verify Login**:
   ```bash
   heroku auth:whoami
   ```
   - Should display your Heroku email address
   - If it shows an error, try logging in again

3. **Verify Heroku Account Access**:
   - Go to [dashboard.heroku.com](https://dashboard.heroku.com) in your browser
   - Ensure you can access your account
   - **Salesforce Employees**: Verify access via the BaseCamp article if needed

## Repository Setup

> **📋 Note**: Repository cloning will be done **during the workshop**. This ensures all attendees follow along together and receive guidance from the facilitator. You don't need to clone the repository before the workshop starts.

**What you need before the workshop:**
- Git installed and verified (see Software Installation above)
- GitHub account created (see Account Setup above)
- Heroku account

**During the workshop, you will:**
- Receive the repository URL from your facilitator
- Clone the repository together as a group
- Follow step-by-step instructions in the workshop guide

## Optional: Slack Sandbox Workspace (5 minutes)

> **Note**: This is optional and can be done during the workshop. However, doing it beforehand saves time.

### 6. Create Slack Sandbox Workspace (Optional)

1. **Go to Slack Developer Program**:
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
   - You'll use this workspace during the workshop

## Final Verification Checklist

Before the workshop starts, run through this checklist to verify everything is set up:

### Software Verification

```bash
# Check all installations
git --version          # Should show version number (e.g., git version 2.40.0)
heroku --version       # Should show version number (e.g., heroku/8.0.0)
python3 --version      # Should show 3.11.x or higher
```

### Heroku Verification

```bash
# Verify Heroku login
heroku auth:whoami     # Should show your email address
```

### Git Verification

```bash
# Verify Git is installed and configured
git --version          # Should show version number
git config --global user.name   # Should show your name (optional but recommended)
git config --global user.email  # Should show your email (optional but recommended)
```

### Account Verification

- [ ] GitHub account created and accessible
- [ ] Heroku account created and accessible at [dashboard.heroku.com](https://dashboard.heroku.com)
- [ ] Slack account created (optional, but helpful)
- [ ] Git installed and verified

## Troubleshooting

### Git Installation Issues

**Windows**:
- If `git` command not found after installation, restart your terminal
- Make sure Git was added to your PATH during installation

**Mac**:
- If using Homebrew and getting errors, try: `brew update && brew install git`

**Linux**:
- If permission denied, use `sudo` for installation commands

### Heroku CLI Installation Issues

**Mac**:
- If Homebrew installation fails, try downloading the installer from the Heroku website

**Windows**:
- Make sure to run the installer as Administrator if needed
- Restart terminal after installation

**All Platforms**:
- If `heroku login` doesn't open a browser, try: `heroku login -i` for interactive login

### Python Installation Issues

**Version Check**:
- Make sure you're checking `python3 --version`, not `python --version`
- Some systems have both Python 2 and 3 installed

**Mac**:
- If Homebrew installation fails, download from python.org
- Make sure to check "Add Python to PATH" during installation

**Linux**:
- You may need to install `python3-pip` separately: `sudo apt-get install python3-pip`

### Heroku Login Issues

- If `heroku login` fails, try: `heroku login -i` for interactive login
- Make sure your Heroku account is active
- Check your internet connection

### Repository Clone Issues

- Make sure you have the correct repository URL from your facilitator
- Verify you have access to the repository (if it's private)
- Check your internet connection
- If you get "permission denied", make sure you're authenticated with GitHub

## What's Next?

Once you've completed all the steps above and verified everything works:

✅ **You're ready for the workshop!**

**Important**: The repository will be cloned **during the workshop** so everyone follows along together with facilitator guidance. This ensures:
- All attendees receive step-by-step instructions at the same time
- The facilitator can provide real-time help and answer questions
- Everyone stays synchronized through the deployment process

The workshop will cover:
- Cloning the repository (with facilitator guidance)
- Setting up your Slack app
- Configuring Slack integrations
- Deploying to Heroku
- Testing your application
- Exploring AI-powered future features

**⏱️ Workshop Time After Pre-Setup**: 40-60 minutes (reduced from 60-90 minutes)

## Need Help?

If you encounter issues during setup:

1. **Check the Troubleshooting section** above
2. **Contact your workshop facilitator** - they can help with setup issues
3. **Common Resources**:
   - [Git Documentation](https://git-scm.com/doc)
   - [Heroku CLI Documentation](https://devcenter.heroku.com/articles/heroku-cli)
   - [Python Documentation](https://docs.python.org/3/)

## Summary

By completing this pre-workshop setup, you'll:
- ✅ Save 20-30 minutes during the workshop
- ✅ Focus on the exciting parts: building and deploying
- ✅ Have a smoother workshop experience
- ✅ Be ready to dive right into coding
- ✅ Have all tools and accounts ready when the facilitator shares the repository

**Remember**: The repository will be cloned during the workshop so everyone follows along together with facilitator guidance.

See you at the workshop! 🚀

