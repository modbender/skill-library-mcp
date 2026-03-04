# Ops MCP Server Examples

This directory contains practical examples for using the ops-mcp-server skill with accurate tool definitions and parameters.

## Available Examples

### Core Modules

- **[sops.md](sops.md)** - Execute standard operating procedures (SOPS)
- **[events.md](events.md)** - Query Kubernetes and system events using NATS subject patterns
- **[metrics.md](metrics.md)** - Query Prometheus metrics with PromQL
- **[logs.md](logs.md)** - Search and analyze logs with ES|QL and Query DSL
- **[traces.md](traces.md)** - Investigate distributed traces and performance

### Advanced Workflows

- **[incident-investigation.md](incident-investigation.md)** - Complete incident investigation workflow combining all modules

## Tool Reference

### SOPS Module (3 tools)

- `list-sops-from-ops` - List available procedures
- `list-sops-parameters-from-ops` - Get procedure parameters
- `execute-sops-from-ops` - Execute a procedure

### Events Module (2 tools)

- `list-events-from-ops` - List event types
- `get-events-from-ops` - Query events with NATS patterns

### Metrics Module (3 tools)

- `list-metrics-from-prometheus` - List available metrics
- `query-metrics-from-prometheus` - Instant PromQL query
- `query-metrics-range-from-prometheus` - Range PromQL query

### Logs Module (3 tools)

- `list-log-indices-from-elasticsearch` - List log indices
- `search-logs-from-elasticsearch` - Full-text search (Query DSL)
- `query-logs-from-elasticsearch` - Query with ES|QL

### Traces Module (4 tools)

- `get-services-from-jaeger` - List traced services
- `get-operations-from-jaeger` - List service operations
- `get-trace-from-jaeger` - Get trace by ID
- `find-traces-from-jaeger` - Search traces by criteria

## Quick Start

Each example file contains:

- **Tool Overview**: Which tools are used
- **Parameters**: Required and optional parameters
- **Examples**: Step-by-step usage examples
- **Expected Output**: What to expect
- **Troubleshooting**: Common issues and solutions
- **Best Practices**: Tips for effective usage

## Usage

### Direct mcporter Calls

Call tools directly using mcporter command line (using npx):

```bash
# List available tools
npx mcporter list ops-mcp-server

# Call a tool (use key=value format for parameters)
npx mcporter call ops-mcp-server <tool-name> param1=value1 param2=value2

# Examples
npx mcporter call ops-mcp-server list-events-from-ops
npx mcporter call ops-mcp-server list-events-from-ops search=pod page_size=20
npx mcporter call ops-mcp-server get-events-from-ops subject_pattern="ops.clusters.*.namespaces.kube-system.pods.*.events"
```

## Parameter Formats

### Time Formats

- **Unix Timestamp (ms)**: `1740672000000` - Used in events
- **RFC 3339**: `2024-01-15T10:30:00Z` - Used in traces
- **Duration String**: `5m`, `1h`, `24h`, `7d` - Used in metrics

### Query Languages

- **PromQL**: Prometheus Query Language
- **ES|QL**: Elasticsearch Query Language (ES 8.11+)
- **Query DSL**: Elasticsearch JSON query format
- **NATS Patterns**: Subject-based patterns with `*` and `>` wildcards

## Documentation Links

- [Design Document](../references/design.md) - Event format specifications
- [Main Skill](../SKILL.md) - Skill overview and setup
- [Prometheus PromQL](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Elasticsearch ES|QL](https://www.elastic.co/guide/en/elasticsearch/reference/current/esql.html)
- [Jaeger Tracing](https://www.jaegertracing.io/docs/)
- [NATS Subjects](https://docs.nats.io/nats-concepts/subjects)
