#!/bin/bash
# Example: Spawn a sub-agent with main session context

# Use OpenClaw CLI or API to spawn:
# sessions_spawn with a task that queries history first

cat <<'EOF'
Example task prompt for sub-agent:

"Before you begin, query main session history to understand context:
sessions_history('agent:main:telegram:direct:8264585335', limit=30)

Then: Build the AREF product page based on our discussion.
Use the session history to understand:
- Design preferences
- Key messaging
- Technical requirements
- Target audience

Deliverable: Complete HTML page in /preview/aref-v2/"

This gives the sub-agent full context of your conversation
while still running on a cheaper model (Haiku/Sonnet).
EOF
