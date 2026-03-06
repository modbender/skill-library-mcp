# Chains: automation

## 1) Start workflow from CRM event

1. `event.bind` on deal/lead update
2. `bizproc.workflow.start`
3. Track state through workflow/task methods

## 2) Robot configuration rollout

1. `bizproc.robot.list`
2. `bizproc.robot.add` or `bizproc.robot.update`
3. Validate on test entity before broader rollout

## 3) Controlled stop path

1. Read active workflow identifiers
2. `bizproc.workflow.terminate` for normal stop
3. `bizproc.workflow.kill` only for emergency cleanup
