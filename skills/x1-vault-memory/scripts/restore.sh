set -euo pipefail
cd /home/node/.openclaw/workspace
node x1-vault-memory/src/restore.js "$@"
