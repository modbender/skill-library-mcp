#!/bin/bash
#
# Verify Hummingbot API installation
# Checks if the Swagger UI is accessible at http://localhost:8000/docs/
#
set -eu

# Load .env if present
for f in hummingbot-api/.env ~/.hummingbot/.env .env; do
    if [ -f "$f" ]; then
        set -a; source "$f"; set +a
        break
    fi
done

API_URL="${HUMMINGBOT_API_URL:-http://localhost:8000}"

echo "Verifying Hummingbot API installation..."
echo ""

# Check if docs page is accessible (contains Swagger UI)
if curl -s "$API_URL/docs" 2>/dev/null | grep -qi "swagger"; then
    echo "✓ Hummingbot API is running"
    echo "  Swagger UI: $API_URL/docs"
    echo "  Credentials: admin/admin (or as configured)"
    exit 0
else
    echo "✗ Hummingbot API is not accessible at $API_URL/docs"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check if containers are running: docker ps | grep hummingbot"
    echo "  2. View logs: cd ./hummingbot-api && docker compose logs -f"
    exit 1
fi
