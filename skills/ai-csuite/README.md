# ai-csuite

Script-backed AI C-Suite skill for structured strategic decisions.

## What this skill does

- Builds a stage-aware executive roster for SaaS teams.
- Runs a multi-round debate with role-based positions.
- Produces a structured `CEO BRIEF` and `CEO DECISION`.
- Validates output shape and scans the skill for publish-time safety checks.

## Included files

- `SKILL.md`: prompt workflow and operating rules.
- `config/company.yaml`: required company context template.
- `scripts/prepare_session.py`: validates context and builds session packet.
- `scripts/run_debate.py`: generates debate output markdown.
- `scripts/validate_output.py`: checks mandatory output markers.
- `scripts/security_scan.py`: static checks for risky patterns/imports.
- `.github/workflows/ci.yml`: GitHub Actions smoke checks.

## Requirements

- Python 3.11+ (stdlib only).
- No third-party Python dependencies.

## Quick start

1. Enter the skill directory:

```bash
cd ai-csuite
```

2. Fill company context:

```bash
cp config/company.yaml config/company.local.yaml
```

Edit `config/company.local.yaml` with your real values.

3. Run security scan:

```bash
python3 scripts/security_scan.py .
```

4. Prepare the session:

```bash
python3 scripts/prepare_session.py \
  --topic "Should we change pricing for SMB annual plans?" \
  --company-file config/company.local.yaml
```

5. Run the debate:

```bash
python3 scripts/run_debate.py \
  --topic "Should we change pricing for SMB annual plans?" \
  --company-file config/company.local.yaml \
  --output logs/latest-decision.md
```

6. Validate generated output:

```bash
python3 scripts/validate_output.py --file logs/latest-decision.md
```

If validation prints `PASS`, the decision file is complete.

## Company config schema

`config/company.yaml` must contain:

- `company_name`
- `product`
- `stage` (`solo | pre-seed | seed | series-a`)
- `arr_or_mrr`
- `runway_months`
- `team_size`
- `constraints` (YAML list)

## Stage behavior

- `solo`: 2 rounds, lean executive panel.
- `pre-seed`: 2 rounds, includes customer voice in debate.
- `seed`: 3 rounds, adds growth debate depth.
- `series-a`: 3 rounds, full C-suite coverage.

`CV` and `CFO` always provide a pre-round data brief, even when not both in debate roster.

## Output contract

Generated markdown includes:

- `DATA BRIEF (Pre-Round)`
- Round sections for active agents
- `CEO BRIEF`
- `CEO DECISION`
- Decision metadata (`CONFIDENCE`, `REVERSIBILITY`, next steps)

## VirusTotal-safe publishing checklist

Before tagging or releasing:

```bash
python3 scripts/security_scan.py .
python3 scripts/prepare_session.py --topic "sanity check" --company-file config/company.yaml
python3 scripts/run_debate.py --topic "sanity check" --company-file config/company.yaml --output logs/sanity.md
python3 scripts/validate_output.py --file logs/sanity.md
```

Expected:

- `security_scan.py` returns `PASS`
- `validate_output.py` returns `PASS`
- No obfuscated payloads, no non-stdlib imports, no hidden outbound calls

## GitHub publishing flow

From repository root:

```bash
git add ai-csuite
git commit -m "Publish ai-csuite skill with runtime scripts and docs"
git push origin main
```

