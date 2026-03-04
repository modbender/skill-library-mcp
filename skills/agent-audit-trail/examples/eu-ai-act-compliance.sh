#!/bin/bash
# EU AI Act Compliance — Example Audit Trail
# Demonstrates logging patterns that satisfy Articles 12, 14, and 50

SCRIPT="./scripts/auditlog.py"

echo "=== EU AI Act Compliance Audit Trail Example ==="
echo ""

# 1. AI Disclosure (Article 50 — Transparency)
echo "1. Logging AI disclosure event..."
$SCRIPT append \
  --kind "disclosure" \
  --summary "AI chatbot identity disclosed to user on website" \
  --target "https://example.com/chat" \
  --domain "customer-facing" \
  --details '{"disclosure_type": "chatbot_banner", "visible": true}'

# 2. AI Decision with Human Oversight (Article 14)
echo "2. Logging AI decision with human gate..."
$SCRIPT append \
  --kind "decision" \
  --summary "AI recommended loan approval — pending human review" \
  --target "application-2026-0001" \
  --domain "high-risk" \
  --details '{"model": "credit-scorer-v3", "confidence": 0.91, "recommendation": "approve"}'

# 3. Human Override (Article 14 — Oversight Evidence)
echo "3. Logging human override..."
$SCRIPT append \
  --kind "human-override" \
  --summary "Human reviewer rejected AI recommendation — additional docs required" \
  --target "application-2026-0001" \
  --domain "high-risk" \
  --gate "review-jane-2026-02-24" \
  --provenance '{"reviewer": "jane@company.com", "channel": "internal-portal"}'

# 4. External API Call (Article 12 — Record-Keeping)
echo "4. Logging external API call..."
$SCRIPT append \
  --kind "api-call" \
  --summary "Called OpenAI GPT-4 for content generation" \
  --target "api.openai.com/v1/chat/completions" \
  --domain "content" \
  --details '{"model": "gpt-4", "tokens_in": 150, "tokens_out": 500}'

# 5. Credential Access (Article 12 — Security Logging)
echo "5. Logging credential access..."
$SCRIPT append \
  --kind "credential-access" \
  --summary "Accessed Stripe API key for payment processing" \
  --target "STRIPE_SECRET_KEY" \
  --domain "payments" \
  --gate "auto-approved-ops" \
  --details '{"scope": "payments", "justification": "process refund #R-4521"}'

# 6. Verify the entire chain
echo ""
echo "=== Verifying audit chain integrity ==="
$SCRIPT verify

echo ""
echo "=== Done. Your audit trail is EU AI Act ready. ==="
