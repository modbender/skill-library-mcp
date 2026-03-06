#!/usr/bin/env bash
# Usage: ./create_agent.sh "Agent_Name" "Role_Description"

NAME=$1
ROLE=$2
DIR="agents/$NAME"

mkdir -p "$DIR/inbox" "$DIR/outbox" "$DIR/workspace"

cat <<EOM > "$DIR/SKILL.md"
---
name: $NAME
description: $ROLE
---
# Mission
You are $NAME. Your role is: $ROLE.
Read instructions from ./inbox and write outputs to ./outbox.
EOM

echo "✅ Factory: Agent $NAME provisioned at $DIR"
