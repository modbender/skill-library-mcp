#!/usr/bin/env node

const https = require('https');
const fs = require('fs');
const path = require('path');

const API_BASE = 'https://dot.mindreset.tech/api/authV2/open';
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const MAX_IMAGE_BYTES = 5 * 1024 * 1024;

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      if (i + 1 < argv.length && !argv[i + 1].startsWith('--')) {
        out[key] = argv[++i];
      } else {
        out[key] = 'true';
      }
    } else {
      out._.push(arg);
    }
  }
  return out;
}

function toBool(v, defaultValue = true) {
  if (v === undefined) return defaultValue;
  return !(String(v).toLowerCase() === 'false' || v === '0');
}

function nowSignature() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
}

function printHelp() {
  console.log(`
Quote/0 API CLI (v1.0.4)

Usage:
  node quote0.js <command> [options]

Commands:
  text        Update Text API content
  image       Update Image API content
  devices     List my devices
  status      Get device status
  next        Switch to next content
  list        List device content by type

Global options:
  --apiKey <key>       API key (fallback: DOT_API_KEY env)
  --deviceId <id>      Device serial number (fallback: DOT_DEVICE_ID env)

text options:
  --title <text>       Title (default: Clawdbot)
  --message <text>     Message body (required)
  --signature <text>   Signature (default: current time)
  --icon <base64>      Base64 PNG icon (40x40)
  --link <url>         NFC redirect URL / scheme
  --taskKey <key>      Target specific Text API slot
  --refresh <bool>     Refresh immediately (default: true)

image options:
  --image <base64>     Base64 PNG image (296x152)
  --imageFile <path>   PNG file path <=5MB (auto convert to base64)
  --link <url>         NFC redirect URL / scheme
  --border <0|1>       Border color (0=white, 1=black; default 0)
  --ditherType <type>  DIFFUSION | ORDERED | NONE
  --ditherKernel <k>   THRESHOLD | ATKINSON | BURKES | FLOYD_STEINBERG | ...
  --taskKey <key>      Target specific Image API slot
  --refresh <bool>     Refresh immediately (default: true)

list options:
  --taskType <type>    Usually loop (default: loop)

Examples:
  node quote0.js text --message "Hello\nWorld"
  node quote0.js image --imageFile ./card.png --ditherType NONE
  node quote0.js devices
  node quote0.js status --deviceId ABCD1234ABCD
`);
}

function request({ method, path: requestPath, apiKey, body }) {
  return new Promise((resolve, reject) => {
    const options = {
      method,
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
    };

    const req = https.request(`${API_BASE}${requestPath}`, options, (res) => {
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => {
        const ok = res.statusCode >= 200 && res.statusCode < 300;
        if (ok) {
          try {
            resolve(JSON.parse(data));
          } catch {
            resolve(data);
          }
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data}`));
        }
      });
    });

    req.on('error', reject);
    if (body !== undefined) req.write(JSON.stringify(body));
    req.end();
  });
}

function needApiKey(args) {
  const apiKey = args.apiKey || process.env.DOT_API_KEY;
  if (!apiKey) {
    throw new Error('缺少 API Key：请传 --apiKey 或设置环境变量 DOT_API_KEY');
  }
  return apiKey;
}

function needDeviceId(args) {
  const deviceId = args.deviceId || process.env.DOT_DEVICE_ID;
  if (!deviceId) {
    throw new Error('缺少设备 ID：请传 --deviceId 或设置环境变量 DOT_DEVICE_ID');
  }
  return deviceId;
}

function isPngBuffer(buf) {
  if (!Buffer.isBuffer(buf) || buf.length < PNG_MAGIC.length) return false;
  return buf.subarray(0, PNG_MAGIC.length).equals(PNG_MAGIC);
}

function readImageBase64(args) {
  if (args.image) return args.image;

  if (args.imageFile) {
    const filePath = path.resolve(args.imageFile);
    const st = fs.statSync(filePath);
    if (!st.isFile()) {
      throw new Error(`imageFile 不是普通文件: ${filePath}`);
    }

    if (path.extname(filePath).toLowerCase() !== '.png') {
      throw new Error(`imageFile 必须是 .png 文件: ${filePath}`);
    }

    if (st.size > MAX_IMAGE_BYTES) {
      throw new Error(`imageFile 过大（>${MAX_IMAGE_BYTES} bytes）: ${filePath}`);
    }

    const buf = fs.readFileSync(filePath);
    if (!isPngBuffer(buf)) {
      throw new Error(`imageFile 不是有效 PNG 文件: ${filePath}`);
    }

    return buf.toString('base64');
  }

  throw new Error('image 命令需要 --image 或 --imageFile');
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const cmd = args._[0];

  if (!cmd || args.help || args.h) {
    printHelp();
    process.exit(0);
  }

  const apiKey = needApiKey(args);

  switch (cmd) {
    case 'devices': {
      const result = await request({ method: 'GET', path: '/devices', apiKey });
      console.log(JSON.stringify(result, null, 2));
      return;
    }

    case 'status': {
      const deviceId = needDeviceId(args);
      const result = await request({ method: 'GET', path: `/device/${deviceId}/status`, apiKey });
      console.log(JSON.stringify(result, null, 2));
      return;
    }

    case 'next': {
      const deviceId = needDeviceId(args);
      const result = await request({ method: 'POST', path: `/device/${deviceId}/next`, apiKey });
      console.log(JSON.stringify(result, null, 2));
      return;
    }

    case 'list': {
      const deviceId = needDeviceId(args);
      const taskType = args.taskType || 'loop';
      const result = await request({ method: 'GET', path: `/device/${deviceId}/${taskType}/list`, apiKey });
      console.log(JSON.stringify(result, null, 2));
      return;
    }

    case 'text': {
      const deviceId = needDeviceId(args);
      if (!args.message) throw new Error('text 命令需要 --message');

      const payload = {
        refreshNow: toBool(args.refresh, true),
        title: args.title || 'Clawdbot',
        message: args.message,
        signature: args.signature || nowSignature(),
      };
      if (args.icon) payload.icon = args.icon;
      if (args.link) payload.link = args.link;
      if (args.taskKey) payload.taskKey = args.taskKey;

      const result = await request({
        method: 'POST',
        path: `/device/${deviceId}/text`,
        apiKey,
        body: payload,
      });
      console.log(JSON.stringify(result, null, 2));
      return;
    }

    case 'image': {
      const deviceId = needDeviceId(args);
      const payload = {
        refreshNow: toBool(args.refresh, true),
        image: readImageBase64(args),
        border: args.border !== undefined ? Number(args.border) : 0,
      };
      if (args.link) payload.link = args.link;
      if (args.ditherType) payload.ditherType = args.ditherType;
      if (args.ditherKernel) payload.ditherKernel = args.ditherKernel;
      if (args.taskKey) payload.taskKey = args.taskKey;

      const result = await request({
        method: 'POST',
        path: `/device/${deviceId}/image`,
        apiKey,
        body: payload,
      });
      console.log(JSON.stringify(result, null, 2));
      return;
    }

    default:
      throw new Error(`未知命令: ${cmd}`);
  }
}

main().catch((err) => {
  console.error('Error:', err.message || err);
  process.exit(1);
});
