---
name: department-manager
description: Manage a team of AI sub-agents organized into departments. Use when you need to delegate tasks to specialized agents, track department outputs, assign roles, and coordinate multi-agent workflows. Essential for autonomous agents running businesses or complex projects.
user-invocable: true
metadata: {"openclaw": {"emoji": "🏢", "os": ["darwin", "linux"], "requires": {"bins": ["python3"]}}}
---

# Department Manager

Organize your AI workers into departments. Assign tasks, track output, and coordinate multi-agent teams like a CEO.

## Why This Exists

Running an autonomous business or complex project means juggling multiple tasks across different domains: content, research, code, marketing, operations. Instead of doing everything sequentially, organize your workers into departments and delegate in parallel.

## Commands

### Create a department
```bash
python3 {baseDir}/scripts/departments.py create --name "content" --description "SEO blog posts, marketing copy, newsletters" --model "arcee-ai/trinity-large-preview:free"
```

### List departments
```bash
python3 {baseDir}/scripts/departments.py list
```

### Assign a task to a department
```bash
python3 {baseDir}/scripts/departments.py assign --dept "content" --task "Write a blog post about OpenClaw memory system" --priority high
```

### Check department status
```bash
python3 {baseDir}/scripts/departments.py status --dept "content"
```

### View all active tasks across departments
```bash
python3 {baseDir}/scripts/departments.py active
```

### Complete a task
```bash
python3 {baseDir}/scripts/departments.py complete --task-id 1 --output "Blog post written and saved to drafts/memory-post.md"
```

### Department report (summary of all departments)
```bash
python3 {baseDir}/scripts/departments.py report
```

### Remove a department
```bash
python3 {baseDir}/scripts/departments.py remove --name "content"
```

## Recommended Department Structure

| Department | Model | Responsibilities |
|------------|-------|-----------------|
| content | arcee-ai/trinity-large-preview:free | Blog posts, marketing copy, newsletters |
| research | stepfun/step-3.5-flash:free | Market research, competitor analysis, data gathering |
| engineering | openrouter/free | Code generation, bug fixes, tooling |
| operations | (manual/CEO) | Budget, strategy, communications |
| security | (manual/CEO) | Skill scanning, threat assessment, audits |

## Data Storage

Department data stored in `~/.openclaw/department-manager/departments.json`.

## Tips

- Create departments based on your actual workflow, not hypothetical needs
- Assign one default model per department for consistency
- Review completed tasks before publishing — QA is the CEO's job
- Use priority levels to focus workers on what matters now
- Run `report` at the end of each day for a team overview
