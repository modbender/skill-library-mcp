# ============================================================
# vscode-control.ps1 — VSCode Control for OpenClaw
# Actions: open-file, open-folder, open-diff, goto,
#          list-extensions, install-extension, uninstall-extension,
#          new-terminal, command-palette, run-command, status, help
# ============================================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("open-file","open-folder","open-diff","goto","list-extensions","install-extension","uninstall-extension","new-terminal","command-palette","run-command","status","help")]
    [string]$Action,

    [string]$Path = "",
    [string]$Path2 = "",
    [int]$Line = 0,
    [int]$Column = 0,
    [string]$ExtensionId = "",
    [string]$Command = "",
    [switch]$NewWindow,
    [switch]$Reuse
)

# --- Locate code CLI ---
function Find-VSCodeCLI {
    # Try 'code' in PATH first
    $codePath = Get-Command "code" -ErrorAction SilentlyContinue
    if ($codePath) { return $codePath.Source }

    # Common install locations
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd",
        "$env:ProgramFiles\Microsoft VS Code\bin\code.cmd",
        "${env:ProgramFiles(x86)}\Microsoft VS Code\bin\code.cmd",
        "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe",
        "$env:ProgramFiles\Microsoft VS Code\Code.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { return $c }
    }

    # VSCode Insiders
    $insiders = Get-Command "code-insiders" -ErrorAction SilentlyContinue
    if ($insiders) { return $insiders.Source }

    return $null
}

$codeCLI = Find-VSCodeCLI
if (-not $codeCLI -and $Action -ne "help") {
    Write-Error "VSCode CLI ('code') not found. Make sure VSCode is installed and 'code' is in PATH."
    Write-Error "Tip: Open VSCode, press Ctrl+Shift+P, type 'Shell Command: Install code command in PATH'"
    exit 1
}

# --- Helper to focus VSCode window ---
function Focus-VSCode {
    Add-Type @"
    using System;
    using System.Runtime.InteropServices;
    using System.Text;
    public class VSCFocus {
        [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
        [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
        [DllImport("user32.dll", CharSet=CharSet.Auto)]
        public static extern int GetWindowText(IntPtr hWnd, StringBuilder sb, int maxCount);
        [DllImport("user32.dll")] public static extern int GetWindowTextLength(IntPtr hWnd);
        [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
        [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
        [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
        public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    }
"@
    $found = $false
    $callback = [VSCFocus+EnumWindowsProc]{
        param($hWnd, $lParam)
        if ([VSCFocus]::IsWindowVisible($hWnd)) {
            $len = [VSCFocus]::GetWindowTextLength($hWnd)
            if ($len -gt 0) {
                $sb = New-Object System.Text.StringBuilder($len + 1)
                [VSCFocus]::GetWindowText($hWnd, $sb, $sb.Capacity) | Out-Null
                if ($sb.ToString() -like "*Visual Studio Code*") {
                    if ([VSCFocus]::IsIconic($hWnd)) {
                        [VSCFocus]::ShowWindow($hWnd, 9) | Out-Null
                    }
                    [VSCFocus]::SetForegroundWindow($hWnd) | Out-Null
                    $script:found = $true
                    return $false  # Stop enumeration
                }
            }
        }
        return $true
    }
    [VSCFocus]::EnumWindows($callback, [IntPtr]::Zero) | Out-Null
}

try {
    switch ($Action) {
        "help" {
            Write-Output @"
desktop-control / vscode-control.ps1
Actions:
  open-file    -Path <file>                  Open a file in VSCode
  goto         -Path <file> -Line <n>        Open file at line[:column]
  open-folder  -Path <folder>                Open folder/workspace [-NewWindow]
  open-diff    -Path <file1> -Path2 <file2>  Diff two files
  list-extensions                             List installed extensions
  install-extension   -ExtensionId <id>      Install extension (e.g. "ms-python.python")
  uninstall-extension -ExtensionId <id>      Uninstall extension
  new-terminal                                Open/toggle integrated terminal
  command-palette                             Open command palette (Ctrl+Shift+P)
  run-command  -Command <cmd>                Run a VSCode command by ID
  status                                      Show VSCode version and status
"@
        }

        "open-file" {
            if (-not $Path) { Write-Error "Missing -Path parameter"; exit 1 }
            $resolvedPath = Resolve-Path $Path -ErrorAction SilentlyContinue
            if (-not $resolvedPath) { $resolvedPath = $Path }
            $args_ = @("--goto", "$resolvedPath")
            if ($Reuse) { $args_ += "--reuse-window" }
            & $codeCLI @args_
            Write-Output "Opened in VSCode: $resolvedPath"
        }

        "goto" {
            if (-not $Path) { Write-Error "Missing -Path parameter"; exit 1 }
            if ($Line -le 0) { Write-Error "Missing -Line parameter"; exit 1 }
            $resolvedPath = Resolve-Path $Path -ErrorAction SilentlyContinue
            if (-not $resolvedPath) { $resolvedPath = $Path }
            $location = "${resolvedPath}:${Line}"
            if ($Column -gt 0) { $location += ":${Column}" }
            & $codeCLI --goto $location
            Write-Output "Opened in VSCode: $location"
        }

        "open-folder" {
            if (-not $Path) { Write-Error "Missing -Path parameter"; exit 1 }
            $resolvedPath = Resolve-Path $Path -ErrorAction SilentlyContinue
            if (-not $resolvedPath) { $resolvedPath = $Path }
            $args_ = @("$resolvedPath")
            if ($NewWindow) { $args_ += "--new-window" }
            & $codeCLI @args_
            Write-Output "Opened folder in VSCode: $resolvedPath"
        }

        "open-diff" {
            if (-not $Path -or -not $Path2) { Write-Error "Missing -Path and -Path2 parameters"; exit 1 }
            $r1 = Resolve-Path $Path -ErrorAction SilentlyContinue
            $r2 = Resolve-Path $Path2 -ErrorAction SilentlyContinue
            if (-not $r1) { $r1 = $Path }
            if (-not $r2) { $r2 = $Path2 }
            & $codeCLI --diff "$r1" "$r2"
            Write-Output "Opened diff: $r1 <-> $r2"
        }

        "list-extensions" {
            Write-Output "Installed VSCode extensions:"
            Write-Output "---"
            & $codeCLI --list-extensions --show-versions
        }

        "install-extension" {
            if (-not $ExtensionId) { Write-Error "Missing -ExtensionId parameter"; exit 1 }
            Write-Output "Installing extension: $ExtensionId ..."
            & $codeCLI --install-extension $ExtensionId --force
            if ($LASTEXITCODE -eq 0) {
                Write-Output "Successfully installed: $ExtensionId"
            } else {
                Write-Error "Failed to install: $ExtensionId"; exit 1
            }
        }

        "uninstall-extension" {
            if (-not $ExtensionId) { Write-Error "Missing -ExtensionId parameter"; exit 1 }
            Write-Output "Uninstalling extension: $ExtensionId ..."
            & $codeCLI --uninstall-extension $ExtensionId
            if ($LASTEXITCODE -eq 0) {
                Write-Output "Successfully uninstalled: $ExtensionId"
            } else {
                Write-Error "Failed to uninstall: $ExtensionId"; exit 1
            }
        }

        "new-terminal" {
            Focus-VSCode
            Start-Sleep -Milliseconds 300
            Add-Type -AssemblyName System.Windows.Forms
            # Ctrl+` toggles terminal
            [System.Windows.Forms.SendKeys]::SendWait("^``")
            Write-Output "Toggled integrated terminal in VSCode"
        }

        "command-palette" {
            Focus-VSCode
            Start-Sleep -Milliseconds 300
            Add-Type -AssemblyName System.Windows.Forms
            # Ctrl+Shift+P opens command palette
            [System.Windows.Forms.SendKeys]::SendWait("^+p")
            Write-Output "Opened command palette in VSCode"
        }

        "run-command" {
            if (-not $Command) { Write-Error "Missing -Command parameter (e.g. 'workbench.action.toggleSidebarVisibility')"; exit 1 }
            # Use the code CLI to execute a command via extension
            # Fallback: focus VSCode, open command palette, type the command
            Focus-VSCode
            Start-Sleep -Milliseconds 300
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait("^+p")
            Start-Sleep -Milliseconds 500
            $escaped = $Command -replace '([\+\^\%\~\(\)\{\}\[\]])', '{$1}'
            [System.Windows.Forms.SendKeys]::SendWait($escaped)
            Start-Sleep -Milliseconds 200
            [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
            Write-Output "Executed VSCode command: $Command"
        }

        "status" {
            Write-Output "VSCode Status:"
            Write-Output "---"
            & $codeCLI --version
            Write-Output "---"
            $vscProcs = Get-Process -Name "Code" -ErrorAction SilentlyContinue
            if ($vscProcs) {
                $totalMem = ($vscProcs | Measure-Object -Property WorkingSet64 -Sum).Sum / 1MB
                Write-Output "Running: Yes ($($vscProcs.Count) processes, $([math]::Round($totalMem))MB total memory)"
            } else {
                Write-Output "Running: No"
            }
        }
    }
    exit 0
} catch {
    Write-Error "ERROR: $_"
    exit 1
}
