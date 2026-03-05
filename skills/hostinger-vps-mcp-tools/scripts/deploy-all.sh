#!/bin/bash
# Complete Koda VPS Deployment
# Usage: ./deploy-all.sh SERVER_IP "Agent Name" [KODA_PORT] [SSH_PORT] [SSH_KEY]

set -e

SERVER_IP="${1:?Usage: $0 SERVER_IP \"Agent Name\" [KODA_PORT] [SSH_PORT] [SSH_KEY]}"
AGENT_NAME="${2:-Koda}"
KODA_PORT="${3:-18789}"
SSH_PORT="${4:-22}"
SSH_KEY="${5:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Koda VPS Full Deployment"
echo "==========================="
echo "Server:    $SERVER_IP"
echo "Agent:     $AGENT_NAME"
echo "Koda Port: $KODA_PORT"
echo "SSH Port:  $SSH_PORT"
echo ""

# SSH options
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p $SSH_PORT"
if [ -n "$SSH_KEY" ]; then
    SSH_OPTS="$SSH_OPTS -i $SSH_KEY"
fi

run_remote() {
    local script="$1"
    shift
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Running: $(basename "$script") $*"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ssh $SSH_OPTS root@"$SERVER_IP" "bash -s $*" < "$script"
    echo ""
}

# For first connection, use default port 22
FIRST_SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
if [ -n "$SSH_KEY" ]; then
    FIRST_SSH_OPTS="$FIRST_SSH_OPTS -i $SSH_KEY"
fi

# Run server setup (uses default port, may change SSH port)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Running: 01-server-setup.sh $KODA_PORT $SSH_PORT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh $FIRST_SSH_OPTS root@"$SERVER_IP" "bash -s $KODA_PORT $SSH_PORT" < "$SCRIPT_DIR/01-server-setup.sh"
echo ""

# Wait for SSH port change if needed
if [ "$SSH_PORT" != "22" ]; then
    echo "Waiting for SSH port change..."
    sleep 5
fi

# Run remaining scripts with potentially new SSH port
run_remote "$SCRIPT_DIR/02-install-gui.sh"
run_remote "$SCRIPT_DIR/03-install-docker.sh"
run_remote "$SCRIPT_DIR/04-deploy-koda.sh" "$KODA_PORT"
run_remote "$SCRIPT_DIR/05-configure-identity.sh" "$AGENT_NAME"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Your virtual employee '$AGENT_NAME' is ready!"
echo ""
echo "📍 Access:"
echo "   Webchat:  http://$SERVER_IP:$KODA_PORT"
echo "   RDP:      $SERVER_IP:3389 (user: koda)"
echo "   SSH:      ssh -p $SSH_PORT koda@$SERVER_IP"
echo ""
echo "📝 Next steps:"
echo "   1. Set password: ssh -p $SSH_PORT root@$SERVER_IP 'passwd koda'"
echo "   2. Open webchat and configure API key"
echo "   3. Customize identity in ~/koda/workspace/"
echo ""
echo "🔒 Security notes:"
echo "   - SSH on non-default port $SSH_PORT"
echo "   - Webchat on custom port $KODA_PORT"
echo "   - fail2ban protects SSH"
echo "   - UFW firewall active"
echo ""
