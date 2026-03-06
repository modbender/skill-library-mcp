# ClickUp Ticket Manager

**CLI tool: `clup`**

A CLI tool for quickly creating ClickUp tasks with **basic quality standards**.

Prevents "open firewall" tickets without any context and enforces meaningful descriptions.

## Features

✅ **JSON Output:** Clean JSON response for easy parsing  
✅ **Smart Defaults:** Configurable tag, "BACKLOG" status  
✅ **Priority Mapping:** urgent, high, normal, low  
✅ **Simple CLI:** Only title + description required  
✅ **Direct Links:** Get ClickUp task URL immediately

## Installation

**Prerequisites:** ClickUp API Key and List ID

```bash
# Make script executable
cd clickup-ticket-manager
chmod +x clup.sh

# Set ENV variables
echo 'export CLICKUP_API_KEY="pk_your_api_key_here"' >> ~/.zshrc
echo 'export CLICKUP_DEFAULT_LIST_ID="your_list_id_here"' >> ~/.zshrc

# Optional: Change default status (default is BACKLOG)
echo 'export CLICKUP_DEFAULT_STATUS="to do"' >> ~/.zshrc

# Optional: Change default tags (comma-separated list, default is "automated")
echo 'export CLICKUP_DEFAULT_TAG="bot-created,automated"' >> ~/.zshrc

source ~/.zshrc

# Now you can run it:
./clup.sh --title "Test" --description "Testing the tool"

# Optional: Add to PATH for system-wide access
sudo ln -s "$(pwd)/clup.sh" /usr/local/bin/clup
# Then you can use: clup --title "..." --description "..."
```

### Getting ClickUp API Key

1. Go to **ClickUp Settings** → **Apps**
2. Click **Generate** under "API Token"
3. Copy the token (starts with `pk_`)

### Finding List ID

1. Open your ClickUp list in browser
2. URL looks like: `https://app.clickup.com/123456/v/li/901234567`
3. Numbers after `/li/` are your List ID (`901234567`)

## Usage

### Basic Syntax

```bash
./clup.sh --title "Title" --description "Description"

# Or if you created a symlink:
clup --title "Title" --description "Description"
```

### Examples

**Standard Ticket:**
```bash
./clup.sh --title "Firewall Rule for Server XY" \
     --description "Open port 443 from web-01 (10.0.1.5) to db-prod (10.0.2.10). Required for API communication after migration. Coordination with network team needed."
```

**High Priority:**
```bash
./clup.sh --title "Login not working" \
     --description "Login page returns 500 error since 2:30 PM. All users affected. Likely caused by last deployment." \
     --priority high
```

**Urgent (Production Down):**
```bash
./clup.sh --title "Database offline" \
     --description "Production database db-prod not responding. All services offline since 3:45 PM. Immediate action required!" \
     --priority urgent
```

**Low Priority (Nice-to-Have):**
```bash
./clup.sh --title "Improve Dashboard UI" \
     --description "Calendar widget could be larger for better readability. User feedback from meeting. Not a blocker, more of an enhancement." \
     --priority low
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--title` | ✅ Yes | Short, clear title |
| `--description` | ✅ Yes | Description with context (min 2-3 sentences!) |
| `--priority` | No | `urgent`, `high`, `normal`, `low` |
| `--status` | No | Status (default: "BACKLOG") |
| `--help` | - | Show help |

### Auto-set Values

- **Tags:** `automated` (default, changeable via `CLICKUP_DEFAULT_TAG`, comma-separated)
- **Status:** `BACKLOG` (default, changeable via `CLICKUP_DEFAULT_STATUS`)
- **Priority:** Not set (ClickUp uses its default unless you specify `--priority`)

## Output

### Success:

```json
{"status":"ok","ticket_id":"abc123xyz","url":"https://app.clickup.com/t/abc123xyz"}
```

### Error:

```json
{"status":"error","http_code":400,"message":"Failed to create ticket"}
```

## Troubleshooting

### "CLICKUP_API_KEY environment variable not set"

Set the ENV variable:
```bash
export CLICKUP_API_KEY="pk_xxx..."
```

Or permanently in `.zshrc`/`.bashrc`:
```bash
echo 'export CLICKUP_API_KEY="pk_xxx..."' >> ~/.zshrc
source ~/.zshrc
```

### "CLICKUP_DEFAULT_LIST_ID environment variable not set"

Find your List ID in the ClickUp URL and set it:
```bash
export CLICKUP_DEFAULT_LIST_ID="123456789"
```

### "Failed to create task (HTTP 401)"

- API Key is invalid or expired
- Generate a new one in ClickUp Settings → Apps

### "Failed to create task (HTTP 404)"

- List ID is wrong
- Check your list URL and copy the ID after `/li/`

### "Invalid priority"

- Only these values allowed: `urgent`, `high`, `normal`, `low`
- Case-insensitive

## Integration with AI Agents

**Workflow:**

1. User → "Create a ticket: open firewall"
2. AI Agent:
   - Asks for details if needed
   - Creates good description (2-3 sentences)
   - Executes `clup` command
3. User gets ClickUp link back

**For agent integration:** Include `SKILL.md` in your agent's context to ensure quality ticket creation.

## Technical Details

- **API:** ClickUp REST API v2
- **Auth:** Bearer Token (API Key)
- **Output:** JSON
- **Dependencies:** `curl`, `bash` (standard on macOS/Linux)

## Pro Tips

💡 **Set aliases:**
```bash
alias ticket='clup'
alias bug='clup --priority high'
```

💡 **Template scripts:**
```bash
# bug.sh
#!/bin/bash
clup --title "$1" --description "$2" --priority high
```

💡 **Use with agent:**
Just say "Create ticket for..." and let the agent ensure quality!

## Roadmap (Ideas for later)

- [ ] Import multiple tickets from JSON/CSV
- [ ] Support custom fields
- [ ] Set assignees
- [ ] Due dates
- [ ] Load templates
- [ ] Jira/Refined integration

---

**ClickUp Ticket Manager** • A simple CLI tool for creating quality tickets
