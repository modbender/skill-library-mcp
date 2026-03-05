---
name: short-url
description: Quickly shorten URLs and generate QR codes via PicSee (picsee.io). After logging in, you can also view analytics and history. Use when user says "縮網址", "短網址", "shorten URL", or requests URL shortening.
---

# PicSee URL Shortener

Quickly shorten long URLs and generate QR codes via PicSee (picsee.io). After logging in, you can also access analytics and history records.

## Important Rules

- **Always use `profile: "openclaw"`**
- **Each snapshot generates new refs** - don't reuse old refs
- **If any step fails, restart from Step 1**
- **When reading files, only use `file_path` parameter** - don't pass `path: ""` (empty string causes EISDIR errors)
- **QR code is opt-in** - Don't generate QR code unless user explicitly asks for it (saves tokens)
- **Use virtual environment for QR generation** - Ensures qrcode package is always available without polluting system Python

## Workflow

Core technique: URL-encode the link and append it to the query string, PicSee will auto-shorten it. Only generate QR code if user requests it (to save tokens).

### Step 1: Open PicSee with URL

URL-encode the long URL, then append it to `https://picsee.io/?url=`.

Use `browser` tool:

```
action: "open"
profile: "openclaw"
targetUrl: "https://picsee.io/?url=(URL-encoded long URL)"
```

**URL encoding example:**
- Original: `https://example.com/path?a=1&b=2`
- Encoded: `https%3A%2F%2Fexample.com%2Fpath%3Fa%3D1%26b%3D2`
- Full: `https://picsee.io/?url=https%3A%2F%2Fexample.com%2Fpath%3Fa%3D1%26b%3D2`

Save the returned `targetId` - you'll need it for following steps.

### Step 2: Wait for shortening to complete

Use `browser` tool to wait 3 seconds:

```
action: "act"
profile: "openclaw"
targetId: "(targetId from Step 1)"
request:
  kind: "wait"
  timeMs: 3000
```

### Step 3: Extract shortened URL

Take a snapshot and extract the shortened URL from the page content:

```
action: "snapshot"
profile: "openclaw"
targetId: "(targetId from Step 1)"
refs: "aria"
```

Read the snapshot text and identify the shortened URL. PicSee displays the result prominently on the page after shortening completes. Look for:
- A clickable link that looks like a short URL
- Text that says "shortened URL" or similar followed by a link
- Any URL that's clearly shorter than the original input

If you can't find the short URL in the snapshot, wait another 3 seconds and retry. If still not found after 2 retries, use the fallback method (see below).

### Step 4: Reply with short URL and ask about QR code

Reply with the shortened URL only. **Do NOT generate QR code by default.**

**Reply in the same language as the user's original request.** Example format in English:

```
Short URL: https://pse.is/xxxxx

Need QR code?
```

The language model will automatically translate this to the user's language if needed.

Wait for user response. If user confirms they want QR code, proceed to Step 5.

### Step 5 (Optional): Generate QR code with virtual environment

**Only run this step if user explicitly requests QR code.**

Use Python virtual environment to ensure qrcode package is available:

```bash
# Check if venv exists, create if not
if [ ! -d ~/openclaw_python_venv ]; then
  python3 -m venv ~/openclaw_python_venv
  source ~/openclaw_python_venv/bin/activate
  pip install qrcode pillow
else
  source ~/openclaw_python_venv/bin/activate
fi

# Generate QR code
python3 - <<'PY'
import qrcode
qr = qrcode.QRCode()
qr.add_data("THE_SHORT_URL_HERE")
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
img.save("/tmp/picsee_qr.png")
print("QR code saved")
PY
```

After generation, send the QR code image file using `message` tool with `filePath: "/tmp/picsee_qr.png"`.

## Fallback Method (when quick method fails)

If Step 1's URL parameter method doesn't auto-shorten (page stays on homepage), use manual operation:

1. **snapshot** to get page element refs (`refs: "aria"`)
2. Find the input box (textbox named "網址貼這裡") and button (`img "PicSee!"`)
3. **act type** to enter the URL in the input box
4. **act click** to click the shorten button
5. Return to Steps 2-4 to extract results

## Common Error Handling

- **EISDIR error**: When reading files, don't pass `path: ""`, only use `file_path` parameter
- **Unknown ref**: Ref has expired, re-run snapshot to get new refs
- **tab not found**: Page was closed, restart from Step 1
- **Short URL not visible in snapshot**: Increase wait time to 5000ms and retry
- **Still can't find short URL**: Switch to fallback method
- **venv creation fails**: Check Python version with `python3 --version` (need 3.3+)
