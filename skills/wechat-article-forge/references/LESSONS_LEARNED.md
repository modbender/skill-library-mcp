# WeChat Publishing 经验教训

> **Platform key:** Lessons marked **(macOS only)** apply when OpenClaw manages the browser via Playwright (e.g. Titan). Lessons marked **(Linux/Ubuntu)** apply to standalone Chrome with direct CDP (e.g. headless Ubuntu server). Unmarked lessons apply to **both platforms**.

---

## 2026-02-26: OpenClaw Browser Tool vs Direct CDP **(macOS only)**

### Problem: Cannot bypass OpenClaw's browser tool on Titan

**Symptom:** Python WebSocket, Playwright `connect_over_cdp`, and raw socket CDP connections all fail to see any pages on port 18800.

**Root cause:** OpenClaw's built-in Chromium uses Playwright, which isolates page contexts. The CDP endpoint exists but:
- `/json/list` returns empty array
- `Target.getTargets` returns 0 targets
- `Target.setDiscoverTargets(true)` fires no events
- External Playwright `connect_over_cdp` sees 0 pages (different context)
- WebSocket without Origin header gets 101 handshake but zero targets

**Solution:** Use OpenClaw's `browser(action=act, request={kind:"evaluate", fn:...})` exclusively. All JS execution goes through this tool. See `browser-automation.md` Path A.

**Lesson:** On machines where OpenClaw manages the browser (macOS default), you are locked into the browser tool. Plan your automation around its constraints (string escaping, no persistent variables across calls unless stored in `window`).

**Does NOT apply to:** Ubuntu/Linux with standalone Chrome launched via `google-chrome-stable --remote-debugging-port=18800 --remote-allow-origins='*'`. Direct CDP WebSocket works fine there (Path B).

---

### Problem: HTML injection fails due to escaping hell **(macOS only — browser tool path)**

**Symptom:** `browser(action=act, request={kind:"evaluate", fn:"..."})` breaks when `fn` contains HTML with quotes, angle brackets, or backslashes.

**Root cause:** The `fn` string goes through multiple serialization layers: JSON (tool call) → JSON (browser protocol) → JS evaluation. Nested quotes and special characters break at each layer.

**Solution: Base64 encoding.**
1. Base64-encode the HTML in shell (`base64 -i file.html | tr -d '\n'`)
2. Store base64 string in page context via `window._b` (chunk if >3500 chars)
3. Decode with `atob(window._b)` in the evaluate call
4. Inject decoded HTML via `ClipboardEvent('paste', {clipboardData: dt})`

**Key finding:** `fn` parameter accepts 3500+ chars with no observed limit. Base64 alphabet (A-Z, a-z, 0-9, +, /, =) has zero escaping conflicts.

**Lesson:** For any complex string injection through browser tool, always base64-encode first. Never try to embed raw HTML/JSON in the fn parameter.

**On Ubuntu (Path B):** This is not an issue. Python `evaluate()` passes the expression string directly over WebSocket with `json.dumps()`, which handles escaping correctly in one layer. You can embed raw HTML in `json.dumps(text_html)` without base64.

---

### Problem: Title field selector changed **(both platforms)**

**Symptom:** Title not being set despite code running without errors.

**Root cause:** WeChat editor's title field changed from `<input>` / contenteditable div to `<textarea>` (as of 2026-02).

**Solution:** Use `HTMLTextAreaElement.prototype.value` setter:
```javascript
var setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
setter.call(textarea, 'title');
textarea.dispatchEvent(new Event('input', {bubbles: true}));
textarea.dispatchEvent(new Event('change', {bubbles: true}));
```

**Lesson:** WeChat's editor DOM changes without notice. Always verify selectors before assuming they work. Take a snapshot first and inspect the actual DOM structure.

---

### Problem: Mixed content blocking **(both platforms)**

**Symptom:** Attempted to serve images from local HTTP server and load via `<img src="http://localhost:8899/...">` in the HTTPS WeChat editor page. Images silently fail to load.

**Root cause:** Browsers block HTTP resources on HTTPS pages (mixed content policy). mp.weixin.qq.com is HTTPS.

**Solution:** Use clipboard blob paste for images instead of URL references. Read image → base64 encode → create Blob in page context → paste via ClipboardEvent.

**Lesson:** Never attempt to inject local server URLs into HTTPS pages. Always use blob/data methods.

---

## 2026-02-26: Cost Optimization Discovery **(both platforms)**

### Z.AI (GLM-Image) vs OpenRouter GPT-4o for Illustrations

| Provider | Cost per image | 4 images | Chinese text accuracy |
|----------|---------------|----------|----------------------|
| Z.AI (GLM-Image) | ~$0.015 | ~$0.06 | 97.9% |
| OpenRouter (GPT-4o) | ~$0.12 | ~$0.50 | 50-90% (unstable) |

**Result:** Z.AI is ~8x cheaper AND produces better Chinese text. Updated default in SKILL.md and figure-generation-guide.md.

---

## 2026-02-26: Pipeline State Gaps **(both platforms)**

### Problem: No resume granularity within publishing phase

**Symptom:** If session compacts during the multi-step browser injection (chunk storage, decode, inject, images, save), there's no way to resume from mid-injection. The entire publishing phase must restart.

**Solution:** Added sub-phase tracking in `pipeline-state.json`:
- `publishing_sub: "preparing"` — opening editor, verifying login
- `publishing_sub: "chunking"` — storing base64 chunks (`chunks_stored: N`) **(Path A only)**
- `publishing_sub: "text_injected"` — HTML content injected
- `publishing_sub: "images_inserting"` — inserting images (`images_inserted: N`)
- `publishing_sub: "images_done"` — all images inserted and verified
- `publishing_sub: "saving"` — save button clicked, waiting for confirmation

---

## 2026-02-23: Original Lessons

### 1. Chrome CDP needs `--remote-allow-origins=*` **(Linux/Ubuntu only)**

WebSocket connections get 403 without this flag. Required for Path B (direct CDP). Not relevant for Path A (browser tool handles the connection internally).

### 2. Save must wait for confirmation **(both platforms)**

Never navigate away after clicking save. Poll for "已保存" / "保存失败" for up to 30 seconds.

### 3. Remote server browser visibility **(Linux/Ubuntu only)**

Users can't see Chrome on a remote Linux server. Options:
- Take screenshots and send to user for verification
- `--headless=new` mode with screenshot-based workflow
- VNC or X11 forwarding for user to see browser
- User runs Chrome locally and uses Browser Relay

### 4. WeChat session expiry **(both platforms)**

Token expires after ~2 hours of inactivity. Check before starting injection. User must re-scan QR code if expired. On Linux, the QR code appears in the Chrome window (needs DISPLAY or VNC). On macOS, the browser tool can take a screenshot to share.

### 5. Image insertion via clipboard blob paste works reliably **(both platforms)**

Confirmed working pattern: find anchor → position cursor → insertParagraph → paste blob → wait for CDN upload (3-5s).

### 6. `DISPLAY` variable required **(Linux/Ubuntu only)**

Chrome needs `DISPLAY=:1` (or whichever X display is active) on headless Linux. Without it, Chrome won't start. Common setup: `Xvfb :1 -screen 0 1920x1080x24 &` then `export DISPLAY=:1`.

---

## Checklist: Before Publishing

- [ ] Token still valid? (check URL, try loading editor page)
- [ ] ProseMirror editor visible? (`document.querySelector('.ProseMirror')` not null)
- [ ] Which path? (Path A for OpenClaw browser tool on macOS, Path B for direct CDP on Linux)
- [ ] HTML base64 encoded and chunked? **(Path A only)**
- [ ] `--remote-allow-origins='*'` in Chrome launch args? **(Path B only)**
- [ ] DISPLAY variable set? **(Linux only)**
- [ ] All images exist locally? (`ls images/fig*.png`)
- [ ] Anchor texts extracted for image positioning?
- [ ] Title text prepared? (use textarea setter — both platforms)

---

## 2026-02-28: WeChat Official Account API as Path C **(both platforms)**

### Discovery: API Works for Unverified Accounts

**Symptom:** We assumed browser automation (Path A/B) was required because the account is an unverified subscription account (未认证订阅号).

**Finding:** The `cgi-bin/draft/add` API works fine for unverified accounts. The restriction on unverified accounts applies to *publishing* (send to followers) but not to *saving drafts*. The API-based path requires only appid + appsecret, both available in `~/.wechat-article-writer/secrets.json`.

**Lesson:** Always check for WeChat API credentials first. If available, skip the browser entirely.

---

### Problem: Chinese text displays as `\u5199\u4e66` escape sequences in WeChat editor

**Symptom:** Article opens in WeChat editor showing literal text like `\u591a\u667a\u80fd\u4f53\u6846\u67b618\u5c0f\u65f6` instead of `多智能体框架18小时`.

**Root cause:** `requests.post(..., json=payload)` internally uses `json.dumps(ensure_ascii=True)` (Python default). This converts all non-ASCII characters to `\uXXXX`. WeChat's editor renders the raw escape sequences as text, not as Unicode characters.

**Solution:** Encode manually with `ensure_ascii=False`:
```python
body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
resp = requests.post(url, data=body, headers={"Content-Type": "application/json; charset=utf-8"})
```

**Lesson:** Never use `requests(..., json=...)` for any WeChat API call containing Chinese text. Always use `data=json.dumps(..., ensure_ascii=False).encode("utf-8")`.

---

### Problem: WeChat API field limits are much stricter than documented

**Symptom:** `draft/add` returns `errcode 45003 "title size out of limit"` even with a 28-character title, and `errcode 45110 "author size out of limit"` even with a 3-character author.

**Finding (empirically confirmed via binary search, 2026-02-28):**

| Field | Documented | **Actual** |
|-------|-----------|-----------|
| `title` | 64 chars | **18 chars** (36 bytes) |
| `author` | 8 chars | **8 bytes** (2 Chinese chars) |
| `digest` | 120 chars | **~28 Chinese chars** |
| `content` | 20,000 bytes | **~18KB UTF-8** |

**Complication:** Error codes are not reliable indicators of which field is the problem. `45003` and `45110` both appeared for content-size issues. Always test fields independently to isolate the real cause.

**Workaround:** Use a short API title (≤18 chars) for the draft box. Edit it to the full title in the WeChat editor UI before publishing — the UI has no such restriction.

**Lesson:** Document these real limits. When any `45xxx` error appears, do a binary-search test on each field independently before concluding which field is at fault.

---

### Problem: Z.AI CDN download returns 404 immediately after generation

**Symptom:** `generate.py` calls Z.AI API → gets a `https://mfile.z.ai/...` URL → requests.get returns 404.

**Root cause:** Z.AI generates the image asynchronously; the CDN URL is valid but the file isn't propagated yet at the moment the download starts.

**Solution:** Retry with delay:
```python
for attempt in range(6):
    time.sleep(4)  # wait before each attempt
    r = requests.get(img_url, timeout=60)
    if r.status_code == 200:
        with open(out_path, "wb") as f:
            f.write(r.content)
        break
```

**Lesson:** Always wrap Z.AI CDN downloads in a retry loop with ≥3 second delay. 4 seconds + 5 retries is reliable in practice.

---

## Checklist Update: Path C Pre-flight

- [ ] `~/.wechat-article-writer/secrets.json` exists with `appid` + `appsecret`?
  - Yes → use Path C
  - No → fall back to Path A (macOS) or Path B (Linux)
- [ ] Access token fetched and valid (not expired)?
- [ ] All images uploaded to WeChat CDN (`media/uploadimg`)? Save URLs in `wechat_image_urls.json`.
- [ ] Cover image uploaded as permanent material? Save `thumb_media_id`.
- [ ] Content cleaned: no `<meta>`, no `<body>`, no `Preview build` banner, no verbose `style="..."`?
- [ ] Content size under ~18KB (UTF-8 bytes)?
- [ ] Title ≤ 18 Chinese chars?
- [ ] Author ≤ 2 Chinese chars (or ≤ 4 ASCII chars)?
- [ ] Using `ensure_ascii=False` in JSON encoding?

---

## 2026-03-01: 预览服务器 (Preview Server) **(both platforms)**

### Problem: 预览链接反复打不开 — 临时服务器反复挂掉

**症状：** 每次调用 `format.sh` 后发一个预览链接，用户反映链接打不开；重启后能用，下次又不行。在整个写作流程里发生了十数次。

**根本原因：** 预览服务器是在 exec 命令里用 `&` 启动的，每次都是重新 kill 然后重启。问题有三层：
1. **不稳定生命周期** — 服务器作为 exec shell 的子进程启动，exec 会话结束后偶尔被杀死
2. **人工介入依赖** — 每次 `format.sh` 之后都要手动重启服务器，忘记或者时序不对就没法访问
3. **端口绑定方式** — 绑到了具体的 Tailscale IP (`<your-tailscale-ip>`) 而非 `0.0.0.0`，IP 变动就挂

**错误做法（不要这样做）：**
```bash
# ❌ 每次 format 后 kill + 重启
kill $(lsof -ti:8898) 2>/dev/null
python3 -m http.server 8898 --bind <your-tailscale-ip> &
```

**正确做法：做成 systemd 用户服务，永久运行，自动重启。**

**一次性设置步骤：**

1. 创建服务器脚本 `~/.wechat-article-writer/preview_server.py`：
```python
#!/usr/bin/env python3
import http.server, os

SERVE_DIR = os.path.expanduser("~/.wechat-article-writer/drafts/wechat-article-writer-deep-dive")
PORT = 8898

class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        super().end_headers()
    def log_message(self, fmt, *args):
        pass

os.chdir(SERVE_DIR)
http.server.HTTPServer(("0.0.0.0", PORT), NoCacheHandler).serve_forever()
```

2. 创建 systemd 服务 `~/.config/systemd/user/wechat-preview.service`：
```ini
[Unit]
Description=WeChat Article Preview Server (port 8898)
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $HOME/.wechat-article-writer/preview_server.py
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
```

3. 启用并启动：
```bash
systemctl --user daemon-reload
systemctl --user enable wechat-preview.service
systemctl --user start wechat-preview.service
```

4. 验证：
```bash
systemctl --user status wechat-preview.service
curl -I http://<your-tailscale-ip>:8898/formatted.html
```

**服务特性：**
- 绑定 `0.0.0.0:8898`（所有网口，包括 Tailscale）
- `Cache-Control: no-store, no-cache` — 每次 format 后直接刷新即可，无需 hard refresh
- `Restart=always` — 崩溃自动重启，无需人工干预
- `enabled` — 开机自启

**format.sh 的正确做法：**
- format.sh **不得** kill 或重启预览服务器
- format.sh 输出的 HTML 里有 "Preview build" 时间戳，配合 no-cache 头，浏览器直接刷新即可看到最新内容

**诊断命令（当链接打不开时）：**
```bash
# 1. 服务还在吗？
systemctl --user status wechat-preview.service

# 2. 端口在监听吗？
ss -tlnp | grep 8898

# 3. 本地可达吗？
curl -I http://<your-tailscale-ip>:8898/formatted.html

# 4. 如果服务挂了，重启：
systemctl --user restart wechat-preview.service
```

**Lesson：** 任何需要"持续可访问"的 HTTP 服务，必须用 systemd 服务管理，不能用 exec 临时启动。exec 进程生命周期不可预测，不适合做服务基础设施。

---

## 2026-03-01: 排版主题 (wenyan Theme) **(both platforms)**

### Problem: 默认主题太素，公众号效果差

**症状：** format.sh 生成的预览和发布到微信的文章排版很平淡，没有视觉层次感。

**根本原因：** format.sh 调用 `wenyan render` 时没有传 `-t` 参数，永远使用 `default` 主题（最素的）。`skill.yml` 里有 `default_theme: condensed` 配置，但 format.sh 完全没读取它；而且 `condensed` 根本不是合法的 wenyan 主题。

**wenyan 可用主题：**
```
default        — 极简，几乎没有样式（不推荐）
pie            — sspai 风格，现代精致，适合科技/深度内容 ✅ 推荐
lapis          — 蓝调极简，清爽
orangeheart    — 暖橙，适合情感/生活类内容
rainbow        — 彩色活泼
maize          — 柔和麦色
purple         — 紫色简约
phycat         — 薄荷绿，结构清晰
```

**修复：**
```bash
# format.sh 现在默认使用 pie 主题
cat "$DRAFT_PATH" | wenyan render -t pie > "$RAW_HTML"

# 也可以在调用时传主题参数
bash format.sh <draft-dir> draft-v4.md lapis
```

**Lesson：** 排版工具的默认选项往往是最保守的，不代表最佳选择。新部署时应明确测试 2-3 个主题，选出最适合内容调性的，写入 format.sh 默认值。

