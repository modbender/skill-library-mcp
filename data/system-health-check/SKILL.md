---
name: system-health-check
description: System health validator — checks skill files, paths, permissions, binaries, backup freshness, and encryption. Produces pass/fail reports.
version: 1.0.0
author: openclaw-greek-accounting
homepage: https://github.com/satoshistackalotto/openclaw-greek-accounting
tags: ["greek", "accounting", "health-check", "monitoring", "diagnostics"]
metadata: {"openclaw": {"requires": {"bins": ["jq", "openssl", "openclaw"], "env": ["OPENCLAW_DATA_DIR"]}, "notes": "Read-only validation skill. Checks file presence, directory structure, permissions, and backup freshness. Never modifies any data. openssl is used only for hash verification.", "path_prefix": "/data/ in examples refers to $OPENCLAW_DATA_DIR (default: /data/)"}}
---

# System Health Check

This skill validates the entire OpenClaw Greek Accounting system in a single command. It checks skill file integrity, directory structure, file permissions, required dependencies, backup freshness, encryption status, and process lock health. Designed to run daily via cron or manually before critical operations.


## Setup

```bash
export OPENCLAW_DATA_DIR="/data"
which jq openssl || sudo apt install jq openssl
```

Read-only validation skill. Checks file presence, directory structure, permissions, and backup freshness. Never modifies any data.


## Core Philosophy

- **Fast & Non-Destructive**: Read-only checks — never modifies any data
- **Comprehensive**: Covers every layer from skill files to encryption status
- **Actionable Output**: Every failure includes a specific remediation command
- **Cron-Friendly**: Exit code 0 for all-pass, exit code 1 for any failure
- **English Output**: Plain English report suitable for accounting assistants and system admins

## OpenClaw Commands

### Full Health Check
```bash
# Run all checks
openclaw health-check --all

# Run all checks with verbose output
openclaw health-check --all --verbose

# Run all checks and write report to /data/reports/system/
openclaw health-check --all --save-report
```

### Individual Check Categories
```bash
# Check skill files only
openclaw health-check --skills

# Check directory structure against canonical data map
openclaw health-check --directories

# Check file permissions on sensitive directories
openclaw health-check --permissions

# Check required binaries and dependencies
openclaw health-check --dependencies

# Check backup freshness and integrity
openclaw health-check --backups

# Check for stale process locks
openclaw health-check --locks

# Check encryption status on sensitive directories
openclaw health-check --encryption

# Check data integrity hashes
openclaw health-check --integrity
```

### Scheduled Checks
```bash
# Quick check — skills + directories + locks (for hourly cron)
openclaw health-check --quick

# Standard check — everything except full integrity hash verification (for daily cron)
openclaw health-check --standard

# Deep check — all checks including full hash verification (for weekly cron)
openclaw health-check --deep
```

## Check Specifications

### 1. Skill File Validation

Verifies all 19 operational skills and the canonical data map are present and well-formed.

```yaml
Skill_File_Checks:
  presence:
    description: "Every skill folder contains a SKILL.md file"
    expected_count: 20
    check: "ls skills/*/SKILL.md"
    
  frontmatter:
    description: "Every SKILL.md has valid YAML frontmatter with required fields"
    required_fields: ["name", "description", "version", "author", "tags", "metadata"]
    check: "Parse frontmatter block between --- delimiters"
    
  evals:
    description: "Every operational skill has an EVALS.json file"
    expected_count: 19
    excluded: ["canonical-data-map"]
    check: "ls skills/*/EVALS.json, validate JSON syntax"
    
  evals_content:
    description: "Each EVALS.json contains at least 5 test cases"
    minimum_cases: 5
    check: "Parse JSON, count array length"

  skill_inventory:
    - "canonical-data-map"
    - "accounting-workflows"
    - "greek-compliance-aade"
    - "cli-deadline-monitor"
    - "greek-email-processor"
    - "greek-individual-taxes"
    - "openclaw-greek-accounting-meta"
    - "aade-api-monitor"
    - "greek-banking-integration"
    - "greek-document-ocr"
    - "efka-api-integration"
    - "dashboard-greek-accounting"
    - "client-data-management"
    - "user-authentication-system"
    - "conversational-ai-assistant"
    - "greek-financial-statements"
    - "client-communication-engine"
    - "system-integrity-and-backup"
    - "analytics-and-advisory-intelligence"
    - "memory-feedback"
```

### 2. Directory Structure Validation

Checks all canonical directories exist under `/data/` as specified in the canonical data map (Skill 00).

```yaml
Directory_Checks:
  top_level:
    required:
      - "/data/incoming/"
      - "/data/processing/"
      - "/data/clients/"
      - "/data/compliance/"
      - "/data/banking/"
      - "/data/ocr/"
      - "/data/efka/"
      - "/data/reports/"
      - "/data/exports/"
      - "/data/imports/"
      - "/data/dashboard/"
      - "/data/auth/"
      - "/data/backups/"
      - "/data/gdpr-exports/"
      - "/data/memory/"
      - "/data/system/"

  subdirectories:
    incoming:
      - "/data/incoming/invoices/"
      - "/data/incoming/receipts/"
      - "/data/incoming/statements/"
      - "/data/incoming/government/"
      - "/data/incoming/payroll/"
      - "/data/incoming/tax-documents/"
      - "/data/incoming/contracts/"
      - "/data/incoming/other/"
    processing:
      - "/data/processing/ocr/"
      - "/data/processing/classification/"
      - "/data/processing/reconciliation/"
      - "/data/processing/compliance/"
    system:
      - "/data/system/logs/"
      - "/data/system/logs/audit/"
      - "/data/system/process-locks/"
      - "/data/system/integrity/"

  unexpected_directories:
    description: "Flag any top-level directory under /data/ not in the canonical map"
    action: "WARN — may indicate a skill creating non-canonical paths"
```

### 3. File Permission Checks

Validates OS-level file permissions on sensitive directories.

```yaml
Permission_Checks:
  restricted_directories:
    - path: "/data/auth/"
      expected_mode: "700"
      description: "Auth directory must be restricted to service user"
    - path: "/data/auth/users/*/credentials.json"
      expected_mode: "600"
      description: "Credential files must not be world-readable"
      
  sensitive_directories:
    - path: "/data/clients/"
      expected_mode: "700"
      description: "Client data directory should be restricted"
    - path: "/data/backups/"
      expected_mode: "700"
      description: "Backup directory should be restricted"
      
  note: "Permission checks may report SKIP on systems where the OpenClaw agent runs as root or in a container without OS-level permission enforcement."
```

### 4. Dependency Checks

Verifies required binaries and environment variables are available.

```yaml
Dependency_Checks:
  required_binaries:
    - name: "jq"
      check: "which jq"
      used_by: "All skills — JSON processing"
    - name: "curl"
      check: "which curl"
      used_by: "AADE monitor, email processor, EFKA, memory-feedback"
    - name: "openssl"
      check: "which openssl"
      used_by: "System integrity, backup encryption"

  required_env_vars:
    - name: "OPENCLAW_DATA_DIR"
      description: "Root data directory path"
      default: "/data/"
      
  optional_env_vars:
    - name: "OPENCLAW_ENCRYPTION_KEY"
      description: "Master encryption key for data-at-rest"
      warn_if_missing: true
    - name: "GITHUB_TOKEN"
      description: "GitHub PAT for memory-feedback PR workflow"
      warn_if_missing: true
    - name: "SMTP_HOST"
      description: "Mail server for client communications"
      warn_if_missing: true
```

### 5. Backup Freshness

Checks that backups are current per the schedule defined in Skill 17.

```yaml
Backup_Checks:
  weekly_full:
    description: "Full backup should exist from within the last 7 days"
    location: "/data/backups/"
    pattern: "full_*.tar.enc"
    max_age_days: 7
    severity: "HIGH if missing"
    
  daily_incremental:
    description: "Incremental backup should exist from within the last 24 hours"
    location: "/data/backups/"
    pattern: "incremental_*.tar.enc"
    max_age_hours: 26
    severity: "MEDIUM if missing (allows 2-hour grace period)"
    
  verification:
    description: "Last backup verification should be within 7 days"
    check: "Look for verification report in /data/reports/system/"
    severity: "MEDIUM if stale"
```

### 6. Process Lock Health

Detects stale process locks that may indicate crashed operations.

```yaml
Lock_Checks:
  location: "/data/system/process-locks/"
  stale_threshold_minutes: 30
  check_method:
    - "List all .lock files"
    - "Read timestamp from each lock file"
    - "Flag locks older than threshold"
    - "Check if process ID in lock file is still running"
  actions:
    stale_found: "WARN — list stale locks with age and owning process"
    suggestion: "Run: openclaw integrity clear-stale-locks --confirm"
    active_found: "INFO — list active locks (normal operation)"
```

### 7. Encryption Status

Verifies encryption configuration on directories that require it per the canonical data map.

```yaml
Encryption_Checks:
  mandatory_encrypted:
    - "/data/auth/"
    - "/data/clients/"
    - "/data/compliance/"
    - "/data/efka/"
    - "/data/gdpr-exports/"
  check_methods:
    luks: "Check if volume is LUKS-encrypted via lsblk or cryptsetup status"
    fscrypt: "Check fscrypt policy on directory"
    env_key: "Verify OPENCLAW_ENCRYPTION_KEY environment variable is set"
  note: "In development/testing environments, encryption may not be configured. Report as WARN, not FAIL."
```

### 8. Data Integrity

Validates file hashes against the integrity registry maintained by Skill 17.

```yaml
Integrity_Checks:
  registry_location: "/data/system/integrity/"
  check_method:
    - "Read hash registry for canonical files"
    - "Recompute SHA-256 hashes for each file"
    - "Compare against stored hashes"
    - "Flag any mismatches"
  scope:
    quick: "Check 10% random sample of files"
    standard: "Check all files modified in last 7 days"
    deep: "Check all files in registry"
  severity:
    mismatch: "HIGH — file has been modified outside normal skill operations"
    missing_from_registry: "MEDIUM — file exists but has no hash recorded"
    missing_file: "HIGH — registry references a file that no longer exists"
```

## Output Format

### Console Output

```
╔══════════════════════════════════════════════════╗
║   OpenClaw Greek Accounting — Health Report      ║
╠══════════════════════════════════════════════════╣
║ Run: 2026-02-19 15:30:00 (Europe/Athens)         ║
║ Mode: standard                                   ║
╚══════════════════════════════════════════════════╝

  SKILLS
  ✅ 20/20 SKILL.md files present
  ✅ 20/20 frontmatter valid
  ✅ 19/19 EVALS.json present
  ✅ All EVALS have 5+ test cases

  DIRECTORIES
  ✅ 16/16 top-level directories present
  ✅ No unexpected top-level directories
  ⚠️  2 subdirectories missing (see details)

  PERMISSIONS
  ✅ /data/auth/ — mode 700
  ❌ /data/clients/ — mode 755 (expected 700)

  DEPENDENCIES
  ✅ jq installed (v1.7.1)
  ✅ curl installed (v8.5.0)
  ✅ openssl installed (v3.0.13)
  ⚠️  OPENCLAW_ENCRYPTION_KEY not set

  BACKUPS
  ✅ Full backup: 2026-02-16 02:00 (3 days ago)
  ✅ Incremental: 2026-02-19 03:00 (12 hours ago)
  ⚠️  Last verification: 2026-02-10 (9 days ago)

  LOCKS
  ✅ No stale process locks

  ENCRYPTION
  ⚠️  Encryption not detected on /data/clients/
  ⚠️  OPENCLAW_ENCRYPTION_KEY not set

  INTEGRITY
  ✅ 847/847 files match stored hashes

═══════════════════════════════════════════════════
  RESULT: 1 FAIL, 4 WARN — review required
  Details: openclaw health-check --all --verbose
═══════════════════════════════════════════════════
```

### JSON Report

Written to `/data/reports/system/health-check_{YYYYMMDD}_{HHMMSS}.json`:

```json
{
  "timestamp": "2026-02-19T15:30:00Z",
  "mode": "standard",
  "result": "WARN",
  "summary": {
    "pass": 18,
    "fail": 1,
    "warn": 4,
    "skip": 0
  },
  "checks": [
    {
      "category": "skills",
      "check": "skill_files_present",
      "result": "PASS",
      "details": "20/20 SKILL.md files present"
    },
    {
      "category": "permissions",
      "check": "clients_directory_mode",
      "result": "FAIL",
      "expected": "700",
      "actual": "755",
      "remediation": "chmod 700 /data/clients/"
    }
  ]
}
```

## Cron Configuration

```json
{
  "cron": {
    "health-quick": {
      "schedule": "0 */4 * * *",
      "command": "openclaw health-check --quick --save-report",
      "description": "Quick check every 4 hours"
    },
    "health-standard": {
      "schedule": "0 7 * * *",
      "command": "openclaw health-check --standard --save-report",
      "description": "Standard check every morning at 07:00 Athens"
    },
    "health-deep": {
      "schedule": "0 3 * * 0",
      "command": "openclaw health-check --deep --save-report",
      "description": "Deep check every Sunday at 03:00 Athens"
    }
  }
}
```

## Integration with Other Skills

### Dashboard Integration
```bash
# Health check status feeds into the dashboard system health panel
openclaw dashboard refresh --state system-health
# Dashboard shows: last check time, result, and count of issues
```

### Memory Integration
```bash
# Failed health checks are logged as system failures for pattern detection
# Written to /data/memory/failures/ with failure_type: health_check_failed
```

### Meta-Skill Integration
```bash
# Health check runs automatically before major operations
openclaw greek monthly-process --pre-flight-check
# Equivalent to: openclaw health-check --quick && openclaw greek monthly-process
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed (may include WARN) |
| 1 | One or more FAIL results |
| 2 | Health check itself failed to run (dependency missing, permission error) |
