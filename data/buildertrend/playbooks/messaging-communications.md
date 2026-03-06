# Messages, Comments & Notifications (Agent-Assisted)

## Overview
Manage all communication channels in Buildertrend — internal messages, feature comments, RFI-linked threads, email integration, notification preferences, and batch communications. BT provides multiple communication layers: Messages (email-style), Comments (feature-attached), Chat (real-time), and automated Notifications.

## Trigger
- the user says "message [sub/client]", "check messages", "notify all subs on [project]"
- New unread messages or comments detected
- Need to send batch communication to all trades on a job
- Review notification settings or activity feed
- "What's the latest on [project]?" — pull activity/comment threads

---

## Step 1: Navigate to Messaging Hub
**Action:** Open Messages inbox

```
browser → navigate to https://buildertrend.net/app/Messages/Inbox
browser → snapshot → verify Messages page loaded
```

**Messaging Menu URLs:**
| Feature | URL | Description |
|---|---|---|
| Comments | `/app/Comments/Conversation` | Conversation-style comments on features |
| Messages | `/app/Messages/Inbox` | Email/message inbox |
| RFIs | `/app/RFIs` | Formal requests for information |
| Notification History | `/app/NotificationHistory` | Sent notification log |
| Surveys | `/app/Surveys/Individual` | Client/sub surveys |
| Chat | `/app/Chat` | Real-time messaging |

**Present to the user:**
```
📬 Message Center:
• Unread messages: [X]
• Recent comments: [Y]
• Open RFIs: [Z]
```

---

## Step 2: Send a Direct Message

### Internal Message
**Action:** Compose and send a message to internal users, subs, or clients

```
browser → snapshot → click "Compose" or "New Message" button
browser → snapshot → select recipients (To field)
browser → snapshot → enter Subject
browser → snapshot → compose message body (rich text editor)
browser → snapshot → attach files if needed
browser → snapshot → click "Send"
browser → snapshot → verify message sent
```

| Field | Type | Required | Notes |
|---|---|---|---|
| To | Combobox (multi-select) | **Yes** | Internal users, subs, clients |
| Subject | Text input | **Yes** | Message subject line |
| Body | Rich text (CKEditor) | **Yes** | Full formatting toolbar |
| Attachments | File upload | No | Documents, photos |
| Job | Combobox | No | Associate with a specific job |

**Message to the user:**
```
📧 Message sent:
• To: [recipient(s)]
• Subject: [subject]
• Job: [project if specified]
```

---

## Step 3: Feature Comments
**Action:** Add comments to specific BT features (bills, POs, daily logs, schedule items, RFIs, change orders, etc.)

### How Comments Work
- Every feature in BT supports a Comments section
- Comments are threaded and timestamped
- Visibility depends on the feature's sharing settings
- Comments create a documented conversation trail

### Adding a Comment
```
browser → snapshot → navigate to the feature item (e.g., a specific bill, PO, schedule item)
browser → snapshot → scroll to Comments section at bottom
browser → snapshot → click comment text area
browser → snapshot → type comment text
browser → snapshot → click "Post" / "Save"
browser → snapshot → verify comment posted
```

### Comment Visibility Rules
| Feature | Who Sees Comments |
|---|---|
| Bills | Internal users + assigned vendor (if shared) |
| Purchase Orders | Internal users + assigned sub/vendor |
| Daily Logs | Based on sharing settings (Internal/Sub/Client/Private) |
| Schedule Items | Assigned users + visibility settings |
| Change Orders | Internal + client (if sent) + assigned subs |
| RFIs | All assigned parties |
| Selections | Internal + client + vendor/installer |
| Warranty | Internal + assigned sub + client (if permitted) |

**Comments URL:** `/app/Comments/Conversation` — conversation-style view across all features

---

## Step 4: Chat (Real-Time)
**Action:** Use BT's built-in chat for instant messaging

```
browser → navigate to https://buildertrend.net/app/Chat
browser → snapshot → verify Chat page loaded
```

- Real-time messaging between internal users
- Job-linked conversations
- Available on desktop and mobile

---

## Step 5: Notification Settings
**Action:** Review and configure notification preferences

### Company-Level Settings
Access from Company Settings pages for each feature:
- Schedule: `/app/Settings/ScheduleSettings`
- Daily Logs: `/app/Settings/DailyLogSettings`
- Change Orders: `/app/Settings/ChangeOrderSettings`
- Warranty: `/app/Settings/WarrantySettings`
- Time Clock: `/app/Settings/TimeClockSettings`
- Bids: `/app/Settings/BidSettings`
- Bills/POs: `/app/Settings/BudgetSettings`
- Invoices: `/app/Settings/OwnerInvoiceSettings`

### Per-User Notification Settings
Org Owners/Admins can configure per user, or users configure their own:
- **Email notifications** — sent to registered email
- **Text (SMS) notifications** — sent to phone number
- **Push notifications** — mobile app alerts
- Collapsible drawers for each feature/section

### Automated Notification Triggers
| Event | Who Gets Notified | Method |
|---|---|---|
| Schedule item created/changed | Assigned subs + team | Email, Push |
| Schedule shift reason | Affected subs + team | Email |
| PO released | Assigned sub/vendor | Email |
| Invoice sent | Client(s) | Email |
| CO sent for approval | Client(s) | Email |
| CO approved | Assigned subs + team | Email, Push |
| Daily Log published | Notified users (configurable) | Email |
| Warranty claim submitted | Coordinator + team | Email, Push |
| Bill approaching due date | Assigned approvers | Email |
| Selection deadline approaching | Client(s) | Email |
| RFI created/response due | Assigned party | Email |
| Time Clock shift approved | Employee | Push |
| Bid package deadline reminder | Subs/vendors (X days before) | Email |
| Client payment received | Internal users (configurable) | Email |

### Schedule Change → Sub Notification
When a schedule item is modified while schedule is Online:
1. BT prompts for Shift Reason and Notes
2. Notification sent to all assigned subs/vendors
3. Subs can Confirm or Decline updated timing

### Invoice → Client Notification
When invoice is sent:
1. Click "Send" on invoice
2. Select which clients receive email
3. Active clients: email + portal notification
4. Inactive clients: email only

---

## Step 6: Notification History
**Action:** Review all sent notifications

```
browser → navigate to https://buildertrend.net/app/NotificationHistory
browser → snapshot → review notification log
```

**Notification History shows:**
- Timestamp of each notification
- Type (email, push, text)
- Recipient
- Feature/event that triggered it
- Delivery status

---

## Step 7: Message Templates
**Action:** Set up reusable message templates for common communications

### Where Templates Live
| Template Type | Settings Location | Purpose |
|---|---|---|
| Sub/Vendor Invitation | Company Settings → Jobs → Invitation text | Default invite email |
| Client Invitation | Company Settings → Jobs → Client invitation | Portal invite email |
| Bid Request Notification | Company Settings → Bids → Default notification | Bid package emails |
| PO Scope of Work | Per PO | Default scope text |
| Invoice Description | Company Settings → Invoices → Default description | Invoice email body |
| CO Introduction/Closing | Per CO or Company Settings → COs | Change order cover text |
| Proposal Intro/Closing | Company Settings → Estimates → Job Proposal Format | Proposal cover text |

### Custom Text in Features
- Change Orders: Introduction Text + Closing Text (per CO, rich text)
- Proposals: Introductory Text + Closing Text (per proposal, rich text)
- POs: Scope of Work (per PO)
- Invoices: Invoice Description (per invoice, rich text)
- Bids: Bid request body text

---

## Step 8: Batch Communication
**Action:** Notify all subs/vendors on a job at once

### Method 1: Schedule Online Toggle
When schedule goes from Offline → Online:
- All assigned subs receive notifications for their schedule items
- Enable: Schedule → toggle Online switch

### Method 2: Mass PO Release
```
browser → navigate to https://buildertrend.net/app/PurchaseOrders
browser → snapshot → check boxes on multiple POs
browser → snapshot → use mass action "Release" / "Send"
browser → snapshot → verify all subs notified
```

### Method 3: Direct Message to All Job Contacts
```
browser → navigate to https://buildertrend.net/app/Messages/Inbox
browser → snapshot → click "Compose" / "New Message"
browser → snapshot → in To field, add all subs/vendors assigned to job
browser → snapshot → compose batch message
browser → snapshot → click "Send"
browser → snapshot → verify sent
```

### Method 4: Client Updates (Weekly Auto-Send)
**URL:** `/app/ClientUpdates`
- Configure day of week for weekly auto-send
- BT compiles past 7 days of activity (photos, daily logs, schedule progress)
- Sends to all clients on all jobs company-wide

```
browser → navigate to https://buildertrend.net/app/ClientUpdates
browser → snapshot → select day of week for auto-send
browser → snapshot → configure included content
browser → snapshot → click "Save"
```

---

## Step 9: Activity Feed / Audit Trail
**Action:** Review all activity on a feature or job

### Feature-Level History
Most BT features have a "History" tab showing:
- Who created/edited/deleted the item
- Timestamp of each change
- What was changed (old value → new value)
- Schedule History: `/app/Schedules/0/ScheduleHistory/{jobId}`

### Job-Level Activity
- Daily Logs capture daily progress
- Comments on features create conversation trail
- Notification History shows all outbound communications

**Message to the user:**
```
📊 Activity Summary for [Project]:
• Last daily log: [date]
• Recent comments: [count] in past 7 days
• Notifications sent: [count] in past 7 days
• Open RFIs: [count]
• Pending approvals: [count]
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| 📋 View All Comments | `primary` | `msg_comments_all` |
| 📧 View Notification History | `primary` | `msg_notif_history` |
| 💬 Send Message | `success` | `msg_compose` |
| 📢 Notify All Subs | `primary` | `msg_batch_subs` |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Recipient not found | Check user is active and has email address |
| Sub not invited to BT | Can still receive email notifications (not portal) |
| Message failed to send | Check internet, retry, report to the user |
| Notifications disabled for user | Check user notification settings, advise enabling |
| Comments section not visible | Check feature sharing/visibility settings |

---

## Quick Reference: Communication Channels

| Channel | Best For | Speed | Documentation |
|---|---|---|---|
| **Messages** | Formal communications, multi-party | Async | ✅ Logged |
| **Comments** | Feature-specific discussion | Async | ✅ Attached to feature |
| **Chat** | Quick internal questions | Real-time | ✅ Logged |
| **RFIs** | Formal questions needing answers | Async + deadline | ✅ Full audit trail |
| **Notifications** | Automated alerts | Instant | ✅ In Notification History |
| **Client Updates** | Weekly progress reports | Weekly auto | ✅ Compiled from activity |
| **Surveys** | Feedback collection | Async | ✅ Logged |

---

## Company-Specific Notes
- **4 internal users:** Administrative Assistant, {{team_member}}, {{owner_name}}, {{team_member}}
- Primary communication channel with {{company_name}}: messaging platform
- BT messages supplement messaging platform for formal/documented communications
- All schedule change notifications go to assigned subs automatically
- Client Updates not yet configured — recommend setting to Friday for weekly recap
