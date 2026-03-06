---
name: capmonster
description: Solve CAPTCHAs (reCAPTCHA v2/v3, hCaptcha, Cloudflare Turnstile, image CAPTCHAs) using CapMonster Cloud API. Use when browser automation encounters CAPTCHA challenges.
---

# CapMonster Cloud CAPTCHA Solver

Solve CAPTCHAs programmatically via CapMonster Cloud API during browser automation.

## API Info

- **Base URL**: `https://api.capmonster.cloud`
- **API Key**: `${CAPMONSTER_API_KEY}`
- **Docs**: https://docs.capmonster.cloud/
- **Python Client**: `tools/capmonster-cloud/capmonster_api.py`

## Pricing (per 1000 solves)

| Type | Price | Avg Time |
|------|-------|----------|
| reCAPTCHA v2 | $0.60 | 10-30s |
| reCAPTCHA v3 | $0.90 | 5-15s |
| hCaptcha | $1.50 | 10-30s |
| Cloudflare Turnstile | $1.20 | 5-15s |
| Image CAPTCHA | $0.04 | 2-5s |

## Quick Reference

### Check Balance

```bash
curl -s -X POST https://api.capmonster.cloud/getBalance \
  -H "Content-Type: application/json" \
  -d '{"clientKey": "${CAPMONSTER_API_KEY}"}' | jq .balance
```

### Using Python Client

```python
import sys
sys.path.insert(0, '/Users/eason/clawd/tools/capmonster-cloud')
from capmonster_api import CapMonsterClient

client = CapMonsterClient("${CAPMONSTER_API_KEY}")

# Check balance
print(f"Balance: ${client.get_balance()}")

# Solve reCAPTCHA v2
token = client.solve_recaptcha_v2(
    website_url="https://example.com/page-with-captcha",
    website_key="6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"
)
```

---

## Complete Workflow: Browser Automation + CAPTCHA Solving

### Step 1: Detect CAPTCHA on Page

Take a browser snapshot and check for CAPTCHA indicators:

```javascript
// Via browser action=act evaluate
browser action=act profile=chrome request={
  "kind": "evaluate",
  "fn": "(() => {
    const indicators = {
      recaptchaV2: !!document.querySelector('.g-recaptcha, [data-sitekey], iframe[src*=\"recaptcha\"]'),
      recaptchaV3: !!document.querySelector('script[src*=\"recaptcha/api.js?render=\"]'),
      hcaptcha: !!document.querySelector('.h-captcha, [data-hcaptcha-sitekey], iframe[src*=\"hcaptcha\"]'),
      turnstile: !!document.querySelector('.cf-turnstile, [data-sitekey], iframe[src*=\"turnstile\"]')
    };
    return JSON.stringify(indicators);
  })()"
}
```

### Step 2: Extract Site Key

**reCAPTCHA v2:**
```javascript
// Option A: From data-sitekey attribute
document.querySelector('[data-sitekey]')?.dataset.sitekey

// Option B: From iframe src
document.querySelector('iframe[src*="recaptcha"]')?.src.match(/k=([^&]+)/)?.[1]

// Option C: From grecaptcha object
window.___grecaptcha_cfg?.clients?.[0]?.Y?.Y?.sitekey
```

**reCAPTCHA v3:**
```javascript
// From script src
document.querySelector('script[src*="recaptcha/api.js?render="]')?.src.match(/render=([^&]+)/)?.[1]

// Or from grecaptcha config
window.___grecaptcha_cfg?.clients?.[0]?.Y?.Y?.sitekey
```

**hCaptcha:**
```javascript
document.querySelector('[data-hcaptcha-sitekey], .h-captcha[data-sitekey]')?.dataset.sitekey ||
document.querySelector('[data-hcaptcha-sitekey]')?.getAttribute('data-hcaptcha-sitekey')
```

**Cloudflare Turnstile:**
```javascript
document.querySelector('.cf-turnstile[data-sitekey], [data-turnstile-sitekey]')?.dataset.sitekey
```

### Step 3: Submit to CapMonster API

**Using curl (shell):**

```bash
# Create task
TASK_ID=$(curl -s -X POST https://api.capmonster.cloud/createTask \
  -H "Content-Type: application/json" \
  -d '{
    "clientKey": "${CAPMONSTER_API_KEY}",
    "task": {
      "type": "RecaptchaV2TaskProxyless",
      "websiteURL": "https://scholar.google.com/",
      "websiteKey": "SITEKEY_HERE"
    }
  }' | jq -r .taskId)

echo "Task ID: $TASK_ID"
```

**Using Python:**

```python
import sys
sys.path.insert(0, '/Users/eason/clawd/tools/capmonster-cloud')
from capmonster_api import CapMonsterClient

client = CapMonsterClient("${CAPMONSTER_API_KEY}")

# For reCAPTCHA v2
token = client.solve_recaptcha_v2(
    website_url="https://scholar.google.com/",
    website_key="EXTRACTED_SITEKEY"
)

# For reCAPTCHA v3
token = client.solve_recaptcha_v3(
    website_url="https://example.com/",
    website_key="EXTRACTED_SITEKEY",
    min_score=0.7,
    page_action="submit"  # Check page source for action name
)

# For hCaptcha
token = client.solve_hcaptcha(
    website_url="https://example.com/",
    website_key="EXTRACTED_SITEKEY"
)

# For Turnstile
token = client.solve_turnstile(
    website_url="https://example.com/",
    website_key="EXTRACTED_SITEKEY"
)
```

### Step 4: Poll for Solution

**Using curl:**

```bash
# Poll until ready (max 120 seconds)
for i in {1..60}; do
  RESULT=$(curl -s -X POST https://api.capmonster.cloud/getTaskResult \
    -H "Content-Type: application/json" \
    -d "{\"clientKey\": \"${CAPMONSTER_API_KEY}\", \"taskId\": $TASK_ID}")
  
  STATUS=$(echo "$RESULT" | jq -r .status)
  
  if [ "$STATUS" = "ready" ]; then
    TOKEN=$(echo "$RESULT" | jq -r '.solution.gRecaptchaResponse // .solution.token')
    echo "Token: $TOKEN"
    break
  fi
  
  echo "Status: $STATUS, waiting..."
  sleep 2
done
```

The Python client handles polling automatically with `solve_and_wait()`.

### Step 5: Inject Solution into Page

**reCAPTCHA v2/v3:**

```javascript
// Via browser evaluate
browser action=act profile=chrome request={
  "kind": "evaluate",
  "fn": "(() => {
    const token = 'CAPMONSTER_TOKEN_HERE';
    
    // Method 1: Set textarea value (most common)
    const textarea = document.querySelector('#g-recaptcha-response, [name=\"g-recaptcha-response\"]');
    if (textarea) {
      textarea.value = token;
      textarea.style.display = 'block';  // Some sites hide it
    }
    
    // Method 2: Also set any iframe response
    document.querySelectorAll('iframe[src*=\"recaptcha\"]').forEach(iframe => {
      try {
        const doc = iframe.contentDocument || iframe.contentWindow.document;
        const ta = doc.querySelector('#g-recaptcha-response');
        if (ta) ta.value = token;
      } catch(e) {}
    });
    
    // Method 3: Trigger callback if exists
    if (typeof ___grecaptcha_cfg !== 'undefined') {
      const clients = ___grecaptcha_cfg.clients;
      for (let cid in clients) {
        const client = clients[cid];
        // Find callback
        const callback = client?.Y?.Y?.callback || client?.Y?.callback;
        if (typeof callback === 'function') {
          callback(token);
        }
      }
    }
    
    return 'Token injected';
  })()"
}
```

**hCaptcha:**

```javascript
browser action=act profile=chrome request={
  "kind": "evaluate",
  "fn": "(() => {
    const token = 'CAPMONSTER_TOKEN_HERE';
    
    // Set response textarea
    const textarea = document.querySelector('[name=\"h-captcha-response\"], [name=\"g-recaptcha-response\"]');
    if (textarea) textarea.value = token;
    
    // Trigger callback
    if (typeof hcaptcha !== 'undefined') {
      // Find widget ID
      const widget = document.querySelector('.h-captcha');
      const widgetId = widget?.dataset.hcaptchaWidgetId || 0;
      // Some sites have custom callbacks
    }
    
    return 'hCaptcha token injected';
  })()"
}
```

**Cloudflare Turnstile:**

```javascript
browser action=act profile=chrome request={
  "kind": "evaluate",
  "fn": "(() => {
    const token = 'CAPMONSTER_TOKEN_HERE';
    
    // Set the hidden input
    const input = document.querySelector('[name=\"cf-turnstile-response\"]');
    if (input) input.value = token;
    
    // Also set any callback data attribute
    const container = document.querySelector('.cf-turnstile');
    if (container && container.dataset.callback) {
      const callbackName = container.dataset.callback;
      if (typeof window[callbackName] === 'function') {
        window[callbackName](token);
      }
    }
    
    return 'Turnstile token injected';
  })()"
}
```

### Step 6: Submit the Form

After injecting the token, submit the form:

```javascript
// Click submit button
browser action=act profile=chrome request={"kind":"click","ref":"submit button ref"}

// Or trigger form submission
browser action=act profile=chrome request={
  "kind": "evaluate",
  "fn": "document.querySelector('form').submit()"
}
```

---

## Google Scholar Specific

Google Scholar uses **invisible reCAPTCHA v2** that triggers on suspicious activity.

### Detection

```javascript
// Check if blocked
const isBlocked = document.body.textContent.includes('unusual traffic') ||
                  document.body.textContent.includes('我們的系統') ||
                  !!document.querySelector('iframe[src*="recaptcha"]');
```

### Extract Site Key

```javascript
// Scholar's recaptcha iframe
const iframe = document.querySelector('iframe[src*="recaptcha"]');
const sitekey = iframe?.src.match(/k=([^&]+)/)?.[1];
// Usually: 6LfwuyUTAAAAAOAmoS0fdqijC2PbbdH4kjq62Y1b
```

### Solve and Submit

```python
import sys
sys.path.insert(0, '/Users/eason/clawd/tools/capmonster-cloud')
from capmonster_api import CapMonsterClient

client = CapMonsterClient("${CAPMONSTER_API_KEY}")

# Scholar's known sitekey (may change)
token = client.solve_recaptcha_v2(
    website_url="https://scholar.google.com/scholar?q=test",
    website_key="6LfwuyUTAAAAAOAmoS0fdqijC2PbbdH4kjq62Y1b"
)

print(f"Token: {token[:50]}...")
```

Then inject via browser automation.

---

## Image CAPTCHA

For traditional image CAPTCHAs (text recognition):

```python
import base64
import sys
sys.path.insert(0, '/Users/eason/clawd/tools/capmonster-cloud')
from capmonster_api import CapMonsterClient

client = CapMonsterClient("${CAPMONSTER_API_KEY}")

# From file
text = client.solve_image_captcha(image_path="/tmp/captcha.png")

# From base64
with open("/tmp/captcha.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
text = client.solve_image_captcha(image_base64=b64)

print(f"CAPTCHA text: {text}")
```

---

## All-in-One Shell Script

Save as `solve-recaptcha.sh`:

```bash
#!/bin/bash
# Usage: ./solve-recaptcha.sh <website_url> <sitekey>

API_KEY="${CAPMONSTER_API_KEY}"
WEBSITE_URL="$1"
SITEKEY="$2"

# Create task
echo "Creating task..."
RESPONSE=$(curl -s -X POST https://api.capmonster.cloud/createTask \
  -H "Content-Type: application/json" \
  -d "{
    \"clientKey\": \"$API_KEY\",
    \"task\": {
      \"type\": \"RecaptchaV2TaskProxyless\",
      \"websiteURL\": \"$WEBSITE_URL\",
      \"websiteKey\": \"$SITEKEY\"
    }
  }")

TASK_ID=$(echo "$RESPONSE" | jq -r .taskId)
ERROR_ID=$(echo "$RESPONSE" | jq -r .errorId)

if [ "$ERROR_ID" != "0" ]; then
  echo "Error: $(echo "$RESPONSE" | jq -r .errorDescription)"
  exit 1
fi

echo "Task ID: $TASK_ID"

# Poll for result
echo "Waiting for solution..."
for i in {1..60}; do
  RESULT=$(curl -s -X POST https://api.capmonster.cloud/getTaskResult \
    -H "Content-Type: application/json" \
    -d "{\"clientKey\": \"$API_KEY\", \"taskId\": $TASK_ID}")
  
  STATUS=$(echo "$RESULT" | jq -r .status)
  
  if [ "$STATUS" = "ready" ]; then
    TOKEN=$(echo "$RESULT" | jq -r '.solution.gRecaptchaResponse')
    COST=$(echo "$RESULT" | jq -r '.cost')
    echo "✅ Solved! Cost: \$$COST"
    echo ""
    echo "TOKEN:"
    echo "$TOKEN"
    exit 0
  fi
  
  printf "."
  sleep 2
done

echo ""
echo "❌ Timeout after 120 seconds"
exit 1
```

---

## Troubleshooting

### Token Invalid / Expired

- Tokens expire in ~2 minutes
- Inject and submit immediately after receiving
- Make sure `websiteURL` matches the actual page URL

### ERROR_CAPTCHA_UNSOLVABLE

- Retry 2-3 times
- Check if sitekey is correct
- Page may have additional protections

### ERROR_RECAPTCHA_TIMEOUT

- Network issue between CapMonster and target
- Try again, or use proxy version (RecaptchaV2Task)

### Token Injected but Form Fails

- Site may validate token server-side with IP check
- Try using proxy version with your IP
- Some sites need callback to be triggered

### Finding the Callback

```javascript
// Check grecaptcha config for callback
JSON.stringify(___grecaptcha_cfg, (k, v) => typeof v === 'function' ? '[Function]' : v, 2)

// Or check data-callback attribute
document.querySelector('[data-callback]')?.dataset.callback
```

---

## Best Practices

1. **Extract sitekey fresh** - Don't hardcode, sites may rotate
2. **Use correct URL** - Must match the page showing CAPTCHA
3. **Inject quickly** - Tokens expire in ~120 seconds
4. **Check for v3** - Some sites use v3 (invisible), need `pageAction`
5. **Monitor balance** - Set up low-balance alerts
6. **Retry on failure** - CapMonster may fail occasionally

## Cost Estimation

| Use Case | CAPTCHAs/day | Monthly Cost |
|----------|--------------|--------------|
| Light (research) | 10 | ~$0.18 |
| Medium (scraping) | 100 | ~$1.80 |
| Heavy (automation) | 1000 | ~$18.00 |

Current balance is ~$10, good for ~16,000 reCAPTCHA v2 solves.
