#!/bin/bash

# Basic Postiz CLI Usage Example
# Make sure to set your API key first: export POSTIZ_API_KEY=your_key

echo "🚀 Postiz CLI Example Workflow"
echo ""

# Check if API key is set
if [ -z "$POSTIZ_API_KEY" ]; then
    echo "❌ POSTIZ_API_KEY is not set!"
    echo "Set it with: export POSTIZ_API_KEY=your_api_key"
    exit 1
fi

echo "✅ API key is set"
echo ""

# 1. List integrations
echo "📋 Step 1: Listing connected integrations..."
postiz integrations:list
echo ""

# 2. Create a post
echo "📝 Step 2: Creating a test post..."
postiz posts:create \
  -c "Hello from Postiz CLI! This is an automated test post." \
  -s "$(date -u -v+1H +%Y-%m-%dT%H:%M:%SZ)" # Schedule 1 hour from now
echo ""

# 3. List posts
echo "📋 Step 3: Listing recent posts..."
postiz posts:list -l 5
echo ""

echo "✅ Example workflow completed!"
echo ""
echo "💡 Tips:"
echo "  - Use -i flag to specify integrations when creating posts"
echo "  - Upload images with: postiz upload ./path/to/image.png"
echo "  - Delete posts with: postiz posts:delete <post-id>"
echo "  - Get help: postiz --help"
