# Document & File Management (Agent-Assisted)

## Overview
The agent helps the user upload, organize, and manage documents in Buildertrend — including plans, contracts, submittals, COIs, photos, and videos. Files can be organized into folder structures per job, attached to relevant BT features (bills, POs, RFIs, daily logs), and shared with subs and clients via their portals. This playbook also covers version tracking for drawings and bulk uploads.

## Trigger
- the user says "upload [document type] to [project]" or "add plans to BT"
- Sub sends COI or submittal → needs to be filed in BT
- New plan revision arrives → upload and track version
- Need to share documents with sub or client via portal
- the user asks "where's the [document] for [project]?"
- Bulk upload: multiple documents need to be filed at once

---

## Step 1: Identify Project
**Action:** Confirm which project

**Message to the user:**
```
📁 Document Management — which project?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🏗️ Project Alpha | `primary` | `bt_doc_project_1` |
| 🏗️ Project Alpha | `primary` | `bt_doc_project_1` |
| 🏗️ Project Beta | `primary` | `bt_doc_project_2` |
| 🏗️ Project Beta | `primary` | `bt_doc_project_2` |
| 🏗️ Project Epsilon | `primary` | `bt_doc_project_3` |
| 🏗️ Project Gamma | `primary` | `bt_doc_project_4` |
| 🏗️ Project Eta | `primary` | `bt_doc_project_5` |
| 🏢 Global Documents | `primary` | `bt_doc_project_global` |
| ❌ Cancel | `danger` | `bt_doc_cancel` |

---

## Step 2: Choose Action
**Message to the user:**
```
📁 Documents for [project] — what do you need?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📤 Upload Document | `success` | `bt_doc_upload` |
| 📁 Browse Job Files | `primary` | `bt_doc_browse` |
| 📎 Attach to Feature | `primary` | `bt_doc_attach` |
| 📤 Share with Sub/Client | `primary` | `bt_doc_share` |
| 📋 Upload Plans/Drawings | `primary` | `bt_doc_plans` |
| 📸 Upload Photos | `primary` | `bt_doc_photos` |
| 📦 Bulk Upload | `primary` | `bt_doc_bulk` |
| ❌ Cancel | `danger` | `bt_doc_cancel` |

---

## Step 3A: Upload Document

### Document Type Selection
**Message to the user:**
```
📤 What type of document?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📋 Plans / Drawings | `primary` | `bt_doc_type_plans` |
| 📝 Contract / Agreement | `primary` | `bt_doc_type_contract` |
| 📄 Submittal | `primary` | `bt_doc_type_submittal` |
| 🛡️ COI / Insurance | `primary` | `bt_doc_type_coi` |
| 📄 Permit / Filing | `primary` | `bt_doc_type_permit` |
| 📊 Report / Inspection | `primary` | `bt_doc_type_report` |
| 📸 Photo(s) | `primary` | `bt_doc_type_photo` |
| 🎥 Video | `primary` | `bt_doc_type_video` |
| 📄 Other | `primary` | `bt_doc_type_other` |

### Folder Selection
**Smart folder suggestion based on document type:**
| Document Type | Suggested BT Folder | Also File to Drive |
|---|---|---|
| Plans / Drawings | Plans and Specs tab | Projects/[Job]/Other Documents |
| Contract | Documents → Contracts folder | Projects/[Job]/Other Documents |
| Submittal | Documents → Submittals folder | Projects/[Job]/Other Documents |
| COI / Insurance | Documents → Insurance folder | Vendors & Subs/[Vendor] |
| Permit | Documents → Permits folder | Projects/[Job]/Other Documents |
| Report | Documents → Reports folder | Projects/[Job]/Other Documents |
| Photo | Photos tab | Projects/[Job]/Other Documents |
| Video | Videos tab | Projects/[Job]/Other Documents |

**Message to the user:**
```
📁 Suggested folder: [folder name]

Upload to this folder or choose another?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Use Suggested Folder | `success` | `bt_doc_folder_suggested` |
| 📁 Choose Different Folder | `primary` | `bt_doc_folder_choose` |
| ➕ Create New Folder | `primary` | `bt_doc_folder_new` |

### Upload via Browser Relay
**Message to the user:**
```
📤 Send me the file(s) and I'll upload to BT.

Or tell me where to find them:
• On the Mac (file path)
• Google Drive link
• Already in BT (attach to feature)
```

---

## Step 3B: Upload Plans/Drawings (Version Tracking)

### Plans and Specs Module
**Message to the user:**
```
📋 Plans Upload — [project]:

Is this a new plan set or a revision of existing drawings?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 🆕 New Plan Set | `success` | `bt_doc_plan_new` |
| 🔄 Revision of Existing | `primary` | `bt_doc_plan_revision` |

### For Revisions:
```
📋 Which plan set is being revised?

Current plans on file:
[list current plans from BT]
```

**Version tracking message:**
```
📋 Plan Revision Uploaded:

📄 Title: [plan name]
🔄 Version: Rev [X] → Rev [X+1]
📅 Date: [today]
📎 Previous version: [archived / still accessible]
🏗️ Project: [project]

⚠️ Notify subs/team about new revision?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📧 Notify All Assigned Subs | `success` | `bt_doc_plan_notify_all` |
| 📧 Notify Specific Subs | `primary` | `bt_doc_plan_notify_select` |
| ⏭️ Don't Notify | `primary` | `bt_doc_plan_no_notify` |

### Browser Relay Execution (Plans)
1. Navigate to `/app/Plans`
2. Snapshot → verify Plans and Specs page
3. Click **"Create new Plan"** or upload button
4. Upload the plan file
5. Set title, version info
6. Snapshot → confirm uploaded
7. If sharing: set visibility permissions

---

## Step 3C: Browse Job Files
**Action:** Navigate the file structure in BT

### Browser Relay Execution
1. Navigate to `/app/Documents/Standard/0` (Documents)
2. Snapshot → parse folder structure and file list
3. Present to the user

**Message to the user:**
```
📁 Files — [project]:

📂 Contracts
  └ [contract_v2.pdf] — uploaded Jan 15
📂 Submittals
  └ [door_hardware_submittal.pdf] — uploaded Feb 1
  └ [tile_submittal.pdf] — uploaded Feb 10
📂 Insurance
  └ [ABC_Plumbing_COI.pdf] — uploaded Dec 20
📂 Permits
  └ (empty)
📸 Photos: [N] photos
🎥 Videos: [N] videos

What would you like to do?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📤 Upload to Folder | `primary` | `bt_doc_upload_to` |
| 📎 Attach File to Feature | `primary` | `bt_doc_attach` |
| ➕ Create New Folder | `primary` | `bt_doc_folder_new` |
| 🔄 Refresh | `primary` | `bt_doc_refresh` |

---

## Step 3D: Attach to Feature
**Action:** Link a document to a BT feature (bill, PO, RFI, daily log, CO, etc.)

**Message to the user:**
```
📎 Attach document to which feature?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 💰 Bill | `primary` | `bt_doc_attach_bill` |
| 📦 Purchase Order | `primary` | `bt_doc_attach_po` |
| ❓ RFI | `primary` | `bt_doc_attach_rfi` |
| 📝 Daily Log | `primary` | `bt_doc_attach_dailylog` |
| 📝 Change Order | `primary` | `bt_doc_attach_co` |
| 📅 Schedule Item | `primary` | `bt_doc_attach_schedule` |
| 🎨 Selection | `primary` | `bt_doc_attach_selection` |

**After feature type selected:** Show list of specific items (e.g., list of bills) → select one → upload/attach the file in that feature's detail page.

---

## Step 3E: Share with Sub/Client
**Action:** Set document visibility for external parties

**Message to the user:**
```
📤 Share document — who should see this?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 👷 Subs/Vendors | `primary` | `bt_doc_share_subs` |
| 👤 Client | `primary` | `bt_doc_share_client` |
| 👷👤 Both | `primary` | `bt_doc_share_both` |
| 🔒 Internal Only | `primary` | `bt_doc_share_internal` |

### Browser Relay Execution
1. Navigate to the file/folder in BT
2. Set visibility permissions:
   - **Documents:** folder-level permissions (subs can view permitted folders)
   - **Photos/Videos:** visibility settings on upload
   - **Feature attachments:** inherit feature visibility
3. Snapshot → confirm sharing settings

---

## Step 3F: Bulk Upload
**Action:** Upload multiple files at once

**Message to the user:**
```
📦 Bulk Upload — [project]:

Send me the files (up to 20 at a time) or tell me the folder path on the Mac.

I'll auto-sort by type:
• PDFs → Documents
• Images → Photos
• Videos → Videos
```

### Bulk Upload Flow:
1. Receive files from the user (via messaging or file path)
2. Sort by file type
3. Present summary:

```
📦 Bulk Upload Ready — [N] files:

📄 Documents: [N]
  • [filename1.pdf] → Contracts folder
  • [filename2.pdf] → Submittals folder
📸 Photos: [N]
  • [photo1.jpg]
  • [photo2.jpg]

Upload all to [project]?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Upload All | `success` | `bt_doc_bulk_upload` |
| ✏️ Change Folders | `primary` | `bt_doc_bulk_edit` |
| ❌ Cancel | `danger` | `bt_doc_bulk_cancel` |

4. Execute uploads sequentially via Browser Relay
5. Report progress: "Uploaded [N]/[total] files"

---

## Step 4: Post-Action
After document management actions:

1. **Log to daily memory** — `memory/YYYY-MM-DD.md`
2. **Cross-file to Google Drive** — if document should also be in {{company_name}}'s Drive
   - Plans → Projects/[Job]/Other Documents
   - COIs → Vendors & Subs/[Vendor name]
   - Contracts → Projects/[Job]/Other Documents
3. **Notify relevant agents:**
   - receipt agent — COI received, file for records
   - procurement agent — submittal uploaded, track review status

---

## Folder Structure Best Practices (BT)
Recommended folder structure per job:

```
📁 [Job Name]
├── 📂 Contracts
├── 📂 Submittals
├── 📂 Insurance (COIs)
├── 📂 Permits & Filings
├── 📂 Shop Drawings
├── 📂 Correspondence
├── 📂 Meeting Minutes
├── 📂 Reports & Inspections
├── 📂 Close-Out
└── 📂 Misc
```

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| File too large | Compress or split, notify the user of size limit |
| Unsupported file type | Convert to supported format (PDF recommended for docs) |
| Folder doesn't exist | Create new folder, then upload |
| Permission denied | Check role permissions, escalate to admin |
| Upload fails mid-batch | Note which files uploaded, retry remaining |
| Browser relay disconnected | Stop, ask the user to re-enable the extension |

---

## URL Patterns
| Page | URL |
|---|---|
| Documents | `/app/Documents/Standard/0` |
| Photos | `/app/Photos/Standard/0` |
| Videos | `/app/Videos/Standard/0` |
| Plans and Specs | `/app/Plans` |
| Files Settings | `/app/Settings/MediaSettings` |
