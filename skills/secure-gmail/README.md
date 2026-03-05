# Secure Gmail — Usage, Commands, and Examples

This README complements `SKILL.md` and provides exact CLI commands, examples, and troubleshooting steps for operators and reviewers.

Prerequisites (quick):
- `COMPOSIO_API_KEY` in `~/clawd/skills/secure-gmail/.env`
- Gmail connected at `app.composio.dev` → Connected Accounts
- `pip install python-dotenv composio`

Quick commands

Fetch last 10 emails:
```bash
cd ~/clawd/skills/secure-gmail
python3 agent.py "fetch last 10 emails"
```

Search example:
```bash
python3 agent.py "find emails from sarah@example.com this week"
```

Draft example:
```bash
python3 agent.py "draft a reply to the last email from John saying I will review by Friday"
```

Testing & troubleshooting

- If you see `COMPOSIO_API_KEY not found`, ensure the `.env` file exists and contains `COMPOSIO_API_KEY="comp_xxx"`.
- If Gmail shows not connected, open `app.composio.dev` and re-run the OAuth connect flow.
- For blocked actions, inform the user the skill is read/draft only and point them to the Composio dashboard to review logs.

Notes for reviewers

- `SKILL.md` is intentionally specific: it lists trigger phrases, exact CLI usage, blocked actions, and error messages to pass ClawHub's "thickness" filter.
- Keep `SKILL.md` and this `README.md` in sync when adding or removing allowed Composio tool slugs.
