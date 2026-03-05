# ============================================================
# app-control.ps1 — Window Management for OpenClaw
# Actions: list-windows, launch, focus, close, minimize,
#          maximize, restore, move, resize, snap, help
# ============================================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("list-windows","launch","focus","close","minimize","maximize","restore","move","resize","snap","help")]
    [string]$Action,

    [string]$Target = "",
    [int]$ProcId = 0,
    [string]$Arguments = "",
    [int]$X = -1,
    [int]$Y = -1,
    [int]$Width = -1,
    [int]$Height = -1,
    [ValidateSet("left","right","top","bottom","topleft","topright","bottomleft","bottomright","")]
    [string]$Position = ""
)

# --- Win32 API ---
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
using System.Collections.Generic;

public class Win32Window {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool IsZoomed(IntPtr hWnd);
    [DllImport("user32.dll", SetLastError=true, CharSet=CharSet.Auto)]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")] public static extern int GetWindowTextLength(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern IntPtr SetFocus(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, IntPtr lpdwProcessId);

    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left, Top, Right, Bottom; }

    public const int SW_HIDE = 0;
    public const int SW_NORMAL = 1;
    public const int SW_MINIMIZE = 6;
    public const int SW_MAXIMIZE = 3;
    public const int SW_RESTORE = 9;
    public const int SW_SHOW = 5;

    public static void ForceForeground(IntPtr hWnd) {
        IntPtr fg = GetForegroundWindow();
        uint fgThread = GetWindowThreadProcessId(fg, IntPtr.Zero);
        uint curThread = GetCurrentThreadId();
        if (fgThread != curThread) {
            AttachThreadInput(curThread, fgThread, true);
            BringWindowToTop(hWnd);
            ShowWindow(hWnd, SW_SHOW);
            AttachThreadInput(curThread, fgThread, false);
        }
        SetForegroundWindow(hWnd);
    }
}
"@

# --- Helpers ---
function Get-AllWindows {
    $windows = [System.Collections.ArrayList]::new()
    $callback = [Win32Window+EnumWindowsProc]{
        param($hWnd, $lParam)
        if ([Win32Window]::IsWindowVisible($hWnd)) {
            $len = [Win32Window]::GetWindowTextLength($hWnd)
            if ($len -gt 0) {
                $sb = New-Object System.Text.StringBuilder($len + 1)
                [Win32Window]::GetWindowText($hWnd, $sb, $sb.Capacity) | Out-Null
                $title = $sb.ToString()
                $wpid = [uint32]0
                [Win32Window]::GetWindowThreadProcessId($hWnd, [ref]$wpid) | Out-Null
                $rect = New-Object Win32Window+RECT
                [Win32Window]::GetWindowRect($hWnd, [ref]$rect) | Out-Null
                $state = "Normal"
                if ([Win32Window]::IsIconic($hWnd)) { $state = "Minimized" }
                elseif ([Win32Window]::IsZoomed($hWnd)) { $state = "Maximized" }
                $null = $windows.Add([PSCustomObject]@{
                    Handle = $hWnd
                    WinPID = $wpid
                    Title  = $title
                    X      = $rect.Left
                    Y      = $rect.Top
                    Width  = $rect.Right - $rect.Left
                    Height = $rect.Bottom - $rect.Top
                    State  = $state
                })
            }
        }
        return $true
    }
    [Win32Window]::EnumWindows($callback, [IntPtr]::Zero) | Out-Null
    return $windows
}

function Find-Window {
    param([string]$TitlePattern, [int]$ByProcId = 0)
    $all = Get-AllWindows
    if ($ByProcId -gt 0) {
        return $all | Where-Object { $_.WinPID -eq $ByProcId } | Select-Object -First 1
    }
    if ($TitlePattern) {
        $match = $all | Where-Object { $_.Title -eq $TitlePattern } | Select-Object -First 1
        if (-not $match) {
            $match = $all | Where-Object { $_.Title -like "*$TitlePattern*" } | Select-Object -First 1
        }
        return $match
    }
    return $null
}

function Get-ScreenSize {
    Add-Type -AssemblyName System.Windows.Forms
    $screen = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
    return @{ Width = $screen.Width; Height = $screen.Height; X = $screen.X; Y = $screen.Y }
}

# --- Actions ---
try {
    switch ($Action) {
        "help" {
            Write-Output @"
desktop-control / app-control.ps1
Actions:
  list-windows              List all visible windows
  launch    -Target <path>  Launch an application [-Arguments <args>]
  focus     -Target <title> Bring window to foreground [-ProcId <pid>]
  close     -Target <title> Close a window gracefully [-ProcId <pid>]
  minimize  -Target <title> Minimize a window [-ProcId <pid>]
  maximize  -Target <title> Maximize a window [-ProcId <pid>]
  restore   -Target <title> Restore a window [-ProcId <pid>]
  move      -Target <title> Move window -X <x> -Y <y>
  resize    -Target <title> Resize window -Width <w> -Height <h>
  snap      -Target <title> Snap window -Position <left|right|...>
"@
        }

        "list-windows" {
            $wins = Get-AllWindows | Where-Object { $_.Width -gt 0 -and $_.Height -gt 0 }
            $wins | ForEach-Object {
                Write-Output ("PID={0}  State={1}  Pos=({2},{3})  Size={4}x{5}  Title=""{6}""" -f $_.WinPID, $_.State, $_.X, $_.Y, $_.Width, $_.Height, $_.Title)
            }
            Write-Output ""
            Write-Output "Total: $($wins.Count) windows"
        }

        "launch" {
            if (-not $Target) { Write-Error "Missing -Target (application path or name)"; exit 1 }
            if ($Arguments) {
                $proc = Start-Process -FilePath $Target -ArgumentList $Arguments -PassThru
            } else {
                $proc = Start-Process -FilePath $Target -PassThru
            }
            Start-Sleep -Milliseconds 500
            Write-Output "Launched: $Target (PID=$($proc.Id))"
        }

        "focus" {
            $win = Find-Window -TitlePattern $Target -ByProcId $ProcId
            if (-not $win) { Write-Error "Window not found: '$Target' (ProcId=$ProcId)"; exit 1 }
            if ([Win32Window]::IsIconic($win.Handle)) {
                [Win32Window]::ShowWindow($win.Handle, [Win32Window]::SW_RESTORE) | Out-Null
            }
            [Win32Window]::ForceForeground($win.Handle)
            Write-Output "Focused: ""$($win.Title)"" (PID=$($win.WinPID))"
        }

        "close" {
            $win = Find-Window -TitlePattern $Target -ByProcId $ProcId
            if (-not $win) { Write-Error "Window not found: '$Target'"; exit 1 }
            $proc = Get-Process -Id $win.WinPID -ErrorAction SilentlyContinue
            if ($proc) {
                $proc.CloseMainWindow() | Out-Null
                Write-Output "Close signal sent: ""$($win.Title)"" (PID=$($win.WinPID))"
            } else {
                Write-Error "Process not found for PID=$($win.WinPID)"; exit 1
            }
        }

        "minimize" {
            $win = Find-Window -TitlePattern $Target -ByProcId $ProcId
            if (-not $win) { Write-Error "Window not found: '$Target'"; exit 1 }
            [Win32Window]::ShowWindow($win.Handle, [Win32Window]::SW_MINIMIZE) | Out-Null
            Write-Output "Minimized: ""$($win.Title)"""
        }

        "maximize" {
            $win = Find-Window -TitlePattern $Target -ByProcId $ProcId
            if (-not $win) { Write-Error "Window not found: '$Target'"; exit 1 }
            [Win32Window]::ShowWindow($win.Handle, [Win32Window]::SW_MAXIMIZE) | Out-Null
            Write-Output "Maximized: ""$($win.Title)"""
        }

        "restore" {
            $win = Find-Window -TitlePattern $Target -ByProcId $ProcId
            if (-not $win) { Write-Error "Window not found: '$Target'"; exit 1 }
            [Win32Window]::ShowWindow($win.Handle, [Win32Window]::SW_RESTORE) | Out-Null
            Write-Output "Restored: ""$($win.Title)"""
        }

        "move" {
            $win = Find-Window -TitlePattern $Target -ByProcId $ProcId
            if (-not $win) { Write-Error "Window not found: '$Target'"; exit 1 }
            $newX = if ($X -ge 0) { $X } else { $win.X }
            $newY = if ($Y -ge 0) { $Y } else { $win.Y }
            [Win32Window]::MoveWindow($win.Handle, $newX, $newY, $win.Width, $win.Height, $true) | Out-Null
            Write-Output "Moved: ""$($win.Title)"" to ($newX, $newY)"
        }

        "resize" {
            $win = Find-Window -TitlePattern $Target -ByProcId $ProcId
            if (-not $win) { Write-Error "Window not found: '$Target'"; exit 1 }
            $newW = if ($Width -gt 0) { $Width } else { $win.Width }
            $newH = if ($Height -gt 0) { $Height } else { $win.Height }
            [Win32Window]::MoveWindow($win.Handle, $win.X, $win.Y, $newW, $newH, $true) | Out-Null
            Write-Output "Resized: ""$($win.Title)"" to ${newW}x${newH}"
        }

        "snap" {
            if (-not $Position) { Write-Error "Missing -Position"; exit 1 }
            $win = Find-Window -TitlePattern $Target -ByProcId $ProcId
            if (-not $win) { Write-Error "Window not found: '$Target'"; exit 1 }
            if ([Win32Window]::IsZoomed($win.Handle)) {
                [Win32Window]::ShowWindow($win.Handle, [Win32Window]::SW_RESTORE) | Out-Null
                Start-Sleep -Milliseconds 100
            }
            $scr = Get-ScreenSize
            $hw = [math]::Floor($scr.Width / 2)
            $hh = [math]::Floor($scr.Height / 2)
            switch ($Position) {
                "left"        { $sx=$scr.X;       $sy=$scr.Y;       $sw=$hw;          $sh=$scr.Height }
                "right"       { $sx=$scr.X+$hw;   $sy=$scr.Y;       $sw=$hw;          $sh=$scr.Height }
                "top"         { $sx=$scr.X;       $sy=$scr.Y;       $sw=$scr.Width;   $sh=$hh         }
                "bottom"      { $sx=$scr.X;       $sy=$scr.Y+$hh;   $sw=$scr.Width;   $sh=$hh         }
                "topleft"     { $sx=$scr.X;       $sy=$scr.Y;       $sw=$hw;          $sh=$hh         }
                "topright"    { $sx=$scr.X+$hw;   $sy=$scr.Y;       $sw=$hw;          $sh=$hh         }
                "bottomleft"  { $sx=$scr.X;       $sy=$scr.Y+$hh;   $sw=$hw;          $sh=$hh         }
                "bottomright" { $sx=$scr.X+$hw;   $sy=$scr.Y+$hh;   $sw=$hw;          $sh=$hh         }
            }
            [Win32Window]::MoveWindow($win.Handle, $sx, $sy, $sw, $sh, $true) | Out-Null
            Write-Output "Snapped: ""$($win.Title)"" to $Position (${sw}x${sh} at ${sx},${sy})"
        }
    }
    exit 0
} catch {
    Write-Error "ERROR: $_"
    exit 1
}
