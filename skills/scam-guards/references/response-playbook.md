# Security Response Playbook

This playbook defines the standard operating procedures when Scam Guards detects a potential threat.

## 🟢 Level 1: SAFE
- **Observation**: No malicious patterns, known IOCs, or high PHI scores detected.
- **Action**: No user intervention required.
- **Output**: Standard scan result/session log with a "Verified" badge.
- **User Recommendation**: Proceed as normal.

## 🟡 Level 2: WARNING
- **Observation**: Moderate PHI scores (0.4 - 0.7) or minor technical anomalies (e.g., typosquatting of a non-critical skill).
- **Action**: Generate an alert in the session log. Log the suspicious event to the evidence chain.
- **Output**: Report with a "WARNING" status.
- **User Recommendation**: Manually review the agent's recent dialogue. Check the authenticity of the skill being used.

## 🔴 Level 3: DANGER
- **Observation**: Critical technical find (e.g., reverse shell pattern, blacklisted wallet) or severe PHI pressure (> 0.7).
- **Action**: Block the immediate action. Create a linked SHA-256 evidence chain. Alert the user immediately with specific threat details.
- **Output**: Report with a "DANGER" status and recommendation to "BLOCK ACCESS."
- **User Recommendation**: Terminate the session immediately. Do not interact with the target URL or wallet.

## 💀 Level 4: CRITICAL
- **Observation**: Confirmed execution of malicious code, access to credential files, or interaction with known ClawHavoc C2 infrastructure.
- **Action**: All Level 3 actions + immediate suggestion to the user to remove the offending skill from their workspace.
- **Output**: Full Security Audit Report + "DO NOT INSTALL" recommendation.
- **User Recommendation**: Remove the skill immediately. Rotate any credentials stored in `.env` or `~/.aws/` that the agent has access to. Report the publisher to ClawHub Support.
