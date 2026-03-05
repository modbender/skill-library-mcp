# Mobilerun Setup

This document describes how Mobilerun authentication and device connectivity works,
so you can diagnose issues and guide the user through setup when needed.

---

## Authentication

### How It Works

Mobilerun uses API keys for programmatic access. All API calls go to `https://api.mobilerun.ai/v1`
with the key in the Authorization header:

```
Authorization: Bearer dr_sk_...
```

- Keys are always prefixed with `dr_sk_` -- if a user provides something without this prefix, it's not a valid Mobilerun key
- Keys are created from the Mobilerun dashboard and can be revoked or expired
- Each key is tied to a single user account

### Getting an API Key

The user needs to:

1. Go to **https://cloud.mobilerun.ai/api-keys**
   - If not logged in, the page redirects to login first (Google, GitHub, or Discord -- no email/password option)
   - After login it redirects back to the API keys page
2. Click the **"New Key"** button
3. Give the key a name (anything descriptive is fine)
4. Copy the full key -- it's only shown once at creation time

The key will look like: `dr_sk_a1b2c3d4e5f6...`

### Verifying the API Key

After receiving a key from the user, verify it works:

```
GET https://api.mobilerun.ai/v1/devices
Authorization: Bearer dr_sk_...
```

| Response | Meaning |
|----------|---------|
| `200` with JSON body | Key is valid. The response shows the user's devices (may be empty if no devices connected yet) |
| `401 Unauthorized` | Key is invalid, expired, or revoked |

### Troubleshooting Auth Issues

**User provides a key that doesn't start with `dr_sk_`:**
- It's not a Mobilerun API key. Ask them to copy it again from https://cloud.mobilerun.ai/api-keys

**401 on a key that previously worked:**
- The key may have been revoked or expired. Ask the user to check the API keys page and create a new one if needed

**User says they can't find the API keys page:**
- Direct them to https://cloud.mobilerun.ai/api-keys -- they need to be logged in first

**User doesn't have an account:**
- They can create one by going to https://cloud.mobilerun.ai/sign-in and signing in with Google, GitHub, or Discord. First login automatically creates an account.

---

## Device Connectivity

### Personal Devices (Portal APK)

A personal device is the user's own Android phone connected to Mobilerun via the Droidrun Portal app.

Guide the user step by step through out the setup process

#### Step 1: Download the Portal APK

1. On the Android device, open Chrome and go to **https://droidrun.ai/portal**
2. This redirects to the GitHub releases page for the Portal app
3. Scroll down to the **"Assets"** section at the bottom of the latest release
4. Tap the file named **`droidrun-portal-vx.x.x.apk`** (the version number varies) -- this is the APK file to download
   - Do NOT tap "Source code (zip)" or "Source code (tar.gz)" -- those are the source code, not the app

#### Step 2: Install the APK

1. Once downloaded, tap the APK file to install it (or find it in Downloads)
2. **Android may show a warning** like "This app may be harmful" or "Install from unknown sources blocked":
   - This is normal for apps installed outside the Play Store
   - Droidrun Portal is open source -- the full source code is available on GitHub at https://github.com/droidrun/droidrun-portal
   - It uses Android's Accessibility API (the same technology used by screen readers and accessibility tools) to read and interact with the screen
   - Tap **"Install anyway"** or enable "Install unknown apps" for Chrome in Settings when prompted

#### Step 3: Enable Accessibility

1. Open the Droidrun Portal app
2. A red banner at the top says **"Accessibility Service Not Enabled"** -- tap **"Enable Now"**
3. This opens Android Settings. Find **"Droidrun Portal"** in the list of accessibility services
4. Tap on it and **toggle it on**
5. Android will show a confirmation dialog explaining what the accessibility service can do -- tap **"Allow"** or **"OK"**

This permission is required -- without it, the agent cannot read the screen UI tree or control the device.

#### Step 4: Connect to Mobilerun

Two options -- **prefer Option B** (API key) since the agent already has the key:

- **Option B (API Key) -- preferred:** Tell the user to **long-press** "Connect to Mobilerun" -- this opens a **"Connect with API Key"** dialog with a single API key field. Tell them to:
  1. Paste the API key (`dr_sk_...`) in the **API Key** field
  2. Tap **Connect**

  The agent should provide the API key to the user -- it's the same key used for API calls.

- **Option A (Login) -- fallback:** Tap **"Connect to Mobilerun"** (normal tap):
  - If already logged in (API key stored on device) → connects directly, no browser
  - If not logged in → opens a browser login page (Google, GitHub, or Discord)

#### Step 5: Verify Connection

Once connected, the Portal app shows the connection status. The device should now appear in `GET /devices` with `state: "ready"`.

If it doesn't show up, check:
- Is the accessibility service still enabled? (some phones disable it after reboot)
- Is the Portal app still open and in the foreground (at least initially)?
- Does the phone have a stable internet connection?

#### Checking Device Status

```
GET https://api.mobilerun.ai/v1/devices
```

Look for a device with `provider: "personal"`:

| Result | Meaning |
|--------|---------|
| No personal device in list | Portal APK isn't installed, not connected, or accessibility permission not granted |
| Device with `state: "ready"` | Device is connected and ready to use |
| Device with `state: "disconnected"` | Portal app lost connection. User should check that the app is open and phone has internet |

#### Common Issues

- **Device shows `disconnected`**: Portal app was closed, phone went to sleep with aggressive battery optimization, or phone lost internet. Ask user to reopen the Portal app.
- **Device was `ready` but stops responding**: The phone may have locked or the Portal app was killed by the OS. Ask user to check the phone.
- **No device appears at all**: Portal APK isn't installed, accessibility permission wasn't granted, or the user didn't connect with their API key.
- **Connection fails in Portal app**: The API key may be wrong or expired. Ask the user to verify the key.
- **User wants to switch accounts**: They can tap **Logout** (shown below Device ID when connected, or as a subtitle under "Connect to Mobilerun" when disconnected). Logout clears credentials; the next Connect tap will open the browser for a fresh login. Note: **Disconnect** only pauses the connection and can be resumed instantly -- it does not clear credentials.

### Cloud Devices

Cloud devices are virtual/emulated devices hosted by Mobilerun. They require a paid subscription.

If a user tries to provision a cloud device without the right plan, the API will return an error.
In that case, let them know they need to upgrade at https://cloud.mobilerun.ai.

Cloud devices go through these states after provisioning:
`creating` -> `assigned` -> `ready`

Use `GET /devices/{deviceId}/wait` to block until the device is ready (avoids polling).

---

## Accounts & Plans

- **Free accounts** can connect personal devices via Portal APK and use the Tools API to control them
- **Paid plans** add cloud device provisioning, task execution (AI agent credits), and additional features

For full plan details (Hobby, Starter, Pro, Enterprise), see [subscription.md](./subscription.md).

If an API call fails with a billing/plan error, direct the user to https://cloud.mobilerun.ai/billing.

---

## Quick Checklist

When starting a session, verify:

1. **API key works** -- `GET /devices` returns 200
2. **Device is available** -- at least one device with `state: "ready"` in the response
3. **Device is responsive** -- `GET /devices/{id}/screenshot` returns a PNG image

If all three pass, you're ready to control the phone. See [phone-api.md](./phone-api.md) for the full API reference.
