/**
 * LYNQN OpenClaw Skill
 * Share text, generate QR codes, and shorten URLs
 */

const LYNQN_API = process.env.LYNQN_API_URL || 'https://lynqn.io/api';

// Derive site origin from API URL (e.g. "https://lynqn.io/api" → "https://lynqn.io")
function siteOrigin() {
  try {
    const u = new URL(LYNQN_API);
    return u.origin;
  } catch {
    return 'https://lynqn.io';
  }
}

// Safe JSON fetch wrapper
async function apiFetch(path, options) {
  const url = `${LYNQN_API}${path}`;
  const res = await fetch(url, options);
  const text = await res.text();

  let data;
  try {
    data = JSON.parse(text);
  } catch {
    throw new Error(`Unexpected response from ${path}: ${text.slice(0, 120)}`);
  }

  if (!res.ok) {
    throw new Error(data.error || `Request failed with status ${res.status}`);
  }
  return data;
}

// Helper to parse expiration times
function parseExpiration(expiresArg) {
  const map = {
    '1d': 60 * 60 * 24,
    '1w': 60 * 60 * 24 * 7,
    '1m': 60 * 60 * 24 * 30,
    '3m': 60 * 60 * 24 * 90,
  };
  return map[expiresArg] || map['1w'];
}

// Command: /lynqn share
async function shareText(agent, args) {
  const flags = agent.parseFlags(args, {
    syntax: { type: 'boolean', default: false },
    expires: { type: 'string', default: '1w' },
  });

  const content = flags._.join(' ');
  if (!content) {
    return agent.reply('Please provide text to share.\nUsage: /lynqn share <text> [--syntax] [--expires 1d|1w|1m|3m]');
  }

  try {
    const data = await apiFetch('/share', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content,
        format: flags.syntax ? 'code' : 'text',
        expiresIn: parseExpiration(flags.expires),
      }),
    });

    const shareUrl = `${siteOrigin()}/s/${data.id}`;

    return agent.reply(
      `Share created!\n\n` +
      `Link: ${shareUrl}\n` +
      `Expires: ${flags.expires}`
    );
  } catch (error) {
    return agent.reply(`Error: ${error.message}`);
  }
}

// Command: /lynqn qr
async function generateQR(agent, args) {
  const flags = agent.parseFlags(args, {
    size: { type: 'number', default: 300 },
    error: { type: 'string', default: 'M' },
  });

  const content = flags._.join(' ');
  if (!content) {
    return agent.reply('Please provide content for QR code.\nUsage: /lynqn qr <content> [--size 200-800] [--error L|M|Q|H]');
  }

  const size = Math.max(200, Math.min(flags.size, 800));
  const errorLevel = ['L', 'M', 'Q', 'H'].includes(flags.error) ? flags.error : 'M';

  const qrUrl = `${siteOrigin()}/qr-generator?text=${encodeURIComponent(content)}&size=${size}&error=${errorLevel}`;

  return agent.reply(
    `QR Code ready!\n\n` +
    `Generate and download: ${qrUrl}\n` +
    `Size: ${size}px | Error correction: ${errorLevel}`
  );
}

// Command: /lynqn shorten
async function shortenURL(agent, args) {
  const flags = agent.parseFlags(args, {});
  const url = flags._.join(' ').trim();

  if (!url) {
    return agent.reply('Please provide a URL to shorten.\nUsage: /lynqn shorten <url>');
  }

  try {
    new URL(url);
  } catch {
    return agent.reply(`Invalid URL: ${url}`);
  }

  try {
    const data = await apiFetch('/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });

    return agent.reply(
      `URL shortened!\n\n` +
      `Short URL: ${data.shortUrl}\n` +
      `Original: ${data.originalUrl}`
    );
  } catch (error) {
    return agent.reply(`Error: ${error.message}`);
  }
}

// Command: /lynqn stats
async function getStats(agent) {
  try {
    const data = await apiFetch('/stats');

    return agent.reply(
      `LYNQN Stats\n\n` +
      `Total shares: ${data.total != null ? Number(data.total).toLocaleString() : 'N/A'}\n` +
      `Platform: ${siteOrigin()}`
    );
  } catch (error) {
    return agent.reply(`Error: ${error.message}`);
  }
}

// Main skill export
module.exports = {
  name: 'lynqn',
  description: 'Share text, generate QR codes, and shorten URLs',

  commands: {
    'lynqn share': shareText,
    'lynqn qr': generateQR,
    'lynqn shorten': shortenURL,
    'lynqn stats': getStats,
  },

  async init(agent) {
    agent.log('LYNQN skill loaded — API: ' + LYNQN_API);
    return true;
  },
};
