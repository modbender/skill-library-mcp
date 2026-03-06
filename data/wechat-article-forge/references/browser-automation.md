# Browser Automation Publishing (CDP)

For **unverified subscription accounts (未认证订阅号)**, WeChat's content APIs are unavailable. This skill uses browser automation to drive the mp.weixin.qq.com editor directly.

There are **two paths** depending on your setup. Read both and use the one that matches.

---

## Path A: OpenClaw Browser Tool (Recommended for Titan/macOS)

When OpenClaw runs its own Chromium (built-in browser at port 18800), you **must** use the OpenClaw `browser` tool. Direct CDP WebSocket connections do not work because Playwright isolates its page contexts.

### Why You Cannot Bypass the Browser Tool

- Port 18800 IS Chrome's CDP remote debugging port
- But `browser` tool uses Playwright internally; pages live in Playwright's private context
- `/json/list` returns an empty array — pages are invisible to external CDP clients
- Direct WebSocket with `Target.getTargets` returns 0 targets
- Python `playwright.connect_over_cdp()` sees 0 pages (different context)
- **Bottom line:** All JS execution must go through `browser(action=act, request={kind:"evaluate", fn:...})`

### Prerequisites

1. OpenClaw running with built-in browser (default on macOS/Titan)
2. User navigates to `mp.weixin.qq.com` via `browser(action=open, targetUrl="https://mp.weixin.qq.com")`
3. User scans QR code to log in
4. Extract `token` from the URL after login

### HTML Injection via Base64 Chunking

Direct HTML strings in the `fn` parameter fail due to nested JSON/JS escaping issues (quotes, angle brackets, backslashes all conflict). Base64 encoding solves this — only alphanumeric + `/+=` characters, zero escaping issues.

**Confirmed working:** 3500-char base64 chunks pass through the browser tool's `evaluate` fn parameter. No obvious size limit found, but chunk for safety.

#### Step 1: Prepare Base64 Chunks (in shell)

```bash
# Read formatted.html, strip <img> tags, base64 encode
DRAFT_DIR=~/.wechat-article-writer/drafts/<slug>
cat "$DRAFT_DIR/formatted.html" | sed 's/<img[^>]*>//g' > /tmp/text-only.html
B64=$(base64 -i /tmp/text-only.html | tr -d '\n')
echo "Total base64 length: ${#B64}"

# Split into 3500-char chunks
CHUNK_SIZE=3500
i=0
while [ $((i * CHUNK_SIZE)) -lt ${#B64} ]; do
  echo "${B64:$((i * CHUNK_SIZE)):$CHUNK_SIZE}" > "/tmp/chunk_${i}.txt"
  i=$((i + 1))
done
echo "Total chunks: $i"
```

#### Step 2: Store Chunks in Page Context (via browser tool)

For each chunk, call:
```
browser(action=act, request={
  kind: "evaluate",
  fn: "window._b = (window._b || '') + '<chunk_content_here>'; return 'stored ' + window._b.length;"
})
```

Track which chunks have been stored in `pipeline-state.json` (field: `chunks_stored`) for resume after compaction.

#### Step 3: Decode and Inject

```
browser(action=act, request={
  kind: "evaluate",
  fn: "(function(){ var html = atob(window._b); delete window._b; var pm = document.querySelector('.ProseMirror'); if(!pm) return 'NO_PM'; pm.focus(); var range = document.createRange(); range.selectNodeContents(pm); window.getSelection().removeAllRanges(); window.getSelection().addRange(range); var dt = new DataTransfer(); dt.setData('text/html', html); pm.dispatchEvent(new ClipboardEvent('paste', {bubbles:true, cancelable:true, clipboardData:dt})); return 'INJECTED ' + html.length + ' chars'; })()"
})
```

#### Step 4: Set Title

The title field is a `<textarea>` (as of 2026-02), not a standard `<input>` or contenteditable div.

```
browser(action=act, request={
  kind: "evaluate",
  fn: "(function(){ var ta = document.querySelector('textarea'); if(!ta) return 'NO_TEXTAREA'; var setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set; setter.call(ta, 'YOUR TITLE HERE'); ta.dispatchEvent(new Event('input', {bubbles:true})); ta.dispatchEvent(new Event('change', {bubbles:true})); return 'TITLE_SET'; })()"
})
```

#### Step 5: Insert Images via Clipboard Blob Paste

For each image, read the file, base64 encode, chunk-store in page context, then paste as blob:

```
browser(action=act, request={
  kind: "evaluate",
  fn: "(function(){ /* 1. Find anchor text */ var pm = document.querySelector('.ProseMirror'); var s0 = pm.querySelector('section'); var kids = Array.from(s0.children); var target = null; for(var i=0;i<kids.length;i++){ if(kids[i].textContent.includes('ANCHOR_TEXT')){ target = kids[i]; }} if(!target) return 'ANCHOR_NOT_FOUND'; /* 2. Position cursor */ var range = document.createRange(); range.selectNodeContents(target); range.collapse(false); var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range); document.execCommand('insertParagraph'); return 'CURSOR_READY'; })()"
})
```

Then paste the image blob:
```
browser(action=act, request={
  kind: "evaluate",
  fn: "(async function(){ var b64 = window._img; delete window._img; var bin = atob(b64); var bytes = new Uint8Array(bin.length); for(var i=0;i<bin.length;i++) bytes[i]=bin.charCodeAt(i); var blob = new Blob([bytes],{type:'image/png'}); var file = new File([blob],'fig.png',{type:'image/png'}); var dt = new DataTransfer(); dt.items.add(file); document.querySelector('.ProseMirror').dispatchEvent(new ClipboardEvent('paste',{bubbles:true,cancelable:true,clipboardData:dt})); return 'PASTED'; })()"
})
```

Wait 3-5 seconds between images for WeChat CDN upload.

#### Step 6: Save as Draft

```
browser(action=act, request={
  kind: "evaluate",
  fn: "(function(){ var btns = document.querySelectorAll('button'); for(var b of btns){ if(b.textContent.includes('保存为草稿')){ b.click(); return 'SAVE_CLICKED'; }} return 'SAVE_BTN_NOT_FOUND'; })()"
})
```

Then poll for save completion (check every 2s, up to 30s):
```
browser(action=act, request={
  kind: "evaluate",
  fn: "(function(){ var text = document.body.innerText; if(text.includes('已保存')) return 'SAVED'; if(text.includes('保存失败')) return 'SAVE_FAILED'; return 'SAVING'; })()"
})
```

### Mixed Content Warning

HTTPS pages (mp.weixin.qq.com) cannot fetch HTTP localhost resources due to mixed content blocking. Do not attempt to serve files from a local HTTP server and inject them via `<img src="http://localhost:...">`. Use base64 blob paste instead.

---

## Path B: Direct CDP via Python WebSocket (Linux/Remote Server)

When Chrome runs as a standalone process (not through OpenClaw's browser tool), you can connect directly via CDP WebSocket. This is the preferred path on any headless Linux server.

### Prerequisites

1. Chrome running with remote debugging:
   ```bash
   DISPLAY=:1 google-chrome-stable \
     --remote-debugging-port=18800 \
     --remote-allow-origins='*' \
     --user-data-dir=/tmp/openclaw-browser2 \
     --no-first-run --disable-default-apps \
     --disable-gpu --disable-software-rasterizer &
   ```
   **`--remote-allow-origins='*'` is REQUIRED** for Python/Node CDP WebSocket access. Without it you get 403.
2. User must scan QR code to log in to mp.weixin.qq.com (session persists in `user-data-dir`).
3. Extract the `token` from the URL: `mp.weixin.qq.com/...?token=XXXXXXXXX`.

### CDP Connection

```python
import json, websocket

# Get tab list
import requests
tabs = requests.get("http://127.0.0.1:18800/json/list").json()
tab_id = tabs[0]["id"]

ws = websocket.create_connection(f"ws://127.0.0.1:18800/devtools/page/{tab_id}")

def evaluate(expr, await_promise=False):
    ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate",
        "params": {"expression": expr, "returnByValue": True, "awaitPromise": await_promise}}))
    return json.loads(ws.recv()).get("result", {}).get("result", {}).get("value")
```

### Publishing Workflow (Python CDP)

#### Phase 1: Inject Text-Only HTML

Strip all `<img>` tags from `formatted.html` and inject the text-only version via clipboard paste.

```python
import re, json

with open('formatted.html') as f:
    html = f.read()
text_html = re.sub(r'<img[^>]*/?>', '', html)

evaluate(f"""
(function() {{
    var pm = document.querySelector('.ProseMirror');
    pm.focus();
    var range = document.createRange();
    range.selectNodeContents(pm);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);
    var dt = new DataTransfer();
    dt.setData('text/html', {json.dumps(text_html)});
    pm.dispatchEvent(new ClipboardEvent('paste', {{
        bubbles: true, cancelable: true, clipboardData: dt
    }}));
    return 'OK';
}})()
""")
```

#### Phase 2: Insert Images at Correct Positions

**CRITICAL:** Images must be inserted at the correct positions, not appended. Use anchor text to find the right DOM node, position the cursor AFTER it, then paste the image blob.

##### Step 2a: Build Image Position Map

```python
positions = []
for match in re.finditer(r'<img[^>]*src="data:image/[^;]+;base64,([^"]+)"[^>]*/?>',  html):
    before_html = html[:match.start()]
    paras = re.findall(r'>([^<]{20,})<', before_html)
    anchor = paras[-1].strip()[:60] if paras else ''
    positions.append((len(positions), anchor))
```

##### Step 2b: For Each Image, Position Cursor and Paste

```python
import base64, time

for img_index, anchor_text in positions:
    # 1. Find anchor and position cursor
    evaluate(f"""
    (function(){{
        var pm = document.querySelector('.ProseMirror');
        var s0 = pm.querySelector('section');
        var kids = Array.from(s0.children);
        var target = null;
        for (var i = 0; i < kids.length; i++) {{
            if (kids[i].textContent.includes({json.dumps(anchor_text)})) {{
                target = kids[i];
            }}
        }}
        if (!target) return 'ANCHOR NOT FOUND';
        var range = document.createRange();
        range.selectNodeContents(target);
        range.collapse(false);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
        return 'CURSOR AT: ' + target.textContent.substring(0, 40);
    }})()
    """)

    evaluate("document.execCommand('insertParagraph')")

    # 2. Read and chunk-upload image
    with open(f'images/fig{img_index+1}.png', 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()

    CHUNK = 500000
    chunks = [b64[i:i+CHUNK] for i in range(0, len(b64), CHUNK)]
    evaluate("window._ic = [];")
    for i, chunk in enumerate(chunks):
        evaluate(f"window._ic[{i}] = '{chunk}';")

    # 3. Paste as blob
    evaluate("""
    (async function() {
        var b64 = window._ic.join(''); delete window._ic;
        var bin = atob(b64);
        var bytes = new Uint8Array(bin.length);
        for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
        var blob = new Blob([bytes], {type: 'image/png'});
        var file = new File([blob], 'fig.png', {type: 'image/png'});
        var dt = new DataTransfer();
        dt.items.add(file);
        document.querySelector('.ProseMirror').dispatchEvent(
            new ClipboardEvent('paste', {bubbles:true, cancelable:true, clipboardData:dt}));
        return 'PASTED';
    })()
    """, await_promise=True)

    time.sleep(5)  # Wait for WeChat CDN upload
```

##### Step 2c: Clean Up Empty Placeholders

```python
evaluate("""
(function() {
    var pm = document.querySelector('.ProseMirror');
    var imgs = pm.querySelectorAll('img');
    var removed = 0;
    Array.from(imgs).forEach(function(img) {
        if (!img.src || img.src.length < 10) { img.remove(); removed++; }
    });
    return 'Removed ' + removed + ' empty placeholders';
})()
""")
```

#### Phase 3: Verify Images

**MANDATORY.** Count images in editor and compare to expected count. FAIL if mismatch.

```python
result = evaluate("""
(function() {
    var pm = document.querySelector('.ProseMirror');
    var imgs = pm.querySelectorAll('img[src]');
    var real = Array.from(imgs).filter(function(i) { return i.src.length > 10; });
    var positions = real.map(function(img) {
        var p = img.closest('section, p, div');
        var text_before = '';
        if (p && p.previousElementSibling) {
            text_before = p.previousElementSibling.textContent.substring(0, 40);
        }
        return text_before;
    });
    return JSON.stringify({count: real.length, positions: positions});
})()
""")
```

#### Phase 4: Set Title, Author, Cover, Save

```python
# Title (textarea as of 2026-02)
evaluate("""
(function(){
    var ta = document.querySelector('textarea');
    if(!ta) return 'NO_TEXTAREA';
    var setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
    setter.call(ta, 'Your Title');
    ta.dispatchEvent(new Event('input', {bubbles:true}));
    ta.dispatchEvent(new Event('change', {bubbles:true}));
    return 'TITLE_SET';
})()
""")

# Save as draft
evaluate("""
var btns = document.querySelectorAll('button');
for (var b of btns) {
    if (b.textContent.includes('保存为草稿')) { b.click(); break; }
}
""")

# Wait for save confirmation (CRITICAL)
for i in range(30):
    time.sleep(1)
    status = evaluate("document.body.innerText")
    if "已保存" in status:
        print("Save successful!")
        break
    if "保存失败" in status:
        print("Save failed!")
        break
```

For cover image, use "从正文选择":
1. Click the cover selection link
2. Wait for dialog with thumbnail images
3. Click the first thumbnail
4. Click "下一步" → dismiss warnings → "确认"

---

## Important Notes (Both Paths)

- **ProseMirror, not UEditor:** The visible editor is `.ProseMirror`, not `#edui1_contentplaceholder`.
- **Base64 images DO NOT survive save.** Must use clipboard blob paste — WeChat auto-uploads to CDN (`mmbiz.qpic.cn`).
- **Image position is cursor-determined.** Position cursor at the correct DOM node BEFORE pasting each image. Use anchor text matching.
- **Insert images in REVERSE ORDER** (last image first) to avoid index shifts. Or re-query the DOM after each insertion.
- **Each blob paste may create 1 real + 1 empty img.** Always clean up empty placeholders before saving.
- **Security warning:** Chrome extensions may trigger "浏览器插件存在安全隐患" — dismiss with "我知道了".
- **Session tokens expire:** Token in URL (e.g. `token=1829963357`) expires after ~2 hours of inactivity. Check token validity before starting injection. If expired, user must re-scan QR code.
- **Title field changed:** As of 2026-02, the title field is a `<textarea>`, not an `<input>` or contenteditable div. Use `HTMLTextAreaElement.prototype.value` setter.

### Choosing Your Path

| Condition | Use |
|-----------|-----|
| OpenClaw on macOS with built-in browser | **Path A** (browser tool) |
| Standalone Chrome on Linux/remote | **Path B** (direct CDP) |
| Linux/Ubuntu server | **Path B** |
| Titan (macOS) | **Path A** |
| Need screenshots for user | Both paths support this |

---

## Path C: WeChat Official Account API (推荐 — No Browser Required)

When the WeChat Official Account appid + appsecret are available, **skip the browser entirely**. The `draft/add` API works for both verified and unverified subscription accounts (订阅号). No QR code scan, no browser session, no DOM fragility.

**Check for credentials first:**
```bash
cat ~/.wechat-article-writer/secrets.json  # {"appid": "wx...", "appsecret": "..."}
```
If the file exists, use Path C. Otherwise fall back to Path A or B.

### Step 1: Get Access Token

```python
import json, requests, os
creds = json.load(open(os.path.expanduser("~/.wechat-article-writer/secrets.json")))
resp = requests.get(
    "https://api.weixin.qq.com/cgi-bin/token",
    params={"grant_type": "client_credential", "appid": creds["appid"], "secret": creds["appsecret"]},
    timeout=30
)
access_token = resp.json()["access_token"]  # valid 7200 seconds
```

### Step 2: Upload Images to WeChat CDN

WeChat blocks external image URLs. All `<img>` sources must be WeChat CDN URLs.

```python
# For article body images (temporary URL, use in <img src="...">):
with open("images/img1.png", "rb") as f:
    r = requests.post(
        "https://api.weixin.qq.com/cgi-bin/media/uploadimg",
        params={"access_token": access_token},
        files={"media": ("img1.png", f, "image/png")}, timeout=60
    )
wx_img_url = r.json()["url"]   # http://mmbiz.qpic.cn/...

# For cover (permanent, needed as thumb_media_id):
with open("images/cover.png", "rb") as f:
    r = requests.post(
        "https://api.weixin.qq.com/cgi-bin/material/add_material",
        params={"access_token": access_token, "type": "image"},
        files={"media": ("cover.png", f, "image/png")}, timeout=60
    )
thumb_media_id = r.json()["media_id"]
```

### Step 3: Clean Article HTML

WeChat requires a clean HTML fragment (no `<html>/<head>/<body>` tags):

```python
import re
with open("formatted.html") as f:
    raw = f.read()
body_match = re.search(r'<body[^>]*>(.*)</body>', raw, re.DOTALL | re.IGNORECASE)
content = body_match.group(1).strip() if body_match else raw
content = re.sub(r'<meta[^>]+>', '', content)
content = re.sub(r'<div>Preview build:[^<]+</div>', '', content)
content = re.sub(r' style="[^"]{100,}"', '', content)   # drop verbose inline styles
content = re.sub(r'</?section[^>]*>', '', content)       # unwrap <section> tags
content = re.sub(r'\n\s*\n', '\n', content).strip()
```

### Step 4: Create Draft

> ⚠️ **CRITICAL: Always use `ensure_ascii=False`**
>
> `requests(..., json=payload)` internally calls `json.dumps(ensure_ascii=True)`, which escapes Chinese as `\u5199\u4e66`. The WeChat editor renders these escape sequences **literally** — the article shows gibberish. Always use `data=json.dumps(..., ensure_ascii=False).encode("utf-8")`.

```python
payload = {
    "articles": [{
        "title": "文章标题",          # see field limits below — ≤18 Chinese chars!
        "author": "作者",             # ≤2 Chinese chars (≤8 bytes)
        "digest": "文章摘要",
        "content": content,
        "content_source_url": "https://github.com/...",
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 1,
        "only_fans_can_comment": 0
    }]
}

body = json.dumps(payload, ensure_ascii=False).encode("utf-8")  # ← MUST be this
resp = requests.post(
    "https://api.weixin.qq.com/cgi-bin/draft/add",
    params={"access_token": access_token},
    data=body,
    headers={"Content-Type": "application/json; charset=utf-8"},
    timeout=60
)
media_id = resp.json()["media_id"]
```

### ⚠️ Undocumented Field Limits (discovered 2026-02-28)

Official docs are wrong. Empirically confirmed limits for unverified subscription accounts:

| Field | Documented | **Actual Limit** | Notes |
|-------|-----------|-----------------|-------|
| `title` | 64 chars | **≤18 chars** (≤36 bytes) | 18 works, 19 fails — binary-search confirmed |
| `author` | 8 chars | **≤8 bytes** (≤2 Chinese chars, ~4 ASCII) | `廖春` (6b) ✓, `廖春华` (9b) ✗ |
| `digest` | 120 chars | **~28 Chinese chars** | Test for your account |
| `content` | 20,000 bytes | **~18KB UTF-8** | Chinese = 3 bytes/char; strip styles to reduce |

**Error codes lie.** `errcode 45003` says "title size out of limit" but often means content too large. `errcode 45110` says "author size out of limit" but can be triggered by content size. Test fields independently.

**Title workaround:** The API title is just for draft box display. Edit it to the full version in the WeChat editor UI (no size limit there) before publishing.

### Full Script

```bash
python3 scripts/publish_via_api.py \
  --draft-dir ~/.wechat-article-writer/drafts/<slug> \
  --title "草稿标题（≤18字）" \
  --author "作者" \
  --source-url "https://..."
```

### Path C vs A/B

| | Path A (Browser Tool) | Path B (Direct CDP) | **Path C (API)** |
|-|----------------------|---------------------|-----------------|
| Requires browser session | ✓ | ✓ | **✗** |
| Works headless | ✗ | ✓ | **✓** |
| Needs appid + secret | ✗ | ✗ | **✓** |
| Title limit | No limit | No limit | ≤18 Chinese chars |
| Image workflow | Clipboard blob paste | Clipboard blob paste | Pre-upload to CDN |
| Reliability | Medium (DOM changes) | Medium (session expiry) | **High** |
