# Supermemory Free Skill for OpenClaw

This skill acts as a cloud backup for knowledge using the Supermemory.ai free tier.

## Features
- **Cloud Storage:** Manually store specific knowledge strings to the cloud.
- **Cloud Search:** Retrieve knowledge when local memory is insufficient.
- **Auto-Capture:** Daily cron job that extracts high-value insights from OpenClaw session logs.

## Setup
1. Get a free API key from [Supermemory.ai](https://supermemory.ai).
2. Set the `SUPERMEMORY_OPENCLAW_API_KEY` in your `.env` file.
3. Run `bash install_cron.sh` to enable auto-capture.

## Tools
- `supermemory_cloud_store(content)`
- `supermemory_cloud_search(query)`
