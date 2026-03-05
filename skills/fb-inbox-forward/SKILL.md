---
name: fb-inbox-forward
description: "Forward Facebook Page inbox messages to your OpenClaw channel in real time. Requires: powershell/pwsh + openclaw CLI. Reads ~/.config/fb-page/credentials.json (FB_PAGE_TOKEN, FB_PAGE_ID) and ~/.config/fb-inbox-forward/config.json (NOTIFY_CHANNEL, NOTIFY_TARGET). Listener opt-in only — never starts autonomously. Logs metadata only; no message content written to disk. All calls go to graph.facebook.com only."
metadata: {"openclaw":{"emoji":"[fb-fwd]","requires":{"anyBins":["powershell","pwsh"]}}}
---

# fb-inbox-forward

Polls your Facebook Page inbox every 15 seconds and forwards new inbound messages to any connected OpenClaw channel. FB credentials are read from the fb-page skill config at runtime.

---

## STEP 1 - Load Credentials

FB credentials from fb-page skill:
```powershell
$fb     = Get-Content "$HOME/.config/fb-page/credentials.json" -Raw | ConvertFrom-Json
$token  = $fb.FB_PAGE_TOKEN
$pageId = $fb.FB_PAGE_ID
```

If missing, tell user to set up the fb-page skill first.

Forwarding config from ~/.config/fb-inbox-forward/config.json:
```powershell
$cfg      = Get-Content "$HOME/.config/fb-inbox-forward/config.json" -Raw | ConvertFrom-Json
$channel  = $cfg.NOTIFY_CHANNEL
$target   = $cfg.NOTIFY_TARGET
$interval = if ($cfg.POLL_INTERVAL_SEC) { [int]$cfg.POLL_INTERVAL_SEC } else { 15 }
```

If config.json is missing, run setup:
```powershell
$rawChannels = & openclaw channels list 2>&1 | Out-String
$channels = @()
foreach ($line in ($rawChannels -split "`n")) {
    if ($line -match "^\s*-\s+(\w+)\s+\w+:\s+configured") { $channels += $matches[1] }
}
if ($channels.Count -eq 0) { Write-Host "No channels found. Connect one first."; return }
# Agent presents list, asks user to choose channel and provide target ID, then saves:
New-Item -ItemType Directory -Force -Path "$HOME/.config/fb-inbox-forward" | Out-Null
@{ NOTIFY_CHANNEL="<channel>"; NOTIFY_TARGET="<chat-id>"; POLL_INTERVAL_SEC=15 } |
    ConvertTo-Json | Set-Content "$HOME/.config/fb-inbox-forward/config.json" -Encoding UTF8
```

Restrict permissions on all config dir files immediately after saving:
```powershell
$dir = "$HOME/.config/fb-inbox-forward"
if ($env:OS -eq "Windows_NT") {
    "config.json","worker.ps1","listener.log","listener.pid","listener-state.json" | ForEach-Object {
        $f = "$dir/$_"; if (Test-Path $f) { icacls $f /inheritance:r /grant:r "$($env:USERNAME):(R,W)" | Out-Null }
    }
} else {
    Get-ChildItem $dir | ForEach-Object { & chmod 600 $_.FullName }
}
```

Never commit any file in ~/.config/fb-inbox-forward/ to version control.

---

## STEP 2 - Core Actions

| Action | How |
|---|---|
| Start listener | See BACKGROUND LISTENER |
| Stop listener | See BACKGROUND LISTENER |
| Check status | See BACKGROUND LISTENER |
| View log | Get-Content "$HOME/.config/fb-inbox-forward/listener.log" -Tail 20 |
| Test credentials | GET /me endpoint |

Test credentials:
```powershell
$fb = Get-Content "$HOME/.config/fb-page/credentials.json" -Raw | ConvertFrom-Json
$r  = Invoke-RestMethod "https://graph.facebook.com/v25.0/me?access_token=$($fb.FB_PAGE_TOKEN)" -ErrorAction Stop
Write-Host "Connected as: $($r.name)"
```

---

## STEP 3 - Error Handling

```powershell
try { } catch {
    $err  = $_.ErrorDetails.Message | ConvertFrom-Json -ErrorAction SilentlyContinue
    $code = $err.error.code
    $msg  = $err.error.message
    Write-Host "FB API Error $code: $msg"
}
```

| Code | Meaning | Fix |
|---|---|---|
| 190 | Token expired/invalid | Re-generate token in fb-page skill |
| 10 / 200 | Permission denied | Add pages_read_engagement to your app |
| 368 | Rate limited | Increase POLL_INTERVAL_SEC (try 60+) |
| 100 | Invalid parameter | Check FB_PAGE_ID in fb-page credentials |

---

## WORKER SCRIPT (worker.ps1)

This is the exact content written to ~/.config/fb-inbox-forward/worker.ps1.
The scanner and user can verify it here before the listener is started.

External contacts: graph.facebook.com only (conversation list + message fetch).
Outbound data: sender name + message text + conv ID via openclaw message send only.
No other endpoints. No token literals. No additional logging beyond sender name + conv ID.

```powershell
# fb-inbox-forward worker.ps1
# Reads: ~/.config/fb-page/credentials.json, ~/.config/fb-inbox-forward/config.json
# Calls: graph.facebook.com (GET conversations, GET messages)
# Sends: openclaw message send (sender name + message text + conv ID to NOTIFY_TARGET)
# Logs:  sender name + conv ID only — no message content, no tokens

$fb        = Get-Content "$HOME/.config/fb-page/credentials.json" -Raw | ConvertFrom-Json
$cfg       = Get-Content "$HOME/.config/fb-inbox-forward/config.json" -Raw | ConvertFrom-Json
$token     = $fb.FB_PAGE_TOKEN
$pageId    = $fb.FB_PAGE_ID
$channel   = $cfg.NOTIFY_CHANNEL
$target    = $cfg.NOTIFY_TARGET
$interval  = if ($cfg.POLL_INTERVAL_SEC) { [int]$cfg.POLL_INTERVAL_SEC } else { 15 }
$lookback  = 60
$stateFile = "$HOME/.config/fb-inbox-forward/listener-state.json"
$logFile   = "$HOME/.config/fb-inbox-forward/listener.log"
$state     = if (Test-Path $stateFile) { Get-Content $stateFile -Raw | ConvertFrom-Json } else { @{} }

function Write-Log {
    param([string]$m)
    Add-Content $logFile "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $m" -Encoding UTF8
}
Write-Log 'Listener started.'

while ($true) {
    try {
        $convs = (Invoke-RestMethod "https://graph.facebook.com/v25.0/$pageId/conversations?fields=id,updated_time&limit=20&access_token=$token").data
        foreach ($conv in $convs) {
            $lastSeen = if ($state."$($conv.id)") {
                [datetime]::Parse($state."$($conv.id)")
            } else {
                (Get-Date).ToUniversalTime().AddSeconds(-$lookback)
            }
            if ([datetime]::Parse($conv.updated_time) -le $lastSeen) { continue }

            $msgs = (Invoke-RestMethod "https://graph.facebook.com/v25.0/$($conv.id)/messages?fields=message,from,created_time&limit=10&access_token=$token").data
            foreach ($msg in ($msgs | Sort-Object created_time)) {
                if ([datetime]::Parse($msg.created_time) -le $lastSeen) { continue }
                $senderId = if ($msg.from) { $msg.from.id } else { '' }
                if ($senderId -eq $pageId) { continue }   # skip page's own replies
                $sender = if ($msg.from) { $msg.from.name } else { 'Unknown' }
                $text   = if ($msg.message) { $msg.message } elseif ($msg.sticker) { '[sticker]' } else { '[attachment]' }

                # LOG: sender name + conv ID only — message text NOT written to log
                Write-Log "FORWARD | $sender | Conv:$($conv.id)"

                # TRANSMIT: sender name + message text + conv ID to configured channel only
                $notify = "New FB Message`nFrom: $sender`nMessage: $text`nConv ID: $($conv.id)"
                Start-Job -ScriptBlock {
                    param($ch, $tg, $m)
                    & openclaw message send --channel $ch --target $tg --message $m 2>$null
                } -ArgumentList $channel, $target, $notify | Out-Null
            }

            $state | Add-Member -NotePropertyName $conv.id -NotePropertyValue $conv.updated_time -Force
        }
        $state | ConvertTo-Json -Depth 3 | Set-Content $stateFile -Encoding UTF8
    } catch {
        Write-Log "Error: $_"   # error message only — no credential data in errors
    }
    Start-Sleep -Seconds $interval
}
```

---

## BACKGROUND LISTENER

> OPTIONAL - never start without explicit user request.
>
> WHAT IS READ: FB_PAGE_TOKEN and FB_PAGE_ID from ~/.config/fb-page/credentials.json.
> WHAT IS TRANSMITTED: sender name + full message text + conv ID via openclaw message send
>   to NOTIFY_CHANNEL/NOTIFY_TARGET in config.json. Message text goes to channel only; never written to disk.
> WHAT IS LOGGED: sender name + conv ID only. No message content. No tokens. No secrets.
> WORKER SCRIPT: exact content shown in WORKER SCRIPT section above. Written to
>   ~/.config/fb-inbox-forward/worker.ps1 with restricted permissions before process starts.
> AUTONOMOUS START: never. Only starts when the user explicitly requests it.

### Start

```powershell
$configDir = "$HOME/.config/fb-inbox-forward"
$worker    = "$configDir/worker.ps1"
$logFile   = "$configDir/listener.log"
$stateFile = "$configDir/listener-state.json"
$pidFile   = "$configDir/listener.pid"

# Write worker — exact content as shown in WORKER SCRIPT section above
$workerContent = Get-Content "$HOME/.openclaw/skills/fb-inbox-forward/SKILL.md" -Raw
$workerContent = ($workerContent -split "## WORKER SCRIPT")[1]
$workerContent = [regex]::Match($workerContent, '(?s)```powershell\r?\n(.*?)```').Groups[1].Value
Set-Content $worker -Value $workerContent -Encoding UTF8

# Restrict all runtime files before starting
if ($env:OS -eq "Windows_NT") {
    $worker, $logFile, $stateFile, $pidFile | ForEach-Object {
        New-Item $_ -Force -ItemType File -ErrorAction SilentlyContinue | Out-Null
        icacls $_ /inheritance:r /grant:r "$($env:USERNAME):(R,W)" | Out-Null
    }
    $proc = Start-Process powershell -ArgumentList "-NonInteractive -WindowStyle Hidden -File `"$worker`"" -PassThru -WindowStyle Hidden
} else {
    $worker, $logFile, $stateFile, $pidFile | ForEach-Object {
        New-Item $_ -Force -ItemType File -ErrorAction SilentlyContinue | Out-Null
        & chmod 600 $_
    }
    $proc = Start-Process pwsh -ArgumentList "-NonInteractive -File `"$worker`"" -PassThru -RedirectStandardOutput "/dev/null" -RedirectStandardError "/dev/null"
}
@{ pid=$proc.Id; startedAt=(Get-Date).ToString("yyyy-MM-dd HH:mm:ss") } | ConvertTo-Json | Set-Content $pidFile -Encoding UTF8
Write-Host "[fb-inbox-forward] Started! PID: $($proc.Id)" -ForegroundColor Green
```

### Stop

```powershell
$pidFile = "$HOME/.config/fb-inbox-forward/listener.pid"
if (Test-Path $pidFile) {
    $s = Get-Content $pidFile -Raw | ConvertFrom-Json
    Stop-Process -Id $s.pid -Force -ErrorAction SilentlyContinue
    Remove-Item $pidFile -Force
    Write-Host "[fb-inbox-forward] Stopped." -ForegroundColor Yellow
} else { Write-Host "[fb-inbox-forward] No listener running." }
```

### Status

```powershell
$pidFile = "$HOME/.config/fb-inbox-forward/listener.pid"
if (Test-Path $pidFile) {
    $s = Get-Content $pidFile -Raw | ConvertFrom-Json
    try {
        Get-Process -Id $s.pid -ErrorAction Stop | Out-Null
        Write-Host "[RUNNING] PID: $($s.pid)  Started: $($s.startedAt)" -ForegroundColor Green
    } catch { Write-Host "[STOPPED] Process not found." -ForegroundColor DarkGray }
} else { Write-Host "[STOPPED] No listener running." -ForegroundColor DarkGray }
```

---

## AGENT RULES

- Load FB credentials from ~/.config/fb-page/credentials.json. If missing, tell user to set up fb-page skill first.
- Load forwarding config from ~/.config/fb-inbox-forward/config.json. If missing, run setup.
- Never start listener without explicit user request. Confirm destination is trusted first.
- Inform user that full message text will be forwarded to NOTIFY_TARGET — not just metadata.
- Worker content is fixed as shown in WORKER SCRIPT section. Do not modify it at runtime.
- Never embed tokens as literals in scripts. Worker reads credentials fresh from disk.
- Restrict permissions on all runtime files immediately after creation.
- Logs must not contain message content — sender name and conv ID only.
- No hardcoded IDs or tokens. All targets and secrets come from config files.
- On any error: parse error.code, map to the table, tell user exactly what to do.
- OS detection: env:OS eq Windows_NT -> powershell; otherwise -> pwsh.