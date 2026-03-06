---
name: comonyx-admin
description: Admin skill to sign into Cosmonyx, fetch companies, filter/export (PDF or Excel), optionally email the export, or send reminder emails to filtered companies.
metadata: {"openclaw":{"emoji":"🛠️"}}
---

# Cosmonyx Admin – Sign in, Fetch Companies, Export as PDF or Excel

This skill lets an **admin** sign in to Cosmonyx, fetch **all company records** using the same endpoints as the Cosmonyx gateway API, then choose to export those records as **PDF** or **Excel**, or send reminder emails. Email is sent by this skill’s own script (`scripts/send-email.py`); see TOOLS.md.

You must run all HTTP requests yourself (no external repos). For structured config (endpoints, run order) you can also load **SKILL.yaml** from this directory if present, but this SKILL.md is the source of truth for behavior.

---

## Step 0 – Prompt for admin credentials

Before calling any API:

- **Ask once**:  
  - "Please provide your **Cosmonyx admin email**."  
  - "Please provide your **Cosmonyx admin password**."
- Do **not** echo the password back in any reply. Treat it as sensitive.
- Use the provided email/password as the sign-in payload.

If the user has already given both an email and password in their initial request, reuse those and do not ask again.

---

## Step 1 – Sign in (admin)

- **POST** `https://gateway-dev.cosmonyx.co/auth/signin`
- **Headers:** `Content-Type: application/json`
- **Body:** JSON with the admin credentials you obtained in Step 0, e.g.:
  - `{"email":"<ADMIN_EMAIL>","password":"<ADMIN_PASSWORD>"}`
- From the response, take the auth token from whichever field exists first:
  - `accessToken`, `token`, `data.token`, or `data.accessToken`
- Keep this token **in memory only** and **never print it** in any reply.

If sign-in fails (4xx/5xx or missing token), stop, explain the error briefly, and ask the user to correct the credentials instead of proceeding.

---

## Step 2 – Fetch all company records

- **GET** `https://gateway-dev.cosmonyx.co/companies`
- **Headers:** `Authorization: Bearer <TOKEN>` where `<TOKEN>` is from Step 1.
- Fetch the **full** list of companies. If the API is paginated:
  - Detect pagination from response fields like `page`, `totalPages`, `links.next`, etc.
  - Request **all pages** until there are no more, concatenating results.
- The list may be in:
  - `data`, `companies`, or the root.
- Extract the **complete list of company objects** into an in-memory structure (array of objects).

If there are zero companies, still continue to the export choice but clearly state that the dataset is empty.

---

## Step 3 – Choose action on the records

After fetching all companies, **prompt the admin** to choose what they want to do:

> "What would you like to do with the Cosmonyx company records?  
> 1) List records where complianceStatus is `Not Started`  
> 2) List records with `riskType` = `Low`  
> 3) List records where the primary user’s `sumsubVerificationStatus` is `under_review`  
> 4) Send reminder emails to records where `complianceStatus` is `Not Started`  
> 5) Send reminder emails to records whose `expiryDate` is before a given date  
> 6) Work with **all** records (no filter)"

### Step 3A – Filtering logic

Apply filters in memory over the full company list from Step 2:

- **Option 1:** compliance not started  
  - Filter: `company.complianceStatus === "Not Started"`.
- **Option 2:** low risk  
  - Filter: `company.riskType === "Low"`.
- **Option 3:** KYC under review  
  - Filter: `company.primaryUser?.sumsubVerificationStatus === "under_review"`.
- **Option 4:** compliance not started (for email)  
  - Same filter as option 1.
- **Option 5:** expiry date before a given date  
  - Ask once: "Please provide a cutoff date (YYYY-MM-DD). Records with `expiryDate` earlier than this date will be selected."  
  - Parse the cutoff into a date and filter records where `expiryDate` is non-null and `< cutoff`.
- **Option 6:** all records  
  - No extra filter; use the full dataset.

If the filter results in zero records, report that to the user and stop (no export and no emails).

### Step 3B – Branching: export vs email

- If the admin chose **1, 2, 3, or 6**, proceed to **Step 4 – Export filtered records (PDF or Excel)**.
- If the admin chose **4 or 5**, proceed to **Step 5 – Send reminder emails to the filtered companies**.

---

## Step 4 – Export filtered records (PDF or Excel)

### Step 4A – Ask export format (PDF vs Excel)

For actions 1, 2, 3, or 6, after filtering:

> "I selected N matching companies. How would you like to export these records?  
> 1) PDF file  
> 2) Excel (.xlsx) file"

Interpret the user’s reply:

- If they answer with "1", "pdf", or similar → choose **PDF**.
- If they answer with "2", "excel", "xlsx", or similar → choose **Excel**.
- If unclear, ask once for clarification and then proceed.

### Step 4B – Generate PDF file (if user chose PDF)

If the user selected **PDF**:

- Create a PDF file summarizing all **filtered** company records (not the full list).
- At minimum, include a table or clearly formatted list with columns such as:
  - `id`, `name`, `status`, `country`, and any other key fields returned.
- Save the file into the current user’s **Downloads** folder so it appears in your normal download location, e.g.:
  - `$HOME/Downloads/comonyx-companies.pdf`
- Ensure the file contains **all** filtered companies from Step 3 (not truncated).

When done, reply with:

1. A short confirmation that admin sign-in succeeded.
2. A brief summary of how many companies were selected by the filter.
3. The **path and name** of the generated PDF file (e.g. `$HOME/Downloads/comonyx-companies.pdf`) so the user (or tools) can retrieve it.

Then proceed to **Step 4D – Optional: Email the exported file**.

Do not ask what to do next.

---

### Step 4C – Generate Excel file (if user chose Excel)

If the user selected **Excel**:

- Create an Excel `.xlsx` file listing all **filtered** company records in a sheet named `Companies`.
- Include columns for key fields such as:
  - `id`, `name`, `status`, `country`, `email`, and any other important fields present in the API response.
- Each company should be one row.
- Save the file into the current user’s **Downloads** folder:
  - `$HOME/Downloads/comonyx-companies.xlsx`
- Ensure the file contains **all** filtered companies from Step 3.

When done, reply with:

1. A short confirmation that admin sign-in succeeded.
2. A brief summary of how many companies were selected by the filter.
3. The **path and name** of the generated Excel file (e.g. `$HOME/Downloads/comonyx-companies.xlsx`).

Then proceed to **Step 4D – Optional: Email the exported file**.

Do not ask what to do next.

---

### Step 4D – Optional: Email the exported file (PDF or Excel)

After Step 4B or 4C (once the export file path is known):

1. **Ask once:** "Would you like this file emailed to someone? If yes, provide the email address." If the user says no or does not provide an address, skip sending and go to the final reply (Step "Reply format").
2. If the user **provides an email address**:
   - Use **TOOLS.md** in this skill directory. Set `EMAIL_TO` to the address they gave and `ATTACHMENT_PATH` to the **exact path** of the generated file (e.g. `$HOME/Downloads/comonyx-companies.pdf` or `$HOME/Downloads/comonyx-companies.xlsx`). Expand `$HOME` to the actual home path if needed (e.g. `/home/musawir`).
   - Write the body file: `echo "Cosmonyx companies export attached." > /tmp/companies_body.txt`
   - Run the one-line send command from TOOLS.md in a single **exec** (with `EMAIL_TO` and `ATTACHMENT_PATH` set). Use the script in **this skill’s** `scripts/send-email.py` (TOOLS.md uses `<skill-dir>` for the path; resolve that to this skill’s directory).
   - If send succeeds, confirm in your final reply: "The export was emailed to \<address\>."
   - If send fails, report the error and still mention where the file was saved.

Do not ask what to do next after sending (or after declining).

---

## Step 5 – Send reminder emails to filtered companies (options 4 and 5)

If the admin chose **option 4 or 5** in Step 3:

1. Use the filtered list from Step 3A.
2. For each company, determine the email recipient:
   - Prefer `company.email` if non-empty.
   - Otherwise use `company.primaryUser?.email` if present.
   - Skip records that have **no email at all**.
3. Ask the admin once for:
   - The **email subject**, e.g. "Compliance onboarding reminder".
   - The **email body template**, which may include placeholders like `{companyName}`, `{status}`, `{expiryDate}` – you can do simple string replacements for these placeholders per company.
4. For each selected company with a recipient address:
   - Fill in the template with that company’s values.
   - Write the final body to a temp file (e.g. `/tmp/comonyx-admin-email-body.txt`).
   - Use the email script in **this skill’s** `scripts/send-email.py` and the SMTP/recipient settings in this skill’s **TOOLS.md**. Set `EMAIL_TO` to that company’s recipient address (and no attachment for reminder emails) before running the send command.
5. Keep track of how many emails were successfully attempted vs skipped (no email address).

If sending fails due to SMTP issues, report the error and remind the user to configure SMTP_* environment variables (host, port, user, password).

---

## Reply format (final response)

After completing the chosen action (export or sending emails), send **one final reply** that includes:

1. **Sign-in result** – e.g. "Signed in to Cosmonyx as admin successfully."
2. **Filter summary** – what option was chosen and how many companies matched (e.g. "Selected 24 companies where complianceStatus is Not Started.").
3. **Outcome**:
   - For exports:  
     - PDF: "Generated PDF export at `$HOME/Downloads/comonyx-companies.pdf`."  
     - Excel: "Generated Excel export at `$HOME/Downloads/comonyx-companies.xlsx`."
   - If the user asked to email the file and you sent it: "The export was emailed to \<address\>."
   - For reminder emails (options 4/5):  
     - E.g. "Attempted to send reminder emails to 24 companies; 22 emails sent, 2 skipped due to missing email address."

Do not add follow-up offers like "let me know if you need anything else" or questions about next steps. End after confirming the outcome.

