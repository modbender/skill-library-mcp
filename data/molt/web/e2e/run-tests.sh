#!/bin/bash

# E2E Test Runner for MoltFundMe
# Ensures servers are running before executing tests

set -e

echo "🔍 Checking if servers are running..."

# Check backend
BACKEND_READY=false
for i in {1..30}; do
  if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    BACKEND_READY=true
    echo "✅ Backend is ready"
    break
  fi
  echo "⏳ Waiting for backend... ($i/30)"
  sleep 1
done

if [ "$BACKEND_READY" = false ]; then
  echo "❌ Backend server is not running. Please start it with: cd backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"
  exit 1
fi

# Check frontend
FRONTEND_READY=false
for i in {1..30}; do
  if curl -s http://localhost:5173 > /dev/null 2>&1; then
    FRONTEND_READY=true
    echo "✅ Frontend is ready"
    break
  fi
  echo "⏳ Waiting for frontend... ($i/30)"
  sleep 1
done

if [ "$FRONTEND_READY" = false ]; then
  echo "❌ Frontend server is not running. Please start it with: cd frontend && bun run dev"
  exit 1
fi

echo ""
echo "🚀 Running E2E tests..."
cd "$(dirname "$0")/.."
bun run test:e2e "$@"
