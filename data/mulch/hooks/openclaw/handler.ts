/**
 * Self-Improvement Hook for OpenClaw
 * Injects a short reminder on agent:bootstrap (main session only). Low token footprint.
 */

import type { HookHandler } from 'openclaw/hooks';

const EVENT_TYPE = 'agent';
const EVENT_ACTION = 'bootstrap';

const REMINDER_CONTENT = `## Self-Improvement (Mulch)

**Session start:** Run \`mulch prime\` when project has \`.mulch/\`.
**Record:** \`mulch record <domain> --type failure|convention|decision|pattern|guide\` — failure needs \`--description\` and \`--resolution\`; convention is one short string; decision needs \`--title\` and \`--rationale\`.
**Promote (proven patterns):** behavior → \`SOUL.md\`; workflow → \`AGENTS.md\`; tool gotchas → \`TOOLS.md\`. Use \`mulch onboard\` for snippets.`;

const handler: HookHandler = async (event) => {
  if (
    !event?.context ||
    event.type !== EVENT_TYPE ||
    event.action !== EVENT_ACTION ||
    (event.sessionKey ?? '').includes(':subagent:')
  ) {
    return;
  }

  const files = event.context.bootstrapFiles;
  if (Array.isArray(files)) {
    files.push({
      path: 'SELF_IMPROVEMENT_REMINDER.md',
      content: REMINDER_CONTENT,
      virtual: true,
    });
  }
};

export default handler;
