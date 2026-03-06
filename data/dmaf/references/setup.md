# DMAF Setup Reference

Full reference for setting up DMAF end-to-end. Ask the user for their GCP project ID first — it drives everything else.

## Variables (resolve before starting)

```bash
PROJECT=your-project-id          # Ask user
REGION=us-central1               # Default, confirm with user
SA=dmaf-runner@${PROJECT}.iam.gserviceaccount.com
MEDIA_BUCKET=gs://${PROJECT}-whatsapp-media
KNOWN_BUCKET=gs://${PROJECT}-known-people
```

---

## 1. GCP Project

```bash
gcloud projects create $PROJECT --name="DMAF"
gcloud config set project $PROJECT

gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  cloudscheduler.googleapis.com \
  secretmanager.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com

gcloud firestore databases create --location=$REGION
```

---

## 2. Service Account + IAM

```bash
gcloud iam service-accounts create dmaf-runner --display-name="DMAF runner"

for role in roles/datastore.user roles/secretmanager.secretAccessor roles/storage.objectAdmin; do
  gcloud projects add-iam-policy-binding $PROJECT \
    --member="serviceAccount:$SA" --role="$role"
done
```

*(Grant `roles/run.invoker` after the Cloud Run job is created — Step 7)*

---

## 3. GCS Buckets

```bash
gsutil mb -p $PROJECT -l $REGION $MEDIA_BUCKET
gsutil mb -p $PROJECT -l $REGION $KNOWN_BUCKET
gsutil iam ch serviceAccount:$SA:objectAdmin $MEDIA_BUCKET
gsutil iam ch serviceAccount:$SA:objectViewer $KNOWN_BUCKET
```

---

## 4. Reference Photos (Known People)

Ask user to provide photos. One subdirectory per person, named as you want them recognised:
```
Alice/ → alice_001.jpg, alice_002.jpg
Bob/   → bob_001.jpg
```

Upload:
```bash
gsutil -m rsync -r -x ".*Zone\.Identifier$" \
  data/known_people/ ${KNOWN_BUCKET}/
```

---

## 5. Google Photos OAuth Token

1. Guide user to [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials)
2. Enable **Photos Library API**
3. Create **OAuth 2.0 Client ID** → Desktop app → Download as `client_secret.json`
4. Place `client_secret.json` in the DMAF repo root
5. Run auth flow:
   ```bash
   source .venv/bin/activate
   python -c "from dmaf.google_photos.auth import get_creds; get_creds()"
   ```
   This creates `token.json`
6. Upload to Secret Manager:
   ```bash
   gcloud secrets create dmaf-photos-token --project=$PROJECT
   gcloud secrets versions add dmaf-photos-token --data-file=token.json
   ```

---

## 6. Config YAML → Secret Manager

Create `config.yaml` from [`config.cloud.example.yaml`](../../config.cloud.example.yaml). Key fields to fill in:

```yaml
watch_dirs:
  - "gs://${PROJECT}-whatsapp-media/"

known_people_gcs_uri: "gs://${PROJECT}-known-people"

recognition:
  backend: auraface    # auraface (Apache 2.0) | insightface | face_recognition
  tolerance: 0.5

google_photos_token_secret: "dmaf-photos-token"
google_photos_album_name: "Family — DMAF Auto-Import"   # or null

dedup:
  backend: firestore
  firestore_project: ${PROJECT}
  firestore_collection: dmaf_files

alerting:
  enabled: true
  timezone: "UTC"          # IANA name — e.g. "America/New_York", "Asia/Jerusalem"
  recipients: ["user@example.com"]
```

Push to Secret Manager:
```bash
gcloud secrets create dmaf-config --project=$PROJECT
gcloud secrets versions add dmaf-config --data-file=config.yaml
```

For SMTP alerts: user needs a Gmail App Password. Guide them to:
[Google Account → Security → App Passwords](https://myaccount.google.com/apppasswords)

---

## 7. Cloud Build + Cloud Run Job

```bash
# Build and push Docker image
cd /path/to/DMAF
gcloud builds submit --config cloudbuild.yaml

# Create the job
gcloud run jobs create dmaf-scan \
  --image=gcr.io/${PROJECT}/dmaf:latest \
  --region=$REGION \
  --service-account=$SA \
  --set-secrets="/run/secrets/dmaf-config=dmaf-config:latest,/run/secrets/dmaf-photos-token=dmaf-photos-token:latest" \
  --memory=2Gi --cpu=2 --max-retries=0 --task-timeout=20m

# Grant scheduler permission
gcloud run jobs add-iam-policy-binding dmaf-scan \
  --region=$REGION --member="serviceAccount:$SA" --role="roles/run.invoker"
```

---

## 8. Cloud Scheduler

```bash
gcloud scheduler jobs create http dmaf-schedule \
  --location=$REGION \
  --schedule="0 * * * *" \
  --uri="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT}/jobs/dmaf-scan:run" \
  --message-body='{}' \
  --oauth-service-account-email="$SA" \
  --oauth-token-scope="https://www.googleapis.com/auth/cloud-platform"
```

---

## 9. Firestore Indexes

```bash
for collection in error_events borderline_events; do
  gcloud firestore indexes composite create \
    --collection-group=$collection \
    --field-config field-path=alerted,order=ASCENDING \
    --field-config field-path=created_ts,order=ASCENDING
done
```

---

## 10. OpenClaw Media Sync

Create `~/.openclaw/workspace/scripts/dmaf-sync.sh` (or copy from [`scripts/dmaf-sync.sh`](../scripts/dmaf-sync.sh)).
Set `GCS_BUCKET` to match your staging bucket URI.

Add to system crontab:
```bash
crontab -e
# Add:
*/30 * * * * /home/openclaw/.openclaw/workspace/scripts/dmaf-sync.sh >> /tmp/dmaf-sync.log 2>&1
```

Configure OpenClaw to accept group media (in `openclaw.json`):
```json5
{
  channels: {
    whatsapp: {
      groupPolicy: "allowlist",
      groups: { "*": { requireMention: true } },
      groupAllowFrom: ["*"],
      mediaMaxMb: 50
    }
  }
}
```

Then: `openclaw gateway restart`

---

## Verification

```bash
# 1. Manual test scan
gcloud run jobs execute dmaf-scan --region=$REGION --async

# 2. Check logs (wait ~2 min)
gcloud logging read \
  'resource.type="cloud_run_job" AND resource.labels.job_name="dmaf-scan"' \
  --limit=30 --format='value(textPayload)' --freshness=10m

# 3. Force a sync
bash ~/.openclaw/workspace/scripts/dmaf-sync.sh

# 4. Ask someone to send a WhatsApp group photo and verify it appears in Google Photos
```
