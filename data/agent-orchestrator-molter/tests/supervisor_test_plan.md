# Supervisor Pattern Test Plan

## Overview

This document outlines testing approaches for the Supervisor pattern implementation.
Python environment not yet available, so these are designed tests for future execution.

## Test Categories

### 1. Unit Tests (Component Level)

#### Worker Pool Tests
```python
# Test worker registration
def test_worker_pool_registration():
    pool = WorkerPool()
    config = WorkerConfig(role=WorkerRole.RESEARCH, name="research-1", system_prompt="...")
    pool.register_worker(config)
    assert pool.get_worker("research-1") is not None

# Test role-based worker creation
def test_worker_pool_from_roles():
    pool = WorkerPool.create_from_roles(["research", "write", "review"])
    assert len(pool.list_workers()) == 3
    assert all(w in pool.list_workers() for w in ["research-1", "write-1", "review-1"])
```

#### Task Decomposition Tests
```python
# Test sequential dependencies
def test_sequential_decomposition():
    supervisor = Supervisor(test_config)
    analysis = {"approach": "sequential", "required_workers": ["research", "write"]}
    steps = supervisor.decompose_task(analysis)
    assert len(steps) == 2
    assert steps[1].dependencies == ["step-1"]

# Test parallel decomposition
def test_parallel_decomposition():
    supervisor = Supervisor(test_config)
    analysis = {"approach": "parallel", "required_workers": ["research", "research"]}
    steps = supervisor.decompose_task(analysis)
    assert all(len(s.dependencies) == 0 for s in steps)
```

#### State Management Tests
```python
# Test dependency checking
def test_can_execute():
    supervisor = Supervisor(test_config)
    # Add completed step
    supervisor.completed_steps["step-1"] = TaskStep(
        step_id="step-1",
        status=WorkerStatus.COMPLETED
    )
    # Test step with satisfied dependencies
    step2 = TaskStep(step_id="step-2", dependencies=["step-1"])
    assert supervisor.can_execute(step2)
    # Test step with unsatisfied dependencies
    step3 = TaskStep(step_id="step-3", dependencies=["step-99"])
    assert not supervisor.can_execute(step3)
```

### 2. Integration Tests (End-to-End)

#### Happy Path Test
```bash
# Test basic research-write-review workflow
python -m agent-orchestrator supervise \
  --task "Explain Bitcoin Lightning Network to a technical audience" \
  --workers "research,write,review" \
  --verbose

# Expected: Three sequential steps, research → write (with research output) → review
```

#### Parallel Workers Test
```bash
# Test parallel research workers
python -m agent-orchestrator supervise \
  --task "Find the best Python web frameworks 2024" \
  --workers "research:3" \
  --strategy adaptive \
  --verbose

# Expected: Three parallel research workers, synthesized output
```

#### Dependency Chain Test
```bash
# Test complex dependency chain
python -m agent-orchestrator supervise \
  --task "Create a Python API with tests and documentation" \
  --workers "plan,code,test,review,write" \
  --verbose

# Expected: plan → code (with plan) → test (with code) → review (with test results) → write (with all)
```

### 3. Failure Handling Tests

#### Retry Logic Test
```bash
# Simulate failure scenario (requires mock or fault injection)
python -m agent-orchestrator supervise \
  --task "Analyze this corrupted data" \
  --workers "analyze" \
  --max-iterations 3

# Expected: Attempts retry up to max_retries configured per worker
```

#### Partial Failure Test
```bash
# Test continuing despite worker failure
python -m agent-orchestrator supervise \
  --task "Research and write report" \
  --workers "research:2,write" \
  --strategy adaptive

# Simulate: One research worker fails, other succeeds, write proceeds with available data
# Expected: Completion with note about partial research
```

#### Total Failure Test
```bash
# Test graceful handling when all workers fail
python -m agent-orchestrator supervise \
  --task "Impossible task with invalid constraints" \
  --workers "analyze" \
  --verbose

# Expected: Clean error message, no crash, partial output if any
```

### 4. Strategy Tests

#### Adaptive Strategy
```bash
# Test dynamic replanning
python -m agent-orchestrator supervise \
  --task "Create a marketing strategy" \
  --workers "research,analyze,plan,write" \
  --strategy adaptive

# Expected: Supervisor may adjust order or spawn additional analysis based on results
```

#### Fixed Strategy
```bash
# Test strict workflow adherence
python -m agent-orchestrator supervise \
  --task "Follow exact process: draft, edit, review" \
  --workers "write,review,review" \
  --strategy fixed

# Expected: Strict sequential execution, no dynamic adjustments
```

#### Iterative Strategy
```bash
# Test feedback loops
python -m agent-orchestrator supervise \
  --task "Refine this code until it passes review" \
  --workers "code,review" \
  --strategy iterative \
  --max-iterations 5

# Expected: code → review → code (with feedback) → review ... until success or max iterations
```

### 5. Edge Cases

#### Single Worker
```bash
# Test supervisor with single worker (degrades gracefully)
python -m agent-orchestrator supervise \
  --task "Simple standalone task" \
  --workers "write"

# Expected: Works like direct agent execution, minimal overhead
```

#### Empty/Invalid Workers
```bash
# Test error handling for invalid worker specification
python -m agent-orchestrator supervise \
  --task "Test" \
  --workers "invalidrole"

# Expected: Treats as CUSTOM role or shows clear error
```

#### Very Large Task
```bash
# Test with lengthy task description
python -m agent-orchestrator supervise \
  --task "$(cat very_long_document.txt)" \
  --workers "summarize,analyze" \
  --verbose

# Expected: Handles large context, may truncate in logs appropriately
```

### 6. CLI Argument Tests

```bash
# Test all argument combinations
python -m agent-orchestrator supervise --help

# Test verbose mode captures reasoning
python -m agent-orchestrator supervise -t "Test" -w "write" -v

# Test no-synthesize returns raw outputs
python -m agent-orchestrator supervise -t "Test" -w "research,write" --no-synthesize

# Test max-iterations limit
python -m agent-orchestrator supervise -t "Test" -w "write" --max-iterations 2
```

## Validation Checklist

Before marking Supervisor pattern complete:

- [ ] Task analysis produces structured output
- [ ] Decomposition creates correct dependency chains
- [ ] Workers receive appropriate context from dependencies
- [ ] Sequential execution respects dependencies
- [ ] Parallel execution works when no dependencies
- [ ] Synthesis combines outputs coherently
- [ ] Retry logic attempts restart on failure
- [ ] Max retries respected before marking failed
- [ ] Verbose mode shows supervisor reasoning
- [ ] State file persists execution progress
- [ ] CLI help is accurate and complete
- [ ] Error messages are clear and actionable

## Test Execution Plan

**Phase 1:** Unit tests (when Python environment available)
- Requires: pytest, mock for SessionManager
- Estimated: 2-3 hours to implement

**Phase 2:** Integration tests (requires full OpenClaw environment)
- Requires: Working sessions_spawn capability
- Estimated: 1-2 hours per test
- Note: Token costs ~15x normal for multi-agent tests

**Phase 3:** Edge case verification
- Requires: Fault injection capability
- Estimated: 2 hours

**Risk Areas:**
1. SessionManager integration with real OpenClaw CLI
2. Timeout handling across multiple agents
3. Token usage can be high for complex workflows
4. Synthesis quality depends on sub-agent capabilities

## Success Metrics

- 100% of happy path tests pass
- 80%+ of edge case tests pass
- Failed workers retry up to configured limit
- Final synthesis is coherent and useful
- Verbose mode provides clear insight into supervisor decisions
- No crashes or hangs on any input
