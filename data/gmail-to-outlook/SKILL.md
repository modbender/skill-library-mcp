---
name: gmail-to-outlook
description: "Migrate email, contacts, and calendars from Google Workspace (Gmail) to Microsoft 365 (Outlook/Exchange Online). Use when a user asks to migrate from Gmail to Outlook, transfer emails from Google Workspace to Office 365, export Google Takeout to Outlook, switch from Gmail to Exchange, or plan a Google Workspace to Microsoft 365 migration. Covers: single-user migrations, bulk/org-wide migrations, MBOX imports, calendar + contacts transfer, DNS/MX cutover, and post-migration validation."
---

# Gmail to Outlook Migration

## Migration Paths

Assess the source environment first:

| Source | Best Method | Scope |
|--------|------------|-------|
| Google Workspace | Microsoft Data Migration Service | Org-wide, bulk |
| Google Takeout (MBOX) | Outlook Desktop Import | Per-user |
| Gmail (personal) | IMAP bridge via Outlook Desktop | Per-user |
| G Suite Legacy | Microsoft Migration Tools | Per-user or bulk |

## Pre-Migration Checklist

Run through this with the client before touching anything:

1. **Inventory** — Number of users, total mailbox sizes, largest mailbox, shared mailboxes, Google Groups
2. **Microsoft 365 plan** — Confirm active subscription, verify admin access (Global Admin required)
3. **Source admin access** — Google Workspace Super Admin + service account for bulk migration
4. **DNS access** — Whoever manages MX records (registrar, Cloudflare, etc.)
5. **Data scope** — Email only? +Contacts? +Calendars? +Drive files?
6. **Cutover window** — When to switch MX records (weekend recommended)
7. **Client communication** — Draft email to users about the switch, new login instructions
8. **Retention** — Keep Google Workspace active 30 days post-migration as safety net

## Method 1: Microsoft Data Migration Service (Recommended for Google Workspace)

Best for org-wide migrations from Google Workspace to Microsoft 365.

### Setup

1. Microsoft 365 Admin Center → **Migration** → **Data Migration**
2. Select **Google Workspace** as source
3. Create service account in Google Admin Console with domain-wide delegation
4. Upload service account key file to Microsoft migration tool
5. Select what to migrate: Email, Contacts, Calendars
6. Choose date range filter (optional — migrate only last N months to save time)

### Execution

1. Add users to migrate (CSV upload for bulk: `source_email,destination_email`)
2. Start migration — Microsoft handles delta sync automatically
3. Monitor progress in Admin Center → shows per-user status
4. Migration runs in background — users can keep using Gmail during this phase

### CSV Format

```csv
source_email,destination_email
john@company.com,john@company.onmicrosoft.com
jane@company.com,jane@company.onmicrosoft.com
```

See `references/csv-template.md` for full template with notes.

## Method 2: Google Takeout + Outlook Import

Best for individual users or when bulk migration fails.

### Export from Google

1. Go to Google Takeout: https://takeout.google.com
2. Select **Mail**, **Contacts**, **Calendar**
3. Choose MBOX format for mail (compatible with Outlook)
4. Download archive when ready (can take hours/days for large mailboxes)

### Import to Outlook

1. **Email**: Outlook Desktop → File → Open & Export → Import/Export → Import from MBOX
2. **Contacts**: Import Google CSV to Outlook contacts
3. **Calendar**: Export Google Calendar as ICS, import to Outlook Calendar

**Limitations**: Manual per-user process, requires desktop Outlook, size limits.

## Method 3: IMAP Bridge (Manual / Small Scale)

For personal Gmail accounts or when other methods fail:

1. Enable IMAP in Gmail: Settings → Forwarding and POP/IMAP → Enable IMAP
2. Create app password for Gmail account
3. In Outlook desktop, add Gmail as IMAP account using app password
4. Set up Microsoft 365 account in same Outlook profile
5. Drag-and-drop folders from Gmail IMAP to Microsoft 365 mailbox

## Data Mapping Considerations

| Gmail Feature | Outlook Equivalent | Notes |
|---------------|-------------------|-------|
| Labels | Folders | Multiple labels become copies in folders |
| Google Groups | Distribution Lists | May need manual recreation |
| Google Drive links | OneDrive links | Links break — migrate files separately |
| Gmail filters | Outlook rules | Manual recreation required |
| Hangouts/Chat history | Teams | Not directly migratable |

## DNS / MX Cutover

After migration data is transferred:

1. **Verify domain** in Microsoft 365 Admin Center (TXT record)
2. **Update MX records** to Microsoft:
   ```
   Priority  Host
   0         company-com.mail.protection.outlook.com
   ```
3. **Set SPF**: `v=spf1 include:spf.protection.outlook.com ~all`
4. **Set DKIM**: Admin Center → Defender → Email authentication → Enable DKIM
5. **Set DMARC**: `v=DMARC1; p=none; rua=mailto:admin@domain.com` (start with `p=none`)
6. **Autodiscover CNAME**: `autodiscover.outlook.com`
7. **TTL**: Lower TTL to 300 before cutover, restore to 3600 after 48h

See `references/dns-records.md` for copy-paste DNS templates.

## Post-Migration Validation

Run these checks for every user:

- [ ] Email receiving on Outlook (send test from external)
- [ ] Historical emails present (spot-check oldest + newest)
- [ ] Folders mapped correctly (labels→folders)
- [ ] Contacts imported (check count vs Google)
- [ ] Calendar events present (check recurring events specifically)
- [ ] Google Groups recreated as Distribution Lists
- [ ] Signatures set up in Outlook
- [ ] Mobile devices re-configured (Outlook app or Exchange)
- [ ] Gmail IMAP disabled or account removed

See `references/validation-checklist.md` for printable per-user checklist.

## Common Issues

| Issue | Fix |
|-------|-----|
| Migration stuck at connecting | Re-check Google service account permissions |
| Labels become nested folders | Expected — Google labels flatten to Outlook folders |
| Calendar recurring events broken | Complex recurrences may need manual recreation |
| Contacts missing phone numbers | Google exports differently — check import mapping |
| Large attachments missing | Items >150MB not migrated — export separately |
| Google Groups not migrating | Create Distribution Lists manually in Exchange Admin |
| Drive file links broken | Migrate files to OneDrive, update links manually |
| MX propagation slow | Check TTL, use `dig MX domain.com` to verify |

## Deliverables Template

For client-facing migration projects, prepare:

1. **Migration Plan** — Timeline, phases, user batches, rollback plan
2. **User Communication** — Email template announcing the switch
3. **Admin Runbook** — Step-by-step for the migration operator
4. **Validation Report** — Per-user sign-off checklist

See `references/client-templates.md` for ready-to-use templates.