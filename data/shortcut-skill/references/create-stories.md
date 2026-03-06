# Bulk Epic + Story Creation

Use this pattern when creating a full feature epic with multiple dependent stories.

**All JSON is built via `jq -n --arg` / `--argjson` — never interpolate values directly into shell strings.**

## 1. Create the Epic First

```bash
SHORTCUT_API_TOKEN=$(cat ~/.openclaw/secrets/shortcut)
BASE="https://api.app.shortcut.com/api/v3"

EPIC=$(jq -n \
  --arg name "My Feature Epic" \
  --arg description "What this epic delivers and why." \
  --arg group_id "$GROUP_ID" \
  '{name: $name, description: $description, group_id: $group_id, labels: [{name: "mobile"}]}' | \
  curl -s -X POST \
    -H "Shortcut-Token: $SHORTCUT_API_TOKEN" \
    -H "Content-Type: application/json" \
    -d @- "$BASE/epics")

EPIC_ID=$(echo "$EPIC" | jq -r '.id')
EPIC_URL=$(echo "$EPIC" | jq -r '.app_url')
echo "Epic: sc-$EPIC_ID → $EPIC_URL"
```

## 2. Create Stories in Dependency Order

Create stories in implementation order (foundations first — infra → api → mobile). Capture each ID for linking.

```bash
create_story() {
  local name="$1" type="$2" description="$3" estimate="$4" label="$5"
  jq -n \
    --arg name "$name" \
    --arg story_type "$type" \
    --arg description "$description" \
    --argjson estimate "$estimate" \
    --argjson workflow_state_id 500000008 \
    --arg group_id "$GROUP_ID" \
    --arg label "$label" \
    --argjson epic_id "$EPIC_ID" \
    '{name: $name, story_type: $story_type, description: $description,
      estimate: $estimate, workflow_state_id: $workflow_state_id,
      group_id: $group_id, labels: [{name: $label}], epic_id: $epic_id}' | \
  curl -s -X POST \
    -H "Shortcut-Token: $SHORTCUT_API_TOKEN" \
    -H "Content-Type: application/json" \
    -d @- "$BASE/stories"
}

S1=$(create_story "Story 1 title" "chore" "**Background**\nContext.\n\n**Acceptance Criteria**\n- [ ] criterion 1" 1 "infra")
S1_ID=$(echo "$S1" | jq -r '.id')
echo "sc-$S1_ID: $(echo "$S1" | jq -r '.name')"

S2=$(create_story "Story 2 title" "bug" "**Background**\nContext.\n\n**Acceptance Criteria**\n- [ ] criterion" 3 "mobile")
S2_ID=$(echo "$S2" | jq -r '.id')
echo "sc-$S2_ID: $(echo "$S2" | jq -r '.name')"

# Repeat for remaining stories...
```

## 3. Wire Dependencies

```bash
wire_block() {
  local blocker=$1 blocked=$2
  jq -n --argjson subject_id "$blocker" --argjson object_id "$blocked" \
    '{subject_id: $subject_id, object_id: $object_id, verb: "blocks"}' | \
  curl -s -X POST \
    -H "Shortcut-Token: $SHORTCUT_API_TOKEN" \
    -H "Content-Type: application/json" \
    -d @- "$BASE/story-links" > /dev/null
  echo "sc-$blocker blocks sc-$blocked"
}

wire_block "$S1_ID" "$S2_ID"
wire_block "$S2_ID" "$S3_ID"
# Final story blocked by all preceding:
wire_block "$S1_ID" "$S4_ID"
wire_block "$S2_ID" "$S4_ID"
wire_block "$S3_ID" "$S4_ID"
```

## 4. Print Summary

```bash
echo ""
echo "✅ Epic sc-$EPIC_ID: $EPIC_URL"
echo "Stories created: sc-$S1_ID  sc-$S2_ID  sc-$S3_ID  sc-$S4_ID"
```

## Description Markdown Template

```markdown
**Background**
1–2 sentences of context: what problem this solves and why it matters now.

**User Story**
As a [user], I want to [action], so that [outcome].

**Acceptance Criteria**
- [ ] Specific, testable criterion starting with a verb
- [ ] Another criterion
- [ ] Edge case handled (e.g. expired token shows friendly error)

**Technical Notes**
Key implementation hints — specific enough to be useful, not prescriptive.
```

## Story Type Quick Reference

| Type | Use when |
|------|----------|
| `feature` | New user-visible functionality |
| `bug` | Something broken that needs fixing |
| `chore` | Technical work with no direct user impact (config, infra, docs, tests) |

## Point Scale

| Points | Effort |
|--------|--------|
| 1 | Trivial, <2h |
| 2 | Small, <1 day |
| 3 | Standard, 1–2 days |
| 5 | Meaty, 2–4 days |
| 8 | Large — consider splitting |
