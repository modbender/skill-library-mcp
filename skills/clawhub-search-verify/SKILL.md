# Clawhub Search & Verify

**Purpose**: Safely discover, audit, and request approval for Clawhub skills before installation.

**Workflow**:
1. Accepts a natural language search term (e.g., “daily server health check”)
2. Uses  to find matching skills
3. Presents top 3 results with: slug, version, description, download count, and risk score
4. Asks for explicit approval: “Install this? (yes/no)” before any install
5. On approval, runs 

**Safety Rules**:
- NEVER installs without your yes confirmation
- Skips any skill with <5 installs or no clear  description
- Logs every search and decision to 
- Runs in sandboxed session with no filesystem write or exec capability — only read-only clawhub search and install via CLI

**Uses only**: , ,  (for CLI),  (for log only)

**Author**: Architect (self-audited)

**Tags**: safe, automation, verify, no-shell, trusted
