# Client Templates — Gmail to Outlook Migration

## Migration Plan Template

### Project: Gmail to Microsoft 365 Migration
**Client:** _________________ **Start Date:** __________ **IT Contact:** _____________

#### Phase 1: Preparation (Week 1)
- [ ] Complete pre-migration inventory
- [ ] Set up Microsoft 365 licenses for all users
- [ ] Create migration CSV with user mappings
- [ ] Configure service account for bulk migration
- [ ] Schedule communication to users

#### Phase 2: Pilot Migration (Week 2)
- [ ] Migrate 5-10 test users
- [ ] Validate data integrity and functionality
- [ ] Gather feedback from pilot users
- [ ] Refine migration process based on results
- [ ] Document any issues and resolutions

#### Phase 3: Phased Rollout (Weeks 3-4)
- [ ] Batch 1: Management/IT team (20% of users)
- [ ] Batch 2: Department leads (30% of users)
- [ ] Batch 3: General users (remaining 50%)
- [ ] 48-hour gap between batches for issue resolution

#### Phase 4: DNS Cutover (Week 4 end)
- [ ] Update MX records to Microsoft 365
- [ ] Monitor mail flow for 24 hours
- [ ] Disable Gmail IMAP access
- [ ] Complete final user validations

#### Rollback Plan
If critical issues arise:
1. Revert MX records to Google Workspace
2. Re-enable Gmail IMAP access
3. Communicate delay to users
4. Address issues before retry

## User Announcement Email

**Subject: Important: Email Migration to Microsoft 365 - Action Required**

Dear Team,

We are migrating our email system from Gmail/Google Workspace to Microsoft 365 (Outlook) to better align with our business needs and improve collaboration capabilities.

### What's Happening
- **Migration Date:** [DATE]
- **Downtime:** Minimal (15-30 minutes during MX cutover)
- **Your Action Required:** Set up new Outlook account

### What's Changing
- **Email Address:** Stays the same (yourname@company.com)
- **New Login:** Use your Microsoft 365 credentials
- **New Apps:** Microsoft Outlook (instead of Gmail)
- **Calendar/Contacts:** Will migrate automatically

### Before Migration Day
1. **Back up important emails** if desired (Google Takeout)
2. **Note important calendar events** for the next 30 days
3. **Update mobile devices** with new Outlook app after migration

### After Migration Day
1. **Log in to outlook.office.com** with your new credentials
2. **Install Outlook app** on mobile devices
3. **Verify your data** migrated correctly
4. **Contact IT** if you have any issues

### New Features You'll Enjoy
- **Better integration** with Office 365 tools (Word, Excel, Teams)
- **Enhanced security** and compliance features
- **Improved mobile experience** with Outlook app
- **Shared calendars** and collaboration tools

### Support
- **Help Desk:** [CONTACT INFO]
- **Migration Support:** Available [DATES/TIMES]
- **Quick Setup Guide:** [LINK TO GUIDE]

Your historical emails, contacts, and calendar will be migrated automatically. We expect the migration to be seamless, but please report any issues immediately.

Thank you for your cooperation during this transition.

Best regards,
IT Team

## Migration Report Template

### Gmail to Microsoft 365 Migration Report
**Date:** __________ **Technician:** _____________ **Client:** _____________

#### Migration Summary
- **Total Users:** _____ **Successful:** _____ **Failed:** _____ **Retry Required:** _____
- **Total Data Migrated:** _____ GB **Largest Mailbox:** _____ GB
- **Migration Duration:** _____ hours **DNS Cutover Time:** _____

#### User Status
| User | Status | Email Count | Issues | Resolution |
|------|--------|-------------|---------|-----------|
| john@company.com | Complete | 5,247 | None | - |
| jane@company.com | Complete | 3,891 | Calendar sync | Fixed manually |
| admin@company.com | Failed | - | Permission error | Retry scheduled |

#### Technical Details
- **Migration Method:** Microsoft Data Migration Service
- **Service Account:** migration-sa@company.iam.gserviceaccount.com
- **Migration Batch ID:** [BATCH_ID]
- **DNS Changes Applied:** [DATE/TIME]

#### Data Integrity Validation
- [ ] Email counts verified for sample users
- [ ] Calendar events spot-checked
- [ ] Contacts migrated completely
- [ ] Folder structure preserved
- [ ] Search functionality tested

#### Issues Encountered
1. **Google Drive links in emails** — Links remain functional, no action needed
2. **Complex calendar recurrence** — 3 users require manual calendar recreation
3. **Large attachments** — 12 emails with 25MB+ attachments need separate migration

#### User Feedback
- **Positive:** Users appreciate unified Microsoft ecosystem
- **Concerns:** Learning curve for Outlook interface
- **Requests:** Training session on advanced Outlook features

#### Post-Migration Actions
- [ ] Schedule user training session for [DATE]
- [ ] Monitor mail flow for 48 hours
- [ ] Follow up with users experiencing issues
- [ ] Complete final validations by [DATE]
- [ ] Document lessons learned

#### Client Sign-off
**Migration completed successfully:** ☐ Yes ☐ No

**Client signature:** ________________________ **Date:** ___________

**IT signature:** __________________________ **Date:** ___________

## Quick Setup Guide Template

### Microsoft 365 Outlook Setup Guide

#### Desktop Setup (Windows/Mac)
1. **Download Outlook** from office.com
2. **Add account** → Choose Microsoft 365
3. **Enter credentials** provided by IT
4. **Wait for sync** (may take 1-2 hours for large mailboxes)

#### Mobile Setup (iOS/Android)
1. **Install Microsoft Outlook** from app store
2. **Tap "Get Started"**
3. **Enter work email** (yourname@company.com)
4. **Enter password** provided by IT
5. **Allow notifications** when prompted

#### Web Access
- **URL:** outlook.office.com
- **Login:** Use your Microsoft 365 credentials
- **Bookmark** for easy access

#### Frequently Asked Questions

**Q: Where are my old emails?**
A: All migrated to your new Outlook mailbox. Check the "Archive" folder for older items.

**Q: My calendar is empty?**
A: Calendar sync may take 2-4 hours. Contact IT if still missing after 24 hours.

**Q: Can I still access Gmail?**
A: Yes, for 30 days during transition period. After that, Gmail will be read-only.

**Q: How do I set up my signature?**
A: Outlook → Settings → Signature. IT can help transfer your old signature.

**Need Help?** Contact IT: [PHONE] | [EMAIL] | [TICKET SYSTEM]