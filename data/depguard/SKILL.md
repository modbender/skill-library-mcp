---
name: depguard
description: Dependency audit, vulnerability scanning, and license compliance. Free vuln check + paid continuous monitoring via git hooks.
homepage: https://depguard.pages.dev
metadata:
  {
    "openclaw": {
      "emoji": "🛡️",
      "primaryEnv": "DEPGUARD_LICENSE_KEY",
      "requires": {
        "bins": ["git", "bash"]
      },
      "install": [
        {
          "id": "lefthook",
          "kind": "brew",
          "formula": "lefthook",
          "bins": ["lefthook"],
          "label": "Install lefthook (git hooks manager)"
        }
      ],
      "os": ["darwin", "linux", "win32"]
    }
  }
user-invocable: true
disable-model-invocation: false
---

# DepGuard — Dependency Audit & License Compliance

DepGuard scans your project dependencies for known vulnerabilities, license violations, and outdated packages. It uses native package manager audit tools (npm audit, pip-audit, cargo-audit, etc.) and enriches results with license analysis and risk scoring.

## Commands

### Free Tier (No license required)

#### `depguard scan [directory]`
One-shot vulnerability and license scan of your project dependencies.

**How to execute:**
```bash
bash "<SKILL_DIR>/scripts/depguard.sh" scan [directory]
```

**What it does:**
1. Detects package manager (npm, yarn, pnpm, pip, cargo, go, composer, bundler, maven, gradle)
2. Runs native audit commands (npm audit, pip-audit, cargo audit, etc.)
3. Parses dependency manifests for license information
4. Generates a security report with severity levels
5. Lists packages with problematic or unknown licenses

**Example usage scenarios:**
- "Scan my dependencies for vulnerabilities" → runs `depguard scan .`
- "Check the licenses of my node modules" → runs `depguard scan . --licenses-only`
- "Are any of my packages insecure?" → runs `depguard scan`

#### `depguard report [directory]`
Generate a formatted dependency health report in markdown.

```bash
bash "<SKILL_DIR>/scripts/depguard.sh" report [directory]
```

### Pro Tier ($19/user/month — requires DEPGUARD_LICENSE_KEY)

#### `depguard hooks install`
Install git hooks that scan dependencies on every commit that modifies lockfiles.

```bash
bash "<SKILL_DIR>/scripts/depguard.sh" hooks install
```

**What it does:**
1. Validates Pro+ license
2. Installs lefthook pre-commit hook targeting lockfile changes
3. On every commit that modifies package-lock.json, yarn.lock, Cargo.lock, etc.: runs vulnerability scan, blocks commit if critical/high vulns found

#### `depguard hooks uninstall`
Remove DepGuard git hooks.

```bash
bash "<SKILL_DIR>/scripts/depguard.sh" hooks uninstall
```

#### `depguard watch [directory]`
Continuous monitoring — re-scans on any lockfile change.

```bash
bash "<SKILL_DIR>/scripts/depguard.sh" watch [directory]
```

#### `depguard fix [directory]`
Auto-fix vulnerabilities by upgrading to patched versions where available.

```bash
bash "<SKILL_DIR>/scripts/depguard.sh" fix [directory]
```

### Team Tier ($39/user/month — requires DEPGUARD_LICENSE_KEY with team tier)

#### `depguard policy [directory]`
Enforce a dependency policy: block specific licenses, require minimum versions, deny specific packages.

```bash
bash "<SKILL_DIR>/scripts/depguard.sh" policy [directory]
```

#### `depguard sbom [directory]`
Generate a Software Bill of Materials (SBOM) in CycloneDX or SPDX format.

```bash
bash "<SKILL_DIR>/scripts/depguard.sh" sbom [directory]
```

#### `depguard compliance [directory]`
Generate a compliance report for auditors — maps licenses to categories (permissive, copyleft, proprietary, unknown).

```bash
bash "<SKILL_DIR>/scripts/depguard.sh" compliance [directory]
```

## Supported Package Managers

| Manager | Lockfile | Audit Tool |
|---------|----------|------------|
| npm | package-lock.json | npm audit |
| yarn | yarn.lock | yarn audit |
| pnpm | pnpm-lock.yaml | pnpm audit |
| pip | requirements.txt / Pipfile.lock | pip-audit / safety |
| cargo | Cargo.lock | cargo audit |
| go | go.sum | govulncheck |
| composer | composer.lock | composer audit |
| bundler | Gemfile.lock | bundle audit |
| maven | pom.xml | mvn dependency-check |
| gradle | build.gradle | gradle dependencyCheck |

## Configuration

Add to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "depguard": {
        "enabled": true,
        "apiKey": "YOUR_LICENSE_KEY",
        "config": {
          "severityThreshold": "high",
          "blockedLicenses": ["GPL-3.0", "AGPL-3.0"],
          "allowedLicenses": ["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC"],
          "ignoredVulnerabilities": [],
          "autoFix": false,
          "sbomFormat": "cyclonedx"
        }
      }
    }
  }
}
```

## Important Notes

- **Free tier** works immediately — no configuration needed
- **All scanning happens locally** using native package manager audit tools
- **License validation is offline** — no phone-home
- Falls back to manifest parsing if native audit tools aren't available
- Supports monorepos — scans all workspaces/packages

## When to Use DepGuard

The user might say things like:
- "Scan my dependencies for vulnerabilities"
- "Check my package licenses"
- "Are any of my npm packages insecure?"
- "Generate a security audit report"
- "Set up dependency monitoring"
- "Block GPL dependencies in this project"
- "Generate an SBOM"
- "Check if we're compliant with our license policy"
