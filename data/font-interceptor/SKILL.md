---
name: font-interceptor
description: Extract fonts (TTF/OTF) from any website using MSCHF Font Interceptor. Use when user drops a URL and wants to identify/extract/download fonts from that website, or asks "what font is this site using" or similar font extraction requests.
---

# Font Interceptor

Extract fonts from any website using https://fontinterceptor.mschfmag.com/

## Workflow

When user provides a URL to extract fonts from:

1. Open browser to `https://fontinterceptor.mschfmag.com/`
2. Enter the target URL in the search/input field
3. Submit and wait for results
4. Report found fonts (names + download links for TTF/OTF files)

## Browser Automation

```javascript
// Using browser tool with openclaw profile
// 1. Navigate to font interceptor
browser({ action: "open", targetUrl: "https://fontinterceptor.mschfmag.com/", profile: "openclaw" })

// 2. Take snapshot to find input field
browser({ action: "snapshot", profile: "openclaw" })

// 3. Type URL into input and submit
browser({ action: "act", request: { kind: "type", ref: "<input-ref>", text: "https://target-site.com", submit: true } })

// 4. Wait for results, take snapshot
browser({ action: "snapshot", profile: "openclaw" })

// 5. Report fonts found, including download links
```

## Fallback (No Browser)

If browser unavailable, instruct user:
1. Go to https://fontinterceptor.mschfmag.com/
2. Paste URL: `<target-url>`
3. Hit enter
4. Download the fonts shown

## Output Format

Report results as:
```
Fonts found on <url>:
- FontName.ttf [download link]
- FontName.otf [download link]
```

If no fonts found, report that the site may use system fonts or web-safe fonts only.
