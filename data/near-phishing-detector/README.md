# NEAR Phishing Detector (OpenClaw Skill)

Security-focused OpenClaw skill for NEAR phishing detection.

Commands:
- `near_phishing_check_url(url)` -> `dict`
- `near_phishing_check_contract(contract)` -> `dict`
- `near_phishing_report(url, details)` -> `dict`
- `near_phishing_database()` -> `list`

## Build

```bash
npm install
npm run build
```

## Test

```bash
npm test
```

## Deliverables mapping

- Phishing detector skill: implemented in `src/phishing-detector.ts`
- URL checking: `near_phishing_check_url`
- Scam database: `near_phishing_database`
- MoltHub-ready manifest: `molthub.json`
