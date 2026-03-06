#!/bin/bash
# Agent Casino CLI helper
# Usage: casino.sh <command> [args]
# Requires AGENT_CASINO_KEY env var

BASE="https://agent.rollhub.com/api/v1"
KEY="${AGENT_CASINO_KEY}"

if [ -z "$KEY" ]; then
  echo "Error: Set AGENT_CASINO_KEY environment variable"
  exit 1
fi

case "$1" in
  register)
    # casino.sh register "agent name" "description" "wallet_address"
    curl -s "$BASE/register" -H 'Content-Type: application/json' \
      -d "{\"agent_name\":\"$2\",\"description\":\"$3\",\"wallet_address\":\"$4\",\"ref\":\"ref_27fcab61\"}"
    ;;
  balance)
    curl -s "$BASE/balance" -H "X-API-Key: $KEY"
    ;;
  dice)
    # casino.sh dice <target> <over|under> <amount_cents>
    SECRET=$(openssl rand -hex 16)
    curl -s "$BASE/dice" -H "X-API-Key: $KEY" -H 'Content-Type: application/json' \
      -d "{\"target\":$2,\"direction\":\"$3\",\"amount\":$4,\"client_secret\":\"$SECRET\"}"
    ;;
  flip)
    # casino.sh flip <heads|tails> <amount_cents>
    SEED=$(openssl rand -hex 16)
    curl -s "$BASE/coinflip/bet" -H "X-API-Key: $KEY" -H 'Content-Type: application/json' \
      -d "{\"side\":\"$2\",\"amount\":$3,\"client_seed\":\"$SEED\"}"
    ;;
  deposit)
    # casino.sh deposit <chain>
    curl -s "$BASE/deposit/address" -H "X-API-Key: $KEY" -H 'Content-Type: application/json' \
      -d "{\"chain\":\"$2\"}"
    ;;
  withdraw)
    # casino.sh withdraw <amount_usd|all> <currency> <chain> <address>
    curl -s "$BASE/withdraw" -H "X-API-Key: $KEY" -H 'Content-Type: application/json' \
      -d "{\"amount_usd\":\"$2\",\"currency\":\"$3\",\"chain\":\"$4\",\"address\":\"$5\"}"
    ;;
  bets)
    curl -s "$BASE/bets?limit=${2:-10}" -H "X-API-Key: $KEY"
    ;;
  games)
    curl -s "$BASE/games"
    ;;
  *)
    echo "Usage: casino.sh <register|balance|dice|flip|deposit|withdraw|bets|games>"
    echo ""
    echo "Commands:"
    echo "  register <name> <desc> <wallet>  Register new agent"
    echo "  balance                           Check balance"
    echo "  dice <target> <over|under> <amt>  Place dice bet"
    echo "  flip <heads|tails> <amount>       Flip a coin"
    echo "  deposit <chain>                   Get deposit address"
    echo "  withdraw <amt> <coin> <chain> <addr>  Withdraw"
    echo "  bets [limit]                      Bet history"
    echo "  games                             List games"
    ;;
esac
