# SKILL: bolta.skills.index

Display name: Bolta Skills Registry
Slug: bolta-skills-registry
Version: 0.5.4
Tags: registry,catalog,bootstrap,workspace,index,discovery
Organization: bolta.ai
Author: Max Fritzhand
Type: registry
Executes: false

## Metadata

```json
{
  "name": "bolta.skills.index",
  "version": "0.5.4",
  "publisher": "bolta.ai",
  "verified": true,
  "sourceRepository": "https://github.com/boltaai/bolta-skills",
  "requiredEnvironmentVariables": [
    {
      "name": "BOLTA_API_KEY",
      "required": true,
      "sensitive": true,
      "description": "Bolta API key (obtain at bolta.ai/register)",
      "format": "sk_live_[64 characters]",
      "scope": "workspace"
    },
    {
      "name": "BOLTA_WORKSPACE_ID",
      "required": true,
      "sensitive": false,
      "description": "Workspace UUID for API operations",
      "format": "UUID"
    },
    {
      "name": "BOLTA_AGENT_ID",
      "required": false,
      "sensitive": false,
      "description": "Agent principal UUID (for audit logging)",
      "format": "UUID"
    }
  ],
  "trustedDomains": [
    "platty.boltathread.com",
    "bolta.ai"
  ],
  "permissions": [
    "network:https:platty.boltathread.com",
    "network:https:bolta.ai"
  ],
  "thirdPartyPackages": [
    {
      "name": "@boltaai/mcp-server",
      "registry": "npm",
      "verified": true,
      "sourceRepository": "https://github.com/boltaai/bolta-mcp-server"
    }
  ]
}
```

## ⚠️ Security Notice

**This skill requires sensitive API credentials. Read this section carefully before installing.**

### Required Credentials

**BOLTA_API_KEY** (REQUIRED, SENSITIVE)
- **Format:** `sk_live_` followed by 64 alphanumeric characters
- **Obtain at:** https://bolta.ai/register
- **Scoping:** Each key is scoped to a SINGLE workspace only
- **Permissions:** Grant LEAST-PRIVILEGE access (e.g., only `posts:write` if creating content)
- **Rotation:** Rotate every 90 days using `bolta.team.rotate_key` skill
- **Storage:** NEVER commit to git - use environment variables or secret managers only

**BOLTA_WORKSPACE_ID** (REQUIRED)
- **Format:** UUID (e.g., `550e8400-e29b-41d4-a716-446655440000`)
- **Source:** Provided during agent registration at bolta.ai/register
- **Purpose:** Identifies which workspace the API key is authorized for

**BOLTA_AGENT_ID** (OPTIONAL, RECOMMENDED)
- **Format:** UUID
- **Purpose:** Links API activity to specific agent principal for audit logs
- **Benefit:** Enables traceability and compliance reporting

### Trusted Network Endpoints

This skill makes HTTPS requests to:
- ✅ `https://platty.boltathread.com` - Bolta API server
- ✅ `https://bolta.ai` - Main application and agent registration portal

**No other domains are contacted.** All requests are authenticated with your API key.

### Third-Party Dependencies

This skill references:
- `@boltaai/mcp-server` (npm package for Claude Desktop integration)
  - **Source:** https://github.com/boltaai/bolta-mcp-server
  - **Verified:** Yes (official Bolta package)
  - **Purpose:** Connects Claude Desktop to Bolta API via MCP protocol

### Pre-Installation Checklist

**Before installing this skill, you MUST:**
- [ ] Verify the source repository: https://github.com/boltaai/bolta-skills
- [ ] Review the SKILL.md and confirm version matches metadata (currently 0.5.4)
- [ ] Obtain a LEAST-PRIVILEGE API key from https://bolta.ai/register
- [ ] Store API key in environment variables (NEVER hardcode or commit)
- [ ] Verify you trust the domains: `platty.boltathread.com` and `bolta.ai`
- [ ] Test in a disposable/test workspace first (recommended)
- [ ] Confirm your API key is scoped ONLY to the intended workspace

**If you cannot verify the above, DO NOT install this skill.**

### Security Best Practices

1. **Credential Management**
   - Use environment variables: `export BOLTA_API_KEY="sk_live_..."`
   - Or use secret managers: AWS Secrets Manager, 1Password, etc.
   - NEVER paste API keys in chat, logs, or public places

2. **Key Rotation**
   - Rotate keys every 90 days minimum
   - Use `bolta.team.rotate_key` skill for zero-downtime rotation
   - Revoke compromised keys immediately at bolta.ai/settings

3. **Permission Scoping**
   - Grant ONLY required permissions (e.g., `posts:write`, `voice:read`)
   - Avoid `workspace:admin` unless absolutely necessary
   - Review permissions quarterly

4. **Monitoring**
   - Review audit logs weekly via `bolta.audit.export_activity`
   - Monitor quota usage via `bolta.quota.status`
   - Set up alerts for unusual API activity

5. **Workspace Isolation**
   - One API key per workspace (NEVER share keys across workspaces)
   - Use separate keys for dev/staging/production environments
   - Revoke keys when decommissioning workspaces

## Purpose

**The canonical registry and orchestration layer for all Bolta skills.**

This skill serves as the single source of truth for skill discovery, installation recommendations, and workspace-aware capability bootstrapping. It does not execute content operations directly — instead, it provides intelligent routing to the appropriate skills based on:

- **Workspace policy** (Safe Mode, autonomy mode, quotas)
- **Principal identity** (user role, agent permissions)
- **Operational context** (what you're trying to accomplish)

**Key Responsibilities:**
1. **Discovery** - Index all available skills with metadata
2. **Recommendation** - Suggest install sets based on workspace policy and role
3. **Orchestration** - Guide multi-skill workflows
4. **Compatibility** - Enforce skill compatibility with workspace settings
5. **Bootstrapping** - Help new workspaces get started quickly

**When to Use:**
- Setting up a new workspace ("What skills should I install?")
- Discovering available capabilities ("What can Bolta do?")
- Troubleshooting skill compatibility ("Why can't I use this skill?")
- Planning multi-step workflows ("Which skills do I need?")

**Data Access:**
This skill accesses:
- ✅ Workspace configuration (policy, quotas, autonomy mode)
- ✅ Voice profile metadata (names, IDs, not full content)
- ✅ Post counts and quota usage
- ✅ Agent principal permissions

This skill does NOT access:
- ❌ Post content or scheduled posts
- ❌ Social media credentials
- ❌ User passwords or authentication tokens
- ❌ Files or media uploads

## Source & Verification

https://github.com/boltaai/bolta-skills

---

## Getting Started: Agent API Setup

Before using Bolta skills, you need to set up agent API access to authenticate your requests.

### Step 1: Register Your Agent

Visit **[bolta.ai/register](https://bolta.ai/register)** to create your agent principal and obtain an API key.

**What you'll need:**
- Bolta workspace (create one at bolta.ai if you don't have one)
- Admin or Owner role in your workspace

### Step 2: Create Agent Principal

During registration, you'll configure:

**Agent Name**
```
Example: "Claude Content Agent"
Description: Human-readable name for audit logs
```

**Agent Role**
```
Options:
- creator  - Can create drafts (recommended for testing)
- editor   - Can create + schedule posts
- reviewer - Can approve/reject posts (review-only access)

Recommended: Start with "creator" role for safety
```

**Permissions**
```
Minimum for content skills:
✓ posts:write  - Create posts
✓ voice:read   - Read voice profiles

Optional (based on use case):
□ posts:schedule  - Schedule posts (requires editor+ role)
□ posts:approve   - Approve posts for publishing
□ templates:read  - Use content templates
□ cron:execute    - Run automated jobs
```

### Step 3: Copy Your API Key

After registration, you'll receive:

```
API Key: sk_live_00000000000000000000000000000000
Workspace ID: 550e8400-e29b-41d4-a716-446655440000
Agent ID: 660e8400-e29b-41d4-a716-446655440001
```

**IMPORTANT:**
- ⚠️ Store API key securely (never commit to git)
- ⚠️ Keys cannot be recovered (only regenerated via `bolta.team.rotate_key`)
- ⚠️ Each key is scoped to ONE workspace

### Step 4: Configure Your Environment

**Set Required Environment Variables:**

Before using any Bolta skills, you MUST configure these environment variables:

```bash
# Required: Your Bolta API key (from bolta.ai/register)
export BOLTA_API_KEY="sk_live_your_actual_key_here"

# Required: Your workspace UUID (from bolta.ai/register)
export BOLTA_WORKSPACE_ID="550e8400-e29b-41d4-a716-446655440000"

# Optional: Agent principal UUID (for audit logging)
export BOLTA_AGENT_ID="660e8400-e29b-41d4-a716-446655440001"
```

**For Claude Desktop (MCP):**
```json
{
  "mcpServers": {
    "bolta": {
      "command": "npx",
      "args": ["-y", "@boltaai/mcp-server"],
      "env": {
        "BOLTA_API_KEY": "sk_live_your_actual_key_here",
        "BOLTA_WORKSPACE_ID": "550e8400-e29b-41d4-a716-446655440000",
        "BOLTA_AGENT_ID": "660e8400-e29b-41d4-a716-446655440001"
      }
    }
  }
}
```

**For Direct API Calls:**
```bash
# Use environment variables in your requests
curl https://platty.boltathread.com/v1/posts \
  -H "Authorization: Bearer ${BOLTA_API_KEY}" \
  -H "X-Workspace-ID: ${BOLTA_WORKSPACE_ID}" \
  -H "Content-Type: application/json" \
  -d '{ "prompt": "Create a post about productivity" }'
```

**For Node.js/TypeScript Applications:**
```javascript
import { BoltaClient } from '@boltaai/sdk';

// Load from environment variables (recommended)
const bolta = new BoltaClient({
  apiKey: process.env.BOLTA_API_KEY,
  workspaceId: process.env.BOLTA_WORKSPACE_ID,
  agentId: process.env.BOLTA_AGENT_ID // Optional
});

// Verify all required vars are set
if (!process.env.BOLTA_API_KEY || !process.env.BOLTA_WORKSPACE_ID) {
  throw new Error('Missing required Bolta credentials. Set BOLTA_API_KEY and BOLTA_WORKSPACE_ID');
}
```

**Security Reminder:**
- ⚠️ Never hardcode API keys in your code
- ⚠️ Use `.env` files locally (add `.env` to `.gitignore`)
- ⚠️ Use secret managers in production (AWS Secrets Manager, Vercel Secrets, etc.)
- ⚠️ Rotate keys every 90 days via `bolta.team.rotate_key`


### Step 5: Verify Setup

Test your configuration with a simple skill:

# Via API
curl https://api.bolta.ai/v1/workspaces/{workspace_id} \
  -H "Authorization: Bearer YOUR_API_KEY"

# Expected response:
{
  "id": "550e8400-...",
  "name": "My Workspace",
  "safe_mode": true,
  "autonomy_mode": "managed",
  "max_posts_per_day": 100
}
```

### Troubleshooting Setup

#### Error: "Invalid API Key"
**Cause:** Key is incorrect or has been rotated

**Solutions:**
1. Verify key matches exactly (no extra spaces)
2. Check if key was rotated → Get new key at bolta.ai/register
3. Ensure you're using the correct workspace key

#### Error: "Workspace Not Found"
**Cause:** Workspace ID mismatch or no access

**Solutions:**
1. Verify workspace_id matches your registration
2. Confirm you have access to this workspace (visit bolta.ai/workspaces)
3. Check if workspace was deleted

#### Error: "Permission Denied"
**Cause:** Agent role lacks required permission

**Solutions:**
1. Check your agent's permissions at bolta.ai/register
2. For content creation: Need `posts:write` minimum
3. For scheduling: Need `posts:schedule` + editor role
4. For automation: Need `cron:execute` permission

---

## Installation & First Run

### 🎯 Complete Skill Pack Installation

**You're currently viewing the registry skill only.** To access the full Bolta skills library, you should install the complete skill pack.

**Option 1: Install Full Skill Pack (Recommended)**

```bash
# Clone the complete Bolta skills repository
git clone https://github.com/boltaai/bolta-skills.git

# Or download the latest release
curl -L https://github.com/boltaai/bolta-skills/archive/refs/heads/main.zip -o bolta-skills.zip
unzip bolta-skills.zip
```

**What You Get:**
```
bolta-skills/
├── README.md                    # ⭐ START HERE - Complete getting started guide
├── skills/
│   ├── bolta.skills.index/      # ✅ You're here (registry)
│   ├── voice-plane/
│   │   ├── bolta.voice.bootstrap/
│   │   ├── bolta.voice.learn_from_samples/
│   │   ├── bolta.voice.evolve/
│   │   └── bolta.voice.validate/
│   ├── content-plane/
│   │   ├── bolta.draft.post/
│   │   ├── bolta.loop.from_template/
│   │   ├── bolta.week.plan/
│   │   ├── bolta.content.repurpose/
│   │   └── bolta.content.thread_builder/
│   ├── review-plane/
│   │   ├── bolta.inbox.triage/
│   │   ├── bolta.review.digest/
│   │   ├── bolta.review.approve_and_route/
│   │   ├── bolta.review.suggest_edits/
│   │   └── bolta.review.compliance_check/
│   ├── automation-plane/
│   │   ├── bolta.cron.generate_to_review/
│   │   ├── bolta.cron.generate_and_schedule/
│   │   ├── bolta.recurring.from_template/
│   │   ├── bolta.auto.respond_to_trending/
│   │   └── bolta.auto.content_gap_fill/
│   └── control-plane/
│       ├── bolta.team.create_agent_teammate/
│       ├── bolta.team.rotate_key/
│       ├── bolta.policy.explain/
│       ├── bolta.audit.export_activity/
│       ├── bolta.quota.status/
│       └── bolta.workspace.config/
├── docs/
│   ├── getting-started.md       # Quickstart guide
│   ├── autonomy-modes.md        # Understanding autonomy levels
│   ├── safe-mode.md             # Safe Mode deep dive
│   ├── quotas.md                # Quota enforcement guide
│   └── voice-versioning.md      # Voice profile evolution
└── examples/
    ├── basic-workflow.md        # Common usage patterns
    ├── automation-setup.md      # Setting up cron jobs
    └── multi-agent.md           # Managing multiple agents
```

**Option 2: Install Individual Skills (Manual)**

If you only need specific skills, install them individually:

```bash
# Install voice bootstrap skill
curl -L https://raw.githubusercontent.com/boltaai/bolta-skills/main/skills/voice-plane/bolta.voice.bootstrap/SKILL.md \
  -o bolta.voice.bootstrap.md

# Install draft post skill
curl -L https://raw.githubusercontent.com/boltaai/bolta-skills/main/skills/content-plane/bolta.draft.post/SKILL.md \
  -o bolta.draft.post.md
```

---

### 📖 First Run: Read the README

**IMPORTANT: After installation, read the README for complete setup instructions.**

**Quick Start Commands:**

```bash
# After cloning/downloading the skill pack:
cd bolta-skills

# Read the README (contains critical setup steps)
cat README.md

# Or open in your editor
code README.md  # VS Code
vim README.md   # Vim
```

**What the README Covers:**
3. ✅ Environment variable configuration
4. ✅ First skill execution (test workflow)
5. ✅ Troubleshooting common issues
6. ✅ Recommended skill installation order
7. ✅ Best practices for production use

**Critical README Sections:**

```markdown
## README.md Structure

### Quick Start
- Installation steps
- API key setup
- First skill test

### Skill Planes Overview
- What each plane does
- When to use each skill
- Skill dependencies

### Configuration
- MCP server setup for Claude Desktop
- Environment variables
- Workspace policy settings

### Common Workflows
- Create first post (voice → draft → review)
- Set up automation (cron jobs)
- Multi-agent teams

### Troubleshooting
- API connection errors
- Permission issues
- Quota problems

### Security
- API key rotation
- Least-privilege permissions
- Audit logging

### Advanced Topics
- Custom skill development
- Skill chaining
- Performance optimization
```

---

### 🚀 Recommended First-Run Flow

**After installing the skill pack:**

**Step 1: Read Documentation**
```bash
# Must-read files in order:
1. README.md              # Complete getting started guide
2. docs/getting-started.md # Quickstart tutorial
3. docs/autonomy-modes.md  # Understand autonomy levels
4. docs/safe-mode.md       # Understand safety controls
```

**Step 2: Verify Installation**
```bash
# Check that all skills are present
ls -la skills/*/SKILL.md

# Should see 21+ skills across 5 planes
# If missing skills, re-run installation
```

**Step 3: Configure Agent**
```bash
# Set environment variables (from README)
export BOLTA_API_KEY="sk_live_..."
export BOLTA_WORKSPACE_ID="..."

# Test API connectivity
curl https://platty.boltathread.com/v1/workspaces/${BOLTA_WORKSPACE_ID} \
  -H "Authorization: Bearer ${BOLTA_API_KEY}"

# Expected: 200 OK with workspace details
```

```

**Step 5: Install Recommended Skills**
```bash
# The registry will recommend skills based on your:
# - Safe Mode setting
# - Autonomy mode
# - User role
# - Current quotas

# Follow recommendations to install your first skill set
```

---

### ⚠️ Common First-Run Mistakes

**Mistake 1: Skipping the README**
```
❌ Installing skills without reading README
✅ Read README.md first → understand workflows → install skills
```

**Mistake 2: Missing Environment Variables**
```
❌ Running skills without BOLTA_API_KEY set
✅ Configure env vars BEFORE running any skill
```

**Mistake 3: Installing Skills Out of Order**
```
❌ Running bolta.draft.post before creating voice profile
✅ Follow recommended order: voice.bootstrap → draft.post → review
```

**Mistake 4: Not Understanding Autonomy Modes**
```
❌ Using autopilot mode without understanding routing
✅ Read docs/autonomy-modes.md → start with "assisted" → graduate to "managed"
```

**Mistake 5: Hardcoding API Keys**
```
❌ Putting API keys directly in skill files
✅ Use environment variables → .env file → add .env to .gitignore
```

---

### 📥 Post-Installation Checklist

After installing the skill pack, verify:

- [ ] ✅ README.md has been read
- [ ] ✅ Environment variables configured (BOLTA_API_KEY, BOLTA_WORKSPACE_ID)
- [ ] ✅ All 21+ skills present in skills/ directory
- [ ] ✅ docs/ directory contains markdown files
- [ ] ✅ API connectivity verified (test curl command works)
- [ ] ✅ MCP server installed (if using Claude Desktop)
- [ ] ✅ Workspace policy reviewed (safe_mode, autonomy_mode)
- [ ] ✅ First skill executed successfully (test run)
- [ ] ✅ Autonomy mode documentation read (docs/autonomy-modes.md)
- [ ] ✅ Safe Mode documentation read (docs/safe-mode.md)

**Once all items are checked, you're ready to use the full Bolta skill library!**

---

### Next Steps After Setup

Once your API is configured:

1. **Create Voice Profile** (if new workspace)
   ```
   Run: bolta.voice.bootstrap
   → Establishes your brand voice
   ```

2. **Test Content Creation**
   ```
   Run: bolta.draft.post
   → Creates a test post in Draft status
   ```

3. **Install Recommended Skills**
   ```
   Run: bolta.skills.index
   → Returns personalized skill recommendations
   ```

4. **Configure Workspace Policy**
   ```
   Review: Safe Mode (ON/OFF)
   Review: Autonomy Mode (assisted/managed/autopilot)
   Set: Daily quota limits
   ```

---

## Architecture: The Five Planes

Skills are organized into **planes** — logical groupings that separate concerns and enable modular capability composition.

### Voice Plane
**Purpose:** Brand voice creation, evolution, and validation

Voice is the foundation of all content operations. These skills help establish, refine, and maintain consistent brand voice across all generated content.

**Core Principle:** Voice should be learned from examples, validated against real content, and evolved over time.

**Skills:**
- `bolta.voice.bootstrap` - Interactive voice profile creation from scratch
- `bolta.voice.learn_from_samples` - Extract voice patterns from existing content
- `bolta.voice.evolve` - Refine voice based on approved posts
- `bolta.voice.validate` - Score content against voice profile (0-100)

**Typical Flow:**
1. Bootstrap initial voice profile
2. Learn from sample content
3. Validate generated content
4. Evolve voice as brand matures

---

### Content Plane
**Purpose:** Content creation, planning, and scheduling

The execution layer for post creation. These skills transform ideas into scheduled social media posts.

**Core Principle:** Content should be intentional, planned, and aligned with voice.

**Skills:**
- `bolta.draft.post` - Create a single post in Draft status
- `bolta.loop.from_template` - Generate multiple posts from a template
- `bolta.week.plan` - Plan a week's worth of content with scheduling
- `bolta.content.repurpose` - Transform long-form content into social posts
- `bolta.content.thread_builder` - Create multi-post threads (Twitter, LinkedIn)

**Output:** Draft or Scheduled posts (subject to Safe Mode routing)

---

### Review Plane
**Purpose:** Human-in-the-loop review and approval workflows

Enables teams to review, approve, and refine agent-generated content before publishing.

**Core Principle:** Autonomy with oversight — agents generate, humans decide.

**Skills:**
- `bolta.inbox.triage` - Organize pending posts by priority/topic
- `bolta.review.digest` - Daily summary of posts awaiting review
- `bolta.review.approve_and_route` - Bulk approve + schedule posts
- `bolta.review.suggest_edits` - AI-powered improvement suggestions
- `bolta.review.compliance_check` - Flag posts for policy violations

**Typical Flow:**
1. Agent creates posts → Pending Approval
2. `review.digest` sends daily summary
3. Human reviews via `inbox.triage`
4. Bulk approve via `approve_and_route`

---

### Automation Plane
**Purpose:** Scheduled, recurring, and autonomous content generation

The autonomy layer. These skills enable hands-off content operations with guardrails.

**Core Principle:** Predictable automation with quota enforcement and safety nets.

**Skills:**
- `bolta.cron.generate_to_review` - Daily content generation → Pending Approval
- `bolta.cron.generate_and_schedule` - Autonomous scheduling (requires Safe Mode OFF)
- `bolta.recurring.from_template` - Recurring posts (daily tips, weekly roundups)
- `bolta.auto.respond_to_trending` - Auto-generate posts from trending topics
- `bolta.auto.content_gap_fill` - Detect scheduling gaps and auto-fill

**Safety Guardrails:**
- Quota enforcement (max posts/day, max API requests/hour)
- Job run tracking (observability for all executions)
- Autonomy mode compatibility checks
- Safe Mode routing (autopilot incompatible with Safe Mode ON)

---

### Control Plane
**Purpose:** Workspace governance, policy, and audit

The management layer for teams, permissions, security, and compliance.

**Core Principle:** Visibility and control for workspace administrators.

**Skills:**
- `bolta.team.create_agent_teammate` - Provision agent principals with specific roles
- `bolta.team.rotate_key` - Rotate API keys for security
- `bolta.policy.explain` - Explain authorization decisions ("Why was this blocked?")
- `bolta.audit.export_activity` - Export audit logs (PostActivity, JobRuns)
- `bolta.quota.status` - View current quota usage (daily posts, hourly API calls)
- `bolta.workspace.config` - View/update autonomy mode, Safe Mode, quotas

**Typical Use Cases:**
- Onboarding new team members (human or agent)
- Investigating authorization failures
- Compliance reporting (SOC2, GDPR data exports)
- Quota monitoring and adjustment

---

## Full Skill Index

### Voice Plane Skills

#### bolta.voice.bootstrap
**Path:** `skills/voice-plane/bolta.voice.bootstrap/SKILL.md`
**Purpose:** Interactive voice profile creation wizard
**Inputs:** Brand name, industry, target audience
**Outputs:** Complete VoiceProfile (tone, dos, don'ts, constraints)
**Permissions:** `voice:write`
**Safe Mode:** Compatible
**Typical Duration:** 5-10 minutes (interactive)

#### bolta.voice.learn_from_samples
**Path:** `skills/voice-plane/bolta.voice.learn_from_samples/SKILL.md`
**Purpose:** Extract voice patterns from existing content
**Inputs:** URLs or text samples (3-10 examples)
**Outputs:** Voice profile draft with auto-detected patterns
**Permissions:** `voice:write`
**Safe Mode:** Compatible
**Typical Duration:** 2-3 minutes

#### bolta.voice.evolve
**Path:** `skills/voice-plane/bolta.voice.evolve/SKILL.md`
**Purpose:** Refine voice based on approved posts
**Inputs:** Date range for approved posts
**Outputs:** Updated VoiceProfile (version incremented)
**Permissions:** `voice:write`, `posts:read`
**Safe Mode:** Compatible
**Typical Duration:** 1-2 minutes
**Note:** Creates new VoiceProfileVersion snapshot

#### bolta.voice.validate
**Path:** `skills/voice-plane/bolta.voice.validate/SKILL.md`
**Purpose:** Score content against voice profile
**Inputs:** Post ID or content text
**Outputs:** Compliance score (0-100), deviation report
**Permissions:** `voice:read`, `posts:read`
**Safe Mode:** Compatible
**Typical Duration:** < 30 seconds

---

### Content Plane Skills

#### bolta.draft.post
**Path:** `skills/content-plane/bolta.draft.post/SKILL.md`
**Purpose:** Create a single post in Draft status
**Inputs:** Topic, platform(s), optional voice profile ID
**Outputs:** Post ID (Draft status)
**Permissions:** `posts:write`
**Safe Mode:** Always routes to Draft
**Autonomy Mode:** Respects assisted/managed routing
**Quota Impact:** +1 to daily post count
**Typical Duration:** 30-60 seconds

#### bolta.loop.from_template
**Path:** `skills/content-plane/bolta.loop.from_template/SKILL.md`
**Purpose:** Generate multiple posts from a template
**Inputs:** Template ID, count (1-50), variation parameters
**Outputs:** Array of Post IDs
**Permissions:** `posts:write`, `templates:read`
**Safe Mode:** Routes all posts to Draft
**Quota Impact:** +N to daily post count (checked before execution)
**Typical Duration:** 1-3 minutes (depends on count)
**Note:** Uses JobRun tracking for observability

#### bolta.week.plan
**Path:** `skills/content-plane/bolta.week.plan/SKILL.md`
**Purpose:** Plan a week's content with scheduling
**Inputs:** Start date, posting frequency, themes
**Outputs:** 7-day content calendar with scheduled posts
**Permissions:** `posts:write`, `posts:schedule`
**Safe Mode:** Routes to Pending Approval if ON
**Autonomy Mode:** Respects managed/autopilot routing
**Quota Impact:** +5-15 to daily post count (spread across week)
**Typical Duration:** 3-5 minutes

#### bolta.content.repurpose
**Path:** `skills/content-plane/bolta.content.repurpose/SKILL.md`
**Purpose:** Transform long-form content into social posts
**Inputs:** Blog URL or full text, target platforms
**Outputs:** Multiple platform-specific posts
**Permissions:** `posts:write`
**Safe Mode:** Routes to Draft
**Typical Duration:** 2-4 minutes

#### bolta.content.thread_builder
**Path:** `skills/content-plane/bolta.content.thread_builder/SKILL.md`
**Purpose:** Create multi-post threads
**Inputs:** Topic, thread length (2-10 posts), platform
**Outputs:** Linked post sequence
**Permissions:** `posts:write`
**Safe Mode:** Routes to Draft
**Typical Duration:** 1-2 minutes

---

### Review Plane Skills

#### bolta.inbox.triage
**Path:** `skills/review-plane/bolta.inbox.triage/SKILL.md`
**Purpose:** Organize pending posts by priority
**Inputs:** Optional filters (platform, date range)
**Outputs:** Categorized list of posts awaiting review
**Permissions:** `posts:read`, `posts:review`
**Safe Mode:** N/A (read-only)
**Typical Duration:** < 10 seconds

#### bolta.review.digest
**Path:** `skills/review-plane/bolta.review.digest/SKILL.md`
**Purpose:** Daily summary of posts awaiting review
**Inputs:** None (workspace context)
**Outputs:** Formatted summary with quick approve links
**Permissions:** `posts:read`, `posts:review`
**Safe Mode:** N/A (read-only)
**Typical Duration:** < 5 seconds
**Note:** Designed for cron execution (daily 9am)

#### bolta.review.approve_and_route
**Path:** `skills/review-plane/bolta.review.approve_and_route/SKILL.md`
**Purpose:** Bulk approve and schedule posts
**Inputs:** Post IDs or filter criteria
**Outputs:** Updated post statuses
**Permissions:** `posts:write`, `posts:approve`, `posts:schedule`
**Safe Mode:** N/A (human override)
**Typical Duration:** < 30 seconds
**Note:** Bypasses Safe Mode (human decision)

#### bolta.review.suggest_edits
**Path:** `skills/review-plane/bolta.review.suggest_edits/SKILL.md`
**Purpose:** AI-powered improvement suggestions
**Inputs:** Post ID
**Outputs:** Suggested edits with rationale
**Permissions:** `posts:read`, `voice:read`
**Safe Mode:** N/A (read-only)
**Typical Duration:** < 30 seconds

#### bolta.review.compliance_check
**Path:** `skills/review-plane/bolta.review.compliance_check/SKILL.md`
**Purpose:** Flag posts for policy violations
**Inputs:** Post ID or bulk filter
**Outputs:** Compliance report with severity flags
**Permissions:** `posts:read`, `policies:read`
**Safe Mode:** N/A (read-only)
**Typical Duration:** < 10 seconds

---

### Automation Plane Skills

#### bolta.cron.generate_to_review
**Path:** `skills/automation-plane/bolta.cron.generate_to_review/SKILL.md`
**Purpose:** Daily content generation → Pending Approval
**Inputs:** None (uses workspace settings)
**Outputs:** Posts in Pending Approval status
**Permissions:** `posts:write`, `cron:execute`
**Safe Mode:** Compatible (routes to Pending Approval)
**Autonomy Mode:** Recommended for managed/governance
**Quota Impact:** +3-10 posts/day (configurable)
**Typical Duration:** 2-5 minutes
**Execution:** Daily cron (configurable time)

#### bolta.cron.generate_and_schedule
**Path:** `skills/automation-plane/bolta.cron.generate_and_schedule/SKILL.md`
**Purpose:** Autonomous scheduling (no human review)
**Inputs:** None (uses workspace settings)
**Outputs:** Posts in Scheduled status
**Permissions:** `posts:write`, `posts:schedule`, `cron:execute`
**Safe Mode:** **INCOMPATIBLE** (requires Safe Mode OFF)
**Autonomy Mode:** **REQUIRES autopilot**
**Quota Impact:** +5-15 posts/day (configurable)
**Typical Duration:** 3-7 minutes
**Execution:** Daily cron (configurable time)
**Warning:** Bypasses human review — use with caution

#### bolta.recurring.from_template
**Path:** `skills/automation-plane/bolta.recurring.from_template/SKILL.md`
**Purpose:** Recurring posts (daily tips, weekly roundups)
**Inputs:** Template ID, recurrence pattern (daily/weekly/monthly)
**Outputs:** RecurringPostReview record + scheduled posts
**Permissions:** `posts:write`, `templates:read`
**Safe Mode:** Respects routing
**Quota Impact:** +N posts per recurrence
**Typical Duration:** 1-2 minutes (setup)

#### bolta.auto.respond_to_trending
**Path:** `skills/automation-plane/bolta.auto.respond_to_trending/SKILL.md`
**Purpose:** Auto-generate posts from trending topics
**Inputs:** Trending topic sources (Twitter, Google Trends)
**Outputs:** Posts related to current trends
**Permissions:** `posts:write`, `integrations:read`
**Safe Mode:** Routes to Pending Approval
**Quota Impact:** +1-5 posts/day
**Typical Duration:** 2-3 minutes

#### bolta.auto.content_gap_fill
**Path:** `skills/automation-plane/bolta.auto.content_gap_fill/SKILL.md`
**Purpose:** Detect scheduling gaps and auto-fill
**Inputs:** Date range to analyze
**Outputs:** Posts to fill detected gaps
**Permissions:** `posts:write`, `posts:read`
**Safe Mode:** Routes to Pending Approval
**Quota Impact:** Variable (based on gaps detected)
**Typical Duration:** 3-5 minutes

---

### Control Plane Skills

#### bolta.team.create_agent_teammate
**Path:** `skills/control-plane/bolta.team.create_agent_teammate/SKILL.md`
**Purpose:** Provision agent principals with roles
**Inputs:** Agent name, role (creator/editor/reviewer), permissions
**Outputs:** AgentPrincipal record + API key
**Permissions:** `workspace:admin`, `agents:create`
**Safe Mode:** N/A (admin operation)
**Role Required:** Owner or Admin
**Typical Duration:** < 30 seconds

#### bolta.team.rotate_key
**Path:** `skills/control-plane/bolta.team.rotate_key/SKILL.md`
**Purpose:** Rotate API keys for security
**Inputs:** API key ID or agent ID
**Outputs:** New API key (old key revoked)
**Permissions:** `workspace:admin`, `agents:manage`
**Safe Mode:** N/A (admin operation)
**Role Required:** Owner or Admin
**Typical Duration:** < 10 seconds
**Note:** Old key immediately invalidated

#### bolta.policy.explain
**Path:** `skills/control-plane/bolta.policy.explain/SKILL.md`
**Purpose:** Explain authorization decisions
**Inputs:** Action attempt (e.g., "Why can't I publish?")
**Outputs:** Policy analysis with specific blockers
**Permissions:** None (informational)
**Safe Mode:** N/A (read-only)
**Typical Duration:** < 5 seconds
**Use Case:** Troubleshooting "Access Denied" errors

#### bolta.audit.export_activity
**Path:** `skills/control-plane/bolta.audit.export_activity/SKILL.md`
**Purpose:** Export audit logs
**Inputs:** Date range, filters (principal, action type, denied actions)
**Outputs:** CSV or JSON export of PostActivity records
**Permissions:** `workspace:admin`, `audit:read`
**Safe Mode:** N/A (admin operation)
**Role Required:** Owner or Admin
**Typical Duration:** < 30 seconds
**Use Case:** Compliance reporting, SOC2 audits

#### bolta.quota.status
**Path:** `skills/control-plane/bolta.quota.status/SKILL.md`
**Purpose:** View current quota usage
**Inputs:** None (workspace context)
**Outputs:** Daily post count, hourly API usage, limits, percentage
**Permissions:** `workspace:read`
**Safe Mode:** N/A (read-only)
**Typical Duration:** < 5 seconds

#### bolta.workspace.config
**Path:** `skills/control-plane/bolta.workspace.config/SKILL.md`
**Purpose:** View/update workspace settings
**Inputs:** Settings to update (autonomy_mode, safe_mode, quotas)
**Outputs:** Updated workspace configuration
**Permissions:** `workspace:admin`
**Safe Mode:** N/A (admin operation)
**Role Required:** Owner or Admin
**Typical Duration:** < 10 seconds
**Warning:** Changing autonomy mode affects all agent operations

---

## Recommended Install Sets

Install sets are curated skill bundles tailored to specific autonomy modes and use cases.

### Assisted Mode Install Set
**Autonomy Level:** Low (maximum human control)
**Safe Mode:** Must be ON
**Use Case:** New users, high-stakes brands, learning Bolta

**Skills:**
- `bolta.voice.bootstrap` - Set up initial voice profile
- `bolta.draft.post` - Create individual posts (always Draft)
- `bolta.loop.from_template` - Scale content creation safely
- `bolta.week.plan` - Plan content calendar

**Rationale:**
Assisted mode prioritizes learning and control. All content goes to Draft for manual review before scheduling. Ideal for:
- Teams new to AI content generation
- Brands with strict compliance requirements
- Users who want to learn Bolta patterns before automating

**Expected Workflow:**
1. Bootstrap voice profile
2. Create posts in Draft (manually or via templates)
3. Human reviews and schedules each post
4. Graduate to Managed when comfortable

---

### Managed Mode Install Set
**Autonomy Level:** Medium (guided automation with oversight)
**Safe Mode:** ON (recommended) or OFF
**Use Case:** Established users, moderate volume, review workflows

**Skills:**
- All Assisted skills +
- `bolta.inbox.triage` - Organize posts for review
- `bolta.review.digest` - Daily review summaries
- `bolta.review.approve_and_route` - Bulk approval workflow
- `bolta.voice.validate` - Quality scoring
- `bolta.cron.generate_to_review` - Daily automated generation

**Rationale:**
Managed mode balances efficiency with oversight. Agent generates content autonomously, but humans approve before publishing. Ideal for:
- Teams with 1-2 reviewers
- Brands publishing 3-10 posts/day
- Users who trust the voice profile

**Expected Workflow:**
1. Agent generates posts overnight (via cron) → Pending Approval
2. Daily digest arrives at 9am
3. Reviewer triages inbox, validates voice compliance
4. Bulk approve/schedule approved posts
5. Refine voice profile based on patterns

---

### Autopilot Mode Install Set
**Autonomy Level:** High (hands-off automation)
**Safe Mode:** Must be OFF (incompatible)
**Use Case:** High volume, trusted voice, minimal oversight

**Skills:**
- All Managed skills +
- `bolta.cron.generate_and_schedule` - Autonomous scheduling
- `bolta.auto.respond_to_trending` - Trend-based posting
- `bolta.auto.content_gap_fill` - Auto-fill scheduling gaps
- `bolta.recurring.from_template` - Recurring post automation
- `bolta.quota.status` - Monitor quota usage

**Rationale:**
Autopilot mode maximizes efficiency for high-volume operations. Agent schedules directly without human approval. Ideal for:
- Established brands with proven voice profiles
- High-frequency posting (10+ posts/day)
- Teams with minimal manual review capacity

**Expected Workflow:**
1. Agent generates and schedules posts automatically
2. Quota enforcement prevents runaway generation
3. Periodic voice validation checks (weekly)
4. Human reviews published analytics, adjusts strategy

**Warning:**
Autopilot bypasses human review. Only use with:
- Well-tested voice profiles (version 5+)
- Quota limits configured (max 20 posts/day recommended)
- Regular validation spot-checks (review 10% of published posts)

---

### Governance Mode Install Set
**Autonomy Level:** N/A (control & audit focused)
**Safe Mode:** N/A
**Use Case:** Admins, compliance teams, workspace management

**Skills:**
- `bolta.policy.explain` - Authorization troubleshooting
- `bolta.audit.export_activity` - Compliance exports
- `bolta.team.create_agent_teammate` - Agent provisioning
- `bolta.team.rotate_key` - Security operations
- `bolta.workspace.config` - Workspace administration
- `bolta.quota.status` - Usage monitoring
- `bolta.voice.validate` - Quality auditing

**Rationale:**
Governance mode is not an autonomy level — it's a control plane install set for administrators. Ideal for:
- Workspace owners managing teams
- Compliance officers conducting audits
- Security teams rotating keys
- Admins troubleshooting authorization issues

**Expected Workflow:**
1. Onboard new team members (human or agent)
2. Configure workspace policies (Safe Mode, autonomy, quotas)
3. Monitor quota usage and adjust limits
4. Export audit logs for compliance reporting
5. Rotate API keys on schedule (e.g., quarterly)
6. Investigate authorization failures via policy.explain

---

## Decision Matrix: Skill Recommendations

This matrix determines which skills to recommend based on workspace context.

### Input Variables
1. **Safe Mode** (ON/OFF)
2. **Autonomy Mode** (assisted/managed/autopilot/governance)
3. **User Role** (owner/admin/editor/creator/reviewer/viewer)
4. **Agent Permissions** (if principal is agent)
5. **Workspace Quotas** (daily post limit, hourly API limit)
6. **Voice Profile Status** (exists, version number)

### Decision Rules

#### Rule 1: Voice Bootstrapping (First-Time Setup)
```
IF voice_profile_count == 0:
  RECOMMEND: bolta.voice.bootstrap (HIGH PRIORITY)
  RATIONALE: Cannot create content without voice profile
```

#### Rule 2: Safe Mode + Autopilot Incompatibility
```
IF safe_mode == ON AND autonomy_mode == "autopilot":
  ERROR: Incompatible configuration
  RECOMMEND: Either disable Safe Mode OR switch to "managed"
  RATIONALE: Autopilot bypasses review; contradicts Safe Mode intent
```

#### Rule 3: Agent Permission Gating
```
IF principal_type == "agent":
  IF agent.permissions NOT IN required_permissions:
    EXCLUDE: Skills requiring missing permissions
    RECOMMEND: bolta.policy.explain to understand blockers
```

#### Rule 4: Role-Based Filtering
```
IF role IN ["viewer", "reviewer"]:
  EXCLUDE: All write operations (posts:write, voice:write)
  INCLUDE: Read-only skills (audit.export, policy.explain)

IF role IN ["creator", "editor"]:
  INCLUDE: Content plane skills
  EXCLUDE: Control plane skills (team.*, workspace.config)

IF role IN ["admin", "owner"]:
  INCLUDE: All skills (no restrictions)
```

#### Rule 5: Quota-Based Warnings
```
IF daily_posts_used >= (daily_post_limit * 0.8):
  WARN: "Approaching daily quota limit"
  RECOMMEND: bolta.quota.status to view usage

IF daily_posts_used >= daily_post_limit:
  BLOCK: All posts:write skills
  RECOMMEND: Increase quota via bolta.workspace.config
```

#### Rule 6: Autonomy Mode Routing
```
IF autonomy_mode == "assisted":
  INCLUDE: Content plane (draft only)
  EXCLUDE: Automation plane (no cron jobs)

IF autonomy_mode == "managed":
  INCLUDE: Content + Review planes
  INCLUDE: bolta.cron.generate_to_review (safe automation)
  EXCLUDE: bolta.cron.generate_and_schedule (requires autopilot)

IF autonomy_mode == "autopilot":
  INCLUDE: All automation skills
  REQUIRE: Safe Mode OFF
  RECOMMEND: Quota monitoring (quota.status)
```

---

## Registry Flow (Detailed)

### Step 1: Gather Workspace Context
**API Call:** `GET /api/v1/workspaces/{workspace_id}`

**Extract:**
- `safe_mode` (boolean)
- `autonomy_mode` (assisted/managed/autopilot/governance)
- `max_posts_per_day` (int, nullable)
- `max_api_requests_per_hour` (int, nullable)

### Step 2: Identify Principal
**API Call:** `GET /api/v1/me` or use request context

**Extract:**
- `principal_type` (user or agent)
- `role` (owner/admin/editor/creator/reviewer/viewer)
- If agent: `permissions` array, `autonomy_override`

### Step 3: Check Voice Profile Status
**API Call:** `GET /api/v1/workspaces/{workspace_id}/voice-profiles`

**Extract:**
- `voice_profile_count` (0 = needs bootstrap)
- Latest `version` (higher version = more refined)
- `status` (active/draft/archived)

### Step 4: Check Quota Usage
**API Call:** `GET /api/v1/workspaces/{workspace_id}/quota-status` (via `bolta.quota.status`)

**Extract:**
- `daily_posts.used` / `daily_posts.limit`
- `hourly_api_requests.used` / `hourly_api_requests.limit`

### Step 5: Apply Decision Rules
Run through decision matrix (see above) to filter skills.

**Output:**
- `recommended_skills` - Array of skill slugs
- `excluded_skills` - Array with exclusion reasons
- `warnings` - Array of configuration issues

### Step 6: Return Structured Response
```json
{
  "workspace_id": "uuid",
  "safe_mode": true,
  "autonomy_mode": "managed",
  "role": "editor",
  "principal_type": "user",
  "voice_profile_status": {
    "exists": true,
    "version": 3,
    "status": "active"
  },
  "quota_status": {
    "daily_posts": {
      "used": 12,
      "limit": 100,
      "percentage": 12
    },
    "hourly_api_requests": {
      "used": 45,
      "limit": 1000,
      "percentage": 4.5
    }
  },
  "recommended_mode": "managed",
  "recommended_skills": [
    "bolta.draft.post",
    "bolta.loop.from_template",
    "bolta.week.plan",
    "bolta.inbox.triage",
    "bolta.review.digest",
    "bolta.review.approve_and_route",
    "bolta.voice.validate",
    "bolta.cron.generate_to_review"
  ],
  "excluded_skills": [
    {
      "skill": "bolta.cron.generate_and_schedule",
      "reason": "Requires autonomy_mode=autopilot (current: managed)"
    },
    {
      "skill": "bolta.workspace.config",
      "reason": "Requires role owner/admin (current: editor)"
    }
  ],
  "warnings": [],
  "next_steps": [
    "Install recommended skills via MCP or API",
    "Run bolta.voice.validate to check content quality",
    "Configure daily digest via bolta.review.digest"
  ]
}
```

---

## Output Examples

### Example 1: New Workspace (First-Time Setup)
```json
{
  "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
  "safe_mode": true,
  "autonomy_mode": "assisted",
  "role": "owner",
  "principal_type": "user",
  "voice_profile_status": {
    "exists": false,
    "version": 0,
    "status": null
  },
  "quota_status": {
    "daily_posts": {"used": 0, "limit": 100, "percentage": 0},
    "hourly_api_requests": {"used": 0, "limit": 1000, "percentage": 0}
  },
  "recommended_mode": "assisted",
  "recommended_skills": [
    "bolta.voice.bootstrap"
  ],
  "excluded_skills": [],
  "warnings": [
    {
      "type": "missing_voice_profile",
      "message": "No voice profile found. Run bolta.voice.bootstrap to get started.",
      "severity": "high"
    }
  ],
  "next_steps": [
    "1. Run bolta.voice.bootstrap to create your brand voice",
    "2. After voice setup, install content plane skills",
    "3. Create your first post with bolta.draft.post"
  ]
}
```

### Example 2: Managed Mode (Typical Production)
```json
{
  "workspace_id": "660e8400-e29b-41d4-a716-446655440001",
  "safe_mode": true,
  "autonomy_mode": "managed",
  "role": "admin",
  "principal_type": "user",
  "voice_profile_status": {
    "exists": true,
    "version": 5,
    "status": "active"
  },
  "quota_status": {
    "daily_posts": {"used": 18, "limit": 50, "percentage": 36},
    "hourly_api_requests": {"used": 142, "limit": 1000, "percentage": 14.2}
  },
  "recommended_mode": "managed",
  "recommended_skills": [
    "bolta.draft.post",
    "bolta.loop.from_template",
    "bolta.week.plan",
    "bolta.content.repurpose",
    "bolta.inbox.triage",
    "bolta.review.digest",
    "bolta.review.approve_and_route",
    "bolta.voice.validate",
    "bolta.voice.evolve",
    "bolta.cron.generate_to_review",
    "bolta.team.create_agent_teammate",
    "bolta.audit.export_activity",
    "bolta.quota.status"
  ],
  "excluded_skills": [
    {
      "skill": "bolta.cron.generate_and_schedule",
      "reason": "Requires autonomy_mode=autopilot AND safe_mode=OFF"
    }
  ],
  "warnings": [],
  "next_steps": [
    "Configure daily content generation via bolta.cron.generate_to_review",
    "Set up review workflow with digest notifications",
    "Consider voice evolution (version 5 is mature)"
  ]
}
```

### Example 3: Autopilot Mode (High Volume)
```json
{
  "workspace_id": "770e8400-e29b-41d4-a716-446655440002",
  "safe_mode": false,
  "autonomy_mode": "autopilot",
  "role": "owner",
  "principal_type": "user",
  "voice_profile_status": {
    "exists": true,
    "version": 12,
    "status": "active"
  },
  "quota_status": {
    "daily_posts": {"used": 47, "limit": 200, "percentage": 23.5},
    "hourly_api_requests": {"used": 523, "limit": 2000, "percentage": 26.15}
  },
  "recommended_mode": "autopilot",
  "recommended_skills": [
    "bolta.draft.post",
    "bolta.loop.from_template",
    "bolta.week.plan",
    "bolta.content.repurpose",
    "bolta.content.thread_builder",
    "bolta.inbox.triage",
    "bolta.review.digest",
    "bolta.review.approve_and_route",
    "bolta.voice.validate",
    "bolta.voice.evolve",
    "bolta.cron.generate_to_review",
    "bolta.cron.generate_and_schedule",
    "bolta.auto.respond_to_trending",
    "bolta.auto.content_gap_fill",
    "bolta.recurring.from_template",
    "bolta.quota.status",
    "bolta.workspace.config"
  ],
  "excluded_skills": [],
  "warnings": [
    {
      "type": "high_autonomy",
      "message": "Autopilot mode bypasses human review. Monitor quota usage and validate voice compliance regularly.",
      "severity": "medium"
    },
    {
      "type": "quota_usage",
      "message": "Daily quota at 23.5% usage. Consider monitoring trends to avoid hitting limit.",
      "severity": "low"
    }
  ],
  "next_steps": [
    "Monitor quota usage daily via bolta.quota.status",
    "Run voice validation spot-checks (10% of published posts)",
    "Review JobRun stats weekly for error trends"
  ]
}
```

### Example 4: Agent Principal (API Key)
```json
{
  "workspace_id": "880e8400-e29b-41d4-a716-446655440003",
  "safe_mode": true,
  "autonomy_mode": "managed",
  "role": "creator",
  "principal_type": "agent",
  "agent": {
    "id": "agent-uuid",
    "name": "Content Bot",
    "permissions": ["posts:write", "posts:read", "templates:read"],
    "autonomy_override": null
  },
  "voice_profile_status": {
    "exists": true,
    "version": 7,
    "status": "active"
  },
  "quota_status": {
    "daily_posts": {"used": 8, "limit": 30, "percentage": 26.67},
    "hourly_api_requests": {"used": 67, "limit": 500, "percentage": 13.4}
  },
  "recommended_mode": "managed",
  "recommended_skills": [
    "bolta.draft.post",
    "bolta.loop.from_template"
  ],
  "excluded_skills": [
    {
      "skill": "bolta.week.plan",
      "reason": "Requires posts:schedule permission (agent lacks this)"
    },
    {
      "skill": "bolta.review.approve_and_route",
      "reason": "Requires posts:approve permission (agent lacks this)"
    },
    {
      "skill": "bolta.voice.evolve",
      "reason": "Requires voice:write permission (agent lacks this)"
    },
    {
      "skill": "bolta.workspace.config",
      "reason": "Requires workspace:admin permission (agent role: creator)"
    }
  ],
  "warnings": [
    {
      "type": "limited_permissions",
      "message": "Agent has limited permissions. Some skills are unavailable.",
      "severity": "info"
    }
  ],
  "next_steps": [
    "Use bolta.draft.post to create content",
    "Use bolta.loop.from_template for batch generation",
    "Human reviewers should use bolta.review.approve_and_route to publish"
  ]
}
```

### Example 5: Quota Limit Reached
```json
{
  "workspace_id": "990e8400-e29b-41d4-a716-446655440004",
  "safe_mode": true,
  "autonomy_mode": "managed",
  "role": "editor",
  "principal_type": "user",
  "voice_profile_status": {
    "exists": true,
    "version": 4,
    "status": "active"
  },
  "quota_status": {
    "daily_posts": {"used": 100, "limit": 100, "percentage": 100},
    "hourly_api_requests": {"used": 234, "limit": 1000, "percentage": 23.4}
  },
  "recommended_mode": "managed",
  "recommended_skills": [
    "bolta.inbox.triage",
    "bolta.review.digest",
    "bolta.review.approve_and_route",
    "bolta.voice.validate",
    "bolta.quota.status",
    "bolta.policy.explain"
  ],
  "excluded_skills": [
    {
      "skill": "bolta.draft.post",
      "reason": "Daily quota limit reached (100/100 posts)"
    },
    {
      "skill": "bolta.loop.from_template",
      "reason": "Daily quota limit reached (100/100 posts)"
    },
    {
      "skill": "bolta.week.plan",
      "reason": "Daily quota limit reached (100/100 posts)"
    }
  ],
  "warnings": [
    {
      "type": "quota_exceeded",
      "message": "Daily post quota limit reached. No new posts can be created until tomorrow (resets at UTC midnight).",
      "severity": "high"
    }
  ],
  "next_steps": [
    "Review and approve existing posts in queue",
    "Consider increasing daily quota via bolta.workspace.config (admin only)",
    "Check quota status at midnight UTC for reset"
  ]
}
```

### Example 6: Incompatible Configuration (Autopilot + Safe Mode)
```json
{
  "workspace_id": "aa0e8400-e29b-41d4-a716-446655440005",
  "safe_mode": true,
  "autonomy_mode": "autopilot",
  "role": "owner",
  "principal_type": "user",
  "voice_profile_status": {
    "exists": true,
    "version": 8,
    "status": "active"
  },
  "quota_status": {
    "daily_posts": {"used": 5, "limit": 150, "percentage": 3.33},
    "hourly_api_requests": {"used": 12, "limit": 1500, "percentage": 0.8}
  },
  "recommended_mode": "ERROR",
  "recommended_skills": [],
  "excluded_skills": [
    {
      "skill": "ALL",
      "reason": "Incompatible configuration: autopilot mode requires Safe Mode OFF"
    }
  ],
  "warnings": [
    {
      "type": "configuration_conflict",
      "message": "Autopilot mode is incompatible with Safe Mode ON. Autopilot bypasses human review, which contradicts Safe Mode's intent.",
      "severity": "critical"
    }
  ],
  "next_steps": [
    "Choose one of the following:",
    "  A) Disable Safe Mode to use autopilot (workspace.config)",
    "  B) Switch to 'managed' autonomy mode to keep Safe Mode ON",
    "Current config blocks all agent operations until resolved."
  ],
  "error": {
    "code": "INCOMPATIBLE_CONFIGURATION",
    "message": "Autopilot autonomy mode requires Safe Mode to be OFF. Please update workspace configuration."
  }
}
```

---

## Integration with Authorization System

The registry integrates with Bolta's authorization layer to ensure skill recommendations respect workspace policies.

### Authorization Flow Integration

**Step 1: Pre-flight Authorization Check**
Before recommending a skill, check if the principal is authorized:

```python
from users.authorization import authorize, PostAction

# Check if user can create posts
auth_result = authorize(
    principal_type="user",
    role="editor",
    workspace=workspace,
    action=PostAction.CREATE,
    requested_status="Scheduled",
    agent=None  # or agent instance if principal is agent
)

if not auth_result.allowed:
    # Exclude skill with reason
    excluded_skills.append({
        "skill": "bolta.week.plan",
        "reason": auth_result.reason
    })
```

**Step 2: Respect Autonomy Mode Routing**
Skills that create posts must account for autonomy mode routing:

```python
# Autonomy mode routing table
AUTONOMY_ROUTING = {
    "assisted": {
        "Draft": "Draft",           # Always Draft
        "Scheduled": "Draft",       # Routed to Draft
        "Posted": "Draft"           # Routed to Draft
    },
    "managed": {
        "Draft": "Draft",
        "Scheduled": "Pending Approval",  # Routed to review
        "Posted": "Pending Approval"      # Routed to review
    },
    "autopilot": {
        "Draft": "Draft",
        "Scheduled": "Scheduled",    # No routing (requires Safe Mode OFF)
        "Posted": "Posted"           # No routing (requires Safe Mode OFF)
    },
    "governance": {
        "Draft": "Pending Approval",
        "Scheduled": "Pending Approval",
        "Posted": "Pending Approval"
    }
}

# Skills should document expected output status after routing
```

**Step 3: Quota Enforcement**
Skills that create posts must respect quota limits:

```python
from posts.quota_enforcement import QuotaEnforcer

# Check quota before recommending bulk operations
allowed, reason = QuotaEnforcer.check_daily_post_quota(
    workspace=workspace,
    count=10  # e.g., bolta.loop.from_template with count=10
)

if not allowed:
    excluded_skills.append({
        "skill": "bolta.loop.from_template",
        "reason": reason  # e.g., "Daily quota exceeded (95/100)"
    })
```

**Step 4: Safe Mode Compatibility**
Some skills are incompatible with Safe Mode:

```python
SAFE_MODE_INCOMPATIBLE = [
    "bolta.cron.generate_and_schedule",  # Bypasses review
]

if workspace.safe_mode and skill in SAFE_MODE_INCOMPATIBLE:
    excluded_skills.append({
        "skill": skill,
        "reason": "Incompatible with Safe Mode ON (requires human review bypass)"
    })
```

---

## Skill Metadata Schema

Each skill should provide structured metadata for registry indexing:

```yaml
skill:
  slug: bolta.draft.post
  display_name: Draft Post
  version: 1.2.0
  plane: content

permissions:
  required:
    - posts:write
  optional:
    - voice:read  # For voice profile selection

compatibility:
  safe_mode: compatible  # compatible | incompatible | n/a
  autonomy_modes:
    - assisted
    - managed
    - autopilot
  roles:
    - owner
    - admin
    - editor
    - creator

quotas:
  posts_created: 1  # Impact on daily quota
  api_requests: 2   # Typical API call count

dependencies:
  required:
    - voice_profile  # Must have voice profile
  optional:
    - templates      # Enhanced with templates

execution:
  typical_duration_seconds: 45
  max_duration_seconds: 120
  idempotent: true
  retryable: true

outputs:
  post_status: Draft  # Before autonomy routing
  job_tracked: true   # Creates JobRun record
  audit_logged: true  # Creates PostActivity record
```

---

## Version History

**0.5.4** (Current) - Version bump

**0.5.3** - Installation & First Run Guidance
- **Added comprehensive "Installation & First Run" section**
- **Added complete skill pack installation instructions (git clone, download)**
- **Added README.md reading prompt (critical for setup)**
- **Added directory structure overview (21+ skills across 5 planes)**
- Added recommended first-run flow (verify → configure → test)
- Added common first-run mistakes guide (avoid pitfalls)
- Added post-installation checklist (10-item verification)
- Enhanced discoverability of full skill library
- Addresses user prompt: "Should we prompt user to install rest of skills from registry?"

**0.5.1** - Security Patch
- **SECURITY: Added explicit Required Environment Variables section**
- **SECURITY: Declared BOLTA_API_KEY, BOLTA_WORKSPACE_ID as required**
- **SECURITY: Added trusted domains list (api.bolta.ai, platty.boltathread.com)**
- **SECURITY: Enhanced security best practices (rotation, least-privilege, monitoring)**
- Added environment variable configuration examples for all platforms
- Added credential security reminders throughout documentation
- Addressed security audit finding: "manifest does not declare required env vars"

**0.5.0**
- Added comprehensive Getting Started guide
- Added Agent API setup instructions (bolta.ai/register)
- Added setup verification steps
- Added troubleshooting section for common setup issues
- Added next steps after agent registration

**0.4.0** 
- Added comprehensive skill descriptions with metadata
- Added detailed decision matrix and authorization integration
- Added 6 output examples covering all scenarios
- Added quota enforcement and compatibility checks
- Added voice plane skills (validate, evolve)
- Added automation plane skills (trending, gap-fill)
- Added control plane skills (quota, workspace config)
- Added skill metadata schema

**0.3.0**
- Added recommended install sets (assisted, managed, autopilot, governance)
- Added plane groupings (voice, content, review, automation, control)
- Added registry flow documentation
- Added basic output example

**0.2.0**
- Added initial skill index
- Added plane definitions

**0.1.0**
- Initial registry structure

---


## Support

For skill installation issues, contact: support@bolta.ai
