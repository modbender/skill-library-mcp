# CX Agent Studio Evaluation Reference

Evaluation helps automate testing, catch regressions, and measure agent quality via test cases.

## Test Case Types

### 1. Scenario Test Cases
- Uses AI to simulate various user conversations based on a high-level **user goal** (e.g., "Securely book a specific room at a chosen hotel").
- Helps explore edge cases without manually writing conversational paths.
- Can be saved as **Golden Conversations** once they work well.
- **Scenario Expectations**:
  - Message expected from end-user or agent.
  - Tool call with expected inputs/outputs.
  - Conditions: Must have, Must not have, After tool call, Variable value.

### 2. Golden Test Cases
- Defines specific, ideal conversation paths for **regression testing**.
- Evaluates if the agent's behavior and tool calls match this ideal path.
- Created via: Simulator, Conversation history, from Scratch, Simulated Scenario, or CSV Batch Upload.
- **Golden Expectations**:
  - Message: Text response from agent matching the expectation semantically.
  - Tool Call: Agent calling a specific tool and response (with input args).
  - Agent Handoff: Conversation transfer to human or another bot.

## Evaluation Metrics

Metrics calculate the agent's performance.

| Metric | Type | Description |
| --- | --- | --- |
| **Tool Correctness** | Golden/Scenario | Percentage of expected parameters matched. Unexpected calls fail the golden test but don't impact this score. |
| **User Goal Satisfaction** | Scenario | Binary metric (0=no, 1=yes). Measures if simulated user believes goals were achieved based on `user_goal` and transcript. |
| **Hallucinations** | Golden/Scenario | Identifies claims not justified by context (variables, history, tools, instructions). Only computed for turns with tool calls. |
| **Semantic Match** | Golden | Measures how well observed agent utterance matches expected utterance (0=contradictory to 4=consistent). |
| **Scenario Expectations** | Scenario | Satisfactory behavior (0=no, 1=yes). Includes tool call and agent response expectations. |
| **Task Completion** | Scenario | Jointly measures user goal achievement and correct agent behavior. |

## AI Issue Discovery

When running 3 or more evaluations, enable **Find issues with AI** to generate a downloadable `loss_report`. You can interact with the helper agent via "Ask Gemini" to explain problems and suggest fixes.

## Personas

Simulated user personas customize scenario tests (e.g., adding age, location, or motivations) to ensure the agent interacts appropriately with expected human users during runtime. Created under "Persona management" and used by selecting the persona during an evaluation run.