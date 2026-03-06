# RS-Skill Troubleshooting Guide

> Common errors, causes, and fixes. We are happy to support — `support@rankscale.ai`

---

## Error: Missing Credentials

**Symptom:**
```
❌ Missing Credentials

Set RANKSCALE_API_KEY and RANKSCALE_BRAND_ID to get started.
```

**Cause:** `RANKSCALE_API_KEY` is not set in your environment.

**Fix:**
1. Check your OpenClaw Gateway config for `RANKSCALE_API_KEY=rk_...`
2. If you haven't received API credentials yet, email `support@rankscale.ai`
3. Restart the OpenClaw Gateway after adding env vars

**Tip:** If your key has the format `rk_<hash>_<brandId>`, the Brand ID is extracted automatically — you may not need `RANKSCALE_BRAND_ID` separately.

---

## Error: 401 Unauthorized / Invalid API Key

**Symptom:**
```
Auth error fetching report: Authentication failed (HTTP 401).
Check your RANKSCALE_API_KEY.
Verify your key at https://rankscale.ai/dashboard/settings/api
```

**Cause:** Your API key is invalid, expired, mis-typed, **or your account is on a trial plan**.

**Fix — verify both of the following:**

1. ✅ **You have a PRO account** (trial accounts do not have REST API access)
   - Log in at [rankscale.ai](https://rankscale.ai) and confirm your plan
   - If on trial, upgrade to PRO before continuing
2. ✅ **REST API is activated by support**
   - Email `support@rankscale.ai` — Subject: "Please activate REST API access"
   - REST API access must be explicitly enabled even on PRO accounts
3. Verify the key at [rankscale.ai/dashboard/settings/api](https://rankscale.ai/dashboard/settings/api)
4. Re-copy the key — make sure there are no trailing spaces

---

## Error: Brand Not Found (HTTP 404)

**Symptom:**
```
Not found (report): Resource not found: metrics/report?brandId=xxx (HTTP 404)
```

**Cause:** The `RANKSCALE_BRAND_ID` doesn't match any brand in your account.

**Fix:**
1. Run `node rankscale-skill.js --discover-brands` to list valid Brand IDs
2. Update `RANKSCALE_BRAND_ID` with the correct value
3. If you just created a brand, allow up to 24h for API indexing

---

## Error: Network / DNS Failure

**Symptom:**
```
Error fetching report: Network error on metrics/report?brandId=xxx:
getaddrinfo ENOTFOUND rankscale.ai
```
The skill falls back to zeroed data and fires CRIT rules:
```
[CRIT] Citation rate critically low (<20%).
[CRIT] GEO score critically low (<40).
```

**Cause:** Your environment cannot reach `rankscale.ai`. Common in sandboxed environments, corporate proxies, or restricted networks.

**Fix:**
1. Check internet connectivity: `curl https://rankscale.ai/health`
2. If behind a proxy, configure `HTTPS_PROXY` in your environment
3. If running in a CI/sandbox environment, whitelist `rankscale.ai`
4. The skill retries 3× per endpoint — total time ~14s before falling back

> **Note:** Zeroed data with CRIT insights does NOT mean your brand is in trouble — it means the API was unreachable. Check connectivity first.

---

## Error: Rate Limited (HTTP 429)

**Symptom:**
The skill pauses briefly then retries automatically. You may see slightly longer execution time.

**Cause:** Too many API requests in a short window.

**Fix:**
- The skill handles this automatically with exponential backoff
- If persistent, wait 60 seconds and retry
- Contact `support@rankscale.ai` if you need higher rate limits

---

## Issue: Slow Response Time (~14 seconds)

**Symptom:** The skill takes 14+ seconds to respond.

**Cause:** DNS resolution is slow or failing, causing 3 retries × 5s timeout per endpoint = ~15s.

**Expected behavior:** With a healthy API connection, execution takes 2–4 seconds.

**Fix:**
1. Check DNS resolution: `nslookup rankscale.ai`
2. If DNS is slow, consider configuring a faster DNS resolver (e.g., 1.1.1.1)
3. If in a sandboxed environment, see "Network / DNS Failure" above

---

## Issue: Output Shows "Your Brand" Instead of Brand Name

**Symptom:** The report header shows `Brand: Your Brand` instead of your actual brand name.

**Cause:** The API returned a response without a `brandName` field, or the skill is running in fallback mode.

**Fix:**
1. Ensure `RANKSCALE_BRAND_ID` is set correctly
2. Check that your brand profile is complete at [rankscale.ai](https://rankscale.ai)
3. Confirm network connectivity (see DNS Failure section)

---

## Issue: No Competitor Data in Gap Analysis

**Symptom:** `--gap-analysis` shows engine gaps and search term gaps but no competitor comparison.

**Cause:** Competitor comparison is not yet implemented in this version of RS-Skill.

**Status:** This is a known planned enhancement. It will appear in a future release.

**Workaround:** Use `--citations gaps` to see citation gaps vs competitors as a proxy.

---

## Issue: Line Width Looks Off on Narrow Terminals

**Symptom:** Some search term lines appear truncated or misaligned.

**Cause:** The default output is optimized for 55-character width. Very narrow terminals (or terminal emulators with small fonts) may wrap lines.

**Fix:** Widen your terminal window. The bar chart display adapts to terminal width.

---

## Still Stuck?

We are happy to support.

📧 `support@rankscale.ai`
🌐 [rankscale.ai](https://rankscale.ai)

Include in your support email:
- Your OS and Node.js version (`node --version`)
- The exact error message
- Whether `curl https://rankscale.ai/health` succeeds
