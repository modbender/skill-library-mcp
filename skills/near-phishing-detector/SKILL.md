---
name: near-phishing-detector
description: Detect potential phishing URLs and suspicious contracts targeting NEAR users.
metadata: {"author":"mastrophot","version":"0.1.0","homepage":"https://github.com/mastrophot/near-phishing-detector"}
---

# NEAR Phishing Detector Skill

Implementation entrypoint: `{baseDir}/dist/index.js`

Use this skill to quickly score suspicious links/contracts and generate actionable phishing reports.

## Commands

```python
@skill.command("near_phishing_check_url")
async def check_url(url: str) -> dict:
    """Check if URL is potential phishing"""

@skill.command("near_phishing_check_contract")
async def check_contract(contract: str) -> dict:
    """Check if contract is suspicious"""

@skill.command("near_phishing_report")
async def report_phishing(url: str, details: str) -> dict:
    """Report phishing attempt"""

@skill.command("near_phishing_database")
async def get_known_scams() -> list:
    """Get database of known scams"""
```

## Notes

- Designed for detection assistance, not legal determination.
- Always verify with official NEAR channels before acting on high-risk links.
