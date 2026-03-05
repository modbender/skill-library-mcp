# Cloudflare R2 CLI Skill

## Skill Metadata

```yaml
name: "r2-cli"
description: "A minimal CLI tool for interacting with Cloudflare R2 storage using Python. Supports upload, download, list, and delete operations via S3-compatible API with AWS Signature V4."
version: "1.0.6"
author:
  username: "@zororaka00"
  name: "Web3 Hungry"
  x_account: "https://x.com/web3hungry"
category: "storage"
tags: ["cloudflare", "python", "r2", "storage"]
source: "r2.py"
credentials:
  required: true
  type: "environment"
  variables:
    - CF_R2_ACCOUNT_ID
    - CF_R2_ACCESS_KEY_ID
    - CF_R2_SECRET_ACCESS_KEY
    - CF_R2_BUCKET
    - CF_R2_REGION
runtime:
  language: "python"
  version: "3.11+"
  dependencies:
    - "defusedxml>=0.7.1"
  env:
    - name: "CF_R2_ACCOUNT_ID"
      required: true
      description: "Cloudflare account ID"
    - name: "CF_R2_ACCESS_KEY_ID"
      required: true
      description: "R2 access key ID"
    - name: "CF_R2_SECRET_ACCESS_KEY"
      required: true
      description: "R2 secret access key"
    - name: "CF_R2_BUCKET"
      required: true
      description: "R2 bucket name"
    - name: "CF_R2_REGION"
      required: false
      description: "Region (default: auto)"

required_env_vars:
  - CF_R2_ACCOUNT_ID
  - CF_R2_ACCESS_KEY_ID
  - CF_R2_SECRET_ACCESS_KEY
  - CF_R2_BUCKET
  - CF_R2_REGION
primaryEnv: CF_R2_ACCESS_KEY_ID
primarySecretEnv: CF_R2_SECRET_ACCESS_KEY
```

## Overview

This skill provides a minimal CLI tool for interacting with Cloudflare R2 storage using Python.
The script (`r2.py`) implements upload, download, list, and delete operations via the Cloudflare R2 S3-compatible API.

It is designed for secure usage in restricted environments with minimal dependencies while following modern security best practices.

## Dependencies

* Python **3.11+**
* Requires: `defusedxml` (for secure XML parsing)

> The tool primarily uses the Python standard library. Only `defusedxml` is required to harden XML parsing against known attacks.

## Installation

No package installation is required for the CLI itself.

If `defusedxml` is not already available:

```bash
pip install defusedxml
```

## Features

* Upload objects to a bucket
* Download objects from a bucket
* List objects in a bucket
* Delete objects from a bucket
* AWS Signature V4 compatible authentication (HMAC SHA256)
* Secure credential handling via environment variables
* Hardened HTTP client with HTTPS-only enforcement
* Safe XML parsing using defused XML protections

## Prerequisites

* Python **3.11+**
* Cloudflare account with R2 enabled
* Bucket created in Cloudflare R2
* API keys with appropriate permissions (least privilege)
* Bucket name must be DNS-compliant (lowercase letters, numbers, hyphens, 3–63 characters, no underscores)

## Environment Variables

| Variable                  | Description              | Example                                |
| ------------------------- | ------------------------ | -------------------------------------- |
| `CF_R2_ACCOUNT_ID`        | Cloudflare account ID    | `123e4567-e89b-12d3-a456-426614174000` |
| `CF_R2_ACCESS_KEY_ID`     | R2 access key ID         | `AKIAxxxxxxxxxxxx`                     |
| `CF_R2_SECRET_ACCESS_KEY` | R2 secret key            | `xxxxxxxxxxxxxxxxxxxxxxxx`             |
| `CF_R2_BUCKET`            | Bucket name              | `my-r2-bucket`                         |
| `CF_R2_REGION`            | Region (default: `auto`) | `auto`                                 |

`CF_R2_REGION` behavior:

* `auto` (default): automatically selects the appropriate region for Cloudflare R2.
* Custom value: you may specify a region string if required by your environment (for example `us-east-1` for compatibility scenarios).

## Environment Setup

This tool reads credentials directly from operating system environment variables.
Set the variables globally before running the CLI.

### Linux / macOS (bash / zsh)

```bash
export CF_R2_ACCOUNT_ID="your_account_id"
export CF_R2_ACCESS_KEY_ID="your_access_key"
export CF_R2_SECRET_ACCESS_KEY="your_secret_key"
export CF_R2_BUCKET="your_bucket_name"
export CF_R2_REGION="auto"
```

**Security Note:** These credentials should only be set temporarily in the current session. For production environments, use secure secret management solutions.

### Windows (PowerShell)

```powershell
$env:CF_R2_ACCOUNT_ID="your_account_id"
$env:CF_R2_ACCESS_KEY_ID="your_access_key"
$env:CF_R2_SECRET_ACCESS_KEY="your_secret_key"
$env:CF_R2_BUCKET="your_bucket_name"
$env:CF_R2_REGION="auto"
```

**Security Note:** These credentials should only be set temporarily in the current session. For production environments, use secure secret management solutions.

### Recommended Secure Credential Management

For production environments, consider using:
- **Cloudflare Workers Secrets** (for Cloudflare environments)
- **AWS Secrets Manager** (if using AWS)
- **HashiCorp Vault** (enterprise secret management)
- **Docker Secrets** (for containerized deployments)
- **Kubernetes Secrets** (for Kubernetes environments)
- **OS-level keyring** (e.g., `keyring` Python package)

### Verify Environment

```bash
echo $CF_R2_ACCOUNT_ID
```

If a value prints, the environment is configured correctly.

> **Important:** Never commit credentials to version control. Use environment variables provided by your operating system or a secure secret management solution.

## Usage

```bash
# Upload a file
python r2.py upload --file local_file.txt --key remote_file.txt

# Download a file
python r2.py download --key remote_file.txt --file local_file.txt

# List objects
python r2.py list

# Delete an object
python r2.py delete --key remote_file.txt
```

## Security Best Practices

* Never commit credentials to version control.
* Use environment variables managed by your operating system, container runtime, or secret manager.
* Apply least-privilege access when creating API keys.
* Rotate keys regularly and revoke compromised keys.
* All credentials are loaded at runtime from environment variables.
* HTTPS is strictly enforced and hostnames are validated to prevent unexpected network access.
* XML responses are parsed using the **defusedxml** library to prevent XXE and entity expansion attacks.
* Errors are handled without exposing sensitive information such as credentials or secrets.

## Credential Security

Never store credentials inside source code or configuration files committed to version control.
Use environment variables provided by your operating system or a secure secret management solution.

## Future Improvements

* Multipart uploads for large objects
* Retry with exponential backoff
* Progress indicators
* Bucket management commands
* Streaming upload/download to reduce memory usage
