---
name: win-files
description: Search, browse, and manage files and folders on Windows — file search, recent files, folder operations, disk info, zero dependencies.
metadata:
  {
    "openclaw":
      {
        "emoji": "📁",
        "os": ["win32"],
      },
  }
---

# win-files

Search, browse, and manage files and folders on Windows.
File search by name or content, recent files, folder operations, disk info.
Zero external dependencies — uses built-in PowerShell cmdlets.

Works on Windows 10/11 with PowerShell 5.1+.

## Search Files by Name

```powershell
powershell.exe -NoProfile -Command "
Get-ChildItem -Path 'SEARCH_PATH' -Recurse -Filter 'PATTERN' -ErrorAction SilentlyContinue |
  Select-Object FullName, @{N='SizeMB';E={[math]::Round($_.Length/1MB,2)}}, LastWriteTime |
  Sort-Object LastWriteTime -Descending |
  Format-Table -AutoSize
"
```

- `SEARCH_PATH`: directory to search (e.g., `C:\Users\me\Documents`)
- `PATTERN`: wildcard pattern (e.g., `*.pdf`, `report*`, `*.txt`)

### With size and date filters

```powershell
powershell.exe -NoProfile -Command "
Get-ChildItem -Path 'SEARCH_PATH' -Recurse -Filter 'PATTERN' -ErrorAction SilentlyContinue |
  Where-Object { $_.Length -gt MIN_BYTES -and $_.LastWriteTime -gt (Get-Date).AddDays(-DAYS) } |
  Sort-Object LastWriteTime -Descending |
  Select-Object FullName, @{N='SizeMB';E={[math]::Round($_.Length/1MB,2)}}, LastWriteTime |
  Format-Table -AutoSize
"
```

- `MIN_BYTES`: minimum file size in bytes (e.g., `1048576` for 1 MB)
- `DAYS`: files modified within the last N days

## Search File Contents

```powershell
powershell.exe -NoProfile -Command "
Get-ChildItem -Path 'SEARCH_PATH' -Recurse -Include '*.txt','*.md','*.log','*.csv','*.json','*.xml','*.ps1','*.py','*.js' -ErrorAction SilentlyContinue |
  Select-String -Pattern 'SEARCH_TEXT' -SimpleMatch |
  Select-Object Path, LineNumber, Line -First 50 |
  Format-Table -AutoSize
"
```

- `SEARCH_TEXT`: text to search for (literal match)
- For regex, remove `-SimpleMatch`
- Adjust `-Include` to target specific file types

## List Recent Files

```powershell
powershell.exe -NoProfile -Command "
$recent = [Environment]::GetFolderPath('Recent')
Get-ChildItem -Path $recent -Filter '*.lnk' |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First COUNT |
  ForEach-Object {
    $shell = New-Object -ComObject WScript.Shell
    $target = $shell.CreateShortcut($_.FullName).TargetPath
    [PSCustomObject]@{
      Name = $_.BaseName
      Target = $target
      Accessed = $_.LastWriteTime.ToString('yyyy-MM-dd HH:mm')
    }
  } | Format-Table -AutoSize
"
```

Replace `COUNT` with the number of recent files to show (e.g., `20`).

## Get File Info

```powershell
powershell.exe -NoProfile -Command "
$f = Get-Item -LiteralPath 'FILE_PATH'
[PSCustomObject]@{
  Name = $f.Name
  FullPath = $f.FullName
  SizeBytes = $f.Length
  SizeMB = [math]::Round($f.Length / 1MB, 2)
  Created = $f.CreationTime
  Modified = $f.LastWriteTime
  ReadOnly = $f.IsReadOnly
  Extension = $f.Extension
  Attributes = $f.Attributes.ToString()
} | Format-List
"
```

## Get Folder Size

```powershell
powershell.exe -NoProfile -Command "
$path = 'FOLDER_PATH'
$result = Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue |
  Measure-Object -Property Length -Sum
Write-Host ('Path: {0}' -f $path)
Write-Host ('Files: {0}' -f $result.Count)
Write-Host ('Size: {0:N2} MB ({1:N2} GB)' -f ($result.Sum / 1MB), ($result.Sum / 1GB))
"
```

### Folder size breakdown (top-level subdirectories)

```powershell
powershell.exe -NoProfile -Command "
Get-ChildItem -Path 'FOLDER_PATH' -Directory | ForEach-Object {
  $size = (Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue |
    Measure-Object -Property Length -Sum).Sum
  [PSCustomObject]@{
    Folder = $_.Name
    SizeMB = [math]::Round(($size / 1MB), 2)
  }
} | Sort-Object SizeMB -Descending | Format-Table -AutoSize
"
```

## List Drives

```powershell
powershell.exe -NoProfile -Command "
Get-CimInstance -ClassName Win32_LogicalDisk |
  Select-Object DeviceID,
    @{N='Label';E={$_.VolumeName}},
    @{N='FileSystem';E={$_.FileSystem}},
    @{N='SizeGB';E={[math]::Round($_.Size/1GB,1)}},
    @{N='FreeGB';E={[math]::Round($_.FreeSpace/1GB,1)}},
    @{N='UsedPct';E={if($_.Size){[math]::Round(($_.Size-$_.FreeSpace)/$_.Size*100,1)}else{'N/A'}}} |
  Format-Table -AutoSize
"
```

## List Folder Contents

```powershell
powershell.exe -NoProfile -Command "
Get-ChildItem -Path 'FOLDER_PATH' |
  Select-Object Mode,
    @{N='Size';E={if($_.PSIsContainer){'<DIR>'}else{'{0:N0}' -f $_.Length}}},
    LastWriteTime,
    Name |
  Format-Table -AutoSize
"
```

## Create Folder

```powershell
powershell.exe -NoProfile -Command "
New-Item -Path 'FOLDER_PATH' -ItemType Directory -Force | Out-Null
Write-Host 'Created: FOLDER_PATH'
"
```

## Copy File or Folder

```powershell
powershell.exe -NoProfile -Command "
Copy-Item -Path 'SOURCE' -Destination 'DEST' -Recurse -Force
Write-Host 'Copied: SOURCE -> DEST'
"
```

## Move / Rename

```powershell
powershell.exe -NoProfile -Command "
Move-Item -Path 'SOURCE' -Destination 'DEST' -Force
Write-Host 'Moved: SOURCE -> DEST'
"
```

## Delete File or Folder

Preview first (dry run):

```powershell
powershell.exe -NoProfile -Command "
Remove-Item -Path 'TARGET_PATH' -Recurse -WhatIf
"
```

Then delete:

```powershell
powershell.exe -NoProfile -Command "
Remove-Item -Path 'TARGET_PATH' -Recurse -Force
Write-Host 'Deleted: TARGET_PATH'
"
```

## Open in File Explorer

```powershell
powershell.exe -NoProfile -Command "
Start-Process explorer.exe 'FOLDER_PATH'
"
```

### Open and select a specific file

```powershell
powershell.exe -NoProfile -Command "
Start-Process explorer.exe '/select,FILE_PATH'
"
```

## Read File

```powershell
powershell.exe -NoProfile -Command "
Get-Content -Path 'FILE_PATH' -Encoding UTF8
"
```

### First or last N lines

```powershell
powershell.exe -NoProfile -Command "
Get-Content -Path 'FILE_PATH' -TotalCount N -Encoding UTF8
"
```

```powershell
powershell.exe -NoProfile -Command "
Get-Content -Path 'FILE_PATH' -Tail N -Encoding UTF8
"
```

## Write Text to File

```powershell
powershell.exe -NoProfile -Command "
Set-Content -Path 'FILE_PATH' -Value 'TEXT_CONTENT' -Encoding UTF8
Write-Host 'Written to FILE_PATH'
"
```

## Common Workflows

### Find large files eating disk space

```
1. win-files: list drives to find low-space disks
2. win-files: folder size breakdown on the target drive
3. win-files: search for large files (filter by MIN_BYTES)
4. Delete or move unnecessary files
```

### Organize downloads folder

```
1. win-files: list recent files in Downloads
2. win-files: create categorized subfolders
3. win-files: move files to appropriate folders
```

### Search and open

```
1. win-files: search for a file by name
2. win-files: open the containing folder in Explorer
```

### Backup before editing

```
1. win-files: copy file to a backup location
2. Edit the original file
3. If something goes wrong, restore from backup
```

## Notes

- Fully offline — no API keys, no network, no external dependencies.
- Uses built-in PowerShell cmdlets (`Get-ChildItem`, `Copy-Item`, etc.).
- Path separators: use backslashes (`C:\Users\...`) for Windows paths.
- For WSL paths, convert with: `wslpath -w '/mnt/c/...'` to get `C:\...`
- Large recursive searches on `C:\` may be slow — narrow the search path when possible.
- `Get-ChildItem -Recurse` skips folders it can't access (with `-ErrorAction SilentlyContinue`).
- File content search is limited to text files — binary files produce garbled output.
- Delete operations are permanent — always use `-WhatIf` to preview first.
- Combine with `win-clipboard` to copy file paths or contents to the clipboard.
