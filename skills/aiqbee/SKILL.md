---
name: aiqbee
description: Connect to your Aiqbee knowledge graph via MCP. Search, create, and link neurons across your architecture, portfolio, and digital strategy brains.
homepage: https://aiqbee.com
metadata: {"clawdbot":{"emoji":"🧠"}}
---

# Aiqbee Brain

Connect your OpenClaw assistant to your [Aiqbee](https://aiqbee.com) knowledge graph. Search, create, and link knowledge across your architecture, portfolio, and digital strategy brains through natural conversation.

## Setup

### Option 1: Direct MCP Configuration (Recommended)

Add to your `openclaw.json`:

```json
{
  "mcpServers": {
    "aiqbee": {
      "transport": "streamable-http",
      "url": "https://mcp.aiqbee.com/mcp"
    }
  }
}
```

Sign in with your Aiqbee account when prompted (OAuth 2.0, opens browser).

### Option 2: Via mcporter

If you have mcporter installed, add to `config/mcporter.json`:

```json
{
  "mcpServers": {
    "aiqbee": {
      "baseUrl": "https://mcp.aiqbee.com/mcp",
      "description": "Aiqbee knowledge graph"
    }
  }
}
```

Verify with:

```bash
mcporter list aiqbee
```

## Authentication

Aiqbee uses OAuth 2.0. On first connection, your browser will open for sign-in. No API keys or environment variables needed — just sign in with your existing Aiqbee account.

## Available Tools (12)

### Read

| Tool | Description |
|------|-------------|
| `aiqbee_search` | Search neurons in your knowledge graph |
| `aiqbee_fetch` | Get full neuron content and metadata |
| `aiqbee_get_brain_info` | Get brain metadata and statistics |
| `aiqbee_get_neuron_types` | List all neuron types with counts |
| `aiqbee_list_neurons` | Paginated neuron listing with filtering |
| `aiqbee_get_relationships` | Get incoming/outgoing relationships for a neuron |

### Write

| Tool | Description |
|------|-------------|
| `aiqbee_create_neuron` | Create a new neuron in your brain |
| `aiqbee_update_neuron` | Update an existing neuron |
| `aiqbee_delete_neuron` | Delete a neuron |
| `aiqbee_create_relationship` | Create a link between two neurons |
| `aiqbee_update_relationship` | Update an existing relationship |
| `aiqbee_delete_relationship` | Remove a relationship |

## Usage Examples

### Search your knowledge graph

"Search my brain for anything related to cloud migration"

```bash
mcporter call 'aiqbee.aiqbee_search(query: "cloud migration")'
```

### Get full neuron details

"Show me the full details of the API gateway neuron"

```bash
mcporter call 'aiqbee.aiqbee_fetch(neuron_id: "neuron-uuid-here")'
```

### Create a new neuron

First call `aiqbee_get_neuron_types()` to get valid type IDs, then create:

```bash
mcporter call 'aiqbee.aiqbee_create_neuron(
  neuron_type_id: "type-uuid-from-get-neuron-types",
  name: "gRPC for internal services",
  content: "We decided to use gRPC for all internal service-to-service communication."
)'
```

### Link neurons together

Use neuron IDs returned from search or create:

```bash
mcporter call 'aiqbee.aiqbee_create_relationship(
  source_neuron_id: "source-uuid",
  target_neuron_id: "target-uuid",
  link_description: "depends on"
)'
```

### List neuron types

"What types of knowledge are in my brain?"

```bash
mcporter call 'aiqbee.aiqbee_get_neuron_types()'
```

### Brain overview

"Give me an overview of my architecture brain"

```bash
mcporter call 'aiqbee.aiqbee_get_brain_info()'
```

## What is Aiqbee?

[Aiqbee](https://aiqbee.com) is a web-based architecture, portfolio, and digital strategy management platform. It organises knowledge as neurons connected by synapses in an interactive knowledge graph.

- **Knowledge Graphs** — Organise ideas as neurons connected by synapses
- **Architecture Management** — Document and manage enterprise architecture
- **Portfolio Management** — Track products, projects, and digital assets
- **AI-Powered Search** — Find anything across your knowledge base
- **Collaboration** — Team workspaces with role-based access

## Resources

- [Aiqbee Platform](https://app.aiqbee.com)
- [Documentation](https://app.aiqbee.com/help)
- [MCP Server](https://mcp.aiqbee.com/mcp)
- [GitHub](https://github.com/AIQBee/aiqbee-ai)
