# Secret Patterns Reference

Regex patterns for grep-based secret detection. Supplements TruffleHog for quick scans.

**Legend:** ✅ scanned (high-confidence) | ⚡ scanned (low-confidence) | 📖 reference only (TruffleHog or manual check)

## AWS

| Pattern | Regex | Status |
|---------|-------|--------|
| AWS Access Key ID | `AKIA[0-9A-Z]{16}` | ✅ scanned |
| AWS Secret Access Key | `(?i)aws_secret_access_key\s*[=:]\s*[A-Za-z0-9/+=]{40}` | 📖 reference only |
| AWS Secret Key (near AKIA) | `AKIA[0-9A-Z]{16}[^A-Za-z0-9][A-Za-z0-9/+=]{40}` | ⚡ low-confidence |

## GitHub

| Pattern | Regex | Status |
|---------|-------|--------|
| GitHub PAT (classic) | `ghp_[A-Za-z0-9]{36}` | ✅ scanned |
| GitHub PAT (fine-grained) | `github_pat_[A-Za-z0-9_]{82}` | ✅ scanned |
| GitHub OAuth | `gho_[A-Za-z0-9]{36}` | ✅ scanned |
| GitHub App Token | `ghu_[A-Za-z0-9]{36}` | ✅ scanned |
| GitHub App Install | `ghs_[A-Za-z0-9]{36}` | ✅ scanned |
| GitHub App Refresh | `ghr_[A-Za-z0-9]{36}` | ✅ scanned |

## Anthropic

| Pattern | Regex | Status |
|---------|-------|--------|
| Anthropic API Key | `sk-ant-[A-Za-z0-9_-]{20,}` | ✅ scanned |

## Slack

| Pattern | Regex | Status |
|---------|-------|--------|
| Slack Bot Token | `xoxb-[0-9]{10,}-[0-9]{10,}-[A-Za-z0-9]{24}` | ✅ scanned |
| Slack User Token | `xoxp-[0-9]{10,}-[0-9]{10,}-[0-9]{10,}-[a-f0-9]{32}` | ✅ scanned |
| Slack Webhook | `https://hooks\.slack\.com/services/T[A-Z0-9]{8,}` | ✅ scanned |

## OpenAI

| Pattern | Regex | Status |
|---------|-------|--------|
| OpenAI API Key | `sk-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20}` | 📖 reference only |
| OpenAI Project Key | `sk-proj-[A-Za-z0-9_-]{80,}` | ✅ scanned |

## Stripe

| Pattern | Regex | Status |
|---------|-------|--------|
| Stripe Secret Key | `sk_live_[A-Za-z0-9]{24,}` | ✅ scanned |
| Stripe Publishable | `pk_live_[A-Za-z0-9]{24,}` | ✅ scanned |
| Stripe Restricted | `rk_live_[A-Za-z0-9]{24,}` | ✅ scanned |

## Google

| Pattern | Regex | Status |
|---------|-------|--------|
| Google API Key | `AIza[0-9A-Za-z_-]{35}` | ✅ scanned |
| Google OAuth Secret | `GOCSPX-[A-Za-z0-9_-]{28}` | ✅ scanned |

## Twilio

| Pattern | Regex | Status |
|---------|-------|--------|
| Twilio API Key | `SK[a-f0-9]{32}` | ✅ scanned |

## SendGrid

| Pattern | Regex | Status |
|---------|-------|--------|
| SendGrid API Key | `SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}` | ✅ scanned |

## npm

| Pattern | Regex | Status |
|---------|-------|--------|
| npm Token | `npm_[A-Za-z0-9]{36}` | ✅ scanned |

## Telegram

| Pattern | Regex | Status |
|---------|-------|--------|
| Telegram Bot Token | `[0-9]{8,10}:[A-Za-z0-9_-]{35}` | 📖 reference only (moved from active scan — too many false positives without `bot` prefix context) |

## HashiCorp

| Pattern | Regex | Status |
|---------|-------|--------|
| Vault Token | `hvs\.[A-Za-z0-9_-]{24,}` | ✅ scanned |

## Database URLs

| Pattern | Regex | Status |
|---------|-------|--------|
| MongoDB Connection | `mongodb://[^ ]{10,}` | ⚡ low-confidence |
| PostgreSQL Connection | `postgres(ql)?://[^ ]{10,}` | ⚡ low-confidence |
| MySQL Connection | `mysql://[^ ]{10,}` | ⚡ low-confidence |
| Redis Connection | `redis://[^ ]{10,}` | ⚡ low-confidence |

## Firebase / Supabase

| Pattern | Regex | Status |
|---------|-------|--------|
| Firebase Config | `FIREBASE_[A-Z_]*=.{10,}` | ⚡ low-confidence |
| Supabase Key | `sbp_[A-Za-z0-9]{40,}` | ⚡ low-confidence |

## Generic

| Pattern | Regex | Status |
|---------|-------|--------|
| Private Key Header | `-----BEGIN (RSA \|EC \|DSA \|OPENSSH )?PRIVATE KEY-----` | ✅ scanned |
| Generic Secret Assignment | `(?i)(password\|secret\|token\|api_key\|apikey\|auth)\s*[=:]\s*['"][A-Za-z0-9+/=_-]{8,}['"]` | 📖 reference only |
| Password/Secret Assignment | `(password\|passwd\|secret)\s*[=:]\s*['"][^\s'"]{8,}['"]` | ⚡ low-confidence |
| Bearer Token | `[Bb]earer\s+[A-Za-z0-9_.~+/-]{20,}` | ⚡ low-confidence |
| JWT Token | `eyJhbGciOi[A-Za-z0-9_-]{20,}` | ⚡ low-confidence |
| Basic Auth | `(?i)basic\s+[A-Za-z0-9+/=]{20,}` | 📖 reference only |

## Environment Variables (Shell Profiles)

| Pattern | Regex | Status |
|---------|-------|--------|
| Hardcoded API Key | `export\s+\w*KEY\s*=\s*['"]?[A-Za-z0-9_-]+` | 📖 reference only (env audit) |
| Hardcoded Token | `export\s+\w*TOKEN\s*=\s*['"]?[A-Za-z0-9_-]+` | 📖 reference only (env audit) |
| Hardcoded Secret | `export\s+\w*SECRET\s*=\s*['"]?[A-Za-z0-9_-]+` | 📖 reference only (env audit) |
| Hardcoded Password | `export\s+\w*PASSWORD\s*=\s*['"]?[A-Za-z0-9_-]+` | 📖 reference only (env audit) |

Files to check: `~/.bashrc`, `~/.zshrc`, `~/.bash_profile`, `~/.profile`

## Docker

| Pattern | Regex | Status |
|---------|-------|--------|
| Dockerfile ENV Secret | `ENV\s+\w*(SECRET\|KEY\|TOKEN\|PASSWORD)\s*=` | 📖 reference only (docker audit) |
| Compose Hardcoded Secret | `(SECRET\|KEY\|TOKEN\|PASSWORD)\s*:\s*[^${]` (not a variable ref) | 📖 reference only (docker audit) |

Files to check: `Dockerfile*`, `docker-compose*.yml`, `docker-compose*.yaml`
