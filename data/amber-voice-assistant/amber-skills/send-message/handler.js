/**
 * Send Message Skill — Handler
 * 
 * Saves a caller's message to the call log and delivers it
 * to the operator via their configured messaging channel.
 * 
 * Telegram delivery is fire-and-forget — the caller gets instant
 * confirmation after the call log write. The gateway round-trip
 * happens in the background.
 */

/**
 * Sanitize a string — strip control characters, enforce max length.
 */
function sanitize(s, maxLen) {
  if (!s) return '';
  return String(s)
    .replace(/[\x00-\x08\x0b\x0c\x0e-\x1f]/g, '')
    .slice(0, maxLen || 500);
}

module.exports = async function sendMessageHandler(params, context) {
  const cleanMessage = sanitize(params.message, 1000);
  const cleanName = sanitize(params.caller_name, 100);
  const cleanCallback = sanitize(params.callback_number, 20);
  const cleanUrgency = params.urgency === 'urgent' ? 'urgent' : 'normal';

  if (!cleanMessage) {
    return {
      success: false,
      error: 'Empty message',
      message: "I didn't catch a message to leave. Could you repeat that?",
    };
  }

  // Step 1: ALWAYS write to call log first (audit trail) — this is the critical path
  const logEntry = {
    type: 'skill.send_message',
    caller_name: cleanName || 'Unknown',
    callback_number: cleanCallback || 'Not provided',
    message: cleanMessage,
    urgency: cleanUrgency,
    delivery_status: 'pending',
  };

  context.callLog.write(logEntry);

  // Step 2: Fire-and-forget delivery via operator's messaging channel
  // Do NOT await — the gateway round-trip can take 10-30 seconds through OpenClaw.
  // The caller gets instant confirmation; delivery happens in the background.
  const operatorName = context.operator.name || 'operator';
  const emoji = cleanUrgency === 'urgent' ? '🚨' : '📞';

  // SECURITY: Caller-supplied content is wrapped in explicit delimiters to prevent
  // prompt injection. The LLM downstream should treat everything between
  // [CALLER MESSAGE START] / [CALLER MESSAGE END] as untrusted user data only.
  const formattedMessage = [
    `${emoji} Message from a call:`,
    '',
    cleanName ? `From: ${cleanName}` : null,
    cleanCallback ? `Callback: ${cleanCallback}` : null,
    cleanUrgency === 'urgent' ? 'Priority: URGENT' : null,
    '',
    '[CALLER MESSAGE START]',
    cleanMessage,
    '[CALLER MESSAGE END]',
  ]
    .filter(function (line) { return line !== null; })
    .join('\n');

  // Fire and forget — log success/failure asynchronously
  context.gateway.sendMessage(formattedMessage)
    .then(function () {
      context.callLog.write({
        type: 'skill.send_message.delivered',
        delivery_channel: 'openclaw_gateway',
      });
    })
    .catch(function (e) {
      context.callLog.write({
        type: 'skill.send_message.delivery_failed',
        error: e && e.message ? e.message : String(e),
      });
    });

  // Return immediately — caller gets instant feedback
  const operatorRef = context.operator.name || 'The operator';
  const spokenResponse = cleanName
    ? `Got it — I've noted your message, ${cleanName}. ${operatorRef} will get back to you.`
    : `Got it — I've noted your message. ${operatorRef} will get back to you.`;

  return {
    success: true,
    message: spokenResponse,
    result: { logged: true, delivered: 'background' },
  };
};
