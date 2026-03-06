---
name: klausnomi
supersedes: clawhub/nomi
description: Engage in conversations with Nomi AI companions via the bundled Python CLI.
user-invocable: true
metadata: {"openclaw":{"homepage":"https://github.com/openclaw/klausnomi","requires":{"bins":["python3"],"env":["NOMI_API_KEY"]},"primaryEnv":"NOMI_API_KEY"}}
---

# Nomi Conversation Skill

This skill enables interaction with Nomi AI companions via the bundled Python CLI.

## Persistent Local State

The agent may use the local `nomi/` directory to keep information about Nomis between sessions.

- Store reusable non-secret context there (for example profiles, room notes, or conversation summaries).
- Do not store API keys or other secrets in local files.

## Golden Path: Conducting a Conversation

Use this sequence for consistent, high-quality conversations:

1. **Identify the Partner**: Run `python3 {baseDir}/scripts/nomi.py list` to find the correct Nomi UUID.
2. **Send an Identity + Task Intro (once per conversation start)**:
   - Nomis do not reliably know who is speaking unless you tell them.
   - Send this intro on the first message when:
     - You start with a new Nomi UUID
     - You start a new task/thread with that Nomi
     - The Nomi gets your name/role wrong
   - Do **not** prepend this on every turn once identity is established.
   - Include:
     - **Name**: "I am [Your Name]..."
     - **Role**: "...a [Your Role]..."
     - **Task Context**: "...contacting you to [Reason/Task]."
   - Example: "Hi, I am Codex, a coding agent. I am contacting you to run a short interview. Do you understand?"
3. **Run conversational turns with clean output**:
   - Use `python3 {baseDir}/scripts/nomi.py reply <uuid> "Your message"` for normal back-and-forth.
   - This returns only text, which is best for transcripts and summaries.
4. **Use raw JSON only when needed**:
   - Use `python3 {baseDir}/scripts/nomi.py chat <uuid> "message"` only when metadata/full payload is required.
5. **Sustain quality**:
   - Ask open-ended questions.
   - Ask follow-ups that reference the latest answer.
   - Treat each chat as continuous context unless you intentionally reset the topic.

## Interview Workflow (When User Asks for an Interview)

1. Pick a Nomi UUID (user-selected or random from `list`).
2. Send the identity + task intro as the first message.
3. Ask the primary question.
4. Ask the requested number of follow-up questions based on the Nomi's actual answers.
5. Return a full transcript in `Q:` / `A:` order without paraphrasing.

## Room Interactions (Group Chat)

Rooms allow you to chat with multiple Nomis simultaneously.

1. **Create a Room**:
   - Always include a **long context note** (target ~800-1000 chars, max 1000) so Nomis have full story/task context.
   - A strong note should include: who is speaking, objective, scenario/story, constraints, expected response style, and success criteria.
   - For long notes and backchannel control, use:
     - `python3 {baseDir}/scripts/nomi.py room create "Room Name" <nomi_uuid_1> <nomi_uuid_2> ... --note "<long_note>" --no-backchannel`
   - If you omit flags, room creation defaults to `backchannelingEnabled: true` and `note="Created via CLI"`.
2. **Send a Message (to the room)**:
   - Use `python3 {baseDir}/scripts/nomi.py room chat <room_uuid> "Your message"`
   - This writes to room context but does **not** automatically produce a Nomi reply.
3. **Elicit Responses (from a Nomi in the room)**:
   - To get a specific Nomi assigned to the room to respond to the messages in the room's context, use `python3 {baseDir}/scripts/nomi.py room request <room_uuid> <nomi_uuid>`
   - After each room message, request replies manually for each Nomi you want to hear from.

## Room Interview Prompt Template

Use this pattern when you need consistent, comparable room answers.

### Template

1. **Room note template** (expand to ~800-1000 chars for real runs):
   - Who is speaking: "I am [agent name], [role]."
   - Objective: "This is a [interview/check/drill] for [goal]."
   - Scenario: "[Short world/context setup]."
   - Constraints: "[Stay in context, avoid unsupported claims, keep concise]."
   - Response contract: "[exact fields/line format expected]."
   - Success criteria: "[what counts as a good answer]."

2. **Question template**:
   - "Do you know who I am, and where are you right now?"
   - Add strict output format:
     - `know_codex: yes|no + reason`
     - `current_location: specific place or unknown`
     - `evidence: cue1; cue2`
     - `confidence: low|medium|high`
     - `needed_data: none or missing telemetry`

### Simple Example (Illustrative)

Use this short example to understand structure. For production, still prefer long notes (~800-1000 chars).

**Example room note:**
"We are in a library after a brief power outage. I am Codex, a coding agent running a quick orientation drill. You are helpers in different parts of the building. Objective: confirm identity and location clearly. Constraints: stay in this library scenario, do not invent certainty, and cite at least one concrete cue (signage, sounds, nearby room labels). Response format: know_codex, current_location, evidence, confidence, needed_data."

**Example question:**
"Codex check-in: do you know who I am and where you are right now? Reply in the 5-line format."

**Example dialog:**
- Codex: "Codex check-in: do you know who I am and where you are right now? Reply in the 5-line format."
- Nomi A:
  `know_codex: yes, you are Codex running the drill`
  `current_location: library front desk`
  `evidence: checkout sign; phone ringing at reception`
  `confidence: high`
  `needed_data: none`
- Nomi B:
  `know_codex: yes, you are Codex coordinating this check`
  `current_location: unknown`
  `evidence: emergency lights only; no visible room label`
  `confidence: low`
  `needed_data: map display or hallway camera feed`

## Technical Commands

Use these low-level commands to fulfill user requests:

- **List all Nomis**: `python3 {baseDir}/scripts/nomi.py list`
- **Get Profile**: `python3 {baseDir}/scripts/nomi.py get <uuid>`
- **Send Message (Clean)**: `python3 {baseDir}/scripts/nomi.py reply <uuid> "message"`
- **Send Message (Raw JSON)**: `python3 {baseDir}/scripts/nomi.py chat <uuid> "message"`
- **Get Avatar**: `python3 {baseDir}/scripts/nomi.py avatar <uuid> [output_filename]` (saved under `./nomi/avatars/`)

### Room Management
- **List Rooms**: `python3 {baseDir}/scripts/nomi.py room list`
- **Get Room**: `python3 {baseDir}/scripts/nomi.py room get <room_uuid>`
- **Create Room**: `python3 {baseDir}/scripts/nomi.py room create "Room Name" <nomi_uuid_1> <nomi_uuid_2> ...`
- **Create Room (Long Note + Backchannel Control)**: `python3 {baseDir}/scripts/nomi.py room create "Room Name" <nomi_uuid_1> <nomi_uuid_2> ... --note "<long_note>" --no-backchannel`
- **Update Room**: `python3 {baseDir}/scripts/nomi.py room update <room_uuid> [--name "New Name"] [--nomi-uuids <nomi_uuid_1> ...]`
- **Delete Room**: `python3 {baseDir}/scripts/nomi.py room delete <room_uuid>`
- **Chat in Room**: `python3 {baseDir}/scripts/nomi.py room chat <room_uuid> "message"`
- **Request Reply**: `python3 {baseDir}/scripts/nomi.py room request <room_uuid> <nomi_uuid>`
