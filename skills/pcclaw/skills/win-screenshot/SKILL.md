---
name: win-screenshot
description: Capture screenshots on Windows (full screen, region, or specific window).
metadata:
  {
    "openclaw":
      {
        "emoji": "📸",
        "os": ["win32"],
      },
  }
---

# win-screenshot

Capture screenshots on Windows using PowerShell and .NET System.Drawing.
No external dependencies — uses built-in Windows APIs.

Pair with OpenClaw's `image` tool to analyze captured screenshots.

## Full Screen Capture

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
$bmp.Save('OUTPUT_PATH', [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Host 'Saved to OUTPUT_PATH'
"
```

Replace `OUTPUT_PATH` with the desired file path (e.g., `$env:TEMP\screenshot.png`).

## Region Capture

Capture a specific rectangular area (x, y, width, height):

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap(WIDTH, HEIGHT)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(X, Y, 0, 0, [System.Drawing.Size]::new(WIDTH, HEIGHT))
$bmp.Save('OUTPUT_PATH', [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
"
```

Replace `X`, `Y`, `WIDTH`, `HEIGHT` with pixel coordinates.

## Multi-Monitor (All Screens)

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$bounds = [System.Windows.Forms.SystemInformation]::VirtualScreen
$bmp = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
$bmp.Save('OUTPUT_PATH', [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
"
```

## List Visible Windows

List all visible windows with titles and dimensions (useful before targeted capture):

```powershell
powershell.exe -NoProfile -Command "
Add-Type @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public class WinAPI {
    [DllImport(\"user32.dll\")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport(\"user32.dll\")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    [DllImport(\"user32.dll\")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport(\"user32.dll\")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
}
'@
[WinAPI]::EnumWindows({
    param(`$hWnd, `$lParam)
    if ([WinAPI]::IsWindowVisible(`$hWnd)) {
        `$sb = New-Object System.Text.StringBuilder(256)
        [WinAPI]::GetWindowText(`$hWnd, `$sb, 256) | Out-Null
        `$title = `$sb.ToString()
        if (`$title.Length -gt 0) {
            `$rect = New-Object WinAPI+RECT
            [WinAPI]::GetWindowRect(`$hWnd, [ref]`$rect) | Out-Null
            `$w = `$rect.Right - `$rect.Left; `$h = `$rect.Bottom - `$rect.Top
            Write-Host \"`$title | `$(`$rect.Left),`$(`$rect.Top) `${w}x`${h}\"
        }
    }
    return `$true
}, [IntPtr]::Zero) | Out-Null
"
```

## Capture Specific Window by Title

Use region capture with coordinates from the window list:

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public class WinFind {
    [DllImport(\"user32.dll\")] public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
    [DllImport(\"user32.dll\")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
}
'@
`$hWnd = [WinFind]::FindWindow(`$null, 'WINDOW_TITLE')
if (`$hWnd -eq [IntPtr]::Zero) { Write-Host 'Window not found'; exit 1 }
`$rect = New-Object WinFind+RECT
[WinFind]::GetWindowRect(`$hWnd, [ref]`$rect) | Out-Null
`$w = `$rect.Right - `$rect.Left; `$h = `$rect.Bottom - `$rect.Top
`$bmp = New-Object System.Drawing.Bitmap(`$w, `$h)
`$g = [System.Drawing.Graphics]::FromImage(`$bmp)
`$g.CopyFromScreen(`$rect.Left, `$rect.Top, 0, 0, [System.Drawing.Size]::new(`$w, `$h))
`$bmp.Save('OUTPUT_PATH', [System.Drawing.Imaging.ImageFormat]::Png)
`$g.Dispose(); `$bmp.Dispose()
Write-Host \"Captured window: `${w}x`${h}\"
"
```

Replace `WINDOW_TITLE` with the exact window title from the window list.

## Recommended Workflow

1. **List windows** to find the target
2. **Capture** (full screen, region, or window)
3. Use OpenClaw's **`image` tool** to analyze the screenshot

```
win-screenshot (capture) → image tool (analyze) → agent acts on result
```

## Notes

- Works on Windows 10/11 with PowerShell 5.1+.
- No external dependencies — uses built-in .NET Framework assemblies.
- Output format: PNG (lossless). Change `ImageFormat::Png` to `Jpeg` for smaller files.
- For WSL: call `powershell.exe` from within WSL; save to a Windows-accessible path.
- DPI scaling: captured resolution matches the actual screen pixels.
- Window capture uses screen coordinates — it captures what's visible (may include overlapping windows).
- Default save location suggestion: `$env:TEMP\pcclaw-screenshot.png`.
