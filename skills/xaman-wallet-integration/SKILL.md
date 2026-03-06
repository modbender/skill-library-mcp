---
name: xaman-wallet
description: "Integrate Xaman wallet (formerly Xumm) for XRP Ledger
  authentication and transactions. Use for: (1) Adding wallet connection to a
  webapp, (2) Implementing sign-in with Xaman, (3) Requesting payment/signatures
  from users, (4) Loading XummPkce SDK from CDN."
---


# Xaman Wallet Integration

## Quick Start

1. **Load the SDK** (in layout.tsx or HTML head):
```html
<script src="https://xumm.app/assets/cdn/xumm-oauth2-pkce.min.js"></script>
```

2. **Initialize and connect**:
```typescript
const XummPkce = (window as any).XummPkce;
const xumm = new XummPkce(API_KEY, {
  redirectUrl: window.location.origin + "/dashboard"
});

// Listen for auth events
xumm.on("success", async (state) => {
  const account = (await xumm.state())?.me?.account;
  console.log("Connected:", account);
});

// Start auth flow (opens popup)
await xumm.authorize();
```

## API Key

Get your API key from: https://xumm.app/dashboard/developer

Environment variable: `NEXT_PUBLIC_XAMAN_API_KEY`

## Key Methods

- `new XummPkce(apiKey, options)` - Initialize SDK
- `xumm.authorize()` - Start OAuth flow, opens Xaman app
- `xumm.state()` - Get current user session
- `xumm.logout()` - Clear session
- `xumm.on("success", callback)` - Listen for successful auth
- `xumm.on("error", callback)` - Listen for errors

## Options

```typescript
{
  redirectUrl: string,      // Where to redirect after auth
  rememberJwt: boolean,     // Persist session in localStorage (default: true)
  storage: Storage,        // Custom storage (default: localStorage)
  implicit: boolean        // Use implicit flow (default: false)
}
```

## Session Recovery

The SDK auto-restores sessions. Call `xumm.logout()` before `authorize()` to force fresh login.

## Troubleshooting

- **Popup blocked**: Browser popup blocker may prevent authorize() - call from user action
- **Account undefined**: Use `xumm.state().then(s => s.me.account)` after success event
- **CORS errors**: Ensure redirectUrl matches your app's origin
