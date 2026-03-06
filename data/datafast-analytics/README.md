# DataFast Analytics OpenClaw Skill

Query DataFast website analytics and visitor data from OpenClaw. This skill wraps the DataFast API and summarizes results for common analytics questions (overview, time series, realtime, breakdowns, visitors, goals, and payments).

## Requirements

- OpenClaw installed
- A DataFast API key (get yours from [datafa.st](https://datafa.st))

## Installation

Clone or copy the skill into your OpenClaw workspace:

```bash
git clone https://github.com/bennyqp/datafast-analytics-openclaw-skill.git ~/.openclaw/workspace/skills/datafast-analytics
```

OpenClaw loads skills from `<workspace>/skills` with highest precedence.

## Configure API Key

Store your API key in a config file:

```bash
mkdir -p ~/.config/datafast
echo "df_your_api_key_here" > ~/.config/datafast/api_key
```

The skill reads the key from `~/.config/datafast/api_key` on each request.

## Usage

Ask OpenClaw analytics questions such as:

- "Show visitors and revenue for the last 30 days."
- "Visitors from X in the last 24 hours."
- "Realtime active visitors right now."
- "Top pages by visitors."
- "Create a custom goal for a visitor."

## What It Calls

Base URL: `https://datafa.st/api/v1/`

Common endpoints:

- `GET /analytics/overview`
- `GET /analytics/timeseries`
- `GET /analytics/realtime`
- `GET /analytics/realtime/map`
- `GET /analytics/devices`
- `GET /analytics/pages`
- `GET /analytics/campaigns`
- `GET /analytics/goals`
- `GET /analytics/referrers`
- `GET /analytics/countries`
- `GET /analytics/regions`
- `GET /analytics/cities`
- `GET /analytics/browsers`
- `GET /analytics/operating-systems`
- `GET /analytics/hostnames`
- `GET /visitors/{datafast_visitor_id}`
- `POST /goals`
- `DELETE /goals`
- `POST /payments`
- `DELETE /payments`

## Filters and Time Ranges

Use `startAt` and `endAt` together for time windows. For segmentation, use `filter_*` parameters supported by the DataFast API (example: `filter_referrer=is:x.com`). See the full API docs in `references/datafast-api-docs.md`.

## Security Notes

- Treat the API key as a secret. Do not paste it into chat prompts.
- The key is stored locally in `~/.config/datafast/api_key` and never leaves your machine.