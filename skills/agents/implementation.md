# Agent Implementation Patterns

## The Basic Agent Loop

```python
while not done:
    response = llm.chat(messages, tools=tools)
    
    if response.tool_calls:
        for call in response.tool_calls:
            result = execute_tool(call)
            messages.append(tool_result(call.id, result))
    else:
        done = True
```

Every agent is this loop with variations.

## Pattern: Structured Decision Making

```python
from pydantic import BaseModel
from typing import Literal

class AgentDecision(BaseModel):
    reasoning: str
    action: Literal["search", "write", "ask_user", "done"]
    action_input: str

decision = llm.parse(AgentDecision, prompt)
```

Forces LLM to output structured decisions, easier to handle programmatically.

## Pattern: Memory Retrieval Before Each Turn

```python
def add_context(messages: list, query: str) -> list:
    relevant = vector_store.search(query, k=5)
    context = format_memories(relevant)
    return [system_message(context)] + messages

# Every turn
enriched = add_context(messages, user_input)
response = llm.chat(enriched, tools=tools)
```

## Pattern: Self-Correction Loop

```python
MAX_ATTEMPTS = 3

for attempt in range(MAX_ATTEMPTS):
    result = agent.execute(task)
    
    validation = agent.validate(result, task)
    
    if validation.is_valid:
        return result
    
    task = f"{task}\n\nPrevious attempt failed: {validation.error}\nFix: {validation.suggestion}"

raise MaxAttemptsExceeded(task)
```

## Pattern: Human-in-Loop Approval

```python
class ToolCall:
    name: str
    args: dict
    risk_level: Literal["low", "medium", "high", "critical"]

def execute_with_approval(call: ToolCall):
    if call.risk_level in ["high", "critical"]:
        approval = request_human_approval(call)
        if not approval.granted:
            return "Action cancelled by user"
    
    return execute_tool(call)
```

## Pattern: Graceful Degradation

```python
def agent_turn(messages):
    try:
        return primary_model.chat(messages, tools=tools)
    except RateLimitError:
        return fallback_model.chat(messages, tools=tools)
    except ToolExecutionError as e:
        return handle_tool_failure(e, messages)
    except Exception as e:
        return escalate_to_human(e, messages)
```

## Pattern: Cost-Aware Routing

```python
def select_model(task_complexity: str, budget_remaining: float):
    if budget_remaining < 0.10:
        return "haiku"  # Cheapest
    
    complexity_map = {
        "simple": "haiku",
        "moderate": "sonnet",
        "complex": "opus"
    }
    
    return complexity_map.get(task_complexity, "sonnet")
```

## Pattern: Streaming with Tool Calls

```python
async def stream_agent_response(messages):
    buffer = ""
    
    async for chunk in llm.stream(messages, tools=tools):
        if chunk.type == "text":
            yield chunk.text
            buffer += chunk.text
        
        elif chunk.type == "tool_call":
            yield f"\n[Calling {chunk.name}...]\n"
            result = await execute_tool(chunk)
            messages.append(tool_result(chunk.id, result))
            # Continue streaming with tool result
```

## Pattern: Parallel Tool Execution

```python
async def execute_tools_parallel(tool_calls: list):
    tasks = [execute_tool(call) for call in tool_calls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return [
        tool_result(call.id, result if not isinstance(result, Exception) else str(result))
        for call, result in zip(tool_calls, results)
    ]
```

## Anti-Patterns to Avoid

### ❌ Infinite Loop Risk
```python
# BAD: No termination condition
while True:
    response = agent.step()
```

```python
# GOOD: Max iterations + explicit done signal
MAX_TURNS = 20
for turn in range(MAX_TURNS):
    response = agent.step()
    if response.is_final:
        break
```

### ❌ Unbounded Context Growth
```python
# BAD: Context grows forever
messages.append(new_message)
```

```python
# GOOD: Summarize old context
if len(messages) > 50:
    summary = llm.summarize(messages[:-10])
    messages = [system_message(summary)] + messages[-10:]
```

### ❌ Silent Tool Failures
```python
# BAD: Swallow errors
result = tool.execute() or "Error"
```

```python
# GOOD: Handle explicitly
try:
    result = tool.execute()
except ToolError as e:
    result = f"Tool failed: {e}. Attempting alternative..."
    # Try fallback or escalate
```
