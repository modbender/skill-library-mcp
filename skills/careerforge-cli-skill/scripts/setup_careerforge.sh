#!/bin/bash
# Setup script for CareerForge CLI

set -e

echo "🎯 Setting up CareerForge CLI..."

# Check if careerforge-cli directory exists
if [ ! -d "careerforge-cli" ]; then
    echo "❌ careerforge-cli directory not found!"
    echo "Please ensure the skill is properly installed."
    exit 1
fi

cd careerforge-cli

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Check for Gemini API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo ""
    echo "⚠️  GEMINI_API_KEY not found in environment"
    echo "Please set your Google Gemini API key:"
    echo "  export GEMINI_API_KEY='your-key-here'"
    echo ""
    echo "Or add it to ~/.bashrc or ~/.zshrc for persistence"
fi

echo ""
echo "✅ CareerForge CLI setup complete!"
echo ""
echo "Usage:"
echo "  node generate_cv_from_json.js job.json"
echo ""
echo "Example job.json:"
echo '  {'
echo '    "title": "Data Analyst",'
echo '    "company": "Example Corp",'
echo '    "description": "Job description here..."'
echo '  }'