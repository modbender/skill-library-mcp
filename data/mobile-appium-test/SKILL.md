---
name: mobile-appium-test
description: >
  Android UI automation testing using Appium with USB-connected real devices.
  Use when the user wants to run Appium tests on physical Android devices connected via USB,
  including: device connection verification, app installation, UI element inspection,
  test execution, screenshot capture, and log collection. Requires ADB and Appium Server installed.
metadata: { "openclaw": { "emoji": "📱", "requires": { "tools": ["adb", "appium"] } } }
---

# Mobile Appium Test

Android UI automation testing using Appium with USB-connected real devices.

## Prerequisites

**Required tools (must be installed):**
- ADB (Android Debug Bridge) - part of Android SDK
- Appium Server (v2.x recommended)
- Appium Doctor (`npm install -g @appium/doctor`)

**Verify installation:**
```bash
adb version
appium --version
appium doctor
```

## Quick Reference

### Device Connection

| Goal | Command |
|------|---------|
| List connected devices | `adb devices` |
| Get device info | `adb shell getprop ro.build.version.release` |
| Restart ADB server | `adb kill-server && adb start-server` |
| USB debug authorization | Check phone for authorization prompt |

### Appium Server

| Goal | Command |
|------|---------|
| Start Appium | `appium --address 127.0.0.1 --port 4723` |
| Start with relaxed security | `appium --relaxed-security` |
| Check Appium status | `curl http://127.0.0.1:4723/status` |

### Common Appium Operations

| Goal | Endpoint/Action |
|------|-----------------|
| Start session | `POST /session` with capabilities |
| Find element | `POST /session/{id}/element` |
| Click element | `POST /session/{id}/element/{id}/click` |
| Send keys | `POST /session/{id}/element/{id}/value` |
| Take screenshot | `GET /session/{id}/screenshot` |
| Get page source | `GET /session/{id}/source` |
| Quit session | `DELETE /session/{id}` |

## Typical Workflow

### 1. Verify Device Connection
```bash
adb devices
```
Ensure device shows `device` status (not `unauthorized` or `offline`).

### 2. Start Appium Server
```bash
appium --address 127.0.0.1 --port 4723 --relaxed-security
```

### 3. Run Test
Use desired capabilities for USB device:
```json
{
  "platformName": "Android",
  "deviceName": "device",
  "udid": "<device-udid>",
  "app": "/path/to/app.apk",
  "automationName": "UiAutomator2",
  "noReset": true
}
```

### 4. Common Test Scenarios

- **Install app**: `adb install app.apk`
- **Launch app**: Appium `appActivity` capability
- **Find element by ID**: `find_element("id", "com.example:id/button")`
- **Find element by text**: `find_element("xpath", "//*[@text='Submit']")`
- **Swipe**: Appium touch action
- **Get logs**: `adb logcat`

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `device not found` | USB connection issue | Check `adb devices`, restart ADB server |
| `unauthorized` | USB debug not authorized | Unlock phone, authorize the computer |
| `no such element` | Element not found | Use `find_elements` with wait, check page source |
| `session not created` | Capability mismatch | Verify UDID, platform version, app path |

## Notes

- Always use `UdID` from `adb devices` for real device testing
- Use `UiAutomator2` as automation engine for Android
- `noReset: true` preserves app state between sessions
- For WiFi debugging: `adb tcpip 5555` then `adb connect <IP>:5555`
