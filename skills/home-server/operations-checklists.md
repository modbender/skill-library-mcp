# Operations Checklists

## Daily Signals

- Check service health dashboards for failed checks.
- Confirm disk utilization trend is stable.
- Verify backup jobs completed without errors.

## Weekly Maintenance

- Review container and host update advisories.
- Rotate logs and inspect sudden growth.
- Revalidate exposed ports against intended policy.

## Before Any Upgrade

- Confirm current backup snapshot age is acceptable.
- Capture a sanitized deployment snapshot: image tags, ports, mounted paths, and feature flags.
- Never export raw environment variables or secret values into notes.
- Define explicit rollback trigger and rollback owner.
- Apply updates in low-risk order: proxy -> shared services -> apps.

## After Upgrade

- Validate login flow and critical user actions.
- Compare resource usage with pre-upgrade baseline.
- Close with a short incident-style note even if no issues occurred.

## Monthly Reliability Check

- Test at least one restore path end-to-end.
- Audit stale services that no longer have an owner.
- Review long-lived warnings and convert to actions.
