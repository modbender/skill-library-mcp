"""
_cv_styles.py - Embedded CSS for CV templates.
All CSS is stored as Python strings - no external files needed.
Stdlib only.
"""

# ---------------------------------------------------------------------------
# Base styles shared between preview and print
# ---------------------------------------------------------------------------

CV_BASE_CSS = """\
/* CV Base Styles - Shared between Preview and Print */
.cv-page {
  --cv-accent: var(--accent-color, #2563eb);
  --cv-text: #1f2937;
  --cv-text-light: #6b7280;
  --cv-border: #e5e7eb;
  font-family: 'Roboto', 'Inter', 'Arial', sans-serif;
  font-size: 11pt;
  line-height: 1.15;
  color: var(--cv-text);
  background: white;
}
.cv-page {
  width: 210mm;
  min-height: 297mm;
  height: auto;
  padding: 15mm 20mm;
  box-sizing: border-box;
}
.cv-page.preview-mode { box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
.cv-page.print-mode { box-shadow: none; }
.cv-page a[href^="http"]::after {
  content: " (" attr(data-short-url) ")";
  font-size: 0.75em;
  font-weight: normal;
  color: var(--cv-text-light);
}
.cv-page a[href^="http"]:not([data-short-url])::after {
  content: " (" attr(href) ")";
  word-break: break-all;
}
.cv-section { break-inside: auto; page-break-inside: auto; }
.cv-header { break-after: avoid; page-break-after: avoid; }
.cv-section-title { break-after: avoid; page-break-after: avoid; }
.page-top-margin { padding-top: 12mm; }
@media print {
  .cv-page {
    background-image: none;
    box-shadow: none;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  @page { size: A4; margin: 12mm 0 8mm 0; }
  @page :first { margin-top: 0; }
}
"""

# ---------------------------------------------------------------------------
# Template: Classic (ATS-Optimised)
# ---------------------------------------------------------------------------

CLASSIC_CSS = """\
/* Template: Classic (ATS-Optimised) */
.cv-page {
  --cv-accent: var(--accent-color, #2563eb);
  --cv-text: #1f2937;
  --cv-text-light: #6b7280;
  --cv-border: #e5e7eb;
  font-family: 'Roboto', 'Arial', sans-serif;
  font-size: 11pt;
  line-height: 1.15;
  color: var(--cv-text);
  padding: 12mm 15mm;
}
.cv-header { text-align: center; padding-bottom: 8pt; border-bottom: 1.5pt solid var(--cv-accent); margin-bottom: 10pt; }
.cv-name { font-size: 20pt; font-weight: 700; color: var(--cv-text); margin-bottom: 2pt; letter-spacing: 0.5pt; }
.cv-title { font-size: 11pt; font-weight: 500; color: var(--cv-accent); margin-bottom: 6pt; }
.cv-contact { display: flex; justify-content: center; flex-wrap: wrap; gap: 4pt 12pt; font-size: 10pt; color: var(--cv-text-light); }
.cv-contact a { color: var(--cv-text-light); text-decoration: none; }
.cv-contact a:hover { color: var(--cv-accent); }
.cv-contact-item { display: inline-flex; align-items: center; gap: 4pt; }
.cv-section { margin-bottom: 8pt; }
.cv-section-title { font-size: 12pt; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5pt; color: var(--cv-accent); border-bottom: 0.5pt solid var(--cv-border); padding-bottom: 2pt; margin-bottom: 5pt; }
.cv-summary { font-size: 11pt; line-height: 1.15; color: var(--cv-text); text-align: justify; }
.cv-skills-list { display: flex; flex-wrap: wrap; gap: 4pt 6pt; }
.cv-skill-tag { display: inline-block; padding: 1pt 0; font-size: 10pt; color: var(--cv-text); }
.cv-skill-tag:not(:last-child)::after { content: " \\2022"; color: var(--cv-text-light); margin-left: 6pt; }
.cv-skill-tag.highlight { font-weight: 600; color: var(--cv-accent); }
.cv-skills-category { margin-bottom: 4pt; display: flex; flex-wrap: wrap; align-items: baseline; }
.cv-skills-category:last-child { margin-bottom: 0; }
.cv-skills-category-name { font-size: 10pt; font-weight: 600; color: var(--cv-accent); margin-right: 6pt; white-space: nowrap; }
.cv-skills-category-name::after { content: ":"; }
.cv-skills-category .cv-skills-list { flex: 1; }
.cv-experience-item { margin-bottom: 8pt; page-break-inside: avoid; }
.cv-experience-item:last-child { margin-bottom: 0; }
.cv-experience-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 1pt; }
.cv-experience-title { font-size: 11pt; font-weight: 600; color: var(--cv-text); }
.cv-experience-date { font-size: 10pt; color: var(--cv-text-light); white-space: nowrap; }
.cv-experience-company { font-size: 10pt; color: var(--cv-accent); margin-bottom: 2pt; }
.cv-experience-location { color: var(--cv-text-light); font-weight: 400; }
.cv-experience-description { font-size: 10pt; color: var(--cv-text-light); margin-bottom: 2pt; font-style: italic; }
.cv-experience-achievements { list-style: none; padding-left: 0; }
.cv-experience-achievements li { position: relative; padding-left: 10pt; margin-bottom: 1pt; font-size: 10pt; line-height: 1.15; }
.cv-experience-achievements li::before { content: "\\2022"; position: absolute; left: 0; color: var(--cv-accent); font-weight: bold; }
.cv-education-item { margin-bottom: 4pt; }
.cv-education-item:last-child { margin-bottom: 0; }
.cv-education-header { display: flex; justify-content: space-between; align-items: baseline; }
.cv-education-degree { font-size: 10pt; font-weight: 600; color: var(--cv-text); }
.cv-education-year { font-size: 10pt; color: var(--cv-text-light); }
.cv-education-institution { font-size: 10pt; color: var(--cv-text-light); }
.cv-education-honors { font-size: 10pt; color: var(--cv-accent); font-style: italic; }
.cv-certifications-list { display: grid; grid-template-columns: repeat(2, 1fr); gap: 2pt 12pt; }
.cv-certification-item { display: flex; justify-content: space-between; align-items: baseline; font-size: 10pt; }
.cv-certification-name { font-weight: 500; }
.cv-certification-issuer { color: var(--cv-text-light); font-size: 9pt; }
.cv-languages-list { display: flex; flex-wrap: wrap; gap: 8pt; }
.cv-language-item { font-size: 10pt; }
.cv-language-name { font-weight: 500; }
.cv-language-level { color: var(--cv-text-light); font-size: 10pt; }
.cv-project-item { margin-bottom: 8pt; }
.cv-project-item:last-child { margin-bottom: 0; }
.cv-project-name { font-size: 11pt; font-weight: 600; color: var(--cv-text); }
.cv-project-name a { color: var(--cv-accent); text-decoration: none; }
.cv-project-description { font-size: 10pt; color: var(--cv-text-light); margin-top: 2pt; }
.cv-soft-skills-list { display: flex; flex-wrap: wrap; gap: 8pt 16pt; }
.cv-soft-skill { font-size: 11pt; color: var(--cv-text); }
.cv-two-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 12pt 24pt; }
.cv-section.hidden { display: none; }
@media print {
  .cv-page { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .cv-experience-item, .cv-education-item, .cv-project-item { page-break-inside: avoid; }
  .cv-section { page-break-inside: auto; break-inside: auto; }
  .cv-section.cv-skills-section, .cv-skills-list, .cv-skills-category { page-break-inside: auto; break-inside: auto; }
  .cv-section-title { page-break-after: avoid; break-after: avoid; }
}
"""

# ---------------------------------------------------------------------------
# Template: Modern Sidebar
# ---------------------------------------------------------------------------

MODERN_SIDEBAR_CSS = """\
/* ============================================
   Template: Modern Sidebar
   Compatibilite ATS: 4/5
   Structure: Sidebar 30% + Main 70%
   ============================================ */

.cv-page {
  --cv-accent: var(--accent-color, #2563eb);
  --cv-accent-light: #eff6ff;
  --cv-text: #1f2937;
  --cv-text-light: #6b7280;
  --cv-text-inverse: #ffffff;
  --cv-border: #e5e7eb;
  --sidebar-width: 35%;

  font-family: 'Roboto', 'Arial', sans-serif;
  font-size: 10pt;
  line-height: 1.15;
  color: var(--cv-text);
  padding: 0 !important;
  display: flex;
  min-height: 297mm;
}

/* Sidebar */
.cv-sidebar {
  width: var(--sidebar-width);
  background: var(--cv-accent);
  color: var(--cv-text-inverse);
  padding: 10mm 8mm;
  display: flex;
  flex-direction: column;
  gap: 8pt;
  min-height: 297mm;
}

/* Main Content */
.cv-main {
  flex: 1;
  padding: 10mm 10mm 8mm 10mm;
  display: flex;
  flex-direction: column;
  gap: 8pt;
}

/* Sidebar Header */
.cv-sidebar .cv-header {
  text-align: center;
  padding-bottom: 8pt;
  border-bottom: 1pt solid rgba(255,255,255,0.2);
}

.cv-sidebar .cv-name {
  font-size: 16pt;
  font-weight: 700;
  color: var(--cv-text-inverse);
  margin-bottom: 3pt;
}

.cv-sidebar .cv-title {
  font-size: 10pt;
  font-weight: 400;
  color: rgba(255,255,255,0.9);
  text-transform: uppercase;
  letter-spacing: 1pt;
}

/* Sidebar Sections */
.cv-sidebar .cv-section {
  margin-bottom: 0;
}

.cv-sidebar .cv-section-title {
  font-size: 9pt;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1pt;
  color: rgba(255,255,255,0.7);
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 8pt;
}

/* Sidebar Contact */
.cv-sidebar .cv-contact {
  display: flex;
  flex-direction: column;
  gap: 6pt;
  font-size: 9pt;
}

.cv-sidebar .cv-contact-item {
  display: flex;
  align-items: center;
  gap: 6pt;
  color: var(--cv-text-inverse);
}

.cv-sidebar .cv-contact a {
  color: var(--cv-text-inverse);
  text-decoration: underline;
  text-underline-offset: 2pt;
}

.cv-sidebar .cv-contact a::after {
  color: rgba(255, 255, 255, 0.85) !important;
}

.cv-sidebar .cv-contact a:hover {
  opacity: 0.9;
}

/* Sidebar Skills */
.cv-sidebar .cv-skills-list {
  display: flex;
  flex-direction: column;
  gap: 6pt;
}

.cv-sidebar .cv-skill-item {
  display: flex;
  flex-direction: column;
  gap: 2pt;
}

.cv-sidebar .cv-skill-name {
  font-size: 9pt;
  font-weight: 500;
}

.cv-sidebar .cv-skill-bar {
  height: 4pt;
  background: rgba(255,255,255,0.2);
  border-radius: 2pt;
  overflow: hidden;
}

.cv-sidebar .cv-skill-level {
  height: 100%;
  background: var(--cv-text-inverse);
  border-radius: 2pt;
}

/* Sidebar Tags (alternative) */
.cv-sidebar .cv-skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4pt;
}

.cv-sidebar .cv-skill-tag {
  padding: 3pt 6pt;
  background: rgba(255,255,255,0.15);
  border-radius: 3pt;
  font-size: 8pt;
  color: var(--cv-text-inverse);
}

.cv-sidebar .cv-skill-tag.highlight {
  background: var(--cv-text-inverse);
  color: var(--cv-accent);
}

/* Sidebar Languages */
.cv-sidebar .cv-languages-list {
  display: flex;
  flex-direction: column;
  gap: 4pt;
}

.cv-sidebar .cv-language-item {
  display: flex;
  justify-content: space-between;
  font-size: 9pt;
}

.cv-sidebar .cv-language-level {
  color: rgba(255,255,255,0.7);
}

/* Sidebar Soft Skills */
.cv-sidebar .cv-soft-skills-list {
  display: flex;
  flex-direction: column;
  gap: 4pt;
}

.cv-sidebar .cv-soft-skill {
  font-size: 9pt;
  padding-left: 10pt;
  position: relative;
}

.cv-sidebar .cv-soft-skill::before {
  content: "\\203A";
  position: absolute;
  left: 0;
  color: rgba(255,255,255,0.6);
}

/* Main Content Styles */
.cv-main .cv-section-title {
  font-size: 10pt;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1pt;
  color: var(--cv-accent);
  border-bottom: 2pt solid var(--cv-accent);
  padding-bottom: 3pt;
  margin-bottom: 6pt;
}

/* Main Summary */
.cv-main .cv-summary {
  font-size: 9pt;
  line-height: 1.4;
  color: var(--cv-text);
  padding: 8pt;
  background: var(--cv-accent-light);
  border-left: 3pt solid var(--cv-accent);
}

/* Main Experience */
.cv-main .cv-experience-item {
  margin-bottom: 8pt;
  page-break-inside: avoid;
}

.cv-main .cv-experience-item:last-child {
  margin-bottom: 0;
}

.cv-main .cv-experience-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 2pt;
}

.cv-main .cv-experience-title {
  font-size: 11pt;
  font-weight: 600;
  color: var(--cv-text);
}

.cv-main .cv-experience-date {
  font-size: 9pt;
  color: var(--cv-text-light);
  background: var(--cv-accent-light);
  padding: 2pt 6pt;
  border-radius: 3pt;
}

.cv-main .cv-experience-company {
  font-size: 10pt;
  color: var(--cv-accent);
  margin-bottom: 4pt;
}

.cv-main .cv-experience-achievements {
  list-style: none;
  padding-left: 0;
}

.cv-main .cv-experience-achievements li {
  position: relative;
  padding-left: 14pt;
  margin-bottom: 2pt;
  font-size: 9pt;
  line-height: 1.3;
}

.cv-main .cv-experience-achievements li::before {
  content: "\\25B8";
  position: absolute;
  left: 0;
  color: var(--cv-accent);
}

/* Main Education */
.cv-main .cv-education-item {
  margin-bottom: 8pt;
  padding-left: 10pt;
  border-left: 2pt solid var(--cv-accent-light);
}

.cv-main .cv-education-degree {
  font-size: 10pt;
  font-weight: 600;
}

.cv-main .cv-education-institution {
  font-size: 9pt;
  color: var(--cv-text-light);
}

.cv-main .cv-education-year {
  font-size: 9pt;
  color: var(--cv-accent);
}

/* Main Certifications */
.cv-main .cv-certification-item {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 4pt 0;
  border-bottom: 1pt dotted var(--cv-border);
}

.cv-main .cv-certification-item:last-child {
  border-bottom: none;
}

/* Main Projects */
.cv-main .cv-project-item {
  margin-bottom: 8pt;
}

.cv-main .cv-project-name {
  font-size: 10pt;
  font-weight: 600;
}

.cv-main .cv-project-name a {
  color: var(--cv-accent);
}

.cv-main .cv-project-description {
  font-size: 9pt;
  color: var(--cv-text-light);
}

/* Utility */
.cv-section.hidden {
  display: none;
}

/* Print */
@media print {
  .cv-page {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  .cv-sidebar {
    background: var(--cv-accent) !important;
  }
}
"""

# ---------------------------------------------------------------------------
# Template: Two-Column
# ---------------------------------------------------------------------------

TWO_COLUMN_CSS = """\
/* ============================================
   Template: Two-Column
   Compatibilite ATS: 3/5
   Structure: 2 colonnes equilibrees (40/60)
   ============================================ */

:root {
  --page-bg: #2563eb;
}

.cv-page {
  --cv-accent: var(--accent-color, #2563eb);
  --cv-accent-light: #eef2ff;
  --cv-accent-dark: #1e40af;
  --cv-text: #1f2937;
  --cv-text-light: #6b7280;
  --cv-border: #e5e7eb;

  font-family: 'Roboto', 'Arial', sans-serif;
  font-size: 10pt;
  line-height: 1.15;
  color: var(--cv-text);
  display: grid;
  grid-template-columns: 38% 62%;
  grid-template-rows: auto 1fr;
  gap: 0;
  padding: 0 !important;
  min-height: 297mm;
  background: white;
  overflow: hidden;
}

/* Header - Full Width */
.cv-header {
  grid-column: 1 / -1;
  background: var(--cv-accent);
  color: white;
  padding: 12mm 15mm;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-sizing: border-box;
  /* Fix subpixel gap on right edge */
  position: relative;
}

.cv-header::after {
  content: "";
  position: absolute;
  top: 0;
  right: -5px;
  bottom: 0;
  width: 10px;
  background: var(--cv-accent);
}

.cv-header-left {
  display: flex;
  flex-direction: column;
  gap: 4pt;
}

.cv-name {
  font-size: 20pt;
  font-weight: 700;
  letter-spacing: 0.5pt;
}

.cv-title {
  font-size: 11pt;
  font-weight: 400;
  opacity: 0.9;
}

.cv-header-right {
  text-align: right;
}

.cv-contact {
  display: flex;
  flex-direction: column;
  gap: 4pt;
  font-size: 9pt;
}

.cv-contact-item {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6pt;
}

.cv-contact a {
  color: white;
  text-decoration: underline;
  text-underline-offset: 2pt;
}

.cv-contact a::after {
  color: rgba(255, 255, 255, 0.85) !important;
}

.cv-contact a:hover {
  opacity: 0.9;
}

/* Left Column */
.cv-column-left {
  background: var(--cv-accent-light);
  padding: 12mm 10mm;
  display: flex;
  flex-direction: column;
  gap: 14pt;
}

/* Right Column */
.cv-column-right {
  padding: 12mm 15mm 12mm 10mm;
  display: flex;
  flex-direction: column;
  gap: 14pt;
}

/* Section Titles */
.cv-section {
  margin-bottom: 0;
}

.cv-section-title {
  font-size: 10pt;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1pt;
  color: var(--cv-accent-dark);
  border-bottom: 2pt solid var(--cv-accent);
  padding-bottom: 4pt;
  margin-bottom: 8pt;
}

.cv-column-left .cv-section-title {
  color: var(--cv-accent-dark);
  border-bottom-color: var(--cv-accent);
}

/* Summary */
.cv-summary {
  font-size: 10pt;
  line-height: 1.5;
  color: var(--cv-text);
  text-align: justify;
}

/* Skills */
.cv-skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5pt;
}

.cv-skill-tag {
  display: inline-block;
  padding: 3pt 8pt;
  background: white;
  border: 1pt solid var(--cv-accent);
  border-radius: 3pt;
  font-size: 8pt;
  color: var(--cv-accent-dark);
}

.cv-skill-tag.highlight {
  background: var(--cv-accent);
  color: white;
  border-color: var(--cv-accent);
}

/* Skills with level */
.cv-skill-item {
  display: flex;
  flex-direction: column;
  gap: 2pt;
  margin-bottom: 6pt;
}

.cv-skill-name {
  font-size: 9pt;
  font-weight: 500;
  color: var(--cv-text);
}

.cv-skill-bar {
  height: 4pt;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 2pt;
  overflow: hidden;
}

.cv-skill-level {
  height: 100%;
  background: var(--cv-accent);
  border-radius: 2pt;
}

/* Languages */
.cv-languages-list {
  display: flex;
  flex-direction: column;
  gap: 4pt;
}

.cv-language-item {
  display: flex;
  justify-content: space-between;
  font-size: 9pt;
  padding: 3pt 0;
  border-bottom: 1pt dotted var(--cv-border);
}

.cv-language-item:last-child {
  border-bottom: none;
}

.cv-language-name {
  font-weight: 500;
}

.cv-language-level {
  color: var(--cv-text-light);
}

/* Soft Skills */
.cv-soft-skills-list {
  display: flex;
  flex-direction: column;
  gap: 4pt;
}

.cv-soft-skill {
  font-size: 9pt;
  padding: 4pt 8pt;
  background: white;
  border-radius: 3pt;
  text-align: center;
}

/* Experience */
.cv-experience-item {
  margin-bottom: 12pt;
  padding-bottom: 10pt;
  border-bottom: 1pt solid var(--cv-border);
  page-break-inside: avoid;
}

.cv-experience-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.cv-experience-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2pt;
}

.cv-experience-title {
  font-size: 11pt;
  font-weight: 600;
  color: var(--cv-text);
}

.cv-experience-date {
  font-size: 8pt;
  color: white;
  background: var(--cv-accent);
  padding: 2pt 6pt;
  border-radius: 3pt;
  white-space: nowrap;
}

.cv-experience-company {
  font-size: 10pt;
  color: var(--cv-accent);
  margin-bottom: 4pt;
}

.cv-experience-location {
  color: var(--cv-text-light);
  font-weight: 400;
}

.cv-experience-description {
  font-size: 9pt;
  color: var(--cv-text-light);
  font-style: italic;
  margin-bottom: 4pt;
}

.cv-experience-achievements {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

.cv-experience-achievements li {
  position: relative;
  padding-left: 12pt;
  margin-bottom: 3pt;
  font-size: 9pt;
  line-height: 1.4;
}

.cv-experience-achievements li::before {
  content: "\\25AA";
  position: absolute;
  left: 0;
  color: var(--cv-accent);
}

/* Education */
.cv-education-item {
  margin-bottom: 8pt;
}

.cv-education-item:last-child {
  margin-bottom: 0;
}

.cv-education-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.cv-education-degree {
  font-size: 10pt;
  font-weight: 600;
  color: var(--cv-text);
}

.cv-education-year {
  font-size: 9pt;
  color: var(--cv-accent);
  font-weight: 600;
}

.cv-education-institution {
  font-size: 9pt;
  color: var(--cv-text-light);
}

.cv-education-honors {
  font-size: 8pt;
  color: var(--cv-accent);
  font-style: italic;
}

/* Certifications */
.cv-certifications-list {
  display: flex;
  flex-direction: column;
  gap: 4pt;
}

.cv-certification-item {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 9pt;
  padding: 4pt 0;
}

.cv-certification-name {
  font-weight: 500;
}

.cv-certification-issuer {
  color: var(--cv-text-light);
  font-size: 8pt;
}

/* Projects */
.cv-project-item {
  margin-bottom: 8pt;
}

.cv-project-item:last-child {
  margin-bottom: 0;
}

.cv-project-name {
  font-size: 10pt;
  font-weight: 600;
}

.cv-project-name a {
  color: var(--cv-accent);
  text-decoration: none;
}

.cv-project-description {
  font-size: 9pt;
  color: var(--cv-text-light);
  margin-top: 2pt;
}

/* Utility */
.cv-section.hidden {
  display: none;
}

/* Print */
@media print {
  .cv-page {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  .cv-header {
    background: var(--cv-accent) !important;
  }

  .cv-column-left {
    background: var(--cv-accent-light) !important;
  }
}
"""

# ---------------------------------------------------------------------------
# Template: Creative (Timeline)
# ---------------------------------------------------------------------------

CREATIVE_CSS = """\
/* ============================================
   Template: Creative
   Compatibilite ATS: 2/5
   Structure: Layout moderne avec timeline
   ============================================ */

:root {
  --page-bg: #1e40af;
}

.cv-page {
  --cv-accent: var(--accent-color, #2563eb);
  --cv-accent-light: #eff6ff;
  --cv-accent-dark: #1e40af;
  --cv-gradient: linear-gradient(135deg, var(--cv-accent) 0%, var(--cv-accent-dark) 100%);
  --cv-text: #1f2937;
  --cv-text-light: #6b7280;
  --cv-border: #e5e7eb;

  font-family: 'Inter', 'Roboto', sans-serif;
  font-size: 10pt;
  line-height: 1.15;
  color: var(--cv-text);
  padding: 0 !important;
  overflow: visible;
  min-height: 297mm;
  display: block;
  position: relative;
  /* Background pour la colonne de droite qui s'etend sur toutes les pages */
  background: linear-gradient(to right, white 65%, #f8fafc 65%);
}

/* Bordure de separation entre main et aside - s'etend sur toute la hauteur */
.cv-page::after {
  content: "";
  position: absolute;
  top: 0;
  left: 65%;
  bottom: 0;
  width: 3pt;
  background: var(--cv-accent-light);
  z-index: 0;
}

/* Header - Hero Style */
.cv-header {
  background: var(--cv-gradient);
  color: white;
  padding: 8mm 12mm 10mm;
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
  /* Fix subpixel gap on right edge */
  box-shadow: 5px 0 0 0 var(--cv-accent-dark);
  /* Passe au-dessus de la bordure de separation */
  z-index: 2;
}

.cv-header::before {
  content: "";
  position: absolute;
  top: -50%;
  right: -10%;
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}

.cv-header-content {
  position: relative;
  z-index: 1;
}

.cv-name {
  font-size: 24pt;
  font-weight: 700;
  letter-spacing: 1pt;
  margin-bottom: 3pt;
}

.cv-title {
  font-size: 11pt;
  font-weight: 300;
  opacity: 0.9;
  text-transform: uppercase;
  letter-spacing: 2pt;
  margin-bottom: 10pt;
}

.cv-contact {
  display: flex;
  flex-wrap: wrap;
  gap: 6pt 20pt;
  font-size: 9pt;
}

.cv-contact-item {
  display: flex;
  align-items: center;
  gap: 6pt;
  opacity: 0.9;
}

.cv-contact-icon {
  width: 14pt;
  height: 14pt;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 8pt;
}

.cv-contact a {
  color: white;
  text-decoration: underline;
  text-underline-offset: 2pt;
}

.cv-contact a::after {
  color: rgba(255, 255, 255, 0.85) !important;
}

.cv-contact a:hover {
  opacity: 0.9;
}

/* Main Content - Table layout pour meilleur support des sauts de page */
.cv-body {
  display: table;
  width: 100%;
  table-layout: fixed;
  position: relative;
  z-index: 1;
}

.cv-main {
  display: table-cell;
  width: 65%;
  padding: 5mm 5mm 10mm 8mm;
  vertical-align: top;
}

.cv-main > .cv-section {
  margin-bottom: 6pt;
}

.cv-aside {
  display: table-cell;
  width: 35%;
  background: transparent; /* Le background est gere par .cv-page */
  padding: 5mm 8mm 10mm 8mm;
  vertical-align: top;
}

.cv-aside > .cv-section {
  margin-bottom: 6pt;
}

/* Section Titles */
.cv-section-title {
  font-size: 10pt;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.5pt;
  color: var(--cv-accent);
  margin-bottom: 6pt;
  display: flex;
  align-items: center;
  gap: 6pt;
}

.cv-section-title::before {
  content: "";
  width: 20pt;
  height: 3pt;
  background: var(--cv-gradient);
  border-radius: 2pt;
}

.cv-aside .cv-section-title {
  font-size: 9pt;
  letter-spacing: 1.5pt;
}

.cv-aside .cv-section-title::before {
  width: 12pt;
  height: 2pt;
}

/* Summary - Quote Style */
.cv-summary {
  font-size: 9pt;
  line-height: 1.4;
  color: var(--cv-text);
  padding: 8pt 12pt;
  background: var(--cv-accent-light);
  border-left: 3pt solid var(--cv-accent);
  border-radius: 0 6pt 6pt 0;
  position: relative;
}

.cv-summary::before {
  content: "\\201C";
  position: absolute;
  top: -5pt;
  left: 8pt;
  font-size: 30pt;
  color: var(--cv-accent);
  opacity: 0.3;
  font-family: Georgia, serif;
}

/* Experience - Timeline */
.cv-experience-list {
  position: relative;
  padding-left: 15pt;
}

.cv-experience-list::before {
  content: "";
  position: absolute;
  left: 4pt;
  top: 8pt;
  bottom: 8pt;
  width: 2pt;
  background: linear-gradient(to bottom, var(--cv-accent), var(--cv-accent-light));
  border-radius: 1pt;
}

.cv-experience-item {
  position: relative;
  margin-bottom: 10pt;
  padding-left: 10pt;
  page-break-inside: avoid;
}

.cv-experience-item:last-child {
  margin-bottom: 0;
}

.cv-experience-item::before {
  content: "";
  position: absolute;
  left: -15pt;
  top: 6pt;
  width: 10pt;
  height: 10pt;
  background: white;
  border: 2pt solid var(--cv-accent);
  border-radius: 50%;
}

.cv-experience-header {
  margin-bottom: 4pt;
}

.cv-experience-title {
  font-size: 11pt;
  font-weight: 600;
  color: var(--cv-text);
  display: block;
}

.cv-experience-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2pt;
}

.cv-experience-company {
  font-size: 10pt;
  color: var(--cv-accent);
  font-weight: 500;
}

.cv-experience-date {
  font-size: 8pt;
  color: var(--cv-text-light);
  background: var(--cv-accent-light);
  padding: 2pt 8pt;
  border-radius: 10pt;
}

.cv-experience-location {
  color: var(--cv-text-light);
  font-weight: 400;
  font-size: 9pt;
}

.cv-experience-description {
  font-size: 9pt;
  color: var(--cv-text-light);
  font-style: italic;
  margin: 4pt 0;
}

.cv-experience-achievements {
  list-style: none;
  padding: 0;
  margin: 6pt 0 0 0;
}

.cv-experience-achievements li {
  position: relative;
  padding-left: 14pt;
  margin-bottom: 2pt;
  font-size: 9pt;
  line-height: 1.3;
}

.cv-experience-achievements li::before {
  content: "\\2192";
  position: absolute;
  left: 0;
  color: var(--cv-accent);
  font-weight: bold;
}

/* Skills - Tags Cloud */
.cv-skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5pt;
}

.cv-skill-tag {
  display: inline-block;
  padding: 4pt 10pt;
  background: white;
  border: 1pt solid var(--cv-border);
  border-radius: 15pt;
  font-size: 8pt;
  color: var(--cv-text);
  transition: all 0.2s;
}

.cv-skill-tag.highlight {
  background: var(--cv-accent);
  color: white;
  border-color: var(--cv-accent);
}

/* Skills with progress */
.cv-skill-item {
  margin-bottom: 8pt;
}

.cv-skill-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 3pt;
}

.cv-skill-name {
  font-size: 9pt;
  font-weight: 500;
}

.cv-skill-percent {
  font-size: 8pt;
  color: var(--cv-text-light);
}

.cv-skill-bar {
  height: 5pt;
  background: var(--cv-border);
  border-radius: 3pt;
  overflow: hidden;
}

.cv-skill-level {
  height: 100%;
  background: var(--cv-gradient);
  border-radius: 3pt;
}

/* Languages - Dots */
.cv-languages-list {
  display: flex;
  flex-direction: column;
  gap: 6pt;
}

.cv-language-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cv-language-name {
  font-size: 9pt;
  font-weight: 500;
}

.cv-language-dots {
  display: flex;
  gap: 3pt;
}

.cv-language-dot {
  width: 8pt;
  height: 8pt;
  border-radius: 50%;
  background: var(--cv-border);
}

.cv-language-dot.filled {
  background: var(--cv-accent);
}

.cv-language-level {
  font-size: 8pt;
  color: var(--cv-text-light);
}

/* Soft Skills - Pills */
.cv-soft-skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4pt;
}

.cv-soft-skill {
  font-size: 8pt;
  padding: 4pt 10pt;
  background: var(--cv-accent-light);
  color: var(--cv-accent-dark);
  border-radius: 12pt;
}

/* Education - Cards */
.cv-education-item {
  background: white;
  padding: 6pt 8pt;
  border-radius: 6pt;
  margin-bottom: 6pt;
  box-shadow: 0 1pt 3pt rgba(0, 0, 0, 0.08);
}

.cv-education-item:last-child {
  margin-bottom: 0;
}

.cv-education-degree {
  font-size: 10pt;
  font-weight: 600;
  color: var(--cv-text);
}

.cv-education-institution {
  font-size: 9pt;
  color: var(--cv-text-light);
  margin-top: 2pt;
}

.cv-education-year {
  font-size: 8pt;
  color: var(--cv-accent);
  font-weight: 600;
  margin-top: 4pt;
}

/* Certifications */
.cv-certification-item {
  display: flex;
  align-items: center;
  gap: 8pt;
  padding: 6pt 0;
  border-bottom: 1pt solid var(--cv-border);
}

.cv-certification-item:last-child {
  border-bottom: none;
}

.cv-certification-badge {
  width: 24pt;
  height: 24pt;
  background: var(--cv-accent-light);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10pt;
  color: var(--cv-accent);
}

.cv-certification-info {
  flex: 1;
}

.cv-certification-name {
  font-size: 9pt;
  font-weight: 500;
}

.cv-certification-issuer {
  font-size: 8pt;
  color: var(--cv-text-light);
}

/* Projects */
.cv-project-item {
  margin-bottom: 10pt;
  padding-bottom: 8pt;
  border-bottom: 1pt dashed var(--cv-border);
}

.cv-project-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.cv-project-name {
  font-size: 10pt;
  font-weight: 600;
}

.cv-project-name a {
  color: var(--cv-accent);
  text-decoration: none;
}

.cv-project-name a:hover {
  text-decoration: underline;
}

.cv-project-description {
  font-size: 9pt;
  color: var(--cv-text-light);
  margin-top: 3pt;
}

/* Utility */
.cv-section.hidden {
  display: none;
}

/* Print */
@media print {
  .cv-page {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    background: linear-gradient(to right, white 65%, #f8fafc 65%) !important;
  }

  .cv-header {
    background: var(--cv-gradient) !important;
    position: relative;
    z-index: 2 !important;
  }

  .cv-page::after {
    z-index: 0 !important;
  }

  .cv-skill-level {
    background: var(--cv-accent) !important;
  }

  /* Pas de marges @page - le design gere ses propres marges */
  @page {
    margin: 0 !important;
  }

  /* Gestion des sauts de page */
  .cv-section {
    page-break-inside: auto;
    break-inside: auto;
  }

  .cv-experience-item,
  .cv-education-item,
  .cv-project-item {
    page-break-inside: avoid;
    break-inside: avoid;
  }

  .cv-section-title {
    page-break-after: avoid;
    break-after: avoid;
  }
}
"""

# ---------------------------------------------------------------------------
# Template registry
# ---------------------------------------------------------------------------

_TEMPLATES = {
    "classic": CLASSIC_CSS,
    "modern-sidebar": MODERN_SIDEBAR_CSS,
    "two-column": TWO_COLUMN_CSS,
    "creative": CREATIVE_CSS,
}


def get_full_css(template: str, color: str) -> str:
    """Return the combined CSS for *template* with *color* as accent.

    Parameters
    ----------
    template:
        One of ``"classic"``, ``"modern-sidebar"``, ``"two-column"``,
        ``"creative"``.
    color:
        A CSS colour value (e.g. ``"#2563eb"``, ``"#10b981"``).

    Returns
    -------
    str
        The base CSS followed by the template CSS, with all occurrences of
        ``var(--accent-color, #2563eb)`` replaced by the literal *color*.
    """
    tpl_css = _TEMPLATES.get(template)
    if tpl_css is None:
        raise ValueError(
            f"Unknown template {template!r}. "
            f"Choose from: {', '.join(sorted(_TEMPLATES))}"
        )

    combined = CV_BASE_CSS + "\n" + tpl_css
    combined = combined.replace("var(--accent-color, #2563eb)", color)
    return combined
