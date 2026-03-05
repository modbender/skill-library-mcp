#!/bin/bash
# Push the latest state.json to GitHub so the dashboard updates
REPO_DIR="/tmp/agent-swarm-public"
STATE_SRC="/home/oryx/.openclaw/workspace/skills/agent-swarm/dashboard/data/state.json"
GH_TOKEN=$(cat /home/oryx/.openclaw/workspace/.gh_classic_token)

if [ ! -d "$REPO_DIR" ]; then
    cd /tmp
    git clone "https://$GH_TOKEN@github.com/clawberrypi/agent-swarm.git" agent-swarm-public 2>/dev/null
fi

cd "$REPO_DIR"
git config user.email "clawberrypi@users.noreply.github.com"
git config user.name "clawberrypi"
git pull origin main 2>/dev/null

cp "$STATE_SRC" "$REPO_DIR/data/state.json"
git add data/state.json
git diff --cached --quiet || {
    git commit -m "update dashboard state $(date -Iseconds)"
    git push origin main 2>/dev/null
    echo "State pushed"
}
