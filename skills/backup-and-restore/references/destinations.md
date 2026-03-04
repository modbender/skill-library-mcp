# Cloud Destination Setup

## Amazon S3

**CLI needed:** `aws` (AWS CLI)
```bash
pip install awscli
# or: sudo apt install awscli
```

**Setup:**
1. Create an S3 bucket in your AWS account
2. Create an IAM user with S3 write access (or use an existing one)
3. Save credentials to `~/.openclaw/credentials/backup/aws-credentials`:
```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
```

**Config entry:**
```json
{ "type": "s3", "bucket": "s3://your-bucket/openclaw-backups", "region": "us-east-1" }
```

---

## Cloudflare R2

R2 is S3-compatible, so it uses the AWS CLI with a custom endpoint.

**CLI needed:** `aws` (AWS CLI)

**Setup:**
1. Create an R2 bucket in your Cloudflare dashboard
2. Go to **Storage & Databases → R2 Object Storage → Overview** → find **Account Details** panel → **API Tokens: Manage** → **Create User Token** (read/write, scoped to bucket)
3. Note the S3 endpoint URL: `https://<account-id>.r2.cloudflarestorage.com`
4. Save credentials to `~/.openclaw/credentials/backup/r2-credentials`:
```bash
export AWS_ACCESS_KEY_ID="your-r2-access-key"
export AWS_SECRET_ACCESS_KEY="your-r2-secret-key"
```

**Config entry:**
```json
{ "type": "r2", "bucket": "your-bucket-name", "accountId": "your-cf-account-id", "endpoint": "https://your-account-id.r2.cloudflarestorage.com" }
```

---

## Backblaze B2

**CLI needed:** `b2`
```bash
pip install b2
```

**Setup:**
1. Create a B2 bucket at backblaze.com
2. Create an application key with write access to the bucket
3. Save credentials to `~/.openclaw/credentials/backup/b2-credentials`:
```bash
export B2_APPLICATION_KEY_ID="your-key-id"
export B2_APPLICATION_KEY="your-key"
```
4. Authorize: `b2 authorize-account $B2_APPLICATION_KEY_ID $B2_APPLICATION_KEY`

**Config entry:**
```json
{ "type": "b2", "bucket": "your-bucket-name" }
```

---

## Google Cloud Storage (GCS)

**CLI needed:** `gsutil` (part of Google Cloud SDK)
```bash
# Debian/Ubuntu:
sudo snap install google-cloud-cli --classic
# or: pip install gsutil
```

**Setup:**
1. Create a GCS bucket in your Google Cloud project
2. Create a service account with Storage Object Admin role
3. Download the JSON key file
4. Save it to `~/.openclaw/credentials/backup/gcs-key.json`

**Config entry:**
```json
{ "type": "gcs", "bucket": "gs://your-bucket/openclaw-backups" }
```

---

## Google Drive

**CLI needed:** `rclone`
```bash
# Install via package manager (recommended):
sudo apt install rclone
# or see https://rclone.org/install/ for other methods
```

**Setup:**
1. Run `rclone config` and set up a Google Drive remote named `gdrive`
2. Follow the OAuth flow to authorize
3. Copy the generated config to `~/.openclaw/credentials/backup/rclone.conf`
   (usually found at `~/.config/rclone/rclone.conf` after setup)

**Config entry:**
```json
{ "type": "gdrive", "folder": "OpenClaw Backups" }
```

---

## Remote Retention & Lifecycle

Local backups are auto-pruned after 30 days (configurable). **Remote backups are never automatically deleted** — this is intentional. Storage is cheap, and offsite backups should be your safety net.

To manage remote retention, set lifecycle rules directly on your storage provider:

- **S3:** Bucket → Management → Lifecycle rules → Expire objects after N days
- **R2:** Bucket → Settings → Object lifecycle rules → Delete after N days
- **B2:** Bucket Settings → Lifecycle Rules → Keep only last N days
- **GCS:** Bucket → Lifecycle → Add rule → Delete object, age > N days
- **Google Drive:** Manual cleanup or use rclone `--min-age` with `rclone delete`

This keeps delete permissions out of your backup credentials — which is best practice. Write-only backup tokens can't accidentally (or maliciously) wipe your backup history.

---

## rsync

**CLI needed:** `rsync` (usually pre-installed on Linux)

**Setup:**
1. Ensure SSH key-based auth is configured to the target host
2. Create the target directory on the remote host

**Config entry:**
```json
{ "type": "rsync", "target": "user@host:/path/to/backups" }
```
