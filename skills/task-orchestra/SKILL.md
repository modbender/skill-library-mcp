---
name: task-orchestra
version: "1.0.0"
description: "Coordinate multiple agents and tasks for complex workflows. Orchestrate subagents, manage dependencies, handle parallel execution, and ensure successful completion of multi-step operations.\n"
metadata:
  openclaw:
    emoji: "🎚️"
    requires:
      bins: ["curl", "jq"]
      env: ["BRAVE_API_KEY"]
    install:
      - id: npm
        kind: node
        package: async
        bins: ["async"]
---

# Task Orchestra

Coordinate multiple agents and tasks for complex workflows.

## When to Use
- Multi-step operations requiring coordination
- Parallel execution of independent tasks
- Complex workflows with dependencies
- Orchestrating subagents for large projects

## Core Capabilities

### 1. Task Coordination
- Break down complex tasks into manageable steps
- Manage dependencies between tasks
- Coordinate parallel execution
- Handle task sequencing and scheduling

### 2. Agent Orchestration
- Spawn and manage multiple subagents
- Route tasks to appropriate agents
- Monitor progress and handle failures
- Aggregate results from multiple sources

### 3. Workflow Management
- Define workflow patterns and templates
- Implement error handling and recovery
- Manage state and progress tracking
- Coordinate handoffs between agents

### 4. Dependency Resolution
- Analyze task dependencies
- Create execution order
- Handle conditional execution
- Manage resource conflicts

## Orchestration Patterns

### 1. Sequential Execution
```
Task A → Task B → Task C
```

### 2. Parallel Execution
```
Task A, Task B, Task C → Aggregate
```

### 3. Pipeline Processing
```
Input → Task A → Task B → Task C → Output
```

### 4. Supervisor Pattern
```
Coordinator → Multiple Subagents → Results
```

### 5. Event-Driven Processing
```
Event → Trigger → Response → Next Event
```

## Quick Actions

- `orchestrate [workflow]` - Execute complex workflow
- `parallel [tasks]` - Run tasks in parallel
- `pipeline [steps]` - Chain tasks in sequence
- `supervise [agents]` - Manage multiple agents
- `dependencies [tasks]` - Analyze and resolve dependencies

## Usage Examples

```
"Orchestrate a complete research project with multiple agents"
"Run these tasks in parallel and combine results"
"Create a pipeline for content creation from research to publication"
"Supervise a team of agents working on different aspects"
"Analyze dependencies and create execution order"
```

## Workflow Templates

### Research Project
```
1. Research Topic → Research Agent
2. Data Collection → Data Agent
3. Analysis → Analysis Agent
4. Report Generation → Writing Agent
5. Review → QA Agent
```

### Content Creation
```
1. Topic Research → Research Agent
2. Outline Creation → Writing Agent
3. Draft Writing → Writing Agent
4. Editing → Editing Agent
5. Publication → Publishing Agent
```

### Software Development
```
1. Requirements → Analysis Agent
2. Design → Design Agent
3. Implementation → Coding Agent
4. Testing → QA Agent
5. Deployment → Deployment Agent
```

## Agent Management

### Spawning Agents
```
sessions_spawn({ task: "specific task", label: "agent-name", mode: "run" })
```

### Monitoring Progress
```
subagents list
```

### Handling Failures
```
subagents kill [agent-id]
subagents steer [agent-id] "new instructions"
```

## Dependency Resolution

### Types of Dependencies
- **Data Dependencies**: Task B needs output from Task A
- **Resource Dependencies**: Tasks sharing same resources
- **Order Dependencies**: Tasks must run in specific order
- **Conditional Dependencies**: Task runs only if condition met

### Resolution Process
```
1. Identify all dependencies
2. Create dependency graph
3. Find topological sort
4. Execute in dependency order
5. Handle conflicts and cycles
```

## Error Handling

### Common Failure Scenarios
- **Agent Failure**: Subagent crashes or times out
- **Dependency Failure**: Required task fails
- **Resource Conflict**: Multiple agents need same resource
- **Network Issues**: API calls fail or timeout

### Recovery Strategies
- **Retry**: Attempt failed task again
- **Alternative**: Use different approach or agent
- **Skip**: Continue without failed task
- **Rollback**: Undo previous steps

## State Management

### Progress Tracking
- Track completed tasks
- Monitor current execution
- Record task results
- Maintain workflow state

### Checkpointing
- Save progress at key points
- Enable restart from checkpoints
- Maintain consistency across failures

## Communication Patterns

### Parent → Child
```
/sessions_send [agent-id] "instructions"
```

### Child → Parent
```
Auto-announce results
Reply with findings
Report errors and status
```

### Agent → Agent
```
Share data through files
Coordinate via shared state
Trigger other agents
```

## Performance Optimization

### Parallel Execution
- Identify independent tasks
- Run in parallel when possible
- Aggregate results efficiently

### Resource Management
- Monitor agent resource usage
- Balance load across agents
- Avoid resource conflicts

### Efficiency Metrics
- Task completion time
- Resource utilization
- Error rates
- Success rates

## Safety Considerations

### Agent Limits
- Max 10 concurrent subagents
- Max 2 levels of nesting
- 10-minute timeout per agent
- Automatic cleanup

### Data Integrity
- Validate task inputs/outputs
- Maintain consistency
- Handle partial failures
- Ensure atomic operations

## Advanced Patterns

### 1. Hierarchical Orchestration
```
Main Coordinator → Team Coordinators → Individual Agents
```

### 2. Dynamic Work Allocation
```
Assign tasks based on agent capabilities
Reassign if agent fails
Balance load dynamically
```

### 3. Event-Driven Workflows
```
Event → Trigger → Agent → Result → Next Event
```

### 4. Adaptive Planning
```
Plan → Execute → Monitor → Adjust → Repeat
```

## Integration with Other Skills

### Self-Evolution
- Use for complex self-improvement tasks
- Coordinate multiple evolution agents
- Manage long-term capability building

### Analysis Skills
- Orchestrate research projects
- Coordinate data analysis
- Manage multi-step investigations

### Content Creation
- Coordinate content production pipelines
- Manage multi-agent content creation
- Orchestrate publication workflows

## Quick Reference

### Common Commands
```bash
# List running agents
subagents list

# Kill failed agent
subagents kill [id]

# Send instructions
sessions_send [agent-id] "message"

# Spawn new agent
sessions_spawn({ task: "task", label: "name", mode: "run" })
```

### Workflow Examples
```bash
# Research project
orchestrate "research-project" with agents: research, analysis, writing

# Content pipeline
pipeline "content-creation" with steps: research, outline, draft, edit, publish

# Software development
supervise "dev-team" with agents: analysis, design, coding, testing, deployment
```

## Best Practices

1. **Start Simple**: Begin with sequential execution
2. **Add Parallelism**: Identify independent tasks
3. **Handle Failures**: Implement robust error handling
4. **Monitor Progress**: Track execution and results
5. **Optimize Performance**: Balance load and resources

## Success Metrics

- Task completion rate
- Execution time efficiency
- Resource utilization
- Error recovery effectiveness
- Overall workflow success

---

**Remember**: Good orchestration makes complex tasks manageable and reliable.