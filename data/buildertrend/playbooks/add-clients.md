# Add & Manage Clients (Agent-Assisted)

## Overview
The agent manages Buildertrend client contacts — adding new clients to jobs, setting roles and permissions, sending portal invitations, configuring what clients can see, managing multiple contacts per job, and linking clients to QuickBooks customer records. This covers the full client lifecycle from first contact through active portal user.

## Trigger
- the user says "add client to [project]" or "invite [name] to the portal"
- the user says "update client permissions for [project]"
- the user says "resend portal invite to [client]"
- New job created (from convert-lead-to-job playbook)
- the user says "add [name] as co-signer" or "add the architect"

---

## Step 1: Identify Project & Action
**Action:** Confirm which project and what client action

**Message to the user:**
```
👤 Client Management — which project?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `bt_client_project_1` |
| 🏗️ Project Alpha | `primary` | `bt_client_project_1` |
| 🏗️ Project Beta | `primary` | `bt_client_project_2` |
| 🏗️ Project Beta | `primary` | `bt_client_project_2` |
| 🏗️ Project Epsilon | `primary` | `bt_client_project_3` |
| 🏗️ Project Gamma | `primary` | `bt_client_project_4` |
| 🏗️ Project Eta | `primary` | `bt_client_project_5` |
| ❌ Cancel | `danger` | `bt_client_cancel` |

**On project selected:**
```
👤 What would you like to do?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ➕ Add New Client | `success` | `bt_client_add_new` |
| ➕ Add Existing Contact | `primary` | `bt_client_add_existing` |
| 📧 Send/Resend Portal Invite | `primary` | `bt_client_invite` |
| 🔒 Update Permissions | `primary` | `bt_client_permissions` |
| ✏️ Edit Client Info | `primary` | `bt_client_edit` |
| 📋 View All Clients | `primary` | `bt_client_view` |
| ❌ Cancel | `danger` | `bt_client_cancel` |

---

## Step 2A: Add New Client Contact
**Action:** Collect client information and add to the job

**Message to the user:**
```
➕ New client for [Project Name]:

I'll need:
• First name & Last name
• Email (required for portal invite)
• Phone number
• Company name (optional)
• Mailing address (optional)
• Role: Primary contact, secondary, co-signer, architect, etc.

Or just tell me what you have.
```

**On response, present summary:**
```
👤 New Client Summary:

📌 Name: [first] [last]
📧 Email: [email]
📱 Phone: [phone]
🏢 Company: [company or "—"]
📍 Address: [address or "—"]
👔 Role: [Primary / Secondary / Co-signer]
🏗️ Job: [project name]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Add Client | `success` | `bt_client_create` |
| ✏️ Edit Details | `primary` | `bt_client_edit_details` |
| ❌ Cancel | `danger` | `bt_client_cancel` |

### Browser Relay — Add New Client
1. Ensure correct job is selected in BT left sidebar
2. Navigate to `/app/JobPage/{jobId}/2?accessedFromContact=true` (Job Details → Clients tab)
3. Click **"+ New Contact"**
4. Fill contact form:
   - **First Name** (text input)
   - **Last Name** (text input)
   - **Email** (text input) — required for portal invite
   - **Phone** (text input)
   - **Cell Phone** (text input)
   - **Company** (text input)
   - **Address** (Street, City, State, Zip)
5. Click **Save**
6. BT prompts: "Would you like to invite this client?"
7. Snapshot → confirm contact created

**Report back:**
```
✅ Client added to [Project Name]!

👤 [Name] — [email]
📋 Status: Not Invited (or Pending if invited)

Would you like to send the portal invite now?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📧 Send Portal Invite | `success` | `bt_client_send_invite` |
| 🔒 Set Permissions First | `primary` | `bt_client_set_perms` |
| ➕ Add Another Client | `primary` | `bt_client_add_another` |
| ⏭️ Done | `primary` | `bt_client_done` |

---

## Step 2B: Add Existing Contact
**Action:** Link an existing BT contact to this job

### Browser Relay — Add Existing
1. Navigate to `/app/JobPage/{jobId}/2?accessedFromContact=true`
2. Click **"+ Existing Contact"**
3. Search by name or email in the contact list
4. Select the contact
5. Click **Save**
6. Snapshot → confirm contact linked

---

## Step 3: Configure Client Permissions
**Action:** Set what the client can see and do in the portal

**⚠️ IMPORTANT:** Set permissions BEFORE sending the portal invite. Once invited, clients immediately see everything their permissions allow.

**Message to the user:**
```
🔒 Client permissions for [Name] on [Project]:

What should they have access to?
```

**Inline buttons (toggle on/off):**
| Button | Style | callback_data |
|---|---|---|
| 📅 Schedule | `primary` | `bt_client_perm_schedule` |
| 📝 Daily Logs | `primary` | `bt_client_perm_dailylogs` |
| 📋 Change Orders | `primary` | `bt_client_perm_co` |
| 🔀 CO Requests (create) | `primary` | `bt_client_perm_co_request` |
| 🎨 Selections | `primary` | `bt_client_perm_selections` |
| 💰 Invoices | `primary` | `bt_client_perm_invoices` |
| 📁 Files / Documents | `primary` | `bt_client_perm_files` |
| 📸 Photos | `primary` | `bt_client_perm_photos` |
| 🔧 Warranty Claims | `primary` | `bt_client_perm_warranty` |
| 📊 Job Costing Budget | `primary` | `bt_client_perm_budget` |
| 💬 Comments | `primary` | `bt_client_perm_comments` |
| ✅ Use Company Defaults | `success` | `bt_client_perm_defaults` |

### Company Default Permissions (Recommended)
| Feature | Access | Notes |
|---|---|---|
| Schedule | ✅ View | See timeline but not internal details |
| Daily Logs | ✅ View shared | Only logs shared with clients |
| Change Orders | ✅ View + Approve | Must approve COs |
| CO Requests | ✅ Create | Can submit CO requests |
| Selections | ✅ View + Approve | Must choose selections |
| Invoices | ✅ View + Pay | See invoices, make payments |
| Files / Documents | ✅ View shared | Only client-shared folders |
| Photos | ✅ View shared | Project photos |
| Warranty Claims | ✅ Create | Post-completion warranty |
| Job Costing Budget | ❌ Hidden | Internal financial data |
| Comments | ✅ View + Create | Communication channel |

### Browser Relay — Set Permissions
1. On Job Details → Clients tab, find the client contact card
2. Click to expand or edit permissions
3. For each feature, toggle the appropriate access level
4. Check/uncheck **notification settings** (email, text, push):
   - ☐ Email notifications
   - ☐ Text notifications  
   - ☐ Push notifications (mobile app)
5. Click **Save**
6. Snapshot → confirm permissions set

**💡 Pro Tip:** Use "Edit from Client Portal" button to preview exactly what the client will see.

---

## Step 4: Send Portal Invitation
**Action:** Invite the client to the Buildertrend Client Portal

**Prerequisites check:**
- ✅ Client has email address
- ✅ Permissions are set
- ✅ Notification preferences configured

### Browser Relay — Send Invite
1. Navigate to `/app/JobPage/{jobId}/2?accessedFromContact=true`
2. Find the client contact card
3. Click **"Send Invite"** button
4. BT shows invitation preview
5. Confirm and click **Send**
6. Client receives email with invitation link
7. Snapshot → confirm invite sent (status changes to **Pending**)

**Report back:**
```
📧 Portal invite sent to [Name]!

👤 [Name] — [email]
📋 Status: Pending (awaiting client signup)
🔒 Permissions: [summary]
📱 Notifications: [email/text/push]

The client will create their login from the invitation email.
When they do, status changes to Active.
```

**Invite Status Flow:**
| Status | Meaning |
|---|---|
| Not Invited | Contact added but no invite sent |
| Pending | Invite sent, awaiting client signup |
| Active | Client created account and can access portal |

---

## Step 5: Manage Existing Clients
**Action:** Update info, resend invites, or deactivate

### View All Clients on Job
### Browser Relay — Read Clients
1. Navigate to `/app/JobPage/{jobId}/2?accessedFromContact=true`
2. Snapshot → extract all client contacts
3. For each: name, email, phone, status (Not Invited / Pending / Active), role

**Present to the user:**
```
👥 Clients on [Project Name]:

| # | Name | Email | Status | Role |
|---|------|-------|--------|------|
| 1 | [Name] | [email] | Active ✅ | Primary |
| 2 | [Name] | [email] | Pending ⏳ | Secondary |
| 3 | [Name] | [email] | Not Invited | Co-signer |
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✏️ Edit [Client 1] | `primary` | `bt_client_edit_1` |
| 📧 Resend Invite to [Client 2] | `primary` | `bt_client_resend_2` |
| 📧 Send Invite to [Client 3] | `success` | `bt_client_invite_3` |
| ➕ Add Another Client | `primary` | `bt_client_add_another` |
| ✅ Done | `success` | `bt_client_done` |

### Resend Invitation
1. Find client contact card
2. Click resend / cancel + re-invite option
3. Snapshot → confirm new invite sent

### Update Client Info
1. Click on client contact card
2. Edit fields (name, email, phone, address)
3. Click **Save**
4. Snapshot → confirm update

### Deactivate Client
```
⚠️ Deactivate [Name]'s portal access?
They'll lose the ability to log in, but their data is preserved.
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ⚠️ Deactivate | `danger` | `bt_client_deactivate` |
| ❌ Keep Active | `primary` | `bt_client_keep` |

---

## Step 6: Add Multiple Contacts Per Job
**Action:** Handle cases like husband + wife, owner + architect, owner + property manager

**Message to the user:**
```
👥 Adding another contact to [Project]:
What's their role?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 👤 Co-Owner / Spouse | `primary` | `bt_client_role_coowner` |
| 📐 Architect / Designer | `primary` | `bt_client_role_architect` |
| 🏢 Property Manager | `primary` | `bt_client_role_pm` |
| 💼 General Contractor (GC) | `primary` | `bt_client_role_gc` |
| 👔 Business Partner | `primary` | `bt_client_role_partner` |
| 📋 Other | `primary` | `bt_client_role_other` |

**Permission suggestions by role:**
| Role | Recommended Permissions |
|---|---|
| Co-Owner / Spouse | Same as primary (full access) |
| Architect / Designer | Schedule, Selections, Change Orders, Files, RFIs, Comments — NO invoices/budget |
| Property Manager | Schedule, Daily Logs, Invoices, Files, Warranty — full financial view |
| GC (if {{company_name}} is sub) | Schedule, POs, Daily Logs, Change Orders, Files |
| Business Partner | Same as primary (full access) |

After role selection → loop back to Step 2A (add contact) with pre-set permission defaults for that role.

---

## Step 7: Link Client to QuickBooks Customer
**Action:** Connect the BT client to their QBO customer record for proper invoicing

**Message to the user:**
```
📊 Link [Client Name] to QuickBooks?
This ensures invoices push correctly to QBO under the right customer.
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🔗 Link to QBO Customer | `success` | `bt_client_qbo_link` |
| ➕ Create New QBO Customer | `primary` | `bt_client_qbo_new` |
| ⏭️ Skip QBO Link | `primary` | `bt_client_qbo_skip` |

### Browser Relay — Link to QBO
1. Navigate to Job Details → **Accounting** tab
2. Click **"Link job"** to QBO Customer/Project
3. Search for existing QBO customer
4. If found: Select and link
5. If not found: BT can create new customer in QBO when invoice is pushed
6. Snapshot → confirm link

**Note:** When QBO is connected ({{company_name}} has QBO Plus):
- BT auto-creates Customers/Sub Customers/Projects in QBO based on job and client info
- Fields mapped: Display Name, Company, Contact Info, Address, Terms
- Invoice push requires job to be linked to QBO customer

---

## Smart Suggestions

### New Client — Pre-Fill Logic
| the user Says | Auto-Fill |
|---|---|
| "Add Jack's wife to Project A" | Search project clients → find Jack → pre-fill last name, address |
| "Add the architect to [project]" | Set role = Architect, suggest architect permissions |
| "Invite everyone on [project]" | Find all Not Invited contacts → batch send invites |

### Permission Recommendations
| Scenario | Suggestion |
|---|---|
| Residential client (single family) | Full default permissions |
| Commercial client (corporate) | Full access + budget visibility |
| Investor (not involved daily) | Invoices + Files only — minimal access |
| Architect (design phase) | Selections + Files + COs — no financials |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login, save client data for resume |
| No email provided | Cannot send portal invite — ask the user for email address |
| Contact already on job | Report: "[Name] is already added to this job with status [X]" |
| Duplicate contact in BT | Present existing contact: "Found [Name] in BT already — add existing or create new?" |
| Invite email bounced | Report bounce, ask the user to verify email address |
| Client email exists in BT | Client may already have credentials from another builder — will merge on login |
| Browser relay disconnected | Stop, save state, ask the user to re-enable |
| Permission change fails | Screenshot the error, report to the user |

---

## Client Notification Settings Reference

### Available Notification Methods
| Method | Description |
|---|---|
| Email | Notifications via email |
| Text (SMS) | Requires phone number |
| Push | Requires BT mobile app installed |

### What Triggers Client Notifications
| Event | Notification Sent? |
|---|---|
| Schedule item updated | If subscribed |
| Daily Log shared with client | If subscribed |
| Change Order sent | Always (email) |
| Selection sent | Always (email) |
| Invoice sent | Always (email) |
| Document/Photo uploaded to shared folder | If subscribed |
| Comment/Message received | If subscribed |
| Portal invite | Always (email) |

---

## URL Quick Reference

| Page | URL |
|---|---|
| Job Details (Clients tab) | `/app/JobPage/{jobId}/2?accessedFromContact=true` |
| Client Contact Settings | `/app/Settings/CustomerContactSettings` |
| Default Job Permissions | `/app/ClientJobPermissionSettings/Defaults` |
| Owner Portal Preview | `/app/ownerPortalRedirect/{jobId}/false` |

---

## Default Invitation Text
The default portal invitation text is editable by Admins in **Company Settings → Jobs tab**. Current default sends a professional email inviting the client to create their Buildertrend account with:
- Login link
- Company name ({{company_name}})
- Project name
- Brief instructions

**Pro Tip:** Preview the client's portal view using "Edit from Client Portal" button on the Clients tab to make sure everything looks right before sending the invite.
