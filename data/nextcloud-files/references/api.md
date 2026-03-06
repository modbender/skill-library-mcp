# Nextcloud API Reference

Read this file when you need details on specific endpoints, error codes, or field values
not covered by the main SKILL.md.

## Table of Contents
1. [WebDAV - Base URL & Auth](#1-webdav--base-url--auth)
2. [WebDAV Methods](#2-webdav-methods)
3. [OCS - Sharing API](#3-ocs--sharing-api)
4. [OCS - User & Capabilities](#4-ocs--user--capabilities)
5. [OCS - System Tags](#5-ocs--system-tags)
6. [Share Permissions Bitmask](#6-share-permissions-bitmask)
7. [Error Codes](#7-error-codes)
8. [PROPFIND Properties](#8-propfind-properties)

---

## 1. WebDAV - Base URL & Auth

```
Base URL : {NC_URL}/remote.php/dav/files/{username}/
Auth     : HTTP Basic (username + app password)
Headers  : OCS-APIRequest: true   (for OCS endpoints only)
           Accept: application/json (for OCS JSON responses)
```

All paths are relative to the user's root. Example:
```
/remote.php/dav/files/alice/Documents/report.pdf
```

---

## 2. WebDAV Methods

### GET - Read file
```
GET /remote.php/dav/files/{user}/{path}
Response: file content (binary or text)
Status: 200 OK | 404 Not Found | 401 Unauthorized
```

### PUT - Create or overwrite file
```
PUT /remote.php/dav/files/{user}/{path}
Body: file content
Headers: Content-Type: text/plain (or appropriate MIME)
Status: 201 Created | 204 No Content (overwrite) | 409 Conflict (parent missing)
```

### MKCOL - Create directory
```
MKCOL /remote.php/dav/files/{user}/{path}
Status: 201 Created | 405 Already Exists | 409 Parent missing
```

### DELETE - Remove file or directory
```
DELETE /remote.php/dav/files/{user}/{path}
Status: 204 No Content | 404 Not Found
Note: Nextcloud moves to trash if trashbin app is enabled.
```

### MOVE - Rename or move
```
MOVE /remote.php/dav/files/{user}/{old_path}
Headers:
  Destination: {full_url_of_new_path}
  Overwrite: T (overwrite) | F (fail if exists)
Status: 201 Created | 204 No Content | 412 Precondition Failed (Overwrite:F, target exists)
```

### COPY - Duplicate
```
COPY /remote.php/dav/files/{user}/{src}
Headers:
  Destination: {full_url_of_dst}
  Overwrite: T | F
  Depth: infinity (for directories)
Status: 201 Created | 204 No Content
```

### PROPFIND - List directory / file metadata
```
PROPFIND /remote.php/dav/files/{user}/{path}
Headers: Depth: 0 (file only) | 1 (one level) | infinity (recursive, expensive)
Body: XML propfind request (see SKILL.md)
Status: 207 Multi-Status
```

### PROPPATCH - Set properties (favorites, etc.)
```
PROPPATCH /remote.php/dav/files/{user}/{path}
Body: XML propertyupdate
  <oc:favorite>1</oc:favorite>  (1=favorite, 0=unfavorite)
Status: 207 Multi-Status
```

### SEARCH - Search by filename (DASL)
```
SEARCH /remote.php/dav
Body: XML basicsearch with <d:like> on <d:displayname>
Status: 207 Multi-Status
Note: Full-text content search requires the Nextcloud Full Text Search app.
```

### HEAD - Check existence
```
HEAD /remote.php/dav/files/{user}/{path}
Status: 200 OK (exists) | 404 Not Found
```

---

## 3. OCS - Sharing API

Base URL: `{NC_URL}/ocs/v2.php/apps/files_sharing/api/v1`
Headers: `OCS-APIRequest: true`, `Accept: application/json`

### POST /shares - Create share
```
Body (form):
  path        : string  - path to file/folder (required)
  shareType   : int     - 0=user, 1=group, 3=public link, 4=email (required)
  shareWith   : string  - user/group ID (required for types 0 and 1)
  permissions : int     - bitmask (default: 17 for user shares, 1 for public links)
  password    : string  - optional, public links only
  expireDate  : string  - "YYYY-MM-DD", optional
  label       : string  - optional display label
  attributes  : string  - JSON array, e.g. [{"scope":"permissions","key":"download","value":false}]
Response: JSON with share data including id, token, url
OCS status: 100 = success
```

### GET /shares - List shares
```
Params:
  path     : string (optional filter)
  reshares : bool   (include reshares)
  subfiles : bool   (include shares in subfolders)
Response: JSON array of share objects
```

### PUT /shares/{id} - Update share
```
Body: same optional fields as POST
```

### DELETE /shares/{id} - Delete share
```
Status: 100 OCS success
```

---

## 4. OCS - User & Capabilities

### GET /ocs/v2.php/cloud/user
```
Returns: id, displayname, email, quota (used/free/total/relative), groups, language
```

### GET /ocs/v2.php/cloud/capabilities
```
Returns: version (major/minor/string), capabilities (files, sharing, theming, etc.)
Useful to detect: NC version, enabled apps, max file size, default share permissions
```

---

## 5. OCS - System Tags

Base URL: `{NC_URL}/remote.php/dav`

### PROPFIND /systemtags/ - List tags
```
Headers: Depth: 1
Props: oc:id, oc:display-name, oc:user-visible, oc:user-assignable
```

### POST /systemtags/ - Create tag
```
Body: JSON {"name": "tag-name", "userVisible": true, "userAssignable": true}
Response: 201 Created, Location header contains tag ID
```

### PUT /systemtags-relations/files/{fileId}/{tagId} - Assign tag
```
Status: 201 Created | 409 Already assigned
fileId: from oc:fileid property in PROPFIND response
```

### DELETE /systemtags-relations/files/{fileId}/{tagId} - Remove tag

---

## 6. Share Permissions Bitmask

| Value | Permission |
|-------|-----------|
| 1     | Read |
| 2     | Update (edit existing files) |
| 4     | Create (add new files) |
| 8     | Delete |
| 16    | Share (re-share) |
| 31    | All (1+2+4+8+16) |

**Common combos:**
- `1` - Read-only public link (default for public shares)
- `17` - Read + Share (default for user shares)
- `7` - Read + Update + Create (collaborative folder, no delete)
- `31` - Full access

---

## 7. Error Codes

### WebDAV HTTP codes
| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content (success, no body) |
| 207 | Multi-Status (PROPFIND/SEARCH responses) |
| 401 | Unauthorized - check credentials |
| 403 | Forbidden - insufficient permissions |
| 404 | Not Found |
| 405 | Method Not Allowed (MKCOL on existing path) |
| 409 | Conflict - parent directory doesn't exist |
| 412 | Precondition Failed - e.g. MOVE with Overwrite:F and target exists |
| 423 | Locked |
| 507 | Insufficient Storage - quota exceeded |

### OCS status codes
| Code | Meaning |
|------|---------|
| 100 | Success |
| 400 | Bad request / missing parameter |
| 403 | Forbidden |
| 404 | Not found |
| 997 | Unauthenticated |

---

## 8. PROPFIND Properties

Namespaces:
- `d:` → `DAV:`
- `oc:` → `http://owncloud.org/ns`
- `nc:` → `http://nextcloud.org/ns`

| Property | Namespace | Description |
|----------|-----------|-------------|
| `d:getlastmodified` | d | Last modified date (RFC 1123) |
| `d:getcontentlength` | d | File size in bytes |
| `d:getcontenttype` | d | MIME type |
| `d:resourcetype` | d | `<d:collection>` if folder, empty if file |
| `d:getetag` | d | ETag for cache validation |
| `oc:fileid` | oc | Unique numeric file ID (needed for tags) |
| `oc:permissions` | oc | Permission string: G=read, W=write, D=delete, R=share, M=mounted, S=shared |
| `oc:size` | oc | Total size including subdirectories |
| `oc:favorite` | oc | 1=favorited, 0=not |
| `oc:share-types` | oc | Array of active share types |
| `oc:owner-id` | oc | Owner's user ID |
| `nc:has-preview` | nc | true/false - preview thumbnail available |
