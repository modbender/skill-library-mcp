#!/bin/bash

# Chrome Extension Generator
# Usage: chrome-extension-generator "Extension Name" "Description" [options]

set -e

NAME="${1:-}"
DESCRIPTION="${2:-}"
TEMPLATE="${3:-basic}"
STACK="${4:-javascript}"

OUTPUT_DIR="${5:-.}"

# Parse options
while [[ $# -gt 5 ]]; do
    case $6 in
        --template|-t)
            TEMPLATE="$7"
            shift 2
            ;;
        --stack|-s)
            STACK="$7"
            shift 2
            ;;
        --output|-o)
            OUTPUT_DIR="$7"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$NAME" ]; then
    echo -e "${YELLOW}Usage: chrome-extension-generator \"Name\" \"Description\" [--template basic|popup|full]${NC}"
    exit 1
fi

if [ -z "$DESCRIPTION" ]; then
    DESCRIPTION="An amazing Chrome extension"
fi

DIR_NAME=$(echo "$NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
OUTPUT_PATH="$OUTPUT_DIR/$DIR_NAME"

mkdir -p "$OUTPUT_PATH"
mkdir -p "$OUTPUT_PATH/_locales/en"

echo -e "${BLUE}📦 Generating Chrome Extension${NC}"
echo "Name: $NAME"
echo "Template: $TEMPLATE"
echo ""

# Generate manifest.json
cat > "$OUTPUT_PATH/manifest.json" << MANIFEST
{
  "manifest_version": 3,
  "name": "$NAME",
  "version": "1.0.0",
  "description": "$DESCRIPTION",
  "permissions": ["storage"],
  "action": {
    "default_popup": "popup.html",
    "default_icon": "icon.png"
  },
  "background": {
    "service_worker": "background.js"
  },
  "icons": {
    "16": "icon.png",
    "48": "icon.png",
    "128": "icon.png"
  }
}
MANIFEST

# Generate popup.html
cat > "$OUTPUT_PATH/popup.html" << POPUP
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>$NAME</title>
  <style>
    body {
      width: 300px;
      padding: 16px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    h1 { font-size: 16px; margin: 0 0 12px; }
    button {
      width: 100%;
      padding: 10px;
      background: #4285f4;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    button:hover { background: #3367d6; }
  </style>
</head>
<body>
  <h1>$NAME</h1>
  <p>$DESCRIPTION</p>
  <button id="actionBtn">Click Me</button>
  <script src="popup.js"></script>
</body>
</html>
POPUP

# Generate popup.js
cat > "$OUTPUT_PATH/popup.js" << POPUP_JS
document.getElementById('actionBtn').addEventListener('click', () => {
  // Your logic here
  console.log('Button clicked!');
  
  // Example: Save to storage
  chrome.storage.local.set({ lastClick: Date.now() }, () => {
    console.log('Saved!');
  });
});
POPUP_JS

# Generate background.js
cat > "$OUTPUT_PATH/background.js" << BACKGROUND
// Background service worker
chrome.runtime.onInstalled.addListener(() => {
  console.log('Extension installed!');
});

// Handle messages from popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'doSomething') {
    // Do something
    sendResponse({ success: true });
  }
});
BACKGROUND

# Generate icon (placeholder)
# In production, you'd generate an actual icon

# Generate README
cat > "$OUTPUT_PATH/README.md" << README
# $NAME

$DESCRIPTION

## Installation

1. Open Chrome and navigate to \`chrome://extensions\`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select this folder

## Development

1. Make changes to the source files
2. Click "Reload" in the extensions page
3. Test your changes

## Files

- \`manifest.json\` - Extension configuration
- \`popup.html/js\` - Popup UI
- \`background.js\` - Background service worker
- \`content.js\` - Content script (add as needed)

## Publishing

1. Package the extension (Pack extension in chrome://extensions)
2. Create a developer account at https://chrome.google.com/webstore/devconsole
3. Upload your packaged extension
4. Fill in store listing details
5. Submit for review

## License

MIT
README

echo -e "${GREEN}✅ Chrome extension generated!${NC}"
echo "📁 Output: $OUTPUT_PATH"
echo ""
echo "Next steps:"
echo "1. cd $OUTPUT_PATH"
echo "2. Add your extension logic"
echo "3. Load in Chrome (chrome://extensions → Developer mode → Load unpacked)"
