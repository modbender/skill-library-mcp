/**
 * Xerolite webhook transform
 * Formats payload and returns agent action with strict no-rephrase instruction
 */
module.exports = async function xeroliteTransform(context) {
  // context contains: { payload, headers, url, path }
  // payload is the actual JSON body from Xerolite
  const data = context.payload || context;
  
  // Format the payload as a readable block
  const lines = ['📥 **Xerolite Notification**', ''];
  
  if (data.event) {
    lines.push(`**Event:** ${data.event}`);
  }
  if (data.message) {
    lines.push(`**Message:** ${data.message}`);
  }
  if (data.data) {
    if (typeof data.data === 'object') {
      lines.push(`**Data:**`);
      for (const [k, v] of Object.entries(data.data)) {
        lines.push(`  • ${k}: ${v}`);
      }
    } else {
      lines.push(`**Data:** ${data.data}`);
    }
  }
  
  // Include any extra fields from payload (not context metadata)
  const knownFields = ['event', 'message', 'data'];
  for (const [key, value] of Object.entries(data)) {
    if (!knownFields.includes(key)) {
      lines.push(`**${key}:** ${typeof value === 'object' ? JSON.stringify(value) : value}`);
    }
  }

  const formattedContent = lines.join('\n');

  // Return agent action with strict instruction
  return {
    action: 'agent',
    name: 'Xerolite',
    message: `Forward to user through channel, Output ONLY the following notification. No commentary, no questions, no time, no offers to help:\n\n${formattedContent}`,
    deliver: true,
    channel: 'telegram',
    allowUnsafeExternalContent: true
  };
};
