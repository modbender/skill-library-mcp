# MCP Tools for Mobb Fixes

## scan_and_fix_vulnerabilities

### Parameters

Required:
- `path` (string): absolute path to the repo root

Optional:
- `offset` (number): pagination offset
- `limit` (number): max number of fixes to return (default 3)
- `maxFiles` (number): scan up to N recently changed files (default 10)
- `rescan` (boolean): force a full rescan
- `scanRecentlyChangedFiles` (boolean): when true and git has no changes, scan recently changed files from git history

### File Selection Rules

- If `path` is a valid git repo, scan changed/staged files.
- If no changes are found and `scanRecentlyChangedFiles` is true (or `maxFiles` is set), scan recently changed files from git history.
- If not a git repo, scan recently changed files in the directory.
- Exclude files larger than 5 MB.

### Rescan and Caching

- The service caches a fix report ID for ~2 hours.
- If a valid cached report exists and `rescan` is false, fetch fixes without rescanning.
- `rescan: true` forces a new scan and upload.
- Supplying `maxFiles` also forces a new scan.

### Pagination

- Use `offset` and `limit` to request additional fixes.
- Do not auto-page; only fetch more when the user explicitly asks.

### Example MCP Call

```json
{
  "path": "/absolute/path/to/repo",
  "limit": 3,
  "maxFiles": 10,
  "rescan": false
}
```

## fetch_available_fixes

Use to fetch a fixes summary without scanning or applying patches.

### Parameters

Required:
- `path` (string): absolute path to the repo root

Optional:
- `offset` (number): pagination offset
- `limit` (number): max number of fixes to return
- `fileFilter` (string[]): relative file paths to filter fixes
- `fetchFixesFromAnyFile` (boolean): fetch fixes for all files

### File Filtering Rules

- `fileFilter` and `fetchFixesFromAnyFile` are mutually exclusive.
- If `fileFilter` is provided, only fixes affecting those files are returned.
- If `fetchFixesFromAnyFile` is true, no file filtering is applied.
- If neither is provided, the tool filters to files with git status changes.

### Example MCP Call

```json
{
  "path": "/absolute/path/to/repo",
  "limit": 10
}
```

## check_for_new_available_fixes

Use to check for fresh fixes or applied fixes at the end of a session.

### Parameters

Required:
- `path` (string): absolute path to the repo root

### Behavior

- Requires a local git repo with an `origin` remote.
- Triggers background scans, an initial scan, and a one-time full scan per repo path.
- If auto-fix is enabled, fixes may be applied automatically and returned as an applied-fixes summary.
- If auto-fix is disabled, fresh fixes are returned for manual review and application.
- May return \"initial scan in progress\" or \"no fresh fixes\" depending on timing.

### Example MCP Call

```json
{
  "path": "/absolute/path/to/repo"
}
```
