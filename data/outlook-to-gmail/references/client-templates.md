# Client-Facing Templates

## Migration Plan (Email to Client)

```
Subject: Email Migration Plan — Outlook → Google Workspace

Hi [Client],

Here's the migration plan for moving your team from Outlook/Office 365 to Google Workspace.

**Timeline:**
- Phase 1 (Day 1-2): Account setup + data migration start
- Phase 2 (Day 3-5): Migration running (users keep using Outlook)
- Phase 3 (Day 6): MX cutover + DNS changes (weekend)
- Phase 4 (Day 7-10): Validation + user support

**What users need to do:**
- Nothing during Phase 1-2 (migration runs in background)
- Phase 3: Switch to Gmail (we'll send instructions)
- Report any missing emails within 5 business days

**What we handle:**
- All technical migration + DNS changes
- Per-user validation
- Support for first 2 weeks post-migration

**Risks & mitigations:**
- Old emails: We keep Outlook active for 30 days as backup
- Large attachments (>25MB): Migrated separately to Drive
- Calendar recurring events: Manual verification for complex patterns

Let me know if you'd like to adjust the timeline.

Best,
[Name]
```

## User Announcement Template

```
Subject: We're moving to Gmail — Here's what you need to know

Hi team,

Starting [DATE], we're switching from Outlook to Gmail (Google Workspace).

**What's happening:**
- Your emails, contacts, and calendar are being migrated automatically
- On [CUTOVER DATE], new emails will arrive in Gmail instead of Outlook

**What you need to do:**
1. Go to https://mail.google.com and sign in with your work email
2. Your password is: [temporary password / SSO instructions]
3. Check that your emails and calendar look correct
4. Set up the Gmail app on your phone (instructions attached)

**Your Outlook will still work** for reading old emails for 30 days. But please start using Gmail for all new emails from [CUTOVER DATE].

**Need help?** Reply to this email or contact [support contact].

Thanks,
[Admin name]
```

## Migration Report Template

```
# Migration Report — [Client Name]

**Date:** [date]
**Migrated by:** [name]
**Method:** Google Data Migration Service / GWMMO / IMAP

## Summary
- Users migrated: X / Y total
- Data migrated: Email ✅ | Contacts ✅ | Calendar ✅
- Total data volume: ~X GB
- Migration duration: X days
- MX cutover completed: [date + time]

## Per-User Status
| User | Email | Contacts | Calendar | Validated |
|------|-------|----------|----------|-----------|
| user1@domain.com | ✅ | ✅ | ✅ | ✅ |
| user2@domain.com | ✅ | ✅ | ⚠️ recurring | ✅ |

## Issues Encountered
1. [Issue + resolution]

## Post-Migration Tasks
- [ ] Monitor MX propagation (48h)
- [ ] Tighten DMARC policy (2 weeks)
- [ ] Decommission Outlook accounts (30 days)
- [ ] Final sign-off from client
```
