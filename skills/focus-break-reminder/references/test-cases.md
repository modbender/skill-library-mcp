# Focus Break Reminder - Test Cases

## 1) Work interval trigger
- Given: enabled=true, work_minutes=50
- When: active duration reaches 50 minutes
- Then: send exactly one reminder

## 2) Cooldown suppression
- Given: cooldown_minutes=30 and reminder just sent
- When: check within 30 minutes
- Then: do not send reminder

## 3) Idle reset
- Given: idle_reset_minutes=15
- When: no activity for >=15 minutes, then user returns
- Then: reset session_start_at and start timing from return time

## 4) Quiet hours
- Given: quiet_hours includes current time
- When: all other conditions pass
- Then: no reminder

## 5) Snooze
- Given: /break snooze 120
- When: within 120 minutes
- Then: no reminder
- And: reminders resume after snooze_until

## 6) Daily cap
- Given: daily_max_reminders=4
- When: 4 reminders already sent today
- Then: no additional reminders today

## 7) Date rollover
- Given: timezone=Asia/Shanghai
- When: local date changes
- Then: remind_count_today resets to 0

## 8) Command validation
- /break set 10 -> reject (below range)
- /break set 50 -> accept
- /break on|off -> toggles enabled
- /break status -> returns config + next eligible time window
