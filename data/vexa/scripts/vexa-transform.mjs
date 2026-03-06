// OpenClaw hook transform for Vexa webhooks.
// Purpose: process only "meeting finished" events and create a basic meeting report.
// Skips: empty payloads, heartbeats, in-progress meetings.
//
// When meeting is finished: injects explicit report command so the agent creates
// the report via `vexa.mjs report`.

export default async function transform(ctx) {
  const p = ctx?.payload || {};

  // Extract platform + native_meeting_id from common payload shapes
  const platform =
    (typeof p.platform === 'string' && p.platform) ||
    (typeof p.meeting?.platform === 'string' && p.meeting.platform) ||
    (typeof p.data?.platform === 'string' && p.data.platform) ||
    '';

  const nativeMeetingId =
    (typeof p.native_meeting_id === 'string' && p.native_meeting_id) ||
    (typeof p.meeting?.native_meeting_id === 'string' && p.meeting.native_meeting_id) ||
    (typeof p.data?.native_meeting_id === 'string' && p.data.native_meeting_id) ||
    '';

  if (!platform || !nativeMeetingId) {
    return null; // skip — no meeting identity
  }

  // Only process when meeting is finished (skip in-progress / heartbeat)
  const status = (
    (typeof p.status === 'string' && p.status) ||
    (typeof p.meeting?.status === 'string' && p.meeting.status) ||
    (typeof p.data?.status === 'string' && p.data.status) ||
    ''
  ).toLowerCase();

  const event = (
    (typeof p.event === 'string' && p.event) ||
    (typeof p.event_type === 'string' && p.event_type) ||
    ''
  ).toLowerCase();

  const completionReason = p.data?.completion_reason ?? p.meeting?.data?.completion_reason;

  const isFinished =
    ['completed', 'finalized', 'done'].includes(status) ||
    (event && (event.includes('complete') || event.includes('final'))) ||
    Boolean(completionReason);

  const isInProgress = ['active', 'in_progress', 'running'].includes(status);

  if (isInProgress) {
    return null; // skip — meeting still running
  }
  if (!isFinished && (status || event)) {
    return null; // skip — has status/event but not finished
  }

  // Meeting finished — inject explicit report command
  const reportCmd = `node skills/vexa/scripts/vexa.mjs report --platform ${platform} --native_meeting_id ${nativeMeetingId}`;

  const message = `Vexa meeting finished webhook received.

**Extracted:** platform=${platform}, native_meeting_id=${nativeMeetingId}

**Task:**
1. Run: \`${reportCmd}\` (creates basic meeting report in memory/meetings/)
2. Open the generated report and add a \`## Summary\` section with 5–10 bullets
3. Update/create entity files under memory/entities/ (products, companies, people) referenced in the report
4. Reply with: report path + entities updated + any issues

Raw payload (for reference):
\`\`\`json
${JSON.stringify(p, null, 2)}
\`\`\``;

  return { message };
}
