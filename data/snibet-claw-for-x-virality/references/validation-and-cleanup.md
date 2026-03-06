# Validation and Cleanup

## Forbidden Output

Reject and rewrite if tweet contains:
- Emojis
- Hashtags
- Markdown markers
- Em dash character
- Thread numbering patterns
- CTA bait phrases

Common CTA bait phrases to block:
- "follow for more"
- "rt if you agree"
- "like and share"
- "drop a comment"

## Anti-AI Cleanup

Run one mandatory cleanup pass:

1. Remove filler language.
2. Remove predictable motivational framing.
3. Remove overexplaining.
4. Remove corporate wording.
5. Remove obvious LLM phrasing.

If text still feels synthetic, run one extra rewrite.

## Structural Checks

Must pass:
- Exactly one tweet
- 1 to 6 short lines preferred
- 4 to 7 lines allowed only when tight
- Whitespace improves readability
- Every line carries signal

## Safety Checks

Maintain:
- No direct plagiarism from voice examples
- No copied sentence skeletons from references
- No explicit impersonation claims

## Release Standard

Tweet is release-ready only when:
- It can be posted instantly
- It triggers likely replies
- It reflects creator mode clearly
