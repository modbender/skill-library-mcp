const https = require('https');
const { getConfig, getState, updateState } = require('./db');

async function notifyProposals(proposals) {
  const config = getConfig();
  if (!config.notifications?.enabled) return;

  // Mute check
  const muteUntil = getState('mute_until');
  if (muteUntil && new Date(muteUntil) > new Date()) {
    console.log(`[NOTIFY] Muted until ${muteUntil}. Skipping.`);
    return;
  }

  const channel = config.notifications.channel || 'telegram';
  const text = formatProposals(proposals);

  // Save digest IDs for NL-feedback
  updateState('last_digest_ids', JSON.stringify(proposals.map(p => p.id)));
  updateState('last_digest_at', new Date().toISOString());

  if (channel === 'telegram') await sendTelegram(text, config);
  else if (channel === 'discord') await sendDiscord(text, config);
}

function formatProposals(proposals) {
  const eff = { quick:'⚡', medium:'🔧', large:'🏗️' };
  const cat = { automation:'🤖', project:'📦', tool:'🔨', optimization:'⚡', fix:'🔧', social:'🎭', follow_up:'📌', learning:'📚' };
  let t = '🧠 *Hey, mir ist was aufgefallen:*\n\n';
  for (const p of proposals) {
    const effort = p.effort_estimate || p.effort || 'medium';
    const type = p.type || 'optimization';
    const followUp = p.follow_up || p.reasoning || '';
    t += `${cat[type]||'💡'} *${p.title}*\n${p.description}`;
    if (followUp) t += `\n💬 _${followUp}_`;
    t += `\n${eff[effort]||''} ${effort} | #${p.id}\n\n`;
  }
  t += '_/accept <ID...> | /reject <ID...> | /drop <ID...>_';
  return t;
}

async function sendTelegram(text, config) {
  const token = config.notifications?.telegram?.botToken;
  const chatId = config.notifications?.telegram?.chatId;
  if (!token || !chatId) { console.warn('⚠️  Telegram not configured'); return; }
  const body = JSON.stringify({ chat_id: chatId, text, parse_mode: 'Markdown', disable_web_page_preview: true });
  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: 'api.telegram.org', path: `/bot${token}/sendMessage`, method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }
    }, (res) => {
      let d=''; res.on('data', c=>d+=c); res.on('end', () => {
        const j=JSON.parse(d); j.ok ? (console.log('✅ Telegram sent'), resolve()) : (console.error('❌ Telegram:', j.description), reject(new Error(j.description)));
      });
    });
    req.on('error', reject); req.write(body); req.end();
  });
}

async function sendDiscord(text, config) {
  const url = config.notifications?.discord?.webhookUrl;
  if (!url) { console.warn('⚠️  Discord webhook not configured'); return; }
  const u = new URL(url);
  const body = JSON.stringify({ content: text.replace(/\*/g, '**') });
  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: u.hostname, path: u.pathname, method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }
    }, (res) => {
      let d=''; res.on('data', c=>d+=c); res.on('end', () => {
        (res.statusCode===204||res.statusCode===200) ? (console.log('✅ Discord sent'), resolve()) : reject(new Error(`Discord: ${res.statusCode}`));
      });
    });
    req.on('error', reject); req.write(body); req.end();
  });
}

async function notifyNudges(nudges) {
  const config = getConfig();
  if (!config.notifications?.enabled) return;
  if (nudges.length === 0) return;

  // Mute check
  const muteUntil = getState('mute_until');
  if (muteUntil && new Date(muteUntil) > new Date()) return;

  let t = '🔔 *Hey, kurze Erinnerung:*\n\n';
  for (const n of nudges) {
    t += `📌 *#${n.id} ${n.title}*\n`;
    if (n.message) t += `${n.message}\n`;
    t += `_/accept ${n.id} | /drop ${n.id}_\n\n`;
  }

  const channel = config.notifications.channel || 'telegram';
  if (channel === 'telegram') await sendTelegram(t, config);
  else if (channel === 'discord') await sendDiscord(t, config);
}

module.exports = { notifyProposals, notifyNudges };
