# Apify Setup Guide

## 1. Install the Python SDK

```bash
pip3 install apify-client
```

## 2. Get an Apify API Token

1. Go to [console.apify.com](https://console.apify.com/)
2. Sign up or log in
3. Navigate to **Settings** > **Integrations** > **API Tokens**
4. Create a new token and copy it

## 3. Set the Environment Variable

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
export APIFY_TOKEN="apify_api_YOUR_TOKEN_HERE"
```

Then reload: `source ~/.zshrc`

## 4. Pricing

Apify provides a **free tier with $5/month** in platform credits. The `trudax/reddit-scraper-lite` actor is lightweight -- a typical search costs only a few cents.
