# Twitter Agent Skill

Async tooling for Twitter/X automations that rely on cookie-based auth (`auth_token` + `ct0`). This packages the client wrappers and helper scripts we use in GanClaw’s social stack so other agents don’t have to rebuild the plumbing.

## Features
- `twitter_api/` package (aiohttp) with modules for tweets, users, relationships, timeline service, etc.
- Helper scripts under `scripts/`:
  - `timeline_summary.py` – fetch the home timeline and summarize top authors/topics.
  - `fetch_notifications.py` – pull notifications and store them as JSON.
  - `analyze_signal.py` – combine timeline + notifications into a markdown signal report.
  - `post_custom_tweet.py` – publish a tweet from any configured account.
  - `follow_account.py` – make every configured account follow a given handle.
- Auth is session-based (same cookies your browser uses) so there’s no dependency on official API keys.

## Requirements
- Python 3.10+
- `pip install -r requirements.txt`
- `.env` file with session cookies for each account you want to automate.

### Environment variables
Copy `.env.example` to `.env` and fill the cookies for each account you care about. Example:
```
ACCOUNT_A_AUTH_TOKEN=auth_token_here
ACCOUNT_A_CT0=ct0_here
ACCOUNT_B_AUTH_TOKEN=
ACCOUNT_B_CT0=
...
```
You can rename the env keys—just update `ACCOUNT_ENV` in the helper scripts so the labels match the keys you choose.

## Usage
```
git clone https://github.com/GAN12003/twitter-agent-skill.git
cd twitter-agent-skill
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env  # fill in your auth_token + ct0 values

# timeline + notification summaries
python scripts/timeline_summary.py
python scripts/fetch_notifications.py
python scripts/analyze_signal.py

# posting / following (pass one of the logical account labels)
python scripts/post_custom_tweet.py account_a "hello from the telemetry deck"
python scripts/follow_account.py thenfter07
```
All scripts load the `.env` in the repo root. Remove accounts you don’t need.

## Notes
- `auth_token`/`ct0` come from a logged-in X session; export them carefully and keep the `.env` private.
- Respect Twitter/X ToS—don’t spam, and avoid aggressive automation.
- This toolkit was born out of the PixelAgents/Sentinel work, but nothing inside is project-specific; rename labels or extend the scripts as you see fit.

## License
MIT
