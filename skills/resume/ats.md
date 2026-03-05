# ATS (Applicant Tracking Systems)

## What ATS Does

ATS parses resumes, extracts data, and filters candidates before humans see them.

**Impact:** 75%+ of resumes rejected by ATS before reaching recruiter.

---

## Format Rules for ATS

### Safe (high parseability)
- Single column layout
- Standard fonts: Arial, Calibri, Times New Roman, Georgia
- Simple bullet points: •, -, not fancy symbols
- Standard section headers: "Experience", "Education", "Skills"
- PDF with text layer (not scanned/image)
- DOCX (most compatible overall)

### Risky (may break parsing)
- Two-column layouts
- Tables for formatting
- Text boxes
- Creative section headers ("My Journey" instead of "Experience")
- Embedded images/logos
- Headers/footers with important info

### Dangerous (will likely fail)
- Scanned PDFs (no text layer)
- Images of text
- Infographic-style resumes
- Heavy use of unicode characters (→, ★, ●)
- Non-standard file formats

---

## Keyword Optimization

### How ATS matches keywords:
- Exact match preferred: "Project Management" ≠ "PM" unless both present
- Phrase matching: "machine learning engineer" as unit
- Frequency matters but stuffing penalizes
- Context increasingly considered by modern ATS

### Keyword strategy:
1. Extract keywords from job description
2. Use exact phrasing when possible
3. Include both acronym and spelled out: "SEO (Search Engine Optimization)"
4. Place keywords in context, not as lists
5. Target 2-3 mentions of critical keywords

### Where to place keywords:
- **Best:** In achievement bullets (contextual)
- **Good:** Skills section
- **OK:** Summary
- **Avoid:** Stuffing anywhere

---

## Section Headers

ATS looks for standard headers. Use these exact terms:

| Standard (recognized) | Avoid (may not parse) |
|-----------------------|----------------------|
| Experience | Work History, Career, Journey |
| Education | Academic Background, Studies |
| Skills | Core Competencies, Expertise |
| Summary | Profile, About Me, Objective |
| Certifications | Licenses, Credentials |

---

## Date Formats

Be consistent throughout. These parse reliably:
- January 2020 – Present
- Jan 2020 – Present
- 01/2020 – Present
- 2020 – Present (year only)

**Problem formats:**
- 1st Jan '20 (abbreviated year)
- Winter 2020 (non-standard)
- Inconsistent format across roles

---

## Contact Information

Place at top, not in header/footer. Include:
- Full name
- Phone (one number)
- Email (professional)
- LinkedIn URL (optional, plain text)
- Location (City, State sufficient — full address not needed)

**Skip:** Photo, personal details, references

---

## Parseability Check

Before submitting, verify:

1. **Text selectable?** — Open PDF, try selecting text. If you can't, ATS can't read it.
2. **Copy-paste test** — Copy resume content to plain text. If it scrambles, ATS will too.
3. **Standard sections?** — Are headers recognizable?
4. **Dates extractable?** — Can you identify employment timeline easily?

---

## ATS Score Estimation

Rate resume against job description:

| Factor | Weight | Check |
|--------|--------|-------|
| Required skills present | 40% | Are all must-haves mentioned? |
| Keywords matched | 30% | JD phrases appear in resume? |
| Format compatible | 20% | Passes parseability checks above? |
| Experience level match | 10% | Years/seniority appropriate? |

**Quick estimate:**
- 80%+ → Likely to pass ATS
- 60-80% → May pass, optimize keywords
- <60% → Unlikely to pass, significant gaps

---

## Multi-Format Strategy

Maintain three versions:
1. **PDF** — For human readers, preserves design
2. **DOCX** — Maximum ATS compatibility, editable
3. **Plain text** — Guaranteed parseable, copy-paste into forms

When submitting:
- If system accepts PDF → submit PDF
- If system accepts only DOC/DOCX → submit DOCX
- If copy-paste into text boxes → use plain text version
