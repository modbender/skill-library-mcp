---
name: win-clipboard
description: Read and write the Windows clipboard (text, images, file lists).
metadata:
  {
    "openclaw":
      {
        "emoji": "📎",
        "os": ["win32"],
      },
  }
---

# win-clipboard

Read and write the Windows clipboard — text, images, and file lists.
No external dependencies — uses built-in .NET Windows.Forms APIs.

## Read Text

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
$text = [System.Windows.Forms.Clipboard]::GetText()
if ($text) { Write-Output $text } else { Write-Host 'Clipboard is empty or not text' }
"
```

## Write Text

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Clipboard]::SetText('YOUR_TEXT_HERE')
Write-Host 'Text copied to clipboard'
"
```

For multi-line text, use a here-string:

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
$text = @'
Line 1
Line 2
Line 3
'@
[System.Windows.Forms.Clipboard]::SetText($text)
Write-Host 'Multi-line text copied'
"
```

## Read Image from Clipboard

Save a clipboard image (e.g., after pressing Print Screen) to a file:

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
if ([System.Windows.Forms.Clipboard]::ContainsImage()) {
    $img = [System.Windows.Forms.Clipboard]::GetImage()
    $img.Save('OUTPUT_PATH', [System.Drawing.Imaging.ImageFormat]::Png)
    $img.Dispose()
    Write-Host 'Image saved to OUTPUT_PATH'
} else {
    Write-Host 'No image in clipboard'
}
"
```

## Copy Image to Clipboard

Load an image file into the clipboard:

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$img = [System.Drawing.Image]::FromFile('INPUT_PATH')
[System.Windows.Forms.Clipboard]::SetImage($img)
$img.Dispose()
Write-Host 'Image copied to clipboard'
"
```

## Read File Drop List

Get the list of files currently in the clipboard (e.g., after Ctrl+C on files in Explorer):

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
if ([System.Windows.Forms.Clipboard]::ContainsFileDropList()) {
    $files = [System.Windows.Forms.Clipboard]::GetFileDropList()
    foreach ($f in $files) { Write-Output $f }
} else {
    Write-Host 'No files in clipboard'
}
"
```

## Check Clipboard Contents

Inspect what type of data is currently in the clipboard:

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
$types = @()
if ([System.Windows.Forms.Clipboard]::ContainsText()) { $types += 'Text' }
if ([System.Windows.Forms.Clipboard]::ContainsImage()) { $types += 'Image' }
if ([System.Windows.Forms.Clipboard]::ContainsFileDropList()) { $types += 'Files' }
if ([System.Windows.Forms.Clipboard]::ContainsAudio()) { $types += 'Audio' }
if ($types.Count -eq 0) { Write-Host 'Clipboard is empty' }
else { Write-Host ('Clipboard contains: ' + ($types -join ', ')) }
"
```

## Clear Clipboard

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Clipboard]::Clear()
Write-Host 'Clipboard cleared'
"
```

## Common Workflows

### Screenshot → Clipboard → File

```powershell
# User presses Print Screen, then:
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
if ([System.Windows.Forms.Clipboard]::ContainsImage()) {
    $img = [System.Windows.Forms.Clipboard]::GetImage()
    $path = \"$env:TEMP\pcclaw-clipboard.png\"
    $img.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $img.Dispose()
    Write-Host $path
} else { Write-Host 'No image in clipboard' }
"
```

### Pipe text through clipboard

```powershell
# Read → process → write back
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Windows.Forms
$text = [System.Windows.Forms.Clipboard]::GetText()
$upper = $text.ToUpper()
[System.Windows.Forms.Clipboard]::SetText($upper)
Write-Host 'Transformed and copied back'
"
```

## Notes

- Works on Windows 10/11 with PowerShell 5.1+.
- No external dependencies — uses .NET Framework System.Windows.Forms.
- For WSL: call `powershell.exe` from within WSL to access the Windows clipboard.
- The clipboard is a global resource — writing overwrites whatever was there before.
- Image operations support PNG, JPEG, BMP, GIF via `System.Drawing.Imaging.ImageFormat`.
- Clipboard access requires a desktop session — won't work in headless/service mode.
- Pairs well with `win-screenshot`: capture screen → save to clipboard → extract to file.
