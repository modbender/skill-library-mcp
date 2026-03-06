# Workflow YAML Format

Workflows live in `workflows/<name>/workflow.yml` inside the Soulforge install directory.

## Schema

```yaml
id: my-workflow           # unique identifier
name: My Workflow         # display name
version: 1
description: |
  What this workflow does.

defaults:                 # applied to all steps unless overridden
  executor: claude-code   # claude-code | codex | openclaw | self
  model: opus             # model passed to executor CLI
  timeout: 600            # seconds per step
  max_retries: 2

steps:
  - id: step-name
    executor: claude-code        # override default executor
    model: opus                  # override default model
    workdir: "{{workdir}}"       # working directory for this step
    type: single                 # single (default) or loop
    timeout: 300                 # override default timeout
    max_retries: 1
    input: |                     # prompt sent to executor
      Instructions with {{template_variables}}.
      Reply with:
      STATUS: done
    expects: "STATUS: done"      # string the output must contain
    on_reject:                   # for self (checkpoint) steps
      reset_to: plan             # reset pipeline to this step on reject
    on_fail:                     # optional failure handling
      retry_step: step-name      # which step to retry
      max_retries: 3
      escalate_to: review-step   # checkpoint on exhaustion
```

## Executor Types

| Executor | What it does |
|----------|-------------|
| `claude-code` | Runs Claude Code CLI (`claude`) with the step's input as prompt. Passes `--model` flag. |
| `codex` | Runs Codex CLI with the step's input. |
| `openclaw` | Sends to an OpenClaw sub-agent session (stub — not yet implemented). |
| `self` | **Human checkpoint.** Pauses the run and waits for `soulforge approve` or `soulforge reject`. |

## Template Variables

Steps can use `{{variable}}` placeholders. Built-in variables:

| Variable | Source |
|----------|--------|
| `{{task}}` | The task string passed to `soulforge run` |
| `{{workdir}}` | The working directory for this run |
| `{{branch}}` | The git branch name |
| `{{build_cmd}}` | From `--var build_cmd=…` |
| `{{test_cmd}}` | From `--var test_cmd=…` |
| `{{run_id}}` | The unique run ID |
| `{{rejection_feedback}}` | Feedback from a rejected checkpoint (when looping back via `on_reject`) |

Custom variables are passed via `--var key=value` flags.

Step outputs are also available as variables in subsequent steps. For example, if the `plan` step outputs `STORIES_JSON: [...]`, later steps can reference `{{stories_json}}`.

## Loop Steps

For iterating over a list (e.g., implementing multiple stories):

```yaml
- id: implement
  type: loop
  loop:
    over: stories              # variable containing the array
    completion: all_done       # complete when all items done
    fresh_session: true        # new executor session per iteration
    verify_each: true          # run verify step after each iteration
    verify_step: verify        # which step to use for verification
  input: |
    CURRENT STORY: {{current_story}}
    COMPLETED: {{completed_stories}}
    REMAINING: {{stories_remaining}}
```

## Example: Feature Development

The built-in `feature-dev` workflow implements a full development pipeline:

1. **plan** (claude-code) — decompose task into ordered user stories
2. **review-plan** (self) — human reviews the plan; reject loops back to re-plan with feedback
3. **implement** (claude-code, loop) — implement each story, verified individually
4. **verify** (claude-code) — verify each story's acceptance criteria
5. **test** (claude-code) — run integration/E2E tests
6. **pr** (claude-code) — create pull request with `gh pr create`
7. **final-review** (self) — human reviews PR before merge

All steps use `model: opus` by default.
