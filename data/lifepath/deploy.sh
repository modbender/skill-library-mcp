#!/bin/bash
# Deploy LifePath to production

set -e

echo "🎭 Deploying LifePath..."

# Check requirements
command -v node >/dev/null 2>&1 || { echo "❌ Node.js required"; exit 1; }
command -v psql >/dev/null 2>&1 || { echo "❌ PostgreSQL required"; exit 1; }

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Check environment
if [ ! -f .env ]; then
    echo "⚠️  .env not found. Copying from example..."
    cp .env.example .env
    echo "📝 Please edit .env with your API keys"
    exit 1
fi

# Initialize database
echo "🗄️  Initializing database..."
npm run init-db

# Start server
echo "🚀 Starting server..."
npm start
