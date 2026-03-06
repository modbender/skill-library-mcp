# STOCK LEDGER — {{COMPANY_NAME}}

(A {{STATE}} Corporation)

---

{{#EACH STOCK_CLASS}}

## {{CLASS_NAME}}

**Authorized:** {{AUTHORIZED}} shares | **Par Value:** ${{PAR_VALUE}} | **Voting:** {{VOTING_RIGHTS}} vote(s) per share
**Total Issued:** {{TOTAL_ISSUED}} / {{AUTHORIZED}} authorized

| Cert. No. | Date Issued | Stockholder | Shares | Consideration | Status |
|-----------|-------------|-------------|--------|---------------|--------|
{{#EACH SHAREHOLDERS}}
| {{CERT_NO}} | {{DATE}} | {{NAME}} | {{SHARES}} | {{CONSIDERATION}} | Outstanding |
{{/EACH}}

{{/EACH}}

---

## VOTING POWER SUMMARY

| Stockholder | {{#EACH STOCK_CLASS}} {{SHORT_NAME}} Shares | {{SHORT_NAME}} Votes | {{/EACH}} Total Votes | % of Total |
|-------------|{{#EACH STOCK_CLASS}}--------|--------|{{/EACH}}-------------|------------|
{{#EACH ALL_SHAREHOLDERS}}
| {{NAME}} | {{#EACH CLASSES}} {{SHARES}} | {{VOTES}} | {{/EACH}} {{TOTAL_VOTES}} | {{PERCENTAGE}} |
{{/EACH}}
| **TOTAL** | {{TOTALS_ROW}} | **100%** |

---

Maintained by the Secretary of the Corporation. Last updated: {{FILING_DATE}}
