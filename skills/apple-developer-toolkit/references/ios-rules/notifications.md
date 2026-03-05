---
description: "Implementation rules for notifications"
---
# Notifications

NOTIFICATIONS (LOCAL — no server needed):

FRAMEWORK: UserNotifications — UNUserNotificationCenter.current()

PERMISSION STATES (CRITICAL — must handle ALL four states):
1. NOT DETERMINED: Call .requestAuthorization(options: [.alert, .badge, .sound]). System shows dialog.
2. AUTHORIZED: Schedule notifications normally.
3. DENIED: App CANNOT re-request permission. Must redirect user to System Settings.
4. PROVISIONAL: Quiet notifications — treat as authorized.

PERMISSION IS SYSTEM-CONTROLLED (CRITICAL):
- Notification authorization is owned by the SYSTEM, not the app.
- Once the user denies, the app has NO way to re-request — only the user can re-enable in System Settings.
- To open System Settings: UIApplication.shared.open(URL(string: UIApplication.openSettingsURLString)!)

UI THAT DISPLAYS NOTIFICATION STATUS (in ANY view — must handle ALL three states):
- .notDetermined: Show an "Enable Notifications" button that calls requestAuthorization(options: [.alert, .badge, .sound]). After the system dialog, re-check status and update UI.
- .authorized / .provisional: Show enabled state (e.g. "bell" icon, "Notifications are enabled" text). This is read-only — the user can disable in System Settings.
- .denied: Show disabled state ("bell.slash" icon) with an actionable "Open Settings" button that calls UIApplication.shared.open(URL(string: UIApplication.openSettingsURLString)!). Show helper text explaining the user must enable in System Settings.
- NEVER use a writable Toggle for notification permission — the app cannot grant/revoke it programmatically. Use buttons with state-specific actions instead.

RE-CHECK ON FOREGROUND (CRITICAL):
Any view displaying notification status MUST re-check when the app returns to foreground.
The user may have changed permissions in System Settings while the app was backgrounded.

  .onReceive(NotificationCenter.default.publisher(for: UIApplication.willEnterForegroundNotification)) { _ in
      Task {
          let settings = await UNUserNotificationCenter.current().notificationSettings()
          isNotificationsEnabled = (settings.authorizationStatus == .authorized || settings.authorizationStatus == .provisional)
      }
  }

SCHEDULING:
- Local: UNMutableNotificationContent + UNNotificationRequest
- Time-based: UNTimeIntervalNotificationTrigger(timeInterval:repeats:)
- Calendar-based: UNCalendarNotificationTrigger(dateMatching:repeats:)
- Default to local notifications unless user explicitly asks for remote/push.

BADGE COUNT:
- Set via UNMutableNotificationContent().badge = NSNumber(value: count)
- Clear on app open: UIApplication.shared.applicationIconBadgeNumber = 0
