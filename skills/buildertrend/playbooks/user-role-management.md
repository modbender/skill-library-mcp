# User & Role Management
> Internal users, client contacts, roles, permissions, and security

## Trigger
- the user says "add user", "change permissions", "create custom role"
- New employee or team member needs BT access
- Role permissions need updating for a user

## Error Handling
| Issue | Resolution |
|---|---|
| Cannot add user | Only Org Owner/Admin can add internal users |
| Duplicate email error | Merge duplicate contacts via Contacts > Checked Actions |
| Permission change not saving | Ensure you click Save, check for required fields |
| User not receiving invite | Check email address, resend invite, check spam folder |
| BT session expired | Stop, notify the user to re-login |

---

## Overview
Buildertrend user management has three categories:
1. **Internal Users** — Your employees and team members
2. **Client Contacts** — Your project clients/homeowners
3. **Sub/Vendor Contacts** — Your trade partners (covered in sub-vendor-onboarding playbook)

Access is controlled through **Roles** (predefined or custom), which determine feature visibility and actions.

---

## INTERNAL USERS

### Adding Internal Users
*Only Org Owners and Admins can add/edit internal users.*

**Single User:**
1. Navigate to **Internal Users** from Users menu
2. Click **+Internal user**
3. Enter name, email, assign role
4. Click **Create** — invitation emailed automatically

**Multiple Users:**
1. Select **Invite multiple users** for bulk invitations

### User Statuses
| Status | Can Login | In Dropdowns | History Preserved |
|--------|-----------|-------------|-------------------|
| **Active** | ✅ | ✅ | ✅ |
| **Inactive** | ❌ | ✅ | ✅ |
| **Archived** | ❌ | ❌ | ✅ |
| **Deleted** | ❌ | ❌ | ⚠️ Partial* |

*Deleted users retain: Time Clock shifts, Comments, Created entities (Jobs, Bills, Invoices, etc.)*

> ⚠️ **Always archive instead of delete** to preserve historical data.

### Security & Login Management
From Internal Users > select user > **Security & Login** tab:
- **Login Access toggle:** Switch between Active/Inactive
- **Archive User:** Remove from dropdowns, prevent login, preserve history

### Notification Settings
Configure by Org Owners/Admins OR by individual users from User Settings.

**Methods:** Email, Text Message, Push (mobile app)

**Setup:**
1. Select user > **Notification Settings** tab
2. Expand feature/section drawers
3. Check boxes for Email, Text Message, or Push per alert type

> **Pro Tip:** If enforcing company-wide notification settings, communicate to team to prevent individual adjustments.

---

## BUILDERTREND ROLES

### Default Roles Reference

| Role | Best For | Key Access |
|------|----------|------------|
| **Org Owner** | Company owner/principal | Full access to everything |
| **Admin** | Office admin, operations lead | Same as Org Owner minus Subscription Management |
| **Project Manager** | PMs, superintendents | Full job access, no Sales/Internal Users/Client Invoices |
| **Office Manager** | Office coordinators | Most items, no Estimates or Warranty |
| **Bookkeeper** | Accounting staff | Financials and job-related items |
| **Selections Coordinator** | Design/selections staff | Selections, POs, COs with pricing |
| **Warranty Coordinator** | Post-construction staff | Warranty, To-Dos, communication tools |
| **Architect** | Design consultants | View-only COs and Selections (no pricing) |
| **Project Estimator** | Estimating team | Estimates, Bids, Selections, Bills/POs |
| **Sales Rep** | Individual salespeople | Own Leads, converts to Jobs |
| **Sales Manager** | Sales leadership | All Leads, Proposals, Estimates |
| **Field Crew** | Field workers, laborers | To-Dos, Daily Logs, Time Clock, Schedule |
| **Purchasing Coordinator** | Procurement staff | Financial tools with cost/price info |

### Job Status Access by Role
| Role | Presale | Open | Warranty | Closed |
|------|---------|------|----------|--------|
| Org Owner | ✅ | ✅ | ✅ | ✅ |
| Admin | ✅ | ✅ | ✅ | ✅ |
| Project Manager | ❌ | ✅ | ✅ | ✅ |
| Office Manager | ✅ | ✅ | ✅ | ✅ |
| Bookkeeper | ✅ | ✅ | ✅ | ✅ |
| Selections Coordinator | ✅ | ✅ | ❌ | ✅ |
| Warranty Coordinator | ❌ | ✅ | ✅ | ✅ |
| Architect | ✅ | ✅ | ❌ | ✅ |
| Project Estimator | ✅ | ✅ | ✅ | ✅ |
| Sales Rep | ✅ | ✅ | ✅ | ✅ |
| Sales Manager | ✅ | ✅ | ✅ | ✅ |
| Field Crew | ❌ | ✅ | ✅ | ❌ |
| Purchasing Coordinator | ✅ | ✅ | ✅ | ✅ |

### Creating Custom Roles
1. Navigate to **Role management** in Company Settings
2. Click **+Role**
3. Enter name and description
4. Set permissions using checkboxes: **View, Add, Edit, Delete** per feature
5. **Pro Tip:** Click **"Add from role"** to pre-populate from an existing role, then modify

### Assigning/Changing Roles
- From Internal Users > select user > **Permissions** tab
- View current role and included permissions
- Reassign to different role as needed
- BT default roles cannot be edited — create custom role instead

---

## CLIENT CONTACTS

### Creating a Client Contact
1. Navigate to **Client Contacts** from Users menu
2. Click **+Contact**
3. Enter name, address, phone, email
4. Click **Save**

> **Bulk upload:** BT Data Entry team can import full contact lists.

### Adding vs. Inviting (Important Distinction!)

| Action | What It Does | Portal Access? | Automatic? |
|--------|-------------|----------------|------------|
| **Adding** | Stores contact info, enables email updates | ❌ | — |
| **Inviting** | Grants Client Portal access | ✅ | Must click Send Invite separately |

> ⚠️ Always ADD first, then INVITE. Adding does NOT auto-send invitation.

### Adding Client to a Job
1. Navigate to **Job Details > Clients tab**
2. Click **+ New Contact** (create new) or **+ Existing Contact** (search existing)
3. Click **Save** to confirm

### Inviting Client to a Job
1. **Verify permissions first** — ensure they match intended access
2. Click **Send Invite** from client card in Clients tab
3. Client receives email to establish portal login
4. After login setup, they access Client Portal

### Client Permissions

#### Setting Default Permissions
1. Navigate to **Company Settings > Default Job Permissions**
2. Configure default access levels
3. Option to update existing jobs to match

#### Per-Job Permissions
Navigate to **Job Details > Clients tab** and configure:

**Project Management — View:**
- Share PM's phone number
- Show Locked Selections
- Schedule access (phases only vs all items)
- Schedule time frame (how far into future)

**Project Management — Submit:**
- Change Order requests
- Warranty claims

**Financial — View:**
- Job Price Summary
- Purchase Orders and Bills
- All Invoices (vs email-only)
- Budget (Legacy and/or Job Costing)
- Budget column selection
- Related items from budget

> **Pro Tip:** Click "Edit from Client Portal" to preview client's view of Selections.

### Common Client Contact Issues

| Issue | Solution |
|-------|----------|
| Duplicate email error on invite | Merge duplicates via Contacts > Checked Actions, or change Primary Email |
| Can't edit client info after activation | Only client can edit once active; you can add additional emails |
| Client profile picture | Only client can upload after activation |
| "Preview as Client" unavailable | Must assign contact to job first |
| Client on multiple jobs | Assign via Jobs List checked actions; client switches jobs via dropdown |

---

## COMPANY RECOMMENDED ROLE SETUP

### Suggested Role Assignments
| Person | Recommended Role | Notes |
|--------|-----------------|-------|
| the user | Org Owner | Full access |
| Project Managers | Project Manager | Standard PM access |
| Field Supervisors | Field Crew | Daily Logs, To-Dos, Time Clock, Schedule |
| Office Staff | Office Manager or custom | Depends on responsibilities |
| Bookkeeper/bookkeeper agent | Bookkeeper | Financials focus |

### Custom Role Considerations
- **Company PM+ Role:** PM role + Client Invoice access (if PMs handle invoicing)
- **Company Field Lead:** Field Crew + limited Bill creation (for receipt capture in field)
- **Company Estimator:** Project Estimator + Sales access (if estimators handle leads)
