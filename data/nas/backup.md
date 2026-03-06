## Backup Strategy

### 3-2-1 Rule Implementation

```
Primary copy: NAS (RAID protected)
Second copy: External USB drive (monthly rotation)
Third copy: Cloud (B2/S3/Glacier, encrypted)
```

### Common Traps

1. **Sync ≠ backup** — Dropbox/Drive sync deletes propagate. Use versioned backup, not sync.

2. **Cloud-only is risky** — Provider outage, account suspension, sync corruption. Local copy mandatory.

3. **Encryption before cloud** — NAS-side encryption (Hyper Backup, Cryptomator) before upload. Don't trust provider encryption alone.

4. **Test restore quarterly** — Pick random files, restore to different location. Verify content integrity.

5. **Retention policies matter** — Keep 30-day daily, 12-month monthly, 7-year annual for important data.

### What to Backup First

Priority order when storage limited:

1. **Irreplaceable** — Photos, documents, creative work
2. **Expensive to recreate** — VMs, configs, databases
3. **Convenient to have** — Media library (can re-rip/download)

### Backup Verification

Monthly: Check backup job logs
Quarterly: Restore test (5 random files)
Annually: Full disaster recovery drill

### Off-site Options by Budget

| Option | Cost | Recovery Speed |
|--------|------|----------------|
| Cloud (B2) | ~$5/TB/mo | Hours-days |
| External drive at friend's house | One-time | Hours |
| Second NAS at office | High upfront | Fast |
| Safety deposit box rotation | Low | Slow |
