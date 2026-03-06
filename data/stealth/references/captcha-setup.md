# CAPTCHA Solver Setup

## Critical: Provider-Type Matrix

Using the wrong provider wastes money and fails silently.

| CAPTCHA | CapSolver | 2Captcha | Anti-Captcha |
|---------|-----------|----------|-------------|
| hCaptcha | ✅ | ❌ DROPPED | ✅ |
| reCAPTCHA v2 | ✅ | ✅ | ✅ |
| reCAPTCHA v3 | ✅ | ✅ | ✅ |
| Turnstile | ✅ | ✅ | ✅ |
| Image/text | ❌ | ✅ | ✅ |

**2Captcha removed hCaptcha support in late 2025.** Submitting hCaptcha tasks returns `ERROR_METHOD_CALL`. Do not retry — switch to CapSolver.

## CapSolver Setup

1. Sign up at capsolver.com
2. Dashboard → API Key
3. Fund account (minimum ~$1, accepts crypto + cards)

```bash
mkdir -p ~/.config/stealth
echo '{"provider":"capsolver","api_key":"CAP-xxx"}' > ~/.config/stealth/captcha.json
chmod 600 ~/.config/stealth/captcha.json
```

## 2Captcha Setup

1. Sign up at 2captcha.com
2. Dashboard → API Key
3. Fund account (minimum ~$1, accepts crypto + PayPal + cards)

```bash
echo '{"provider":"2captcha","api_key":"xxx"}' > ~/.config/stealth/captcha.json
chmod 600 ~/.config/stealth/captcha.json
```

## Solving Flow

### Step 1: Detect captcha type

Look in page source for:
- `hcaptcha.com/1/api.js` → hCaptcha
- `google.com/recaptcha/api.js` → reCAPTCHA
- `challenges.cloudflare.com` → Turnstile
- `<img>` with captcha-like src → Image captcha

Extract the `sitekey` (usually in a `data-sitekey` attribute or script config).

### Step 2: Submit to solver

**hCaptcha via CapSolver:**
```python
import requests, time

# Create task
resp = requests.post("https://api.capsolver.com/createTask", json={
    "clientKey": API_KEY,
    "task": {
        "type": "HCaptchaTaskProxyLess",
        "websiteURL": PAGE_URL,
        "websiteKey": SITEKEY
    }
}).json()
task_id = resp["taskId"]

# Poll for result
while True:
    time.sleep(3)
    result = requests.post("https://api.capsolver.com/getTaskResult", json={
        "clientKey": API_KEY, "taskId": task_id
    }).json()
    if result["status"] == "ready":
        token = result["solution"]["gRecaptchaResponse"]
        break
```

**reCAPTCHA v2 via 2Captcha:**
```python
import requests, time

# Submit
resp = requests.get(
    f"http://2captcha.com/in.php?key={API_KEY}&method=userrecaptcha"
    f"&googlekey={SITEKEY}&pageurl={PAGE_URL}&json=1"
).json()
captcha_id = resp["request"]

# Poll (wait 20s before first check)
time.sleep(20)
while True:
    result = requests.get(
        f"http://2captcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}&json=1"
    ).json()
    if result["status"] == 1:
        token = result["request"]
        break
    time.sleep(5)
```

**Cloudflare Turnstile via CapSolver:**
```python
resp = requests.post("https://api.capsolver.com/createTask", json={
    "clientKey": API_KEY,
    "task": {
        "type": "AntiTurnstileTaskProxyLess",
        "websiteURL": PAGE_URL,
        "websiteKey": SITEKEY
    }
}).json()
# Same polling as above
```

### Step 3: Inject token

**hCaptcha / reCAPTCHA:**
```javascript
// In browser context (Playwright/Puppeteer)
document.querySelector('[name="h-captcha-response"]').value = token;
document.querySelector('[name="g-recaptcha-response"]').value = token;
// Trigger callback if needed
window.hcaptcha?.getResponse && hcaptcha.submit();
// Or for reCAPTCHA:
___grecaptcha_cfg?.clients?.[0]?.aa?.l?.callback?.(token);
```

**Turnstile:**
```javascript
document.querySelector('[name="cf-turnstile-response"]').value = token;
// Submit the form
document.querySelector('form').submit();
```

### Step 4: Verify

After injection, submit the form or trigger the next action. If the page reloads with another CAPTCHA, the token may have expired (they're time-limited, typically 60-120 seconds). Re-solve and inject faster.
