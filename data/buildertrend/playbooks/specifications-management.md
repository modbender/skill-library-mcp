# Specifications Management
> Creating, sharing, templating, and linking project specifications

## Trigger
- the user says "create a spec", "add specifications", "scope documentation"
- New project needs scope of work documented
- Spec needs to be linked to a bid package or shared with subs

## Error Handling
| Issue | Resolution |
|---|---|
| Text editor not loading | Clear cache, try different browser, check BT status |
| Spec template not found | Check Settings > Templates > Specifications |
| Cannot share with sub | Verify sub is added to the job and has portal access |
| PDF export formatting broken | Try shorter section titles, reduce embedded images |
| BT session expired | Stop, notify the user to re-login |

---

## Overview
Project Specifications (Specs) document scope of work, materials, installation procedures, and more. Key uses:
- **Internal team** — Detailed scope for project execution
- **Clients** — Simplified version during proposal process
- **Subcontractors** — Detailed version during bidding process
- **Bids** — Linked to bid packages for sub reference

---

## Creating Specifications

### From Desktop
1. Navigate to **Project Management** dropdown > **Specifications**
2. Click **+ Specification**
3. Add content in the text editor:
   - Full text description of scope
   - Images (via toolbar)
   - Links (via toolbar)
4. Click **Publish**
5. Set **Viewing Permissions**:
   - ☐ Share with Client (view-only)
   - ☐ Share with Subs/Vendors (view-only)
6. Click **Publish** again to confirm

### Editing Specifications
- **From Book/List view:** Click the Edit icon
- **From within Spec:** Click the pencil icon
- Click **Save** when complete

### Managing Specifications
Use the **3 dots menu** (available in both views) for:
- Edit Viewing Permissions
- Print
- Delete

---

## Specification Templates

### Creating a Template (Full Job Copy)
1. Navigate to **Job Info**
2. Click the **3 dots** at bottom
3. Select **"Copy to Template"**
4. This copies ALL feature info from the job (excluding client details)
5. Delete unwanted info from template anytime

**Access:** Templates menu > Template List > select template > navigate to Specs via top navigation.

### Working Templates (Specs-Only)
For template that only includes Specs (not full job):
1. Go to **Job Info > Options**
2. Scroll to **Template Options**
3. Check **"Make this job a working template"**
4. Add a name, then Save

**Key difference:** Working templates don't appear in Templates menu. Used for importing onto specific features within other jobs.

---

## Linking Specifications to Bids

Specs can be attached to Bid packages before release to subs.

### How to Link
1. Navigate to **Financial > Bids**
2. Open an existing Bid or create a New Bid Package
3. Select **Link to Specifications**
4. Choose the desired Spec
5. Select **Add** (to link) or **Edit** (to modify first)

### Important Rules
| Rule | Detail |
|------|--------|
| No deletion after linking | Once Spec is linked and Bid is saved, Spec cannot be deleted |
| No editing on released Bids | Spec cannot be edited if Bid is released; must reopen/unrelease first |
| Warning on release | Reminder appears when releasing Bid with linked Spec |

### Sub Access to Specs via Bids
- **External subs** (not in BT): See Spec info embedded within the Bid
- **In-BT subs:** Have view and print access to the Spec
- **Bids visible from within Spec** once linked (two-way navigation)

---

## Permissions
Internal Users (including Custom Roles) need specific permissions:
- **View** — See specifications
- **Add** — Create new specifications
- **Edit** — Modify existing specifications
- **Delete** — Remove specifications

Configure in Role Management (Company Settings).

---

## Best Practices for {{company_name}}

### Spec Organization
1. **Create a master Spec template** for each job type (commercial TI, residential renovation, etc.)
2. **Use categories** for sections: Demolition, Framing, Electrical, Plumbing, HVAC, Finishes, etc.
3. **Include images** — Reference photos, detail drawings, product cut sheets
4. **Link product URLs** for material specifications

### Workflow
1. **Pre-bid:** Create detailed Spec → Link to Bid Package → Release to subs
2. **Post-award:** Update Spec with awarded sub's details → Share with client (simplified)
3. **During construction:** Reference Spec for scope verification → Update as changes occur
4. **Use Change Orders** when spec changes affect contract price

### Sharing Strategy
| Audience | What to Share | When |
|----------|---------------|------|
| Internal team | Full detailed Spec | Job setup |
| Clients | Simplified scope overview | Proposal stage |
| Subcontractors | Detailed scope + materials | Via Bid packages |
| Installers | Approved choices + install notes | Post-selection |

### Template Maintenance
- Review and update master templates quarterly
- Include latest material specs, code requirements
- Note regional requirements (local building code requirements)
