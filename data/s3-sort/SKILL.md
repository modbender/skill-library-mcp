---
name: s3-bulk-upload
description: Upload many files to S3 with automatic organization by first-character prefixes.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - AWS_ACCESS_KEY_ID
        - AWS_SECRET_ACCESS_KEY
      bins:
        - aws
    primaryEnv: AWS_ACCESS_KEY_ID
    emoji: "\U0001F4E6"
    install:
      - kind: brew
        formula: awscli
        bins: [aws]
---

# S3 Bulk Upload

Upload files to S3 with automatic organization using first-character prefixes (e.g., `a/apple.txt`, `b/banana.txt`, `0-9/123.txt`).

## Quick Start

Use the included script for bulk uploads:

```bash
# Basic upload
./s3-bulk-upload.sh ./files my-bucket

# Dry run to preview
./s3-bulk-upload.sh ./files my-bucket --dry-run

# Use sync mode (faster for many files)
./s3-bulk-upload.sh ./files my-bucket --sync

# With storage class
./s3-bulk-upload.sh ./files my-bucket --storage-class STANDARD_IA
```

## Prerequisites

Verify AWS credentials are configured:

```bash
aws sts get-caller-identity
```

If this fails, ensure `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set, or configure via `aws configure`.

## Organization Logic

Files are organized by the first character of their filename:

| First Character | Prefix |
|-----------------|--------|
| `a-z` | Lowercase letter (e.g., `a/`, `b/`) |
| `A-Z` | Lowercase letter (e.g., `a/`, `b/`) |
| `0-9` | `0-9/` |
| Other | `_other/` |

## Single File Upload

Upload a single file with automatic prefix:

```bash
FILE="example.txt"
BUCKET="my-bucket"

# Compute prefix from first character
FIRST_CHAR=$(echo "${FILE}" | cut -c1 | tr '[:upper:]' '[:lower:]')
if [[ "$FIRST_CHAR" =~ [a-z] ]]; then
  PREFIX="$FIRST_CHAR"
elif [[ "$FIRST_CHAR" =~ [0-9] ]]; then
  PREFIX="0-9"
else
  PREFIX="_other"
fi

aws s3 cp "$FILE" "s3://${BUCKET}/${PREFIX}/${FILE}"
```

## Bulk Upload

Upload all files from a directory:

```bash
SOURCE_DIR="./files"
BUCKET="my-bucket"

for FILE in "$SOURCE_DIR"/*; do
  [ -f "$FILE" ] || continue
  BASENAME=$(basename "$FILE")
  FIRST_CHAR=$(echo "$BASENAME" | cut -c1 | tr '[:upper:]' '[:lower:]')

  if [[ "$FIRST_CHAR" =~ [a-z] ]]; then
    PREFIX="$FIRST_CHAR"
  elif [[ "$FIRST_CHAR" =~ [0-9] ]]; then
    PREFIX="0-9"
  else
    PREFIX="_other"
  fi

  aws s3 cp "$FILE" "s3://${BUCKET}/${PREFIX}/${BASENAME}"
done
```

## Efficient Bulk Sync

For large uploads, stage files with symlinks then use `aws s3 sync`:

```bash
SOURCE_DIR="./files"
STAGING_DIR="./staging"
BUCKET="my-bucket"

# Create staging directory with prefix structure
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR"

for FILE in "$SOURCE_DIR"/*; do
  [ -f "$FILE" ] || continue
  BASENAME=$(basename "$FILE")
  FIRST_CHAR=$(echo "$BASENAME" | cut -c1 | tr '[:upper:]' '[:lower:]')

  if [[ "$FIRST_CHAR" =~ [a-z] ]]; then
    PREFIX="$FIRST_CHAR"
  elif [[ "$FIRST_CHAR" =~ [0-9] ]]; then
    PREFIX="0-9"
  else
    PREFIX="_other"
  fi

  mkdir -p "$STAGING_DIR/$PREFIX"
  ln -s "$(realpath "$FILE")" "$STAGING_DIR/$PREFIX/$BASENAME"
done

# Sync entire staging directory to S3
aws s3 sync "$STAGING_DIR" "s3://${BUCKET}/"

# Clean up
rm -rf "$STAGING_DIR"
```

## Verification

List files by prefix:

```bash
BUCKET="my-bucket"
PREFIX="a"

aws s3 ls "s3://${BUCKET}/${PREFIX}/" --recursive
```

Generate a manifest of all uploaded files:

```bash
BUCKET="my-bucket"

aws s3 ls "s3://${BUCKET}/" --recursive | awk '{print $4}'
```

Count files per prefix:

```bash
BUCKET="my-bucket"

for PREFIX in {a..z} 0-9 _other; do
  COUNT=$(aws s3 ls "s3://${BUCKET}/${PREFIX}/" --recursive 2>/dev/null | wc -l | tr -d ' ')
  [ "$COUNT" -gt 0 ] && echo "$PREFIX: $COUNT files"
done
```

## Error Handling

Common issues and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| `AccessDenied` | Insufficient permissions | Check IAM policy has `s3:PutObject` on bucket |
| `NoSuchBucket` | Bucket doesn't exist | Create bucket or check bucket name spelling |
| `InvalidAccessKeyId` | Bad credentials | Verify `AWS_ACCESS_KEY_ID` is correct |
| `ExpiredToken` | Session token expired | Refresh credentials or re-authenticate |

Test bucket access before bulk upload:

```bash
BUCKET="my-bucket"
echo "test" | aws s3 cp - "s3://${BUCKET}/_test_access.txt" && \
  aws s3 rm "s3://${BUCKET}/_test_access.txt" && \
  echo "Bucket access OK"
```

## Storage Classes

Optimize costs with storage classes:

```bash
# Standard (default)
aws s3 cp file.txt s3://bucket/prefix/file.txt

# Infrequent Access (cheaper storage, retrieval fee)
aws s3 cp file.txt s3://bucket/prefix/file.txt --storage-class STANDARD_IA

# Glacier Instant Retrieval (archive with fast access)
aws s3 cp file.txt s3://bucket/prefix/file.txt --storage-class GLACIER_IR

# Intelligent Tiering (auto-optimize based on access patterns)
aws s3 cp file.txt s3://bucket/prefix/file.txt --storage-class INTELLIGENT_TIERING
```

Add `--storage-class` to bulk upload loops for cost optimization on infrequently accessed files.
