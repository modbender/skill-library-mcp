/**
 * common.js - Korean Scraper 공통 유틸리티
 */

const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();

// Stealth 플러그인 적용
chromium.use(stealth);

/**
 * Anti-bot 설정이 적용된 브라우저 생성
 */
async function createStealthBrowser(options = {}) {
  const headless = process.env.HEADLESS !== 'false';
  
  const browser = await chromium.launch({
    headless,
    args: [
      '--disable-blink-features=AutomationControlled',
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-web-security',
      '--disable-features=IsolateOrigins,site-per-process'
    ]
  });

  const context = await browser.newContext({
    userAgent: options.userAgent || getRandomUserAgent(),
    viewport: { width: 1920, height: 1080 },
    locale: 'ko-KR',
    timezoneId: 'Asia/Seoul',
    extraHTTPHeaders: {
      'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    }
  });

  // navigator.webdriver 제거
  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    });
    
    // Chrome detection 우회
    window.chrome = {
      runtime: {}
    };
    
    // Permissions API 우회
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
      parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
    );
  });

  return { browser, context };
}

/**
 * 랜덤 User-Agent 생성 (한국 사용자 기준)
 */
function getRandomUserAgent() {
  const userAgents = [
    // Desktop Chrome (Windows)
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    // Desktop Chrome (Mac)
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    // Mobile Chrome (Android)
    'Mozilla/5.0 (Linux; Android 13; SM-S901N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    // Mobile Safari (iPhone)
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1'
  ];
  
  return userAgents[Math.floor(Math.random() * userAgents.length)];
}

/**
 * 인간처럼 랜덤 딜레이
 */
async function humanDelay(minMs = 1000, maxMs = 3000) {
  const delay = Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
  await new Promise(resolve => setTimeout(resolve, delay));
}

/**
 * 스크롤 다운 (무한 스크롤 대응)
 */
async function scrollDown(page, times = 3) {
  for (let i = 0; i < times; i++) {
    await page.evaluate(() => {
      window.scrollBy(0, window.innerHeight);
    });
    await humanDelay(500, 1500);
  }
}

/**
 * 텍스트 정제 (공백, 개행 정리)
 */
function cleanText(text) {
  if (!text) return '';
  return text
    .replace(/\s+/g, ' ')
    .replace(/\n+/g, '\n')
    .trim();
}

/**
 * JSON 출력 (stdout)
 */
function outputJSON(data) {
  console.log(JSON.stringify(data, null, 2));
}

/**
 * 에러 JSON 출력
 */
function outputError(message, details = {}) {
  outputJSON({
    status: 'error',
    message,
    ...details
  });
}

/**
 * 성공 JSON 출력
 */
function outputSuccess(data) {
  outputJSON({
    status: 'success',
    ...data
  });
}

/**
 * 스크린샷 저장 (디버깅용)
 */
async function saveScreenshot(page, filename) {
  if (process.env.SCREENSHOT === 'true') {
    await page.screenshot({ path: filename, fullPage: true });
    console.error(`Screenshot saved: ${filename}`);
  }
}

/**
 * Rate limiting (동일 도메인 요청 간격)
 */
const lastRequestTime = {};
async function rateLimit(domain, minInterval = 2000) {
  const now = Date.now();
  const lastTime = lastRequestTime[domain] || 0;
  const elapsed = now - lastTime;
  
  if (elapsed < minInterval) {
    const waitTime = minInterval - elapsed;
    await new Promise(resolve => setTimeout(resolve, waitTime));
  }
  
  lastRequestTime[domain] = Date.now();
}

/**
 * URL에서 도메인 추출
 */
function getDomain(url) {
  try {
    return new URL(url).hostname;
  } catch (e) {
    return 'unknown';
  }
}

/**
 * 날짜 파싱 (한국 형식)
 * 예: "2시간 전", "2026.02.17", "어제", "2월 17일"
 */
function parseKoreanDate(dateStr) {
  const now = new Date();
  
  // "N시간 전"
  const hoursAgo = dateStr.match(/(\d+)시간\s*전/);
  if (hoursAgo) {
    const hours = parseInt(hoursAgo[1]);
    return new Date(now.getTime() - hours * 60 * 60 * 1000).toISOString().split('T')[0];
  }
  
  // "N분 전"
  const minsAgo = dateStr.match(/(\d+)분\s*전/);
  if (minsAgo) {
    return now.toISOString().split('T')[0];
  }
  
  // "어제"
  if (dateStr.includes('어제')) {
    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    return yesterday.toISOString().split('T')[0];
  }
  
  // "2026.02.17"
  const dotFormat = dateStr.match(/(\d{4})\.(\d{2})\.(\d{2})/);
  if (dotFormat) {
    return `${dotFormat[1]}-${dotFormat[2]}-${dotFormat[3]}`;
  }
  
  // "2월 17일" (올해)
  const monthDay = dateStr.match(/(\d+)월\s*(\d+)일/);
  if (monthDay) {
    const year = now.getFullYear();
    const month = String(monthDay[1]).padStart(2, '0');
    const day = String(monthDay[2]).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
  
  // 파싱 실패 시 원본 반환
  return dateStr;
}

/**
 * 숫자 파싱 (한국 단위)
 * 예: "1.2만", "523", "1,234"
 */
function parseKoreanNumber(numStr) {
  if (!numStr) return 0;
  
  // 쉼표 제거
  let cleaned = String(numStr).replace(/,/g, '');
  
  // "만" 단위
  const manMatch = cleaned.match(/([\d.]+)만/);
  if (manMatch) {
    return Math.floor(parseFloat(manMatch[1]) * 10000);
  }
  
  // 일반 숫자
  return parseInt(cleaned) || 0;
}

module.exports = {
  createStealthBrowser,
  getRandomUserAgent,
  humanDelay,
  scrollDown,
  cleanText,
  outputJSON,
  outputError,
  outputSuccess,
  saveScreenshot,
  rateLimit,
  getDomain,
  parseKoreanDate,
  parseKoreanNumber
};
