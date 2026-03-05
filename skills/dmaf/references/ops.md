# DMAF Operations Reference

Day-to-day commands for managing a running DMAF deployment.

---

## Scan Operations

```bash
# Trigger a manual scan (async — returns immediately)
gcloud run jobs execute dmaf-scan --region=us-central1 --async

# Wait for completion
gcloud run jobs executions list --job=dmaf-scan --region=us-central1 --limit=3

# View scan logs (last hour)
gcloud logging read \
  'resource.type="cloud_run_job" AND resource.labels.job_name="dmaf-scan"' \
  --limit=50 --format='value(textPayload)' --freshness=1h

# View only summary lines (fast)
gcloud logging read \
  'resource.type="cloud_run_job" AND resource.labels.job_name="dmaf-scan"' \
  --limit=20 --freshness=1h \
  --format='value(textPayload)' | grep -E "processed|matched|uploaded|error"
```

---

## Known People Management

```bash
PROJECT=your-project-id
KNOWN_BUCKET=gs://${PROJECT}-known-people

# Add a new person — create subdir named after them
gsutil cp /path/to/photos/*.jpg ${KNOWN_BUCKET}/NewPerson/

# View current known people
gsutil ls ${KNOWN_BUCKET}/

# View photos for a specific person
gsutil ls ${KNOWN_BUCKET}/Alice/

# Remove a person
gsutil -m rm -r ${KNOWN_BUCKET}/OldPerson/

# Sync local known_people directory to GCS
gsutil -m rsync -r -x ".*Zone\.Identifier$" \
  data/known_people/ ${KNOWN_BUCKET}/
```

No rebuild needed — the Cloud Run job downloads reference photos at startup each run.

---

## Config Updates

```bash
# Edit and push a new config version
gcloud secrets versions add dmaf-config --data-file=config.yaml

# View current config
gcloud secrets versions access latest --secret=dmaf-config | less

# View config history
gcloud secrets versions list dmaf-config
```

Key config changes and their effects:
- `recognition.tolerance` → stricter/looser matching (lower = fewer false positives)
- `alerting.timezone` → IANA timezone for email timestamps (e.g. `"America/New_York"`)
- `alerting.enabled` → toggle email alerts
- `google_photos_album_name` → change/create target album (takes effect next scan)
- `delete_source_after_upload: true` → clean up GCS after upload (saves storage cost)

---

## Media Sync (OpenClaw Side)

```bash
# Force sync now (don't wait for cron)
bash ~/.openclaw/workspace/scripts/dmaf-sync.sh

# Check sync history
tail -50 /tmp/dmaf-sync.log

# Check what's pending in the inbound directory
ls -la ~/.openclaw/media/inbound/ | wc -l

# Check crontab is set
crontab -l | grep dmaf
```

---

## GCS Staging Bucket

```bash
PROJECT=your-project-id
MEDIA_BUCKET=gs://${PROJECT}-whatsapp-media

# See what's in the staging bucket (not yet scanned)
gsutil ls $MEDIA_BUCKET

# Count unprocessed files
gsutil ls $MEDIA_BUCKET | wc -l

# Clean up staging bucket after a test (careful — deletes unscanned files)
gsutil -m rm "${MEDIA_BUCKET}/**"
```

---

## Firestore (Dedup Database)

```bash
PROJECT=your-project-id

# Count processed files
gcloud firestore indexes list --project=$PROJECT  # verify indexes exist

# View recent error events (Firestore console is easier for browsing)
# URL: https://console.firebase.google.com/project/${PROJECT}/firestore
```

To reset dedup for a specific file (force reprocess):
```bash
# Get doc ID = sha256(gs://full-uri)[:32]
python3 -c "
import hashlib
uri = 'gs://your-bucket/filename.jpg'
print(hashlib.sha256(uri.encode()).hexdigest()[:32])
"
# Then delete the doc in Firestore console or via gcloud
```

---

## Cloud Run Job Management

```bash
PROJECT=your-project-id

# View job configuration
gcloud run jobs describe dmaf-scan --region=us-central1

# Update job (e.g. more memory)
gcloud run jobs update dmaf-scan --region=us-central1 --memory=4Gi

# View recent executions
gcloud run jobs executions list --job=dmaf-scan --region=us-central1 --limit=10

# Delete a stuck execution
gcloud run jobs executions delete EXECUTION_NAME --region=us-central1
```

---

## Google Photos Token Refresh

If uploads stop working (token expired or revoked):

```bash
cd /path/to/DMAF
source .venv/bin/activate
python -c "from dmaf.google_photos.auth import get_creds; get_creds()"
# Re-authorize in browser, then:
gcloud secrets versions add dmaf-photos-token --data-file=token.json
```

---

## Cloud Scheduler

```bash
# Check scheduler job
gcloud scheduler jobs describe dmaf-schedule --location=us-central1

# Trigger manually (outside of schedule)
gcloud scheduler jobs run dmaf-schedule --location=us-central1

# Change schedule (e.g. every 30 min instead of hourly)
gcloud scheduler jobs update http dmaf-schedule \
  --location=us-central1 --schedule="*/30 * * * *"
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| No files in staging bucket | OpenClaw not capturing / sync not running | Check `openclaw gateway status`, run sync manually |
| Scan runs but 0 matches | Tolerance too strict / known_people wrong | Lower `tolerance`, verify `gsutil ls $KNOWN_BUCKET` |
| Upload errors in logs | Google Photos token expired | Refresh token (see above) |
| `403 PERMISSION_DENIED` in scheduler | IAM binding missing | Re-run `add-iam-policy-binding` for `roles/run.invoker` |
| `404` errors in Firestore | Old code bug — should not happen in current version | Check deployed image tag matches latest build |
| Alert emails not arriving | SMTP config wrong / App Password invalid | Check `alerting.smtp` in config, regenerate App Password |
