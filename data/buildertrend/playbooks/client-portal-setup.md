# Client Portal Configuration (Agent-Assisted)

## Overview
The agent helps the user set up and manage the client-facing portal in Buildertrend — configuring what the client can see (schedule, daily logs, selections, invoices, photos, documents), sending portal invitations, managing notification preferences, setting up selection presentations, and configuring change order approval flows. A well-configured portal keeps clients informed and engaged without requiring phone calls for every update.

## Trigger
- the user says "set up portal for [client]" or "configure client access for [project]"
- New job created → client needs portal access
- Client asks about project status → suggest portal access
- Change in what client should see (e.g., add budget visibility for open book job)
- Need to send selections for client review
- Set up online payment for invoices

---

## Step 1: Identify Project
**Action:** Confirm which project

**Message to the user:**
```
👤 Client Portal Setup — which project?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `bt_portal_project_1` |
| 🏗️ Project Alpha | `primary` | `bt_portal_project_1` |
| 🏗️ Project Beta | `primary` | `bt_portal_project_2` |
| 🏗️ Project Beta | `primary` | `bt_portal_project_2` |
| 🏗️ Project Epsilon | `primary` | `bt_portal_project_3` |
| 🏗️ Project Gamma | `primary` | `bt_portal_project_4` |
| 🏗️ Project Eta | `primary` | `bt_portal_project_5` |
| ❌ Cancel | `danger` | `bt_portal_cancel` |

---

## Step 2: Choose Action
**Message to the user:**
```
👤 Client Portal — [project] — what do you need?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 👤 Add & Invite Client | `success` | `bt_portal_add_client` |
| 🔐 Configure Permissions | `primary` | `bt_portal_permissions` |
| 🔔 Notification Settings | `primary` | `bt_portal_notifications` |
| 🎨 Send Selections for Review | `primary` | `bt_portal_selections` |
| 📝 Set Up CO Approval Flow | `primary` | `bt_portal_co_flow` |
| 💳 Online Payment Setup | `primary` | `bt_portal_payments` |
| 👁️ Preview Client View | `primary` | `bt_portal_preview` |
| ❌ Cancel | `danger` | `bt_portal_cancel` |

---

## Step 3A: Add & Invite Client

### Collect Client Info
**Message to the user:**
```
👤 Client details:

• Name:
• Email:
• Phone:
• Role: (Owner? Developer? Tenant?)
```

### Browser Relay Execution — Add Client
1. Navigate to Job Details → Clients tab: `/app/JobPage/{jobId}/2?accessedFromContact=true`
2. Snapshot → verify Clients tab loaded
3. Click **"+ New Contact"** (or **"+ Existing Contact"** if already in system)
4. Fill:
   - **First Name / Last Name**
   - **Email** (required for portal invitation)
   - **Phone**
5. Click **Save**
6. BT prompts: "Would you like to invite this client?"
7. **Before inviting** → configure permissions first (Step 3B)

**Report back:**
```
✅ Client added to [project]:

👤 [Client Name]
📧 [email]
📊 Status: Added — pending invitation
💡 Configure permissions before sending invite.
```

---

## Step 3B: Configure Permissions

### Permission Categories
**Message to the user:**
```
🔐 What should [Client Name] see on the portal?

I'll set up permissions based on your preferences:
```

**Inline buttons (preset packages):**
| Button | Style | callback_data |
|---|---|---|
| 📋 Full Transparency (Everything) | `success` | `bt_portal_perm_full` |
| 📊 Standard (Schedule + Logs + Photos) | `primary` | `bt_portal_perm_standard` |
| 📦 Minimal (Schedule + Invoices Only) | `primary` | `bt_portal_perm_minimal` |
| ✏️ Custom (Pick & Choose) | `primary` | `bt_portal_perm_custom` |

### Permission Detail Matrix
| Feature | Full | Standard | Minimal | Description |
|---------|------|----------|---------|-------------|
| Schedule | ✅ | ✅ | ✅ | View project timeline |
| Daily Logs | ✅ | ✅ | ❌ | View daily progress + photos |
| Selections | ✅ | ✅ | ❌ | Review/approve finish choices |
| Change Orders | ✅ | ✅ | ❌ | View/approve COs |
| CO Requests | ✅ | ❌ | ❌ | Client can submit CO requests |
| Invoices | ✅ | ✅ | ✅ | View and pay invoices |
| Photos | ✅ | ✅ | ❌ | Browse project photos |
| Documents | ✅ | ❌ | ❌ | View shared documents |
| Videos | ✅ | ❌ | ❌ | View project videos |
| Files Upload | ✅ | ❌ | ❌ | Client can upload files |
| Warranty Claims | ✅ | ❌ | ❌ | Submit warranty requests |
| To-Dos | ✅ | ❌ | ❌ | View/create own to-dos |
| Job Costing Budget | ⚠️ Optional | ❌ | ❌ | See budget details (use with caution) |
| Comments | ✅ | ✅ | ❌ | Add comments on features |
| Messages | ✅ | ✅ | ✅ | Direct messaging |

### Custom Permission Selection
If "Custom" chosen:
```
🔐 Toggle each feature for [Client Name]:
```

**Inline buttons (toggle on/off):**
| Button | Style | callback_data |
|---|---|---|
| 📅 Schedule: ON | `success` | `bt_portal_toggle_schedule` |
| 📝 Daily Logs: OFF | `primary` | `bt_portal_toggle_dailylogs` |
| 🎨 Selections: ON | `success` | `bt_portal_toggle_selections` |
| 📝 Change Orders: ON | `success` | `bt_portal_toggle_co` |
| 💰 Invoices: ON | `success` | `bt_portal_toggle_invoices` |
| 📸 Photos: ON | `success` | `bt_portal_toggle_photos` |
| 📁 Documents: OFF | `primary` | `bt_portal_toggle_documents` |
| ... | ... | ... |
| ✅ Apply Permissions | `success` | `bt_portal_perm_apply` |

### Browser Relay Execution — Set Permissions
1. Navigate to Job Details → Clients tab
2. Click client's contact card
3. Review **permissions** checkboxes
4. Toggle each feature according to selected package
5. Click **Save**
6. Snapshot → confirm permissions saved

---

## Step 3C: Send Portal Invitation
**Action:** Send the invitation email

**Message to the user:**
```
📧 Ready to invite [Client Name] to the portal!

They'll receive an email with a link to create their BT account.

Permissions set:
✅ Schedule
✅ Daily Logs
✅ Selections
✅ Invoices
✅ Photos

Send invitation?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📧 Send Invitation | `success` | `bt_portal_invite_send` |
| 🔐 Review Permissions First | `primary` | `bt_portal_invite_review` |
| ⏭️ Invite Later | `primary` | `bt_portal_invite_later` |

### Browser Relay Execution
1. Navigate to Job Details → Clients tab
2. Find client card → Click **"Send Invite"**
3. Preview invitation text (editable in Company Settings → Jobs tab)
4. Confirm send
5. Snapshot → verify invitation sent

**Report back:**
```
📧 Portal invitation sent!

👤 [Client Name]
📧 Sent to: [email]
📊 Status: Pending (awaiting account creation)

Once they create an account:
• Status changes to "Active"
• They can access all permitted features
• They'll get notifications based on settings
```

---

## Step 3D: Notification Settings
**Action:** Configure what notifications the client receives

**Message to the user:**
```
🔔 Notification preferences for [Client Name]:

How much should we notify them?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🔔 All Notifications | `primary` | `bt_portal_notif_all` |
| 🔔 Important Only (COs, Invoices, Selections) | `success` | `bt_portal_notif_important` |
| 🔕 Minimal (Invoices Only) | `primary` | `bt_portal_notif_minimal` |
| ✏️ Custom | `primary` | `bt_portal_notif_custom` |

### Notification Types
| Notification | All | Important | Minimal |
|-------------|-----|-----------|---------|
| Schedule changes | ✅ | ❌ | ❌ |
| Daily Logs posted | ✅ | ❌ | ❌ |
| New selection for review | ✅ | ✅ | ❌ |
| Change Order sent | ✅ | ✅ | ❌ |
| Invoice sent | ✅ | ✅ | ✅ |
| Payment received | ✅ | ✅ | ✅ |
| Document shared | ✅ | ❌ | ❌ |
| Photos uploaded | ✅ | ❌ | ❌ |
| Comment/message | ✅ | ✅ | ❌ |

### Notification Methods
- **Email** — default for all notifications
- **Text/SMS** — optional (client can enable)
- **Push notifications** — via BT mobile app

### Browser Relay Execution
1. Navigate to client card → Notification Settings
2. Toggle notification categories
3. Save changes

---

## Step 3E: Selection Presentations
**Action:** Set up selections for client review via portal

**Message to the user:**
```
🎨 Set up selections for [Client Name] to review?

This lets them browse options, see pricing vs allowance, and approve their choices — all through the portal.
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🎨 Set Up Selections | `success` | `bt_portal_sel_setup` |
| 📤 Send Existing Selections | `primary` | `bt_portal_sel_send` |
| ⏭️ Skip | `primary` | `bt_portal_sel_skip` |

If setting up selections: Follow `manage-selections.md` playbook.

If sending existing: Navigate to `/app/Selections/Default` → click Send on pending selections.

---

## Step 3F: Change Order Approval Flow
**Action:** Configure how COs are approved by the client

**Message to the user:**
```
📝 Change Order approval settings for [project]:

How should Change Orders be approved?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✍️ Require Client Signature | `success` | `bt_portal_co_signature` |
| ✅ Email Approval (No Signature) | `primary` | `bt_portal_co_email` |
| 🏢 Internal Approval Only | `primary` | `bt_portal_co_internal` |

### Signature Flow:
1. CO is created and sent to client
2. Client views CO in portal or email
3. Client clicks **Approve** → digital signature collected
4. Team notified of approval
5. If "Invoice upon client approval" is checked → auto-creates invoice

### Allow Client CO Requests
```
💡 Allow [Client Name] to submit Change Order Requests through the portal?

This lets them formally request scope changes, which you can review and approve/decline.
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Yes — Enable CO Requests | `success` | `bt_portal_co_requests_on` |
| ❌ No — Builder-Only | `primary` | `bt_portal_co_requests_off` |

### Browser Relay Execution
1. Navigate to Job Details → Clients tab
2. Find client → check/uncheck **"Change Order Requests"** permission
3. Save
4. Navigate to CO Settings if needed: `/app/Settings/ChangeOrderSettings`

---

## Step 3G: Online Payment Setup
**Action:** Enable client to pay invoices online via portal

**Message to the user:**
```
💳 Set up online payments for [project]?

Currently: [Active / Not Active]

Online payment allows clients to pay invoices via:
• Credit/debit card (2.99% fee)
• ACH bank transfer ($15 per transaction)
• Digital wallets

Processing: 3-5 business days
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 💳 Enable Online Payments | `success` | `bt_portal_payments_enable` |
| ⏭️ Skip — Use Offline Payments | `primary` | `bt_portal_payments_skip` |

**Note:** BT Online Payments requires enrollment. If not active:
```
⚠️ Online Payments is not currently active on your BT account.

To enable, contact BT:
📧 CSAE@buildertrend.com
👤 Dylan Chamberlain (Account Executive)

Requirements: Legal company name, EIN, 6-month business tenure, bank account info.
```

---

## Step 3H: Preview Client View
**Action:** See what the client sees

### Browser Relay Execution
1. Navigate to Job Details → Clients tab
2. Click **"Edit from Client Portal"** (preview button)
3. BT redirects to: `/app/ownerPortalRedirect/{jobId}/false`
4. Snapshot → capture client's view
5. Show to the user for review

**Message to the user:**
```
👁️ Client Portal Preview — [project]:

Here's what [Client Name] will see:
[snapshot of portal view]

Does this look right?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Looks Good | `success` | `bt_portal_preview_ok` |
| 🔐 Adjust Permissions | `primary` | `bt_portal_permissions` |
| 🔙 Back to Builder View | `primary` | `bt_portal_preview_exit` |

---

## Step 4: Post-Action
After portal configuration:

1. **Log to daily memory** — `memory/YYYY-MM-DD.md`
2. **Update Apple Reminders** — track client invitation status
3. **Notify the user** when client creates account (status changes from Pending → Active)
4. **Brief client on portal** — optionally create a welcome message or guide

---

## Client Status Lifecycle

| Status | Meaning | Action |
|---|---|---|
| Added | Contact in BT, no invitation | Send invite |
| Pending | Invitation sent, no account | Wait / resend |
| Active | Account created, portal active | Full access per permissions |
| Deactivated | Access revoked | Reactivate if needed |

---

## Multiple Clients per Job
Some projects have multiple client contacts (e.g., both spouses, developer + architect):

1. Add each contact separately
2. Set individual permissions per contact
3. Each gets their own invitation and login
4. Can set different notification preferences per contact

---

## Client Updates Feature
BT has an auto-update feature: `/app/ClientUpdates`

**Message to the user:**
```
📬 Enable weekly Client Updates for [project]?

BT can automatically send the client a weekly summary including:
• Schedule progress from the past 7 days
• Daily log activity
• Photo updates
• To-Do completion

Choose the day to send:
```

**Inline buttons (day of week):**
| Button | Style | callback_data |
|---|---|---|
| Mon | `primary` | `bt_portal_update_mon` |
| Fri | `primary` | `bt_portal_update_fri` |
| Sun | `primary` | `bt_portal_update_sun` |
| ⏭️ Skip | `primary` | `bt_portal_update_skip` |

### Browser Relay Execution
1. Navigate to `/app/ClientUpdates`
2. Select the day of week
3. Click **Save**

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Client email missing | Cannot invite — ask for email |
| Invitation bounced | Verify email address, resend |
| Client can't log in | Check invitation status, resend if needed |
| Portal preview not loading | Try different browser, check BT status |
| Online payments not available | Contact BT account rep for enrollment |
| Browser relay disconnected | Stop, ask the user to re-enable the extension |

---

## Default Invitation Text
Editable at: Company Settings → Jobs tab
Default text covers: welcome message, portal features, login instructions, mobile app download link.

---

## URL Patterns
| Page | URL |
|---|---|
| Job Clients Tab | `/app/JobPage/{jobId}/2?accessedFromContact=true` |
| Client Portal Preview | `/app/ownerPortalRedirect/{jobId}/false` |
| Client Updates | `/app/ClientUpdates` |
| Client Default Permissions | `/app/ClientJobPermissionSettings/Defaults` |
| Job Settings | `/app/Settings/JobSettings` |
| Change Order Settings | `/app/Settings/ChangeOrderSettings` |
| Invoice Settings | `/app/Settings/OwnerInvoiceSettings` |
| Online Payments | `/app/PaymentsOverview` |
