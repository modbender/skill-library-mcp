# TaxClaw — Privacy Policy

**Last updated:** February 22, 2026  
**Effective date:** February 22, 2026  
**Publisher:** Outbranch Network LLC, a New York limited liability company  
**Contact:** lando@outbranch.net

---

## Overview

TaxClaw is designed as a **local-first tool**. Your tax documents and extracted data are processed and stored on your device by default and are not transmitted to Outbranch Network LLC or any third party unless you explicitly enable Cloud Mode.

We do not require accounts. We do not collect analytics. We do not sell your data.

---

## 1. Local Mode (Default)

When you use TaxClaw in **Local Mode** (powered by Ollama running on your device):

**What stays on your machine — always:**
- Your uploaded tax documents (PDFs and images)
- All extracted field values (W-2 boxes, 1099 amounts, K-1 fields, etc.)
- Your TaxClaw database (SQLite, stored in your configured data directory)
- All export files (CSV, JSON) you generate

**What is NEVER transmitted in Local Mode:**
- The contents of your tax documents
- Extracted field values
- Personally identifiable information from your documents (names, SSNs, EINs, account numbers, dollar amounts)
- Metadata about your documents
- Your IP address or device identifier (TaxClaw has no telemetry, no analytics, no phone-home)

**AI processing in Local Mode:**  
All AI extraction is performed by Ollama, running entirely on your local machine. No document data leaves your device during extraction.

**No accounts required:**  
TaxClaw does not require user accounts, email addresses, or registration of any kind. We maintain no user database.

---

## 2. Cloud Mode (Optional — Requires Explicit Consent)

If you choose to enable **Cloud Mode** in TaxClaw Settings, excerpts of your tax document data are transmitted to a third-party AI provider (currently Anthropic, Inc.) for processing via their API.

**Before enabling Cloud Mode, you must:**
- Affirmatively acknowledge the Cloud Mode privacy notice in TaxClaw Settings
- Confirm you understand that document data will leave your device

**What leaves your device when Cloud Mode is enabled:**
- Excerpts of text extracted from your tax documents (field names and values)
- Sent to: **Anthropic, Inc.** (Claude AI API) — `api.anthropic.com`
- Purpose: AI-powered field extraction from your documents

**What Outbranch Network LLC does NOT do with Cloud Mode data:**
- We do not log, store, or retain your document data on our servers
- We do not receive your raw document files — only the API call and response pass through your local TaxClaw instance
- We do not sell, share, or analyze your document content

**Third-party privacy policy:**  
Anthropic's handling of API inputs is governed by Anthropic's Privacy Policy:  
https://www.anthropic.com/privacy

**Recommendation:** For maximum privacy, use Local Mode (Ollama). Local Mode processes everything on your device and transmits nothing.

---

## 3. No Analytics, No Telemetry

TaxClaw does **not** collect:
- Usage analytics or telemetry
- Crash reports (unless you manually share logs with us)
- Performance metrics
- Feature usage data
- Device identifiers or fingerprints
- IP addresses

There is no tracking of any kind built into TaxClaw.

---

## 4. Affiliate Links

TaxClaw's export flow may include links to third-party tax reconciliation services (such as Koinly, CoinTracker, or ZenLedger). These are **affiliate links** — Outbranch Network may earn a referral commission if you sign up through these links at no additional cost to you.

Clicking affiliate links may transmit referral data (such as a referral code or click identifier) to those third-party services. Their privacy policies govern what data they collect. We recommend reviewing each service's privacy policy before signing up.

Affiliate links are clearly disclosed wherever they appear in TaxClaw's interface.

---

## 5. Your Controls

**Delete all data:**  
You can delete any document from TaxClaw using the Delete button on the document detail page. This removes the document record from the database and deletes the stored file from your data directory.

**Export your data:**  
You can export all your extracted data at any time using the Export functions on the Documents list page or individual document pages (CSV or JSON format).

**Wipe everything:**  
To completely remove TaxClaw data, delete your TaxClaw data directory (configured in Settings or config.yaml) and uninstall the application.

**No deletion requests needed:**  
Because TaxClaw stores your data locally on your device, you control deletion entirely yourself. There is no server-side data to request deletion of (in Local Mode).

---

## 6. Children's Privacy

TaxClaw is not directed at children under 13 and is intended for use by adults managing their own tax documents. We do not knowingly collect information from anyone under 13.

---

## 7. Changes to This Policy

If we make material changes to this Privacy Policy (for example, if a future version of TaxClaw adds server-side features), we will update the "Last updated" date above and post the updated policy within the TaxClaw application and on the GitHub repository. We will provide prominent notice for any changes that materially affect how your data is handled.

---

## 8. Contact

For privacy questions or concerns:

**Outbranch Network LLC**  
Email: lando@outbranch.net  
GitHub: https://github.com/DougButdorf/TaxClaw

We will respond to privacy inquiries within a reasonable time.

---

*This Privacy Policy was last reviewed and updated: February 22, 2026.*
