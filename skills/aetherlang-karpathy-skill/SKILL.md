---
name: aetherlang-karpathy-upgrades
description: Implement 10 advanced AI agent node types for any DSL/runtime system — plan compiler, code interpreter, critique loops, intelligent routing, multi-agent ensemble, persistent memory, external API tools, iterative loops, data transforms, and parallel execution. Use this skill whenever the user wants to add agent capabilities to a workflow engine, build an AI orchestration framework, implement Karpathy-style AI upgrades, add new node types to a DSL runtime, or create autonomous agent pipelines. Also trigger when the user mentions AetherLang, flow engines, node types, agent frameworks, or wants to upgrade their AI system with capabilities like self-programming, reflection, routing, ensemble, memory, or tool use.
---

# AetherLang Karpathy Agent Upgrades

A battle-tested skill for implementing 10 advanced AI agent node types that transform any simple LLM pipeline into a full autonomous AI agent framework. Based on Andrej Karpathy's vision of AI systems that think, compute, reflect, and act autonomously.

Built and validated in production on the AetherLang Omega platform (neurodoc.app), these upgrades have been tested with real API calls, Docker deployments, and live traffic.

## The 10 Karpathy Upgrades

| # | Node Type | Capability | What It Does |
|---|-----------|-----------|--------------|
| 1 | `plan` | Self-Programming | LLM generates sub-flows dynamically, then runtime compiles and executes them |
| 2 | `code_interpreter` | Real Computation | Sandboxed Python execution with safe imports, no more hallucinated math |
| 3 | `critique` | Self-Improvement | Evaluates output quality (0-10), retries up to 3x with feedback until threshold met |
| 4 | `router` | Intelligent Branching | LLM picks optimal processing path, skips unselected routes (10x speedup) |
| 5 | `ensemble` | Multi-Agent Synthesis | Runs multiple AI personas in parallel, synthesizes superior combined response |
| 6 | `memory` | Persistent State | Store/recall/search data across executions with namespace isolation |
| 7 | `tool` | External API Access | Call any REST API (GET/POST/PUT/DELETE) with security limits |
| 8 | `loop` | Iterative Execution | Repeat any node over multiple items with collect or chain modes |
| 9 | `transform` | Data Reshaping | Template, extract, format, or LLM-powered data transformation between nodes |
| 10 | `parallel` | Concurrent Execution | Run multiple nodes simultaneously (3 API calls in 0.2s instead of 3s) |

## Architecture Pattern

Every upgrade follows the same 3-step implementation pattern. This is universal and works for any Python-based DSL runtime.

### Step 1: Parser — Add Node Type to Enum
```python
class NodeType(Enum):
    LLM = "llm"
    # ... existing types ...
    PLAN = "plan"
    CODE_INTERPRETER = "code_interpreter"
    CRITIQUE = "critique"
    ROUTER = "router"
    ENSEMBLE = "ensemble"
    MEMORY = "memory"
    TOOL = "tool"
    LOOP = "loop"
    TRANSFORM = "transform"
    PARALLEL = "parallel"
```

### Step 2: Runtime Dispatch — Route to Handler
Add an `elif` branch in the main node execution dispatcher:
```python
async def _execute_node(self, ctx, node):
    if node.node_type == NodeType.LLM:
        result = await self._execute_llm(ctx, node, data)
    elif node.node_type == NodeType.PLAN:
        result = await self._execute_plan(ctx, node, data)
    elif node.node_type == NodeType.CODE_INTERPRETER:
        result = await self._execute_code_interpreter(ctx, node, data)
    # ... etc for all 10 types
```

### Step 3: Runtime Method — Implement Logic
Add the `async def _execute_<type>()` method to the runtime class.

**CRITICAL WARNING**: In Python, if a method name appears twice in a class, the LAST definition silently wins. Always check for and remove old stubs before inserting new methods:
```bash
grep -c "async def _execute_plan" runtime.py  # Must be exactly 1
```

## Implementation Order and Dependencies

Implement in this order due to dependencies:

1. **PLAN** — No dependencies, foundational self-programming
2. **CODE_INTERPRETER** — No dependencies, standalone sandboxed execution
3. **CRITIQUE** — Uses `_execute_node()` for retries, needs existing node execution
4. **ROUTER** — Uses `_execute_node()` for selected routes, needs skip logic in main loop
5. **ENSEMBLE** — Uses `asyncio.gather()` for parallel agent execution
6. **MEMORY** — File-based JSON persistence, fully independent
7. **TOOL** — Needs HTTP client (httpx preferred over aiohttp in Docker)
8. **LOOP** — Uses `_execute_node()` for iterating target nodes
9. **TRANSFORM** — Independent, JSON parsing and LLM reformatting
10. **PARALLEL** — Uses `asyncio.gather()`, needs skip logic like ROUTER

---

## Upgrade #1: PLAN — Self-Programming Compiler

The PLAN node lets the AI write its own processing pipeline dynamically.

**Parameters**:
- `steps` (int): Number of sub-steps to generate, default 3

**How It Works**:
1. Send query to LLM asking it to break the task into N sequential steps
2. LLM returns JSON: `[{"step": 1, "action": "description", "type": "llm|code|search"}]`
3. For each step, create a temporary node and execute it
4. Collect all step results and combine into final response

**System Prompt for Plan Generation**:
```
Break this task into exactly {steps} sequential steps.
Return ONLY a JSON array: [{"step": 1, "action": "what to do", "type": "llm"}]
Valid types: llm (text generation), code (calculation), search (information lookup)
```

**Implementation**:
```python
async def _execute_plan(self, ctx, node, data):
    query = data["inputs"].get("query", "")
    steps = int(node.params.get("steps", "3"))
    
    # 1. Generate plan via LLM
    plan_response = await self.openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": plan_system_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.3
    )
    plan = json.loads(plan_response.choices[0].message.content)
    
    # 2. Execute each step
    results = []
    for step in plan:
        step_result = await self._execute_plan_step(ctx, step, query, results)
        results.append(step_result)
    
    # 3. Combine results
    combined = "\n\n".join([f"Step {r['step']}: {r['result']}" for r in results])
    return {"response": combined, "plan_steps": plan, "node_type": "plan"}
```

---

## Upgrade #2: CODE_INTERPRETER — Sandboxed Python

Executes real Python code for accurate calculations instead of LLM hallucinations.

**Safety Configuration**:
```python
FORBIDDEN_OPERATIONS = ['__import__', 'exec', 'eval', 'compile', 'open',
                        'subprocess', 'os', 'sys', 'socket', 'shutil']
ALLOWED_IMPORTS = {'math': math, 'statistics': statistics}
SAFE_BUILTINS = {'abs': abs, 'round': round, 'min': min, 'max': max,
                 'sum': sum, 'len': len, 'range': range, 'int': int,
                 'float': float, 'str': str, 'bool': bool, 'list': list,
                 'dict': dict, 'print': print, 'isinstance': isinstance}
CODE_TIMEOUT = 5  # seconds
```

**Implementation**:
```python
async def _execute_code_interpreter(self, ctx, node, data):
    query = data["inputs"].get("query", "")
    
    # 1. LLM generates code
    code_response = await self.openai_client.chat.completions.create(
        model=node.params.get("model", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": "Write Python code. Set variable `result` at the end. ONLY code, no markdown."},
            {"role": "user", "content": query}
        ],
        temperature=0.2
    )
    code = code_response.choices[0].message.content.strip()
    code = code.replace("```python", "").replace("```", "").strip()
    
    # 2. Security check
    for forbidden in FORBIDDEN_OPERATIONS:
        if forbidden in code:
            return {"response": f"Blocked: {forbidden}", "node_type": "code_interpreter"}
    
    # 3. Sandboxed execution
    safe_globals = {"__builtins__": SAFE_BUILTINS, "math": math, "statistics": statistics}
    local_vars = {}
    
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(exec, code, safe_globals, local_vars)
        future.result(timeout=CODE_TIMEOUT)
    
    result = local_vars.get("result", "No result variable set")
    return {"response": str(result), "code": code, "node_type": "code_interpreter"}
```

---

## Upgrade #3: CRITIQUE — Self-Improvement Loop

Evaluates output quality and retries with feedback until quality threshold is met.

**Parameters**:
- `threshold` (float): Minimum score 0-10, default 7
- `max_retries` (int): Max attempts, capped at hard limit of 3
- `criteria` (str): Evaluation criteria, default "accuracy, completeness, clarity"

**Implementation Logic**:
```
1. Get upstream output
2. For each attempt (0 to max_retries):
   a. Send output + criteria to evaluator LLM
   b. Parse: {score: 8.5, passed: true, feedback: "...", strengths: "..."}
   c. If score >= threshold → PASS, return output
   d. If max retries hit → return best attempt
   e. Else → re-execute source node with enhanced query containing feedback
```

**Enhanced Query Format for Retries**:
```
[Original query]

[IMPROVEMENT FEEDBACK - attempt 2/3]:
Score: 5.5/10 (need 7.0/10)
Issues: Missing specific examples
Keep: Good structure and flow
Please improve your response addressing the feedback above.
```

---

## Upgrade #4: ROUTER — Intelligent Branching

LLM analyzes query and selects the optimal downstream node to execute, skipping all others.

**Parameters**:
- `routes` (str): Comma-separated "alias:description" pairs
- `strategy` (str): "single" or "multi", default "single"

**Critical Skip Logic** (required for performance — 10x speedup):

Two parts must be implemented:

**Part 1 — Main execution loop check**:
```python
for node_alias in execution_order:
    if node_alias in ctx.node_outputs:
        ctx.log("SYSTEM", "INFO", f"Skip {node_alias} (already executed)")
        continue
    # ... execute node normally
```

**Part 2 — Router marks unselected routes**:
```python
# After executing selected route(s):
for route_alias in route_map:
    if route_alias not in selected:
        ctx.node_outputs[route_alias] = {"skipped_by_router": True, "response": ""}
```

**Result**: Query "What is 15% tip on $85.50?" routes to calculator node in 2.3s instead of executing all 3 routes in 21s.

---

## Upgrade #5: ENSEMBLE — Mixture of Agents

Runs the same query through multiple AI personas in parallel, then synthesizes the best elements into a superior response.

**Parameters**:
- `agents` (str): Comma-separated "alias:persona" pairs
- `synthesize` (str): "true" (default) or "false" to return all
- `model` (str): Agent model, default "gpt-4o-mini"
- `synth_model` (str): Synthesizer model

**Safety**: MAX_ENSEMBLE_AGENTS = 7

**Implementation Pattern**:
```python
async def _execute_ensemble(self, ctx, node, data):
    # 1. Parse agents
    agents = parse_agents(node.params.get("agents", ""))
    
    # 2. Run ALL agents in parallel
    async def run_agent(alias, persona):
        response = await self.openai_client.chat.completions.create(
            model=agent_model,
            messages=[
                {"role": "system", "content": f"You are: {persona}. Respond from YOUR unique perspective."},
                {"role": "user", "content": query}
            ],
            temperature=0.8  # High for diversity
        )
        return {"alias": alias, "response": response.choices[0].message.content}
    
    results = await asyncio.gather(*[run_agent(a, p) for a, p in agents])
    
    # 3. Synthesize
    synthesis = await self.openai_client.chat.completions.create(
        model=synth_model,
        messages=[{"role": "user", "content": f"Combine best insights from: {results}"}],
        temperature=0.5
    )
    return {"response": synthesis.choices[0].message.content, "node_type": "ensemble"}
```

**Real Test**: Moussaka recipe with French Chef + Greek Grandmother + Molecular Scientist = superior unified recipe.

---

## Upgrade #6: MEMORY — Persistent State

File-based JSON storage for data that persists across flow executions.

**Parameters**:
- `namespace` (str): Memory bucket, default "default"
- `action` (str): "store", "recall", "search", "clear", "auto"
- `key` (str): Storage key, or LLM auto-extracts one
- `ttl` (str): Hours until expiry, "0" = forever

**Storage Format** (`memory_store/{namespace}.json`):
```json
{
  "diet": {
    "value": "I am vegan and allergic to nuts",
    "_ts": 1708502400.0,
    "_query": "I am vegan and allergic to nuts"
  }
}
```

**Actions**:
- `store` — Save upstream response or query with key
- `recall` — Return specific key or all entries as context
- `search` — LLM semantic search over stored entries
- `clear` — Delete key or entire namespace
- `auto` — LLM decides whether to store or recall based on context

---

## Upgrade #7: TOOL — External API Access

Call any REST API from within a flow with safety limits.

**Parameters**:
- `url` (str): API endpoint (supports `{query}` placeholder)
- `method` (str): GET, POST, PUT, DELETE (default: GET)
- `headers` (str): JSON string of HTTP headers
- `body` (str): Request body template
- `extract` (str): Dot-notation for JSON extraction (e.g., "data.items.0.name")
- `timeout` (str): Seconds, default 10, max 30

**Safety Limits**:
```python
TOOL_BLOCKED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254", "10.", "192.168."]
TOOL_MAX_RESPONSE = 50000  # chars
TOOL_TIMEOUT = 10  # seconds, max 30
```

**Use httpx** (not aiohttp — more commonly available in Docker/FastAPI environments):
```python
async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
    resp = await client.request(method, url, headers=headers)
```

**CRITICAL PARSER FIX**: Comment regex `//.*$` strips URLs. Must add negative lookbehind:
```python
# Before: r'//.*?$|/\*.*?\*/'  — BREAKS https:// URLs
# After:  r'(?<!:)//.*?$|/\*.*?\*/'  — Protects :// protocol
```

---

## Upgrade #8: LOOP — Iterative Execution

Repeat any target node over multiple items with collect or chain modes.

**Parameters**:
- `over` (str): Pipe-separated items (e.g., "Italian|Greek|Japanese") or "count:5"
- `target` (str): Node alias to execute each iteration
- `max` (str): Safety cap, default 10, hard limit 20
- `mode` (str): "collect" (gather all) or "chain" (each feeds into next)

**IMPORTANT**: Use `|` as separator, NOT `,` — the parser splits on commas for param separation.

**Implementation**:
```python
for i, item in enumerate(items):
    iter_query = f"{query}\n\nItem ({i+1}/{len(items)}): {item}"
    
    # Clear previous output so target re-executes
    if target_alias in ctx.node_outputs:
        del ctx.node_outputs[target_alias]
    
    await self._execute_node(ctx, target_node)
    result = ctx.node_outputs.get(target_alias, {})
    results.append(result)

# Mark target as managed by loop
ctx.node_outputs[target_alias] = {"executed_by_loop": True}
```

**Real Test**: "Give me a signature dish recipe" looped over Italian|Greek|Japanese = 3 unique recipes.

---

## Upgrade #9: TRANSFORM — Smart Data Reshaping

Reshapes data between nodes in 4 modes. The "glue" that makes complex pipelines work.

**Parameters**:
- `mode` (str): "llm" (default), "template", "extract", "format"
- `template` (str): String with `{NodeAlias}` and `{NodeAlias.field.subfield}` placeholders
- `extract` (str): Dot-path for JSON extraction
- `format` (str): Output as "json", "csv", "markdown", "text"
- `instruction` (str): Custom LLM instruction (underscores become spaces)

**Mode Details**:
- **template**: `Bitcoin: {T.bitcoin.usd} USD` → `Bitcoin: 67884 USD` (2 nesting levels)
- **extract**: `data.items.0.name` navigates JSON tree
- **format**: Converts JSON arrays to CSV or markdown tables
- **llm**: LLM intelligently reformats (temp 0.3 for precision)

**Real Test**: TOOL fetches Bitcoin price JSON → TRANSFORM summarizes = "The current price of Bitcoin is $67,861 USD" in 0.9s.

---

## Upgrade #10: PARALLEL — Concurrent Execution

Run multiple independent nodes at the same time for massive speedup.

**Parameters**:
- `targets` (str): Pipe-separated node aliases (e.g., "A|B|C")
- `merge` (str): "combine" (concatenate), "best" (longest response), "json" (structured)

**Safety**: MAX_PARALLEL_TASKS = 10

**Critical Fix**: `_execute_node()` stores results in `ctx.node_outputs` but may not return them directly. Always read from context:
```python
# WRONG — result may be None:
result = await self._execute_node(ctx, target_node)

# RIGHT — always read from context:
await self._execute_node(ctx, target_node)
result = ctx.node_outputs.get(alias, {})
```

**Real Test**: 3 CoinGecko API calls (ping + BTC price + ETH price) completed in 0.2s parallel vs ~3s sequential.

---

## Common Debugging Patterns

### Problem: Duplicate Method — Old Stub Wins
**Symptom**: New method exists but old logic runs.
**Cause**: Python uses LAST definition. Old stub at line 1800 overrides new method at line 650.
**Fix**: `grep -c "async def _execute_X" runtime.py` — if > 1, delete the old one.

### Problem: URL Gets Stripped to "https:"
**Symptom**: TOOL node sends `https:` instead of `https://api.example.com`
**Cause**: Comment regex `//.*$` matches `//` in URLs.
**Fix**: `(?<!:)//.*?$` — negative lookbehind for colon.

### Problem: Nodes Run After Router Selects
**Symptom**: Router picks node B but A and C also execute (21s instead of 2.3s).
**Fix**: Add skip check in main loop + mark unselected routes in ctx.node_outputs.

### Problem: Parameters Merge Together
**Symptom**: `namespace=prefs action=store` becomes `{'namespace': 'prefs action=store'}`
**Fix**: Parser must split on space too: `elif char in (',', ' ') and not in_quotes:`

### Problem: Empty Results from Parallel/Loop
**Symptom**: Node executes (logs show success) but calling node gets empty result.
**Fix**: Read from `ctx.node_outputs.get(alias)` instead of `_execute_node()` return value.

### Problem: Module Not Found in Docker
**Symptom**: `No module named 'aiohttp'`
**Fix**: Use `httpx` (ships with FastAPI/Starlette). Check: `docker exec container python3 -c "import httpx"`

---

## Deployment Checklist
```bash
# 1. Backup before ANY changes
cp runtime.py runtime.py.backup_$(date +%Y%m%d_%H%M%S)

# 2. Add to parser enum
sed -i '/LAST_TYPE = "last"/a\    NEW_TYPE = "new_type"' parser.py

# 3. Add dispatch + method to runtime
python3 << 'PYEOF'
# ... patch script
PYEOF

# 4. Validate Python syntax
python3 -c "import ast; ast.parse(open('runtime.py').read()); print('SYNTAX OK')"
python3 -c "import ast; ast.parse(open('parser.py').read()); print('PARSER OK')"

# 5. Check for duplicates
grep -c "async def _execute_new_type" runtime.py  # MUST be 1

# 6. Build & deploy
docker compose up -d --build backend && sleep 12

# 7. Check boot
docker logs container_name 2>&1 | tail -5

# 8. Test with minimal flow
curl -s -X POST https://api.example.com/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "flow Test { ... }", "query": "test"}'

# 9. Commit
git add parser.py runtime.py
git commit -m "Upgrade N: NODE_TYPE — description"
git push origin main
```

## Testing Pattern

Every upgrade should be tested with a minimal isolated flow:
```
flow TestNodeType {
  input text query;
  node X: <node_type> <params>;
  query -> X;
  output text result from X;
}
```

Then test in combination with other nodes:
```
flow Pipeline {
  input text query;
  node T: tool url=https://api.example.com method=GET;
  node X: transform mode=llm instruction=Summarize;
  query -> T -> X;
  output text result from X;
}
```

## Safety Summary

| Node | Limit | Value |
|------|-------|-------|
| code_interpreter | Execution timeout | 5 seconds |
| code_interpreter | Forbidden ops | 10 operations blocked |
| critique | Max retries | 3 (hard cap) |
| ensemble | Max agents | 7 |
| memory | Max entry size | 5000 chars |
| tool | Response cap | 50KB |
| tool | Timeout | 10s default, 30s max |
| tool | Blocked hosts | Private IPs, localhost |
| loop | Max iterations | 20 |
| parallel | Max tasks | 10 |

## Credits

Built by Hlia (From Kitchen to Code) on the AetherLang Omega platform.
Inspired by Andrej Karpathy's AI agent architecture principles.
Production-tested at neurodoc.app with real API traffic.
