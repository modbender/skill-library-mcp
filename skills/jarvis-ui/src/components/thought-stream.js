// ── 思考流背景（固定區域 + 滾動 + 漸層消失） ──

const thoughts = [
  '分析使用者意圖... 判斷最佳回應策略',
  'PARSING CONTEXT WINDOW: 128K TOKENS LOADED',
  '記憶搜索中... memory/2026-02-12.md',
  'EVALUATING RESPONSE CANDIDATES...',
  '檢查 SOUL.md 人格一致性...',
  'AUDIO FREQUENCY ANALYSIS: PEAK AT 440HZ',
  '比對長期記憶與短期記憶的關聯性',
  'GSAP.TIMELINE({SMOOTHNESS: 0.85})',
  '推理鏈：前提 → 分析 → 結論 → 驗證',
  'SCANNING SKILL REGISTRY: 6 MODULES ACTIVE',
  '語意理解中... 信心度 0.94',
  'THREE.VECTOR3 → ANOMALY.POSITION.UPDATE()',
  '情感分析：正面 0.7 / 中性 0.2 / 負面 0.1',
  'HEARTBEAT.CHECK() — ALL SYSTEMS NOMINAL',
  '正在組織回應結構... 預計 3 段落',
  'CONTEXT.RELEVANCE.SCORE = 0.89',
  '回顧最近 5 則對話以維持連貫性',
  'MODEL.INFERENCE({TEMP: 0.7, TOP_P: 0.95})',
  '判斷：此問題需要技術性回答',
  'LOADING AGENT.JSON — CONFIG PASSED',
  '搜尋最適合的表達方式...',
  'NEURAL.PATHWAY("CREATIVE_REASONING")',
  '交叉驗證：記憶 × 上下文 × 指令',
  'OPTIMIZER.RUN({BEAM_SEARCH, WIDTH: 4})',
  '這個想法有趣... 深入展開中',
  'SYSTEM.COHERENCE.CHECK — PASSED ✓',
  '平衡效率與完整性的取捨...',
  'TOKEN.BUDGET.REMAINING: 45,231',
  '觀察到新模式... 記錄至長期記憶',
  'ATTENTION.LAYER[32].REDISTRIBUTING...',
];

let container = null;
let textArea = null;
let intervalId = null;
let lineIndex = 0;
let currentLine = null;
let charIdx = 0;
let typeTimer = null;

function createContainer() {
  container = document.createElement('div');
  container.id = 'thought-stream';
  container.style.cssText = `
    position: fixed;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    width: 45%;
    max-width: 600px;
    height: 250px;
    pointer-events: none;
    z-index: 2;
    overflow: hidden;
    -webkit-mask-image: linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.3) 30%, rgba(0,0,0,0.8) 70%, rgba(0,0,0,1) 100%);
    mask-image: linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.3) 30%, rgba(0,0,0,0.8) 70%, rgba(0,0,0,1) 100%);
  `;

  textArea = document.createElement('div');
  textArea.style.cssText = `
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 0 10px;
  `;

  container.appendChild(textArea);
  document.body.appendChild(container);
}

function startNewLine() {
  const text = thoughts[lineIndex % thoughts.length];
  lineIndex++;

  const line = document.createElement('div');
  line.style.cssText = `
    font-family: "TheGoodMonolith", monospace;
    font-size: 14px;
    letter-spacing: 1.5px;
    line-height: 1.8;
    color: rgba(var(--accent-rgb), 0.45);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-align: center;
  `;
  line.textContent = '';
  // 新行加到底部，舊的往上推然後頂部漸層消失
  textArea.appendChild(line);

  // 限制行數，移除最頂部（最舊）的
  while (textArea.children.length > 12) {
    textArea.removeChild(textArea.firstChild);
  }

  // 逐字打出
  currentLine = { el: line, text, charIdx: 0 };
  if (typeTimer) clearInterval(typeTimer);
  typeTimer = setInterval(() => {
    if (!currentLine) return;
    if (currentLine.charIdx < currentLine.text.length) {
      currentLine.el.textContent = currentLine.text.substring(0, currentLine.charIdx + 1);
      currentLine.charIdx++;
    } else {
      clearInterval(typeTimer);
      typeTimer = null;
      currentLine = null;
    }
  }, 40);
}

export function initThoughtStream() {
  createContainer();
  // 延遲啟動
  setTimeout(() => {
    startNewLine();
    intervalId = setInterval(startNewLine, 3500);
  }, 4000);
}

export function stopThoughtStream() {
  if (intervalId) clearInterval(intervalId);
  if (typeTimer) clearInterval(typeTimer);
}
