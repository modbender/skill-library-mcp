# Chain of Custody Log

## Case: case-2026-EXAMPLE

---

### Entry 1: Case Created
- **Timestamp:** 2026-02-17T10:30:00.000Z
- **Event:** case_created
- **Actor:** system
- **Details:** Case initialized with confidentiality classification
- **Chain Hash:** `a1b2c3d4...`

---

### Entry 2: Evidence Ingested
- **Timestamp:** 2026-02-17T10:42:00.000Z
- **Event:** evidence_ingested
- **Actor:** session-example
- **Evidence ID:** ev-example001
- **File:** incident_photo.jpg
- **SHA-256:** `e3b0c442...`
- **Source:** WhatsApp (user-redacted)
- **Chain Hash:** `b2c3d4e5...`
- **Previous Hash:** `a1b2c3d4...`

---

### Entry 3: Derivative Created
- **Timestamp:** 2026-02-17T10:45:00.000Z
- **Event:** derivative_created
- **Actor:** system
- **Evidence ID:** ev-example001
- **Derivative Type:** thumbnail
- **Derivative SHA-256:** `a7ffc6f8...`
- **Chain Hash:** `c3d4e5f6...`
- **Previous Hash:** `b2c3d4e5...`

---

### Entry 4: Evidence Ingested
- **Timestamp:** 2026-02-17T11:20:00.000Z
- **Event:** evidence_ingested
- **Actor:** session-example
- **Evidence ID:** ev-example002
- **File:** recorded_audio.mp3
- **SHA-256:** `cf80cd8a...`
- **Source:** Telegram (user-redacted)
- **Chain Hash:** `d4e5f678...`
- **Previous Hash:** `c3d4e5f6...`

---

### Entry 5: Evidence Verified
- **Timestamp:** 2026-02-17T11:25:00.000Z
- **Event:** evidence_verified
- **Actor:** system
- **Evidence ID:** ev-example001
- **Result:** PASSED (hash match, original intact)
- **Chain Hash:** `e5f67890...`
- **Previous Hash:** `d4e5f678...`

---

### Entry 6: Evidence Ingested
- **Timestamp:** 2026-02-17T11:35:00.000Z
- **Event:** evidence_ingested
- **Actor:** session-example
- **Evidence ID:** ev-example003
- **File:** document.pdf
- **SHA-256:** `7d865e95...`
- **Source:** Email (sender-redacted@example.com)
- **Chain Hash:** `f6789012...`
- **Previous Hash:** `e5f67890...`

---

### Entry 7: Case Exported
- **Timestamp:** 2026-02-17T12:00:00.000Z
- **Event:** evidence_exported
- **Actor:** system
- **Export Format:** ZIP
- **Export SHA-256:** `1234567890abcdef...`
- **Items Included:** 3
- **Chain Hash:** `78901234...`
- **Previous Hash:** `f6789012...`

---

## Verification Summary

| Evidence ID | File | Hash | Last Verified | Status |
|-------------|------|------|---------------|--------|
| ev-example001 | incident_photo.jpg | e3b0c442... | 2026-02-17T11:25:00Z | ✅ VERIFIED |
| ev-example002 | recorded_audio.mp3 | cf80cd8a... | - | ⏳ PENDING |
| ev-example003 | document.pdf | 7d865e95... | - | ⏳ PENDING |

---

## Notes

1. All timestamps are in UTC (ISO 8601 format)
2. Hash chain provides cryptographic proof of sequence integrity
3. Each entry links to previous entry via hash reference
4. Any modification to historical entries would break the chain
5. Original evidence files are stored with read-only permissions

---

## Legal Notice

This chain of custody log is generated automatically by EvidenceOps.
For legal proceedings, verify chain integrity by recalculating hashes.

**Case Retention:** 2,555 days (7 years)
**Scheduled Deletion:** 2033-02-17
**Legal Hold:** Not active
