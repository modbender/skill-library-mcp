---
name: shortcut
description: "Access and manage Shortcut.com (formerly Clubhouse) project management. Use when the user asks to: list stories, view backlog, search issues, check epics, update story state, create stories or epics, add comments, wire story dependencies, or fetch/triage a story. Trigger keywords: shortcut, story, backlog, sc-XXXX, sprint, epic, ticket."
metadata:
  {
    "openclaw": {
      "emoji": "🎯",
      "homepage": "https://developer.shortcut.com/api/rest/v3",
      "requires": {
        "bins": ["curl", "jq"],
        "secrets": ["shortcut"]
      },
      "primaryEnv": "SHORTCUT_API_TOKEN",
      "credentialNote": "Shortcut API token — stored at ~/.openclaw/secrets/shortcut. Generate at app.shortcut.com → Settings → API Tokens."
    }
  }
---

# Shortcut.com Skill 🎯

Read and write Shortcut.com stories, epics, and workflows via the REST API v3.

## Auth Setup

Token is stored at `~/.openclaw/secrets/shortcut` (mode 600, readable only by your user).

```bash
SHORTCUT_API_TOKEN=$(cat ~/.openclaw/secrets/shortcut 2>/dev/null)
BASE="https://api.app.shortcut.com/api/v3"
```

If empty, ask the user for their API token, then save it:
```bash
mkdir -p ~/.openclaw/secrets
echo -n "<token>" > ~/.openclaw/secrets/shortcut && chmod 600 ~/.openclaw/secrets/shortcut
```

Generate a token at **app.shortcut.com → Settings → API Tokens**. Shortcut tokens have full member-level access — no scope restriction is available. Rotate or delete the token at any time from the same settings page.

> If you prefer not to persist the token on disk, skip saving and export it for the session only:
> `export SHORTCUT_API_TOKEN="<token>"`

---

## ⚠️ JSON Construction Rule

**Always use `jq -n --arg` / `--argjson` to build request bodies.** Never interpolate user-supplied values directly into shell strings — this prevents shell injection from values containing quotes, backticks, or `$()`.

```bash
# ✅ Safe — jq handles all escaping
DATA=$(jq -n --arg name "$TITLE" --arg desc "$DESCRIPTION" \
  '{name: $name, description: $desc}')
curl -s -X POST -H "Shortcut-Token: $SHORTCUT_API_TOKEN" \
  -H "Content-Type: application/json" -d "$DATA" "$BASE/stories"

# ❌ Unsafe — never do this
curl ... -d "{\"name\": \"$TITLE\"}"
```

---

## Reading

### Get a Story
```bash
curl -s -H "Shortcut-Token: $SHORTCUT_API_TOKEN" "$BASE/stories/<id>" | \
  jq '{id, name, story_type, description, workflow_state_id, estimate, epic_id, labels: [.labels[].name]}'
```
Strip the `sc-` prefix from IDs (use the number only).

### Search Stories
```bash
curl -s -H "Shortcut-Token: $SHORTCUT_API_TOKEN" \
  "$BASE/search/stories?$(jq -rn --arg q "$QUERY" 'query=\($q|@uri)&page_size=10')" | \
  jq '.data[] | {id, name, story_type, estimate}'
```

### List My Stories
```bash
ME=$(curl -s -H "Shortcut-Token: $SHORTCUT_API_TOKEN" "$BASE/member" | jq -r '.id')
curl -s -H "Shortcut-Token: $SHORTCUT_API_TOKEN" \
  "$BASE/search/stories?owner_id=${ME}&page_size=25" | \
  jq '.data[] | {id, name, story_type, workflow_state_id}'
```

### List Workflows & States
```bash
curl -s -H "Shortcut-Token: $SHORTCUT_API_TOKEN" "$BASE/workflows" | \
  jq '.[] | {workflow: .name, states: [.states[] | {id, name, type}]}'
```

### List Epics
```bash
curl -s -H "Shortcut-Token: $SHORTCUT_API_TOKEN" "$BASE/epics" | \
  jq '.[] | {id, name, state, total_stories: .stats.num_stories_total}'
```

### Get Epic Stories
```bash
curl -s -H "Shortcut-Token: $SHORTCUT_API_TOKEN" "$BASE/epics/<epic_id>/stories" | \
  jq '.[] | {id, name, story_type, workflow_state_id, estimate}'
```

### List Teams (Groups)
```bash
curl -s -H "Shortcut-Token: $SHORTCUT_API_TOKEN" "$BASE/groups" | \
  jq '[.[] | {id, name, mention_name}]'
```

---

## Writing

All write operations build JSON with `jq -n --arg` to safely handle user-supplied strings.

### Create Story
```bash
DATA=$(jq -n \
  --arg name "$STORY_TITLE" \
  --arg description "$STORY_DESCRIPTION" \
  --arg story_type "$STORY_TYPE" \
  --argjson estimate "$ESTIMATE" \
  --argjson workflow_state_id "$STATE_ID" \
  --arg group_id "$GROUP_ID" \
  --argjson epic_id "$EPIC_ID" \
  '{name: $name, description: $description, story_type: $story_type,
    estimate: $estimate, workflow_state_id: $workflow_state_id,
    group_id: $group_id, epic_id: $epic_id}')

curl -s -X POST \
  -H "Shortcut-Token: $SHORTCUT_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$DATA" "$BASE/stories" | jq '{id, name, app_url}'
```

Story types: `feature`, `bug`, `chore`

To add labels, extend the jq expression:
```bash
DATA=$(jq -n --arg name "$TITLE" --arg label "mobile" \
  '{name: $name, labels: [{name: $label}]}')
```

### Create Epic
```bash
DATA=$(jq -n \
  --arg name "$EPIC_TITLE" \
  --arg description "$EPIC_DESCRIPTION" \
  --arg group_id "$GROUP_ID" \
  '{name: $name, description: $description, group_id: $group_id}')

curl -s -X POST \
  -H "Shortcut-Token: $SHORTCUT_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$DATA" "$BASE/epics" | jq '{id, name, app_url}'
```

### Update Story (state, estimate, title, etc.)
```bash
DATA=$(jq -n --argjson state "$NEW_STATE_ID" '{workflow_state_id: $state}')

curl -s -X PUT \
  -H "Shortcut-Token: $SHORTCUT_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$DATA" "$BASE/stories/$STORY_ID" | jq '{id, name, workflow_state_id}'
```

### Add Comment
```bash
DATA=$(jq -n --arg text "$COMMENT_TEXT" '{text: $text}')

curl -s -X POST \
  -H "Shortcut-Token: $SHORTCUT_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$DATA" "$BASE/stories/$STORY_ID/comments" | jq '{id, text}'
```

### Wire Story Dependencies (blocker links)
```bash
DATA=$(jq -n \
  --argjson object_id "$BLOCKED_ID" \
  --argjson subject_id "$BLOCKER_ID" \
  '{object_id: $object_id, subject_id: $subject_id, verb: "blocks"}')

curl -s -X POST \
  -H "Shortcut-Token: $SHORTCUT_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$DATA" "$BASE/story-links" | jq '{id, verb}'
```

---

## Workflow State Reference

Common default state IDs (verify with the workflows endpoint for your workspace):

| State | Typical ID |
|-------|-----------|
| Backlog | 500000008 |
| Ready for Development | 500000007 |
| In Development | 500000006 |
| Ready for Review | 500000010 |
| Completed | 500000011 |

Always confirm state IDs by calling `/workflows` — they vary per account.

---

## Bulk Story Creation

For creating full epics with multiple dependent stories, see `references/create-stories.md`.

---

## Display Format

Stories:
```
🎯 sc-1234 — User Authentication Flow [feature, 5pts]
   Status: In Development | Epic: Auth & Onboarding
   Labels: backend, mobile

   > Users should be able to log in with email/password...
```

Backlog list (table format):
```
| ID      | Story                    | Type    | Pts | State   |
|---------|--------------------------|---------|-----|---------|
| sc-1234 | User Auth Flow           | feature | 5   | In Dev  |
| sc-1235 | Fix password reset email | bug     | 2   | Backlog |
```

---

## Tips

- Always check for API token before making requests
- Strip `sc-` prefix from story IDs for API calls
- Labels are auto-created by Shortcut if they don't exist — safe to pass new label names
- Rate limit: 200 req/min — not a concern in normal usage
- For exact story lookup always use `/stories/<id>` directly, not search
