---
name: haplo-donor-selection
description: "Haploidentical donor selection for hematopoietic cell transplantation (HCT). Extracts HLA typing from images/PDFs, queries IPD-IMGT/HLA APIs (B-Leader, DPB1 TCE, KIR Ligand), applies TCE-Core reclassification (Solomon 2024), calculates 3-year DFS via local Cox model (Fuchs 2022), ranks donors, compares against MSD/MMUD reference outcomes (Mehta 2024), and generates a clinical decision report with PDF export. Use when: user sends HLA typing reports for haplo donor evaluation, asks about B-leader matching, DPB1 TCE permissiveness, KIR ligand analysis, or needs haplo vs MSD/MUD/MMUD outcome comparisons for transplant planning."
---

# Haplo Donor Selection Workflow

## Overview

12-step pipeline: HLA report intake → clinical data collection → API-based
immunogenetic analysis → Cox model DFS prediction → donor ranking → comparative
outcome analysis → PDF report generation.

## Workflow Steps

### Step 0: Receive HLA Typing Report
Accept image (JPG/PNG) or PDF. Extract all HLA loci at 4-digit resolution:
A, B, C, DRB1, DQB1, DPB1 for patient and each donor.

### Step 1: Collect Patient Clinical Info
Ask sequentially (do NOT assume — ask one at a time):

1. **疾病诊断** — AML / ALL / MDS
2. **疾病状态** — see `references/disease-codes.md`
3. **患者年龄**
4. **HCT-CI 评分** — 0 / 1 / 2 / ≥3

CMV: default all positive (patient + donors). Donor ages from typing report.

### Step 2: Extract HLA Typing
Parse each person's alleles from the report image/PDF.
Verify: 6 loci × 2 alleles = 12 values per person.

### Step 2.5: Data Cross-Validation (MANDATORY)
Use the report's built-in **Matches row** to verify extracted data:
- For each donor × each locus, count shared alleles with patient (0/1/2)
- Compare against the Matches number shown in the report
- If mismatch → re-read that locus from the image
- **DPB1 is rightmost column — highest risk of column misalignment**
- This step catches OCR/reading errors before they propagate to wrong rankings

### Step 3: Haplotype Deduction & Donor Screening
For sibling donors, deduce parental haplotypes.
- 1 shared haplotype → ✅ Haploidentical
- 2 shared → MSD (flag separately)
- 0 shared → ❌ Exclude with explanation

### Step 4: IPD-IMGT/HLA API Calls
Run `scripts/hla_matching.py --json '{...}'`

Three API endpoints:
- **B-Leader**: `https://www.ebi.ac.uk/cgi-bin/ipd/matching/b_leader`
- **DPB1 TCE v3**: `https://www.ebi.ac.uk/cgi-bin/ipd/matching/dpb1_tce_v3`
- **KIR Ligand**: `https://www.ebi.ac.uk/cgi-bin/ipd/matching/kir_ligand`

Donor IDs must be ASCII-only in URL params.

### Step 5: TCE-Core Reclassification (Solomon 2024)
TCE Group 3 splits into core vs non-core. See `references/tce-core.md`.

Key rule: G3 non-core mismatched with G3 core → C-NPMM → nonpermissive (HR 0.72).

### Step 6: DRB1/DQB1 Match Status
Compare patient vs donor alleles:
- DRB1: match / mismatch
- DQB1: match / mismatch
- Best combo: mismatch/match (HR 0.80)
- Worst combo: match/match (HR 1.32)

### Step 7: Cox Model DFS Calculation
Run `scripts/haplo_dfs.py --json '{...}'`

Model: Fuchs et al., Blood 2022, Table 3.
Baseline S₀(3yr) = 0.413. See `references/cox-model.md` for all coefficients.

### Step 8: Donor Ranking
Sort by 3-year DFS descending.
- Ranking factors: B-Leader + DRB1/DQB1 + DPB1 TCE-Core + CMV + HCT-CI + age
- KIR: display only, does NOT affect ranking

### Step 9: MSD/MMUD Comparison Table (Mehta 2024)
Always show 5-row comparison table. See `references/mehta-comparison.md`.

| Group | Source |
|---|---|
| ⭐ Optimal Haplo (by B-Leader + DRB1 group) | Mehta TCT 2024 |
| 🟢 Young MSD+PTCy (under 50y) | Mehta Blood Adv 2024 |
| 🟡 Old MSD+PTCy (≥50y) | Mehta Blood Adv 2024 |
| 🔵 MMUD PBM-matched (CNI) | Mehta TCT 2024 |
| 🟠 MMUD PBM-mismatched (CNI) | Mehta TCT 2024 |

### Step 10: Donor Selection Recommendation
Auto-generate recommendations for each hypothetical scenario:
- 🟢 If young MSD available → choose whom?
- 🟡 If old MSD available → choose whom?
- 🔵 If MMUD available → choose whom?
- 💡 Final conclusion

Logic depends on: Haplo group × donor age × patient age.

### Step 11: Generate Final Report
Output 8-part text report:
1. Patient info
2. Donor ranking (DFS + KIR display)
3. MSD/MMUD comparison table
4. HR comparisons + age effects
5. GVHD advantage analysis
6. If-other-donor-type recommendations
7. Comprehensive conclusion
8. References (7 papers)

### Step 12: Export PDF and Save
Generate PDF using `scripts/report_pdf.py`, filename: `{patient_name}_DFS.pdf`

**Save location** (in order of preference):
1. **Google Drive** — if `gog` CLI is configured and user provides a folder path/ID:
   - Use `gog drive upload <file> --parent <folder_id>`
   - Ask user for Drive folder on first use, remember for subsequent runs
2. **Default local path** — `~/openclaw-reports/HLA/`
   - Create directory if not exists
   - Always save a local copy regardless of Drive upload

## Scripts

| Script | Purpose |
|---|---|
| `scripts/hla_matching.py` | B-Leader, DPB1 TCE, KIR Ligand API queries |
| `scripts/haplo_dfs.py` | Cox model DFS + comparison + recommendation |
| `scripts/report_pdf.py` | Text report → PDF (Chinese font support) |

## References

| File | Content |
|---|---|
| `references/disease-codes.md` | Supported disease/stage codes |
| `references/cox-model.md` | Full Cox model coefficients |
| `references/tce-core.md` | TCE-Core reclassification rules |
| `references/mehta-comparison.md` | Mehta 2024 reference outcome data |

## Dependencies

- Python 3.x with `urllib`, `json`, `math` (stdlib)
- `fpdf2` (for PDF generation)
- Chinese font: WenQuanYi Zen Hei (`/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`)
- Internet access for IPD-IMGT/HLA API calls
