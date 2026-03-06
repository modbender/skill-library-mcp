#!/usr/bin/env node
/**
 * mk-banner.js — 매경 1면 이미지 다운로드 + 1150x630 배너 크롭
 * 
 * Usage:
 *   node mk-banner.js              # 오늘 날짜
 *   node mk-banner.js 2026-02-21   # 특정 날짜
 * 
 * Output:
 *   /tmp/mk-banner-YYYY-MM-DD.jpg  (1150x630)
 *   stdout에 출력 파일 경로 출력
 * 
 * Dependencies:
 *   sharp (OpenClaw 내장)
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

// OpenClaw 내장 sharp 사용
let sharp;
try {
  sharp = require('sharp');
} catch {
  try {
    sharp = require('/opt/homebrew/lib/node_modules/openclaw/node_modules/sharp');
  } catch (e) {
    console.error('❌ sharp 모듈을 찾을 수 없습니다. npm install sharp 실행 필요.');
    process.exit(1);
  }
}

// ── Config ──────────────────────────────────────────────────
const BANNER_WIDTH = 1150;
const BANNER_HEIGHT = 630;
const MK_URL_PATTERN = 'https://file2.mk.co.kr/mkde/{YYYY}/{MM}/{DD}/page/01_01_ORG.jpg';
const OUTPUT_DIR = '/tmp';

// Border (best-practice look)
const DEFAULT_BORDER = { enabled: true, size: 2, color: '#D0D0D0' }; // light gray

// ── Helpers ─────────────────────────────────────────────────

function getDateStr(dateArg) {
  const d = dateArg ? new Date(dateArg + 'T00:00:00+09:00') : new Date();
  const yyyy = d.getFullYear().toString();
  const mm = (d.getMonth() + 1).toString().padStart(2, '0');
  const dd = d.getDate().toString().padStart(2, '0');
  return { yyyy, mm, dd };
}

function buildUrl(yyyy, mm, dd) {
  return MK_URL_PATTERN
    .replace('{YYYY}', yyyy)
    .replace('{MM}', mm)
    .replace('{DD}', dd);
}

function download(url) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    client.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return download(res.headers.location).then(resolve).catch(reject);
      }
      if (res.statusCode !== 200) {
        return reject(new Error(`HTTP ${res.statusCode} for ${url}`));
      }
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => resolve(Buffer.concat(chunks)));
      res.on('error', reject);
    }).on('error', reject);
  });
}

async function cropBanner(inputBuffer, width, height, border = DEFAULT_BORDER) {
  const meta = await sharp(inputBuffer).metadata();

  // 원본 비율 유지하면서 target 비율에 맞게 center crop
  const targetRatio = width / height;
  const srcRatio = meta.width / meta.height;

  let cropWidth, cropHeight, left, top;

  if (srcRatio > targetRatio) {
    // 원본이 더 넓음 → 좌우 크롭
    cropHeight = meta.height;
    cropWidth = Math.round(meta.height * targetRatio);
    left = Math.round((meta.width - cropWidth) / 2);
    top = 0;
  } else {
    // 원본이 더 높음 → 상단 기준 크롭 (신문 헤더가 위에 있으므로 top=0)
    cropWidth = meta.width;
    cropHeight = Math.round(meta.width / targetRatio);
    left = 0;
    top = 0; // 상단 기준
  }

  // Perform crop first, then resize to exact target
  let pipeline = sharp(inputBuffer)
    .extract({ left, top, width: cropWidth, height: cropHeight })
    .resize(width, height);

  // Add border (light gray) for best-practice look
  if (border?.enabled) {
    // Create a border overlay as SVG sized to final image
    const b = Math.max(1, border.size || 2);
    const svg = Buffer.from(
      `<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
        <rect x="${b/2}" y="${b/2}" width="${width - b}" height="${height - b}" fill="none" stroke="${border.color || '#D0D0D0'}" stroke-width="${b}"/>
      </svg>`
    );

    pipeline = pipeline.composite([{ input: svg, top: 0, left: 0 }]);
  }

  return pipeline
    .jpeg({ quality: 90 })
    .toBuffer();
}

// addBorder() 제거됨 — 테두리는 cropBanner() 내 SVG 오버레이로 처리 (1150x630 고정)

function copyToClipboard(filePath) {
  const { execSync } = require('child_process');
  // macOS: osascript로 이미지를 클립보드에 복사
  const absPath = path.resolve(filePath);
  const script = `set the clipboard to (read (POSIX file "${absPath}") as JPEG picture)`;
  execSync(`osascript -e '${script}'`);
}

// ── Main ────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const clipboard = args.includes('--clipboard') || args.includes('-c');
  const noBorder = args.includes('--no-border');
  const dateArg = args.find(a => !a.startsWith('-'));
  const { yyyy, mm, dd } = getDateStr(dateArg);
  const url = buildUrl(yyyy, mm, dd);
  const outputPath = path.join(OUTPUT_DIR, `mk-banner-${yyyy}-${mm}-${dd}.jpg`);
  
  console.error(`📥 다운로드: ${url}`);
  
  let buffer;
  try {
    buffer = await download(url);
  } catch (e) {
    console.error(`❌ 다운로드 실패: ${e.message}`);
    process.exit(1);
  }
  
  console.error(`📐 크롭: ${BANNER_WIDTH}x${BANNER_HEIGHT}`);
  const border = noBorder ? { ...DEFAULT_BORDER, enabled: false } : DEFAULT_BORDER;
  let banner = await cropBanner(buffer, BANNER_WIDTH, BANNER_HEIGHT, border);
  
  fs.writeFileSync(outputPath, banner);
  console.error(`✅ 저장: ${outputPath} (${(banner.length / 1024).toFixed(1)}KB)`);
  
  if (clipboard) {
    try {
      copyToClipboard(outputPath);
      console.error(`📋 클립보드 복사 완료`);
    } catch (e) {
      console.error(`⚠️ 클립보드 복사 실패: ${e.message}`);
    }
  }
  
  // stdout에 경로만 출력 (파이프 용도)
  console.log(outputPath);
}

main().catch((e) => {
  console.error(`❌ 에러: ${e.message}`);
  process.exit(1);
});
