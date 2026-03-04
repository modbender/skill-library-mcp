# ============================================================
# input-sim.ps1 — Keyboard & Mouse Input Simulation for OpenClaw
# Actions: type-text, send-keys, mouse-click, mouse-move,
#          mouse-scroll, help
# ============================================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("type-text","send-keys","mouse-click","mouse-move","mouse-scroll","help")]
    [string]$Action,

    [string]$Text = "",
    [string]$Keys = "",
    [int]$X = -1,
    [int]$Y = -1,
    [ValidateSet("left","right","middle","")]
    [string]$Button = "left",
    [switch]$DoubleClick,
    [int]$Clicks = 0,
    [int]$DelayMs = 50
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;

public class InputSim {
    [DllImport("user32.dll")] public static extern void SetCursorPos(int X, int Y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, int dx, int dy, int dwData, IntPtr dwExtraInfo);
    [DllImport("user32.dll")] public static extern bool GetCursorPos(out POINT lpPoint);

    [StructLayout(LayoutKind.Sequential)]
    public struct POINT { public int X; public int Y; }

    public const uint MOUSEEVENTF_LEFTDOWN   = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP     = 0x0004;
    public const uint MOUSEEVENTF_RIGHTDOWN  = 0x0008;
    public const uint MOUSEEVENTF_RIGHTUP    = 0x0010;
    public const uint MOUSEEVENTF_MIDDLEDOWN = 0x0020;
    public const uint MOUSEEVENTF_MIDDLEUP   = 0x0040;
    public const uint MOUSEEVENTF_WHEEL      = 0x0800;
    public const uint MOUSEEVENTF_ABSOLUTE   = 0x8000;
    public const uint MOUSEEVENTF_MOVE       = 0x0001;
}
"@

# --- Key Mapping for SendKeys ---
function ConvertTo-SendKeysFormat {
    param([string]$KeyCombo)
    # Parse combos like "Ctrl+Shift+P", "Alt+F4", "F5", "Enter"
    $parts = $KeyCombo -split '\+'
    $modifiers = ""
    $key = ""
    foreach ($part in $parts) {
        switch ($part.Trim().ToLower()) {
            "ctrl"    { $modifiers += "^" }
            "control" { $modifiers += "^" }
            "alt"     { $modifiers += "%" }
            "shift"   { $modifiers += "+" }
            "win"     { # Win key handled separately
                        $modifiers += "^{ESC}" # Approximation
                      }
            "enter"     { $key = "{ENTER}" }
            "return"    { $key = "{ENTER}" }
            "tab"       { $key = "{TAB}" }
            "escape"    { $key = "{ESC}" }
            "esc"       { $key = "{ESC}" }
            "backspace" { $key = "{BACKSPACE}" }
            "delete"    { $key = "{DELETE}" }
            "del"       { $key = "{DELETE}" }
            "up"        { $key = "{UP}" }
            "down"      { $key = "{DOWN}" }
            "left"      { $key = "{LEFT}" }
            "right"     { $key = "{RIGHT}" }
            "home"      { $key = "{HOME}" }
            "end"       { $key = "{END}" }
            "pageup"    { $key = "{PGUP}" }
            "pgup"      { $key = "{PGUP}" }
            "pagedown"  { $key = "{PGDN}" }
            "pgdn"      { $key = "{PGDN}" }
            "space"     { $key = " " }
            "insert"    { $key = "{INSERT}" }
            "ins"       { $key = "{INSERT}" }
            "capslock"  { $key = "{CAPSLOCK}" }
            "numlock"   { $key = "{NUMLOCK}" }
            "scrolllock"{ $key = "{SCROLLLOCK}" }
            "prtsc"     { $key = "{PRTSC}" }
            "break"     { $key = "{BREAK}" }
            "f1"  { $key = "{F1}" }
            "f2"  { $key = "{F2}" }
            "f3"  { $key = "{F3}" }
            "f4"  { $key = "{F4}" }
            "f5"  { $key = "{F5}" }
            "f6"  { $key = "{F6}" }
            "f7"  { $key = "{F7}" }
            "f8"  { $key = "{F8}" }
            "f9"  { $key = "{F9}" }
            "f10" { $key = "{F10}" }
            "f11" { $key = "{F11}" }
            "f12" { $key = "{F12}" }
            default {
                $k = $part.Trim()
                if ($k.Length -eq 1) {
                    # Single character — check if it's special in SendKeys
                    if ($k -match '[\+\^\%\~\(\)\{\}\[\]]') {
                        $key = "{$k}"
                    } else {
                        $key = $k.ToLower()
                    }
                } else {
                    $key = $k.ToLower()
                }
            }
        }
    }
    if ($modifiers -and $key) {
        return "$modifiers($key)"
    } elseif ($key) {
        return $key
    } else {
        return $KeyCombo
    }
}

try {
    switch ($Action) {
        "help" {
            Write-Output @"
desktop-control / input-sim.ps1
Actions:
  type-text    -Text <text>       Type text into focused window [-DelayMs <ms>]
  send-keys    -Keys <combo>      Send keyboard shortcut (e.g. "Ctrl+S", "Alt+F4", "Enter", "F5")
  mouse-click  -X <x> -Y <y>     Click at coordinates [-Button left|right|middle] [-DoubleClick]
  mouse-move   -X <x> -Y <y>     Move mouse to coordinates
  mouse-scroll -Clicks <n>        Scroll (positive=up, negative=down)

Key combos: Ctrl, Alt, Shift + letter/number/F-key/special
Special keys: Enter, Tab, Escape, Backspace, Delete, Up, Down, Left, Right, Home, End,
              PageUp, PageDown, Space, F1-F12, Insert, CapsLock, NumLock
"@
        }

        "type-text" {
            if (-not $Text) { Write-Error "Missing -Text parameter"; exit 1 }
            Start-Sleep -Milliseconds 100
            # Use SendKeys for each character with optional delay
            # Escape special SendKeys characters
            $escaped = $Text -replace '([\+\^\%\~\(\)\{\}\[\]])', '{$1}'
            [System.Windows.Forms.SendKeys]::SendWait($escaped)
            Write-Output "Typed: ""$Text"" ($($Text.Length) characters)"
        }

        "send-keys" {
            if (-not $Keys) { Write-Error "Missing -Keys parameter"; exit 1 }
            Start-Sleep -Milliseconds 100
            $sendKeysFormat = ConvertTo-SendKeysFormat $Keys
            [System.Windows.Forms.SendKeys]::SendWait($sendKeysFormat)
            Write-Output "Sent: $Keys (SendKeys format: $sendKeysFormat)"
        }

        "mouse-click" {
            if ($X -lt 0 -or $Y -lt 0) { Write-Error "Missing -X and -Y coordinates"; exit 1 }
            [InputSim]::SetCursorPos($X, $Y)
            Start-Sleep -Milliseconds 50
            switch ($Button.ToLower()) {
                "left" {
                    [InputSim]::mouse_event([InputSim]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, [IntPtr]::Zero)
                    [InputSim]::mouse_event([InputSim]::MOUSEEVENTF_LEFTUP, 0, 0, 0, [IntPtr]::Zero)
                    if ($DoubleClick) {
                        Start-Sleep -Milliseconds 50
                        [InputSim]::mouse_event([InputSim]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, [IntPtr]::Zero)
                        [InputSim]::mouse_event([InputSim]::MOUSEEVENTF_LEFTUP, 0, 0, 0, [IntPtr]::Zero)
                    }
                }
                "right" {
                    [InputSim]::mouse_event([InputSim]::MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, [IntPtr]::Zero)
                    [InputSim]::mouse_event([InputSim]::MOUSEEVENTF_RIGHTUP, 0, 0, 0, [IntPtr]::Zero)
                }
                "middle" {
                    [InputSim]::mouse_event([InputSim]::MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, [IntPtr]::Zero)
                    [InputSim]::mouse_event([InputSim]::MOUSEEVENTF_MIDDLEUP, 0, 0, 0, [IntPtr]::Zero)
                }
            }
            $clickType = if ($DoubleClick) { "Double-click" } else { "Click" }
            Write-Output "$clickType ($Button) at ($X, $Y)"
        }

        "mouse-move" {
            if ($X -lt 0 -or $Y -lt 0) { Write-Error "Missing -X and -Y coordinates"; exit 1 }
            [InputSim]::SetCursorPos($X, $Y)
            Write-Output "Mouse moved to ($X, $Y)"
        }

        "mouse-scroll" {
            if ($Clicks -eq 0) { Write-Error "Missing -Clicks parameter (positive=up, negative=down)"; exit 1 }
            $scrollAmount = $Clicks * 120  # 120 = one wheel notch
            [InputSim]::mouse_event([InputSim]::MOUSEEVENTF_WHEEL, 0, 0, $scrollAmount, [IntPtr]::Zero)
            $direction = if ($Clicks -gt 0) { "up" } else { "down" }
            Write-Output "Scrolled $direction by $([Math]::Abs($Clicks)) clicks"
        }
    }
    exit 0
} catch {
    Write-Error "ERROR: $_"
    exit 1
}
