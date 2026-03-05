/**
 * human-like.js — 拟人化浏览器操作工具模块
 * 
 * 解决风控检测的核心问题：
 * 1. 随机延迟替代固定延迟
 * 2. 逐字打字含偶发 typo + 修正
 * 3. 鼠标移动轨迹（贝塞尔曲线）
 * 4. 页面浏览模拟（滚动、停留）
 * 5. 定时任务随机偏移
 * 
 * Usage:
 *   const { humanType, humanClick, humanDelay, humanScroll, humanFill } = require('./utils/human-like');
 */

// ─── 随机数工具 ───

/** 正态分布随机数 (Box-Muller) */
function gaussRandom(mean, stddev) {
  const u1 = Math.random();
  const u2 = Math.random();
  const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  return mean + z * stddev;
}

/** 在 [min, max] 范围内的随机整数 */
function randInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/** 在 [min, max] 范围内的随机浮点数 */
function randFloat(min, max) {
  return Math.random() * (max - min) + min;
}

// ─── 延迟 ───

/**
 * 拟人化随机延迟
 * @param {number} minMs - 最小毫秒
 * @param {number} maxMs - 最大毫秒
 * @returns {Promise<number>} 实际等待的毫秒数
 */
async function humanDelay(minMs = 500, maxMs = 2000) {
  const delay = randInt(minMs, maxMs);
  await new Promise(r => setTimeout(r, delay));
  return delay;
}

/**
 * 模拟思考停顿（较长的延迟，用于填写表单前等）
 */
async function humanThink(minMs = 1500, maxMs = 4000) {
  return humanDelay(minMs, maxMs);
}

// ─── 鼠标移动 ───

/**
 * 贝塞尔曲线插值
 */
function bezierPoint(t, p0, p1, p2, p3) {
  const mt = 1 - t;
  return mt * mt * mt * p0 + 3 * mt * mt * t * p1 + 3 * mt * t * t * p2 + t * t * t * p3;
}

/**
 * 生成从当前位置到目标的鼠标移动路径（贝塞尔曲线 + 抖动）
 */
function generateMousePath(fromX, fromY, toX, toY) {
  const steps = randInt(15, 30);
  const cp1x = fromX + (toX - fromX) * randFloat(0.1, 0.4) + randFloat(-50, 50);
  const cp1y = fromY + (toY - fromY) * randFloat(0.1, 0.4) + randFloat(-50, 50);
  const cp2x = fromX + (toX - fromX) * randFloat(0.6, 0.9) + randFloat(-30, 30);
  const cp2y = fromY + (toY - fromY) * randFloat(0.6, 0.9) + randFloat(-30, 30);

  const path = [];
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    // 非线性时间：开始和结束慢，中间快（ease-in-out）
    const eased = t < 0.5
      ? 2 * t * t
      : 1 - Math.pow(-2 * t + 2, 2) / 2;

    const x = bezierPoint(eased, fromX, cp1x, cp2x, toX) + randFloat(-2, 2);
    const y = bezierPoint(eased, fromY, cp1y, cp2y, toY) + randFloat(-2, 2);
    path.push({ x: Math.round(x), y: Math.round(y) });
  }
  // 最后一步精确到目标
  path[path.length - 1] = { x: toX, y: toY };
  return path;
}

/**
 * 拟人化点击：鼠标移动轨迹 → 短暂悬停 → 点击
 * @param {import('playwright').Page} page
 * @param {string} selector - CSS 选择器
 * @param {object} [opts] - { timeout, button }
 */
async function humanClick(page, selector, opts = {}) {
  const { timeout = 10000, button = 'left' } = opts;

  const el = typeof selector === 'string'
    ? await page.waitForSelector(selector, { timeout })
    : selector;

  const box = await el.boundingBox();
  if (!box) throw new Error(`Element not visible: ${selector}`);

  // 目标点：在元素内随机偏移（不总是正中心）
  const targetX = box.x + box.width * randFloat(0.25, 0.75);
  const targetY = box.y + box.height * randFloat(0.3, 0.7);

  // 获取当前鼠标位置（默认从视窗随机位置开始）
  const viewport = page.viewportSize() || { width: 1280, height: 800 };
  const fromX = randInt(0, viewport.width);
  const fromY = randInt(0, viewport.height);

  // 移动鼠标
  const path = generateMousePath(fromX, fromY, targetX, targetY);
  for (const point of path) {
    await page.mouse.move(point.x, point.y);
    await new Promise(r => setTimeout(r, randInt(3, 12)));
  }

  // 悬停一小会儿
  await humanDelay(80, 250);

  // 点击（含随机按下/释放时间差）
  await page.mouse.down({ button });
  await new Promise(r => setTimeout(r, randInt(40, 120)));
  await page.mouse.up({ button });

  // 点击后短暂停顿
  await humanDelay(100, 400);
}

// ─── 打字 ───

// 常见 typo 映射（QWERTY 相邻键）
const ADJACENT_KEYS = {
  a: 'sqwz', b: 'vngh', c: 'xdfv', d: 'sfcxe', e: 'wrd',
  f: 'dgcvr', g: 'fhbvt', h: 'gjbny', i: 'uojk', j: 'hknui',
  k: 'jlmio', l: 'kop', m: 'njk', n: 'bmhj', o: 'iplk',
  p: 'ol', q: 'wa', r: 'etfd', s: 'adwxz', t: 'rfgy',
  u: 'yihj', v: 'cbfg', w: 'qase', x: 'zsdc', y: 'tugh', z: 'asx',
};

/**
 * 拟人化逐字打字（含偶发 typo + 退格修正）
 * @param {import('playwright').Page} page
 * @param {string} selector - 输入框选择器 (input/textarea)
 * @param {string} text - 要输入的文本
 * @param {object} [opts] - { minDelay, maxDelay, typoRate }
 */
async function humanType(page, selector, text, opts = {}) {
  const {
    minDelay = 50,      // 每键最小间隔 ms
    maxDelay = 180,      // 每键最大间隔 ms
    typoRate = 0.03,     // typo 概率 (3%)
  } = opts;

  if (selector) {
    await humanClick(page, selector);
    await humanDelay(200, 600);
  }

  for (let i = 0; i < text.length; i++) {
    const char = text[i];

    // 偶发 typo（仅对英文字母）
    if (Math.random() < typoRate && /[a-z]/i.test(char) && ADJACENT_KEYS[char.toLowerCase()]) {
      const adjacent = ADJACENT_KEYS[char.toLowerCase()];
      const typoChar = adjacent[randInt(0, adjacent.length - 1)];
      await page.keyboard.type(typoChar);
      await humanDelay(100, 300); // 发现错误的反应时间
      await page.keyboard.press('Backspace');
      await humanDelay(50, 150);
    }

    await page.keyboard.type(char);

    // 随机打字速度：正态分布围绕平均值波动
    const avgDelay = (minDelay + maxDelay) / 2;
    const stdDev = (maxDelay - minDelay) / 4;
    let delay = Math.round(gaussRandom(avgDelay, stdDev));
    delay = Math.max(minDelay, Math.min(maxDelay, delay));

    // 标点/空格后偶尔多停顿
    if (/[,.!?;:，。！？；：\s]/.test(char) && Math.random() < 0.3) {
      delay += randInt(100, 400);
    }

    await new Promise(r => setTimeout(r, delay));
  }
}

/**
 * 拟人化填充 contenteditable（模拟键盘输入而非 fill/evaluate 注入）
 * @param {import('playwright').Page} page
 * @param {string} selector - contenteditable 元素选择器
 * @param {string} text - 要输入的文本
 * @param {object} [opts] - 同 humanType
 */
async function humanFillContentEditable(page, selector, text, opts = {}) {
  await humanClick(page, selector);
  await humanDelay(300, 800);

  // 逐行输入，换行用 Enter
  const lines = text.split('\n');
  for (let i = 0; i < lines.length; i++) {
    if (i > 0) {
      await page.keyboard.press('Enter');
      await humanDelay(200, 500);
    }
    if (lines[i]) {
      await humanType(page, null, lines[i], opts);
    }
  }
}

// ─── 页面浏览模拟 ───

/**
 * 模拟人类浏览页面（随机滚动 + 停留）
 * @param {import('playwright').Page} page
 * @param {object} [opts] - { scrolls, minPause, maxPause }
 */
async function humanScroll(page, opts = {}) {
  const {
    scrolls = randInt(2, 5),
    minPause = 500,
    maxPause = 2000,
  } = opts;

  for (let i = 0; i < scrolls; i++) {
    const deltaY = randInt(100, 400) * (Math.random() < 0.8 ? 1 : -1); // 偶尔往回滚
    await page.mouse.wheel(0, deltaY);
    await humanDelay(minPause, maxPause);
  }
}

/**
 * 模拟"先看看页面"（加载后的自然浏览行为）
 */
async function humanBrowse(page, opts = {}) {
  const { duration = randInt(2000, 5000) } = opts;
  const start = Date.now();

  while (Date.now() - start < duration) {
    const action = Math.random();
    if (action < 0.5) {
      // 滚动
      await page.mouse.wheel(0, randInt(50, 200));
    } else if (action < 0.8) {
      // 随机移动鼠标
      const viewport = page.viewportSize() || { width: 1280, height: 800 };
      await page.mouse.move(randInt(100, viewport.width - 100), randInt(100, viewport.height - 100));
    }
    // 停顿
    await humanDelay(300, 1500);
  }
}

// ─── 定时任务偏移 ───

/**
 * 计算定时任务的随机偏移（避免固定时间发布）
 * @param {number} baseMinutes - 基准分钟数
 * @param {number} range - 偏移范围（±分钟）
 * @returns {number} 偏移后的分钟数
 */
function jitterSchedule(baseMinutes, range = 30) {
  const offset = randInt(-range, range);
  return Math.max(0, baseMinutes + offset);
}

/**
 * 等待随机偏移时间
 * @param {number} minMinutes
 * @param {number} maxMinutes
 */
async function jitterWait(minMinutes = 1, maxMinutes = 10) {
  const ms = randInt(minMinutes * 60000, maxMinutes * 60000);
  console.log(`[JITTER] Waiting ${(ms / 60000).toFixed(1)} min`);
  await new Promise(r => setTimeout(r, ms));
  return ms;
}

// ─── 导出 ───

module.exports = {
  // 随机工具
  randInt,
  randFloat,
  gaussRandom,
  // 延迟
  humanDelay,
  humanThink,
  // 鼠标
  humanClick,
  generateMousePath,
  // 打字
  humanType,
  humanFillContentEditable,
  // 浏览
  humanScroll,
  humanBrowse,
  // 定时偏移
  jitterSchedule,
  jitterWait,
};
