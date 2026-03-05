# Admin Setup & Customization
> Company settings, logo, subscription, Boost, grids, filters, tags, custom fields

## Trigger
- the user says "update company settings", "change logo", "configure BT"
- New Buildertrend account needs initial setup
- Subscription or plan change needed

## Error Handling
| Issue | Resolution |
|---|---|
| Settings page not loading | Clear cache, retry. May need Admin role |
| Logo upload fails | Check file size (<5MB) and format (PNG/JPG) |
| Permission denied | Only Org Owner/Admin can modify company settings |
| BT session expired | Stop, notify the user to re-login |

---

## Overview
Admin setup in Buildertrend covers:
- Company information and branding
- Subscription management
- Default settings and permissions
- Grid views, filters, tags, and custom fields
- Training resources (Buildertrend Learning Academy)

---

## COMPANY SETTINGS

### Updating Company Logo
1. Go to **User Profile Icon** > **Company Settings**
2. In Company section, click **Company Logo**
3. Choose which logo to update:
   - **Website Logo** — Main branding
   - **Mobile Logo** — Mobile app display
   - **Mini Logo** — Compact display
4. Click **"Choose File"** and upload image
5. Click **"Update Account"**

### Company Information on Printouts
- Navigate to **Company Settings > Company Information**
- Add up to **3 fields** to appear in printout headers
- Customize printout content: select Print > **More Settings**

### Subscription Management
Navigate to **Manage Subscription** from user profile icon:
- Review/upgrade **Subscription** and **Buildertrend Offerings**
- Access **Payment Info, Payment History, Order Forms**
- Add additional services from **Additional Options**

---

## BUILDERTREND BOOST

Premium training package ($$ add-on) including:
- ✅ Personalized coaching
- ✅ Dedicated account management
- ✅ Strategic check-ins
- ✅ Thorough account reviews
- ✅ Tailored success plan

### Adding Buildertrend Boost
1. User Profile Icon > **Manage Subscription**
2. Buildertrend Offerings > **Manage Subscription**
3. Under current package > **Additional Options**
4. Check box next to **Buildertrend Boost**
5. **Proceed to Checkout** > **Submit Order**

---

## GRIDS, FILTERS & VIEWS

### Grid Views vs Filters
| Feature | Purpose | Example |
|---------|---------|---------|
| **Grid View** | Define what columns/information to display | Add "Date Paid" column to Bills grid |
| **Filter** | Search/narrow displayed data | Show only Bills paid in last 30 days |

### Working with Filters
- **Default filter:** Unique to each user (won't affect others)
- **Deleting shared filter:** Removes for entire team
- **Deleting private filter:** Only removes for you
- **Export:** Click "Export" in top right corner → downloads Excel

### Creating Useful Filters
Common filter combinations for construction:
- Bills: Status = Open, Date range = This month
- POs: Status = Pending, Assigned to = [specific sub]
- Invoices: Status = Unpaid, Job = [specific job]
- Daily Logs: Date range = Last week, Job = [specific job]

---

## TAGS & CUSTOM FIELDS

### Tags
- **Simple labels** for categorization
- Single-line text
- Must be added individually to each item
- Good for: quick categorization, high-level details, filtering

### Custom Fields
- **Detailed information** added to features
- Visible to internal teams, trade partners, and/or clients
- Once added, appear on **all new and existing jobs**
- Good for: structured data, compliance tracking, reporting

### Key Differences
| Attribute | Tags | Custom Fields |
|-----------|------|---------------|
| Complexity | Simple label | Structured data |
| Scope | Per-item | All jobs |
| Visibility | Internal | Configurable |
| Use case | Quick categorization | Detailed tracking |

---

## DEFAULT SETTINGS TO CONFIGURE

### Job Defaults
- **Default Job Permissions** (Company Settings) — Set client access levels for all new jobs
- **Work Days** — Standard work week
- **Job Types** — Categorize projects (Commercial TI, Residential, etc.)
- **Job Groups** — Custom groupings for filtering

### Financial Defaults
- **Cost Codes** — Standardized cost categorization
- **Invoice numbering** — Prefix conventions
- **Tax settings** — Automated sales tax by zip code

### Communication Defaults
- **Invitation verbiage** — Customize client invitation email text
- **Notification preferences** — Company-wide notification standards

### Permission Defaults
- **Default Client Permissions** — What clients see/do by default
- **Default Sub/Vendor Permissions** — Trade partner access defaults

---

## BUILDERTREND LEARNING ACADEMY

Free online learning platform at https://learn.buildertrend.net

### Resources Available
| Resource | Description |
|----------|-------------|
| **Courses** | Feature-based learning (30+ courses) |
| **Learning Paths** | Multi-course guided journeys |
| **Certifications** | Formal BT certifications |
| **Live Group Trainings** | Interactive online sessions |
| **In-Person Training** | Buildertrend University conferences |

### Key Courses for {{company_name}} Setup
1. **Getting Started** (35 min) — Account setup + team involvement
2. **Buildertrend Introduction** (20 min) — Core features overview
3. **Feature: Cost Codes** (30 min) — Job costing structure
4. **Onboarding: Job Management** (16 min) — Series Course 1
5. **Onboarding: Financial Management** — Series Course 2
6. **Implementation Journey** Learning Path (~3 hours) — Complete implementation guide

### Recommended Learning Path
1. Start: Implementation Journey learning path
2. Then: Feature-specific courses for each team member's role
3. Then: Certification for key users
4. Ongoing: Live Group Trainings for deep dives

---

## BROWSER & TECHNICAL REQUIREMENTS

### Recommended Browsers
- ✅ Chrome (Windows and Mac)
- ✅ Firefox (Windows and Mac)
- ✅ Safari (Mac only)
- ⚠️ Internet Explorer — may have issues
- ⚠️ Safari (Windows) — may have issues

### Recommended Resolution
**1920 x 1080** for optimal viewing of all information.

### Troubleshooting
- **Clear cookies & cache** to resolve odd behaviors and speed up performance
- **Check browser version** — ensure up to date

---

## COMPANY SETUP CHECKLIST

### Phase 1: Foundation
- [ ] Update company logo (Website, Mobile, Mini)
- [ ] Complete Company Information (3 printout fields)
- [ ] Set up Cost Codes structure
- [ ] Configure Job Types and Job Groups
- [ ] Set default work days

### Phase 2: Users & Permissions
- [ ] Add all Internal Users with appropriate roles
- [ ] Create custom roles if needed (see user-role-management playbook)
- [ ] Configure default Client Permissions
- [ ] Configure default Sub/Vendor Permissions
- [ ] Set notification preferences company-wide

### Phase 3: Templates & Defaults
- [ ] Create Job Templates for common project types
- [ ] Create Specification Templates
- [ ] Set up Estimate Templates
- [ ] Configure default invitation verbiage
- [ ] Set up financial defaults (numbering, tax)

### Phase 4: Training
- [ ] Enroll team in BT Learning Academy
- [ ] Assign Implementation Journey to all users
- [ ] Schedule role-specific feature courses
- [ ] Consider Buildertrend Boost for accelerated setup
