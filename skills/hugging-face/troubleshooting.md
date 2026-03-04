# Troubleshooting - Hugging Face

## 401 Unauthorized

Likely causes:
- Missing `HF_TOKEN`
- Expired or revoked token
- Typo in auth header

Actions:
1. Verify token is set in current shell
2. Regenerate token if needed
3. Re-run with minimal payload first

## 403 Forbidden or Gated Access

Likely causes:
- Model requires access approval
- Account lacks permission scope

Actions:
1. Check model card access requirements
2. Request access or switch to open alternative
3. Document gating status in shortlist

## 404 Model Not Found

Likely causes:
- Wrong model id
- Model moved or deleted
- Typo in endpoint path

Actions:
1. Re-validate model id via model API search
2. Update references in shortlist
3. Use fallback model immediately if production request is blocked

## 429 Rate Limited

Likely causes:
- Burst traffic or quota limits

Actions:
1. Back off with incremental delays
2. Reduce request frequency and payload size
3. Queue non-urgent evaluations instead of retrying aggressively

## 503 or Cold Start Timeout

Likely causes:
- Endpoint cold start
- Temporary infra saturation

Actions:
1. Retry with shorter input
2. Switch to backup model
3. Return partial result with clear status if blocking persists

## Bad Output Quality

Likely causes:
- Prompt mismatch for the model family
- Wrong task family selection
- Unstable parameters

Actions:
1. Lower temperature
2. Tighten prompt instructions
3. Re-run benchmark set and compare against shortlist alternatives
