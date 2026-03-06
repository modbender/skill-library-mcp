# Phone Control API Reference

Base URL: `https://api.mobilerun.ai/v1`
Auth: `Authorization: Bearer dr_sk_...`

This document covers how to control an Android device connected to Mobilerun.
The primary use case is controlling the user's own personal device connected via the Droidrun Portal APK.

For platform-level operations (provisioning cloud devices, AI agent tasks, webhooks), see [api.md](./api.md).

---

## Finding & Checking the Device

### List Devices

```
GET /devices
```

Returns all devices for the user. Check the `state` and `provider` fields to understand what's available.
See [setup.md](./setup.md) for device connectivity troubleshooting and Portal APK setup.

### Device States

| State          | Meaning |
|----------------|---------|
| `creating`     | Device is being provisioned (cloud devices only) |
| `assigned`     | Device is assigned but not yet ready |
| `ready`        | Device is connected and accepting commands |
| `disconnected` | Connection lost -- Portal app may be closed or phone lost network |
| `terminated`   | Device has been shut down (cloud devices only) |
| `unknown`      | Unexpected state |

For personal devices, you'll typically see `ready` or `disconnected`.
If `disconnected`, ask the user to check that the Portal app is open and the phone has internet.

### Get Device Info

```
GET /devices/{deviceId}
```

Returns device details including `state`, `stateMessage`, `provider`, `deviceType`, and more.

### Get Device Time

```
GET /devices/{deviceId}/time
```

Returns the current time on the device as a string.

---

## Screen Observation

These are the primary tools for understanding what's on the device screen.

### Take Screenshot

```
GET /devices/{deviceId}/screenshot
```

Query param: `hideOverlay` (default: `false`)

Returns a **PNG image** as binary data. Use this to see what's currently displayed on screen.

### Get UI State (Accessibility Tree)

```
GET /devices/{deviceId}/ui-state
```

Query param: `filter` (default: `false`) -- set to `true` to filter out non-interactive elements.

Returns an `AndroidState` object with three sections:

#### phone_state

```json
{
  "keyboardVisible": false,
  "packageName": "app.lawnchair",
  "currentApp": "Lawnchair",
  "isEditable": false,
  "focusedElement": {
    "className": "string",
    "resourceId": "string",
    "text": "string"
  }
}
```

- `currentApp` -- human-readable name of the foreground app
- `packageName` -- Android package name of the foreground app
- `keyboardVisible` -- whether the soft keyboard is showing
- `isEditable` -- whether the currently focused element accepts text input
- `focusedElement` -- details about the focused UI element (if any)

#### device_context

```json
{
  "screen_bounds": { "width": 720, "height": 1616 },
  "screenSize": { "width": 0, "height": 0 },
  "display_metrics": {
    "density": 1.75,
    "densityDpi": 280,
    "scaledDensity": 1.75,
    "widthPixels": 720,
    "heightPixels": 1616
  },
  "filtering_params": {
    "min_element_size": 5,
    "overlay_offset": 0
  }
}
```

- `screen_bounds` -- the actual screen resolution in pixels. All tap/swipe coordinates use this coordinate space.
- `display_metrics` -- physical display properties (density, DPI)
- `filtering_params.min_element_size` -- minimum element size in pixels (used when `filter=true`)

#### a11y_tree (Accessibility Tree)

A recursive tree of UI elements. Each node has:

```json
{
  "className": "android.widget.TextView",
  "packageName": "app.lawnchair",
  "resourceId": "app.lawnchair:id/search_container",
  "text": "Search",
  "contentDescription": "",
  "boundsInScreen": { "left": 48, "top": 1420, "right": 671, "bottom": 1532 },
  "isClickable": true,
  "isLongClickable": false,
  "isEditable": false,
  "isScrollable": false,
  "isEnabled": true,
  "isVisibleToUser": true,
  "isCheckable": false,
  "isChecked": false,
  "isFocusable": false,
  "isFocused": false,
  "isSelected": false,
  "isPassword": false,
  "hint": "",
  "childCount": 0,
  "children": []
}
```

**Key node fields:**
- `text` -- the visible text on the element
- `contentDescription` -- accessibility label (useful when `text` is empty, e.g. icon buttons)
- `resourceId` -- Android resource ID (e.g. `com.app:id/button_ok`) -- useful for identifying elements
- `boundsInScreen` -- pixel coordinates as `{left, top, right, bottom}`. To tap an element, calculate its center: `x = (left + right) / 2`, `y = (top + bottom) / 2`
- `isClickable` -- whether the element responds to taps
- `isEditable` -- whether the element is a text input field
- `isScrollable` -- whether the element supports scrolling (swipe gestures)
- `children` -- nested child elements (the tree is recursive)

**Example: reading a home screen**
```
FrameLayout (0,0,720,1616)
  ScrollView (0,0,720,1616) [scrollable]
    FrameLayout (14,113,706,326)
      LinearLayout (42,128,706,310) [clickable]
        TextView (42,156,706,198) "Tap to set up"
  View (0,94,720,1574) "Home"
  TextView (14,1222,187,1422) "Phone" [clickable]
  TextView (187,1222,360,1422) "Contacts" [clickable]
  TextView (360,1222,533,1422) "Files" [clickable]
  TextView (533,1222,706,1422) "Chrome" [clickable]
  FrameLayout (48,1420,671,1532) "Search" [clickable]
```

To tap "Chrome": bounds are (533,1222,706,1422), so tap at x=(533+706)/2=619, y=(1222+1422)/2=1322.

Use `filter=true` for a cleaner tree focused on actionable elements (filters out non-interactive containers).

---

## Device Actions

All action endpoints take a `deviceId` path parameter.
Optional header: `X-Device-Display-ID` (integer, default: `0`) -- for multi-display devices.

### Tap

```
POST /devices/{deviceId}/tap
Content-Type: application/json

{ "x": 540, "y": 960 }
```

Taps at pixel coordinates. Use the `screen_bounds` from UI state and element bounds from the a11y tree to calculate where to tap.

### Swipe

```
POST /devices/{deviceId}/swipe
Content-Type: application/json

{
  "startX": 540,
  "startY": 1200,
  "endX": 540,
  "endY": 400,
  "duration": 300
}
```

`duration` is in milliseconds (minimum: 10). Common patterns:
- **Scroll down**: swipe from bottom to top (high startY -> low endY)
- **Scroll up**: swipe from top to bottom
- **Swipe left/right**: adjust X coordinates, keep Y similar

### Global Actions

```
POST /devices/{deviceId}/global
Content-Type: application/json

{ "action": 2 }
```

| Action code | Button  |
|-------------|---------|
| `1`         | BACK    |
| `2`         | HOME    |
| `3`         | RECENT  |

### Type Text

```
POST /devices/{deviceId}/keyboard
Content-Type: application/json

{ "text": "Hello world", "clear": false }
```

Types text into the currently focused input field.
- `clear: true` -- clears the field before typing
- Make sure an input field is focused first (check `phone_state.isEditable`)
- If the keyboard isn't visible, you may need to tap on an input field first

### Press Key

```
PUT /devices/{deviceId}/keyboard
Content-Type: application/json

{ "key": 66 }
```

Sends an Android keycode. Only text-input-related keycodes are supported -- system/hardware keys (volume, power, etc.) will fail.

Working keycodes:

| Keycode | Key |
|---------|-----|
| `4`   | BACK |
| `61`  | TAB |
| `66`  | ENTER |
| `67`  | DEL (backspace) |
| `112` | FORWARD_DEL (delete) |

For system navigation (home, back, recent), use `POST /devices/{id}/global` instead.

### Clear Input

```
DELETE /devices/{deviceId}/keyboard
```

Clears the currently focused input field.

---

## App Management (On-Device)

### List Installed Apps

```
GET /devices/{deviceId}/apps
```

Query param: `includeSystemApps` (default: `false`)

Returns an array of `AppInfo`:
```json
{
  "packageName": "com.example.app",
  "label": "Example App",
  "versionName": "1.2.3",
  "versionCode": 123,
  "isSystemApp": false
}
```

### List Package Names

```
GET /devices/{deviceId}/packages
```

Query param: `includeSystemPackages` (default: `false`)

Returns a string array of package names. Lighter than the full app list.

### Install App

```
POST /devices/{deviceId}/apps
Content-Type: application/json

{ "packageName": "com.example.app" }
```

Installs an app from the Mobilerun app library (not the Play Store directly).
Takes a couple of minutes and there's no status endpoint -- you'd have to poll `GET /devices/{id}/apps` to confirm.

**Prefer manually installing via Play Store instead.** Open the Play Store app on the device, search for the app, and tap install -- this is faster and more reliable. Only use this API endpoint if the user explicitly asks for it.

> On personal devices, this endpoint may fail because Android blocks app installations from unknown sources by default. The user would need to explicitly enable "Install unknown apps" for the Portal APK in their device settings. Another reason to prefer the Play Store approach.

### Start App

```
PUT /devices/{deviceId}/apps/{packageName}
Content-Type: application/json

{}
```

Optional body: `{ "activity": "com.example.app.MainActivity" }` -- to launch a specific activity.
Usually omitting activity is fine; it launches the default/main activity.

### Stop App

```
PATCH /devices/{deviceId}/apps/{packageName}
Content-Type: application/json

{}
```

### Uninstall App

```
DELETE /devices/{deviceId}/apps/{packageName}
Content-Type: application/json

{}
```

---

## Typical Workflow

1. **Find the device**: `GET /devices`
   - Look for a device with `state: "ready"`
   - If a device shows `disconnected`: ask user to reopen Portal app
   - If no devices at all: user needs to connect a device (see [setup.md](./setup.md))

2. **Observe**:
   - `GET /devices/{id}/screenshot` -- see the screen
   - `GET /devices/{id}/ui-state?filter=true` -- get actionable UI elements

3. **Act**:
   - Tap: `POST /devices/{id}/tap` with `{x, y}`
   - Type: `POST /devices/{id}/keyboard` with `{text, clear}`
   - Swipe: `POST /devices/{id}/swipe` with coordinates + duration
   - Navigate: `POST /devices/{id}/global` -- back (1), home (2), recent (3)
   - Open app: `PUT /devices/{id}/apps/{packageName}`

4. **Repeat** observe + act until the goal is achieved.

---

## Error Handling

All API errors follow this format:

```json
{
  "title": "Unauthorized",
  "status": 401,
  "detail": "Invalid API key.",
  "errors": []
}
```

| Status | Meaning | What to do |
|--------|---------|------------|
| `401` | Invalid, expired, or revoked API key | Ask user to check/recreate key at https://cloud.mobilerun.ai/api-keys |
| `404` / `500` | Device not found or invalid device ID | Verify the device ID is correct, re-list devices |
| Action fails on valid device | Device may be locked, busy, or unresponsive | Take a screenshot to check device state, try again |
