---
name: external-ai-integration
description: "Leverage external AI models (ChatGPT, Claude, Hugging Face, etc.) as tools via browser automation (Chrome Relay) and optional Hugging Face API. Use when you need to augment the assistant's capabilities with external LLMs for reasoning, summarization, code generation, or other tasks without spawning isolated sub‑agents."
---

# External AI Integration Skill

This skill provides patterns for using external AI models as **tools** that the assistant can call on‑demand. It extends existing browser‑automation and API‑integration skills, enabling the assistant to:

- **Automate interactions** with ChatGPT, Claude, Gemini, or other web‑based LLMs via Chrome Relay (browser automation).
- **Call Hugging Face Inference API** for models hosted on Hugging Face Spaces (text‑generation, summarization, translation, etc.).
- **Integrate external reasoning** into the assistant's own workflow—e.g., asking ChatGPT for a second opinion, using Claude for detailed analysis, or leveraging Hugging Face for domain‑specific tasks.
- **Avoid spawning isolated sub‑agents** by treating external models as tools, keeping control and context within the main assistant session.

## When to use

- You need additional reasoning power, a different model's perspective, or a specialized model (e.g., code generation, translation) that your primary model lacks.
- The task benefits from a second opinion or parallel evaluation (e.g., reviewing code, analyzing strategy).
- You want to use a model with a larger context window, better coding ability, or specific domain knowledge (Claude, ChatGPT, Hugging Face models).
- You are asked to “integrate external AI via browser” or “use ChatGPT/Claude as a tool”.
- You need to call Hugging Face Inference API for a specific model (e.g., summarization, sentiment analysis) and incorporate the result into your response.

## Core patterns

### 1. Browser Automation (Chrome Relay) for Web‑Based LLMs

Use Chrome Relay to automate interactions with ChatGPT, Claude, Gemini, or any other web‑based LLM that requires a browser interface.

**Prerequisites:**
- Chrome Relay extension installed and a tab attached (user must click the OpenClaw Browser Relay toolbar icon).
- The target LLM website (e.g., `chatgpt.com`, `claude.ai`) already logged in (session cookies present).
- Basic familiarity with the browser automation playbook (`memory/patterns/playbooks.md` – “Browser Automation (Chrome Relay)”).

**Steps:**

1. **Attach to the Chrome Relay profile** (`profile="chrome"`).
2. **Navigate to the target LLM** (or reuse an already‑open tab).
3. **Take a snapshot** to locate the input field and send button (use `refs="aria"` for stable references).
4. **Type the prompt** into the input field and submit (click send button or press Enter).
5. **Wait for the response** (poll for a new element, detect typing indicators, or use a fixed timeout).
6. **Extract the response text** from the appropriate DOM element.
7. **Return the response** to the assistant's workflow.

**Example workflow:**

```python
# This is a conceptual example; actual implementation uses browser tool calls.
def ask_chatgpt(prompt):
    # 1. Ensure Chrome Relay is attached
    browser(action="open", profile="chrome", targetUrl="https://chatgpt.com")
    # 2. Snapshot to get references
    snap = browser(action="snapshot", refs="aria")
    # 3. Find input field (aria role="textbox") and send button
    input_ref = snap.find_element(role="textbox", name="Message")
    send_ref = snap.find_element(role="button", name="Send")
    # 4. Type prompt and click send
    browser(action="act", request={"kind":"type", "ref":input_ref, "text":prompt})
    browser(action="act", request={"kind":"click", "ref":send_ref})
    # 5. Wait for response (simplified)
    time.sleep(10)
    # 6. Snapshot again, extract response from last message bubble
    snap2 = browser(action="snapshot", refs="aria")
    response_element = snap2.find_last_message()
    return response_element.text
```

**Key considerations:**
- **Session persistence:** The attached tab must stay logged in; avoid actions that log out.
- **Rate limits:** Be aware of the LLM's rate limits and usage policies.
- **Error handling:** Detect captchas, “network error” messages, or “try again” buttons and fall back gracefully.
- **Multi‑turn conversations:** Maintain conversation context by keeping the same tab and not refreshing.

### 2. Hugging Face Inference API Integration

For models hosted on Hugging Face Spaces or the Inference API, you can call them directly via HTTP requests.

**Prerequisites:**
- Hugging Face API token (stored in 1Password or environment variable).
- Model identifier (e.g., `"gpt2"`, `"google/flan-t5-large"`, `"microsoft/DialoGPT-medium"`).
- Knowledge of the model's expected input/output format.

**Steps:**

1. **Retrieve the API token** (use 1Password skill or read from `~/.huggingface/token`).
2. **Construct the request** (URL, headers, JSON payload).
3. **Send the request** via `curl` or `exec` with `requests` Python module.
4. **Parse the response** and extract the generated text.
5. **Handle errors** (rate limits, model loading, invalid token).

**Example script (using curl):**

```bash
#!/bin/bash
set -e

MODEL="google/flan-t5-large"
PROMPT="Translate English to German: How are you?"
API_TOKEN=$(op read "op://Personal/HuggingFace/api_token")

curl -s "https://api-inference.huggingface.co/models/$MODEL" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"inputs\": \"$PROMPT\"}" | jq -r '.[0].generated_text'
```

**Example Python function (using requests):**

```python
import requests
import os

def hf_inference(model, inputs, parameters=None):
    api_token = os.getenv("HF_TOKEN")  # or retrieve via 1Password
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {api_token}"}
    payload = {"inputs": inputs}
    if parameters:
        payload.update(parameters)
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()
```

**Key considerations:**
- **Cost:** Inference API may have costs; monitor usage.
- **Model readiness:** Some models need to be loaded; include `{"options":{"wait_for_model":true}}` in parameters.
- **Output format:** Response structure varies by model; inspect with a test call first.

### 3. Orchestrating External AI as a Tool

Instead of spawning a sub‑agent, the assistant calls external AI within its own reasoning flow.

**Pattern:**

1. **Determine need:** Decide which external model is appropriate (ChatGPT for creative tasks, Claude for analysis, Hugging Face for specialized models).
2. **Prepare the prompt:** Format the prompt with clear instructions, context, and expected output format.
3. **Call the tool:** Use browser automation for web‑based LLMs or API call for Hugging Face.
4. **Integrate the result:** Parse, validate, and incorporate the external response into your own answer.
5. **Fallback:** If the external call fails, continue with your own reasoning or try an alternative.

**Example decision logic:**

```python
def external_ai_assist(task_type, prompt):
    if task_type == "code_review":
        # Use Claude via browser automation
        return ask_claude(prompt)
    elif task_type == "translation":
        # Use Hugging Face translation model
        return hf_inference("Helsinki-NLP/opus-mt-en-de", prompt)
    elif task_type == "creative_writing":
        # Use ChatGPT via browser automation
        return ask_chatgpt(prompt)
    else:
        raise ValueError(f"No external AI configured for {task_type}")
```

### 4. Prompt Engineering for External Models

External models may require different prompting styles than the assistant's native model.

- **ChatGPT/Claude:** Use conversational style, system prompts, and markdown formatting.
- **Hugging Face models:** Follow the model's expected input format (e.g., `"Translate English to German: ..."` for T5).
- **Include context:** Provide necessary background, constraints, and examples in the prompt.
- **Specify output format:** Ask for JSON, bullet points, code blocks, etc.

**Example prompt for code review:**

```
You are an expert software engineer reviewing the following code snippet. Please:
1. Identify potential bugs or security issues.
2. Suggest performance improvements.
3. Comment on code style and readability.
4. Output your review as a JSON with keys "bugs", "performance", "style".

Code:
```python
def calculate_average(numbers):
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers)
```
```

### 5. Error Handling and Fallbacks

External services can fail; plan for graceful degradation.

- **Browser automation failures:** Captchas, login required, network errors. Fallback: try Hugging Face API or continue without external help.
- **API failures:** Rate limits, model not found, token invalid. Fallback: use a different model or skip external step.
- **Timeouts:** Set reasonable timeouts (e.g., 30 seconds for browser automation, 10 seconds for API). Fallback: proceed with assistant's own reasoning.
- **Log failures:** Record external AI failures in `memory/YYYY‑MM‑DD.md` with tag `external‑ai‑failure` for later analysis.

**Example fallback structure:**

```python
try:
    response = ask_chatgpt(prompt)
except (BrowserError, TimeoutError) as e:
    log_failure("ChatGPT", e)
    # Fallback to Hugging Face
    response = hf_inference("google/flan-t5-xxl", prompt)
except Exception as e:
    log_failure("All external AI", e)
    response = None

if response:
    integrate(response)
else:
    # Continue with assistant's own reasoning
    pass
```

## Examples

### Example 1: Code Review with Claude

**Scenario:** The assistant is asked to review a complex React component. It uses Claude (via Chrome Relay) for a detailed second opinion.

**Steps:**
1. Assistant prepares a prompt with the component code and review instructions.
2. Calls `ask_claude(prompt)` using browser automation.
3. Claude returns a structured review.
4. Assistant incorporates Claude's feedback into its final answer.

### Example 2: Translation via Hugging Face

**Scenario:** User provides a paragraph in English and asks for a German translation. Assistant calls Hugging Face translation model.

**Steps:**
1. Assistant constructs prompt: `"Translate English to German: <text>"`.
2. Calls `hf_inference("Helsinki-NLP/opus-mt-en-de", prompt)`.
3. Parses the generated text.
4. Returns translation to user.

### Example 3: Creative Brainstorming with ChatGPT

**Scenario:** User needs ideas for a blog post title. Assistant uses ChatGPT to generate 10 options.

**Steps:**
1. Assistant navigates to ChatGPT tab, inputs “Generate 10 catchy blog post titles about AI assistants”.
2. Waits for response, extracts list.
3. Presents the list to user, adding its own commentary.

### Example 4: Combined Analysis (Assistant + External)

**Scenario:** User asks for a strategic analysis of a business decision. Assistant uses its own reasoning, then asks ChatGPT for potential blind spots.

**Steps:**
1. Assistant produces its own analysis.
2. Assistant prompts ChatGPT: “What are potential blind spots in the following analysis? <analysis>”
3. Integrates ChatGPT's blind‑spot list into final answer.

## Anti‑Patterns

- **Over‑reliance on external AI:** Using external models for trivial tasks increases latency and dependency. Use only when value added justifies the cost/risk.
- **Ignoring context size:** Web‑based LLMs have context limits; sending huge contexts may truncate or fail. Summarize or chunk appropriately.
- **Exposing secrets:** Never paste API tokens, passwords, or sensitive data into external AI prompts (especially web‑based). Use 1Password for tokens.
- **Assuming correctness:** External AI can be wrong, biased, or hallucinate. Always validate critical outputs.
- **Breaking conversation flow:** Browser automation that logs out or loses the tab breaks future calls. Keep session alive and avoid destructive actions.
- **Cost unawareness:** Hugging Face Inference API may incur costs; monitor usage and set budgets.
- **Neglecting fallbacks:** Not planning for external AI failure leaves the assistant stuck. Always have a fallback path.

## Related Patterns

- **Browser Automation (Chrome Relay) playbook** – detailed steps for Chrome Relay automation.
- **Hugging Face skill** – using Hugging Face Hub, Spaces, and Inference API with budget management.
- **1Password skill** – retrieving API tokens securely.
- **API‑Tool Integration skill** – general patterns for calling external APIs.
- **Error Recovery Automation skill** – handling failures in external services.
- **Health Monitoring skill** – monitoring external service availability.

## References

- `docs/browser-automation.md` – Chrome Relay setup and commands.
- `skills/huggingface/SKILL.md` – Hugging Face API usage.
- `skills/1password/SKILL.md` – retrieving secrets.
- `memory/patterns/playbooks.md` – Browser Automation playbook.
- `scripts/external_ai_integration.py` (this skill's core implementation).
- `playbooks/external-ai-integration-playbook.md` (orchestration playbook).

## Skill Integration

When a task would benefit from external AI reasoning, read this skill to decide which model to use and how to call it. Store successful patterns in `memory/patterns/tools.md`. Update `pending.md` if external AI fails repeatedly and needs manual configuration.

This skill increases autonomy by expanding the assistant's toolset with external AI models, allowing it to tackle a wider range of tasks without spawning sub‑agents and maintaining control over the workflow.