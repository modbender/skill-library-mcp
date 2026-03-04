# OpenClaw Menu Bar App

Quick chat access to OpenClaw from your macOS menu bar!

## Features

✅ **Menu bar icon** - Always accessible  
✅ **Quick chat** - Instant access to OpenClaw  
✅ **Drag & drop** - Drop files directly  
✅ **Model switching** - Sonnet/Opus toggle  
✅ **Message history** - Persists across restarts  
✅ **Keyboard shortcut** - Cmd+Shift+O to show/hide  
✅ **Connection status** - Live gateway monitoring  

---

## Setup

### 1. Install Dependencies

```bash
cd /Users/prabhanjansharma/.openclaw/workspace/openclaw-menubar
npm install
```

### 2. Create Menu Bar Icon

You need a PNG icon for the menu bar. Convert the SVG:

**Option A: Using ImageMagick**
```bash
brew install imagemagick
convert icons/icon.svg -resize 22x22 icons/icon.png
convert icons/icon.svg -resize 44x44 icons/icon@2x.png
```

**Option B: Using sips (macOS built-in)**
```bash
# First open icon.svg in Preview and export as PNG
# Then resize:
sips -z 22 22 icons/icon.png
sips -z 44 44 icons/icon@2x.png
```

**Option C: Manual (temporary)**
Use any 🦞 emoji as icon temporarily - the app will still work!

### 3. Configure Gateway

Update `renderer.js` if your gateway URL or token is different:

```javascript
const GATEWAY_URL = 'http://192.168.1.29:18789';
const GATEWAY_TOKEN = 'your-token-here';
```

### 4. Run the App

```bash
npm start
```

Or for development (with DevTools):

```bash
NODE_ENV=development npm start
```

---

## Usage

### Basic Chat

1. Click the 🦞 icon in menu bar
2. Type your message
3. Press Enter or click Send

### Model Switching

- **Sonnet** (default) - Fast, cost-effective
- **Opus** - Heavy lifting, complex tasks

Toggle via dropdown in app header.

### Drag & Drop Files

Just drag any file onto the chat window!

Supported:
- Images (PNG, JPG, GIF, WebP)
- Documents (PDF, TXT, MD)
- Code files (JS, PY, etc.)
- Max 10MB per file

### Keyboard Shortcuts

- **Cmd+Shift+O** - Show/hide app
- **Enter** - Send message
- **Shift+Enter** - New line

---

## Gateway API

The app connects to OpenClaw Gateway at:

```
http://192.168.1.29:18789/api/chat
```

**Request format:**
```json
{
  "message": "Your message",
  "model": "claude-sonnet",
  "files": [
    {
      "name": "file.txt",
      "type": "text/plain",
      "content": "base64..."
    }
  ]
}
```

**Response:**
```json
{
  "message": "Assistant response",
  "model": "claude-sonnet-4-5-20250929",
  "usage": { ... }
}
```

---

## Building for Distribution

To create a standalone .app:

```bash
npm run build
```

The app will be in `dist/OpenClaw.app`

---

## Troubleshooting

### "Cannot connect to Gateway"

1. Check OpenClaw Gateway is running:
   ```bash
   openclaw status
   ```

2. Verify gateway bind is set to "lan":
   ```bash
   openclaw config get gateway.bind
   ```

3. Test gateway manually:
   ```bash
   curl http://192.168.1.29:18789/api/status
   ```

### "Icon not showing"

The SVG needs to be converted to PNG first. See Setup step 2.

Temporary fix: Edit `main.js` and comment out the icon line:

```javascript
// icon: path.join(__dirname, 'icons', 'icon.png'),
```

The app will use a default system icon.

### "App doesn't open"

Try clearing Electron cache:

```bash
rm -rf ~/Library/Application\ Support/openclaw-menubar
npm start
```

---

## Development

### File Structure

```
openclaw-menubar/
├── main.js           - Electron main process (menu bar setup)
├── renderer.js       - Chat logic & API calls
├── index.html        - Chat UI structure
├── styles.css        - UI styling
├── package.json      - Dependencies
├── icons/
│   ├── icon.svg      - Source icon
│   ├── icon.png      - Menu bar icon (22x22)
│   └── icon@2x.png   - Retina icon (44x44)
└── README.md
```

### Adding Features

**Custom commands:**
Edit `renderer.js` and add handlers in `sendMessage()`

**UI changes:**
Edit `styles.css` and `index.html`

**Gateway integration:**
Modify API calls in `renderer.js`

---

## Credits

Built with:
- **Electron** - Desktop app framework
- **menubar** - Menu bar integration
- **axios** - HTTP client

---

## License

MIT

---

**Enjoy your OpenClaw menu bar app!** 🦞🚀
