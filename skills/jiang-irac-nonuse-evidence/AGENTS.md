# AGENTS.md — Nonuse Defense Automation Repo Rules (CN Trademark)

## 0. Prime Directive
You are modifying a production-grade legal-tech automation repo for China trademark non-use defense (撤三答辩).
Changes MUST be:
- Minimal and verifiable (small diffs, no unnecessary refactor).
- Auditable (every conclusion must be traceable to evidence + rules).
- Fail-safe (never silently ignore errors that may change legal conclusions).

Do NOT fabricate facts, evidence, case data, or outputs. If sample input is missing, run compilation/tests only.

## 1. Repository Goals (What “Done” Means)
1) Observability:
   - All runs produce logs/app.log and logs/error.log
   - All runs write logs/audit.jsonl with structured events
2) Explainability:
   - Every scoring/decision output is backed by reason_chain.json
   - All thresholds/weights are externalized in rules/*.yaml and recorded in rule_profile_used.json
3) Stability:
   - No infinite hangs (LibreOffice conversion must have timeout)
   - No destructive shell ops without guardrails (safe_rm)
4) Safety:
   - No network exposure without explicit token if binding non-localhost
   - Never print secrets/tokens into logs

## 2. Coding Standards (Python)
- Python: keep code compatible with current interpreter used in repo (do not upgrade language features blindly).
- Prefer standard library.
- Add dependencies ONLY if strictly necessary; justify in commit notes.
- Never use `except Exception: pass` or swallow errors.
- Every exception handler must:
  - logger.exception(...)
  - audit({type:"exception", step, file, error, traceback?})
  - Either re-raise OR return a structured failure result.

### Logging
Use utils/logger.py:
- setup_logger(name) -> logger
- audit(event: dict) -> append JSON line into logs/audit.jsonl
Audit events MUST include:
- ts (ISO8601)
- run_id (stable for the run)
Recommended fields:
- type, step, file, evidence_id, elapsed_ms, ok, reason_code

### Determinism
- Do not introduce non-deterministic ordering.
- Sort file lists before processing.
- If hashing/signature is used, document algorithm and keep stable.

## 3. Rules Externalization (Legal Explainability)
All thresholds/weights/risk levels must live in:
- rules/time_rules.yaml
- rules/score_rules.yaml
- rules/risk_rules.yaml

At runtime:
- Load with yaml.safe_load
- Write case_output_dir/rule_profile_used.json including:
  - source file paths
  - file hash (sha256)
  - loaded keys (or full content if small)

No hard-coded magic numbers for scoring/risk gates unless explicitly allowed and documented.

## 4. Reason Chain Output (Auditability)
For each case run, generate:
- case_output_dir/reason_chain.json

Minimum schema:
- run_id
- per element (T1..T6 or equivalent):
  - score
  - hit_rules (keys)
  - evidence (list of evidence IDs or filenames)
  - citations (file + page/section indices if available)
- final_decision + rationale pointers

Do not store full sensitive evidence text in reason_chain; store excerpts only if already intended for report outputs.

## 5. LibreOffice Conversion
All doc/docx to pdf conversions:
- Must use subprocess.run(..., timeout=DEFAULT_TIMEOUT)
- On timeout or failure:
  - write logs/docx2pdf_fail.log with cmd/stdout/stderr
  - audit docx2pdf_fail with reason_code

Return structured results:
- ok, out_pdf_path, reason_code

## 6. Shell Build Scripts Safety (macOS)
All build scripts must:
- set -euo pipefail
- define safe_rm(target):
  - reject empty, "/", and paths outside BASE_DIR
- never rm -rf without safe_rm

If codesign/notarization is present:
- do NOT log credentials
- allow opt-in via env vars (SIGN_IDENTITY, NOTARY_PROFILE)

## 7. Web UI Security
Default binding:
- localhost only
If host != 127.0.0.1 OR token is provided:
- require Authorization: Bearer <token> for write endpoints
- audit every request: path/method/remote_addr/auth_ok
- never log token raw value

## 8. Verification Checklist (Must Run)
After changes:
1) python -m py_compile on all modified .py
2) Grep report for previously swallowed exceptions now audited
3) If runnable input exists, run one minimal case and confirm:
   - logs/audit.jsonl has start/end
   - reason_chain.json exists
   - rule_profile_used.json exists (if rules implemented)

## 9. Output Style for Codex
When reporting completion:
- List changed files
- For each file: what changed + why
- How to verify (commands + expected artifacts)
Avoid long explanations.