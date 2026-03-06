# Workflow Patterns

## Pattern 1: Simple Automation

Single prompt with resource embedding.

```yaml
name: simple-task
steps:
  - name: execute
    prompt: task-prompt
    resources:
      - file://data/{input}.md
```

## Pattern 2: Prompt Chain

Sequential multi-step workflow.

```yaml
name: chained-workflow
steps:
  - name: plan
    prompt: planner
    output: plan_result
    
  - name: generate
    prompt: generator
    input: "{plan_result}"
    
  - name: execute
    action: execute-task
    input: "{generated_content}"
```

## Pattern 3: Dynamic Branching

Conditional paths based on input.

```yaml
name: smart-processor
steps:
  - name: analyze
    action: analyze-input
    
branches:
  - condition: "{type} == 'api'"
    steps:
      - name: generate-api-docs
        action: api-doc-generator
        
  - condition: "{type} == 'component'"
    steps:
      - name: generate-component-docs
        action: component-doc-generator
        
  - default:
    steps:
      - name: generate-general-docs
        action: general-doc-generator
```

## Pattern 4: Parallel Execution

Multiple steps running concurrently.

```yaml
name: parallel-analysis
steps:
  - parallel:
      - name: analyze-code
        action: code-analyzer
        
      - name: analyze-tests
        action: test-analyzer
        
      - name: analyze-deps
        action: dependency-analyzer
        
  - name: merge-results
    action: result-merger
    input: "{parallel_results}"
```

## Pattern 5: Cross-Server Workflow

Multiple MCP servers collaborating.

```yaml
name: multi-server-pipeline
servers:
  - name: builder
    command: mcp-builder-server
    
  - name: tester
    command: mcp-tester-server
    
  - name: deployer
    command: mcp-deploy-server

steps:
  - name: build
    server: builder
    action: compile
    
  - name: test
    server: tester
    action: run-tests
    
  - name: deploy
    server: deployer
    action: release
```

## Pattern 6: Human-in-the-Loop

Pause for human approval.

```yaml
name: approval-workflow
steps:
  - name: generate-proposal
    prompt: proposal-generator
    
  - name: await-approval
    type: human-input
    message: "Please review and approve the proposal"
    
  - name: execute-approved
    condition: "{approval} == true"
    action: execute-proposal
```

## Pattern 7: Error Recovery

Graceful error handling.

```yaml
name: resilient-workflow
steps:
  - name: primary-action
    action: main-task
    on_error:
      - name: fallback-1
        action: alternative-1
        on_error:
          - name: fallback-2
            action: alternative-2
            on_error:
              - name: notify-failure
                action: send-alert
```

## Pattern 8: Iterative Refinement

Loop until condition met.

```yaml
name: iterative-improvement
steps:
  - name: initial-draft
    prompt: draft-generator
    
  - loop:
      max_iterations: 5
      condition: "{quality_score} < 0.9"
      steps:
        - name: evaluate
          action: quality-check
          
        - name: refine
          prompt: refinement
          input: "{draft}"
          output: draft
```

## Pattern 9: Scheduled Execution

Time-based triggers.

```yaml
name: scheduled-report
triggers:
  schedule: "0 9 * * 1"  # Mondays at 9am
  
steps:
  - name: collect-data
    action: gather-metrics
    
  - name: generate-report
    prompt: report-generator
    
  - name: distribute
    action: send-email
```

## Pattern 10: Event-Driven

React to external events.

```yaml
name: event-handler
triggers:
  webhook:
    path: /github/pr
    method: POST
    
steps:
  - name: parse-event
    action: extract-pr-data
    
  - name: analyze-changes
    action: diff-analyzer
    
  - name: post-comment
    action: github-comment
```

## Best Practices

1. **Idempotency**: Steps should be safe to retry
2. **Observability**: Log all step executions
3. **Timeouts**: Set reasonable timeouts per step
4. **Retry Logic**: Implement exponential backoff
5. **Circuit Breakers**: Fail fast on repeated errors
6. **Resource Cleanup**: Clean up temp resources
7. **Input Validation**: Validate all inputs early
8. **Output Contracts**: Define clear output schemas
