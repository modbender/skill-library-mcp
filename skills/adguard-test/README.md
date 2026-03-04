# 🛡️ AdGuard Home Skill

Query AdGuard Home instances for DNS statistics, blocked domains, filter rules, and configuration.

## Features

- 📊 DNS query and blocking statistics
- 💻 Top clients ranking
- 🚫 Blocked domains leaderboard
- 🔧 Service status monitoring
- 🌐 DNS configuration details
- 🛡️ Filter rules inspection
- 📜 Recent query log
- 👥 Client management
- 🔒 TLS/encryption status
- ✅ Multi-instance support

## Installation

### Via ClawHub (Recommended)

```bash
clawhub install adguard-home
```

### Manual Installation

Copy this skill folder to your OpenClaw workspace:

```bash
cp -r skills/adguard-home ~/.openclaw/workspace/skills/
```

## Configuration

### 🔒 Security Best Practices

**⚠️ Important:** Do not store plaintext credentials in configuration files. Use environment variables or a secrets manager.

#### Option 1: Environment Variables (Recommended)

```bash
export ADGUARD_URL="http://192.168.145.249:1080"
export ADGUARD_USERNAME="admin"
export ADGUARD_PASSWORD="your-secure-password"
```

#### Option 2: 1Password CLI

```bash
export ADGUARD_PASSWORD=$(op read "op://vault/AdGuard/credential")
```

#### Option 3: Workspace Config (Local Development Only)

For local development, create `adguard-instances.json` in the skill directory:

```json
{
  "instances": {
    "dns1": {
      "url": "http://192.168.145.249:1080",
      "username": "admin",
      "password": "your-secure-password"
    }
  }
}
```

**⚠️ Never commit this file to version control. Add it to `.gitignore`.**

## Usage

```bash
# Statistics
/adguard stats [instance]
/adguard top-clients [instance]
/adguard top-blocked [instance]

# Status & Configuration
/adguard status [instance]
/adguard dns-info [instance]
/adguard filter-rules [instance]
/adguard tls-status [instance]
/adguard clients [instance]

# Query Log
/adguard querylog [instance] [limit]

# Health Check
/adguard health [instance]
```

## Examples

```bash
# Check DNS statistics
/adguard stats dns1

# View service status
/adguard status dns1

# See DNS configuration
/adguard dns-info dns1

# View filter rules
/adguard filter-rules dns1

# Check last 20 queries
/adguard querylog dns1 20
```

## Version

**v1.2.1** - 🔐 Credential Security (env vars, 1Password support, no multi-path search)

**v1.2.0** - 🔒 Security Hardening (Fixed command injection, native HTTP client, input validation)

**v1.1.1** - Support default and custom workspace paths

## Author

**Leo Li (@foxleoly)**

## License

MIT
