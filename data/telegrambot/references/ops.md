# Ops Runbook

## Start (PowerShell)
```powershell
$env:GOD_MODE_HOST='127.0.0.1'
$env:GOD_MODE_PORT='8888'
$env:GOD_MODE_ROOT='C:\'
$env:GOD_MODE_TOKEN='change-me-now'
node .\skills\god-mode-manager\scripts\server.cjs
```

## Health check
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8888/' -Headers @{ 'x-god-mode-token'='change-me-now' }
```

## List directory
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8888/list?path=Users' -Headers @{ 'x-god-mode-token'='change-me-now' }
```

## Read small file
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8888/read?path=Windows\\System32\\drivers\\etc\\hosts' -Headers @{ 'x-god-mode-token'='change-me-now' }
```

## Download file (binary-safe)
```powershell
Invoke-WebRequest -Uri 'http://127.0.0.1:8888/download?path=Windows\\System32\\drivers\\etc\\hosts' -Headers @{ 'x-god-mode-token'='change-me-now' } -OutFile .\hosts.copy
```

## Security defaults
- Keep `GOD_MODE_HOST=127.0.0.1`.
- Keep token auth enabled (`GOD_MODE_TOKEN_REQUIRED=true`).
- Rotate `GOD_MODE_TOKEN` when shared in logs.
