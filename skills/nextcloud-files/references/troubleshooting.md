# Nextcloud Skill - Troubleshooting

## Credentials missing

```
NextcloudError: Credentials missing. Set NC_URL / NC_USER / NC_APP_KEY in
~/.openclaw/secrets/nextcloud_creds or as environment variables.
```
→ Run `python3 scripts/setup.py` or create the file manually (see SKILL.md).

---

## 401 Unauthorized

Cause: wrong username/password, or account locked.

Fixes:
- Confirm the App Password is still active: Nextcloud → Settings → Security → App passwords
- App passwords are invalidated when the account password changes
- Try `curl -u user:pass https://cloud.example.com/ocs/v2.php/cloud/user` to isolate

---

## 403 Forbidden

Cause: the user doesn't have permission on the target path, or the operation is disabled.

Fixes:
- Check that the authenticated user owns or has write access to the path
- If using a shared/group folder, verify permissions in NC admin
- Check `config.json`: `allow_write`, `allow_delete`, `allow_share` may be `false`

---

## 404 Not Found

Cause: path doesn't exist, typo in path, or wrong NC_URL.

Fixes:
- Run `python3 scripts/nextcloud.py ls /` to verify root is reachable
- Check that NC_URL has no trailing slash and points to the NC root, not a sub-path

---

## 405 Method Not Allowed on MKCOL

Cause: directory already exists (normal - the skill treats 405 as success).
If you see it as an error elsewhere: the WebDAV method may be disabled.

---

## 409 Conflict on PUT

Cause: parent directory doesn't exist.

Fix: `write_file` creates parents automatically. If it fails, create the path manually:
```bash
python3 scripts/nextcloud.py mkdir /path/to/parent
```

---

## 507 Insufficient Storage

Cause: quota exceeded.

Fix:
```bash
python3 scripts/nextcloud.py quota
```
Then free space or ask the NC admin to raise your quota.

---

## PROPFIND returns empty or partial results

Cause: Depth header too small, or path points to a file, not a directory.

Fix:
```bash
python3 scripts/nextcloud.py ls /path --depth 2  # increase depth
python3 scripts/nextcloud.py exists /path         # confirm it's a directory
```

---

## Search returns no results

Cause: filename search (DASL `displayname LIKE`) only matches file/folder names.
Content search requires the **Full Text Search** app in Nextcloud.

Fix: ensure the search query matches a substring of the filename, not content.

---

## Share creation fails (OCS 403)

Cause: public sharing may be disabled by the NC admin.

Check: NC Admin → Settings → Sharing → "Allow apps to use the Share API"

---

## PermissionDeniedError: base_path

```
PermissionDeniedError: Path '/other/folder' is outside allowed base_path '/Jarvis'
```
→ Either update `base_path` in `config.json`, or use a path inside the allowed subtree.

---

## SSL / Certificate errors

Cause: self-signed certificate on the NC instance.

Fix (not recommended for production):
```python
import urllib3
urllib3.disable_warnings()
# or pass verify=False to requests - patch nextcloud.py session if needed
```
Better fix: install a valid certificate (Let's Encrypt).

---

## Tags: file_id is empty

Cause: `oc:fileid` is not returned by default in some PROPFIND responses.

Fix: the skill includes `oc:fileid` in all `list_dir` calls. If empty, use `ls --json` and inspect:
```bash
python3 scripts/nextcloud.py ls /path --json | python3 -c "import sys,json; [print(f['name'], f['file_id']) for f in json.load(sys.stdin)]"
```
