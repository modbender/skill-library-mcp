# Report Templates & Customization

## Audience Formats

### Executive Summary (`--audience exec`)
Target: VPs, C-suite, stakeholders who need the 30-second version.
- RAG status per workstream (Red/Amber/Green)
- 3-5 bullet key highlights
- Top risks (max 3)
- Decisions needed from leadership
- Upcoming milestones
- **Under 200 words total**

### Engineering Update (`--audience eng`)
Target: Engineering leads, tech leads, ICs who need sprint details.
- Sprint progress by status category
- Completed items (last 7 days)
- Current blockers with owners
- Stale ticket warnings
- PR review queue (needs-review flagged)
- CI health status

### Full Program Update (`--audience full`)
Target: Program stakeholders, cross-functional partners.
- Overall RAG with per-workstream detail
- Status tables per workstream
- Complete issue lists (done, blocked, stale)
- GitHub metrics per repo
- Milestone tracking table
- Full risk register
- Dependency status

## RAG Status Logic

Automatic RAG calculation per workstream:

- **🔴 RED**: 3+ blockers OR <30% sprint completion
- **🟡 AMBER**: 1+ blockers OR 3+ stale tickets OR <60% sprint completion
- **🟢 GREEN**: No blockers, minimal stale tickets, >60% completion

Override: add `"rag_override": "red"` to workstream config for manual control.

## Customizing Reports

### Add custom sections
Edit program config `report_sections`:
```json
{
  "report_sections": {
    "exec": ["rag", "highlights", "risks", "milestones", "decisions"],
    "eng": ["sprint", "completed", "blockers", "stale", "github"],
    "full": ["rag", "sprint", "completed", "blockers", "stale", "github", "milestones", "risks", "dependencies"]
  }
}
```

### Custom delivery
Add to program config:
```json
{
  "delivery": {
    "exec": {"via": "email", "to": ["vp@company.com"]},
    "eng": {"via": "slack", "channel": "#eng-updates"},
    "full": {"via": "confluence", "space": "ENG", "page_title": "Program Status"}
  }
}
```
