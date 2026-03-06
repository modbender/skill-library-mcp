/**
 * Dolphin Anty Browser Automation
 * Запуск профиля + подключение через Playwright для автоматизации
 * 
 * Использование:
 *   node dolphin_automate.js --profile-id <ID> --task screenshot --url "https://..."
 *   node dolphin_automate.js --profile-id <ID> --task scrape --url "https://..."
 *   node dolphin_automate.js --profile-id <ID> --task navigate --url "https://..."
 *   node dolphin_automate.js --profile-id <ID> --task warmup
 *   node dolphin_automate.js --profile-id <ID> --task custom --url "https://..." --code "document.title"
 */

const http = require('http');
const fs = require('fs');
const pathModule = require('path');
const { argv } = process;

const API_BASE = 'http://localhost:3001/v1.0';
const TOKEN_FILE = pathModule.join(__dirname, '..', '.token');

function getToken() {
  if (fs.existsSync(TOKEN_FILE)) return fs.readFileSync(TOKEN_FILE, 'utf8').trim();
  return null;
}

// ─── HTTP Helper ─────────────────────────────────────────────────

function apiRequest(method, path) {
  return new Promise((resolve, reject) => {
    const url = new URL(API_BASE + path);
    const token = getToken();
    const headers = {};
    if (token) headers['Authorization'] = 'Bearer ' + token;
    
    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname + url.search,
      method: method,
      headers: headers,
      timeout: 30000,
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, data: JSON.parse(data) });
        } catch {
          resolve({ status: res.statusCode, data: data });
        }
      });
    });

    req.on('error', (err) => {
      if (err.code === 'ECONNREFUSED') {
        reject(new Error('Dolphin Anty не запущен! Откройте приложение.'));
      } else {
        reject(err);
      }
    });

    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Таймаут подключения к Dolphin Anty'));
    });

    req.end();
  });
}

// ─── Случайная задержка (имитация человека) ─────────────────────

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function randomDelay(minMs = 500, maxMs = 2000) {
  return sleep(Math.floor(Math.random() * (maxMs - minMs)) + minMs);
}

// ─── Запуск профиля ─────────────────────────────────────────────

async function startProfile(profileId) {
  console.log(`🚀 Запускаю профиль ${profileId}...`);
  const res = await apiRequest('GET', `/browser_profiles/${profileId}/start?automation=1`);

  if (!res.data || !res.data.automation) {
    throw new Error(
      `Не удалось запустить профиль. Ответ: ${JSON.stringify(res.data)}`
    );
  }

  const { port, wsEndpoint } = res.data.automation;
  console.log(`✅ Профиль запущен. Port: ${port}, wsEndpoint: ${wsEndpoint}`);
  return { port, wsEndpoint };
}

// ─── Остановка профиля ──────────────────────────────────────────

async function stopProfile(profileId) {
  console.log(`⏹️ Останавливаю профиль ${profileId}...`);
  await apiRequest('GET', `/browser_profiles/${profileId}/stop`);
  console.log(`✅ Профиль остановлен.`);
}

// ─── Подключение Playwright ─────────────────────────────────────

async function connectBrowser(port, wsEndpoint) {
  let playwright;
  try {
    playwright = require('playwright');
  } catch {
    // Fallback: try global node_modules
    try {
      const globalPath = require('child_process').execSync('npm root -g', { encoding: 'utf8' }).trim();
      playwright = require(require('path').join(globalPath, 'playwright'));
    } catch {
      console.error('❌ Playwright не установлен. Выполните: npm install -g playwright');
      process.exit(1);
    }
  }

  const wsUrl = `ws://127.0.0.1:${port}${wsEndpoint}`;
  console.log(`🔗 Подключаюсь к браузеру: ${wsUrl}`);
  
  const browser = await playwright.chromium.connectOverCDP(wsUrl);
  const contexts = browser.contexts();
  const context = contexts[0] || await browser.newContext();
  
  return { browser, context };
}

// ─── Задачи ─────────────────────────────────────────────────────

async function taskScreenshot(context, url) {
  const page = await context.newPage();
  console.log(`📸 Открываю ${url}...`);
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await randomDelay(1000, 3000);
  
  const filename = `screenshot_${Date.now()}.png`;
  await page.screenshot({ path: filename, fullPage: true });
  console.log(`✅ Скриншот сохранён: ${filename}`);
  await page.close();
}

async function taskScrape(context, url) {
  const page = await context.newPage();
  console.log(`🔍 Собираю данные с ${url}...`);
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await randomDelay(1000, 3000);
  
  const data = await page.evaluate(() => {
    const title = document.title;
    const metaDesc = document.querySelector('meta[name="description"]')?.content || '';
    const h1s = [...document.querySelectorAll('h1')].map(el => el.textContent.trim());
    const h2s = [...document.querySelectorAll('h2')].map(el => el.textContent.trim());
    const links = [...document.querySelectorAll('a[href]')]
      .map(a => ({ text: a.textContent.trim().substring(0, 80), href: a.href }))
      .filter(l => l.text && l.href.startsWith('http'))
      .slice(0, 50);
    const paragraphs = [...document.querySelectorAll('p')]
      .map(p => p.textContent.trim())
      .filter(t => t.length > 20)
      .slice(0, 20);
    const images = [...document.querySelectorAll('img[src]')]
      .map(img => ({ src: img.src, alt: img.alt || '' }))
      .slice(0, 20);
    
    return { title, metaDesc, h1s, h2s, links, paragraphs, images };
  });

  console.log(`\n📄 Результаты скрапинга:\n`);
  console.log(`Заголовок: ${data.title}`);
  console.log(`Описание: ${data.metaDesc}`);
  if (data.h1s.length) console.log(`H1: ${data.h1s.join(', ')}`);
  if (data.h2s.length) console.log(`H2: ${data.h2s.join(' | ')}`);
  console.log(`Ссылок: ${data.links.length}`);
  console.log(`Параграфов: ${data.paragraphs.length}`);
  console.log(`Изображений: ${data.images.length}`);
  
  // Выводим JSON для парсинга агентом
  const outputFile = `scrape_${Date.now()}.json`;
  require('fs').writeFileSync(outputFile, JSON.stringify(data, null, 2), 'utf8');
  console.log(`\n💾 Полные данные сохранены: ${outputFile}`);
  
  await page.close();
}

async function taskNavigate(context, url) {
  const page = await context.newPage();
  console.log(`🌐 Открываю ${url}...`);
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await randomDelay(1000, 2000);
  
  const title = await page.title();
  console.log(`✅ Страница открыта: "${title}"`);
  console.log(`   URL: ${page.url()}`);
  // Не закрываем страницу — пользователь может продолжить вручную
}

async function taskWarmup(context) {
  const sites = [
    'https://www.google.com',
    'https://www.youtube.com',
    'https://www.wikipedia.org',
    'https://www.reddit.com',
    'https://news.ycombinator.com',
    'https://www.amazon.com',
    'https://www.github.com',
    'https://stackoverflow.com',
    'https://www.twitch.tv',
    'https://www.medium.com',
  ];

  // Случайно выбираем 3-5 сайтов
  const count = Math.floor(Math.random() * 3) + 3;
  const shuffled = sites.sort(() => Math.random() - 0.5).slice(0, count);

  console.log(`🔥 Прогрев профиля: посещу ${count} сайтов...\n`);

  for (const site of shuffled) {
    const page = await context.newPage();
    try {
      console.log(`  → ${site}`);
      await page.goto(site, { waitUntil: 'domcontentloaded', timeout: 20000 });
      
      // Имитация чтения — скроллим
      await randomDelay(2000, 5000);
      await page.evaluate(() => window.scrollBy(0, Math.random() * 500 + 200));
      await randomDelay(1000, 3000);
      await page.evaluate(() => window.scrollBy(0, Math.random() * 300 + 100));
      await randomDelay(1000, 2000);
      
    } catch (err) {
      console.log(`  ⚠️ ${site}: ${err.message.substring(0, 60)}`);
    }
    await page.close();
    await randomDelay(1000, 3000); // Пауза между сайтами
  }

  console.log(`\n✅ Прогрев завершён. Посещено ${count} сайтов.`);
}

async function taskCustom(context, url, code) {
  if (!code) {
    console.error('❌ Для task=custom нужен --code "javascript code"');
    process.exit(1);
  }
  
  const page = await context.newPage();
  if (url) {
    console.log(`🌐 Открываю ${url}...`);
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await randomDelay(500, 1500);
  }
  
  console.log(`⚡ Выполняю код...`);
  const result = await page.evaluate(code);
  console.log(`✅ Результат:`, result);
  await page.close();
}

// ─── CLI Parser ─────────────────────────────────────────────────

function getArg(name) {
  const idx = argv.indexOf(name);
  if (idx !== -1 && idx + 1 < argv.length) return argv[idx + 1];
  return null;
}

// ─── Main ────────────────────────────────────────────────────────

async function main() {
  const profileId = getArg('--profile-id');
  const task = getArg('--task');
  const url = getArg('--url');
  const code = getArg('--code');

  if (!profileId || !task) {
    console.log(`
Dolphin Anty Browser Automation

Использование:
  node dolphin_automate.js --profile-id <ID> --task <TASK> [--url <URL>] [--code <JS>]

Задачи:
  screenshot  — скриншот страницы
  scrape      — сбор данных (заголовки, ссылки, текст, картинки)
  navigate    — открыть URL в профиле
  warmup      — прогрев (посещение случайных сайтов)
  custom      — выполнить произвольный JS-код
    `);
    process.exit(1);
  }

  let automation;
  try {
    automation = await startProfile(profileId);
  } catch (err) {
    console.error('❌', err.message);
    process.exit(1);
  }

  const { port, wsEndpoint } = automation;
  
  // Даём браузеру полностью загрузиться
  await sleep(2000);

  let browser, context;
  try {
    ({ browser, context } = await connectBrowser(port, wsEndpoint));
  } catch (err) {
    console.error('❌ Не удалось подключиться к браузеру:', err.message);
    await stopProfile(profileId);
    process.exit(1);
  }

  try {
    switch (task) {
      case 'screenshot':
        if (!url) { console.error('❌ Нужен --url'); process.exit(1); }
        await taskScreenshot(context, url);
        break;
      case 'scrape':
        if (!url) { console.error('❌ Нужен --url'); process.exit(1); }
        await taskScrape(context, url);
        break;
      case 'navigate':
        if (!url) { console.error('❌ Нужен --url'); process.exit(1); }
        await taskNavigate(context, url);
        break;
      case 'warmup':
        await taskWarmup(context);
        break;
      case 'custom':
        await taskCustom(context, url, code);
        break;
      default:
        console.error(`❌ Неизвестная задача: ${task}`);
    }
  } catch (err) {
    console.error('❌ Ошибка выполнения:', err.message);
  }

  // Для navigate — не отключаемся, пользователь работает
  if (task !== 'navigate') {
    try {
      await browser.close();
    } catch { /* игнорируем */ }
    await stopProfile(profileId);
  }
}

main();
