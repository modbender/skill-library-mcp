# State Management Helpers

Python-style pseudocode for Cord tree state management.

## Initialize State

```python
def init_cord_state(goal: str, state_file: str = "cord-state.json"):
    state = {
        "goal": goal,
        "nodes": {},
        "nextId": 1,
        "created": datetime.now().isoformat(),
        "status": "running"
    }
    write_json(state_file, state)
    return state
```

## Add Node

```python
def add_node(state, type: str, goal: str, prompt: str = None, 
             blocked_by: list = None, options: list = None):
    node_id = f"#{state['nextId']}"
    state["nextId"] += 1
    
    node = {
        "type": type,  # spawn | fork | ask | serial
        "goal": goal,
        "prompt": prompt or goal,
        "status": "blocked" if blocked_by else "pending",
        "blockedBy": blocked_by or [],
        "result": None,
        "sessionKey": None,
        "created": datetime.now().isoformat()
    }
    
    if type == "ask":
        node["options"] = options
        node["status"] = "blocked" if blocked_by else "waiting"
    
    state["nodes"][node_id] = node
    return node_id
```

## Get Ready Nodes

```python
def get_ready_nodes(state) -> list:
    """Nodes with status 'blocked' whose dependencies are all complete."""
    ready = []
    for node_id, node in state["nodes"].items():
        if node["status"] != "blocked":
            continue
        
        deps_complete = all(
            state["nodes"][dep]["status"] == "complete"
            for dep in node["blockedBy"]
        )
        
        if deps_complete:
            ready.append(node_id)
    
    return ready
```

## Collect Sibling Results (for Fork)

```python
def collect_sibling_results(state, node) -> str:
    """Gather results from completed siblings for fork context injection."""
    results = []
    
    for dep_id in node["blockedBy"]:
        dep = state["nodes"][dep_id]
        if dep["status"] == "complete" and dep["result"]:
            results.append(f"[{dep_id}] {dep['goal']}:\n{dep['result']}")
    
    return "\n\n---\n\n".join(results)
```

## Dispatch Node

```python
def dispatch_node(state, node_id: str):
    node = state["nodes"][node_id]
    
    if node["type"] == "spawn":
        # Clean slate - just the prompt
        result = sessions_spawn(
            task=node["prompt"],
            label=node_id.replace("#", "node-"),
            runTimeoutSeconds=600
        )
        node["sessionKey"] = result.get("childSessionKey")
        node["status"] = "running"
    
    elif node["type"] == "fork":
        # Inject sibling context
        context = collect_sibling_results(state, node)
        full_prompt = f"""{node['prompt']}

## Context from Prior Work

{context}
"""
        result = sessions_spawn(
            task=full_prompt,
            label=node_id.replace("#", "node-"),
            runTimeoutSeconds=600
        )
        node["sessionKey"] = result.get("childSessionKey")
        node["status"] = "running"
    
    elif node["type"] == "ask":
        # Message human, await response
        question = node.get("question", node["goal"])
        options = node.get("options", [])
        
        msg = f"🤔 **Question from task tree:**\n\n{question}"
        if options:
            msg += f"\n\nOptions: {', '.join(options)}"
        
        message(action="send", message=msg)
        node["status"] = "waiting"
    
    elif node["type"] == "serial":
        # Dispatch first child, others will follow
        children = node.get("children", [])
        if children:
            first_child = children[0]
            dispatch_node(state, first_child)
```

## Update From Agent Status

```python
def update_from_agents(state):
    """Poll subagents and update node statuses."""
    agents = subagents(action="list")
    
    for node_id, node in state["nodes"].items():
        if node["status"] != "running":
            continue
        
        # Find matching agent
        agent = find_agent_by_label(agents, node_id.replace("#", "node-"))
        
        if not agent:
            continue
        
        if agent["status"] == "complete":
            # Extract result from session history
            history = sessions_history(sessionKey=node["sessionKey"])
            result = extract_final_result(history)
            
            node["status"] = "complete"
            node["result"] = result
            node["completedAt"] = datetime.now().isoformat()
        
        elif agent["status"] == "failed":
            node["status"] = "failed"
            node["error"] = agent.get("error", "Unknown error")
```

## Main Loop

```python
def run_cord_tree(goal: str, state_file: str = "cord-state.json"):
    # Initialize
    state = init_cord_state(goal, state_file)
    
    # Build initial tree (agent-specific logic here)
    # ... add_node calls based on goal analysis ...
    
    save_state(state, state_file)
    
    # Execution loop
    while True:
        # Update from running agents
        update_from_agents(state)
        
        # Check for completion
        all_complete = all(
            n["status"] in ["complete", "failed", "skipped"]
            for n in state["nodes"].values()
        )
        
        if all_complete:
            state["status"] = "complete"
            save_state(state, state_file)
            break
        
        # Dispatch ready nodes
        ready = get_ready_nodes(state)
        for node_id in ready:
            dispatch_node(state, node_id)
        
        save_state(state, state_file)
        
        # Wait before next poll
        time.sleep(30)
    
    return state
```

## Handle ASK Response

```python
def handle_ask_response(state, node_id: str, response: str):
    """Called when human responds to an ask node."""
    node = state["nodes"][node_id]
    
    if node["status"] != "waiting":
        raise Error(f"Node {node_id} is not waiting for response")
    
    node["result"] = response
    node["status"] = "complete"
    node["completedAt"] = datetime.now().isoformat()
    
    save_state(state)
```

## Visualize Tree

```python
def print_tree(state):
    """Print tree status for debugging."""
    print(f"Goal: {state['goal']}")
    print(f"Status: {state['status']}")
    print()
    
    status_icons = {
        "pending": "○",
        "blocked": "◌",
        "running": "●",
        "waiting": "?",
        "complete": "✓",
        "failed": "✗",
        "skipped": "–"
    }
    
    for node_id, node in state["nodes"].items():
        icon = status_icons.get(node["status"], "?")
        blocked = f" (blocked-by: {', '.join(node['blockedBy'])})" if node["blockedBy"] else ""
        print(f"{icon} {node_id} [{node['type']}] {node['goal']}{blocked}")
        
        if node["status"] == "complete" and node["result"]:
            # Truncate long results
            result = node["result"][:100] + "..." if len(node["result"]) > 100 else node["result"]
            print(f"    result: {result}")
```
