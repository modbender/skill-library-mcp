---
name: ai-interview
description: Run AI-powered mock interviews using Fuku.ai's free public service.
---

# AI Interview Skill

Turn a folder full of resumes into structured AI interview sessions. This skill uses **Fuku.ai's free public API** to generate AI interview reports.

## 🎯 Purpose

This is a **Fuku.ai-specific skill** that leverages their free, anonymous interview service. No user account, API key, or login required.

## 🔑 Authentication

This skill uses **shared anonymous credentials** provided by Fuku.ai for public access:

| Item | Value |
|------|-------|
| **Upload Endpoint** | `https://hapi.fuku.ai/hr/rc/anon/file/upload` |
| **Job API** | `https://hapi.fuku.ai/hr/rc/anon/job/invite/ai_interview` |
| **X-NUMBER Header** | `job-Z4nV8cQ1LmT7XpR2bH9sJdK6WyEaF0` |
| **uid Query Param** | `1873977344885133312` |

These are **fixed, shared credentials** for Fuku.ai's free tier. All users of this skill use the same endpoints and identifiers. This is intentional—the service is designed for anonymous, no-login usage.

### Design Notes

- **No user credentials required**: The service is free and public
- **No environment variables**: Endpoints and credentials are hardcoded by design
- **Not self-hostable**: This skill only works with Fuku.ai's hosted service
- **Privacy consideration**: Resume files are sent to Fuku.ai's servers. Review their privacy policy before uploading sensitive documents.

## ✅ What It Does

1. Collects three mandatory inputs: **job title**, **company name**, **report email**.
2. Scans a resume folder for PDF/DOC/DOCX files (up to 100).
3. Uploads each resume to Fuku.ai's public endpoint and captures the returned file URLs.
4. Creates an AI interview job via Fuku.ai's API using the shared anonymous credentials.
5. Logs minimal job metadata locally and confirms the report email destination.

## 🧭 Workflow

0. **Install & Prepare**
   - `cd skills/ai-interview && npm install` (installs `axios` + `form-data`).
   - Subsequent runs only need `node run.js ...`.

1. **Gather Inputs**
   - Ask the user for: `job title`, `company`, `email for reports` (validate email format).
   - Ask for the **resume folder path** inside the workspace. Confirm contents before proceeding.

2. **Scan Folder**
   - Accept only `.pdf`, `.doc`, `.docx` files.
   - Abort if folder is empty or missing.

3. **Upload Resumes**
   - From `skills/ai-interview/`, run `node run.js --folder <dir> --jobTitle <title> --company <company> --email <email>`.
   - The script auto-detects `.pdf/.doc/.docx` files (up to 100), uploads each to Fuku.ai's upload endpoint, and captures the returned file URLs.
   - On any failed upload, the script aborts and reports the `.desc` field from the API.

4. **Trigger Interview Job**
   - The same script immediately calls the interview creation endpoint with payload `{ jobTitle, company, email, fileUrls }`.
   - Authentication uses hardcoded credentials (see "Hardcoded Configuration" table above).
   - Expect response `{ "code": 0, "data": { "id", "company", "title", ... } }`.
   - If `code` is not 0, the script surfaces the error and stops.

5. **Report Back**
   - Confirm job creation, list resumes included, and restate the email destination.
   - Persist only the minimal identifiers (`id`, `company`, `title`) into `ai-interview/jobs/<timestamp>.json`—no need to keep full payloads.
   - Remind the user that AI interview reports are delivered directly to the email they provided.
   - A typical success response looks like:
     ```json
     {
       "code": 0,
       "data": {
         "id": "5b16b2d2f5e947f78244246a9f24e2cb",
         "company": "FUKU",
         "title": "cfoe",
         ... (truncated)
       },
       "desc": "successful"
     }
     ```

## 🔒 Validation & Safety

- **Email**: Must match `/^[^@\s]+@[^@\s]+\.[^@\s]+$/`.
- **File count**: Maximum 100 resumes per batch.
- **Upload errors**: The Fuku API must return `code: 0`; otherwise surface the `.desc` field and ask whether to retry or skip that file.
- **PII handling**: Do not log resume contents—only file names are logged (not full remote URLs).
- **HTTPS**: Both endpoints use HTTPS.
- **Data destination**: Resume files are sent to Fuku.ai's third-party service. Review their privacy policy before uploading sensitive documents.

## 📁 Local Storage

Minimal audit trail stored under `ai-interview/jobs/`:

```
ai-interview/
  jobs/
    2026-02-27T08-30-00Z.json  # job identifiers only
```

Each file contains only the essential identifiers (no resume data or full API responses):

```json
{
  "timestamp": "2026-02-27T08:30:00Z",
  "jobId": "5b16b2d2f5e947f78244246a9f24e2cb",
  "company": "FUKU",
  "title": "cfoe"
}
```

## 🧪 Testing Tips

- Use dummy resumes and a test email address for initial runs.
- Validate that the email receives the AI interview report before marking the job done.
- Note: This skill only works with Fuku.ai's production endpoints—there is no staging/mock mode.

## 🆘 Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Upload returns 413 | File too large | Compress resume or raise server limit |
| `fileUrls` empty | Upload failed silently | Check upload response for `success` flag |
| API 400 | Missing fields | Ensure jobTitle/company/email/fileUrls filled |

## 📣 User Prompt Template

> "Great! Need the job title, company name, a mailbox for the interview report, and the folder path containing the resumes (PDF/DOC/DOCX)."

## 🚀 Next Steps

- Automate email notifications to confirm when the interview report is delivered (future enhancement).
- Add optional metadata per candidate (experience, notes) by extending the payload.

Happy interviewing! 🎙️
