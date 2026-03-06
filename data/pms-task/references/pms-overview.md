# PMS Domain Overview

## What is PMS?

**POD Management System (PMS)** - A role-based dashboard for **Apni Pathshala** POD operations.

**Apni Pathshala** is an education initiative with multiple PODs (Points of Delivery) - learning centers where students receive education.

## Core Entities

### POD (Point of Delivery)
A learning center/location where education is delivered.

**Key Fields:**
- `name` - POD name
- `code` - Unique identifier
- `status` - ACTIVE / INACTIVE / ONBOARDING
- `phase` - Current phase of POD
- `type` - NON_PROFIT / FOR_PROFIT / etc.
- `podLeaderName` - Leader of the POD
- `leaderIds` - Multiple leaders can manage a POD
- `numberOfStudents` - Student count
- `city`, `district`, `state` - Location
- `cluster`, `region` - Organizational grouping
- `redFlags` - Issue counter (max configurable)

### User Roles
Role-based access control with granular permissions.

**Built-in Roles:**
- `SUPER_ADMIN` - Full system access (priority 9)
- Custom roles created by admins

**Modules Available:**
- DASHBOARD
- APPLICATIONS
- PODS
- STUDENTS
- INVENTORY
- WEEKLY_REPORTS
- MONTHLY_REPORTS
- COMPLAINTS
- COMMUNICATIONS
- SUCCESS_STORIES
- EMAIL_TEMPLATES
- API_WEBHOOKS
- S3_STORAGE
- USER_MANAGEMENT
- FORM_CONFIG
- SYSTEM_SETTINGS

**Permissions:**
- VIEW, CREATE, EDIT, DELETE
- APPROVE, REJECT, EXPORT, ASSIGN
- MANAGE_USERS, MANAGE_SETTINGS

### Application
POD application intake form for new centers.

### Complaint
Helpdesk/ticketing system for issues.

### Reports
- **Weekly Reports** - Regular POD updates
- **Monthly Reports** - Comprehensive monthly data

### Inventory
Asset tracking for POD equipment (PCs, etc.)

### Success Stories
Student/alumni success story documentation

---

## Key Pages/Features

| Page | Description |
|------|-------------|
| **Dashboard** | Main overview with metrics |
| **Applications** | New POD application management |
| **PODs** | POD directory and management |
| **Students** | Student records |
| **Inventory** | Equipment/asset tracking |
| **Weekly Reports** | Weekly submission tracking |
| **Monthly Reports** | Monthly compliance reports |
| **Complaints** | Helpdesk/ticket system |
| **Communications** | Two-way messaging |
| **Success Stories** | Story documentation |
| **S3 Storage** | File/media management |
| **Announcements** | Broadcast messages |
| **Users** | User management |
| **System Settings** | Configuration |

---

## Workflow Context

### POD Lifecycle
1. **Application** → Public landing page captures new POD applications
2. **Onboarding** → POD status is ONBOARDING, credentials auto-provisioned
3. **Active** → POD is operational, submitting reports
4. **Inactive** → POD is paused/closed

### Report Compliance
- POD Leaders submit weekly/monthly reports
- Admins review and approve/reject
- Notifications for pending reports

### Complaint System
- Issues logged with priority
- Assigned to relevant parties
- Status tracking (New → In Progress → Resolved)

---

## Technical Stack

- **Frontend:** Vite + React + TypeScript
- **Backend:** Express + TypeScript + MongoDB
- **Auth:** JWT-based with role permissions
- **Storage:** AWS S3 for files/media
- **Email:** SMTP for notifications
- **Integrations:** Google Sheets import/export, Scogo ticketing

---

## Common Bug Categories

When logging bugs, consider these areas:

1. **Authentication/Login** - Login issues, OTP problems
2. **POD Management** - CRUD operations, leader assignments
3. **Reports** - Submission, validation, viewing
4. **Complaints** - Ticket creation, status updates
5. **Inventory** - Asset tracking issues
6. **Communications** - Messaging problems
7. **S3 Storage** - File upload/download
8. **Permissions** - Role-based access issues
9. **Google Sheets Sync** - Import/export failures
10. **UI/UX** - Display, responsiveness issues

---

## Important Files

```
server/src/
├── models/          # Mongoose schemas
├── modules/         # Feature modules
├── routes/          # API routes
└── services/        # Business logic

client/src/
├── pages/           # Feature screens
├── components/      # Reusable UI
├── providers/       # Auth context
└── lib/             # API utilities
```

---

_This reference helps create contextual bug reports with proper terminology and domain understanding._
