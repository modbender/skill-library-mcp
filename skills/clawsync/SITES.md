# Sites Documentation

This file documents all Nick's projects for QA and maintenance.

---

**Last Updated:** 2026-02-22

### Last QA Check: 2026-02-22
- ✅ All homepages loading (200 OK)
- ✅ UK Tutors: search/list page functional
- ✅ UK Tutors Supabase: tutors endpoint returning data (3 sample tutors)
- ✅ ExamPulse: quiz page functional
- ✅ Personal Blog: blog page functional

### Pages
| Page | File | Status |
|------|------|--------|
| Home | index.html | ✅ |
| For Tutors | list.html | ✅ |
| Blog | blog/ | ✅ |

### Functionality
- ✅ Search tutors by subject, location, level
- ✅ Tutor cards with ratings, subjects, price
- ✅ Contact form → Supabase leads table
- ✅ PostHog analytics tracking

### Data
- Supabase: araqigsimkjsmwhnjesv
- Tables: tutors, leads
- **API Key (updated 2026-02-19):** `REDACTED_BY_SECURITY_POLICY`

### Skills
- /skills/uk-tutors-marketing/SKILL.md
- /skills/outscraper/SKILL.md

### Marketing Docs
- /uk-tutors-marketing/personas.md
- /uk-tutors-marketing/lead-magnets.md
- /uk-tutors-marketing/site-analysis.md
- /uk-tutors-marketing/campaign-strategy.md

---

## 2. ExamPulse Marketing

**URL:** https://nickconstantinou.github.io/exam-pulse-marketing/
**Repo:** nickconstantinou/exam-pulse-marketing
**Last Updated:** 2026-02-18

### Pages
| Page | File | Status |
|------|------|--------|
| Home | index.html | ✅ |
| Quiz | quiz.html | ✅ |
| Grade Calculator | grade-calculator.html | ✅ |
| Gap Diagnostic | gap-diagnostic.html | ✅ |
| Blog | blog.html | ✅ |
| Blog Posts | blog/*.html | ✅ |

### Functionality
- ✅ A/B testing with PostHog
- ✅ Lead capture forms
- ✅ Quiz flow
- ✅ Grade calculator
- ✅ SEO optimized

### Skills
- /skills/marketing/* (multiple)

---

## 3. Personal Blog (Dashboard)

**URL:** https://nickconstantinou.github.io/dashboard/
**Repo:** nickconstantinou/dashboard
**Last Updated:** 2026-02-18

### Pages
| Page | File | Status |
|------|------|--------|
| Home | index.html | ✅ |
| Blog | blog.html | ✅ |
| Training | training.html | ✅ |
| Sources | sources.html | ✅ |
| Changelog | changelog.html | ✅ |

### Functionality
- ✅ Content from crawled sources
- ✅ Blog posts with frontmatter

### Cron Jobs
- Daily 7am: Content crawler
- Daily 7am: FPL digest

---

## 4. ExamPulse App

**Repo:** nickconstantinou/exam-pulse
**Branch:** feature/frontend-vibe-shift (PR #4)

### Status
- PR #4 ready to merge
- Tests have pre-existing failures

---

## QA Checkpoints

When updating any site:
1. Verify deployment (curl/screenshot)
2. Check all links work
3. Test search/forms
4. Update this doc
5. Commit with descriptive message
