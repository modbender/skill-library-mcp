# Restic Home Backup Ops Checklist

## Daily checks
- `systemctl status restic-home-backup.timer`
- `journalctl -u restic-home-backup.service -n 80 --no-pager`
- `source /etc/restic-home.env && restic snapshots`

## Weekly checks
- `journalctl -u restic-home-prune.service -n 80 --no-pager`
- Verify snapshot count aligns with retention policy.

## Monthly checks
- `journalctl -u restic-home-check.service -n 120 --no-pager`
- Perform restore drill:
  - `mkdir -p /tmp/restic-restore-test`
  - `source /etc/restic-home.env && restic restore latest --target /tmp/restic-restore-test`
  - Validate representative files, then remove test directory.

## Common failures

### Wrong password
Symptoms: `wrong password or no key found`
- Confirm `/etc/restic-home.env` points to correct `RESTIC_PASSWORD_FILE`.
- Confirm password file permissions (`chmod 600`).

### Repo unreachable
Symptoms: timeout / connection refused
- Verify network path, endpoint DNS, firewall rules.
- Retry with direct `restic snapshots` for clean repro.

### Permission denied
Symptoms: cannot read env or source path
- Ensure service user has read access to backup source.
- Ensure env and password files are root-only but readable where needed.

## Safety
- Never run `restic forget --prune` with altered retention blindly.
- Never delete repository data without explicit user confirmation.
- Keep at least one independent offsite copy.
