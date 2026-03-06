const fs   = require('fs');
const path = require('path');

const STATE_FILE = path.join(
  process.env.HOME,
  '.openclaw', 'skills', 'sleep-snooze', 'data', 'state.json'
);

const QUEUE_SCRIPT = path.join(
  process.env.HOME,
  '.openclaw', 'skills', 'sleep-snooze', 'scripts', 'queue-message.js'
);

const handler = async (event) => {
  if (event.type !== 'agent' || event.action !== 'bootstrap') return;

  let state;
  try {
    state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  } catch {
    // sleep-snooze not configured yet — skip silently
    return;
  }

  if (!state.isSleeping) return;

  // Inject a strongly-worded bootstrap file into every agent session
  if (event.context && Array.isArray(event.context.bootstrapFiles)) {
    event.context.bootstrapFiles.push({
      basename: 'SLEEP_MODE_ACTIVE.md',
      content: buildSleepNotice(state),
    });
  }
};

function buildSleepNotice(state) {
  return `# 🌙 SLEEP MODE IS ACTIVE — READ THIS BEFORE TAKING ANY ACTION

The user is currently sleeping. Sleep window: **${state.sleepStart} → ${state.wakeTime} (${state.timezone})**.

## RULE: Do NOT send any message to the user

This includes: summaries, alerts, status updates, heartbeats, digests, reports, or any other notification.

## Instead: Queue every message

For anything you would normally send, run this command instead:

\`\`\`bash
node ${QUEUE_SCRIPT} \\
  --provider <provider-name> \\
  --sender-id <your-agent-id> \\
  --sender-name "<Your Agent Name>" \\
  --message "<the full message text>"
\`\`\`

Exit codes:
- **0** — queued successfully → do nothing else, do not send
- **2** — urgent message → deliver immediately, prefix with 🚨

## Urgency bypass (exit code 2 only)

Only consider a message urgent if:
- It contains the words: \`urgent\`, \`emergency\`, \`critical\`, \`911\`, \`help me\`
- The sender is a known VIP contact

Everything else — including routine heartbeats, weekly recaps, stock summaries, and backup confirmations — must be **queued, not sent**.

## If the user sends you a message first

If the user themselves initiates contact, suspend sleep mode for 30 minutes (they are awake). Respond normally.
`;
}

module.exports = handler;
