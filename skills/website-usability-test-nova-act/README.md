# Nova Act Usability Testing Skill v1.0.2

AI-orchestrated usability testing for websites using Amazon Nova Act browser automation.

## ⚠️ Prerequisites & Credentials

**This skill requires an Amazon Nova Act API key.**

| Requirement | Details |
|-------------|---------|
| **API Key** | Nova Act API key from [AWS Console](https://console.aws.amazon.com/) |
| **Config Location** | `~/.openclaw/config/nova-act.json` |
| **Format** | `{"apiKey": "your-nova-act-api-key-here"}` |

## 🔒 Data & Privacy Notice

**What this skill accesses:**
- **Reads:** `~/.openclaw/config/nova-act.json` (your API key)
- **Writes:** `./nova_act_logs/`, `./test_results_adaptive.json`, `./nova_act_usability_report.html`

**Trace files contain screenshots and full page content.** Run tests only on non-production environments. Traces may capture PII visible on tested pages.

---

## Features

🎯 **Agent-Driven Interpretation**: The script collects raw data, the AI agent (you) interprets responses and generates reports. No hardcoded regex, no extra API calls.

📊 **Three-Phase Flow**:
1. **Collect** - Script runs Nova Act, captures raw responses
2. **Interpret** - Agent reads JSON, determines goal achievement
3. **Report** - Agent generates HTML with accurate pass/fail status

## What It Does

- **Workflow Testing**: Tests complete user journeys (booking flights, checkout, posting) with safety guardrails
- **Adaptive Testing**: AI-driven browser automation that explores websites like a real user
- **Safety First**: Automatically stops before material impact (payment, posting, account creation)
- **Contextual Personas**: Analyzes your site and generates relevant user personas automatically
- **Realistic Test Cases**: Creates targeted test scenarios based on what your page actually offers (including full workflows)
- **Cookbook-Guided**: Loads best practices and safety guidelines automatically at test start
- **Comprehensive Reports**: Auto-generates HTML reports with detailed findings and session trace links

## Features

✅ **Workflow Testing** - Tests complete user journeys end-to-end (booking, checkout, posting, signup)  
✅ **Safety Guardrails** - Automatically stops before payment, posting, or account creation  
✅ **Real Browser Automation** - Actual Playwright browser control via Nova Act  
✅ **Cookbook Integration** - Loads best practices and workflow patterns automatically  
✅ **Fully Dynamic Testing** - Exploration strategies generated per website/persona (no hardcoded logic!)  
✅ **Smart Persona Generation** - Analyzes page content to create relevant user types  
✅ **Adaptive Testing** - AI tries multiple variations when element text doesn't match exactly  
✅ **Robust Error Handling** - Handles scroll loops, timeouts, and Nova Act failures gracefully  
✅ **Detailed Reporting** - Professional HTML reports with step-by-step observations  
✅ **Trace File Integration** - Links to Nova Act's HTML session recordings for replay

### Supported Workflows

**E-Commerce:**
- Product search → Add to cart → Checkout → **STOP before payment**

**Booking (Flights/Hotels):**
- Search → Select → Fill details → **STOP before booking**

**Social Media:**
- Create post → Add content → **STOP before publishing**

**Account Signup:**
- Fill registration form → **STOP before final submission**

**Form Submission:**
- Fill form fields → **STOP before submit**

### Safety Guarantees

The skill will **NEVER:**
- ❌ Complete actual purchases
- ❌ Create real accounts
- ❌ Post publicly
- ❌ Send emails/messages
- ❌ Subscribe to newsletters

The skill will **ALWAYS:**
- ✅ Test up to (but not including) final action
- ✅ Verify final button exists and is accessible
- ✅ Document safety stop in observations  

## Installation

### Step 1: Install Python packages

```bash
pip3 install nova-act pydantic playwright
```

### Step 2: Install Playwright browser

```bash
playwright install chromium
```

> **Note:** On Linux, you may also need system dependencies:
> `sudo playwright install-deps chromium`

### Step 3: Configure API key

```bash
# Create config directory and file
mkdir -p ~/.openclaw/config
cat > ~/.openclaw/config/nova-act.json << EOF
{
  "apiKey": "your-nova-act-api-key-here"
}
EOF
```

Then:
1. Get your Nova Act API key from [AWS Console](https://console.aws.amazon.com/)
2. Edit `~/.openclaw/config/nova-act.json`
3. Replace `"your-nova-act-api-key-here"` with your actual key

### Requirements

- **Python 3.8+** (Python 3.12+ recommended)
- **~300MB disk space** for Playwright browser
- **Nova Act API key** from [AWS Console](https://console.aws.amazon.com/)

## Usage

Ask your OpenClaw agent:

```
Test https://example.com for usability
Run a usability test on example.com
```

The agent will:
1. Analyze the page structure
2. Generate contextual personas
3. Create realistic test cases
4. Run adaptive browser tests
5. Auto-generate an HTML report

## Example Output

**Test Results:**
- **Tech-savvy developer**: 3/3 tasks ✅ - Found docs, playground, value proposition
- **Business decision-maker**: 1/3 tasks - Found value prop, ❌ no pricing page, ❌ getting started not implemented
- **Beginner user**: 1/3 tasks - Found value prop, ❌ no tutorials, ❌ no help/support

**Report includes:**
- Executive summary with success rates
- Detailed step-by-step observations
- Links to Nova Act HTML trace files for session replay
- Recommendations for improvements

## How It Works

### Phase 1: Data Collection (Script)
1. **Page Analysis**: Captures title, navigation, key elements
2. **Persona Generation**: Creates contextual user types based on page content
3. **Test Case Creation**: Generates realistic tasks per persona
4. **Browser Automation**: Nova Act executes simple browser commands
5. **Raw Data Capture**: Saves responses with `needs_agent_analysis: true`

### Phase 2: Agent Interpretation (You)
6. **Read JSON Results**: Load `test_results_adaptive.json`
7. **Interpret Responses**: For each step, determine if `raw_response` indicates success
8. **Set Goal Achievement**: Mark `goal_achieved: true/false` on each step
9. **Calculate Success**: Set `overall_success` based on goals achieved

### Phase 3: Report Generation (Agent)
10. **Call Report Generator**: Pass interpreted results to `generate_enhanced_report()`
11. **View Report**: HTML shows ✅ PASSED / ❌ FAILED / ⏳ PENDING

### Report Status Indicators

| Status | Meaning |
|--------|---------|
| ✅ PASSED | Agent interpreted, goals achieved |
| ❌ FAILED | Agent interpreted, goals not achieved |
| ⏳ PENDING | Awaiting agent interpretation |

### Why "Dynamic"?

Unlike traditional testing tools with hardcoded scenarios, this skill **generates the test strategy at runtime**:

- **Hardcoded approach** (old way): `if test_case == "find docs": ask "Do you see Documentation?"`
- **Dynamic approach** (this skill): AI analyzes the test case + persona + page context → generates contextual exploration steps with fallback strategies

This means the skill adapts to ANY website without requiring updates to hardcoded logic!

## Nova Act Quirks

Nova Act uses **exact text matching** - if the page says "Docs" but you ask for "Documentation", it returns FALSE. This skill handles that by:
- Trying multiple variations per test ("Documentation" → "Docs" → "API" → "Developer")
- Iterative exploration rather than rigid scripts
- Logging all attempts for debugging

## Files

- `SKILL.md` - Main skill instructions for OpenClaw agents
- `scripts/run_adaptive_test.py` - Adaptive testing engine
- `scripts/enhanced_report_generator.py` - HTML report generator with trace links
- `scripts/trace_finder.py` - Extracts trace file paths from Nova Act output
- `references/nova-act-cookbook.md` - Nova Act usage patterns and quirks
- `references/persona-examples.md` - Sample personas for different site types
- `assets/report-template.html` - HTML report template

## Contributing

Found a bug? Have an improvement? Submit a PR or open an issue on GitHub.

## License

MIT

## Credits

Built for OpenClaw by Adi using Amazon Nova Act SDK.
