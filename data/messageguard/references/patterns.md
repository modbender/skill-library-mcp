# Built-in Pattern Library

All patterns below are active by default. Override or disable any by adding an entry with the same `name` in your config's `patterns` list.

## Quick Reference

| Name | Default Action | Detects |
|------|---------------|---------|
| `private_key_block` | **block** | PEM private key headers |
| `aws_access_key` | **block** | AWS AKIA… access key IDs |
| `aws_secret_key` | **block** | AWS secret access keys in assignment form |
| `jwt_token` | **block** | JSON Web Tokens (eyJ…) |
| `github_token` | **block** | GitHub personal/OAuth/app tokens |
| `slack_token` | **block** | Slack xox* tokens |
| `stripe_key` | **block** | Stripe sk_live/sk_test keys |
| `openai_key` | **block** | OpenAI sk-… keys |
| `anthropic_key` | **block** | Anthropic sk-ant-… keys |
| `google_api_key` | **block** | Google AIza… keys |
| `sendgrid_key` | **block** | SendGrid SG.… keys |
| `twilio_token` | **block** | Twilio SK… tokens |
| `ssh_connection_with_password` | **block** | sshpass -p <password> |
| `ssn_us` | **block** | US Social Security Numbers (###-##-####) |
| `generic_api_key` | mask | api_key / api_secret / client_secret assignments |
| `bearer_token` | mask | HTTP Bearer token values |
| `password_assignment` | mask | password= / passwd= assignments |
| `database_url` | mask | Password field in DB connection strings |
| `credit_card` | mask | Visa / MC / Amex / Discover card numbers |
| `env_file_line` | mask | .env-style KEY=longvalue lines |
| `private_ip_range` | warn | RFC1918 private IP addresses |

---

## Pattern Details

### `private_key_block`
Matches PEM private key delimiters (`-----BEGIN PRIVATE KEY-----`, RSA, EC, OPENSSH, etc.).
Action: **block** — A message containing a PEM key fragment should never be transmitted.

### `aws_access_key`
Matches the literal `AKIA` + 16 uppercase alphanumeric chars (AWS IAM key ID format).
Action: **block**

### `aws_secret_key`
Matches `aws_secret_key` / `aws_secret_access_key` in assignment form followed by a 40-char base64 value.
Uses `capture_group: 1` to target the value only.
Action: **block**

### `jwt_token`
Matches three base64url segments separated by dots, starting with `eyJ`.
Action: **block** — JWTs typically contain authentication claims.

### `generic_api_key`
Matches `api_key`, `apikey`, `api_secret`, `app_secret`, `client_secret` followed by a value ≥20 chars.
Uses `capture_group: 1` so the key name is preserved; only the value is masked.
Action: **mask**

### `bearer_token`
Matches `Bearer <token>` in HTTP Authorization headers or log output.
Uses `capture_group: 1` to mask the token value only.
Action: **mask**

### `password_assignment`
Matches `password=`, `passwd=`, `pass=`, `pwd=` followed by a non-whitespace value ≥6 chars.
Uses `capture_group: 1`.
Action: **mask**

### `database_url`
Matches the password field in connection strings: `protocol://user:PASSWORD@host`.
Uses `capture_group: 1` to mask only the password segment.
Action: **mask**

### `github_token`
Matches `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_` followed by 36+ chars.
Action: **block**

### `slack_token`
Matches Slack OAuth tokens (`xoxb-`, `xoxa-`, `xoxp-`, `xoxr-`, `xoxs-`).
Action: **block**

### `stripe_key`
Matches `sk_live_` or `sk_test_` Stripe secret keys.
Action: **block**

### `openai_key`
Matches `sk-` followed by ≥20 alphanumeric chars (OpenAI API key format).
Action: **block**

### `anthropic_key`
Matches `sk-ant-` followed by 40+ chars.
Action: **block**

### `google_api_key`
Matches `AIza` followed by 35 alphanumeric chars.
Action: **block**

### `sendgrid_key`
Matches SendGrid's `SG.<22 chars>.<43 chars>` format.
Action: **block**

### `twilio_token`
Matches Twilio SK + 32 hex chars.
Action: **block**

### `ssh_connection_with_password`
Matches `sshpass -p <value>` shell commands, capturing the inline password.
Action: **block**

### `credit_card`
Matches major card network numbers (Visa 16-digit, MC, Amex, Discover) by structural pattern.
Action: **mask**
Note: Uses Luhn-agnostic structural regex; may produce occasional false positives on random 16-digit numbers.

### `ssn_us`
Matches US SSN format `###-##-####`.
Action: **block** — PII; should never appear in chat.

### `env_file_line`
Matches lines in `.env` format: `UPPER_KEY=longvalue` (value ≥8 chars).
Action: **mask**

### `private_ip_range`
Matches RFC1918 private IPs: 10.x, 172.16-31.x, 192.168.x.
Action: **warn** — Often legitimately shared in support/debugging contexts; warn by default, escalate to block if needed.

---

## Customising Patterns

### Add a new pattern

```yaml
patterns:
  - name: internal_deploy_key
    regex: '\bDEPLOY-[A-F0-9]{32}\b'
    action: block
    description: "Internal CI/CD deploy key"
```

### Override an existing built-in's action

```yaml
patterns:
  - name: private_ip_range
    regex: '\b(?:192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3})\b'
    action: block
```

### Disable a built-in

```yaml
patterns:
  - name: env_file_line
    regex: "DISABLED"
    disabled: true
```
