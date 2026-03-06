# Callbacks in CX Agent Studio

Callbacks let you hook into an agent's execution process using Python code to observe, customize, and control behavior at specific points.

## Callback Types
1. **`before_agent_callback(callback_context)`**:
   - Called before the agent is invoked.
   - Purpose: Setup resources, validate session state, avoid agent invocation.
   - Return: `Optional[Content]`. If set, agent is skipped.

2. **`after_agent_callback(callback_context)`**:
   - Called after the agent completes.
   - Purpose: Cleanup tasks, post-execution validation, modify final state.
   - Return: `Optional[Content]`. If set, replaces agent output.

3. **`before_model_callback(callback_context, llm_request)`**:
   - Called before model request.
   - Purpose: Inspect/modify the model request, prompt validation, caching.
   - Return: `Optional[LlmResponse]`. If set, model call is skipped.

4. **`after_model_callback(callback_context, llm_response)`**:
   - Called after a model response is received.
   - Purpose: Reformat responses, censor sensitive info, parse structured data to variables, handle errors.
   - Return: `Optional[LlmResponse]`. If set, replaces model response.

5. **`before_tool_callback(tool, input, callback_context)`**:
   - Called before tool calls.
   - Purpose: Inspect/modify tool arguments, auth checks, tool caching.
   - Return: `Optional[dict[str, Any]]`. If set, tool execution is skipped and dict is returned to the model.

6. **`after_tool_callback(tool, input, callback_context, tool_response)`**:
   - Called after tool completion.
   - Purpose: Post-processing tool results, save parts to variables.
   - Return: `Optional[dict[str, Any]]`. If set, overrides the tool response provided to the model.

## Custom Payloads (`custom_payloads`)
Used for supplementary non-textual data (JSON) within an agent's response to interact with external systems/clients (escalation, rich content widgets, routing).
- Set using `before_model_callback` or `after_model_callback`.
- Value is not visible to the LLM.
- Used as a `Blob` with mime_type `application/json`.
- `Part.from_json(data=payload_string)`