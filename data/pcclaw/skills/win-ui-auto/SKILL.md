---
name: win-ui-auto
description: Windows UI automation — inspect elements, click, type, manage windows and apps.
metadata:
  {
    "openclaw":
      {
        "emoji": "🖱️",
        "os": ["win32"],
      },
  }
---

# win-ui-auto

Windows UI automation using .NET UI Automation and Win32 APIs.
The Windows counterpart to Peekaboo (macOS).

No external dependencies — uses built-in PowerShell, .NET Framework, and Win32 APIs.

## Capabilities

| Feature | Peekaboo (macOS) | win-ui-auto (Windows) |
|---------|------------------|-----------------------|
| See UI elements | `peekaboo see` | UI Automation tree walk |
| Click elements | `peekaboo click` | SetCursorPos + mouse_event |
| Type text | `peekaboo type` | SendKeys |
| Hotkeys | `peekaboo hotkey` | SendKeys with modifiers |
| List windows | `peekaboo list windows` | EnumWindows / UI Automation |
| Focus window | `peekaboo window focus` | SetForegroundWindow |
| Move/resize | `peekaboo window set-bounds` | MoveWindow |
| Launch app | `peekaboo app launch` | Start-Process |
| Screenshot | `peekaboo image` | win-screenshot skill |

## Recommended Workflow

```
1. List windows     → find target window
2. See elements     → enumerate UI tree, get element positions
3. Screenshot       → capture window (use win-screenshot skill)
4. Analyze image    → use OpenClaw image tool to understand layout
5. Click / Type     → interact with specific elements
```

---

## List Windows

List all visible windows with position and size:

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$root = [System.Windows.Automation.AutomationElement]::RootElement
$wc = [System.Windows.Automation.PropertyCondition]::new(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Window)
$wins = $root.FindAll([System.Windows.Automation.TreeScope]::Children, $wc)
foreach ($w in $wins) {
    $n = $w.Current.Name; $c = $w.Current.ClassName; $r = $w.Current.BoundingRectangle
    if ($n.Length -gt 0 -and -not [System.Double]::IsInfinity($r.Width)) {
        Write-Host ('{0} | class={1} | {2},{3} {4}x{5}' -f $n,$c,[math]::Round($r.X),[math]::Round($r.Y),[math]::Round($r.Width),[math]::Round($r.Height))
    }
}
"
```

## See UI Elements

Inspect the UI Automation tree of a specific window. Returns control type, name, automation ID, and bounding rectangle for each element.

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$root = [System.Windows.Automation.AutomationElement]::RootElement
$wc = [System.Windows.Automation.PropertyCondition]::new(
    [System.Windows.Automation.AutomationElement]::NameProperty, 'WINDOW_TITLE')
$win = $root.FindFirst([System.Windows.Automation.TreeScope]::Children, $wc)
if (-not $win) { Write-Host 'Window not found'; exit 1 }
$all = [System.Windows.Automation.Condition]::TrueCondition
$els = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $all)
$i = 0
foreach ($el in $els) {
    $ct = $el.Current.ControlType.ProgrammaticName -replace 'ControlType\.',''
    $nm = $el.Current.Name
    $aid = $el.Current.AutomationId
    $r = $el.Current.BoundingRectangle
    if (-not [System.Double]::IsInfinity($r.Width) -and $r.Width -gt 0) {
        $cx = [math]::Round($r.X + $r.Width/2); $cy = [math]::Round($r.Y + $r.Height/2)
        Write-Host ('E{0} {1} | name={2} | id={3} | center={4},{5}' -f $i,$ct,$nm,$aid,$cx,$cy)
    }
    $i++
    if ($i -ge 100) { Write-Host '... (truncated at 100 elements)'; break }
}
"
```

Replace `WINDOW_TITLE` with the exact title from the window list. Each element is prefixed with an ID like `E0`, `E1`, etc. The `center` coordinates can be used for clicking.

### Filter by Control Type

Show only buttons:

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$root = [System.Windows.Automation.AutomationElement]::RootElement
$wc = [System.Windows.Automation.PropertyCondition]::new(
    [System.Windows.Automation.AutomationElement]::NameProperty, 'WINDOW_TITLE')
$win = $root.FindFirst([System.Windows.Automation.TreeScope]::Children, $wc)
if (-not $win) { Write-Host 'Window not found'; exit 1 }
$bc = [System.Windows.Automation.PropertyCondition]::new(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Button)
$btns = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $bc)
foreach ($b in $btns) {
    $r = $b.Current.BoundingRectangle
    if (-not [System.Double]::IsInfinity($r.Width)) {
        $cx = [math]::Round($r.X + $r.Width/2); $cy = [math]::Round($r.Y + $r.Height/2)
        Write-Host ('Button: {0} | id={1} | center={2},{3}' -f $b.Current.Name,$b.Current.AutomationId,$cx,$cy)
    }
}
"
```

Other control types: `Edit`, `Text`, `CheckBox`, `RadioButton`, `ComboBox`, `List`, `ListItem`, `Menu`, `MenuItem`, `Tab`, `TabItem`, `Tree`, `TreeItem`, `Hyperlink`, `Image`, `Slider`, `ProgressBar`.

## Click

Click at specific screen coordinates:

```powershell
powershell.exe -NoProfile -Command "
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class Mouse {
    [DllImport(\"user32.dll\")] public static extern bool SetCursorPos(int X, int Y);
    [DllImport(\"user32.dll\")] public static extern void mouse_event(uint f, int dx, int dy, int d, IntPtr e);
    public const uint DOWN = 0x02, UP = 0x04;
    public static void Click(int x, int y) {
        SetCursorPos(x, y);
        System.Threading.Thread.Sleep(50);
        mouse_event(DOWN, 0, 0, 0, IntPtr.Zero);
        mouse_event(UP, 0, 0, 0, IntPtr.Zero);
    }
}
'@
[Mouse]::Click(X, Y)
Write-Host 'Clicked at X,Y'
"
```

Replace `X` and `Y` with target coordinates (e.g., from the `center` output of the See command).

### Double Click

```powershell
powershell.exe -NoProfile -Command "
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class Mouse {
    [DllImport(\"user32.dll\")] public static extern bool SetCursorPos(int X, int Y);
    [DllImport(\"user32.dll\")] public static extern void mouse_event(uint f, int dx, int dy, int d, IntPtr e);
    public const uint DOWN = 0x02, UP = 0x04;
    public static void DoubleClick(int x, int y) {
        SetCursorPos(x, y);
        System.Threading.Thread.Sleep(50);
        mouse_event(DOWN, 0, 0, 0, IntPtr.Zero); mouse_event(UP, 0, 0, 0, IntPtr.Zero);
        System.Threading.Thread.Sleep(80);
        mouse_event(DOWN, 0, 0, 0, IntPtr.Zero); mouse_event(UP, 0, 0, 0, IntPtr.Zero);
    }
}
'@
[Mouse]::DoubleClick(X, Y)
Write-Host 'Double-clicked at X,Y'
"
```

### Right Click

```powershell
powershell.exe -NoProfile -Command "
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class Mouse {
    [DllImport(\"user32.dll\")] public static extern bool SetCursorPos(int X, int Y);
    [DllImport(\"user32.dll\")] public static extern void mouse_event(uint f, int dx, int dy, int d, IntPtr e);
    public const uint RDOWN = 0x08, RUP = 0x10;
    public static void RightClick(int x, int y) {
        SetCursorPos(x, y);
        System.Threading.Thread.Sleep(50);
        mouse_event(RDOWN, 0, 0, 0, IntPtr.Zero);
        mouse_event(RUP, 0, 0, 0, IntPtr.Zero);
    }
}
'@
[Mouse]::RightClick(X, Y)
Write-Host 'Right-clicked at X,Y'
"
```

## Type Text

Send keystrokes to the focused window:

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait('YOUR_TEXT_HERE')
"
```

Special characters in SendKeys:
- `{ENTER}` — Enter key
- `{TAB}` — Tab key
- `{BACKSPACE}` or `{BS}` — Backspace
- `{DELETE}` or `{DEL}` — Delete
- `{ESCAPE}` or `{ESC}` — Escape
- `{UP}`, `{DOWN}`, `{LEFT}`, `{RIGHT}` — Arrow keys
- `{HOME}`, `{END}`, `{PGUP}`, `{PGDN}` — Navigation
- `{F1}` through `{F12}` — Function keys
- `+` — Shift, `^` — Ctrl, `%` — Alt (modifiers)

### Type multi-line text

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait('Line 1{ENTER}Line 2{ENTER}Line 3')
"
```

## Hotkeys

Send keyboard shortcuts:

```powershell
# Ctrl+S (Save)
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait('^s')
"

# Ctrl+C (Copy)
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait('^c')
"

# Ctrl+V (Paste)
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait('^v')
"

# Alt+F4 (Close)
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait('%{F4}')
"

# Ctrl+Shift+T (Reopen tab)
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait('^+t')
"

# Win+D (Show desktop)
powershell.exe -NoProfile -Command "
\$shell = New-Object -ComObject Shell.Application
\$shell.ToggleDesktop()
"
```

## Focus Window

Bring a window to the foreground by title:

```powershell
powershell.exe -NoProfile -Command "
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class WinFocus {
    [DllImport(\"user32.dll\")] public static extern IntPtr FindWindow(string cls, string title);
    [DllImport(\"user32.dll\")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
'@
$h = [WinFocus]::FindWindow($null, 'WINDOW_TITLE')
if ($h -eq [IntPtr]::Zero) { Write-Host 'Window not found'; exit 1 }
[WinFocus]::ShowWindow($h, 9)  # SW_RESTORE
[WinFocus]::SetForegroundWindow($h)
Write-Host 'Focused: WINDOW_TITLE'
"
```

## Move / Resize Window

```powershell
powershell.exe -NoProfile -Command "
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class WinMove {
    [DllImport(\"user32.dll\")] public static extern IntPtr FindWindow(string cls, string title);
    [DllImport(\"user32.dll\")] public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int W, int H, bool repaint);
}
'@
$h = [WinMove]::FindWindow($null, 'WINDOW_TITLE')
if ($h -eq [IntPtr]::Zero) { Write-Host 'Window not found'; exit 1 }
[WinMove]::MoveWindow($h, X, Y, WIDTH, HEIGHT, $true)
Write-Host 'Moved window to X,Y WIDTHxHEIGHT'
"
```

## Minimize / Maximize / Close Window

```powershell
powershell.exe -NoProfile -Command "
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class WinCtl {
    [DllImport(\"user32.dll\")] public static extern IntPtr FindWindow(string cls, string title);
    [DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport(\"user32.dll\")] public static extern bool PostMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
}
'@
$h = [WinCtl]::FindWindow($null, 'WINDOW_TITLE')
if ($h -eq [IntPtr]::Zero) { Write-Host 'Window not found'; exit 1 }

# Minimize: ShowWindow($h, 6)
# Maximize: ShowWindow($h, 3)
# Restore:  ShowWindow($h, 9)
# Close:    PostMessage($h, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero)

[WinCtl]::ShowWindow($h, ACTION)
Write-Host 'Done'
"
```

Action codes: `6` = minimize, `3` = maximize, `9` = restore. For close, use `PostMessage` with `0x0010` (WM_CLOSE).

## Launch Application

```powershell
# By name
powershell.exe -NoProfile -Command "Start-Process 'notepad'"

# By path
powershell.exe -NoProfile -Command "Start-Process 'C:\Program Files\MyApp\app.exe'"

# With arguments
powershell.exe -NoProfile -Command "Start-Process 'code' -ArgumentList 'C:\projects\myrepo'"

# Open URL in default browser
powershell.exe -NoProfile -Command "Start-Process 'https://example.com'"

# Open file with default app
powershell.exe -NoProfile -Command "Start-Process 'C:\Users\me\doc.pdf'"
```

## List Running Processes

```powershell
powershell.exe -NoProfile -Command "
Get-Process | Where-Object { \$_.MainWindowTitle.Length -gt 0 } |
    Select-Object Id, ProcessName, MainWindowTitle | Format-Table -AutoSize
"
```

## Quit Application

```powershell
# Graceful close by process name
powershell.exe -NoProfile -Command "
Get-Process -Name 'notepad' -ErrorAction SilentlyContinue | ForEach-Object { $_.CloseMainWindow() }
"

# Force kill
powershell.exe -NoProfile -Command "Stop-Process -Name 'notepad' -Force"
```

## Mouse Scroll

```powershell
powershell.exe -NoProfile -Command "
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class Scroll {
    [DllImport(\"user32.dll\")] public static extern void mouse_event(uint f, int dx, int dy, int d, IntPtr e);
    public const uint WHEEL = 0x0800;
    public static void Up(int clicks) { mouse_event(WHEEL, 0, 0, clicks * 120, IntPtr.Zero); }
    public static void Down(int clicks) { mouse_event(WHEEL, 0, 0, -clicks * 120, IntPtr.Zero); }
}
'@
# Scroll down 3 clicks
[Scroll]::Down(3)
"
```

## Full Workflow Example

```
# 1. List windows
→ Found: "Notepad - myfile.txt" at 100,100 800x600

# 2. Focus window
→ SetForegroundWindow("Notepad - myfile.txt")

# 3. See elements
→ E5 Edit | name= | id=15 | center=500,400
→ E8 MenuItem | name=File | id= | center=120,125

# 4. Click on Edit area
→ Click(500, 400)

# 5. Type text
→ SendKeys("Hello from PCClaw!")

# 6. Save with Ctrl+S
→ SendKeys("^s")

# 7. Screenshot to verify
→ (use win-screenshot skill)
```

## Notes

- Works on Windows 10/11 with PowerShell 5.1+.
- No external dependencies — uses .NET Framework UI Automation and Win32 API.
- UI Automation requires the target app to expose an accessibility tree (most modern apps do).
- `SendKeys` requires the target window to be focused. Always focus first, then type.
- `SetCursorPos` + `mouse_event` uses absolute screen coordinates.
- Some apps with elevated privileges (admin) may not respond to input from a non-elevated process.
- For complex automation flows: see → screenshot → analyze with `image` tool → click/type.
- Combine with `win-screenshot` for visual verification and `win-clipboard` for data transfer.
- Use the element `center` coordinates from the See command as click targets.
- Truncate element lists at a reasonable limit (50-100) for large windows.
