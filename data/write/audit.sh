#!/usr/bin/env bash
# Run quality audit on a piece, generate report
set -euo pipefail

WORKSPACE="${1:?Usage: audit.sh <workspace> <piece-id>}"
PIECE_ID="${2:?Provide piece ID}"

PIECE_DIR="$WORKSPACE/pieces/$PIECE_ID"
CONTENT_FILE="$PIECE_DIR/content.md"
AUDIT_DIR="$WORKSPACE/audits/$PIECE_ID"

[[ -f "$CONTENT_FILE" ]] || { echo "❌ Content not found: $CONTENT_FILE"; exit 1; }

mkdir -p "$AUDIT_DIR"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
AUDIT_FILE="$AUDIT_DIR/audit_${TIMESTAMP}.md"

# Generate audit template
cat > "$AUDIT_FILE" << EOF
# Audit Report

**Piece:** $PIECE_ID
**Date:** $(date -Iseconds)
**Content Version:** $(jq -r '.versions[-1].version // "v0"' "$PIECE_DIR/meta.json")
**Word Count:** $(wc -w < "$CONTENT_FILE" | tr -d ' ')

---

## Dimensions

### Grammar & Mechanics
<!-- Score 1-10, issues found -->
- Score: 
- Issues:

### Clarity & Structure
<!-- Is it easy to follow? Does it flow? -->
- Score:
- Issues:

### Audience Fit
<!-- Does it match the intended reader? -->
- Score:
- Issues:

### Content Quality
<!-- Is the substance good? Facts correct? -->
- Score:
- Issues:

### Tone & Voice
<!-- Matches brief? Consistent throughout? -->
- Score:
- Issues:

### Conciseness
<!-- Any fluff? Could be shorter? -->
- Score:
- Issues:

---

## Summary

**Overall Score:** /10

**Must Fix:**
1. 
2. 

**Nice to Fix:**
1. 

**Ready to Publish:** Yes / No

---

## Recommended Actions

- [ ] Rewrite section X
- [ ] Fix grammar issues
- [ ] Shorten by N words
EOF

# Update piece metadata
jq --arg audit "audit_${TIMESTAMP}" --arg ts "$(date -Iseconds)" \
  '.audits += [{"id": $audit, "timestamp": $ts}]' \
  "$PIECE_DIR/meta.json" > "$PIECE_DIR/meta.json.tmp" && \
  mv "$PIECE_DIR/meta.json.tmp" "$PIECE_DIR/meta.json"

echo "✅ Audit created: $AUDIT_FILE"
echo ""
echo "Fill in the scores and issues, then run rewrite if needed."
