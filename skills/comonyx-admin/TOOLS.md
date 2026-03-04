# TOOLS.md – Email (including attachments) for comonyx-admin

This skill sends email using the **script in this skill** at `scripts/send-email.py`. The script reads SMTP and sender settings from a **`.env` file** in the skill root (same folder as this TOOLS.md). It also supports an optional **attachment** via `ATTACHMENT_PATH` (e.g. the generated PDF or Excel file).

**Setup:** Copy `.env.example` to `.env` in this skill root and set `SMTP_USERNAME`, `SMTP_PASSWORD`, and optionally `SMTP_HOST`, `SMTP_PORT`, `SMTP_DEFAULT_EMAIL`, `SMTP_DEFAULT_NAME`. The script loads `.env` automatically when run.

**Agent:** When the user asks to email an exported file (or you offer and they accept), obtain the recipient address and set `EMAIL_TO` and `ATTACHMENT_PATH` in the command (these are usually not in .env because they change per request). Resolve **&lt;skill-dir&gt;** to the absolute path of the directory that contains this TOOLS.md (the comonyx-admin skill root).

## Sending the exported file (PDF or Excel) to a recipient

1. Ensure the export file exists at the path you reported (e.g. `$HOME/Downloads/comonyx-companies.pdf` or `$HOME/Downloads/comonyx-companies.xlsx`).
2. Write a short body to the body file (required by the script):
   ```bash
   echo "Cosmonyx companies export attached." > /tmp/companies_body.txt
   ```
3. Run the send command. **Agent:** Replace `<recipient>` with the email address from the user, `<path-to-file>` with the actual export path (e.g. `/home/musawir/Downloads/comonyx-companies.pdf`), and `<skill-dir>` with the comonyx-admin skill directory path. If `.env` exists in the skill root, you only need to pass `EMAIL_TO` and `ATTACHMENT_PATH` in the command; SMTP_* can be omitted (read from .env).

**One-line command** (run in a single exec; SMTP vars are read from .env if present, otherwise set them here):

```bash
export EMAIL_TO='<recipient>' ATTACHMENT_PATH='<path-to-file>' && echo "Cosmonyx companies export attached." > /tmp/companies_body.txt && cd "<skill-dir>/scripts" && python3 send-email.py /tmp/companies_body.txt
```

If `.env` is not set up, use the full export (all variables) as before:

```bash
export SMTP_HOST=in-v3.mailjet.com SMTP_USERNAME=... SMTP_PASSWORD=... SMTP_PORT=587 SMTP_DEFAULT_EMAIL=... SMTP_DEFAULT_NAME=IdentityGram EMAIL_TO='<recipient>' ATTACHMENT_PATH='<path-to-file>' && echo "Cosmonyx companies export attached." > /tmp/companies_body.txt && cd "<skill-dir>/scripts" && python3 send-email.py /tmp/companies_body.txt
```

## Variable reference

| Variable             | Description | Where |
|----------------------|-------------|--------|
| `SMTP_HOST`          | SMTP server (e.g. Mailjet) | .env or export |
| `SMTP_USERNAME`      | SMTP API key / user | .env or export |
| `SMTP_PASSWORD`      | SMTP secret / password | .env or export |
| `SMTP_PORT`          | Use `587` | .env or export |
| `SMTP_DEFAULT_EMAIL` | Sender email | .env or export |
| `SMTP_DEFAULT_NAME`  | Sender name | .env or export |
| `EMAIL_TO`           | Recipient. **Agent:** Set to the address from the user. | export (per request) |
| `ATTACHMENT_PATH`    | Full path to PDF or Excel to attach. **Agent:** Set to the export path. | export (per request) |

Values in the exec command override values from `.env`. If send fails (e.g. connection refused), report the error and suggest checking `.env` or SMTP_* and `SMTP_PORT=587`.
