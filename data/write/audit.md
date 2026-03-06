# Audit Reference

## When to Audit
- Before delivering anything > 300 words
- Before publishing/sending important pieces
- When `auto_audit: true` in config
- When user requests review

## Audit Dimensions

### 1. Grammar & Mechanics (1-10)
- Spelling errors
- Punctuation mistakes
- Subject-verb agreement
- Tense consistency

### 2. Clarity & Structure (1-10)
- Is the main point obvious?
- Does it flow logically?
- Are transitions smooth?
- Is the structure appropriate for the type?

### 3. Audience Fit (1-10)
- Matches reader's knowledge level?
- Tone appropriate for relationship?
- Jargon level correct?

### 4. Content Quality (1-10)
- Facts accurate?
- Arguments supported?
- Examples concrete?
- Nothing important missing?

### 5. Tone & Voice (1-10)
- Matches brief requirements?
- Consistent throughout?
- Authentic (not robotic)?

### 6. Conciseness (1-10)
- Any fluff paragraphs?
- Could be shorter without losing value?
- Every sentence earns its place?

## Audit Workflow

1. Run audit script
   ```bash
   ./scripts/audit.sh ~/writing article-20260211-143052
   ```

2. Sub-agent fills in the audit report with scores + issues

3. If overall < 7/10 or any "Must Fix":
   - Spawn rewrite sub-agent for specific issues
   - Apply rewrite via edit.sh (versions automatically)
   - Re-audit

4. If overall ≥ 8/10 and no blockers:
   - Ready to deliver

## Audit Report Location
```
audits/{piece-id}/
  audit_20260211-150000.md
  audit_20260211-160000.md  # after rewrite
```

## For Long Pieces (Books, Long Articles)
- Audit section by section
- Name audits: `audit_section1_20260211.md`
- Rewrite sections independently
- Final audit of assembled piece
