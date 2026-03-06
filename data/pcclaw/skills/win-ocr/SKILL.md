---
name: win-ocr
description: Extract text from images and screenshots using Windows built-in OCR (multilingual, offline, zero dependencies).
metadata:
  {
    "openclaw":
      {
        "emoji": "👁️",
        "os": ["win32"],
      },
  }
---

# win-ocr

Extract text from images and screenshots using the Windows built-in OCR engine.
Fully offline, multilingual, zero external dependencies.

Works on Windows 10 1809+ and Windows 11.

## Available Languages

Check which OCR languages are installed:

```powershell
powershell.exe -NoProfile -Command "
[Windows.Media.Ocr.OcrEngine, Windows.Media.Ocr, ContentType = WindowsRuntime] | Out-Null
$langs = [Windows.Media.Ocr.OcrEngine]::AvailableRecognizerLanguages
foreach ($l in $langs) { Write-Host ('{0} [{1}]' -f $l.DisplayName, $l.LanguageTag) }
"
```

Common language tags: `en-US`, `zh-Hant-TW`, `zh-Hans-CN`, `ja`, `ko`, `de-DE`, `fr-FR`, `es-ES`.

## OCR from Image File

Extract text from any image (PNG, JPG, BMP):

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() |
    Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation``1' })[0]
Function Await($WinRtTask, $ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null; $netTask.Result
}
[Windows.Media.Ocr.OcrEngine, Windows.Media.Ocr, ContentType = WindowsRuntime] | Out-Null
[Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType = WindowsRuntime] | Out-Null
[Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime] | Out-Null

$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync('IMAGE_PATH')) ([Windows.Storage.StorageFile])
$stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
$decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$softBmp = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])

$lang = [Windows.Globalization.Language]::new('LANG_TAG')
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)
$result = Await ($engine.RecognizeAsync($softBmp)) ([Windows.Media.Ocr.OcrResult])

foreach ($line in $result.Lines) { Write-Output $line.Text }
"
```

Replace `IMAGE_PATH` with the full path to the image file.
Replace `LANG_TAG` with a language tag (e.g., `en-US` or `zh-Hant-TW`).

## OCR from Live Screenshot

Capture the screen and immediately extract text:

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Runtime.WindowsRuntime
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() |
    Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation``1' })[0]
Function Await($WinRtTask, $ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null; $netTask.Result
}
[Windows.Media.Ocr.OcrEngine, Windows.Media.Ocr, ContentType = WindowsRuntime] | Out-Null
[Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType = WindowsRuntime] | Out-Null
[Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime] | Out-Null

# Capture screen
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
$path = \"$env:TEMP\pcclaw-ocr.png\"
$bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()

# OCR
$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($path)) ([Windows.Storage.StorageFile])
$stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
$decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$softBmp = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])

$lang = [Windows.Globalization.Language]::new('en-US')
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)
$result = Await ($engine.RecognizeAsync($softBmp)) ([Windows.Media.Ocr.OcrResult])

foreach ($line in $result.Lines) { Write-Output $line.Text }
"
```

## OCR from Screen Region

Capture and OCR a specific rectangular area:

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Runtime.WindowsRuntime
Add-Type -AssemblyName System.Drawing
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() |
    Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation``1' })[0]
Function Await($WinRtTask, $ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null; $netTask.Result
}
[Windows.Media.Ocr.OcrEngine, Windows.Media.Ocr, ContentType = WindowsRuntime] | Out-Null
[Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType = WindowsRuntime] | Out-Null
[Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime] | Out-Null

$bmp = New-Object System.Drawing.Bitmap(WIDTH, HEIGHT)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(X, Y, 0, 0, [System.Drawing.Size]::new(WIDTH, HEIGHT))
$path = \"$env:TEMP\pcclaw-ocr-region.png\"
$bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()

$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($path)) ([Windows.Storage.StorageFile])
$stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
$decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$softBmp = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])

$lang = [Windows.Globalization.Language]::new('LANG_TAG')
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)
$result = Await ($engine.RecognizeAsync($softBmp)) ([Windows.Media.Ocr.OcrResult])

foreach ($line in $result.Lines) { Write-Output $line.Text }
"
```

Replace `X`, `Y`, `WIDTH`, `HEIGHT` with the region coordinates, and `LANG_TAG` with the language.

## OCR with Word Bounding Boxes

Get word-level positions (useful for clicking on recognized text):

```powershell
powershell.exe -NoProfile -Command "
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() |
    Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation``1' })[0]
Function Await($WinRtTask, $ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null; $netTask.Result
}
[Windows.Media.Ocr.OcrEngine, Windows.Media.Ocr, ContentType = WindowsRuntime] | Out-Null
[Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType = WindowsRuntime] | Out-Null
[Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime] | Out-Null

$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync('IMAGE_PATH')) ([Windows.Storage.StorageFile])
$stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
$decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$softBmp = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])

$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new('en-US'))
$result = Await ($engine.RecognizeAsync($softBmp)) ([Windows.Media.Ocr.OcrResult])

foreach ($line in $result.Lines) {
    foreach ($word in $line.Words) {
        $r = $word.BoundingRect
        $cx = [math]::Round($r.X + $r.Width/2); $cy = [math]::Round($r.Y + $r.Height/2)
        Write-Host ('{0} | center={1},{2} | {3}x{4}' -f $word.Text,$cx,$cy,[math]::Round($r.Width),[math]::Round($r.Height))
    }
}
"
```

This outputs each word with its center coordinate — use these with `win-ui-auto` to click on recognized text.

## Recommended Workflows

### Screen → OCR → Understand

```
1. win-screenshot: capture full screen or window
2. win-ocr: extract text from the screenshot
3. Agent processes the text
```

### See text → Click on it

```
1. win-ocr (with bounding boxes): find word positions
2. win-ui-auto: click at the word's center coordinates
```

### Multilingual document

```
1. Run OCR with en-US for English text
2. Run OCR with zh-Hant-TW for Chinese text
3. Combine results
```

## Notes

- Fully offline — no API keys, no network, no external dependencies.
- Uses Windows.Media.Ocr WinRT API (built into Windows 10 1809+ and Windows 11).
- Supported image formats: PNG, JPG, BMP, GIF, TIFF.
- OCR quality depends on image resolution and clarity — higher resolution = better results.
- Max image size: 10000x10000 pixels (WinRT limit).
- The Await helper is required because PowerShell 5.1 doesn't natively support WinRT async operations.
- Additional languages can be installed via Settings → Time & Language → Language & Region.
- For WSL: call `powershell.exe` from within WSL; use Windows-accessible image paths.
- Combine with `win-screenshot` for live screen reading and `win-ui-auto` for acting on OCR results.
