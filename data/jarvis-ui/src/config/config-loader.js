// ── 前端設定載入 ──
// 從 /api/config 拿設定，fallback 用 agent.json

let _config = null;

export async function loadConfig() {
  if (_config) return _config;

  try {
    const res = await fetch('/api/config');
    if (res.ok) {
      _config = await res.json();
      return _config;
    }
  } catch {}

  // fallback: 靜態 agent.json
  try {
    const { default: agent } = await import('./agent.json', { with: { type: 'json' } });
    _config = { name: agent.title, agent: { name: agent.name, emoji: '🌸', skills: agent.skills.map(s => s.name) }, theme: {} };
  } catch {
    _config = { name: 'JARVIS', agent: { name: 'JARVIS', emoji: '🤖', skills: [] }, theme: {} };
  }

  return _config;
}

export function getConfig() {
  return _config;
}
