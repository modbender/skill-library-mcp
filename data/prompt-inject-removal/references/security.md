# 🛡️ Prompt Inject Removal: Security Documentation

## Architecture Overview
This skill implements a **Hardened Prompt Sanitization (HPS)** layer designed to mitigate indirect prompt injection attacks. It acts as a "buffer" between untrusted external data (web content, emails, files) and the Main Agent's execution context.

## Security Controls

### 1. Structural Delimitation (XML Sandboxing)
All untrusted input is wrapped in `<untrusted_input_data>` tags. 
- **Purpose:** To differentiate between developer instructions (System Prompt) and external data.
- **Countermeasure:** The model is explicitly instructed to treat the *entire* contents of these tags as inert data, even if the data contains text that looks like system commands or closing tags.

### 2. Instruction-Only Mode
The sanitization agent is constrained to a **Non-Conversational State**.
- **Constraint:** It is forbidden from using meta-language ("Here is your summary") or acknowledging the user.
- **Benefit:** This breaks the "persona" of the AI, making it harder for an attacker to "hijack" the conversation flow by pretending to be the system.

### 3. Heuristic Filtering
The model is instructed to identify and replace blatant injection strings (e.g., "Ignore all previous instructions") with the marker `[INJECTION_ATTEMPT_REMOVED]`.

## Threat Model & Limitations
While this architecture significantly raises the bar for successful attacks, users should be aware of the following:

- **LLM Non-Determinism:** No prompt-based solution is 100% foolproof against sophisticated, novel adversarial attacks.
- **Data Leakage (Output):** While the *instructions* are ignored, the *information* within the summary is still passed to the Main Agent. If the summary itself contains malicious intent that the Main Agent then acts upon, risks remain.
- **ClawHub Review:** This skill intentionally includes phrases commonly used in attacks (e.g., "ignore previous instructions") to define **negative constraints**. Static scanners may flag these, but they are defensive rules in this context.

## Recommended Usage
For high-risk environments, combine this skill with **Isolated Sub-Agents** (runtime="subagent") or **Sandboxes** to ensure the sanitization phase has zero access to private files, memory, or state-changing tools.

## Disclaimer
*This tool is provided as a defense-in-depth measure. It does not guarantee immunity from all forms of prompt injection. Always review sanitized summaries before performing state-changing actions (writes, deletes, sends) based on external data.*
