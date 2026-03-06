---
name: ztpc-spam-sweep
description: Use a persistent OpenClaw browser profile to access
  http://mail.ztpc.com/ (Aliyun Enterprise Mail), scan UNREAD emails only, and
  conservatively mark obvious spam / phishing as Spam (never delete). ...
---

# ztpc-spam-sweep
## Purpose
Use a persistent OpenClaw browser profile to access **http://mail.ztpc.com/** (Aliyun Enterprise Mail),
scan **UNREAD** emails only, and conservatively mark obvious spam / phishing as **Spam** (never delete).
The skill's final message to the user MUST be **Chinese** and **short** (summary only).

> Key constraint: This mailbox may sometimes require captcha/SMS/2FA.
> - Captcha / slider / click-to-verify: always stop and report that manual verification is required.
> - SMS 2FA: if `interactive_2fa=true` (human-in-the-loop), you may request the code from the user and continue; otherwise stop.

---

## Invocation / Inputs
Invoke as:
`/skill mail-spam-sweep {"dry_run": true|false, "max": <int>, "interactive_2fa": true|false}`

- `dry_run` (default: `false`):
  - `true`: evaluate and report only; **do not** click "Mark as spam".
  - `false`: mark decided SPAM emails as spam (no deletion).
- `max` (default: `20`, hard cap: `50`): max number of **unread** emails to evaluate.
- `interactive_2fa` (default: `false`):
  - `false` (recommended for cron/unattended runs): if SMS/2FA is required, STOP and report manual verification needed.
  - `true` (interactive runs only): if SMS/2FA page appears, the skill may:
    1) click "Send Verification Code",
    2) ask the user to provide the SMS code (usually 6 digits, valid ~5 minutes),
    3) fill the code and proceed,
    4) tick "trusted device" if available to reduce future prompts.

---

## Required files
### 1) secrets.json (required)
Path:
`~/.openclaw/workspace/skills/ztpc-spam-sweep/secrets.json`

Format:
```json
{"username":"ztpc@ztpc.com","password":"YOUR_PASSWORD"}
```

Rules:
- Never print the secret values.
- If secrets.json is missing or invalid -> stop with Chinese status message.

### 2) allowlist.txt (optional but strongly recommended)
Path:
`~/.openclaw/workspace/skills/ztpc-spam-sweep/allowlist.txt`

Format: one entry per line (domain or full email). `#` starts a comment.
Example:
```
# trusted domains
ztpc.com
cnpe.cc
cgnpc.com.cn
```

Matching rule:
- If sender email matches an allowlisted **email**, or sender domain matches an allowlisted **domain**,
  the message is **NEVER** treated as spam (unless explicit blocklist match).

### 3) blocklist.txt (optional)
Path:
`~/.openclaw/workspace/skills/ztpc-spam-sweep/blocklist.txt`

Format: one entry per line (domain or full email). `#` starts a comment.

Matching rule:
- If sender email/domain matches blocklist -> SPAM (highest priority).

---

## HARD RULES (must follow)
1. Always reuse the SAME persistent browser profile:
   - Use OpenClaw's configured `defaultProfile` (recommended: `openclaw`).
   - Do NOT use a temporary/clean profile.
2. **Only scan UNREAD** messages.
   - Do NOT iterate the whole Inbox.
   - Do NOT open every email; rely on the mail list row fields (sender/subject/preview/flags).
3. Never delete emails. The only destructive action allowed is:
   - Mark as spam / move to spam folder.
4. Verification handling:
   - If the login flow requires **captcha / slider / click-to-verify** => STOP and report in Chinese:
     `状态：需要人工验证（验证码/二次验证）`
   - If the login flow requires **SMS 2FA**:
     - If `interactive_2fa=true`: proceed with human-in-the-loop SMS code entry (see Step 1).
     - Else: STOP and report:
       `状态：需要人工验证（验证码/二次验证）`
5. Final output must be a **single Chinese report** (no step-by-step narration).
6. Never output credentials or any sensitive data.

---

## Spam / Phishing decision policy (supports Chinese + English)
### Priority order
1) **Blocklist hit** -> SPAM
2) **Allowlist hit** -> NOT SPAM (skip)
3) Otherwise -> apply heuristic rules below.

### A. Strong-evidence rules (SPAM immediately)
Mark as SPAM if ANY of the following is true:

**A1. Brand / authority impersonation + mismatch**
- Sender display name contains authority keywords (examples below),
  AND sender domain is NOT clearly matching that authority context.

Authority keywords (Chinese/English examples):
- Chinese: `管理员`, `安全中心`, `客服`, `官方`, `银行`, `税务`, `法院`, `公安`, `财务`, `出纳`, `人事`, `IT`, `邮箱`, `系统`
- English: `admin`, `security`, `support`, `official`, `bank`, `tax`, `court`, `police`, `finance`, `hr`, `it`

**A2. Financial / process hijack / urgent secrecy**
Subject or preview contains patterns like:
- `紧急`, `立即`, `限时`, `最后一次`, `逾期`, `冻结`, `异常`, `验证`, `认证`, `升级`, `重新登录`, `安全提醒`
AND at least one of:
- `转账`, `付款`, `汇款`, `收款账户变更`, `开票信息变更`, `财务指令`, `保密`, `不要走流程`
OR a suspicious link/download instruction:
- `点击链接`, `下载`, `附件查看`, `打开文件`

**A3. Obvious scam / phishing template**
- “领导让我联系你/马上转账/不要告诉别人/保密/紧急付款”
- “司法/公安/法院/税务通知，要求点击链接或下载附件”
- “工资/补贴/报销异常，需要重新认证/登录验证”

**A4. Non-business mass marketing pattern**
- Subject contains heavy marketing/lottery keywords AND sender is unknown/untrusted:
  `中奖`, `返利`, `贷款`, `低息`, `套现`, `博彩`, `娱乐城`, `发票代开`, `代开发票`, `刷单`, `兼职日结`, `理财高收益`, `稳赚`
  (Treat as SPAM unless allowlisted.)

### B. Scoring rules (for borderline Chinese spam/phishing)
If no strong-evidence rule hit, compute a risk score from subject + preview + sender signals.

Score additions (examples):
- (+3) Contains: `点击链接|登录验证|重新认证|过期|异常|冻结|升级|安全提醒`
- (+2) Contains: `紧急|立即|限时|最后一次提醒|逾期`
- (+2) Contains finance-ish tokens: `账单|发票|报销|付款|转账|合同款|对账`
- (+2) Has attachment indicator AND sender not allowlisted
- (+3) Sender appears to be free email (`qq.com|163.com|126.com|gmail.com|outlook.com`) while claiming authority keywords
- (+1) Sender appears "new/unknown" (cannot be verified; default +1 when not allowlisted)

Score reductions:
- (SKIP) Allowlist hit => NOT SPAM (handled earlier)
- (-2) Subject contains obvious internal/project keywords AND sender domain looks corporate
  (Examples: `联系单`, `函`, `函件`, `项目部`,`月报`, `周报`, `日报`)

Decision threshold:
- score >= **6** => SPAM
- else => NOT SPAM / UNCERTAIN (leave untouched)

> This is intentionally conservative; tune thresholds/keywords by editing this file and your allowlist.

---

## Procedure (browser automation)
### Step 0: Setup
- Read `secrets.json`.
- Load allowlist/blocklist if present.

### Step 1: Open and login
1. Open browser using the persistent OpenClaw profile.
2. Navigate to `http://mail.ztpc.com/`.
3. Detect whether already logged in:
   - If the UI shows mailbox main layout (folders like 收件箱/未读邮件/垃圾邮件 etc) => logged in.
   - Else, if login iframe/panel is visible => proceed to login.
4. Login (if needed):
   - Fill username + password from `secrets.json`.
   - Click 登录.
   - If login fails with “用户名或密码错误” => STOP and report:
     `状态：登录失败（账号或密码错误）`
   - If a captcha / slider / click-to-verify appears (e.g. “请输入验证码” + image, sliding puzzle, click-confirm) => STOP and report:
     `状态：需要人工验证（验证码/二次验证）`
   - If an **SMS/2FA** page appears (e.g. "Authentication", "SMS", "Send Verification Code", masked mobile number):
     - If `interactive_2fa=false` => STOP and report:
       `状态：需要人工验证（验证码/二次验证）`
     - If `interactive_2fa=true` (interactive runs only):
       1) Click **Send Verification Code**.
       2) Prompt the user (in Chinese) to provide the SMS code (typically 6 digits; valid ~5 minutes).
       3) Fill the code into the input (e.g. textbox "Please input").
       4) If present, tick **Set as a trusted device** (or equivalent wording) to reduce future prompts.
       5) Click **Next** and wait for mailbox main UI.
       6) If still blocked by additional verification => STOP and report:
          `状态：需要人工验证（验证码/二次验证）`

### Step 2: Navigate to UNREAD ONLY
- Click the left folder **“未读邮件”** (or a dedicated Unread filter).
- Do NOT open “收件箱” list unless Unread folder is unavailable.
- If Unread folder is not found, try UI search/filter for unread.
- Cap evaluation to `max` items.

### Step 3: Extract rows (lightweight)
For each unread mail row (up to `max`):
- Extract at least:
  - sender display name
  - (if visible) sender email / domain
  - subject
  - preview snippet (one-line)
  - attachment indicator (if visible)

IMPORTANT:
- Do NOT open the mail body unless necessary to find sender email/domain (prefer not to).
- If sender email/domain cannot be obtained from list view, decide using display name + subject + preview only.

### Step 4: Decide and act
For each row:
1. If allowlist match => keep (NOT SPAM).
2. Else if blocklist match => SPAM.
3. Else apply strong-evidence rules; if match => SPAM.
4. Else score; if score >= 6 => SPAM; else keep.

Action:
- If `dry_run=true`: do not click spam; only record decisions.
- If `dry_run=false` and decided SPAM:
  - Select the message (checkbox or row select)
  - Click UI action to mark as spam / move to spam:
    - typically a “垃圾邮件” button or a “更多” menu -> “标记为垃圾邮件”
  - Ensure the UI action is “mark/move to spam”, not delete.

### Step 5: Final report (Chinese, strict)
Return exactly ONE final message with this structure:

```
✅ 状态：完成（dry_run=<true|false>, max=<N>）
🗑️ 垃圾邮件处理：<S> 封
- <发件人> — <主题>
...

⚠️ 非垃圾/不确定（未处理）：<K> 封
- <发件人> — <主题>
...
```

If stopped for manual verification:
```
⛔ 状态：需要人工验证（验证码/二次验证）
说明：检测到登录需要验证码/二次验证，请先在同一浏览器 profile 中手动完成一次验证，然后再次运行本技能。
```

If secrets missing:
```
⛔ 状态：缺少配置（secrets.json）
说明：请在 ~/.openclaw/workspace/skills/ztpc-spam-sweep/secrets.json 填写用户名与密码。
```

---

## Notes / Tuning tips
- **Most important**: keep your allowlist current for business domains to avoid false positives.
- If you see recurring spam from a stable domain/email, add it to `blocklist.txt`.
- This skill intentionally avoids reading the entire Inbox to reduce cost and noise.
