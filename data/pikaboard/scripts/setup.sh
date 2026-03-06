#!/bin/bash
# PikaBoard Setup Script
# Run from pikaboard repo root

set -e

echo "📋 Setting up PikaBoard..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js 18+ required. Found: $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v)"

# Backend setup
echo "📦 Installing backend..."
cd backend
npm install
npm run build
cd ..

# Frontend setup
echo "🎨 Installing frontend..."
cd frontend
npm install
npm run build
cd ..

# Create .env if not exists
if [ ! -f backend/.env ]; then
    echo "⚙️ Creating .env..."
    cat > backend/.env << EOF
DATABASE_PATH=./pikaboard.db
PIKABOARD_TOKEN=$(openssl rand -hex 32)
PORT=3001
EOF
    echo "✅ Created backend/.env with random API token"
    echo "   Check the file for your PIKABOARD_TOKEN"
else
    echo "✅ backend/.env already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start PikaBoard:"
echo "  cd backend && npm start"
echo ""
echo "Dashboard: http://localhost:3001"
echo ""
