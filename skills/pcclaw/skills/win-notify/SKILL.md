---
name: win-notify
description: Send Windows toast notifications via PowerShell (no dependencies).
metadata:
  {
    "openclaw":
      {
        "emoji": "🔔",
        "os": ["win32"],
      },
  }
---

# win-notify

Send native Windows 10/11 toast notifications from the agent using PowerShell.
No external dependencies — uses built-in WinRT APIs.

## Usage

Send a simple notification:

```powershell
powershell.exe -NoProfile -Command "
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null

$template = @'
<toast>
  <visual>
    <binding template=`"ToastGeneric`">
      <text>TITLE_HERE</text>
      <text>BODY_HERE</text>
    </binding>
  </visual>
</toast>
'@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('OpenClaw').Show($toast)
"
```

Replace `TITLE_HERE` and `BODY_HERE` with actual content.

## Examples

### Basic notification

```powershell
powershell.exe -NoProfile -Command "
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml('<toast><visual><binding template=\"ToastGeneric\"><text>Task Complete</text><text>Your build finished successfully.</text></binding></visual></toast>')
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('OpenClaw').Show($toast)
"
```

### Notification with attribution

```powershell
powershell.exe -NoProfile -Command "
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml('<toast><visual><binding template=\"ToastGeneric\"><text>Reminder</text><text>Meeting with Alex in 15 minutes</text><text placement=\"attribution\">via OpenClaw</text></binding></visual></toast>')
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('OpenClaw').Show($toast)
"
```

### Notification with image

```powershell
powershell.exe -NoProfile -Command "
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml('<toast><visual><binding template=\"ToastGeneric\"><text>Screenshot Captured</text><text>Saved to Desktop</text><image placement=\"hero\" src=\"file:///C:/Users/user/Desktop/screenshot.png\"/></binding></visual></toast>')
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('OpenClaw').Show($toast)
"
```

## Notes

- Works on Windows 10 1607+ and Windows 11.
- Notifications appear in the Windows Action Center.
- The `ToastGeneric` template supports title, body, attribution text, images, and progress bars.
- No installation required — uses PowerShell and built-in WinRT APIs.
- For WSL: call `powershell.exe` from within WSL to send notifications to the Windows desktop.
- XML special characters in title/body must be escaped (`&amp;`, `&lt;`, `&gt;`).
