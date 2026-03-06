---
name: win-browser
description: Browser integration — open URLs, read bookmarks and history from Edge/Chrome, get active tabs, list downloads, zero dependencies.
metadata:
  {
    "openclaw":
      {
        "emoji": "🌐",
        "os": ["win32"],
      },
  }
---

# win-browser

Read bookmarks and browsing history from Microsoft Edge and Google Chrome, open URLs, get active tab titles, and list downloads. Uses built-in PowerShell + winsqlite3.dll for history access.

Works on Windows 10/11 with Edge and/or Chrome.

## Detect Installed Browsers

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$browsers = @(
    @{ Name='Microsoft Edge'; Path='C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'; Data="$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default" },
    @{ Name='Google Chrome'; Path='C:\Program Files\Google\Chrome\Application\chrome.exe'; Data="$env:LOCALAPPDATA\Google\Chrome\User Data\Default" },
    @{ Name='Google Chrome (x86)'; Path='C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'; Data="$env:LOCALAPPDATA\Google\Chrome\User Data\Default" },
    @{ Name='Firefox'; Path='C:\Program Files\Mozilla Firefox\firefox.exe'; Data='' },
    @{ Name='Brave'; Path='C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'; Data="$env:LOCALAPPDATA\BraveSoftware\Brave-Browser\User Data\Default" }
)
foreach ($b in $browsers) {
    if (Test-Path $b.Path) {
        $ver = (Get-Item $b.Path).VersionInfo.ProductVersion
        $hasData = if ($b.Data -and (Test-Path $b.Data)) { 'data found' } else { 'no profile data' }
        Write-Host ('{0} v{1} ({2})' -f $b.Name, $ver, $hasData)
    }
}
$handler = (Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice' -ErrorAction SilentlyContinue).ProgId
Write-Host ''
Write-Host ('Default HTTPS handler: {0}' -f $handler)
"
```

## Open URL

Opens a URL in the default browser:

```powershell
powershell.exe -NoProfile -Command "
Start-Process 'URL_HERE'
"
```

Replace `URL_HERE` with the full URL (e.g., `https://example.com`).

### Open URL in Specific Browser

```powershell
powershell.exe -NoProfile -Command "
Start-Process 'msedge' -ArgumentList 'URL_HERE'
"
```

Replace `msedge` with `chrome`, `firefox`, or `brave` for other browsers.

## Get Active Tab Titles

Shows titles of all open browser windows (reflects the active tab in each window):

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Get-Process | Where-Object { $_.MainWindowTitle -and ($_.ProcessName -match 'msedge|chrome|firefox|brave') } | ForEach-Object {
    Write-Host ('{0}: {1}' -f $_.ProcessName, $_.MainWindowTitle)
}
"
```

## Read Bookmarks (Edge)

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$path = \"$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Bookmarks\"
if (!(Test-Path $path)) { Write-Host 'Edge bookmarks not found'; exit }
$json = Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json

function Show-BM($node, $indent) {
    if ($node.type -eq 'url') {
        Write-Host ((' ' * $indent) + $node.name)
        Write-Host ((' ' * $indent) + '  ' + $node.url)
    } elseif ($node.type -eq 'folder' -and $node.children) {
        Write-Host ((' ' * $indent) + '[' + $node.name + ']')
        foreach ($child in $node.children) { Show-BM $child ($indent + 2) }
    }
}
foreach ($root in $json.roots.PSObject.Properties) {
    if ($root.Value.children -and $root.Value.children.Count -gt 0) {
        Write-Host ('[' + $root.Name + ']')
        foreach ($child in $root.Value.children) { Show-BM $child 2 }
    }
}
"
```

## Read Bookmarks (Chrome)

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$path = \"$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Bookmarks\"
if (!(Test-Path $path)) { Write-Host 'Chrome bookmarks not found'; exit }
$json = Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json

function Show-BM($node, $indent) {
    if ($node.type -eq 'url') {
        Write-Host ((' ' * $indent) + $node.name)
        Write-Host ((' ' * $indent) + '  ' + $node.url)
    } elseif ($node.type -eq 'folder' -and $node.children) {
        Write-Host ((' ' * $indent) + '[' + $node.name + ']')
        foreach ($child in $node.children) { Show-BM $child ($indent + 2) }
    }
}
foreach ($root in $json.roots.PSObject.Properties) {
    if ($root.Value.children -and $root.Value.children.Count -gt 0) {
        Write-Host ('[' + $root.Name + ']')
        foreach ($child in $root.Value.children) { Show-BM $child 2 }
    }
}
"
```

## Search Bookmarks

Search across both Edge and Chrome bookmarks by keyword:

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$query = 'SEARCH_TERM'
$paths = @(
    @{ Browser='Edge'; Path=\"$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Bookmarks\" },
    @{ Browser='Chrome'; Path=\"$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Bookmarks\" }
)

function Search-BM($node, $q) {
    $results = @()
    if ($node.type -eq 'url') {
        if ($node.name -match $q -or $node.url -match $q) {
            $results += @{ name=$node.name; url=$node.url }
        }
    } elseif ($node.children) {
        foreach ($child in $node.children) { $results += Search-BM $child $q }
    }
    return $results
}

foreach ($p in $paths) {
    if (!(Test-Path $p.Path)) { continue }
    $json = Get-Content $p.Path -Raw -Encoding UTF8 | ConvertFrom-Json
    $found = @()
    foreach ($root in $json.roots.PSObject.Properties) {
        $found += Search-BM $root.Value $query
    }
    if ($found.Count -gt 0) {
        Write-Host ('{0}: {1} match(es)' -f $p.Browser, $found.Count)
        foreach ($r in $found) {
            Write-Host ('  ' + $r.name)
            Write-Host ('    ' + $r.url)
        }
    }
}
"
```

Replace `SEARCH_TERM` with your search keyword (case-insensitive regex).

## Read Recent History (Edge)

Reads the last N visited URLs from Edge history. Copies the database first (Edge locks it while running).

To use this command, save the following to a `.ps1` file and execute with `powershell.exe -NoProfile -ExecutionPolicy Bypass -File path\to\script.ps1`, or run inline if no `!=` characters cause issues.

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$src = \"$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\History\"
if (!(Test-Path $src)) { Write-Host 'Edge history not found'; exit }
$tmp = \"$env:TEMP\pcclaw_edge_hist.db\"
Copy-Item $src $tmp -Force

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class SQ {
    const string L = \"winsqlite3.dll\";
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

$db = [IntPtr]::Zero
[SQ]::sqlite3_open_v2($tmp, [ref]$db, 1, [IntPtr]::Zero) | Out-Null
$st = [IntPtr]::Zero
$sql = 'SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT NUM_RESULTS'
[SQ]::sqlite3_prepare_v2($db, $sql, -1, [ref]$st, [IntPtr]::Zero) | Out-Null
while ([SQ]::sqlite3_step($st) -eq 100) {
    $url = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 0))
    $title = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 1))
    $visits = [SQ]::sqlite3_column_int64($st, 2)
    $ts = [SQ]::sqlite3_column_int64($st, 3)
    $date = [DateTime]::new(1601,1,1).AddTicks($ts * 10).ToString('yyyy-MM-dd HH:mm')
    Write-Host (\"[{0}] ({1}x) {2}\" -f $date, $visits, $title)
    Write-Host (\"  {0}\" -f $url)
}
[SQ]::sqlite3_finalize($st) | Out-Null
[SQ]::sqlite3_close($db) | Out-Null
Remove-Item $tmp -Force -ErrorAction SilentlyContinue
"
```

Replace `NUM_RESULTS` with how many results to show (e.g., `20`).

- Timestamps are Chrome/Edge format: microseconds since 1601-01-01 UTC.
- The database is copied to `%TEMP%` first to avoid file locking issues.

## Read Recent History (Chrome)

Same as Edge, but with Chrome's history path:

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$src = \"$env:LOCALAPPDATA\Google\Chrome\User Data\Default\History\"
if (!(Test-Path $src)) { Write-Host 'Chrome history not found'; exit }
$tmp = \"$env:TEMP\pcclaw_chrome_hist.db\"
Copy-Item $src $tmp -Force

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class SQ {
    const string L = \"winsqlite3.dll\";
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

$db = [IntPtr]::Zero
[SQ]::sqlite3_open_v2($tmp, [ref]$db, 1, [IntPtr]::Zero) | Out-Null
$st = [IntPtr]::Zero
$sql = 'SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT NUM_RESULTS'
[SQ]::sqlite3_prepare_v2($db, $sql, -1, [ref]$st, [IntPtr]::Zero) | Out-Null
while ([SQ]::sqlite3_step($st) -eq 100) {
    $url = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 0))
    $title = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 1))
    $visits = [SQ]::sqlite3_column_int64($st, 2)
    $ts = [SQ]::sqlite3_column_int64($st, 3)
    $date = [DateTime]::new(1601,1,1).AddTicks($ts * 10).ToString('yyyy-MM-dd HH:mm')
    Write-Host (\"[{0}] ({1}x) {2}\" -f $date, $visits, $title)
    Write-Host (\"  {0}\" -f $url)
}
[SQ]::sqlite3_finalize($st) | Out-Null
[SQ]::sqlite3_close($db) | Out-Null
Remove-Item $tmp -Force -ErrorAction SilentlyContinue
"
```

## Search History

Search Edge or Chrome history by keyword in URL or title. Replace `BROWSER_NAME` with `Edge` or `Chrome`, and `SEARCH_TERM` with your keyword.

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$browser = 'BROWSER_NAME'
if ($browser -eq 'Edge') {
    $src = \"$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\History\"
} else {
    $src = \"$env:LOCALAPPDATA\Google\Chrome\User Data\Default\History\"
}
if (!(Test-Path $src)) { Write-Host \"$browser history not found\"; exit }
$tmp = \"$env:TEMP\pcclaw_search_hist.db\"
Copy-Item $src $tmp -Force

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class SQ {
    const string L = \"winsqlite3.dll\";
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

$db = [IntPtr]::Zero
[SQ]::sqlite3_open_v2($tmp, [ref]$db, 1, [IntPtr]::Zero) | Out-Null
$st = [IntPtr]::Zero
$sql = 'SELECT url, title, visit_count, last_visit_time FROM urls WHERE url LIKE ?1 OR title LIKE ?1 ORDER BY last_visit_time DESC LIMIT 30'
[SQ]::sqlite3_prepare_v2($db, $sql, -1, [ref]$st, [IntPtr]::Zero) | Out-Null
$pattern = [SQ]::ToUtf8('%SEARCH_TERM%')
[SQ]::sqlite3_bind_text($st, 1, $pattern, $pattern.Length - 1, [IntPtr]::Zero) | Out-Null
$count = 0
while ([SQ]::sqlite3_step($st) -eq 100) {
    $url = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 0))
    $title = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 1))
    $visits = [SQ]::sqlite3_column_int64($st, 2)
    $ts = [SQ]::sqlite3_column_int64($st, 3)
    $date = [DateTime]::new(1601,1,1).AddTicks($ts * 10).ToString('yyyy-MM-dd HH:mm')
    Write-Host (\"[{0}] ({1}x) {2}\" -f $date, $visits, $title)
    Write-Host (\"  {0}\" -f $url)
    $count++
}
[SQ]::sqlite3_finalize($st) | Out-Null
[SQ]::sqlite3_close($db) | Out-Null
Remove-Item $tmp -Force -ErrorAction SilentlyContinue
Write-Host ''
Write-Host (\"Found {0} result(s) in $browser history\" -f $count)
"
```

## List Downloads

List recent downloads from Edge or Chrome. Replace `BROWSER_NAME` with `Edge` or `Chrome`.

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$browser = 'BROWSER_NAME'
if ($browser -eq 'Edge') {
    $src = \"$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\History\"
} else {
    $src = \"$env:LOCALAPPDATA\Google\Chrome\User Data\Default\History\"
}
if (!(Test-Path $src)) { Write-Host \"$browser history not found\"; exit }
$tmp = \"$env:TEMP\pcclaw_dl_hist.db\"
Copy-Item $src $tmp -Force

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class SQ {
    const string L = \"winsqlite3.dll\";
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

$db = [IntPtr]::Zero
[SQ]::sqlite3_open_v2($tmp, [ref]$db, 1, [IntPtr]::Zero) | Out-Null
$st = [IntPtr]::Zero
$sql = 'SELECT target_path, total_bytes, start_time, end_time, state, tab_url FROM downloads ORDER BY start_time DESC LIMIT NUM_RESULTS'
[SQ]::sqlite3_prepare_v2($db, $sql, -1, [ref]$st, [IntPtr]::Zero) | Out-Null
while ([SQ]::sqlite3_step($st) -eq 100) {
    $path = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 0))
    $size = [SQ]::sqlite3_column_int64($st, 1)
    $startTs = [SQ]::sqlite3_column_int64($st, 2)
    $state = [SQ]::sqlite3_column_int64($st, 4)
    $tabUrl = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 5))
    $date = [DateTime]::new(1601,1,1).AddTicks($startTs * 10).ToString('yyyy-MM-dd HH:mm')
    $sizeMB = [math]::Round($size / 1MB, 1)
    $stateStr = switch ($state) { 0 {'in-progress'} 1 {'complete'} 2 {'cancelled'} 3 {'interrupted'} default {\"state=$state\"} }
    $fileName = [System.IO.Path]::GetFileName($path)
    Write-Host (\"[{0}] {1} ({2} MB, {3})\" -f $date, $fileName, $sizeMB, $stateStr)
    Write-Host (\"  From: {0}\" -f $tabUrl)
}
[SQ]::sqlite3_finalize($st) | Out-Null
[SQ]::sqlite3_close($db) | Out-Null
Remove-Item $tmp -Force -ErrorAction SilentlyContinue
"
```

Replace `NUM_RESULTS` with how many downloads to show (e.g., `20`).

- `state`: 0 = in-progress, 1 = complete, 2 = cancelled, 3 = interrupted
- Download records are in the same History database as browsing history.

## Most Visited Sites

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$src = \"$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\History\"
if (!(Test-Path $src)) { Write-Host 'Edge history not found'; exit }
$tmp = \"$env:TEMP\pcclaw_top_hist.db\"
Copy-Item $src $tmp -Force

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class SQ {
    const string L = \"winsqlite3.dll\";
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

$db = [IntPtr]::Zero
[SQ]::sqlite3_open_v2($tmp, [ref]$db, 1, [IntPtr]::Zero) | Out-Null
$st = [IntPtr]::Zero
$sql = 'SELECT url, title, visit_count FROM urls ORDER BY visit_count DESC LIMIT 20'
[SQ]::sqlite3_prepare_v2($db, $sql, -1, [ref]$st, [IntPtr]::Zero) | Out-Null
while ([SQ]::sqlite3_step($st) -eq 100) {
    $url = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 0))
    $title = [SQ]::Utf8([SQ]::sqlite3_column_text($st, 1))
    $visits = [SQ]::sqlite3_column_int64($st, 2)
    Write-Host (\"({0}x) {1}\" -f $visits, $title)
    Write-Host (\"  {0}\" -f $url)
}
[SQ]::sqlite3_finalize($st) | Out-Null
[SQ]::sqlite3_close($db) | Out-Null
Remove-Item $tmp -Force -ErrorAction SilentlyContinue
"
```

## Common Workflows

### Look up a previously visited page

```
1. win-browser: search history for keyword
2. Use the URL from results
```

### Find a bookmarked resource

```
1. win-browser: search bookmarks for keyword
2. Open the URL or use it in workflow
```

### Check what user was browsing

```
1. win-browser: read recent history (last 20)
2. Summarize browsing patterns
```

### Open a link and monitor

```
1. win-browser: open URL in default browser
2. win-browser: get active tab titles (verify it loaded)
```

## Notes

- **History database locking**: Edge/Chrome lock their History database while running. All history commands copy the DB to `%TEMP%` first, so they work while the browser is open.
- **Timestamps**: Chrome/Edge use WebKit timestamps — microseconds since 1601-01-01 UTC. Converted via `[DateTime]::new(1601,1,1).AddTicks(ts * 10)`.
- **Bookmarks**: Stored as JSON at `%LOCALAPPDATA%\{Browser}\User Data\Default\Bookmarks`. No locking issues — safe to read directly.
- **Downloads**: Stored in the same History SQLite database, in the `downloads` table.
- **Multiple profiles**: Commands read from the `Default` profile. For other profiles, change `Default` to `Profile 1`, `Profile 2`, etc. in the paths.
- **Firefox**: Uses a different database format (places.sqlite). Not currently supported — Edge and Chrome cover most Windows users.
- **Privacy**: All data is read locally. Nothing is sent anywhere.
- **winsqlite3.dll**: Ships with Windows 10 1803+. Zero external dependencies for history access.
