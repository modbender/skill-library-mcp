# screen-info.ps1 - Screen and System Info for OpenClaw
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("displays","active-window","window-info","screenshot","clipboard-get","clipboard-set","system-info","help")]
    [string]$Action,
    [string]$Target = "",
    [string]$OutputPath = "",
    [string]$Text = ""
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class ScreenHelper {
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll", CharSet=CharSet.Auto)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder sb, int maxCount);
    [DllImport("user32.dll")] public static extern int GetWindowTextLength(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
    [DllImport("user32.dll", CharSet=CharSet.Auto)] public static extern int GetClassName(IntPtr hWnd, StringBuilder sb, int maxCount);
    [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool IsZoomed(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr lParam);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
}
"@

function Get-WindowDetails([IntPtr]$hWnd) {
    $sb = New-Object System.Text.StringBuilder(256)
    [ScreenHelper]::GetWindowText($hWnd, $sb, 256) | Out-Null
    $title = $sb.ToString()
    $sb.Clear() | Out-Null
    [ScreenHelper]::GetClassName($hWnd, $sb, 256) | Out-Null
    $class = $sb.ToString()
    $procId = [uint32]0
    [ScreenHelper]::GetWindowThreadProcessId($hWnd, [ref]$procId) | Out-Null
    $rect = New-Object ScreenHelper+RECT
    [ScreenHelper]::GetWindowRect($hWnd, [ref]$rect) | Out-Null
    $state = "Normal"
    if ([ScreenHelper]::IsIconic($hWnd)) { $state = "Minimized" }
    elseif ([ScreenHelper]::IsZoomed($hWnd)) { $state = "Maximized" }
    return @{
        Handle=$hWnd; Title=$title; Class=$class; PID=$procId
        X=$rect.Left; Y=$rect.Top
        Width=$rect.Right-$rect.Left; Height=$rect.Bottom-$rect.Top
        State=$state
    }
}

function Find-WindowByTitle([string]$pattern) {
    $script:result = $null
    $cb = [ScreenHelper+EnumWindowsProc]{
        param($h,$l)
        if ([ScreenHelper]::IsWindowVisible($h)) {
            $len = [ScreenHelper]::GetWindowTextLength($h)
            if ($len -gt 0) {
                $s = New-Object System.Text.StringBuilder($len+1)
                [ScreenHelper]::GetWindowText($h, $s, $s.Capacity) | Out-Null
                if ($s.ToString() -like "*$pattern*") {
                    $script:result = $h
                    return $false
                }
            }
        }
        return $true
    }
    [ScreenHelper]::EnumWindows($cb, [IntPtr]::Zero) | Out-Null
    return $script:result
}

try {
    switch ($Action) {
        "help" {
            Write-Output "screen-info.ps1 - displays, active-window, window-info, screenshot, clipboard-get, clipboard-set, system-info"
        }
        "displays" {
            $screens = [System.Windows.Forms.Screen]::AllScreens
            $i = 0
            foreach ($s in $screens) {
                $i++
                $p = if($s.Primary){"(Primary)"}else{""}
                Write-Output "Display #$i $p"
                Write-Output "  Device:     $($s.DeviceName)"
                Write-Output "  Resolution: $($s.Bounds.Width)x$($s.Bounds.Height)"
                Write-Output "  Position:   ($($s.Bounds.X), $($s.Bounds.Y))"
                Write-Output "  WorkArea:   $($s.WorkingArea.Width)x$($s.WorkingArea.Height)"
                Write-Output "  BitsPerPx:  $($s.BitsPerPixel)"
                Write-Output ""
            }
            Write-Output "Total: $i display(s)"
        }
        "active-window" {
            $hw = [ScreenHelper]::GetForegroundWindow()
            if ($hw -eq [IntPtr]::Zero) { Write-Error "No active window"; exit 1 }
            $d = Get-WindowDetails $hw
            Write-Output "Active Window:"
            Write-Output "  Title:  $($d.Title)"
            Write-Output "  Class:  $($d.Class)"
            Write-Output "  PID:    $($d.PID)"
            Write-Output "  Pos:    ($($d.X), $($d.Y))"
            Write-Output "  Size:   $($d.Width)x$($d.Height)"
            Write-Output "  State:  $($d.State)"
        }
        "window-info" {
            if (-not $Target) { Write-Error "Missing -Target"; exit 1 }
            $hw = Find-WindowByTitle $Target
            if (-not $hw -or $hw -eq [IntPtr]::Zero) { Write-Error "Window not found: '$Target'"; exit 1 }
            $d = Get-WindowDetails $hw
            Write-Output "Window Info:"
            Write-Output "  Title:  $($d.Title)"
            Write-Output "  Class:  $($d.Class)"
            Write-Output "  PID:    $($d.PID)"
            Write-Output "  Pos:    ($($d.X), $($d.Y))"
            Write-Output "  Size:   $($d.Width)x$($d.Height)"
            Write-Output "  State:  $($d.State)"
        }
        "screenshot" {
            $outPath = if($OutputPath){$OutputPath}else{"$env:USERPROFILE\screenshot_$(Get-Date -Format 'yyyyMMdd_HHmmss').png"}
            if ($Target) {
                $hw = Find-WindowByTitle $Target
                if (-not $hw -or $hw -eq [IntPtr]::Zero) { Write-Error "Window not found: '$Target'"; exit 1 }
                $rect = New-Object ScreenHelper+RECT
                [ScreenHelper]::GetWindowRect($hw, [ref]$rect) | Out-Null
                $w = $rect.Right - $rect.Left; $h = $rect.Bottom - $rect.Top
                $bmp = New-Object System.Drawing.Bitmap($w, $h)
                $g = [System.Drawing.Graphics]::FromImage($bmp)
                $g.CopyFromScreen($rect.Left, $rect.Top, 0, 0, [System.Drawing.Size]::new($w,$h))
                $g.Dispose()
            } else {
                $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
                $bmp = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height)
                $g = [System.Drawing.Graphics]::FromImage($bmp)
                $g.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
                $g.Dispose()
            }
            $bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
            $bmp.Dispose()
            Write-Output "Screenshot saved: $outPath"
        }
        "clipboard-get" {
            $clip = [System.Windows.Forms.Clipboard]::GetText()
            if ($clip) {
                Write-Output "Clipboard content:"
                Write-Output "---"
                Write-Output $clip
                Write-Output "---"
                Write-Output "($($clip.Length) characters)"
            } else { Write-Output "Clipboard is empty or contains non-text data." }
        }
        "clipboard-set" {
            if (-not $Text) { Write-Error "Missing -Text"; exit 1 }
            [System.Windows.Forms.Clipboard]::SetText($Text)
            Write-Output "Clipboard set ($($Text.Length) characters)"
        }
        "system-info" {
            $os = Get-CimInstance Win32_OperatingSystem
            $cs = Get-CimInstance Win32_ComputerSystem
            $uptime = (Get-Date) - $os.LastBootUpTime
            Write-Output "System Info:"
            Write-Output "  Computer:   $($cs.Name)"
            Write-Output "  OS:         $($os.Caption) $($os.Version)"
            Write-Output "  RAM:        $([math]::Round($cs.TotalPhysicalMemory/1GB,1)) GB"
            Write-Output "  Free RAM:   $([math]::Round($os.FreePhysicalMemory/1MB,1)) GB"
            Write-Output "  Uptime:     $($uptime.Days)d $($uptime.Hours)h $($uptime.Minutes)m"
            Write-Output "  User:       $env:USERNAME"
            $screens = [System.Windows.Forms.Screen]::AllScreens
            Write-Output "  Displays:   $($screens.Count)"
            foreach ($s in $screens) {
                $p = if($s.Primary){"*"}else{""}
                Write-Output "    $p $($s.DeviceName): $($s.Bounds.Width)x$($s.Bounds.Height)"
            }
        }
    }
    exit 0
} catch { Write-Error "ERROR: $_"; exit 1 }
