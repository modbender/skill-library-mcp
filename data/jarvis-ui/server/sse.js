// ── SSE 廣播管理 ──

const sseClients = new Set();
const voiceChatHandlers = new Set();

export function addClient(res) { sseClients.add(res); }
export function removeClient(res) { sseClients.delete(res); }
export function clientCount() { return sseClients.size; }
export function addVoiceHandler(h) { voiceChatHandlers.add(h); }
export function removeVoiceHandler(h) { voiceChatHandlers.delete(h); }

// 提取文字內容
function extractText(payload) {
  if (!payload.message?.content) return '';
  const content = payload.message.content;
  if (Array.isArray(content)) return content.filter(c => c.type === 'text').map(c => c.text).join('');
  return typeof content === 'string' ? content : '';
}

export function broadcastChat(payload) {
  const text = extractText(payload);
  const event = {
    runId: payload.runId,
    state: payload.state,
    text,
    role: payload.message?.role || '',
    done: payload.state === 'final' || payload.state === 'aborted',
  };
  if (payload.message?.model) event.model = payload.message.model;
  if (payload.message?.provider) event.provider = payload.message.provider;
  if (payload.message?.usage) event.usage = payload.message.usage;

  const data = JSON.stringify(event);
  for (const res of sseClients) res.write(`data: ${data}\n\n`);
  for (const handler of voiceChatHandlers) { try { handler(payload); } catch {} }
}

export function broadcastSystem(data) {
  const msg = JSON.stringify({ type: 'system', ...data });
  for (const res of sseClients) res.write(`data: ${msg}\n\n`);
}

export function broadcastEvent(type) {
  const msg = JSON.stringify({ type });
  for (const res of sseClients) res.write(`data: ${msg}\n\n`);
}
