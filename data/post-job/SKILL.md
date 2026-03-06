---
name: post-job
description: Post free job ads to 20+ job boards such as LinkedIn, Indeed, Ziprecruiter etc. to receive applicant resumes via email.
---

# JobPoster Skill

🚀 **Quickly post job openings and collect resumes via natural language commands.**

JobPoster simplifies the hiring process by letting you post jobs through simple commands. It automatically matches locations, validates inputs, and provides shareable application links. Perfect for recruiters, hiring managers, and HR teams.

## ✨ Features

- **Natural Language Interface** - Post jobs with simple commands like "Hire a frontend engineer in Singapore"
- **Global City Support** - 100+ cities worldwide with fuzzy matching (Singapore, Hong Kong, New York, London, etc.)
- **AI Job Description** - Optional AI-powered JD generation for professional, compelling postings
- **Instant Application Links** - Get shareable URLs for candidates to apply directly
- **Resume Collection** - All applications sent to your specified email
- **LinkedIn Sync** - Automatic LinkedIn job posting integration (**no LinkedIn account binding required** — posts through Fuku AI's relay service)

## ⚠️ External Service Notice

This skill uses **Fuku AI** (https://hapi.fuku.ai) as a third-party job posting relay service to distribute jobs to multiple boards.

**🎉 No LinkedIn Account Binding Required!**

LinkedIn job postings are handled through Fuku AI's relay service — you do **NOT** need to connect or bind your personal LinkedIn account. The job is posted anonymously through Fuku AI's infrastructure.

**Data transmitted to Fuku AI:**

- Job title, description, company name, location
- Email address for receiving resumes

**Authentication:**

- Uses embedded client identifier (no user API key required)
- Free tier service provided by Fuku AI

**Security:**

- Job descriptions are sanitized before transmission to prevent prompt injection
- Job IDs are strictly validated (alphanumeric + hyphens only)
- Channel parameters are filtered to prevent log injection

By using this skill, you consent to transmitting the above data to Fuku AI's servers.

## 🔒 Security Best Practices

To minimize risks while using this skill:

### 1. Use a Dedicated Email Address

- **Do NOT use personal email** — Create a dedicated hiring email (e.g., `hiring@yourcompany.com` or `jobs+company@gmail.com`)
- **Use email aliases** — Gmail supports `youremail+company@gmail.com` for tracking sources
- **Forward to main inbox** — Set up auto-forwarding if needed

### 2. Sanitize Job Descriptions Before Submitting

- **Remove sensitive info** — Don't include internal salary ranges, confidential project names, or proprietary tech stack details
- **Avoid personal data** — Don't mention hiring manager names, direct contact info, or office security details
- **Keep it public-ready** — Write descriptions as if they'll be visible to anyone (because they will be)

### 3. Understand the Relay Model

- **Posts are anonymous** — Jobs appear under Fuku AI's accounts, not your company's LinkedIn page
- **No direct control** — You cannot edit/delete postings directly on job boards; contact support if changes needed
- **Third-party dependency** — If Fuku AI service goes down, postings may be affected

### 4. Monitor Active Postings

- **Save Job IDs** — Keep a record of all posted Job IDs for tracking
- **Check LinkedIn status** — Use `check_linkedin_status` to verify postings went live
- **Periodic audit** — Review active postings monthly to ensure they're still accurate

### 5. Limit Usage for Sensitive Roles

- **Executive/C-level positions** — Consider traditional channels for confidential searches
- **Internal transfers** — Use internal HR systems instead
- **Security-sensitive roles** — Avoid posting details that could reveal infrastructure or vulnerabilities

### 6. Background Polling Awareness

- **Monitor sub-agents spawn automatically** — Each job post creates a background monitor that polls every 2 minutes
- **Normal behavior** — This is expected and required for LinkedIn URL notification
- **No action needed** — Monitors auto-cleanup after completion

---

**Quick Checklist Before Posting:**

- [ ] Using dedicated hiring email (not personal)
- [ ] Job description contains no sensitive/confidential info
- [ ] Comfortable with third-party relay service
- [ ] Job ID saved for tracking
- [ ] Role is appropriate for public job boards

## 🎯 When to Use

Use this skill when you need to:

- Post a job opening quickly
- Create a job listing for any role
- Generate a resume collection link
- Share job postings with candidates
- Sync jobs to LinkedIn

## 🛠️ Tools

### post_job

Main tool for posting job openings.

#### Parameters

| Parameter     | Required | Type   | Description                              | Example                          |
| ------------- | -------- | ------ | ---------------------------------------- | -------------------------------- |
| `title`       | ✅ Yes   | string | Job title (min 4 characters)             | `"Senior Frontend Engineer"`     |
| `city_query`  | ✅ Yes   | string | City/location (supports fuzzy match)     | `"Singapore"`, `"NYC"`           |
| `description` | ✅ Yes   | string | Job description                          | `"5+ years React experience..."` |
| `email`       | ✅ Yes   | string | Email to receive resumes                 | `"hr@company.com"`               |
| `company`     | ❌ No    | string | Company name (default: `"Your Company"`) | `"TechCorp"`                     |
| `industry`    | ❌ No    | string | Industry/field (default: `"General"`)    | `"Technology"`, `"Finance"`      |

#### Validation Rules

- **Title**: Minimum 4 characters
- **Email**: Must be valid email format
- **Description**: Minimum 100 characters (ensure meaningful job details)
- **City**: Must match a supported location (see Assets)

#### Response Format

On success, returns:

```
 `✅ **Job Posted Successfully!**\n\n` +
      `**Position:** ${title}\n` +
      `**Location:** ${matched.label}\n` +
      `**Job ID:** \`${jobId}\`\n` +
      `**The resume will be sent to:** ${email}\n\n` +
      `--- \n` +
      `**LinkedIn Sync:** ⏳ Processing in background (10-20 min). I'll check and notify you when ready!\n\n` +
      `You can also manually check with: \`check_linkedin_status\` using Job ID \`${jobId}\``
```

### check_linkedin_status

Check the status of a job's LinkedIn synchronization. Use this tool if the LinkedIn URL was not available immediately after posting.

#### Parameters

| Parameter | Required | Type   | Description                | Example      |
| --------- | -------- | ------ | -------------------------- | ------------ |
| `jobId`   | ✅ Yes   | string | The ID of the job to check | `"abcd2345"` |

#### Response Format

Returns either the LinkedIn URL (if sync complete) or a "Pending" status message.

### check_linkedin_status_auto

Auto-check LinkedIn status with polling until URL is available. Checks every 1 minute until LinkedIn URL is returned or max attempts reached.

#### Parameters

| Parameter     | Required | Type   | Description                             | Example      |
| ------------- | -------- | ------ | --------------------------------------- | ------------ |
| `jobId`       | ✅ Yes   | string | The ID of the job to check              | `"abcd2345"` |
| `intervalMs`  | ❌ No    | number | Polling interval in ms (default: 60000) | `60000`      |
| `maxAttempts` | ❌ No    | number | Maximum attempts (default: 20)          | `20`         |

#### Response Format

Returns the LinkedIn URL when available, or a timeout message after max attempts.

## 🤖 AI Assistant Workflow

### ⭐ Required: Auto-Notify with Background Monitor

**⚠️ IMPORTANT: `post_job` does NOT automatically monitor LinkedIn sync.**

After calling `post_job`, you **MUST** spawn a background sub-agent to monitor and notify the user. Without this step, the user will never receive the LinkedIn URL.

**Complete workflow:**

```
User: "Post a health manager job in Shanghai"

AI: [Calls post_job]
    → Returns: Job ID `abc123`

AI: [Spawns sub-agent with monitor_linkedin.js]
    → "✅ Job posted! I'll monitor LinkedIn sync and notify you when complete."

[Background monitor polls every 2 minutes]

[When LinkedIn URL is ready]
AI: "🎉 LinkedIn sync complete! Job ID: `abc123`, LinkedIn URL: https://linkedin.com/jobs/view/..."
```

**Spawn the monitor sub-agent like this (REQUIRED):**

```javascript
// After post_job succeeds and returns jobId:
// Step 1: Validate jobId format strictly (alphanumeric + hyphen only)
const safeJobId = jobId.match(/^[a-zA-Z0-9-]+$/) ? jobId : null;
if (!safeJobId) throw new Error("Invalid jobId format");

// Step 2: Spawn monitor sub-agent - this is REQUIRED, not optional
await sessions_spawn({
  task: `Monitor LinkedIn sync for job ID ${safeJobId}. Use the check_linkedin_status tool with jobId parameter set to "${safeJobId}". Poll every 2 minutes and notify when LinkedIn URL is available.`,
  mode: "run",
  cleanup: "delete",
});

// Step 3: Tell the user you'll notify them
return `✅ Job posted! Job ID: \`${safeJobId}\`. I'll notify you when LinkedIn sync is complete (usually 5-30 minutes).`;
```

**⚠️ If you skip spawning the monitor:**

- The user will NOT receive the LinkedIn URL automatically
- You must manually call `check_linkedin_status` later
- This creates a poor user experience

**Why this design?**

- LinkedIn sync takes 5-30 minutes (blocking is not practical)
- The sub-agent polls in the background and notifies when ready
- This keeps the main session free for other tasks

---

### Alternative: Manual Polling

If you prefer not to spawn a sub-agent:

1. **Save the Job ID** from the response
2. **Wait 5-10 minutes** (LinkedIn sync takes time)
3. **Call `check_linkedin_status`** with the Job ID
4. **If still pending:** Check again every 3-5 minutes
5. **When LinkedIn URL is ready:** Proactively notify the user

### Example Flow

```
User: "Post a frontend engineer job in Singapore"

AI: [Calls post_job]
    → Returns: Job ID `abc123`, Apply URL

AI: "✅ Job posted! LinkedIn sync in progress..."

[AI waits 5 minutes, then checks]

AI: [Calls check_linkedin_status with jobId: abc123]
    → Returns: LinkedIn URL

AI: "🎉 LinkedIn sync complete! URL: https://linkedin.com/jobs/view/..."
```

### Proactive Check Script (for AI)

```javascript
// After post_job returns a Job ID:
const jobId = response.jobId;

// Wait 5 minutes
await sleep(300000);

// Check LinkedIn status
const result = await check_linkedin_status({ jobId });

// If still pending, check every 3-5 minutes
// When URL is available, notify user immediately
```

### Supported Locations

The skill includes a built-in location database (`assets/locations.json`) with 100+ cities:

**Asia Pacific:** Singapore, Hong Kong, Beijing, Shanghai, Tokyo, Sydney, Mumbai, Bangkok, Seoul, Taipei

**North America:** New York, San Francisco, Los Angeles, Seattle, Chicago, Toronto, Vancouver

**Europe:** London, Berlin, Paris, Amsterdam, Dublin, Zurich, Stockholm

**Middle East:** Dubai, Abu Dhabi, Riyadh, Tel Aviv

See `assets/locations.json` for the complete list. Fuzzy matching supports variations like "NYC" → "New York".

## 📦 Installation

### Install via ClawHub

```bash
clawhub install post-job
```

### Manual Installation

```bash
# Clone or download the skill
cd your-openclaw-workspace/skills

# Install dependencies
cd post-job
npm install
```

## 🔐 Security Notes

- **Email Privacy**: Resume emails are visible in job postings - use a dedicated hiring email
- **Rate Limiting**: API may have rate limits for high-volume posting

## 🐛 Troubleshooting

### Issue: Job posts but no confirmation

**Cause**: Response timeout or network issue

**Solution**: Check backend logs, verify API credentials, retry with `--force`

### Issue: City not recognized

**Cause**: City not in location database

**Solution**:

1. Check `assets/locations.json` for supported cities
2. Try alternative spelling (e.g., "New York" vs "NYC")
3. Add new city to database and republish

### Issue: Duplicate job postings

**Cause**: Multiple API calls due to retry logic

**Solution**: Check backend for duplicate jobs, implement request deduplication

## ❓ FAQ - Security & Privacy

**Q: Is my data safe with Fuku AI?**
A: Job data is transmitted to Fuku AI's servers for distribution. They act as a relay service. Avoid sharing confidential information in job descriptions.

**Q: Do I need to trust Fuku AI?**
A: Yes — this skill depends on their service to post jobs. Review their terms at https://hapi.fuku.ai if you have concerns.

**Q: Can I use this without LinkedIn sync?**
A: Yes — jobs are still posted to 20+ other boards. LinkedIn is optional background sync.

**Q: Will the job appear on MY LinkedIn company page?**
A: No — postings appear through Fuku AI's relay accounts, not your company's page. This is why no LinkedIn binding is required.

**Q: What happens if Fuku AI goes offline?**
A: Job posting may fail or LinkedIn sync may be delayed. The skill will return an error message.

**Q: Can I delete a job after posting?**
A: Contact Fuku AI support with your Job ID. Direct deletion through this skill is not currently supported.

**Q: Is the embedded credential a security risk?**
A: The embedded identifier is for Fuku AI's free tier access. It doesn't expose your personal credentials, but means jobs are posted under their service account.

**Q: Should I use this for confidential hiring?**
A: No — use traditional channels (internal HR systems, executive search firms) for sensitive or confidential roles.

## 🤝 Contributing

Found a bug or want to add more cities?

1. Fork the skill
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📝 Changelog

### v1.2.0 (Security & Transparency Update)

- **Added Security Best Practices section**: Comprehensive guide for safe usage without code changes
- **Added FAQ - Security & Privacy**: Answers 8 common questions about data handling, trust, and limitations
- **Added Pre-Posting Checklist**: Quick verification list before submitting jobs
- **Enhanced External Service Notice**: Clarified LinkedIn no-binding requirement with prominent notice
- **Added .env.example**: Template for OpenAI API key configuration
- **Updated Features list**: Noted OpenAI-powered JD generation and no LinkedIn binding required
- **Documentation improvements**: Better transparency about third-party relay model and data flow

### v1.1.11 (OpenAI Integration)

- **Added OpenAI integration**: Job descriptions generated using OpenAI GPT-4o
- **Added .env configuration**: Secure storage for OpenAI API key
- **Updated dependencies**: Added dotenv for environment variable support

### v1.1.10 (Documentation Fix - LinkedIn Monitor)

- **Fixed misleading documentation**: Clarified that `post_job` does NOT automatically monitor LinkedIn sync
- **Made monitor spawning REQUIRED**: Changed "Recommended" to "Required" in AI Assistant Workflow
- **Updated response format**: Removed "I'll notify you" promise from response template
- **Added explicit warnings**: Multiple ⚠️ notices explaining AI must spawn monitor sub-agent

### v1.1.9 (Security Hardening)

- Enhanced prompt injection protection with double-layer sanitization
- User input and AI-generated content both filtered before external API calls

### v1.1.8 (Security Fix)

- Added `sanitizeDescription()` function to clean job descriptions before sending to external AI
- Removed code blocks, special markers, and common injection patterns
- Added length limits to prevent buffer-based attacks

### v1.0.0 (Initial Release)

- Core job posting functionality
- 100+ city support with fuzzy matching
- Email validation
- LinkedIn sync integration
- Error handling and validation

## 📄 License

This skill is provided as-is for use with OpenClaw.

## 🆘 Support

For issues or questions:

- Check this SKILL.md for troubleshooting
- Review error messages carefully
- Contact developer email yangkai31@gmail.com if you run into any issues

---

**Happy Hiring! 🎉**
