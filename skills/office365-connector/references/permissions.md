# Microsoft Graph Permissions Reference

This document provides detailed information about each permission requested by the Microsoft Graph skill, what data each permission can access, and security considerations.

## Permission Types

Microsoft Graph supports two permission types:

- **Delegated permissions**: Used by apps with a signed-in user. The app acts on behalf of the user.
- **Application permissions**: Used by apps without a signed-in user (background services).

**This skill uses DELEGATED permissions only** - all operations are performed on behalf of the authenticated user, not as a background service.

## Required Permissions

### User.Read (Default/Required)

**What it does:**
- Sign in and read user profile information
- Required for authentication to work

**Data accessed:**
- Display name
- Email address
- Profile photo
- User ID
- Job title
- Department
- Office location

**Security considerations:**
- Minimum permission required for any Microsoft Graph integration
- Read-only access to basic profile
- Cannot modify user profile

**Example use cases:**
- Displaying "Signed in as: user@example.com"
- Personalizing email signatures

**Risk level:** ⬛️ Low

---

### offline_access (Required)

**What it does:**
- Maintains access to data you have given it access to
- Enables refresh tokens for long-term access without re-authentication

**Data accessed:**
- No direct data access
- Allows token refresh without user interaction

**Security considerations:**
- Essential for production apps to avoid constant re-authentication
- Refresh tokens expire after 90 days of inactivity
- Tokens can be revoked at any time by user or admin

**Example use cases:**
- Checking email without signing in every time
- Background calendar synchronization

**Risk level:** ⬛️ Low

---

### Mail.Read

**What it does:**
- Read emails in all folders
- View email metadata (sender, subject, date)
- Access email body content and attachments

**Data accessed:**
- All emails in user's mailbox
- Email headers (from, to, cc, bcc, subject, date)
- Email body (text and HTML)
- Attachments
- Folder structure
- Message properties (read status, importance, categories)

**Security considerations:**
- **Read-only** - Cannot modify, send, or delete emails
- Provides access to potentially sensitive information
- Includes deleted items and archive folders

**Example use cases:**
- "Show me unread emails from today"
- "Search for emails about the project"
- "What attachments did I receive this week?"

**Risk level:** ⬛️⬛️ Medium

---

### Mail.ReadWrite

**What it does:**
- All capabilities of Mail.Read PLUS:
- Modify email properties (mark as read, flag, categorize)
- Move or copy emails between folders
- Delete emails (moves to Deleted Items)
- Create and update draft emails

**Data accessed:**
- Same as Mail.Read
- Write access to email properties and folder locations

**Security considerations:**
- **Cannot send emails** - requires separate Mail.Send permission
- Can permanently delete from Deleted Items folder
- Can modify email metadata and organization
- Cannot access or modify admin/security controls

**Example use cases:**
- "Mark all emails from sender@example.com as read"
- "Move emails about Project X to a folder"
- "Delete emails older than 6 months"
- "Create a draft email to save for later"

**Risk level:** ⬛️⬛️⬛️ Medium-High

---

### Mail.Send

**What it does:**
- Send emails as the signed-in user
- Send emails with attachments
- Reply to and forward existing emails

**Data accessed:**
- No additional read access
- Only provides send capability

**Security considerations:**
- **Highest impact permission** - can send emails on user's behalf
- No safeguards against sending to wrong recipients
- Sent emails appear to come from the user
- Cannot send as other users or distribution lists
- Subject to same sending limits as user account

**Example use cases:**
- "Send a summary email to team@company.com"
- "Reply to the latest email from john@example.com"
- "Forward this PDF to sarah@example.com"

**Risk level:** ⬛️⬛️⬛️⬛️ High

---

### Calendars.Read

**What it does:**
- View all calendar events
- Read event details (title, location, attendees, time)
- Access calendar properties

**Data accessed:**
- All calendars user has access to
- Event details (subject, location, start, end, time zone)
- Attendee information
- Meeting organizer
- Recurrence patterns
- Event categories and properties

**Security considerations:**
- **Read-only** - Cannot create, modify, or delete events
- Includes private/confidential event details
- Access to meeting attendee email addresses
- Can view events from shared calendars

**Example use cases:**
- "What meetings do I have tomorrow?"
- "Check my availability next Tuesday"
- "Show me all events with Jane this month"

**Risk level:** ⬛️⬛️ Medium

---

### Calendars.ReadWrite

**What it does:**
- All capabilities of Calendars.Read PLUS:
- Create new calendar events
- Update existing events
- Delete events
- Respond to meeting invitations
- Manage calendar permissions

**Data accessed:**
- Same as Calendars.Read
- Write access to all calendar operations

**Security considerations:**
- Can create/modify/delete any event user has access to
- Can accept or decline meetings on user's behalf
- Changes to recurring events affect all instances
- Can make events private or public
- Cannot access other users' private calendars without permission

**Example use cases:**
- "Schedule a meeting with john@example.com for next Monday at 2pm"
- "Cancel my 3pm meeting tomorrow"
- "Move my Friday meeting to Thursday"
- "Accept all meeting invitations from this week"

**Risk level:** ⬛️⬛️⬛️ Medium-High

---

### Contacts.Read

**What it does:**
- Read contacts from user's contact folders
- View contact details (name, email, phone, address)
- Access contact groups

**Data accessed:**
- All contacts user has access to
- Contact properties (name, emails, phones, addresses)
- Company information
- Job titles
- Notes and custom fields
- Contact photos

**Security considerations:**
- **Read-only** - Cannot create, modify, or delete contacts
- Access to potentially sensitive personal information
- Includes business and personal contact details
- Can view contacts from shared contact folders

**Example use cases:**
- "Find contact information for Sarah Johnson"
- "Show me all contacts from Microsoft"
- "What's John's phone number?"

**Risk level:** ⬛️⬛️ Medium

---

### Contacts.ReadWrite

**What it does:**
- All capabilities of Contacts.Read PLUS:
- Create new contacts
- Update existing contacts
- Delete contacts
- Manage contact folders
- Update contact photos

**Data accessed:**
- Same as Contacts.Read
- Write access to all contact operations

**Security considerations:**
- Can modify or delete any contact user has access to
- Can create contacts with any information
- Changes are permanent (no built-in undo)
- Cannot access other users' private contacts without permission

**Example use cases:**
- "Add Mike Williams as a contact: mike@example.com"
- "Update Sarah's phone number to 555-1234"
- "Delete all contacts from Contoso company"
- "Create a contact group for my project team"

**Risk level:** ⬛️⬛️⬛️ Medium-High

---

## Permission Combinations

### Minimal Setup (Read-Only)
If you only need to **read** data without making changes:
- User.Read
- offline_access
- Mail.Read
- Calendars.Read
- Contacts.Read

**Use cases:** Reporting, search, analytics, dashboards

---

### Standard Setup (Read + Write)
For full functionality including creating/modifying data:
- User.Read
- offline_access
- Mail.Read
- Mail.ReadWrite
- Mail.Send
- Calendars.Read
- Calendars.ReadWrite
- Contacts.Read
- Contacts.ReadWrite

**Use cases:** Full email/calendar/contact management, automation, workflows

---

### Email-Only Setup
If you only need email capabilities:
- User.Read
- offline_access
- Mail.Read
- Mail.ReadWrite (optional)
- Mail.Send (optional)

**Use cases:** Email monitoring, automated replies, email organization

---

### Calendar-Only Setup
If you only need calendar capabilities:
- User.Read
- offline_access
- Calendars.Read
- Calendars.ReadWrite (optional)

**Use cases:** Meeting scheduling, availability checking, calendar synchronization

---

## Security Best Practices

### 1. Principle of Least Privilege
Only request permissions you actually need:
- Need read-only access? Don't request ReadWrite
- Only using email? Don't request Calendar/Contacts permissions
- Review periodically and remove unused permissions

### 2. User Transparency
- Clearly explain why each permission is needed
- Show users what data will be accessed
- Provide opt-out for optional features

### 3. Data Handling
- Don't store sensitive email/calendar/contact data unnecessarily
- Encrypt data at rest if storing locally
- Follow data retention policies
- Delete tokens when no longer needed

### 4. Monitoring & Auditing
- Monitor Azure AD sign-in logs regularly
- Review Microsoft Graph API usage
- Alert on unusual access patterns
- Keep audit trail of operations

### 5. Token Security
- Store tokens securely (encrypted, restricted permissions)
- Never expose tokens in logs or error messages
- Rotate client secrets regularly
- Revoke tokens immediately if compromised

## Permission Comparison: Delegated vs Application

**This skill uses DELEGATED permissions**, but here's the key difference:

| Aspect | Delegated (This Skill) | Application (Not Used) |
|--------|------------------------|------------------------|
| User context | Acts as signed-in user | Acts as application itself |
| Data access | Only user's own data | All users' data in organization |
| Authentication | User signs in | No user sign-in required |
| Consent | User consent required | Admin consent required |
| Risk level | Medium | High |
| Use case | Personal automation | Background services, admin tools |

**Why delegated is safer:**
- Scoped to individual user's data only
- User explicitly authorizes access
- No access to other users' data
- Easier to revoke (user or admin can remove access)

## Revoking Access

Users can revoke access at any time:

1. Visit https://myaccount.microsoft.com/
2. Click **Privacy** → **Apps and services**
3. Find the app (e.g., "OpenClaw Microsoft Graph Integration")
4. Click **Revoke access**

Alternatively, administrators can revoke access in Azure AD.

## Admin Consent Requirements

Some organizations require **admin consent** for apps to access Microsoft Graph:

**When admin consent is needed:**
- Organization has configured Azure AD to require admin approval
- App requests sensitive permissions (varies by org policy)
- App is published to app gallery

**How to check if needed:**
- Azure Portal → App registrations → Your app → API permissions
- Look for "Admin consent required" in Status column

**Getting admin consent:**
- Request IT admin to grant consent via Azure Portal
- Or send admin consent URL (see setup guide)

## Additional Resources

- **Microsoft Graph permissions reference**: https://learn.microsoft.com/en-us/graph/permissions-reference
- **Best practices for permissions**: https://learn.microsoft.com/en-us/graph/permissions-overview
- **Delegated vs application permissions**: https://learn.microsoft.com/en-us/graph/auth/auth-concepts
- **Consent framework**: https://learn.microsoft.com/en-us/azure/active-directory/develop/consent-framework

## FAQ

**Q: Can this app read other users' emails?**
A: No. Delegated permissions only grant access to the signed-in user's own data.

**Q: Can the app send emails without my knowledge?**
A: The app can send emails on your behalf, but only when you explicitly ask it to. All sent emails appear in your Sent Items folder.

**Q: What happens if I revoke access?**
A: The app immediately loses access to your data. Stored tokens become invalid. You'll need to re-authenticate if you want to use the app again.

**Q: Can this app access my OneDrive or SharePoint files?**
A: No. This skill only requests email, calendar, and contact permissions. File access requires separate permissions (Files.Read, Files.ReadWrite, etc.).

**Q: How long do tokens last?**
A: Access tokens expire after 1 hour. Refresh tokens typically last 90 days but are automatically refreshed as long as you use the app regularly.

**Q: Is this secure?**
A: When configured properly, yes. The OAuth 2.0 protocol is industry-standard and secure. Follow the security best practices in this document and the setup guide.

**Q: Can my IT admin see what the app is doing?**
A: Yes. Administrators can view sign-in logs and API usage in Azure AD. This is actually a security feature that helps detect unauthorized access.
