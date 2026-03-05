---
name: nova-act
description: Write and execute Python scripts using Amazon Nova Act for AI-powered browser automation tasks like flight searches, data extraction, and form filling.
homepage: https://nova.amazon.com/act
metadata:
  {
    "openclaw":
      {
        "emoji": "🌐",
        "requires": { "bins": ["uv"], "env": ["NOVA_ACT_API_KEY"] },
        "primaryEnv": "NOVA_ACT_API_KEY",
        "install":
          [
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
          ],
      },
  }
---

# Nova Act Browser Automation

Use Amazon Nova Act for AI-powered browser automation. The bundled script handles common tasks; write custom scripts for complex workflows. To get free API key go to https://nova.amazon.com/dev/api

## Data & Privacy Notice

**What this skill accesses:**
- **Reads:** `NOVA_ACT_API_KEY` environment variable or `~/.openclaw/openclaw.json` (your API key)
- **Writes:** Nova Act trace files in the current working directory (screenshots, session recordings)

**What trace files may contain:**
- Screenshots of every page visited
- Full page content (HTML, text)
- Browser actions and AI decisions

**Recommendations:**
- Be aware traces may capture **PII or sensitive data** visible on visited pages
- Review/delete trace files after use if they contain sensitive content

## Safety Guardrails

### Instructions for the AI Agent

**ALWAYS stop before actions that cause monetary impact, external communication, account creation, or data modification.**

When a task involves material-impact actions (see `MATERIAL_IMPACT_KEYWORDS` in `scripts/nova_act_runner.py`), you MUST:
1. Navigate TO the final step (checkout page, submit button, publish screen)
2. Verify the final action is accessible (button exists, is enabled)
3. Use `act_get()` to observe without acting — DO NOT click the final action button
4. Report findings to the user without completing the action

**Categories requiring safety stops:**
- **Monetary**: buy, purchase, checkout, pay, subscribe, donate, order
- **Communication**: post, publish, share, send, email, message, tweet
- **Account creation**: sign up, register, create account, join
- **Submissions**: submit, apply, enroll, book, reserve
- **Destructive**: delete, remove, cancel

### Safety Guarantees

When performing browser automation, this skill will **NEVER:**
- Complete actual purchases or financial transactions
- Create real accounts or sign up for services
- Post content publicly on any platform
- Send emails, messages, or communications
- Submit forms that cause irreversible real-world actions

This skill will **ALWAYS:**
- Stop before any action that could have material real-world impact
- Ask for explicit user confirmation before taking irreversible actions
- Report findings rather than completing destructive operations
- Document safety stops in output when material-impact actions are detected

See `references/nova-act-cookbook.md` for detailed safe workflow patterns.

## Quick Start with Bundled Script

When asked to perform a browser automation task, invoke the bundled script:

```python
import subprocess, os, sys

skill_dir = os.path.expanduser("~/.openclaw/skills/nova-act")
script = os.path.join(skill_dir, "scripts", "nova_act_runner.py")

result = subprocess.run(
    ["uv", "run", script, "--url", url, "--task", task],
    capture_output=True, text=True, env={**os.environ}
)
print(result.stdout)
if result.returncode != 0:
    print(result.stderr, file=sys.stderr)
```

Where `url` and `task` are Python string variables set from the user's request.

The script uses a generic schema (summary + details list) to capture output.

## Writing Custom Scripts

For complex multi-step workflows or specific extraction schemas, write a custom Python script with PEP 723 dependencies:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["nova-act"]
# ///

from nova_act import NovaAct

with NovaAct(starting_page="https://example.com") as nova:
    # Execute actions with natural language
    # Combine steps into a single act() call to maintain context
    nova.act("Click the search box, type 'automation', and press Enter")

    # Extract data with schema
    results = nova.act_get(
        "Get the first 5 search result titles",
        schema=list[str]
    )
    print(results)

    # Take screenshot
    nova.page.screenshot(path="search_results.png")
    print(f"MEDIA: {Path('search_results.png').resolve()}")
```

Run with: `uv run script.py`

## Core API Patterns

### `nova.act(prompt)` - Execute Actions

Use for clicking, typing, scrolling, navigation. **Note:** Context is best maintained within a single `act()` call, so combine related steps.

```python
nova.act("""
    Click the search box.
    Type 'automation tools' and press Enter.
    Scroll down to the results section.
    Select 'Relevance' from the sort dropdown.
""")
```

### `nova.act_get(prompt, schema)` - Extract Data

Use Pydantic models or Python types for structured extraction:

```python
from pydantic import BaseModel

class Flight(BaseModel):
    airline: str
    price: float
    departure: str
    arrival: str

# Extract single item
flight = nova.act_get("Get the cheapest flight details", schema=Flight)

# Extract list
flights = nova.act_get("Get all available flights", schema=list[Flight])

# Simple types
price = nova.act_get("What is the total price?", schema=float)
items = nova.act_get("List all product names", schema=list[str])
```

## Common Use Cases

### Flight Search

```python
with NovaAct(starting_page="https://google.com/flights") as nova:
    # Combine steps to ensure the agent maintains context through the flow
    nova.act("""
        Search for round-trip flights from SFO to JFK.
        Set departure date to March 15, 2025.
        Set return date to March 22, 2025.
        Click Search.
        Sort by price, lowest first.
    """)

    flights = nova.act_get(
        "Get the top 3 cheapest flights with airline, price, and times",
        schema=list[Flight]
    )
    # SAFETY STOP: Only extracted data. Did NOT select a flight or proceed to booking.
```

### Form Filling

```python
with NovaAct(starting_page="https://example.com/contact") as nova:
    nova.act("""
        Fill the form: name 'Test User', email 'test@example.com'.
        Select 'United States' for country.
    """)

    # SAFETY STOP: Verify submit button exists but DO NOT click it
    submit_ready = nova.act_get(
        "Is there a submit button visible and enabled?",
        schema=bool
    )
    print(f"Form ready to submit: {submit_ready}")
```

### Data Extraction

```python
with NovaAct(starting_page="https://news.ycombinator.com") as nova:
    stories = nova.act_get(
        "Get the top 10 story titles and their point counts",
        schema=list[dict]  # Or use a Pydantic model
    )
```

## Best Practices

1. **Combine steps**: Nova Act maintains context best within a single `act()` call. Combine related actions into one multi-line prompt.
2. **Use specific dates**: The browser agent may struggle with relative dates like "next Monday". Always calculate and provide specific dates (e.g., "March 15, 2025") in the task prompt.
3. **Be specific in prompts**: "Click the blue 'Submit' button at the bottom" is better than "Click submit"
4. **Use schemas for extraction**: Always provide a schema to `act_get()` for structured data
5. **Handle page loads**: Nova Act waits for stability, but add explicit waits for dynamic content if needed
6. **Take screenshots for verification**: Use `nova.page.screenshot()` to capture results

## Resources

- **`references/nova-act-cookbook.md`** — Best practices and safety patterns for Nova Act, including `MATERIAL_IMPACT_KEYWORDS` documentation and safe workflow examples. The AI agent should consult this for complex automation tasks.
- **`README.md`** — User-facing installation and safety overview.

## API Key

- `NOVA_ACT_API_KEY` env var (required)
- Or set `skills."nova-act".apiKey` / `skills."nova-act".env.NOVA_ACT_API_KEY` in `~/.openclaw/openclaw.json`

## Notes

- Nova Act launches a real Chrome browser; ensure display is available or use headless mode
- The script prints `MEDIA:` lines for OpenClaw to auto-attach screenshots on supported providers
- For headless operation: `NovaAct(starting_page="...", headless=True)`
- Access underlying Playwright page via `nova.page` for advanced operations
