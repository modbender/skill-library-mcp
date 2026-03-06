# MinIO

## Create bucket

1. MinIO Console → **Buckets** → **Create Bucket**
2. Set access to **Private**

## Credentials

1. MinIO Console → **Access Keys** → **Create Access Key**
2. Optionally attach a policy restricting to one bucket:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::YOUR_BUCKET"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::YOUR_BUCKET/*"
    }
  ]
}
```

## Configure

```bash
openclaw config patch 'skills.entries.cloud-backup.config.bucket="my-backup-bucket"'
openclaw config patch 'skills.entries.cloud-backup.config.region="us-east-1"'
openclaw config patch 'skills.entries.cloud-backup.config.endpoint="https://minio.example.com"'
openclaw config patch 'skills.entries.cloud-backup.env.ACCESS_KEY_ID="<access_key>"'
openclaw config patch 'skills.entries.cloud-backup.env.SECRET_ACCESS_KEY="<secret_key>"'
```

## Notes

- Region can be anything — MinIO doesn't enforce it, but `us-east-1` is conventional.
- For self-signed TLS, set `AWS_CA_BUNDLE=/path/to/ca.pem` in the environment.
- If MinIO runs on a non-standard port, include it in the endpoint: `https://minio.local:9000`.
- Default admin credentials (`minioadmin`/`minioadmin`) should never be used for backups — create a dedicated access key.
