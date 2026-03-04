// Local verification runner only.
// OpenClaw production flow should use the browser tool, not this Playwright script.
const fs = require('fs');
const path = require('path');
const { chromium } = require('/opt/homebrew/lib/node_modules/playwright');

const cwd = __dirname;

function parseCliArgs(argv) {
  const options = {
    image: null,
    outDir: null,
    state: null,
    engine: 'playwright',
    delayMs: 2000,
    headless: null,
    help: false
  };

  const readNext = (index, label) => {
    const next = argv[index + 1];
    if (!next || next.startsWith('-')) {
      throw new Error(`missing value for ${label}`);
    }
    return next;
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];

    if (arg === '--help' || arg === '-h') {
      options.help = true;
      continue;
    }
    if (arg === '--headless') {
      options.headless = true;
      continue;
    }
    if (arg === '--headed') {
      options.headless = false;
      continue;
    }

    if (arg === '--image' || arg === '-i') {
      options.image = readNext(i, arg);
      i += 1;
      continue;
    }
    if (arg.startsWith('--image=')) {
      options.image = arg.slice('--image='.length);
      continue;
    }

    if (arg === '--out-dir') {
      options.outDir = readNext(i, arg);
      i += 1;
      continue;
    }
    if (arg.startsWith('--out-dir=')) {
      options.outDir = arg.slice('--out-dir='.length);
      continue;
    }

    if (arg === '--state') {
      options.state = readNext(i, arg);
      i += 1;
      continue;
    }
    if (arg.startsWith('--state=')) {
      options.state = arg.slice('--state='.length);
      continue;
    }

    if (arg === '--engine') {
      options.engine = readNext(i, arg);
      i += 1;
      continue;
    }
    if (arg.startsWith('--engine=')) {
      options.engine = arg.slice('--engine='.length);
      continue;
    }

    if (arg === '--delay-ms') {
      const raw = readNext(i, arg);
      const value = Number(raw);
      if (!Number.isFinite(value) || value < 0) {
        throw new Error(`invalid value for --delay-ms: ${raw}`);
      }
      options.delayMs = Math.floor(value);
      i += 1;
      continue;
    }
    if (arg.startsWith('--delay-ms=')) {
      const raw = arg.slice('--delay-ms='.length);
      const value = Number(raw);
      if (!Number.isFinite(value) || value < 0) {
        throw new Error(`invalid value for --delay-ms: ${raw}`);
      }
      options.delayMs = Math.floor(value);
      continue;
    }

    if (!arg.startsWith('-') && !options.image) {
      options.image = arg;
      continue;
    }

    throw new Error(`unknown argument: ${arg}`);
  }

  return options;
}

function printHelpAndExit() {
  console.log(`Usage:
  node verify-taobao-runner.js [--image <path>] [--headless|--headed] [--out-dir <dir>] [--state <path>] [--engine playwright] [--delay-ms <n>]

Examples:
  node verify-taobao-runner.js
  node verify-taobao-runner.js --image ./fixtures/sample.png
  node verify-taobao-runner.js /absolute/path/to/image.jpg --headless --delay-ms 4000
`);
  process.exit(0);
}

let cli;
try {
  cli = parseCliArgs(process.argv.slice(2));
  if (cli.help) {
    printHelpAndExit();
  }
  if (cli.engine !== 'playwright') {
    throw new Error(`unsupported engine: ${cli.engine}. This local script currently supports only 'playwright'.`);
  }
} catch (err) {
  console.error(`argument error: ${String(err.message || err)}`);
  console.error('run `node verify-taobao-runner.js --help` for usage');
  process.exit(2);
}

const imagePath = path.resolve(cwd, cli.image || 'test.png');
const outDir = path.resolve(cwd, cli.outDir || 'verification-artifacts');
const resultPath = path.join(outDir, 'result.json');
const logPath = path.join(outDir, 'run-log.txt');
const statePath = path.resolve(cwd, cli.state || path.join(outDir, 'taobao-storage-state.json'));

const logLines = [];
function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}`;
  logLines.push(line);
  console.log(line);
}

async function waitWithDelay(page, baseMs, reason) {
  const finalMs = baseMs + cli.delayMs;
  if (reason) {
    log(`wait ${finalMs}ms: ${reason}`);
  }
  await page.waitForTimeout(finalMs);
}

async function safeScreenshot(page, name) {
  try {
    const p = path.join(outDir, name);
    await page.screenshot({ path: p, fullPage: true });
    log(`screenshot saved: ${p}`);
  } catch (e) {
    log(`screenshot failed ${name}: ${String(e.message || e)}`);
  }
}

async function clickFirstVisible(page, selectors, timeout = 1800) {
  for (const selector of selectors) {
    const target = page.locator(selector).first();
    try {
      if (await target.isVisible({ timeout })) {
        await target.click({ timeout: 5000, force: true });
        return selector;
      }
    } catch (e) {
      log(`click skipped ${selector}: ${String(e.message || e).slice(0, 120)}`);
    }
  }
  return null;
}

async function clickAddToCartWithScroll(page, selectors) {
  const direct = await clickFirstVisible(page, selectors, 2200);
  if (direct) return direct;

  for (let round = 0; round < 5; round++) {
    const scrollHint = await page.evaluate((currentRound) => {
      const anchorSelectors = [
        '#tbpcDetail_SkuPanelFoot',
        '#SkuPanel_tbpcDetail_ssr2025',
        '#right-content-area',
        "[class*='PurchasePanel']"
      ];

      for (const selector of anchorSelectors) {
        const el = document.querySelector(selector);
        if (el && el.scrollIntoView) {
          el.scrollIntoView({ behavior: 'instant', block: 'center' });
          return `anchor:${selector}`;
        }
      }

      const root = document.scrollingElement || document.documentElement || document.body;
      if (!root) return 'none';

      const ratios = [0.18, 0.35, 0.5, 0.65, 0.8];
      const ratio = ratios[Math.min(currentRound, ratios.length - 1)];
      root.scrollTop = Math.floor((root.scrollHeight - root.clientHeight) * ratio);
      return `ratio:${ratio}`;
    }, round).catch(() => 'unknown');

    log(`add-cart button not found, scrolling detail page (round ${round + 1}, ${scrollHint})`);
    await waitWithDelay(page, 1000, '滚动后等待按钮渲染');

    const clicked = await clickFirstVisible(page, selectors, 2200);
    if (clicked) return clicked;
  }

  return null;
}

async function detectAddCartSuccess(page, timeoutMs = 8000) {
  const successTexts = [
    '成功加入购物车',
    '加入购物车成功',
    '已成功加入购物车',
    '已加入购物车',
    '已添加到购物车'
  ];
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    for (const t of successTexts) {
      if (await page.locator(`text=${t}`).first().isVisible({ timeout: 400 }).catch(() => false)) {
        return t;
      }
    }
    await page.waitForTimeout(500);
  }
  return null;
}

function normalizeCandidateHref(rawHref) {
  if (!rawHref || typeof rawHref !== 'string') return null;
  let href = rawHref.trim();
  if (!href || href.toLowerCase().startsWith('javascript:')) return null;

  if (href.startsWith('//')) {
    href = `https:${href}`;
  }

  if (!/^https?:\/\//i.test(href)) return null;
  return href;
}

function isLikelyDetailUrl(url) {
  return /https?:\/\/(?:item\.taobao\.com\/item\.htm|detail\.tmall\.com\/item\.htm)/i.test(url || '');
}

async function openDetailPageFromCandidates(context, candidates) {
  const maxTry = Math.min(candidates.length, 5);
  const errors = [];

  for (let i = 0; i < maxTry; i++) {
    const candidate = candidates[i];
    const href = normalizeCandidateHref(candidate.href);
    if (!href) {
      errors.push(`候选#${i + 1} href 无效`);
      continue;
    }

    const detailPage = await context.newPage();
    try {
      await detailPage.goto(href, { waitUntil: 'domcontentloaded', timeout: 90000 });
      await waitWithDelay(detailPage, 4500, '等待详情页稳定');

      const finalUrl = detailPage.url();
      const hasAddCartButton = await detailPage.locator(
        "#tbpcDetail_SkuPanelFoot button:has-text('加入购物车'), #J_LinkBasket, button:has-text('加入购物车'), a:has-text('加入购物车')"
      ).first().isVisible({ timeout: 2500 }).catch(() => false);

      if (isLikelyDetailUrl(finalUrl) || hasAddCartButton) {
        return {
          detailPage,
          chosenCandidate: { ...candidate, href },
          chosenIndex: i,
          detailUrl: finalUrl
        };
      }

      errors.push(`候选#${i + 1} 未进入详情页: ${finalUrl}`);
      await detailPage.close().catch(() => {});
    } catch (e) {
      errors.push(`候选#${i + 1} 打开失败: ${String(e.message || e).slice(0, 120)}`);
      await detailPage.close().catch(() => {});
    }
  }

  throw new Error(`无法从搜索结果进入商品详情页（已尝试前 ${maxTry} 个候选）：${errors.join(' | ')}`);
}

function extractItemIdFromUrl(rawUrl) {
  try {
    const u = new URL(rawUrl);
    return u.searchParams.get('id');
  } catch {
    return null;
  }
}

async function readMiniCartCount(page) {
  const selectors = [
    '#J_MiniCartNum',
    '.site-nav .site-nav-cart a',
    "[class*='cart'] [class*='num']"
  ];

  for (const selector of selectors) {
    const node = page.locator(selector).first();
    const visible = await node.isVisible({ timeout: 1200 }).catch(() => false);
    if (!visible) continue;

    const text = ((await node.textContent().catch(() => null)) || '').trim();
    const digits = text.replace(/[^\d]/g, '');
    if (digits) return Number(digits);
  }

  return null;
}

async function checkItemInCart(context, itemId) {
  if (!itemId) return false;

  const cartPage = await context.newPage();
  try {
    await cartPage.goto('https://cart.taobao.com/cart.htm', { waitUntil: 'domcontentloaded', timeout: 90000 });
    await waitWithDelay(cartPage, 3500, '等待购物车页稳定');

    const matched = await cartPage.evaluate((id) => {
      const escaped = id.replace(/"/g, '\\"');
      const byData = document.querySelector(`[data-itemid="${escaped}"], [data-id="${escaped}"]`);
      if (byData) return true;

      const byLink = document.querySelector(`a[href*="id=${escaped}"]`);
      if (byLink) return true;

      const body = document.body ? document.body.innerText : '';
      return body.includes(id);
    }, itemId);

    return Boolean(matched);
  } catch (e) {
    log(`checkItemInCart failed: ${String(e.message || e).slice(0, 180)}`);
    return false;
  } finally {
    await cartPage.close().catch(() => {});
  }
}

function isValidCookieValue(value) {
  if (!value) return false;
  const normalized = String(value).trim().toLowerCase();
  return normalized !== '' && normalized !== 'deleted' && normalized !== 'null' && normalized !== 'undefined';
}

async function verifyTaobaoLogin(page, context) {
  const cookies = await context.cookies('https://www.taobao.com').catch(() => []);
  const nickCookieNames = ['_nk_', 'tracknick', 'lgc'];

  let cookieNick = null;
  for (const name of nickCookieNames) {
    const matched = cookies.find(c => c.name === name && isValidCookieValue(c.value));
    if (matched) {
      cookieNick = matched.value;
      break;
    }
  }

  const nickSelectors = [
    '.site-nav-login-info-nick',
    '.member-nick-info',
    '.J_UserNick'
  ];

  let pageNick = null;
  for (const selector of nickSelectors) {
    const node = page.locator(selector).first();
    const visible = await node.isVisible({ timeout: 1200 }).catch(() => false);
    if (!visible) continue;

    const text = ((await node.textContent().catch(() => null)) || '').trim();
    if (text && !/登录/.test(text)) {
      pageNick = text;
      break;
    }
  }

  const loginPromptSelectors = [
    "text=亲，请登录",
    ".member-logout .login-guide-title",
    "a:has-text('立即登录')"
  ];
  let loginPromptVisible = false;
  for (const selector of loginPromptSelectors) {
    if (await page.locator(selector).first().isVisible({ timeout: 1000 }).catch(() => false)) {
      loginPromptVisible = true;
      break;
    }
  }

  const isLoggedIn = Boolean(cookieNick || pageNick) && !loginPromptVisible;
  return {
    isLoggedIn,
    cookieNick: cookieNick || null,
    pageNick: pageNick || null,
    loginPromptVisible
  };
}

async function run() {
  fs.mkdirSync(outDir, { recursive: true });

  const result = {
    success: false,
    imagePath,
    steps: [],
    selectedMode: '搜索并加购模式',
    uploaded: false,
    cameraEntryClicked: false,
    loginCheck: null,
    currentUrl: '',
    topCandidates: [],
    selectedCandidate: null,
    addToCart: {
      attempted: false,
      success: false,
      signal: null,
      buttonSelector: null,
      reason: null,
      detailUrl: null,
      itemId: null,
      cartCountBefore: null,
      cartCountAfter: null,
      cartContainsItemBefore: null,
      cartContainsItemAfter: null
    },
    error: null,
    startedAt: new Date().toISOString()
  };

  if (!fs.existsSync(imagePath)) {
    throw new Error(`image not found: ${imagePath}`);
  }

  let browser;
  try {
    const headless = cli.headless === null ? process.env.PW_HEADLESS === '1' : cli.headless;
    browser = await chromium.launch({ headless });
    log(`launch browser with headless=${headless}`);
    log(`run config => engine=${cli.engine}, imagePath=${imagePath}, outDir=${outDir}, delayMs=${cli.delayMs}`);

    const context = await browser.newContext({
      viewport: { width: 1440, height: 1800 },
      locale: 'zh-CN',
      storageState: fs.existsSync(statePath) ? statePath : undefined
    });
    if (fs.existsSync(statePath)) {
      log(`loaded storage state: ${statePath}`);
    } else {
      log(`storage state not found, continue without cookie: ${statePath}`);
    }
    const page = await context.newPage();

    page.on('console', msg => log(`browser console [${msg.type()}]: ${msg.text().slice(0, 180)}`));
    page.on('pageerror', err => log(`pageerror: ${err.message}`));

    result.steps.push('打开淘宝首页');
    await page.goto('https://www.taobao.com', { waitUntil: 'domcontentloaded', timeout: 90000 });
    await waitWithDelay(page, 4000, '等待淘宝首页稳定');
    result.currentUrl = page.url();
    await safeScreenshot(page, '01-home.png');

    result.steps.push('验证登录状态');
    const loginCheck = await verifyTaobaoLogin(page, context);
    result.loginCheck = loginCheck;
    log(`login check => ${JSON.stringify(loginCheck)}`);
    if (!loginCheck.isLoggedIn) {
      await safeScreenshot(page, '01b-login-required.png');
      throw new Error('未检测到淘宝登录状态，请先登录后重试（可先运行 node save-taobao-cookie.js 保存登录态）');
    }

    const cameraSelectors = [
      'text=搜同款',
      'text=拍立淘',
      'text=相机',
      '[aria-label*="相机"]',
      '[class*="camera"]',
      '[class*="image-search"]',
      '[class*="search-suggest-image-search"]'
    ];

    result.steps.push('尝试进入图片搜索入口');
    for (const selector of cameraSelectors) {
      const locator = page.locator(selector).first();
      try {
        if (await locator.isVisible({ timeout: 2500 })) {
          await locator.click({ timeout: 5000 });
          result.cameraEntryClicked = true;
          log(`clicked camera entry by selector: ${selector}`);
          break;
        }
      } catch (e) {
        log(`camera selector skipped: ${selector} => ${String(e.message || e).slice(0, 120)}`);
      }
    }

    await waitWithDelay(page, 2500, '等待图搜面板展开');
    await safeScreenshot(page, '02-after-camera-click.png');

    result.steps.push(`上传图片 ${path.basename(imagePath)}`);
    const contexts = [page, ...page.frames()];
    for (const ctx of contexts) {
      const ctxName = ctx === page ? 'main-page' : `frame:${ctx.url().slice(0, 120)}`;
      const inputs = ctx.locator("input[type='file']");
      const count = await inputs.count();
      if (!count) continue;

      for (let i = 0; i < count; i++) {
        try {
          await inputs.nth(i).setInputFiles(imagePath, { timeout: 7000 });
          result.uploaded = true;
          log(`uploaded image via ${ctxName} input#${i}`);
          break;
        } catch (e) {
          log(`upload failed via ${ctxName} input#${i}: ${String(e.message || e).slice(0, 180)}`);
        }
      }
      if (result.uploaded) break;
    }

    if (!result.uploaded) {
      throw new Error('未找到可用的图片上传 input[type=file]');
    }

    await waitWithDelay(page, 1500, '等待上传后面板稳定');
    await safeScreenshot(page, '03-after-upload.png');

    result.steps.push('点击图片搜索弹层中的搜索按钮');
    let searchClicked = false;
    let searchClickDetail = '';
    await page.locator('.image-search-context-wrapper-active').first().waitFor({ state: 'visible', timeout: 5000 }).catch(() => {});
    const newPagePromise = context.waitForEvent('page', { timeout: 10000 }).catch(() => null);

    const popupSearchSelectors = [
      "#image-search-upload-button.upload-button.upload-button-active",
      ".image-search-context-wrapper-active #image-search-upload-button.upload-button.upload-button-active",
      ".image-search-context-wrapper-active .upload-button.upload-button-active[data-spm='image_search_button']",
      ".image-search-context-wrapper-active .image-search-context-wrapper-inner.image-search-success-wrapper-active .upload-button.upload-button-active"
    ];

    for (const selector of popupSearchSelectors) {
      try {
        const btn = page.locator(selector).first();
        if (await btn.isVisible({ timeout: 2000 })) {
          await btn.click({ timeout: 5000, force: true });
          searchClicked = true;
          searchClickDetail = selector;
          break;
        }
      } catch (e) {
        log(`popup search click skipped ${selector}: ${String(e.message || e).slice(0, 120)}`);
      }
    }

    if (!searchClicked) {
      const scopedFallback = page.locator(".image-search-context-wrapper-active .upload-button:has-text('搜索')").first();
      if (await scopedFallback.isVisible({ timeout: 2000 })) {
        await scopedFallback.click({ timeout: 5000, force: true });
        searchClicked = true;
        searchClickDetail = ".image-search-context-wrapper-active .upload-button:has-text('搜索')";
      }
    }

    if (!searchClicked) {
      throw new Error('上传后未找到弹窗内“搜索”按钮（预期为 #image-search-upload-button.upload-button.upload-button-active）');
    }
    log(`clicked search trigger: ${searchClickDetail}`);

    const possibleNewPage = await newPagePromise;
    let resultPage = page;
    if (possibleNewPage) {
      await possibleNewPage.waitForLoadState('domcontentloaded', { timeout: 30000 }).catch(() => {});
      resultPage = possibleNewPage;
      log(`search opened new page: ${resultPage.url()}`);
    } else {
      await waitWithDelay(page, 5000, '等待当前页跳转到搜索结果');
      log(`search stayed on same page: ${page.url()}`);
    }

    await waitWithDelay(resultPage, 5000, '等待搜索结果列表加载');
    result.currentUrl = resultPage.url();
    await safeScreenshot(resultPage, '04-search-result-page.png');

    result.steps.push('尝试关闭登录弹窗');
    let popupClosed = false;
    const closeSelectors = [
      "text=关闭弹窗",
      "text=关闭",
      "text=先逛逛",
      "text=稍后再说",
      "text=暂不登录",
      "button:has-text('关闭')",
      ":text('关闭')",
      "[aria-label*='关闭']",
      "[class*='close']"
    ];

    const closeContexts = [resultPage, ...resultPage.frames()];
    for (const ctx of closeContexts) {
      const ctxName = ctx === resultPage ? 'main-page' : `frame:${ctx.url().slice(0, 120)}`;
      for (const selector of closeSelectors) {
        const target = ctx.locator(selector).first();
        try {
          if (await target.isVisible({ timeout: 1200 })) {
            await target.click({ timeout: 3000 });
            popupClosed = true;
            log(`popup close clicked: ${ctxName} ${selector}`);
            break;
          }
        } catch (e) {
          log(`popup close skipped ${ctxName} ${selector}: ${String(e.message || e).slice(0, 120)}`);
        }
      }
      if (popupClosed) break;
    }
    if (!popupClosed) {
      await resultPage.keyboard.press('Escape').catch(() => {});
      await waitWithDelay(resultPage, 1000, '弹窗关闭后等待页面恢复');
      log('popup close fallback: pressed Escape');
    }
    if (popupClosed) {
      await waitWithDelay(resultPage, 4000, '等待关闭弹窗后的结果页稳定');
      await safeScreenshot(resultPage, '05-after-close-popup.png');
    }

    result.steps.push('采样结果候选');
    const candidates = await resultPage.evaluate(() => {
      const list = [];
      const seen = new Set();
      const anchors = Array.from(document.querySelectorAll(
        "a[href*='item.taobao.com'], a[href*='detail.tmall.com'], a[href*='/item.htm']"
      ));

      for (const a of anchors) {
        const title = (a.textContent || '').replace(/\\s+/g, ' ').trim();
        if (!title || title.length < 8 || title.length > 120) continue;
        if (seen.has(title)) continue;

        const root = a.closest('div,li,article,section') || a.parentElement || a;
        const rootText = (root && root.textContent ? root.textContent : '').replace(/\\s+/g, ' ');
        const m = rootText.match(/¥\\s?\\d+(?:\\.\\d+)?/);
        const price = m ? m[0].replace(/\\s+/g, '') : null;

        seen.add(title);
        list.push({ title, price, href: a.href });
        if (list.length >= 10) break;
      }

      return list;
    });

    result.topCandidates = candidates;
    if (!candidates.length) {
      throw new Error('图搜结果为空，无法继续执行加购');
    }

    result.steps.push('选择候选商品并进入详情页');
    const {
      detailPage,
      chosenCandidate,
      chosenIndex,
      detailUrl
    } = await openDetailPageFromCandidates(context, candidates);
    result.selectedCandidate = chosenCandidate;
    result.addToCart.detailUrl = detailUrl;
    result.addToCart.itemId = extractItemIdFromUrl(chosenCandidate.href);
    log(`selected candidate index: ${chosenIndex + 1}`);
    result.addToCart.cartCountBefore = await readMiniCartCount(detailPage);
    if (result.addToCart.itemId) {
      result.addToCart.cartContainsItemBefore = await checkItemInCart(context, result.addToCart.itemId);
      log(`cart contains item(${result.addToCart.itemId}) before click: ${result.addToCart.cartContainsItemBefore}`);
    }
    await safeScreenshot(detailPage, '06-detail-page.png');

    result.steps.push('点击加入购物车');
    result.addToCart.attempted = true;

    const addCartButtonSelectors = [
      "#tbpcDetail_SkuPanelFoot button:has-text('加入购物车')",
      "#tbpcDetail_SkuPanelFoot .leftButtons--yzXHnpOm button:has-text('加入购物车')",
      "#SkuPanel_tbpcDetail_ssr2025 #tbpcDetail_SkuPanelFoot button",
      "#right-content-area button:has-text('加入购物车')",
      "#right-content-area a:has-text('加入购物车')",
      "#J_LinkBasket",
      ".tb-btn-add a",
      "[class*='PurchasePanel'] button:has-text('加入购物车')",
      "[class*='PurchasePanel'] a:has-text('加入购物车')"
    ];

    const clickedAddBtn = await clickAddToCartWithScroll(detailPage, addCartButtonSelectors);
    if (!clickedAddBtn) {
      result.addToCart.reason = '未找到加入购物车按钮';
      throw new Error('详情页未找到可点击的“加入购物车”按钮');
    }
    result.addToCart.buttonSelector = clickedAddBtn;
    log(`clicked add-cart button: ${clickedAddBtn}`);

    let addCartSignal = await detectAddCartSuccess(detailPage, 9000);
    if (!addCartSignal) {
      const skuOptionSelector = [
        "[class*='sku'] li:not(.disabled):not(.is-disabled):not(.tb-disabled):not(.selected):not(.tb-selected)",
        "[class*='Sku'] li:not(.disabled):not(.is-disabled):not(.tb-disabled):not(.selected):not(.tb-selected)",
        "li[data-value]:not(.disabled):not(.is-disabled):not(.tb-disabled):not(.selected):not(.tb-selected)"
      ];
      const pickedSku = await clickFirstVisible(detailPage, skuOptionSelector, 1000);
      if (pickedSku) {
        log(`selected sku option by selector: ${pickedSku}`);
        await waitWithDelay(detailPage, 700, '等待规格选择生效');
      }

      const confirmSelectors = [
        "button:has-text('确定')",
        "a:has-text('确定')",
        "button:has-text('加入购物车')",
        "a:has-text('加入购物车')",
        "text=确定"
      ];
      const clickedConfirm = await clickFirstVisible(detailPage, confirmSelectors, 1200);
      if (clickedConfirm) {
        log(`clicked sku confirm/add button: ${clickedConfirm}`);
      }
      addCartSignal = await detectAddCartSuccess(detailPage, 9000);
    }

    result.addToCart.cartCountAfter = await readMiniCartCount(detailPage);
    const countIncreased = (
      result.addToCart.cartCountBefore !== null &&
      result.addToCart.cartCountAfter !== null &&
      result.addToCart.cartCountAfter > result.addToCart.cartCountBefore
    );
    if (countIncreased) {
      log(`mini cart count increased: ${result.addToCart.cartCountBefore} -> ${result.addToCart.cartCountAfter}`);
    }

    let cartContainsItemAfter = false;
    if (result.addToCart.itemId) {
      cartContainsItemAfter = await checkItemInCart(context, result.addToCart.itemId);
      result.addToCart.cartContainsItemAfter = cartContainsItemAfter;
      log(`cart contains item(${result.addToCart.itemId}) after click: ${cartContainsItemAfter}`);
    }
    const cartContainsTransition = (
      result.addToCart.cartContainsItemBefore === false &&
      cartContainsItemAfter === true
    );

    if (addCartSignal || countIncreased || cartContainsTransition) {
      result.addToCart.success = true;
      result.addToCart.signal = addCartSignal || (countIncreased ? '购物车数量增加' : '购物车页新增该商品');
    } else {
      result.addToCart.reason = '未检测到成功提示且购物车状态未变化，疑似未成功加购';
      throw new Error(result.addToCart.reason);
    }
    await safeScreenshot(detailPage, '07-after-add-to-cart.png');

    result.success = true;
    result.finishedAt = new Date().toISOString();

    fs.writeFileSync(logPath, logLines.join('\n'));
    fs.writeFileSync(resultPath, JSON.stringify(result, null, 2));

    await context.close();
    await browser.close();
    return result;
  } catch (e) {
    result.error = String(e.message || e);
    result.finishedAt = new Date().toISOString();

    try {
      fs.writeFileSync(logPath, logLines.join('\n'));
      fs.writeFileSync(resultPath, JSON.stringify(result, null, 2));
    } catch {}

    if (browser) {
      try {
        await browser.close();
      } catch {}
    }

    throw e;
  }
}

run()
  .then((result) => {
    console.log('VERIFICATION_RESULT=' + JSON.stringify(result));
    process.exit(0);
  })
  .catch((err) => {
    console.error('VERIFICATION_FAILED=' + String(err.message || err));
    process.exit(1);
  });
