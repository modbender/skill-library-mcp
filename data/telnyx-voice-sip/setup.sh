#!/bin/bash
#
# setup.sh - Set up Telnyx Voice skill
#

set -e

echo "🎙️  Telnyx Voice Setup"
echo "======================"
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Install from https://nodejs.org"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js 18+ required. You have $(node -v)"
    exit 1
fi
echo "✅ Node.js $(node -v)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found"
    exit 1
fi
echo "✅ npm $(npm -v)"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
npm install

# Check for .env
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo ""
        echo "📝 Creating .env from .env.example..."
        cp .env.example .env
        echo ""
        echo "⚠️  Edit .env and add your TELNYX_API_KEY"
        echo "   Get one at: https://portal.telnyx.com/#/app/api-keys"
    fi
else
    echo "✅ .env exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your Telnyx API key"
echo "  2. Run: npm run dev"
echo "  3. Call the SIP address shown in console"
