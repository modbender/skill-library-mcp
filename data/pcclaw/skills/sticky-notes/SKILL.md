---
name: sticky-notes
description: Read and search Windows Sticky Notes — access your notes via the local SQLite database using built-in winsqlite3.dll, zero dependencies.
metadata:
  {
    "openclaw":
      {
        "emoji": "📝",
        "os": ["win32"],
      },
  }
---

# sticky-notes

Read and search Windows Sticky Notes directly from the local database.
Uses Windows built-in `winsqlite3.dll` via P/Invoke — zero external dependencies.

Works on Windows 10/11 with PowerShell 5.1+. Requires the Sticky Notes app to have been opened and at least one note created.

## Check Database

Verify that the Sticky Notes database exists:

```powershell
powershell.exe -NoProfile -Command "
$dbPath = Join-Path $env:LocalAppData 'Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite'
if (Test-Path $dbPath) {
    $f = Get-Item $dbPath
    Write-Host ('Database: {0}' -f $dbPath)
    Write-Host ('Size: {0:N0} bytes' -f $f.Length)
    Write-Host ('Modified: {0}' -f $f.LastWriteTime)
} else {
    Write-Host 'Database not found. Open Sticky Notes and create at least one note first.'
}
"
```

## Discover Schema

Check the actual table structure (useful if the schema varies between Windows versions):

```powershell
powershell.exe -NoProfile -Command "
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class SQ {
    const string L = ""winsqlite3.dll"";
    [DllImport(L)] public static extern int sqlite3_open_v2(string f, out IntPtr db, int flags, IntPtr vfs);
    [DllImport(L)] public static extern int sqlite3_close(IntPtr db);
    [DllImport(L)] public static extern int sqlite3_prepare_v2(IntPtr db, string sql, int n, out IntPtr st, IntPtr t);
    [DllImport(L)] public static extern int sqlite3_step(IntPtr st);
    [DllImport(L)] public static extern IntPtr sqlite3_column_text(IntPtr st, int c);
    [DllImport(L)] public static extern int sqlite3_finalize(IntPtr st);
    public static string Utf8(IntPtr p) {
        if (p == IntPtr.Zero) return string.Empty;
        int len = 0; while (Marshal.ReadByte(p, len) != 0) len++;
        byte[] b = new byte[len]; Marshal.Copy(p, b, 0, len);
        return System.Text.Encoding.UTF8.GetString(b);
    }
}
'@
$dbPath = Join-Path $env:LocalAppData 'Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite'
$db = [IntPtr]::Zero; $st = [IntPtr]::Zero
[SQ]::sqlite3_open_v2($dbPath, [ref]$db, 1, [IntPtr]::Zero) | Out-Null
$sql = ""SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name""
[SQ]::sqlite3_prepare_v2($db, $sql, -1, [ref]$st, [IntPtr]::Zero) | Out-Null
while ([SQ]::sqlite3_step($st) -eq 100) {
    $name = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 0))
    $ddl = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 1))
    Write-Host ('=== {0} ===' -f $name)
    Write-Host $ddl
    Write-Host ''
}
[SQ]::sqlite3_finalize($st) | Out-Null
[SQ]::sqlite3_close($db) | Out-Null
"
```

## List All Notes

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class SQ {
    const string L = ""winsqlite3.dll"";
    [DllImport(L)] public static extern int sqlite3_open_v2(string f, out IntPtr db, int flags, IntPtr vfs);
    [DllImport(L)] public static extern int sqlite3_close(IntPtr db);
    [DllImport(L)] public static extern int sqlite3_prepare_v2(IntPtr db, string sql, int n, out IntPtr st, IntPtr t);
    [DllImport(L)] public static extern int sqlite3_step(IntPtr st);
    [DllImport(L)] public static extern IntPtr sqlite3_column_text(IntPtr st, int c);
    [DllImport(L)] public static extern long sqlite3_column_int64(IntPtr st, int c);
    [DllImport(L)] public static extern int sqlite3_finalize(IntPtr st);
    public static string Utf8(IntPtr p) {
        if (p == IntPtr.Zero) return string.Empty;
        int len = 0; while (Marshal.ReadByte(p, len) != 0) len++;
        byte[] b = new byte[len]; Marshal.Copy(p, b, 0, len);
        return System.Text.Encoding.UTF8.GetString(b);
    }
}
'@
$dbPath = Join-Path $env:LocalAppData 'Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite'
$db = [IntPtr]::Zero; $st = [IntPtr]::Zero
[SQ]::sqlite3_open_v2($dbPath, [ref]$db, 1, [IntPtr]::Zero) | Out-Null
$sql = ""SELECT Id, Text, Theme, CreatedAt, UpdatedAt FROM Note WHERE DeletedAt IS NULL OR DeletedAt = '' OR DeletedAt = 0 ORDER BY UpdatedAt DESC""
[SQ]::sqlite3_prepare_v2($db, $sql, -1, [ref]$st, [IntPtr]::Zero) | Out-Null
$i = 1
while ([SQ]::sqlite3_step($st) -eq 100) {
    $id = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 0))
    $text = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 1))
    $theme = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 2))
    $ticks = [SQ]::sqlite3_column_int64($st, 4)
    $updated = if ($ticks -gt 0) { [DateTime]::new($ticks).ToString('yyyy-MM-dd HH:mm') } else { 'unknown' }
    $preview = if ($text.Length -gt 80) { $text.Substring(0,80) + '...' } else { $text }
    $preview = $preview -replace ""[\r\n]+"", ' '
    Write-Host (""--- Note {0} [{1}] ---"" -f $i, $theme)
    Write-Host (""ID: {0}"" -f $id)
    Write-Host (""Preview: {0}"" -f $preview)
    Write-Host (""Updated: {0}"" -f $updated)
    Write-Host ''
    $i++
}
if ($i -eq 1) { Write-Host 'No notes found.' }
[SQ]::sqlite3_finalize($st) | Out-Null
[SQ]::sqlite3_close($db) | Out-Null
"
```

Flag `1` = `SQLITE_OPEN_READONLY`. Safe to run while Sticky Notes is open.

Timestamps are stored as .NET Ticks (100-nanosecond intervals since 0001-01-01).

## Read a Specific Note

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class SQ {
    const string L = ""winsqlite3.dll"";
    [DllImport(L)] public static extern int sqlite3_open_v2(string f, out IntPtr db, int flags, IntPtr vfs);
    [DllImport(L)] public static extern int sqlite3_close(IntPtr db);
    [DllImport(L)] public static extern int sqlite3_prepare_v2(IntPtr db, string sql, int n, out IntPtr st, IntPtr t);
    [DllImport(L)] public static extern int sqlite3_step(IntPtr st);
    [DllImport(L)] public static extern IntPtr sqlite3_column_text(IntPtr st, int c);
    [DllImport(L)] public static extern long sqlite3_column_int64(IntPtr st, int c);
    [DllImport(L)] public static extern int sqlite3_finalize(IntPtr st);
    public static string Utf8(IntPtr p) {
        if (p == IntPtr.Zero) return string.Empty;
        int len = 0; while (Marshal.ReadByte(p, len) != 0) len++;
        byte[] b = new byte[len]; Marshal.Copy(p, b, 0, len);
        return System.Text.Encoding.UTF8.GetString(b);
    }
}
'@
$dbPath = Join-Path $env:LocalAppData 'Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite'
$db = [IntPtr]::Zero; $st = [IntPtr]::Zero
[SQ]::sqlite3_open_v2($dbPath, [ref]$db, 1, [IntPtr]::Zero) | Out-Null
$sql = ""SELECT Text, Theme, CreatedAt, UpdatedAt FROM Note WHERE Id = 'NOTE_ID'""
[SQ]::sqlite3_prepare_v2($db, $sql, -1, [ref]$st, [IntPtr]::Zero) | Out-Null
if ([SQ]::sqlite3_step($st) -eq 100) {
    $text = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 0))
    $theme = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 1))
    $created = [SQ]::sqlite3_column_int64($st, 2)
    $updated = [SQ]::sqlite3_column_int64($st, 3)
    $cDate = if ($created -gt 0) { [DateTime]::new($created).ToString('yyyy-MM-dd HH:mm') } else { 'unknown' }
    $uDate = if ($updated -gt 0) { [DateTime]::new($updated).ToString('yyyy-MM-dd HH:mm') } else { 'unknown' }
    Write-Host (""Theme: {0} | Created: {1} | Updated: {2}"" -f $theme, $cDate, $uDate)
    Write-Host '---'
    Write-Host $text
} else { Write-Host 'Note not found.' }
[SQ]::sqlite3_finalize($st) | Out-Null
[SQ]::sqlite3_close($db) | Out-Null
"
```

Replace `NOTE_ID` with the note's GUID from the list command.

## Search Notes

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class SQ {
    const string L = ""winsqlite3.dll"";
    [DllImport(L)] public static extern int sqlite3_open_v2(string f, out IntPtr db, int flags, IntPtr vfs);
    [DllImport(L)] public static extern int sqlite3_close(IntPtr db);
    [DllImport(L)] public static extern int sqlite3_prepare_v2(IntPtr db, string sql, int n, out IntPtr st, IntPtr t);
    [DllImport(L)] public static extern int sqlite3_step(IntPtr st);
    [DllImport(L)] public static extern IntPtr sqlite3_column_text(IntPtr st, int c);
    [DllImport(L)] public static extern long sqlite3_column_int64(IntPtr st, int c);
    [DllImport(L)] public static extern int sqlite3_finalize(IntPtr st);
    [DllImport(L)] public static extern int sqlite3_bind_text(IntPtr st, int idx, byte[] val, int n, IntPtr d);
    public static string Utf8(IntPtr p) {
        if (p == IntPtr.Zero) return string.Empty;
        int len = 0; while (Marshal.ReadByte(p, len) != 0) len++;
        byte[] b = new byte[len]; Marshal.Copy(p, b, 0, len);
        return System.Text.Encoding.UTF8.GetString(b);
    }
    public static byte[] ToUtf8(string s) {
        byte[] u = System.Text.Encoding.UTF8.GetBytes(s);
        byte[] r = new byte[u.Length + 1]; Array.Copy(u, r, u.Length);
        return r;
    }
}
'@
$dbPath = Join-Path $env:LocalAppData 'Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite'
$db = [IntPtr]::Zero; $st = [IntPtr]::Zero
[SQ]::sqlite3_open_v2($dbPath, [ref]$db, 1, [IntPtr]::Zero) | Out-Null
$sql = ""SELECT Id, Text, Theme, UpdatedAt FROM Note WHERE Text LIKE ? AND (DeletedAt IS NULL OR DeletedAt = '' OR DeletedAt = 0) ORDER BY UpdatedAt DESC""
[SQ]::sqlite3_prepare_v2($db, $sql, -1, [ref]$st, [IntPtr]::Zero) | Out-Null
$pattern = '%' + 'SEARCH_TERM' + '%'
[SQ]::sqlite3_bind_text($st, 1, [SQ]::ToUtf8($pattern), -1, [IntPtr]::Zero) | Out-Null
$i = 0
while ([SQ]::sqlite3_step($st) -eq 100) {
    $id = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 0))
    $text = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 1))
    $theme = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 2))
    $ticks = [SQ]::sqlite3_column_int64($st, 3)
    $updated = if ($ticks -gt 0) { [DateTime]::new($ticks).ToString('yyyy-MM-dd HH:mm') } else { 'unknown' }
    $preview = if ($text.Length -gt 100) { $text.Substring(0,100) + '...' } else { $text }
    $preview = $preview -replace ""[\r\n]+"", ' '
    Write-Host (""--- [{0}] {1} ---"" -f $theme, $updated)
    Write-Host (""ID: {0}"" -f $id)
    Write-Host $preview
    Write-Host ''
    $i++
}
Write-Host (""{0} note(s) found."" -f $i)
[SQ]::sqlite3_finalize($st) | Out-Null
[SQ]::sqlite3_close($db) | Out-Null
"
```

Replace `SEARCH_TERM` with the text to search for (case-insensitive via SQLite LIKE). Supports Chinese and other non-ASCII text via UTF-8 bind.

## Create a Note

Close the Sticky Notes app before writing to avoid database conflicts.

```powershell
powershell.exe -NoProfile -Command "
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class SQ {
    const string L = ""winsqlite3.dll"";
    [DllImport(L)] public static extern int sqlite3_open_v2(string f, out IntPtr db, int flags, IntPtr vfs);
    [DllImport(L)] public static extern int sqlite3_close(IntPtr db);
    [DllImport(L)] public static extern int sqlite3_prepare_v2(IntPtr db, string sql, int n, out IntPtr st, IntPtr t);
    [DllImport(L)] public static extern int sqlite3_step(IntPtr st);
    [DllImport(L)] public static extern int sqlite3_finalize(IntPtr st);
    [DllImport(L)] public static extern int sqlite3_bind_text(IntPtr st, int idx, byte[] val, int n, IntPtr d);
    [DllImport(L)] public static extern int sqlite3_bind_int64(IntPtr st, int idx, long val);
    [DllImport(L)] public static extern int sqlite3_bind_int(IntPtr st, int idx, int val);
    [DllImport(L)] public static extern IntPtr sqlite3_errmsg(IntPtr db);
    public static string Utf8(IntPtr p) {
        if (p == IntPtr.Zero) return string.Empty;
        int len = 0; while (Marshal.ReadByte(p, len) != 0) len++;
        byte[] b = new byte[len]; Marshal.Copy(p, b, 0, len);
        return System.Text.Encoding.UTF8.GetString(b);
    }
    public static byte[] ToUtf8(string s) {
        byte[] u = System.Text.Encoding.UTF8.GetBytes(s);
        byte[] r = new byte[u.Length + 1]; Array.Copy(u, r, u.Length);
        return r;
    }
}
'@
$dbPath = Join-Path $env:LocalAppData 'Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite'
$db = [IntPtr]::Zero; $st = [IntPtr]::Zero
[SQ]::sqlite3_open_v2($dbPath, [ref]$db, 6, [IntPtr]::Zero) | Out-Null
$id = [Guid]::NewGuid().ToString()
$now = [DateTime]::UtcNow.Ticks
$text = 'NOTE_TEXT'
$theme = 'NOTE_THEME'
$sql = 'INSERT INTO Note (Id, Text, Theme, IsOpen, CreatedAt, UpdatedAt) VALUES (?, ?, ?, ?, ?, ?)'
[SQ]::sqlite3_prepare_v2($db, $sql, -1, [ref]$st, [IntPtr]::Zero) | Out-Null
[SQ]::sqlite3_bind_text($st, 1, [SQ]::ToUtf8($id), -1, [IntPtr]::Zero) | Out-Null
[SQ]::sqlite3_bind_text($st, 2, [SQ]::ToUtf8($text), -1, [IntPtr]::Zero) | Out-Null
[SQ]::sqlite3_bind_text($st, 3, [SQ]::ToUtf8($theme), -1, [IntPtr]::Zero) | Out-Null
[SQ]::sqlite3_bind_int($st, 4, 1) | Out-Null
[SQ]::sqlite3_bind_int64($st, 5, $now) | Out-Null
[SQ]::sqlite3_bind_int64($st, 6, $now) | Out-Null
$rc = [SQ]::sqlite3_step($st)
if ($rc -eq 101) {
    Write-Host ('Note created: {0}' -f $id)
} else {
    $err = [SQ]::Utf8([SQ]::sqlite3_errmsg($db))
    Write-Host ('Error: {0}' -f $err)
}
[SQ]::sqlite3_finalize($st) | Out-Null
[SQ]::sqlite3_close($db) | Out-Null
"
```

- `NOTE_TEXT`: the note content
- `NOTE_THEME`: color — `Yellow`, `Green`, `Pink`, `Purple`, `Blue`, or `Charcoal`
- Flag `6` = `SQLITE_OPEN_READWRITE`
- Timestamps use .NET Ticks (bigint). Reopen Sticky Notes after creating to see the new note.

## Update a Note

Close the Sticky Notes app before writing.

```powershell
powershell.exe -NoProfile -Command "
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class SQ {
    const string L = ""winsqlite3.dll"";
    [DllImport(L)] public static extern int sqlite3_open_v2(string f, out IntPtr db, int flags, IntPtr vfs);
    [DllImport(L)] public static extern int sqlite3_close(IntPtr db);
    [DllImport(L)] public static extern int sqlite3_prepare_v2(IntPtr db, string sql, int n, out IntPtr st, IntPtr t);
    [DllImport(L)] public static extern int sqlite3_step(IntPtr st);
    [DllImport(L)] public static extern int sqlite3_finalize(IntPtr st);
    [DllImport(L)] public static extern int sqlite3_bind_text(IntPtr st, int idx, byte[] val, int n, IntPtr d);
    [DllImport(L)] public static extern int sqlite3_bind_int64(IntPtr st, int idx, long val);
    public static byte[] ToUtf8(string s) {
        byte[] u = System.Text.Encoding.UTF8.GetBytes(s);
        byte[] r = new byte[u.Length + 1]; Array.Copy(u, r, u.Length);
        return r;
    }
}
'@
$dbPath = Join-Path $env:LocalAppData 'Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite'
$db = [IntPtr]::Zero; $st = [IntPtr]::Zero
[SQ]::sqlite3_open_v2($dbPath, [ref]$db, 6, [IntPtr]::Zero) | Out-Null
$now = [DateTime]::UtcNow.Ticks
$sql = 'UPDATE Note SET Text = ?, UpdatedAt = ? WHERE Id = ?'
[SQ]::sqlite3_prepare_v2($db, $sql, -1, [ref]$st, [IntPtr]::Zero) | Out-Null
[SQ]::sqlite3_bind_text($st, 1, [SQ]::ToUtf8('NEW_TEXT'), -1, [IntPtr]::Zero) | Out-Null
[SQ]::sqlite3_bind_int64($st, 2, $now) | Out-Null
[SQ]::sqlite3_bind_text($st, 3, [SQ]::ToUtf8('NOTE_ID'), -1, [IntPtr]::Zero) | Out-Null
$rc = [SQ]::sqlite3_step($st)
if ($rc -eq 101) { Write-Host 'Note updated.' }
else { Write-Host 'Error updating note.' }
[SQ]::sqlite3_finalize($st) | Out-Null
[SQ]::sqlite3_close($db) | Out-Null
"
```

Replace `NOTE_ID` with the GUID and `NEW_TEXT` with the new content.

## Delete a Note

Soft-delete (marks as deleted, hidden from the app). Close Sticky Notes first.

```powershell
powershell.exe -NoProfile -Command "
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class SQ {
    const string L = ""winsqlite3.dll"";
    [DllImport(L)] public static extern int sqlite3_open_v2(string f, out IntPtr db, int flags, IntPtr vfs);
    [DllImport(L)] public static extern int sqlite3_close(IntPtr db);
    [DllImport(L)] public static extern int sqlite3_prepare_v2(IntPtr db, string sql, int n, out IntPtr st, IntPtr t);
    [DllImport(L)] public static extern int sqlite3_step(IntPtr st);
    [DllImport(L)] public static extern int sqlite3_finalize(IntPtr st);
    [DllImport(L)] public static extern int sqlite3_bind_text(IntPtr st, int idx, byte[] val, int n, IntPtr d);
    [DllImport(L)] public static extern int sqlite3_bind_int64(IntPtr st, int idx, long val);
    public static byte[] ToUtf8(string s) {
        byte[] u = System.Text.Encoding.UTF8.GetBytes(s);
        byte[] r = new byte[u.Length + 1]; Array.Copy(u, r, u.Length);
        return r;
    }
}
'@
$dbPath = Join-Path $env:LocalAppData 'Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite'
$db = [IntPtr]::Zero; $st = [IntPtr]::Zero
[SQ]::sqlite3_open_v2($dbPath, [ref]$db, 6, [IntPtr]::Zero) | Out-Null
$now = [DateTime]::UtcNow.Ticks
$sql = 'UPDATE Note SET DeletedAt = ? WHERE Id = ?'
[SQ]::sqlite3_prepare_v2($db, $sql, -1, [ref]$st, [IntPtr]::Zero) | Out-Null
[SQ]::sqlite3_bind_int64($st, 1, $now) | Out-Null
[SQ]::sqlite3_bind_text($st, 2, [SQ]::ToUtf8('NOTE_ID'), -1, [IntPtr]::Zero) | Out-Null
$rc = [SQ]::sqlite3_step($st)
if ($rc -eq 101) { Write-Host 'Note deleted.' }
else { Write-Host 'Error deleting note.' }
[SQ]::sqlite3_finalize($st) | Out-Null
[SQ]::sqlite3_close($db) | Out-Null
"
```

## Export All Notes

Export all notes to a text file:

```powershell
powershell.exe -NoProfile -Command "
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class SQ {
    const string L = ""winsqlite3.dll"";
    [DllImport(L)] public static extern int sqlite3_open_v2(string f, out IntPtr db, int flags, IntPtr vfs);
    [DllImport(L)] public static extern int sqlite3_close(IntPtr db);
    [DllImport(L)] public static extern int sqlite3_prepare_v2(IntPtr db, string sql, int n, out IntPtr st, IntPtr t);
    [DllImport(L)] public static extern int sqlite3_step(IntPtr st);
    [DllImport(L)] public static extern IntPtr sqlite3_column_text(IntPtr st, int c);
    [DllImport(L)] public static extern long sqlite3_column_int64(IntPtr st, int c);
    [DllImport(L)] public static extern int sqlite3_finalize(IntPtr st);
    public static string Utf8(IntPtr p) {
        if (p == IntPtr.Zero) return string.Empty;
        int len = 0; while (Marshal.ReadByte(p, len) != 0) len++;
        byte[] b = new byte[len]; Marshal.Copy(p, b, 0, len);
        return System.Text.Encoding.UTF8.GetString(b);
    }
}
'@
$dbPath = Join-Path $env:LocalAppData 'Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite'
$outPath = 'OUTPUT_PATH'
$db = [IntPtr]::Zero; $st = [IntPtr]::Zero
[SQ]::sqlite3_open_v2($dbPath, [ref]$db, 1, [IntPtr]::Zero) | Out-Null
$sql = ""SELECT Id, Text, Theme, CreatedAt FROM Note WHERE DeletedAt IS NULL OR DeletedAt = '' OR DeletedAt = 0 ORDER BY CreatedAt""
[SQ]::sqlite3_prepare_v2($db, $sql, -1, [ref]$st, [IntPtr]::Zero) | Out-Null
$sb = New-Object System.Text.StringBuilder
$i = 0
while ([SQ]::sqlite3_step($st) -eq 100) {
    $id = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 0))
    $text = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 1))
    $theme = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 2))
    $ticks = [SQ]::sqlite3_column_int64($st, 3)
    $created = if ($ticks -gt 0) { [DateTime]::new($ticks).ToString('yyyy-MM-dd HH:mm') } else { 'unknown' }
    [void]$sb.AppendLine(('=== Note {0} [{1}] Created: {2} ===' -f ($i+1), $theme, $created))
    [void]$sb.AppendLine($text)
    [void]$sb.AppendLine('')
    $i++
}
[System.IO.File]::WriteAllText($outPath, $sb.ToString(), [System.Text.Encoding]::UTF8)
Write-Host ('{0} notes exported to {1}' -f $i, $outPath)
[SQ]::sqlite3_finalize($st) | Out-Null
[SQ]::sqlite3_close($db) | Out-Null
"
```

Replace `OUTPUT_PATH` with the desired file path (e.g., `C:\Users\me\Desktop\sticky-notes-export.txt`).

## Open Sticky Notes App

```powershell
cmd.exe /c start "" "shell:AppsFolder\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe!App"
```

## Common Workflows

### Quick capture via agent

```
1. Agent receives info to save (e.g., a phone number, meeting notes)
2. sticky-notes: create a note with the content
3. User opens Sticky Notes app to see it on desktop
```

### Search and retrieve

```
1. User asks "what was that note about the API key?"
2. sticky-notes: search notes for "API key"
3. sticky-notes: read the full note by ID
```

### Backup notes before reset

```
1. sticky-notes: export all notes to a text file
2. Save export to Dropbox or other backup location
```

### Daily review

```
1. sticky-notes: list all notes
2. Agent summarizes note contents for the user
3. Identify stale notes for cleanup
```

## Notes

- **Read operations** (list, read, search, export) are safe while Sticky Notes is open — they use `SQLITE_OPEN_READONLY`.
- **Write operations** (create, update, delete) require Sticky Notes to be closed to avoid database conflicts.
- Uses `winsqlite3.dll` from `C:\Windows\System32` — shipped with Windows 10 1803+ (zero dependencies).
- UTF-8 support via custom marshaling — Chinese and other non-ASCII text works correctly.
- Timestamps are .NET Ticks (bigint) — 100-nanosecond intervals since 0001-01-01. Converted to readable dates in output.
- The database is at: `%LocalAppData%\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite`
- If the database doesn't exist, open the Sticky Notes app and create at least one note.
- Notes synced via Microsoft account may also appear in OneNote — changes made here will sync on next app open.
- The delete operation is a soft-delete (`DeletedAt` ticks) — same as the app's own delete behavior.
- Theme colors: `Yellow`, `Green`, `Pink`, `Purple`, `Blue`, `Charcoal`.
