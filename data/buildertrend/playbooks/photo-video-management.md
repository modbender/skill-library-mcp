# Photo & Video Documentation

## Overview
Upload, organize, annotate, and share construction photos and videos in Buildertrend. Document site progress at every phase, attach media to daily logs, RFIs, to-dos, warranty claims, and selections. Share with clients via portal and maintain a complete visual record of every project.

## Trigger
- "Upload photos for [project]", "add site photos"
- "Create album for [phase]", "organize photos"
- "Share photos with client", "photo markup"
- "Upload video walkthrough", "site documentation"
- "Before/after photos for [area]"
- Daily log creation (auto-attach photos)

---

## Step 1: Navigate to Photos/Videos
**Action:** Open the media management page for the correct project

### Browser Relay Steps
1. Select job in left sidebar (or navigate via Jobs menu)
2. Navigate to:
   - Photos: `/app/Photos/Standard/0`
   - Videos: `/app/Videos/Standard/0`
3. Snapshot → confirm correct job and existing albums

**Present to the user:**
```
📸 Photos for [Project Name]:
• Albums: [list existing albums]
• Total photos: [count]
• Last upload: [date]

What would you like to do?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📤 Upload photos | `primary` | `bt_photo_upload` |
| 📁 Create new album | `primary` | `bt_photo_album` |
| ✏️ Annotate/markup | `primary` | `bt_photo_markup` |
| 👁️ Share with client | `primary` | `bt_photo_share` |
| 🎥 Upload video | `primary` | `bt_video_upload` |
| 📋 View all photos | `primary` | `bt_photo_viewall` |

---

## Step 2: Upload Photos
**Action:** Upload photos to a job album

### Browser Relay Steps
1. On Photos page, click "Upload" or drag-and-drop area
2. Select files (supports .jpg, .png, .heic, .gif, .webp)
3. Choose or create album for organization
4. Set sharing permissions:
   - Internal Users only (default)
   - Subs/Vendors
   - Client (visible in portal)
5. Add tags if applicable
6. Click Upload / Save
7. Snapshot → confirm upload success

**From Mobile (field crew instructions):**
1. Open BT mobile app
2. Select job
3. Tap Photos
4. Tap camera icon or upload icon
5. Take photo or select from gallery
6. Assign to album
7. Photo auto-uploads with date/time/GPS metadata

---

## Step 3: Create & Organize Albums
**Action:** Set up album structure for the project

### Company Standard Album Structure
| Album Name | Phase | Contents |
|---|---|---|
| 📋 Pre-Construction | Before work | Existing conditions, site survey, pre-demo state |
| 🔨 Demolition | Demo phase | Demo progress, hazmat abatement, structural findings |
| 🏗️ Rough-In — Framing | Rough | Framing, structural steel, blocking |
| 🔌 Rough-In — MEP | Rough | Electrical, plumbing, HVAC rough-in |
| 🧱 Rough-In — Other | Rough | Insulation, drywall, fire protection |
| 🔍 Inspections | Throughout | DOB inspections, special inspections, testing |
| 🎨 Finishes | Finish phase | Paint, tile, flooring, millwork, countertops |
| 🚪 Fixtures & Hardware | Finish | Doors, hardware, lighting, plumbing fixtures |
| ✅ Punch List | Closeout | Items flagged during walkthrough |
| 📦 Closeout | Final | Final condition, as-built photos, completion |
| ⚠️ Issues & Defects | Any time | Deficiencies, damage, rework needed |
| 📄 Documents & Receipts | Any time | Photo'd receipts, delivery tickets, labels |

### Browser Relay Steps
1. On Photos page, click "New Album" or "Create Folder"
2. Enter album name from {{company_name}} standard list
3. Set permissions (who can see this album)
4. Save
5. Repeat for additional albums

---

## Step 4: Annotate / Markup Photos
**Action:** Add markup annotations for team communication

### Browser Relay Steps
1. Click on a photo to open it
2. Click "Annotate" or "Markup" tool
3. Available tools:
   - ✏️ Freehand draw (red, blue, black)
   - 📝 Text labels
   - ➡️ Arrows and pointers
   - 🔲 Shapes (rectangle, circle, line)
4. Add annotation explaining the issue/note
5. Save markup
6. Photo now shows as annotated in album

**Use Cases:**
- Circle a defect and add "FIX THIS" label
- Arrow pointing to incorrect installation
- Note dimensions or materials on a rough-in photo
- Mark up a plan photo with field observations

---

## Step 5: Attach Photos to Other BT Features
**Action:** Link photos to daily logs, RFIs, to-dos, warranty claims, selections

### Attach to Daily Log
1. Create or edit Daily Log (`/app/DailyLogs`)
2. In Attachments section, click "Add file"
3. Select from job's photo library or upload new
4. Photos appear in the daily log entry

### Attach to RFI
1. Open RFI (`/app/RFIs`)
2. Click attachments area
3. Add photos documenting the question/issue
4. Sub/architect sees photos with the RFI

### Attach to To-Do / Punch List
1. Open task (`/app/tasks`)
2. In detail panel, click "Upload" or "Add" attachment
3. Select relevant photos
4. Assignee sees photos with the task

### Attach to Warranty Claim
1. Open warranty (`/app/Warranties`)
2. Add photos of the warranty issue
3. Photos shared with sub responsible for repair

### Attach to Selection
1. Open selection (`/app/Selections/Default`)
2. Add product/finish photos for client review
3. Client sees options in their portal

---

## Step 6: Share Photos with Client via Portal
**Action:** Make photos visible to the client in their BT portal

### Browser Relay Steps
1. Navigate to Photos → select album or photos
2. Check sharing permissions → enable "Client" visibility
3. Client can view in their portal at `/app/ownerPortalRedirect/{jobId}/false`
4. Optionally send notification to client about new photos

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 👁️ Share album with client | `success` | `bt_photo_share_client` |
| 🔒 Keep internal only | `primary` | `bt_photo_internal` |
| 📧 Notify client of new photos | `primary` | `bt_photo_notify` |

---

## Step 7: Video Upload & Organization
**Action:** Upload and organize job videos

### Browser Relay Steps
1. Navigate to `/app/Videos/Standard/0`
2. Click upload area
3. Select video file (common formats: .mp4, .mov, .avi)
4. Set title and description
5. Assign to folder/category
6. Set sharing permissions
7. Save

**Company Video Types:**
| Type | When | Purpose |
|---|---|---|
| Site walkthrough | Weekly | Progress documentation |
| Issue documentation | As needed | Defect/problem evidence |
| Inspection video | At inspections | Record inspector comments |
| Client update | Milestone | Share progress with client |
| Time-lapse | Ongoing | Daily photo compilation |
| Safety briefing | Start of job | Document safety training |

---

## Step 8: Before/After Documentation
**Action:** Create paired before/after photo sets

### Company Standard Before/After Protocol
1. **Before:** Photograph area BEFORE work begins
   - Capture existing conditions from multiple angles
   - Include wide shot + detail shots
   - Note any pre-existing damage
   - Album: "Pre-Construction" or relevant phase album

2. **After:** Photograph same area AFTER work complete
   - Match angles from "before" photos
   - Capture completed work quality
   - Include detail shots of finish work
   - Album: Relevant phase album (e.g., "Finishes")

3. **Organize:** Name convention
   - `[Area] - Before - [Date]`
   - `[Area] - After - [Date]`

---

## Company Site Documentation Standards

### What to Photograph (Every Project)
| Phase | Required Photos |
|---|---|
| Pre-Demo | All rooms/areas, existing conditions, utilities, structural |
| Demolition | Progress daily, hazmat findings, structural reveals |
| Rough-In | All MEP before closing walls, blocking, fire stopping |
| Inspections | Inspector on site, inspection cards, test results |
| Drywall | Before taping, after taping, before paint |
| Finishes | Each trade's completed work, detail shots |
| Punch List | Each punch item with annotation |
| Final | All rooms complete, exterior, equipment labels, as-built |

### Photo Naming Best Practice
```
[Date]_[Area]_[Trade]_[Description]
2026-02-19_Kitchen_Plumbing_RoughInComplete
2026-02-19_Bathroom2_Tile_GroutDrying
```

---

## Smart Suggestions

| Context | Suggestion |
|---|---|
| Daily log created without photos | "Want to attach site photos to today's log?" |
| RFI created about a visual issue | "Upload a photo to make this RFI clearer" |
| Punch list walkthrough happening | "Time to photograph punch list items" |
| Inspection scheduled tomorrow | "Reminder: photograph conditions before/during inspection" |
| Client meeting prep | "Want to share latest photos with client?" |
| Project milestone reached | "Create a progress video update for the client?" |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Upload fails | Check file size/format. Max size varies. Try smaller file or different format |
| Photo won't display | May be corrupt file — try re-uploading |
| Album permissions wrong | Edit album → update sharing settings |
| Video too large to upload | Compress video or split into segments |
| Browser relay disconnected | Stop, ask the user to re-enable extension |
| Mobile upload not syncing | Check internet connection on mobile device, force-refresh app |

---

## Batch Mode
When uploading multiple photos for a site visit:

1. Select all photos for upload (bulk select)
2. Assign to correct album
3. Set permissions (internal, subs, client)
4. Bulk upload → wait for all to process
5. Confirm: "Uploaded [X] photos to [album] for [project]"

**Progress tracking:**
```
📸 Uploading site photos...
✅ 15/20 photos uploaded
⏳ Processing remaining 5...
✅ All 20 photos uploaded to "Rough-In — MEP" album
```

---

## URL Patterns
| Page | URL |
|---|---|
| Photos | `/app/Photos/Standard/0` |
| Videos | `/app/Videos/Standard/0` |
| Documents | `/app/Documents/Standard/0` |
| Daily Logs | `/app/DailyLogs` |
| Tasks | `/app/tasks` |
| RFIs | `/app/RFIs` |
| Warranties | `/app/Warranties` |
| Selections | `/app/Selections/Default` |
| Client Portal | `/app/ownerPortalRedirect/{jobId}/false` |
| Files Settings | `/app/Settings/MediaSettings` |
