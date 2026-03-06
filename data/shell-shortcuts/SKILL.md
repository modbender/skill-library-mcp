---
name: shell-shortcuts
description: Configure cross-platform terminal shortcut commands on a new machine, including proxy_on/proxy_off (env vars + git global proxy), goto (persistent path jump shortcuts), gpu (nvidia-smi helper), and optional Conda auto-activation. Use when setting up Windows PowerShell Profile / CMD AutoRun, or adding functions to macOS/Linux shell rc files.
---

# Shell Shortcuts (proxy_on, proxy_off, goto, gpu, conda autostart)

Goal: make a fresh machine behave the same across Windows / macOS / Ubuntu with a small set of commands:

- `proxy_on` / `proxy_off`: toggle terminal proxy (env vars + Git global proxy)
- `goto`: persistent path shortcuts (e.g. `goto work`)
- `gpu`: show NVIDIA GPU status (`nvidia-smi` wrapper; Windows/Ubuntu only)
- Optional: auto-activate a Conda env when a new shell starts

This skill is intentionally opinionated:

- Prefer PowerShell on Windows for the full `goto` experience.
- Keep everything idempotent by putting functions/scripts behind a clearly-marked block.

## Defaults (edit as needed)

- HTTP/HTTPS proxy: `http://127.0.0.1:7890`
- SOCKS5 proxy: `socks5://127.0.0.1:7890`
- NO_PROXY: `localhost,127.0.0.1,.qualcomm.com,*.amazonaws.com`

## Windows: PowerShell (recommended)

Edit your PowerShell profile: `$PROFILE`

Add (or replace) a block like below. The `goto` DB is `$HOME\.goto_paths.json`.

```powershell
# >>> shell-shortcuts >>>

function proxy_off {
  param([switch]$Quiet)
  Remove-Item Env:http_proxy,Env:https_proxy,Env:all_proxy,Env:no_proxy -ErrorAction SilentlyContinue
  Remove-Item Env:HTTP_PROXY,Env:HTTPS_PROXY,Env:ALL_PROXY,Env:NO_PROXY -ErrorAction SilentlyContinue

  if (Get-Command git -ErrorAction SilentlyContinue) {
    git config --global --unset http.proxy 2>$null | Out-Null
    git config --global --unset https.proxy 2>$null | Out-Null
  }

  if (-not $Quiet) { Write-Host "Proxy is OFF" }
}

function proxy_on {
  param(
    [string]$HttpProxyUrl = "http://127.0.0.1:7890",
    [string]$SocksProxyUrl = "socks5://127.0.0.1:7890",
    [string]$NoProxyList = "localhost,127.0.0.1,.qualcomm.com,*.amazonaws.com"
  )

  proxy_off -Quiet

  $env:http_proxy  = $HttpProxyUrl
  $env:https_proxy = $HttpProxyUrl
  $env:HTTP_PROXY  = $HttpProxyUrl
  $env:HTTPS_PROXY = $HttpProxyUrl

  $env:all_proxy = $SocksProxyUrl
  $env:ALL_PROXY = $SocksProxyUrl

  $env:no_proxy = $NoProxyList
  $env:NO_PROXY = $NoProxyList

  if (Get-Command git -ErrorAction SilentlyContinue) {
    git config --global http.proxy  $HttpProxyUrl  | Out-Null
    git config --global https.proxy $HttpProxyUrl  | Out-Null
  }

  Write-Host "Proxy is ON"
  Write-Host "  HTTP/HTTPS: $HttpProxyUrl"
  Write-Host "  SOCKS5:     $SocksProxyUrl"
  Write-Host "  NO_PROXY:   $NoProxyList"
}

function _goto_db_path {
  Join-Path $HOME ".goto_paths.json"
}

function _goto_load {
  $db = _goto_db_path
  if (-not (Test-Path -LiteralPath $db)) { return @{} }
  try {
    $raw = Get-Content -Raw -Encoding UTF8 -LiteralPath $db
    if (-not $raw.Trim()) { return @{} }
    $obj = $raw | ConvertFrom-Json
    $ht = @{}
    foreach ($p in $obj.PSObject.Properties) { $ht[$p.Name] = [string]$p.Value }
    return $ht
  } catch {
    throw "Failed to parse goto DB: $db. Fix JSON or delete it."
  }
}

function _goto_save([hashtable]$ht) {
  $db = _goto_db_path
  $dir = Split-Path -Parent $db
  if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
  ($ht | ConvertTo-Json -Depth 5) | Set-Content -Encoding UTF8 -LiteralPath $db
}

function goto {
  param(
    [Parameter(Position = 0)][string]$Cmd,
    [Parameter(ValueFromRemainingArguments = $true)][string[]]$Rest
  )

  $ht = _goto_load

  switch ($Cmd) {
    { $_ -in @($null, "", "ls", "list") } {
      if ($ht.Count -eq 0) { Write-Host "No shortcuts. Use: goto add <key> <path>"; return }
      Write-Host "Available shortcuts:"
      foreach ($k in ($ht.Keys | Sort-Object)) {
        "{0,-12} -> {1}" -f $k, $ht[$k] | Write-Host
      }
      return
    }
    "add" {
      if ($Rest.Count -lt 2) { throw "Usage: goto add <shortcut> <path>" }
      $key = $Rest[0]
      $path = ($Rest | Select-Object -Skip 1) -join " "
      if ($path -like "~*") { $path = $path -replace "^~", $HOME }
      $resolved = Resolve-Path -LiteralPath $path -ErrorAction Stop
      $ht[$key] = $resolved.Path
      _goto_save $ht
      Write-Host "Added: $key -> $($ht[$key])"
      return
    }
    { $_ -in @("rm","remove","del") } {
      if ($Rest.Count -ne 1) { throw "Usage: goto remove <shortcut>" }
      $key = $Rest[0]
      $ht.Remove($key) | Out-Null
      _goto_save $ht
      Write-Host "Removed: $key"
      return
    }
    "clear" {
      _goto_save @{}
      Write-Host "All shortcuts cleared."
      return
    }
    default {
      if (-not $Cmd) { return }
      if (-not $ht.ContainsKey($Cmd)) {
        Write-Host "Unknown shortcut: $Cmd"
        Write-Host "Tip: goto list"
        return 1
      }
      Set-Location -LiteralPath $ht[$Cmd]
      return
    }
  }
}

function gpu {
  $cmd = Get-Command nvidia-smi -ErrorAction SilentlyContinue
  if (-not $cmd) {
    Write-Host "nvidia-smi not found (need NVIDIA driver/tools)."
    return 1
  }
  & $cmd.Path
}

# Optional: Conda auto-activate (edit these)
# $CondaRoot = "D:\\ProgramData\\miniconda3"
# $CondaEnv  = "wayne3.10"
# if (Test-Path -LiteralPath (Join-Path $CondaRoot "Scripts\\conda.exe")) {
#   $hook = (& (Join-Path $CondaRoot "Scripts\\conda.exe") "shell.powershell" "hook") 2>$null | Out-String
#   if ($hook) { Invoke-Expression $hook }
#   conda activate $CondaEnv
# }

# <<< shell-shortcuts <<<
```

Usage:

```powershell
proxy_on
proxy_off
goto list
goto add work D:\work
goto work
gpu
```

## Windows: CMD (optional)

CMD has a reserved `goto` keyword. Use `jump` as the real command, and optionally alias `goto` to `jump` for interactive sessions via `doskey`.

Recommended layout:

- Put scripts in `C:\Users\<You>\bin\`
- Add that folder to PATH (or do it in your CMD startup script)

Create `C:\Users\<You>\cmd_startup.cmd`:

```bat
@echo off
set "PATH=%USERPROFILE%\bin;%PATH%"

REM Optional: conda auto-activate (edit these)
REM call "D:\ProgramData\miniconda3\condabin\conda.bat" activate wayne3.10

REM Interactive alias only (scripts/cmd /c should call jump directly)
doskey goto=jump $*
```

Enable AutoRun (current user):

```bat
reg add "HKCU\Software\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d "%USERPROFILE%\cmd_startup.cmd" /f
```

Implement these `.cmd` files under `%USERPROFILE%\bin`:

`proxy_on.cmd` / `proxy_off.cmd`: set/unset proxy env vars and set/unset Git global proxy.

`gpu.cmd`: run `nvidia-smi`.

`jump.cmd`: persistent shortcut DB at `%USERPROFILE%\.goto_paths` (format: `key|C:\abs\path`).

If you need exact templates, read `shell-shortcuts/references/windows-cmd.md`.

## macOS / Ubuntu (bash/zsh)

Add functions to `~/.zshrc` or `~/.bashrc`:

- `proxy_on` / `proxy_off`
- `goto` (persistent DB at `~/.goto_paths`)
- Ubuntu: `gpu` (requires `nvidia-smi`)

Templates are in `shell-shortcuts/references/unix.md` (copy/paste and adjust proxy defaults).
