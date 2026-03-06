---
name: easy-opencode
description: opencode can do all the things related to code
metadata: {"clawdbot":{"emoji":"💯🚀🎯","requires":{"bins":["opencode"]}}}
---

# Opencode 

## Core rule

For any problem related to coding of a repository, please use opencode directly, the major burden of question-answering and coding should be given to opencode which is very capable to do it well.
Your job to pass the question to opencode, digest the result from opencode and select what to do next (plan or build) based on the result from opencode.
All planning and coding happens inside Opencode.

## Usages

- Available agents:
  - plan
  - build
- Always select Plan first.
- plan agent: run with `cd [repo dir] && opencode run "[instructions/questions]" --continue --agent plan`
- build agent: run with `cd [repo dir] && opencode run "[instructions/questions]" --continue --agent build`

## Plan agent behavior

- Ask Opencode to analyze the task.
- Request a clear step-by-step plan.
- Allow Opencode to ask clarification questions.
- Review the plan carefully.
- If the plan is incorrect or incomplete:
  - Ask Opencode to revise it.
- Do not allow code generation in Plan.

## Build agent behavior

- Ask Opencode to implement the approved plan.
- If Opencode asks any question:
  - Immediately switch back to Plan.
  - Answer and confirm the plan.
  - Switch back to Build.

## Completion

- Repeat the Plan → Build loop until all user requirements are satisfied.
- Never skip Plan.
- Never answer questions in Build.

