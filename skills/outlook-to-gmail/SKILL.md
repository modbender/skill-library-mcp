---
name: outlook-to-gmail
description: "Migrate email, contacts, and calendars from Microsoft Outlook (Office 365 / Exchange / PST) to Google Workspace (Gmail). Use when a user asks to migrate from Outlook to Gmail, transfer emails from Microsoft 365 to Google Workspace, import PST files to Gmail, switch from Exchange to Gmail, or plan an Office 365 to Google Workspace migration. Covers: single-user migrations, bulk/org-wide migrations, PST imports, calendar + contacts transfer, DNS/MX cutover, and post-migration validation."
---

# Outlook to Gmail Migration

## Migration Paths

Assess the source environment first:

| Source | Best Method | Scope |
|--------|------------|-------|
| Office 365 / Exchange Online | Google Data Migration Service (Admin Console) | Org-wide, bulk |
| On-prem Exchange | GWMMO tool or IMAP migration | Per-user or bulk |
| PST files | GWMMO tool or Outlook IMAP bridge | Per-user |
| Outlook.com (personal) | IMAP migration in Admin Console | Per-user |

## Pre-Migration Checklist

Run through this with the client before touching anything:

1. **Inventory** — Number of users, total mailbox sizes, largest mailbox, shared mailboxes, distribution lists
2. **Google Workspace plan** — Confirm active subscription, verify admin access (Super Admin required)
3. **Source admin access** — Global Admin (O365) or Exchange Admin + app passwords
4. **DNS access** — Whoever manages MX records (registrar, Cloudflare, etc.)
5. **Data scope** — Email only? +Contacts? +Calendars? +Drive files?
6. **Cutover window** — When to switch MX records (weekend recommended)
7. **Client communication** — Draft email to users about the switch, new login instructions
8. **Retention** — Keep source mailboxes active 30 days post-migration as safety net

## Method 1: Google Data Migration Service (Recommended for O365)

Best for org-wide migrations from Exchange Online / Office 365.

### Setup

1. Google Admin Console → **Data** → **Data import & export** → **Data Migration (New)**
2. Select **Microsoft Office 365** as source
3. Click **Connect** → sign in as Microsoft Global Admin → grant permissions
4. Select what to migrate: Email, Contacts, Calendars
5. Choose date range filter (optional — migrate only last N months to save time)

### Execution

1. Add users to migrate (CSV upload for bulk: `source_email,destination_email`)
2. Start migration — Google handles delta sync automatically
3. Monitor progress in Admin Console → shows per-user status
4. Migration runs in background — users can keep using Outlook during this phase

### CSV Format

```csv
source_email,destination_email
john@company.onmicrosoft.com,john@company.com
jane@company.onmicrosoft.com,jane@company.com
```

See `references/csv-template.md` for full template with notes.

## Method 2: GWMMO Tool (PST / Outlook Profile)

Best for individual users or PST file imports.

1. Download GWMMO: https://tools.google.com/dlpage/gsmmo/
2. Install on machine with Outlook profile or PST access
3. Sign in with Google Workspace account
4. Select Outlook profile or browse to PST file
5. Choose data: Email, Contacts, Calendars, Junk
6. Start import — progress shown in tool

**Limitations**: Runs per-user, requires desktop access, Windows only.

## Method 3: IMAP Bridge (Manual / Small Scale)

For personal Outlook.com accounts or when other methods fail:

1. Enable IMAP in Gmail: Settings → Forwarding and POP/IMAP → Enable IMAP
2. In Outlook desktop, add Gmail as IMAP account
3. Drag-and-drop folders from Outlook mailbox to Gmail IMAP folders
4. Slow but works for any IMAP-capable source

## DNS / MX Cutover

After migration data is transferred:

1. **Verify domain** in Google Admin Console (TXT record)
2. **Update MX records** to Google:
   ```
   Priority  Host
   1         ASPMX.L.GOOGLE.COM
   5         ALT1.ASPMX.L.GOOGLE.COM
   5         ALT2.ASPMX.L.GOOGLE.COM
   10        ALT3.ASPMX.L.GOOGLE.COM
   10        ALT4.ASPMX.L.GOOGLE.COM
   ```
3. **Set SPF**: `v=spf1 include:_spf.google.com ~all`
4. **Set DKIM**: Admin Console → Apps → Gmail → Authenticate email → Generate DKIM
5. **Set DMARC**: `v=DMARC1; p=none; rua=mailto:admin@domain.com` (start with `p=none`, tighten later)
6. **TTL**: Lower TTL to 300 before cutover, restore to 3600 after 48h

See `references/dns-records.md` for copy-paste DNS templates.

## Post-Migration Validation

Run these checks for every user:

- [ ] Email receiving on Gmail (send test from external)
- [ ] Historical emails present (spot-check oldest + newest)
- [ ] Folders/labels mapped correctly
- [ ] Contacts imported (check count)
- [ ] Calendar events present (check recurring events specifically)
- [ ] Shared mailboxes / groups recreated as Google Groups
- [ ] Signatures set up in Gmail
- [ ] Mobile devices re-configured (Gmail app or IMAP)
- [ ] Outlook desktop disconnected or reconfigured

See `references/validation-checklist.md` for printable per-user checklist.

## Common Issues

| Issue | Fix |
|-------|-----|
| Migration stuck at 0% | Re-authorize source admin credentials |
| Missing folders | Google flattens deep nesting → becomes labels |
| Calendar recurring events broken | Re-create manually (known Google limitation with complex recurrences) |
| Contacts duplicated | Use Google Contacts merge duplicates tool |
| Large attachments missing | Items >25MB not migrated — export separately |
| Shared mailbox not migrating | Convert to Google Group or shared drive |
| MX propagation slow | Check TTL, use `dig MX domain.com` to verify |

## Deliverables Template

For client-facing migration projects, prepare:

1. **Migration Plan** — Timeline, phases, user batches, rollback plan
2. **User Communication** — Email template announcing the switch
3. **Admin Runbook** — Step-by-step for the migration operator
4. **Validation Report** — Per-user sign-off checklist

See `references/client-templates.md` for ready-to-use templates.
