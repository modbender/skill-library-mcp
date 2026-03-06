/**
 * Pi Workflow Self-Improvement Hook for OpenClaw
 * 
 * Injects a reminder at agent bootstrap to evaluate learnings.
 * Tailored for workspace tasks/ structure (not .learnings/)
 */

const REMINDER_CONTENT = `
## 🧠 Self-Improvement Reminder

After completing tasks, evaluate if any learnings should be captured using Phase 1+2 format.

### Log Lessons (Corrections & Insights)
Capture to: \`tasks/lessons.md\`

When to log:
- User corrects you ("That's wrong...")
- You discover a better pattern
- You learn something new about the system

Format: \`[LRN-YYYYMMDD-XXX] lesson_name (category)\` with metadata: Priority, Status, Area, Pattern-Key, Recurrence-Count

### Log Errors (Failures & Diagnosis)
Capture to: \`tasks/errors.md\`

When to log:
- Command returns error / API fails
- Exception thrown unexpectedly
- Tool integration breaks

Format: \`[ERR-YYYYMMDD-XXX] service_name\` with Error Output, Context, Suggested Fix

### Log Features (Capability Gaps)
Capture to: \`tasks/feature_requests.md\`

When to log:
- "I wish Tool X could do Y"
- Missing integration or workflow
- Blocker for desired functionality

Format: \`[FEAT-YYYYMMDD-XXX] capability_name\` with Complexity Estimate, Suggested Implementation

### Tracking Recurring Patterns
- Increment \`Recurrence-Count\` when you see same issue again
- When count ≥ 3 over 30 days → consider promoting to permanent rule in AGENTS.md

### Promotion Path
When a lesson becomes broadly applicable:
- **Behavioral patterns** → \`SOUL.md\`
- **Workflow improvements** → \`AGENTS.md\`
- **Tool gotchas** → \`TOOLS.md\`

See \`references/phase1-phase2-enhanced-lessons.md\` for detailed guide.
`.trim();

const handler = async (event) => {
  // Safety checks for event structure
  if (!event || typeof event !== 'object') {
    return;
  }

  // Only handle agent:bootstrap events
  if (event.type !== 'agent' || event.action !== 'bootstrap') {
    return;
  }

  // Safety check for context
  if (!event.context || typeof event.context !== 'object') {
    return;
  }

  // Skip sub-agent sessions to avoid bootstrap issues
  // Sub-agents have sessionKey patterns like "agent:main:subagent:..."
  const sessionKey = event.sessionKey || '';
  if (sessionKey.includes(':subagent:')) {
    return;
  }

  // Inject the reminder as a virtual bootstrap file
  // Check that bootstrapFiles is an array before pushing
  if (Array.isArray(event.context.bootstrapFiles)) {
    event.context.bootstrapFiles.push({
      path: 'PI_WORKFLOW_REMINDER.md',
      content: REMINDER_CONTENT,
      virtual: true,
    });
  }
};

module.exports = handler;
module.exports.default = handler;
