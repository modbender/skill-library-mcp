---
name: github-chat-ops
description: Manage a single GitHub repository via chat for non-technical requesters—after they share the repo URL and a temporary personal token, pull status, summarize who did what and when, and create/follow up on issues directly through the GitHub API.
---

## Overview
Use this skill whenever a non-technical person (often over WhatsApp) needs lightweight GitHub help without cloning or forking a repo. Typical asks:
- "Tell me what changed recently and who did it."
- "Create an issue describing X."
- "Follow up on existing issues or PRs."
The workflow relies entirely on the GitHub REST API using a personal access token (PAT) the requester provides during the chat.

## 1. Gather prerequisites every session
1. **Repo identifier** – ask for full URL or `owner/name`.
2. **PAT** – confirm it has `repo` scope (private repos) or `public_repo` (public). Remind them to generate a short-lived token and send it in the chat; you’ll discard it afterward.
3. **Task brief** – what they need (issue, summary, follow-up) plus timeframe (e.g., "last 7 days").

_Always restate the inputs back to them before acting. If anything is missing, pause and ask._

## 2. Handle tokens safely
- Paste the token into a temporary shell variable in the current session only:
  ```bash
  export GITHUB_TOKEN="<token-from-chat>"
  ```
- Never save tokens to disk or log files. When finished, run `unset GITHUB_TOKEN`.
- Every API call must set `Authorization: Bearer $GITHUB_TOKEN` and `Accept: application/vnd.github+json`.

## 3. Fetch repo context before acting
1. **Health check**: `GET /repos/{owner}/{repo}` – confirms access and surfaces default branch.
2. **Recent commits** (for summaries / who-did-what):
   - `GET /repos/{owner}/{repo}/commits?since=<ISO8601>&until=<ISO8601>`
   - For per-author breakdown, add `author=<username>` or group results locally.
3. **Issues & PRs**: `GET /repos/{owner}/{repo}/issues?state=all&since=<ISO8601>`.
   - Distinguish PRs via `pull_request` key.

Record the raw JSON responses (e.g., save to `/tmp/commits.json`) if you need to run jq filters before summarizing.

## 4. Deep repo inspection without cloning
When you need file-level context (to quote code in an issue or explain why a commit matters), walk the tree via the REST API:
1. **List directories/files**: `GET /repos/{owner}/{repo}/contents/<path>?ref=<branch>` returns metadata plus download URLs.
2. **Fetch raw blobs**: reuse the `download_url` or call `GET /repos/{owner}/{repo}/contents/<path>` with header `Accept: application/vnd.github.raw`.
3. **Large trees**: `GET /repos/{owner}/{repo}/git/trees/<sha>?recursive=1` to grab the whole structure, then request the files you care about.
4. Cache what you read per session (e.g., store under `/tmp/github-chat-ops/<repo>/...`) so subsequent lookups avoid extra API calls.
Always mention the file + path + relevant snippet when writing summaries or issues.

## 5. Summaries for non-technical readers (with real changes)
Translate activity into plain language:
- Group commits by contributor, then describe what actually changed (features/tests/configs) rather than just commit titles.
- For each commit, hit `GET /repos/{owner}/{repo}/commits/{sha}` to see `files[]` (filenames, additions/removals, patch).
- Extract the top 1–2 bullets per contributor: e.g., "Updated `quiz_generator.py` to support context prompts and added 3 YAML fixtures."
- Mention timestamps in the user’s timezone (Africa/Lagos unless told otherwise).
- Highlight status (merged, open, blocked) and outstanding follow-ups.
Keep summaries short, bullet-style, and avoid jargon.

## 6. Creating or updating issues
1. Clarify the problem, expected outcome, priority, and owners while chatting.
2. Draft the issue body locally in Markdown (include background, repro steps, acceptance criteria).
3. Create the issue via `POST /repos/{owner}/{repo}/issues` with JSON payload:
   ```json
   {
     "title": "...",
     "body": "...",
     "assignees": ["username"],
     "labels": ["priority:high"]
   }
   ```
4. Echo the created issue URL back to the user and summarize what was filed.

_For follow-ups_, use `PATCH /repos/{owner}/{repo}/issues/{number}` to update state or assignees, and `POST /repos/{owner}/{repo}/issues/{number}/comments` for status notes.

## 7. Conversation pattern (WhatsApp-ready)
1. Confirm: "I’ll need the repo URL + a temporary token with repo scope—can you share those now?"
2. After each action, report in natural language first, then share links/details.
3. Keep tokens out of summaries. If the user sends screenshots or sensitive info, acknowledge and avoid re-sharing it elsewhere.

## 8. Daily automation & cron jobs
- Store long-lived secrets outside the skill (e.g., `.env.github-chat-ops` with `GITHUB_CHAT_OPS_TOKEN`, repo, timezone).
- Build reusable scripts under `scripts/` (see `scripts/github_chat_ops_daily.py`) that load env vars, call the same APIs, and print a ready-to-send summary.
- When scheduling via `cron`, run the script from the workspace root, capture stdout verbatim for the message, and surface errors if the script exits non-zero.
- Let end users customize repo/timezone by editing the env file; document that in the skill release notes so downstream consumers know where to look.

## 9. References
Use [`references/github-api-cheatsheet.md`](references/github-api-cheatsheet.md) for ready-made curl templates covering the endpoints above plus pagination tips.
