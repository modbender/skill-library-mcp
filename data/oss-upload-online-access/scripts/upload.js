#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');
const { URL } = require('url');

const MAX_SIZE = 100 * 1024 * 1024; // 100MB
const SKILL_ROOT = path.resolve(__dirname, '..');
const CONFIG_PATH = path.join(SKILL_ROOT, 'config.json');
const DIR_PREFIX = 'skill';

function getObjectDir(filename) {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, '0');
  const d = String(now.getDate()).padStart(2, '0');
  const ext = (path.extname(filename) || '').slice(1).toLowerCase() || 'other';
  return `${DIR_PREFIX}/${y}/${m}/${d}/${ext}`;
}

const TEXT_EXT = new Set([
  'txt', 'text', 'log', 'md', 'markdown', 'html', 'htm', 'json', 'xml', 'csv', 'css', 'js', 'ts', 'tsx', 'mjs', 'cjs', 'jsx',
  'yaml', 'yml', 'ini', 'conf', 'cfg', 'sh', 'bash', 'bat', 'cmd', 'py', 'rb', 'go', 'rs', 'vue', 'svelte', 'map',
  'scss', 'sass', 'less', 'styl', 'coffee', 'lua', 'php', 'pl', 'pm', 'r', 'scala', 'swift', 'kt', 'kts', 'java', 'c', 'cpp', 'cc', 'cxx', 'h', 'hpp', 'hxx',
  'vb', 'vbs', 'ps1', 'psd1', 'psm1', 'rkt', 'lisp', 'clj', 'cljs', 'edn', 'ex', 'exs', 'elm', 'fs', 'fsx', 'fsi',
  'toml', 'rst', 'adoc', 'asciidoc', 'tex', 'latex', 'bib', 'nfo', 'me', 'env', 'lock', 'gitignore', 'dockerignore', 'editorconfig',
  'graphql', 'gql', 'sql', 'proto', 'thrift', 'avsc', 'raml',
  'srt', 'vtt', 'ass', 'ssa', 'm3u', 'm3u8', 'pls',
]);

const MIME_MAP = {
  // ========== 文本 / 源码 ==========
  md: 'text/markdown; charset=UTF-8',
  markdown: 'text/markdown; charset=UTF-8',
  txt: 'text/plain; charset=UTF-8',
  text: 'text/plain; charset=UTF-8',
  log: 'text/plain; charset=UTF-8',
  html: 'text/html; charset=UTF-8',
  htm: 'text/html; charset=UTF-8',
  json: 'application/json; charset=UTF-8',
  xml: 'application/xml; charset=UTF-8',
  csv: 'text/csv; charset=UTF-8',
  css: 'text/css; charset=UTF-8',
  js: 'application/javascript; charset=UTF-8',
  mjs: 'application/javascript; charset=UTF-8',
  cjs: 'application/javascript; charset=UTF-8',
  jsx: 'text/jsx; charset=UTF-8',
  ts: 'application/typescript; charset=UTF-8',
  tsx: 'text/tsx; charset=UTF-8',
  yaml: 'text/yaml; charset=UTF-8',
  yml: 'text/yaml; charset=UTF-8',
  ini: 'text/plain; charset=UTF-8',
  conf: 'text/plain; charset=UTF-8',
  cfg: 'text/plain; charset=UTF-8',
  toml: 'application/toml; charset=UTF-8',
  rst: 'text/x-rst; charset=UTF-8',
  adoc: 'text/plain; charset=UTF-8',
  asciidoc: 'text/plain; charset=UTF-8',
  tex: 'application/x-tex; charset=UTF-8',
  latex: 'application/x-latex; charset=UTF-8',
  bib: 'application/x-bibtex; charset=UTF-8',
  scss: 'text/x-scss; charset=UTF-8',
  sass: 'text/x-sass; charset=UTF-8',
  less: 'text/x-less; charset=UTF-8',
  styl: 'text/x-stylus; charset=UTF-8',
  coffee: 'text/plain; charset=UTF-8',
  lua: 'text/x-lua; charset=UTF-8',
  php: 'text/x-php; charset=UTF-8',
  pl: 'text/x-perl; charset=UTF-8',
  pm: 'text/x-perl; charset=UTF-8',
  r: 'text/x-r; charset=UTF-8',
  scala: 'text/x-scala; charset=UTF-8',
  swift: 'text/x-swift; charset=UTF-8',
  kt: 'text/x-kotlin; charset=UTF-8',
  kts: 'text/x-kotlin; charset=UTF-8',
  java: 'text/x-java-source; charset=UTF-8',
  c: 'text/x-c; charset=UTF-8',
  cpp: 'text/x-c++; charset=UTF-8',
  cc: 'text/x-c++; charset=UTF-8',
  cxx: 'text/x-c++; charset=UTF-8',
  h: 'text/x-c; charset=UTF-8',
  hpp: 'text/x-c++; charset=UTF-8',
  hxx: 'text/x-c++; charset=UTF-8',
  vb: 'text/x-vb; charset=UTF-8',
  vbs: 'text/vbscript; charset=UTF-8',
  ps1: 'text/plain; charset=UTF-8',
  psd1: 'text/plain; charset=UTF-8',
  psm1: 'text/plain; charset=UTF-8',
  sql: 'application/sql; charset=UTF-8',
  graphql: 'application/graphql; charset=UTF-8',
  gql: 'application/graphql; charset=UTF-8',
  proto: 'text/plain; charset=UTF-8',
  thrift: 'application/x-thrift; charset=UTF-8',
  raml: 'application/raml+yaml; charset=UTF-8',
  avsc: 'application/json; charset=UTF-8',
  srt: 'text/plain; charset=UTF-8',
  vtt: 'text/vtt; charset=UTF-8',
  ass: 'text/x-ssa; charset=UTF-8',
  ssa: 'text/x-ssa; charset=UTF-8',
  m3u: 'audio/x-mpegurl; charset=UTF-8',
  m3u8: 'application/vnd.apple.mpegurl; charset=UTF-8',
  pls: 'audio/x-scpls; charset=UTF-8',
  sh: 'application/x-sh; charset=UTF-8',
  bat: 'text/plain; charset=UTF-8',
  cmd: 'text/plain; charset=UTF-8',
  map: 'application/json; charset=UTF-8',
  // ========== 文档 ==========
  pdf: 'application/pdf',
  doc: 'application/msword',
  docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  xls: 'application/vnd.ms-excel',
  xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  ppt: 'application/vnd.ms-powerpoint',
  pptx: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  odt: 'application/vnd.oasis.opendocument.text',
  ods: 'application/vnd.oasis.opendocument.spreadsheet',
  odp: 'application/vnd.oasis.opendocument.presentation',
  odb: 'application/vnd.oasis.opendocument.database',
  odf: 'application/vnd.oasis.opendocument.formula',
  odg: 'application/vnd.oasis.opendocument.graphics',
  odm: 'application/vnd.oasis.opendocument.text-master',
  odc: 'application/vnd.oasis.opendocument.chart',
  odi: 'application/vnd.oasis.opendocument.image',
  rtf: 'application/rtf',
  epub: 'application/epub+zip',
  mobi: 'application/x-mobipocket-ebook',
  azw: 'application/vnd.amazon.ebook',
  azw3: 'application/vnd.amazon.ebook',
  djvu: 'image/vnd.djvu',
  xps: 'application/vnd.ms-xpsdocument',
  oxps: 'application/oxps',
  pages: 'application/vnd.apple.pages',
  numbers: 'application/vnd.apple.numbers',
  key: 'application/vnd.apple.keynote',
  vsd: 'application/vnd.visio',
  vsdx: 'application/vnd.visio',
  fb2: 'application/xml',
  // ========== 图片 ==========
  png: 'image/png',
  jpg: 'image/jpeg',
  jpeg: 'image/jpeg',
  gif: 'image/gif',
  webp: 'image/webp',
  svg: 'image/svg+xml',
  bmp: 'image/bmp',
  ico: 'image/x-icon',
  tiff: 'image/tiff',
  tif: 'image/tiff',
  heic: 'image/heic',
  heif: 'image/heif',
  avif: 'image/avif',
  jfif: 'image/jpeg',
  jxr: 'image/jxr',
  jxra: 'image/jxra',
  apng: 'image/apng',
  ps: 'application/postscript',
  eps: 'application/postscript',
  xcf: 'image/x-xcf',
  psd: 'image/vnd.adobe.photoshop',
  ai: 'application/postscript',
  raw: 'image/x-raw',
  arw: 'image/x-raw',
  cr2: 'image/x-raw',
  nef: 'image/x-raw',
  orf: 'image/x-raw',
  dng: 'image/x-adobe-dng',
  // ========== 视频 ==========
  mp4: 'video/mp4',
  m4v: 'video/mp4',
  webm: 'video/webm',
  mov: 'video/quicktime',
  avi: 'video/x-msvideo',
  mkv: 'video/x-matroska',
  wmv: 'video/x-ms-wmv',
  flv: 'video/x-flv',
  f4v: 'video/x-f4v',
  '3gp': 'video/3gpp',
  '3g2': 'video/3gpp2',
  mpeg: 'video/mpeg',
  mpg: 'video/mpeg',
  mpe: 'video/mpeg',
  m2v: 'video/mpeg',
  mts: 'video/mp2t',
  m2ts: 'video/mp2t',
  ogv: 'video/ogg',
  vob: 'video/dvd',
  divx: 'video/x-msvideo',
  // ========== 音频 ==========
  mp3: 'audio/mpeg',
  wav: 'audio/wav',
  ogg: 'audio/ogg',
  oga: 'audio/ogg',
  opus: 'audio/opus',
  m4a: 'audio/mp4',
  aac: 'audio/aac',
  flac: 'audio/flac',
  weba: 'audio/webm',
  wma: 'audio/x-ms-wma',
  mid: 'audio/midi',
  midi: 'audio/midi',
  aiff: 'audio/aiff',
  aif: 'audio/aiff',
  aifc: 'audio/aiff',
  amr: 'audio/amr',
  au: 'audio/basic',
  snd: 'audio/basic',
  ra: 'audio/vnd.rn-realaudio',
  ram: 'audio/x-pn-realaudio',
  mka: 'audio/x-matroska',
  ac3: 'audio/ac3',
  eac3: 'audio/eac3',
  spx: 'audio/ogg',
  voc: 'audio/x-voc',
  // ========== 字体 ==========
  ttf: 'font/ttf',
  otf: 'font/otf',
  woff: 'font/woff',
  woff2: 'font/woff2',
  eot: 'application/vnd.ms-fontobject',
  // ========== 压缩 / 归档 ==========
  zip: 'application/zip',
  rar: 'application/x-rar-compressed',
  '7z': 'application/x-7z-compressed',
  tar: 'application/x-tar',
  gz: 'application/gzip',
  bz2: 'application/x-bzip2',
  xz: 'application/x-xz',
  zst: 'application/zstd',
  lz: 'application/x-lzma',
  lzma: 'application/x-lzma',
  lz4: 'application/x-lz4',
  tgz: 'application/gzip',
  tbz2: 'application/x-bzip2',
  txz: 'application/x-xz',
  cab: 'application/vnd.ms-cab-compressed',
  cpio: 'application/x-cpio',
  ar: 'application/x-unix-archive',
  deb: 'application/vnd.debian.binary-package',
  rpm: 'application/x-rpm',
  z: 'application/x-compress',
  lzh: 'application/x-lzh-compressed',
  lha: 'application/x-lzh-compressed',
  cbr: 'application/x-cbr',
  cbz: 'application/zip',
  cbt: 'application/x-cbt',
  cb7: 'application/x-7z-compressed',
  sit: 'application/x-stuffit',
  sitx: 'application/x-stuffitx',
  // ========== 3D / 模型 / CAD ==========
  glb: 'model/gltf-binary',
  gltf: 'model/gltf+json',
  obj: 'model/obj',
  stl: 'model/stl',
  '3ds': 'image/x-3ds',
  dae: 'model/vnd.collada+xml',
  fbx: 'application/octet-stream',
  blend: 'application/octet-stream',
  step: 'model/step',
  stp: 'model/step',
  iges: 'model/iges',
  igs: 'model/iges',
  // ========== 证书 / 密钥 ==========
  pem: 'application/x-pem-file',
  crt: 'application/x-x509-ca-cert',
  cer: 'application/x-x509-ca-cert',
  der: 'application/x-x509-ca-cert',
  p12: 'application/x-pkcs12',
  pfx: 'application/x-pkcs12',
  key: 'application/x-pem-file',
  p7b: 'application/x-pkcs7-certificates',
  p7c: 'application/pkcs7-mime',
  // ========== 安装包 / 可执行 ==========
  exe: 'application/x-msdownload',
  msi: 'application/x-msi',
  dmg: 'application/x-apple-diskimage',
  pkg: 'application/x-apple-diskimage',
  apk: 'application/vnd.android.package-archive',
  aab: 'application/x-authorware-bin',
  iso: 'application/x-iso9660-image',
  img: 'application/octet-stream',
  run: 'application/x-executable',
  // ========== 其他常见 ==========
  wasm: 'application/wasm',
  swf: 'application/x-shockwave-flash',
  torrent: 'application/x-bittorrent',
  crx: 'application/x-chrome-extension',
  xpi: 'application/x-xpinstall',
  bin: 'application/octet-stream',
  dat: 'application/octet-stream',
  avro: 'application/avro',
};

function getContentType(filename) {
  const ext = (path.extname(filename) || '').slice(1).toLowerCase();
  return MIME_MAP[ext] || 'application/octet-stream';
}

function removeSpecialChars(str) {
  return String(str || '').replace(/[^\w\s\-\.]/g, '');
}

function extractDomain(url) {
  const m = url.match(/^(https?:\/\/[^/]+)/);
  return m ? m[1] : null;
}

/**
 * 生成仅含字母与数字且不重复的文件名：3 位随机小写字母 + 时间戳 + 6 位随机数字 + 扩展名
 * 格式：abc + YYYYMMDDHHmmss + 123456 + .ext
 */
function alphanumericUniqueFilename(original) {
  const extRaw = (path.extname(original) || '').slice(1).toLowerCase();
  const ext = extRaw.replace(/[^a-z0-9]/g, '') || 'bin';
  const ts = new Date().toISOString().replace(/[-:T.Z]/g, '').slice(0, 14);
  const letters = 'abcdefghijklmnopqrstuvwxyz';
  let prefix = '';
  for (let i = 0; i < 3; i++) prefix += letters[Math.floor(Math.random() * letters.length)];
  let suffix = '';
  for (let i = 0; i < 6; i++) suffix += Math.floor(Math.random() * 10);
  return `${prefix}${ts}${suffix}.${ext}`;
}

/**
 * Resolve config with priority:
 * 1. Environment variables (injected by OpenClaw/ClawHub platform)
 * 2. Local config.json (for local / self-hosted use)
 *
 * Aliyun env vars: OSS_ALIYUN_REGION, OSS_ALIYUN_BUCKET,
 *   OSS_ALIYUN_ACCESS_KEY_ID, OSS_ALIYUN_ACCESS_KEY_SECRET,
 *   OSS_ALIYUN_ENDPOINT (optional), OSS_ALIYUN_CUSTOM_DOMAIN (optional)
 * Tencent env vars: OSS_TENCENT_BUCKET, OSS_TENCENT_REGION,
 *   OSS_TENCENT_SECRET_ID, OSS_TENCENT_SECRET_KEY,
 *   OSS_TENCENT_ACCELERATED_DOMAIN (optional)
 */
function resolveConfig() {
  const aliyunEnv = {
    region: (process.env.OSS_ALIYUN_REGION || '').trim(),
    bucket: (process.env.OSS_ALIYUN_BUCKET || '').trim(),
    accessKeyId: (process.env.OSS_ALIYUN_ACCESS_KEY_ID || '').trim(),
    accessKeySecret: (process.env.OSS_ALIYUN_ACCESS_KEY_SECRET || '').trim(),
    endpoint: (process.env.OSS_ALIYUN_ENDPOINT || '').trim(),
    customDomain: (process.env.OSS_ALIYUN_CUSTOM_DOMAIN || '').trim(),
  };
  const tencentEnv = {
    bucket: (process.env.OSS_TENCENT_BUCKET || '').trim(),
    region: (process.env.OSS_TENCENT_REGION || '').trim(),
    secretId: (process.env.OSS_TENCENT_SECRET_ID || '').trim(),
    secretKey: (process.env.OSS_TENCENT_SECRET_KEY || '').trim(),
    acceleratedDomain: (process.env.OSS_TENCENT_ACCELERATED_DOMAIN || '').trim(),
    storageClass: (process.env.OSS_TENCENT_STORAGE_CLASS || '').trim(),
  };

  const hasAliyunEnv = !!(aliyunEnv.region && aliyunEnv.bucket && aliyunEnv.accessKeyId && aliyunEnv.accessKeySecret);
  const hasTencentEnv = !!(tencentEnv.bucket && tencentEnv.region && tencentEnv.secretId && tencentEnv.secretKey);

  if (hasAliyunEnv || hasTencentEnv) {
    return { aliyun: aliyunEnv, tencent: tencentEnv };
  }

  // Fallback to local config.json
  if (!fs.existsSync(CONFIG_PATH)) {
    console.error('错误：未找到有效配置。请在 OpenClaw Skills 配置页面填入环境变量，或本地复制 config.example.json 为 config.json 并填入配置。');
    process.exit(1);
  }
  const raw = fs.readFileSync(CONFIG_PATH, 'utf8');
  try {
    const cfg = JSON.parse(raw);
    delete cfg._comments;
    return cfg;
  } catch (e) {
    console.error('错误：config.json 格式无效。');
    process.exit(1);
  }
}

function isAliyunConfigured(cfg) {
  const a = cfg.aliyun || {};
  return !!(a.region && a.bucket && a.accessKeyId && a.accessKeySecret);
}

function isTencentConfigured(cfg) {
  const t = cfg.tencent || {};
  return !!(t.bucket && t.region && t.secretId && t.secretKey);
}

function selectProvider(cfg, userProvider) {
  if (userProvider) {
    const p = userProvider.toLowerCase();
    if (p === 'aliyun' && isAliyunConfigured(cfg)) return 'aliyun';
    if (p === 'tencent' && isTencentConfigured(cfg)) return 'tencent';
    console.error(`错误：用户指定了 ${userProvider}，但该云厂商配置不完整。请在 OpenClaw Skills 配置页面填入对应环境变量，或检查 config.json。`);
    process.exit(1);
  }
  if (isAliyunConfigured(cfg)) return 'aliyun';
  if (isTencentConfigured(cfg)) return 'tencent';
  console.error('错误：未找到有效配置。请至少配置阿里云或腾讯云（env var 或 config.json），并填写 region、bucket、accessKeyId、accessKeySecret（或 secretId、secretKey）。');
  process.exit(1);
}

/**
 * 校验 URL 是否可访问（HEAD 请求，2xx 视为成功；跟随一次 3xx 重定向）
 * @param {string} url
 * @param {number} [redirectsLeft=1]
 * @returns {Promise<boolean>}
 */
function verifyUrlAccessible(url, redirectsLeft = 1) {
  if (!url || !url.startsWith('http')) return Promise.resolve(false);
  return new Promise((resolve) => {
    const parsed = new URL(url);
    const client = parsed.protocol === 'https:' ? https : http;
    const opts = { method: 'HEAD', timeout: 15000 };
    const req = client.request(url, opts, (res) => {
      if (res.statusCode >= 200 && res.statusCode < 300) {
        return resolve(true);
      }
      if (redirectsLeft > 0 && res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        const next = res.headers.location;
        return verifyUrlAccessible(next.startsWith('http') ? next : new URL(next, url).href, redirectsLeft - 1).then(resolve);
      }
      resolve(false);
    });
    req.on('error', () => resolve(false));
    req.on('timeout', () => {
      req.destroy();
      resolve(false);
    });
    req.end();
  });
}

function getBufferFromUrl(url) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(url);
    const client = parsed.protocol === 'https:' ? https : http;
    client.get(url, { timeout: 60000 }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return getBufferFromUrl(res.headers.location).then(resolve).catch(reject);
      }
      const chunks = [];
      let size = 0;
      res.on('data', (chunk) => {
        size += chunk.length;
        if (size > MAX_SIZE) {
          res.destroy();
          reject(new Error('文件超过 100MB 限制'));
          return;
        }
        chunks.push(chunk);
      });
      res.on('end', () => resolve(Buffer.concat(chunks)));
      res.on('error', reject);
    }).on('error', reject);
  });
}

async function uploadAliyun(buffer, filename, cfg) {
  const ALIOSS = require('ali-oss');
  const a = cfg.aliyun || {};
  const bucket = removeSpecialChars(a.bucket);
  let region = removeSpecialChars(a.region);
  if (region === 'oss-accelerate') {
    console.error('错误：region 不能填 oss-accelerate，请填 bucket 实际地域（如 oss-cn-shenzhen）。传输加速用 endpoint 配置。');
    process.exit(1);
  }
  const clientOpts = {
    region,
    accessKeyId: a.accessKeyId,
    accessKeySecret: a.accessKeySecret,
    bucket,
    secure: true,
  };
  if (a.endpoint) {
    clientOpts.endpoint = a.endpoint.trim();
  }
  const client = new ALIOSS(clientOpts);
  const dir = getObjectDir(filename);
  const key = `${dir}/${filename}`;
  await client.put(key, buffer, {
    timeout: 600000,
    headers: {
      'content-type': getContentType(filename),
      'x-oss-object-acl': 'public-read',
    },
  });
  try {
    await client.head(key);
  } catch (e) {
    throw new Error('上传后校验失败：对象在 OSS 上不存在，请检查 bucket/region/endpoint 配置。');
  }
  let url = client._objectUrl(key);
  if (url && url.startsWith('http://')) {
    url = url.replace(/^http:\/\//, 'https://');
  }
  if (a.customDomain) {
    const d = extractDomain(url);
    if (d) url = url.replace(d, a.customDomain.replace(/\/$/, ''));
  }
  return url;
}

function uploadTencent(buffer, filename, cfg) {
  return new Promise((resolve, reject) => {
    const COS = require('cos-nodejs-sdk-v5');
    const t = cfg.tencent || {};
    const bucket = removeSpecialChars(t.bucket);
    const region = removeSpecialChars(t.region);
    const cos = new COS({
      SecretId: t.secretId,
      SecretKey: t.secretKey,
      FileParallelLimit: 10,
      Timeout: 600000,
    });
    const dir = getObjectDir(filename);
    const key = `${dir}/${filename}`;
    const putParams = {
      Bucket: bucket,
      Region: region,
      Key: key,
      Body: buffer,
      ContentType: getContentType(filename),
      ACL: 'public-read',
    };
    if (t.storageClass) putParams.StorageClass = t.storageClass;
    cos.putObject(
      putParams,
      (err, data) => {
        if (err) return reject(err);
        cos.headObject(
          { Bucket: bucket, Region: region, Key: key },
          (headErr) => {
            if (headErr) {
              return reject(new Error('上传后校验失败：对象在 COS 上不存在，请检查 Bucket/Region 配置。'));
            }
            let url = (data.Location || '').replace(/^(http:\/\/|https:\/\/|\/\/|)(.*)/, 'https://$2');
            if (t.acceleratedDomain) {
              url = url.replace(/^(https:\/\/[^/]+)(\/.*)$/, `https://${t.acceleratedDomain}$2`);
            }
            resolve(url);
          }
        );
      }
    );
  });
}

async function main() {
  const args = process.argv.slice(2);
  let input = null;
  let provider = null;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--provider' && args[i + 1]) {
      provider = args[i + 1];
      i++;
    } else if (!input) {
      input = args[i];
    }
  }

  if (!input) {
    console.error('用法: node scripts/upload.js <本地路径或URL> [--provider aliyun|tencent]');
    process.exit(1);
  }

  const cfg = resolveConfig();
  const chosen = selectProvider(cfg, provider);

  let buffer;
  let suggestedFilename;

  if (/^https?:\/\//i.test(input)) {
    try {
      buffer = await getBufferFromUrl(input);
    } catch (e) {
      console.error('下载失败:', e.message || e);
      process.exit(1);
    }
    try {
      const u = new URL(input);
      suggestedFilename = path.basename(u.pathname) || 'download';
      if (!path.extname(suggestedFilename)) suggestedFilename += '.bin';
    } catch {
      suggestedFilename = `download_${Date.now()}.bin`;
    }
  } else {
    const fp = path.isAbsolute(input) ? input : path.resolve(process.cwd(), input);
    if (!fs.existsSync(fp)) {
      console.error('错误：文件不存在:', fp);
      process.exit(1);
    }
    const stat = fs.statSync(fp);
    if (!stat.isFile()) {
      console.error('错误：不是文件:', fp);
      process.exit(1);
    }
    if (stat.size > MAX_SIZE) {
      console.error('错误：文件超过 100MB 限制');
      process.exit(1);
    }
    const ext = (path.extname(fp) || '').slice(1).toLowerCase();
    if (TEXT_EXT.has(ext)) {
      const raw = fs.readFileSync(fp, 'utf8');
      buffer = Buffer.from(raw, 'utf8');
    } else {
      buffer = fs.readFileSync(fp);
    }
    suggestedFilename = path.basename(fp);
  }

  const filename = alphanumericUniqueFilename(suggestedFilename);

  try {
    let url;
    if (chosen === 'aliyun') {
      url = await uploadAliyun(buffer, filename, cfg);
    } else {
      url = await uploadTencent(buffer, filename, cfg);
    }
    const accessible = await verifyUrlAccessible(url);
    if (!accessible) {
      console.error('上传后校验失败：链接不可访问，无法提供有效链接。请检查存储桶权限、ACL 或网络。');
      process.exit(1);
    }
    console.log(url);
  } catch (e) {
    // 仅输出通用错误信息，绝不泄露配置、凭证或堆栈
    console.error('上传失败，请检查网络连接或凭证配置（OSS_ALIYUN_* / OSS_TENCENT_* 环境变量，或 config.json）是否正确。');
    process.exit(1);
  }
}

main();
