# Echo: Sales Intelligence & CRM Skill

AI-powered sales intelligence system that transforms your email mailbox into a comprehensive CRM database.

## Features

- **Email Ingestion**: Continuously fetch emails from Gmail
- **Quote Extraction**: Automatically extract quotes from emails and PDFs
- **Company Intelligence**: Scrape company websites for business info
- **Sales Pipeline Analysis**: Understand your sales stages and outcomes
- **Pricing Intelligence**: Learn product pricing from historical quotes
- **Email Generation**: Generate personalized emails in your voice

## Setup

1. Place your `credentials.json` at `~/.echo_credentials/credentials.json`
2. Update `skill.yaml` with your Telegram bot token
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python echo_skill.py`

## Commands

- `/start` - Initialize Echo
- `/stats` - Show sales statistics
- `/customers` - List all customers
- `/hot_deals` - Show hot prospects
- `/draft <customer>` - Generate email draft
- `/help` - Show all commands

## Status

🟢 Active Development
