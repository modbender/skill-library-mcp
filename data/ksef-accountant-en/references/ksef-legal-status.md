# KSeF Legal Status - Details

**Last updated:** 8 February 2026
**NOTE:** Information may change. Regularly verify current regulations and communications from the Ministry of Finance.

---

## Implementation Schedule (Planned)

### Phase 1: Large Taxpayers (from 1 February 2026)
**Who it applies to:** Turnover >200 million PLN gross in 2024

**Obligations:**
- Issuing invoices through KSeF
- Receiving invoices through KSeF

### Phase 2: Other Taxpayers (from 1 April 2026)
**Who it applies to:** Turnover <=200 million PLN

**Obligations:**
- Receiving invoices through KSeF (from 1 February 2026)
- Issuing invoices through KSeF (from 1 April 2026)
- Until 31 March 2026 they may issue invoices outside KSeF

### Phase 3: Micro-entrepreneurs (from 1 January 2027)
**Who it applies to:** Monthly turnover <10 thousand PLN

**Obligations:**
- Receiving: from 1 February 2026
- Issuing: from 1 January 2027

---

## Transition Period

**NOTE:** Details may change. The information presented is based on currently available communications.

### Planned Grace Period
- **Until 31 December 2026** - anticipated no penalties for errors
- Applies to: errors in FA(3) structure, submission delays
- Does not apply to: evasion of invoice issuance

### Offline24 Mode
- **Status:** Planned as a permanent system feature
- **Purpose:** Emergency situations (no internet, KSeF outage, disasters)
- **Submission deadline:** 24h after connectivity is restored
- **Legal note:** Right to deduct VAT from the date of KSeF number assignment (not from the offline issue date)

### Invoices Outside KSeF
- **Until 31 March 2026:** Allowed for companies <=200 million PLN
- **From 1 April 2026:** Prohibited (with exceptions for special cases)

---

## System Changes

### KSeF 1.0 -> KSeF 2.0
- **KSeF 1.0:** Planned shutdown 26 January 2026
- **Technical break:** 5 days (26-31 January 2026)
- **KSeF 2.0:** Planned launch 1 February 2026

### FA(2) -> FA(3)
- **FA(2):** Planned end of support 1 February 2026
- **FA(3):** Mandatory from 1 February 2026
- **Migration:** All taxpayers must adapt their systems

---

## Legal Consequences (Future)

**NOTE:** The information below relates to the planned penalty system after the grace period ends.

### After 1 January 2027 (Planned)
- No invoice in KSeF -> possible penalty
- Invoice outside KSeF -> possible penalty
- Delayed submission -> possible penalty

**Penalty amounts:** Consult the current VAT Act

---

## Technical Requirements

### Mandatory Structure
- **FA(3) ver. 1-0E**
- Format: XML compliant with schema
- Encoding: UTF-8
- Validation: Automatic upon receipt by KSeF

### Certificates (MCU)
- **MCU:** Certificate and Authorization Module
- **Status:** Per schedule, active from 1.11.2025
- **Purpose:** Alternative authorization method (in addition to tokens)

---

## Information Sources

### Official
- KSeF Portal: https://ksef.podatki.gov.pl
- Ministry of Finance: https://www.gov.pl/web/kas/ksef

### Monitoring Changes
- MF Communications: https://ksef.podatki.gov.pl/web/ksef/aktualnosci
- KSeF Latarnia (status): https://github.com/CIRFMF/ksef-latarnia

---

**Last updated:** 8 February 2026
**Next review:** Recommended every 2 weeks
