# BotSee Skill for Claude Code

> Monitor your brand's AI visibility across ChatGPT, Claude, Perplexity, and Gemini.

**Version:** 0.2.4

BotSee is an agent-first API that delivers structured data from every major AI search engine — competitors, keywords, sources, and raw responses — programmatically, from Claude Code.

- Find competitors as AI search engines see them
- Measure share of voice vs competitors
- Identify which sources AI cites for your category
- Uncover exact search queries AI runs for your space
- Generate AI-optimized content from analysis data
- Track visibility over time with historical analysis

## Installation

Copy the entire skill directory to Claude Code:
```bash
# macOS/Linux
cp -r . ~/.claude/skills/botsee
```

Restart Claude Code or reload skills.

## Requirements

- Claude Code
- Python 3 (pre-installed on macOS)

## Quick Start (Credit Card)

```bash
# Step 1: Get signup URL (credit card flow)
/botsee signup

# Step 2: Visit the URL in browser, complete signup

# Step 3: Paste your API key in the chat
# Claude will automatically save it

# Step 4: Create site and generate content
/botsee create-site https://example.com

# Optional: Customize generation counts
/botsee create-site https://example.com --types 3 --personas 2 --questions 10

# Run analysis (~660 credits)
/botsee analyze

# Generate blog post (15 credits)
/botsee content

# Check status and balance
/botsee
```

## Quick Start (USDC on Base)

```bash
# Step 1: Create signup token for USDC flow
/botsee signup --crypto

# Step 2: Initiate USDC payment on Base
/botsee signup-pay-usdc --amount-cents 250 --from-address 0xYOUR_WALLET

# Step 3: Check completion and save API key when ready
/botsee signup-status

# Step 4: Create site and generate content
/botsee create-site https://example.com

# Optional: Customize generation counts
/botsee create-site https://example.com --types 3 --personas 2 --questions 10

# Run analysis (~660 credits)
/botsee analyze

# Generate blog post (15 credits)
/botsee content

# Check status and balance
/botsee

# Optional: Top up credits later with USDC
/botsee topup-usdc --amount-cents 5000 --from-address 0xYOUR_WALLET
```

## Example Conversational Workflow

Use these natural language prompts to guide Claude through the complete BotSee workflow:

### Prompt 1: Install & Signup
```
Install the BotSee Skill from github.com/RivalSee/botsee-skill. Then sign me up for BotSee using my email user@example.com so I can analyze how AI search engines see my product.
```

### Prompt 2: Create Site with Structure
```
Create a BotSee site for https://myproduct.com with 1 customer type, 2 personas, and 5 questions per persona. Set it up so I can run a competitive analysis.
```

### Prompt 3: Analyze & Show Competitors
```
Run a competitive analysis and show me the full list of competitors mentioned by AI search engines, including their mention percentages and what contexts they appear in.
```

### Prompt 4: Show Keywords
```
Show me all the keywords that AI search engines associate with my product category, sorted by frequency.
```

### Prompt 5: Generate Blog Titles
```
Based on those keywords and competitor insights, give me 5 compelling blog post titles that would help us compete better in AI search results.
```

### Prompt 6: Write Blog Post
```
Write a full blog post for the first title, including our competitive position, opportunities, threats, and recommended actions based on the analysis data.
```

**Total cost:** ~725 credits ($7.25 at $0.01/credit) | **Time:** ~15 minutes
**Output:** Competitor rankings with percentages, keyword frequency analysis, and strategic blog content

## Commands

### Workflow Commands

#### `/botsee`
Shows current status, balance, and available commands.

```
🤖 BotSee
━━━━━━━━━━━━━━━
💰 Credits: 1,250
🌐 Sites: 1
🔑 Key: bts_live_abc123...
```

#### `/botsee signup`
Signup for BotSee and get your API key.
Default behavior is **Signup with Credit Card** (Stripe web flow).

**New user (no API key):**
```bash
# Step 1: Get signup URL
/botsee signup

# Step 2: Visit the URL, complete signup, and paste your API key in the chat
# Claude will automatically save it for you

# Step 3: Create your site
/botsee create-site https://example.com
```

The signup flow:
1. Run `/botsee signup` to get your unique signup URL
2. Visit the URL in your browser and complete signup
3. Paste your API key in the chat (e.g., "My API key is bts_live_abc123")
4. Claude automatically saves it - you can then run `/botsee create-site`

**Optional contact info:**
```bash
/botsee signup --email you@example.com --name "Your Name" --company "Your Company"
```

Contact fields are optional - the API will use defaults if not provided.

**Existing user (has API key):**
```bash
/botsee signup --api-key bts_live_YOUR_KEY
```

Validates and saves your existing API key.

**Cost:** Free (signup doesn't consume credits)

**Signup with USDC (Base):**
```bash
# Create signup token with USDC payment method
/botsee signup --crypto

# Start USDC payment (Base mainnet)
/botsee signup-pay-usdc --amount-cents 250 --from-address 0xYOUR_WALLET

# Poll signup status (saves API key on completion)
/botsee signup-status
```

Network:
- `base-mainnet` (Chain ID 8453, production)

#### `/botsee signup-pay-usdc`
Initiate USDC payment for a signup token (`POST /api/v1/signup/:token/pay-usdc`).

```bash
/botsee signup-pay-usdc --token <setup_token> --amount-cents 5000 --from-address 0xYOUR_WALLET
```

Optional:
- `--payment <proof>` x402 `payment` header value when retrying after HTTP 402
- `--tx-hash 0x...` build transaction-based x402 payload (`txHash`) automatically
- `--asset USDC` asset value for tx-hash payload (default: `USDC`)

Transaction-hash example:
```bash
/botsee signup-pay-usdc --token <setup_token> --amount-cents 5000 --from-address 0xYOUR_WALLET --tx-hash 0xYOUR_TX_HASH
```

#### `/botsee signup-status`
Check signup status and automatically save API key when completed.

```bash
/botsee signup-status
/botsee signup-status --token <setup_token>
```

#### `/botsee topup-usdc`
Add credits via USDC on Base (`POST /api/v1/billing/topups/usdc`).

```bash
/botsee topup-usdc --amount-cents 5000 --from-address 0xYOUR_WALLET
```

Optional:
- `--payment <proof>` x402 `payment` header value when retrying after HTTP 402
- `--tx-hash 0x...` build transaction-based x402 payload (`txHash`) automatically
- `--asset USDC` asset value for tx-hash payload (default: `USDC`)

Transaction-hash example:
```bash
/botsee topup-usdc --amount-cents 5000 --from-address 0xYOUR_WALLET --tx-hash 0xYOUR_TX_HASH
```

#### `/botsee create-site <domain>`
Create site and generate content.

**Requires:** API key from `/botsee signup`

```bash
/botsee create-site https://example.com
```

The create-site command will:
1. Create a site for the domain
2. Generate customer types, personas, and questions
3. Save configuration to workspace and user config

**Customize generation counts:**
```bash
/botsee create-site https://example.com --types 3 --personas 2 --questions 10
```

**Cost:** ~75 credits with defaults (2 types, 2 personas/type, 5 questions/persona)
- Site creation: 5 credits
- Customer types: 5 credits per type
- Personas: 5 credits per persona
- Questions: 10 credits flat per persona

#### `/botsee create-site <domain>`
Save custom configuration for later use with setup.

```bash
# With defaults (2/2/5)
/botsee create-site https://example.com

# With custom values
/botsee create-site https://example.com --types 3 --personas 3 --questions 10
```

Saves to `.context/botsee-config.json`. Setup reads this config automatically.

#### `/botsee config-show`
Display saved workspace configuration.

```
📋 BotSee Configuration
━━━━━━━━━━━━━━━━━━━━━
Domain: https://example.com
Customer Types: 2
Personas per Type: 2
Questions per Persona: 5

Ready to run: /botsee setup <domain>
```

#### `/botsee analyze`
Runs competitive analysis. Starts the analysis, polls until complete, then displays competitors, keywords, and cited sources.

```
📊 Top Competitors:
  1. competitor.com - 45 mentions
  2. rival.com - 32 mentions

🔑 Top Keywords:
  • "best email marketing" (12x)
  • "affordable crm software" (8x)

📄 Top Sources:
  • techcrunch.com (5x) ⭐
  • g2.com (3x)

💰 Remaining: 265 credits
```

**Cost:** ~660 credits per run (varies by question count and models)

#### `/botsee content`
Generates blog post from latest analysis. Auto-saves to `botsee-YYYYMMDD-HHMMSS.md`.

**Cost:** 15 credits

---

### Sites Management

#### `/botsee list-sites`
List all sites in your account.

```bash
/botsee list-sites
```

#### `/botsee get-site [uuid]`
View details of a specific site. If uuid is omitted, shows the current site from config.

```bash
/botsee get-site
/botsee get-site abc-def-123
```

#### `/botsee create-site <domain>`
Create a new site. Saves the new site UUID to config.

```bash
/botsee create-site https://example.com
```

**Cost:** 5 credits (auto-generates product_name and value_proposition)

#### `/botsee archive-site [uuid]`
Archive a site. If uuid is omitted, archives the current site.

```bash
/botsee archive-site
/botsee archive-site abc-def-123
```

---

### Customer Types Management

#### `/botsee list-types`
List all customer types for the current site.

```bash
/botsee list-types
```

#### `/botsee get-type <uuid>`
View details of a specific customer type.

```bash
/botsee get-type type-uuid-123
```

#### `/botsee create-type <name> [description]`
Create a new customer type manually.

```bash
/botsee create-type "Enterprise Buyers" "Large companies seeking solutions"
```

**Cost:** 5 credits

#### `/botsee generate-types [count]`
Generate customer types using AI. Defaults to 2.

```bash
/botsee generate-types
/botsee generate-types 3
```

**Cost:** 5 credits per type

#### `/botsee update-type <uuid> [--name NAME] [--description DESC]`
Update a customer type.

```bash
/botsee update-type type-uuid-123 --name "Enterprise Decision Makers"
/botsee update-type type-uuid-123 --description "C-level executives"
```

#### `/botsee archive-type <uuid>`
Archive a customer type.

```bash
/botsee archive-type type-uuid-123
```

---

### Personas Management

#### `/botsee list-personas [type_uuid]`
List personas. Show all or filter by customer type.

```bash
/botsee list-personas
/botsee list-personas type-uuid-123
```

#### `/botsee get-persona <uuid>`
View details of a specific persona.

```bash
/botsee get-persona persona-uuid-456
```

#### `/botsee create-persona <type_uuid> <name> [description]`
Create a new persona manually.

```bash
/botsee create-persona type-uuid-123 "Sarah Chen" "VP of Marketing at mid-sized SaaS"
```

**Cost:** 5 credits

#### `/botsee generate-personas <type_uuid> [count]`
Generate personas for a customer type using AI. Defaults to 2.

```bash
/botsee generate-personas type-uuid-123
/botsee generate-personas type-uuid-123 3
```

**Cost:** 5 credits per persona

#### `/botsee update-persona <uuid> [--name NAME] [--description DESC]`
Update a persona.

```bash
/botsee update-persona persona-uuid-456 --name "Sarah Chen (CMO)"
/botsee update-persona persona-uuid-456 --description "Chief Marketing Officer"
```

#### `/botsee archive-persona <uuid>`
Archive a persona.

```bash
/botsee archive-persona persona-uuid-456
```

---

### Questions Management

#### `/botsee list-questions [persona_uuid]`
List questions. Show all or filter by persona.

```bash
/botsee list-questions
/botsee list-questions persona-uuid-456
```

#### `/botsee get-question <uuid>`
View details of a specific question.

```bash
/botsee get-question question-uuid-789
```

#### `/botsee create-question <persona_uuid> <question_text>`
Create a new question manually.

```bash
/botsee create-question persona-uuid-456 "What are the best email marketing tools?"
```

#### `/botsee generate-questions <persona_uuid> [count]`
Generate questions for a persona using AI. Defaults to 5.

```bash
/botsee generate-questions persona-uuid-456
/botsee generate-questions persona-uuid-456 10
```

**Cost:** 10 credits per generation call (not per question)

#### `/botsee update-question <uuid> <question_text>`
Update a question's text.

```bash
/botsee update-question question-uuid-789 "What are the best affordable email marketing tools?"
```

#### `/botsee delete-question <uuid>`
Delete a question permanently.

```bash
/botsee delete-question question-uuid-789
```

---

### Results Commands

#### `/botsee results-competitors`
View competitor analysis results from the latest analysis.

```bash
/botsee results-competitors
```

#### `/botsee results-keywords`
View keyword analysis results from the latest analysis.

```bash
/botsee results-keywords
```

#### `/botsee results-sources`
View source analysis results (which websites cited your site/competitors).

```bash
/botsee results-sources
```

#### `/botsee results-responses`
View all raw AI responses from the latest analysis.

```bash
/botsee results-responses
```

#### `/botsee results-keyword-opportunities <analysis_uuid>`
Questions where your brand is missing or ranks poorly, with per-provider breakdown showing mention rates, rank positions, and exact keywords each AI used.

```bash
/botsee results-keyword-opportunities <analysis_uuid>
/botsee results-keyword-opportunities <analysis_uuid> --threshold 0.8
/botsee results-keyword-opportunities <analysis_uuid> --rank-threshold 3
```

- `--threshold` (0.0–1.0, default 1.0): include questions where brand mention rate is below this value
- `--rank-threshold` (integer): also flag questions where brand appeared but at a rank worse than this

#### `/botsee results-source-opportunities <analysis_uuid>`
Sources AI cited in responses where your brand was NOT mentioned — ideal targets for content and link-building.

```bash
/botsee results-source-opportunities <analysis_uuid>
```

## Full CRUD Operations

BotSee skill provides complete CRUD (Create, Read, Update, Delete) operations for all resources:

**Sites:** List, view, create, and archive sites
**Customer Types:** List, view, create, generate (AI), update, and archive types
**Personas:** List, view, create, generate (AI), update, and archive personas
**Questions:** List, view, create, generate (AI), update, and delete questions

You can:
- Use the high-level `/botsee setup` command for automatic setup
- Or manually build your structure using individual CRUD commands
- View and edit any resource at any time
- Generate additional resources as needed
- Customize your analysis by adding/removing questions

## Configuration

**Workspace Config** (`.context/botsee-config.json`):
Saved by `/botsee create-site`, used by `/botsee setup`:
```json
{
  "domain": "https://example.com",
  "types": 2,
  "personas_per_type": 2,
  "questions_per_persona": 5
}
```

**User Config** (`~/.botsee/config.json`):
Saved by `/botsee setup` with secure permissions (600):
```json
{
  "api_key": "bts_live_...",
  "site_uuid": "..."
}
```

## Example Workflows

### New User Setup
```bash
/botsee setup https://www.example.com

# Output:
🤖 BotSee Setup

📋 Complete signup to get your API key:

   https://botsee.io/setup/abc123...

⏳ Waiting for signup completion...
✅ Signup complete!

Using: 2 types, 2 personas/type, 5 questions/persona

⏳ Creating site: https://www.example.com
✅ Site created: abc-def-123

⏳ Generating 2 customer type(s)...
📋 Customer Types:
  • Small Business Owners
  • Marketing Managers

⏳ Generating personas (2 per type)...
  ✓ Small Business Owners: 2 persona(s)
  ✓ Marketing Managers: 2 persona(s)
✅ Generated 4 persona(s)

⏳ Generating questions (5 per persona)...
✅ Generated 20 question(s)

✅ Setup complete!

Generated:
  • 2 customer type(s)
  • 4 persona(s)
  • 20 question(s)

💰 Remaining: 925 credits

Next: /botsee analyze
```

### Custom Setup
```bash
/botsee create-site https://www.example.com --types 3 --personas 3 --questions 10
/botsee config-show
/botsee setup https://www.example.com --api-key bts_live_abc123...
```

### Run Analysis and Generate Content
```bash
/botsee analyze
/botsee content
```

### View and Edit Personas
```bash
# List all personas
/botsee list-personas

# View specific persona
/botsee get-persona persona-uuid-456

# Update persona description
/botsee update-persona persona-uuid-456 --description "Chief Marketing Officer at enterprise SaaS"

# List questions for this persona
/botsee list-questions persona-uuid-456

# Add a new question
/botsee create-question persona-uuid-456 "What are the best alternatives to HubSpot?"
```

### Manage Customer Types
```bash
# List all customer types
/botsee list-types

# Add a new customer type manually
/botsee create-type "Startup Founders" "Early-stage founders bootstrapping their companies"

# Generate personas for the new type
/botsee generate-personas type-uuid-new 3

# Generate questions for each persona
/botsee list-personas type-uuid-new
/botsee generate-questions persona-uuid-1 10
/botsee generate-questions persona-uuid-2 10
/botsee generate-questions persona-uuid-3 10
```

### View Results
```bash
# After running analysis, view different result types
/botsee results-competitors
/botsee results-keywords
/botsee results-sources
/botsee results-responses
```


## Configuration Management

### Config Files

**User Config** (`~/.botsee/config.json`)
- **Purpose:** Stores API key and site UUID
- **Permissions:** 0o600 (owner read/write only)
- **Created by:** `/botsee setup` command
- **Contents:**
  ```json
  {
    "api_key": "bts_live_...",
    "site_uuid": "abc-def-123"
  }
  ```

**Workspace Config** (`.context/botsee-config.json`)
- **Purpose:** Stores generation defaults (types/personas/questions)
- **Permissions:** Standard file permissions
- **Created by:** `/botsee create-site` command (optional)
- **Contents:**
  ```json
  {
    "domain": "https://example.com",
    "types": 2,
    "personas_per_type": 2,
    "questions_per_persona": 5
  }
  ```

### Managing Configs

**View current configuration:**
```bash
/botsee                    # Show status + API key suffix
/botsee config-show        # Show workspace config
```

**Edit configuration:**
```bash
# Workspace config (generation counts)
/botsee create-site <domain> --types 3 --personas 3 --questions 10

# User config (API key + site)
/botsee setup <domain> --api-key <new_key>
```

**Manual editing:**
- User config: Edit `~/.botsee/config.json` (must maintain 0o600 permissions)
- Workspace config: Edit `.context/botsee-config.json`

**Reset configuration:**
```bash
rm ~/.botsee/config.json        # Remove user config
rm .context/botsee-config.json  # Remove workspace config
/botsee setup <domain>          # Start fresh
```

---

## Troubleshooting

### Authentication Issues

**"Invalid API key"**
- **Cause:** API key expired or incorrect
- **Solution:** Run `/botsee setup <domain>` to create new account or use `--api-key` with valid key
- **Check:** API key should start with `bts_live_` or `bts_test_`

**"No BotSee config found"**
- **Cause:** Missing `~/.botsee/config.json` file
- **Solution:** Run `/botsee setup <domain>` to initialize configuration

### Credit Issues

**"Insufficient credits"**
- **Cause:** Account balance too low
- **Solution:** Use `/botsee topup-usdc --amount-cents 250 --from-address 0x...` or add credits at https://botsee.io/billing
- **Check:** Run `/botsee` to view current balance

**Analysis uses more credits than expected**
- **Cause:** More questions generated than planned
- **Check:** Run `/botsee list-questions` to count total questions
- **Solution:** Reduce question count or delete unnecessary questions

**"HTTP 402 Payment required"**
- **Cause:** Endpoint requires x402 payment proof or account has insufficient credits
- **Solution:** Top up with `/botsee topup-usdc ...` and retry
- **Optional:** Retry USDC payment endpoints with `--payment <proof>` to send x402 `payment` header

### Connection Issues

**"Connection error"**
- **Cause:** Network connectivity or API downtime
- **Solution:**
  - Check internet connection
  - Verify https://botsee.io is accessible
  - API calls timeout after 30 seconds - retry for transient errors

**"SSL certificate verification failed"**
- **Cause:** Corporate proxy or outdated CA certificates
- **Solution:** Update system certificates or check proxy settings

### Setup Issues

**Signup times out**
- **Cause:** Didn't complete browser signup within 5 minutes
- **Solution:** Run `/botsee setup <domain>` again to get new signup URL

**"Site creation failed"**
- **Cause:** Invalid domain format or duplicate site
- **Solution:**
  - Ensure domain starts with `https://`
  - Check `/botsee list-sites` for existing sites
  - Domain may already be registered to another account

### Analysis Issues

**Analysis takes too long**
- **Normal:** Analysis can take 5-10 minutes depending on question count
- **Timeout:** Commands timeout after 10 minutes
- **Solution:** Reduce number of questions if analysis consistently times out

**"No analysis found"**
- **Cause:** Haven't run `/botsee analyze` yet
- **Solution:** Run analysis first, then generate content

**Missing analysis UUID**
- **Cause:** Analysis UUID not captured from analyze command output
- **Where to find:** Look for line `📊 Analysis started: abc-def-123`
- **Solution:** Re-run `/botsee analyze` and copy the UUID from output

## Credits & Costs

**Credit rate:** 1 credit = $0.01 USD | **Minimum purchase:** $20 (2,000 credits) | All CRUD operations are free

### Setup (one-time with defaults)
- Site creation: **5 credits**
- Generate 2 customer types: **10 credits** (5 each)
- Generate 4 personas: **20 credits** (5 each)
- Generate questions (4 calls): **40 credits** (10 per call, not per question)
- **Total:** ~75 credits

### Individual Operations

**Sites:**
- **Create site:** 5 credits (auto-generates product_name/value_proposition)

**Customer Types:**
- **Create customer type (manual):** 5 credits
- **Generate customer types (AI):** 5 credits **per type** generated

**Personas:**
- **Create persona (manual):** 5 credits
- **Generate personas (AI):** 5 credits **per persona** generated

**Questions:**
- **Create question (manual):** Free
- **Generate questions (AI):** 10 credits **per API call**
  - Each call generates multiple questions (default: 5)
  - Cost is per generation call, **not** per question
  - Example: Generating 5 questions = 10 credits (one call)
  - Example: Generating 10 questions for 4 personas = 40 credits (4 calls, one per persona)

**Analysis & Content:**
- **Analysis (per run):** ~660 credits (varies by question count and AI models used)
- **Content generation:** 15 credits

### Credit Cost Clarification

**"Per type" vs "Per call":**
- **Per type/persona:** Each individual resource costs credits
  - Generate 3 types = 15 credits (3 × 5)
  - Generate 4 personas = 20 credits (4 × 5)

- **Per call (questions only):** Cost is for the API call, not individual questions
  - One call generates multiple questions (you specify count: 3-10)
  - Cost: 10 credits regardless of how many questions generated in that call
  - Setup calls generate-questions once per persona, so 4 personas = 40 credits (4 calls)

### Example Workflows
- **First complete workflow** (setup + analysis + content): ~750 credits
- **Add new customer type with 3 personas (10 questions each):**
  - Create type: 5 credits
  - Generate 3 personas: 15 credits
  - Generate questions (3 calls): 30 credits
  - **Total:** 50 credits

## License

MIT License - see LICENSE file

## Support

- Documentation: https://botsee.io/docs
- Issues: https://github.com/rivalsee/botsee-skill/issues
