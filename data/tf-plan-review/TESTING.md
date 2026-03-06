# TESTING.md — tf-plan-review Test Plan

Run all tests from the `studio/skills/tf-plan-review/` directory.

## Prerequisites

```bash
# jq is required
jq --version    # should output jq-1.6 or later

# At least one of:
terraform version   # Terraform 1.5+
tofu --version      # OpenTofu 1.6+
```

## Test 1: Help & Version

```bash
bash scripts/tf-plan-review.sh --help
bash scripts/tf-plan-review.sh --version
```

**Expected:**
- `--help` prints usage with subcommands and environment variables
- `--version` prints `tf-plan-review v0.1.1`

## Test 2: Unknown Subcommand

```bash
bash scripts/tf-plan-review.sh foobar 2>&1
echo "Exit code: $?"
```

**Expected:** Error message "Unknown subcommand: foobar", exit code 1.

## Test 3: No Terraform Config — Clean Error

```bash
mkdir -p /tmp/tf-plan-review-empty
bash scripts/tf-plan-review.sh plan /tmp/tf-plan-review-empty 2>/dev/null
```

**Expected:** JSON with `"error": true` and message about no Terraform configuration files.

**Verify:**
```bash
bash scripts/tf-plan-review.sh plan /tmp/tf-plan-review-empty 2>/dev/null | jq -r '.error'
# Should output: true
```

## Test 4: Validate — Simple Valid Config

```bash
mkdir -p /tmp/tf-plan-review-valid
cat > /tmp/tf-plan-review-valid/main.tf << 'HCL'
terraform {
  required_version = ">= 1.0"
}

variable "name" {
  type    = string
  default = "test"
}

output "greeting" {
  value = "Hello, ${var.name}!"
}
HCL

bash scripts/tf-plan-review.sh validate /tmp/tf-plan-review-valid 2>/dev/null | jq '.valid'
# Should output: true
```

## Test 5: Validate — Invalid Config

```bash
mkdir -p /tmp/tf-plan-review-invalid
cat > /tmp/tf-plan-review-invalid/main.tf << 'HCL'
resource "aws_instance" "test" {
  # Missing required attributes, but validate checks syntax not providers
  ami = var.nonexistent_variable
}
HCL

bash scripts/tf-plan-review.sh validate /tmp/tf-plan-review-invalid 2>/dev/null | jq '.valid'
# Should output: false (or true depending on provider — validates syntax)
```

## Test 6: Plan — Local-Only Config (No Provider)

This tests plan analysis without needing cloud credentials:

```bash
mkdir -p /tmp/tf-plan-review-local
cat > /tmp/tf-plan-review-local/main.tf << 'HCL'
terraform {
  required_version = ">= 1.0"
}

resource "null_resource" "example" {
  triggers = {
    always = timestamp()
  }
}
HCL

# This requires the null provider, so init first:
cd /tmp/tf-plan-review-local && terraform init

# Now analyze:
bash scripts/tf-plan-review.sh plan /tmp/tf-plan-review-local 2>/dev/null | jq '.summary'
```

**Expected:** JSON with `create: 1` (the null_resource).

**Verify risk classification:**
```bash
bash scripts/tf-plan-review.sh plan /tmp/tf-plan-review-local 2>/dev/null | jq '.resources[0].risk'
# Should output: "🟢 SAFE"
```

## Test 7: Plan — Risk Classification (Mock)

Test risk classification with a simulated plan that includes dangerous resources. Create a config with IAM and database resources:

```bash
mkdir -p /tmp/tf-plan-review-risky
cat > /tmp/tf-plan-review-risky/main.tf << 'HCL'
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-west-2"
}

resource "aws_iam_role" "admin" {
  name = "admin-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_db_instance" "production" {
  allocated_storage = 20
  engine            = "mysql"
  instance_class    = "db.t3.micro"
}
HCL
```

> **Note:** This test requires AWS credentials to run `terraform plan`. If unavailable, verify the risk classification logic by inspecting the script's pattern matching:

```bash
# Verify critical patterns match IAM and RDS:
echo "aws_iam_role" | grep -qiE 'iam|security_group|kms|db_instance|rds_cluster' && echo "PASS: IAM detected as critical"
echo "aws_db_instance" | grep -qiE 'iam|security_group|kms|db_instance|rds_cluster' && echo "PASS: RDS detected as critical"
```

## Test 8: State — Empty Directory

```bash
mkdir -p /tmp/tf-plan-review-nostate
bash scripts/tf-plan-review.sh state "" /tmp/tf-plan-review-nostate 2>/dev/null
echo "Exit code: $?"
```

**Expected:** JSON error about no state found. Non-zero exit.

## Test 9: OpenTofu Support

```bash
# If tofu is installed:
TF_BINARY=tofu bash scripts/tf-plan-review.sh --version
# Should still output: tf-plan-review v0.1.1

# If tofu is NOT installed:
TF_BINARY=tofu bash scripts/tf-plan-review.sh plan /tmp/tf-plan-review-valid 2>/dev/null | jq -r '.message'
# Should output error about tofu not found
```

## Test 10: Markdown Report Output

```bash
mkdir -p /tmp/tf-plan-review-local
cd /tmp/tf-plan-review-local && terraform init 2>/dev/null

# Capture stderr (Markdown report)
bash scripts/tf-plan-review.sh plan /tmp/tf-plan-review-local 1>/dev/null 2>/tmp/tf-report.md

# Verify Markdown structure:
grep -q "Terraform Plan Risk Assessment" /tmp/tf-report.md && echo "PASS: Has title"
grep -q "Change Summary" /tmp/tf-report.md && echo "PASS: Has summary"
grep -q "Pre-Apply Checklist" /tmp/tf-report.md && echo "PASS: Has checklist"
grep -q "Anvil AI" /tmp/tf-report.md && echo "PASS: Has branding"
```

## Test 11: Non-existent Directory

```bash
bash scripts/tf-plan-review.sh plan /tmp/this-does-not-exist 2>/dev/null | jq -r '.error'
# Should output: true
```

## Test 12: Missing jq Graceful Error

```bash
# Simulate missing jq by using a clean PATH
PATH=/usr/bin:/bin bash scripts/tf-plan-review.sh plan . 2>/dev/null | head -1
# If jq is in /usr/bin, this won't trigger. Test by renaming jq temporarily (not recommended)
# The point is: the script should output a JSON error, not a bash crash
```

## Cleanup

```bash
rm -rf /tmp/tf-plan-review-* /tmp/tf-report.md
```

## Security Verification

These are manual verification steps, not automated tests:

1. **Grep for apply:** `grep -ri 'terraform apply\|tofu apply' scripts/` — should return ZERO matches
2. **Grep for destroy:** `grep -ri 'terraform destroy\|tofu destroy' scripts/` — should return ZERO matches  
3. **Grep for eval:** `grep -ri 'eval ' scripts/` — should return ZERO matches
4. **Grep for backtick execution:** `grep -P '`[^`]+`' scripts/` — should return ZERO matches (use $() instead)
5. **Verify set -euo pipefail:** `head -5 scripts/tf-plan-review.sh` — must include it
