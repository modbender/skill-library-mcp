# 即梦 (Jimeng) Session Data Usage Guide

This reference file explains how to use browser-session-manager with Jimeng (即梦) session data.

## JSON Structure

The Jimeng session export contains:

### Cookies (26 cookies total)
Key authentication cookies:
- `sessionid` / `sessionid_ss` - Session identifiers
- `passport_csrf_token` - CSRF protection token
- `sid_guard` - Security guard token
- `ttwid` - User identification
- `odin_tt` - Authentication token

### localStorage
Contains user preferences and settings:
- User ID and tokens (`__tea_cache_tokens_513695`)
- Model preferences (`dreamina__generator_image__selectedImageModel`)
- Theme settings (`DREAMINA_THEME`)
- AB test configurations
- Canvas/project settings

### sessionStorage
Session-specific data (usually empty or minimal)

## Usage Example

```javascript
const { applySessionData } = require('./scripts/browser-session-manager.js');

async function accessJimeng() {
  const result = await applySessionData(
    'https://jimeng.jianying.com/ai-tool/home',
    '/path/to/jimeng-session.json',
    {
      headless: true,
      screenshotPath: '/tmp/jimeng-home.png',
      waitTime: 5000
    }
  );
  
  console.log('Page loaded:', result.title);
  return result;
}
```

## Important Notes

1. **Session Expiration**: Cookies have expiration dates (mostly 2027-02-13). Sessions will become invalid after expiration.

2. **Security**: The session data contains sensitive authentication tokens. Never share or commit this data.

3. **Rate Limiting**: Jimeng may detect automated access and rate-limit or block requests.

4. **Cookie Domains**: Cookies are set for both `jimeng.jianying.com` and `.jianying.com` domains.

## Common Use Cases

### 1. Access AI Image Generation
```javascript
await applySessionData(
  'https://jimeng.jianying.com/ai-tool/home?type=image',
  sessionJsonPath,
  { screenshotPath: '/tmp/jimeng-image.png', waitTime: 8000 }
);
```

### 2. Access Video Generation
```javascript
await applySessionData(
  'https://jimeng.jianying.com/ai-tool/home?type=video',
  sessionJsonPath,
  { screenshotPath: '/tmp/jimeng-video.png', waitTime: 8000 }
);
```

### 3. Check User Credits/Balance
```javascript
const result = await applySessionData(
  'https://jimeng.jianying.com/member/credits',
  sessionJsonPath,
  { screenshotPath: '/tmp/jimeng-credits.png', waitTime: 5000 }
);
```

## Troubleshooting

**Login page still showing:**
- Session may be expired
- Check if `sessionid` cookie is properly set
- Verify the user agent matches the original browser

**Features not loading:**
- Some features require specific localStorage values
- Check browser console for JavaScript errors

**Rate limited:**
- Add delays between requests
- Use different IP/proxy if heavily rate-limited