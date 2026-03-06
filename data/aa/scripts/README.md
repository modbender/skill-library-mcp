# Scripts and rules (optional)

The client can add:

- **Custom templates** – Add entries to `templates/reply_templates.json` or provide their own JSON file path.
- **Rules** – e.g. "never auto-reply to emails containing X" or "always use template Y for sender Z." The agent should read these from the user's config or environment, not from this package.
- **Gmail API / IMAP** – Credentials and send logic must be provided by the user (env vars or secure config). This skill only defines behavior (draft content, tone, templates); it does not store credentials.

No executable scripts are required for the skill to work; the agent follows SKILL.md and uses the templates as reference.
