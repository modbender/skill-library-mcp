# Remote Action Execution

Detailed guidance on discovering and executing methods on remote actors.

## Overview

ActingWeb's actor model enables invoking methods on remote actors — robots, services, other AI assistants, or any connected device. Connections that offer actions can be services, physical devices, or other AI assistants (e.g., ChatGPT, other Claude instances) that have established a trust relationship with the user.

## Workflow

The typical workflow is: `list_connections()` → `describe_method()` → `execute_method()`

Always check the method's parameter schema before executing to ensure you pass the correct arguments.

## Discover Available Methods

```
list_connections()
# Returns: {peer_id: 'abc123', displayname: 'Neo Robot', methods: [{name: 'pack_items', description: '...'}]}
```

## Get Method Parameters

```
describe_method(peer_id="abc123", method_name="pack_items")
# Returns: {input_schema: {properties: {items: {type: 'array'}}, required: ['items']}}
```

## Execute a Method

```
execute_method(method_name="pack_items", peer_id="abc123", parameters={"items": ["clothes", "laptop"]})
```

## Best Practices

- Always call `describe_method()` before `execute_method()` to understand required and optional parameters
- Remote actions may have side effects (e.g., controlling a physical device), so confirm with the user before executing unfamiliar methods
- A connection may offer remote actions, share memories, or both — `list_connections()` shows everything
