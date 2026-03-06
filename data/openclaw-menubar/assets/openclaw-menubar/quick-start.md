# Quick Start Guide

## 🚀 Get it Running in 2 Minutes!

### Step 1: Install Dependencies (if not done)

```bash
cd /Users/prabhanjansharma/.openclaw/workspace/openclaw-menubar
npm install
```

Wait for it to finish (1-2 minutes)...

---

### Step 2: Create Icon (Simple Way)

For now, we'll use a text-based icon:

**Edit `main.js` and replace the icon line:**

```javascript
// Find this line:
icon: path.join(__dirname, 'icons', 'icon.png'),

// Replace with:
icon: path.join(__dirname, 'icons', 'IconTemplate.png'),  // macOS will use emoji
```

**OR** just comment it out:
```javascript
// icon: path.join(__dirname, 'icons', 'icon.png'),
```

---

### Step 3: Run It!

```bash
npm start
```

You should see:
- 🦞 Icon appear in menu bar (or default icon)
- Click it to open chat
- Try typing a message!

---

## Troubleshooting

### npm install fails?

Try:
```bash
npm install --legacy-peer-deps
```

### Icon not showing?

No worries! The app will use a default system icon. It still works perfectly.

To fix later:
```bash
brew install imagemagick
./create-icon.sh
```

### Can't connect to gateway?

1. Check OpenClaw is running:
   ```bash
   openclaw status
   ```

2. Update gateway URL in `renderer.js` if needed

---

## Next Steps

Once it's running:

1. **Try chatting**: "Hey, what's the weather?"
2. **Drag a file**: Drop any file into the chat
3. **Switch models**: Use the dropdown (Sonnet/Opus)
4. **Keyboard shortcut**: Cmd+Shift+O to show/hide

---

**That's it!** Your menu bar app is ready! 🎉
