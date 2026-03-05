import { formatAmountByMarket, formatNum, formatPct, formatRatioPct, normalizeNewlines, maxConsecutiveCharRun, toFencedCodeBlock } from "./utils.mjs";

const REPORTIFY_CUSTOM_MAX_BLOCKS = 6;
const REPORTIFY_CUSTOM_MAX_CHARS_PER_BLOCK = 12000;

function redactSecrets(text) {
  if (!text) return text;
  return String(text)
    .replace(/Bearer\s+[A-Za-z0-9\-\._~\+\/]+=*/gi, "Bearer [REDACTED]")
    .replace(/QVERIS_API_KEY\s*[:=]\s*['"]?[^'"\s]+['"]?/gi, "QVERIS_API_KEY=[REDACTED]")
    .replace(/("?(?:qveris_api_key|authorization)"?\s*[:=]\s*)("[^"]*"|'[^']*'|[^\s,}]+)/gi, "$1[REDACTED]");
}

export function extractReportifyCustomBlocks(inputText) {
  const text = String(inputText || "");
  const matches = text.match(/<reportify-custom[\s\S]*?<\/reportify-custom>/gi);
  if (!matches || matches.length === 0) return [];
  return matches.slice(0, REPORTIFY_CUSTOM_MAX_BLOCKS);
}

export { toFencedCodeBlock, normalizeNewlines, maxConsecutiveCharRun };

export function formatReportifyCustomBlocksSafe(inputText) {
  const blocks = extractReportifyCustomBlocks(inputText);
  if (blocks.length === 0) return [];
  const lines = [];
  lines.push("## reportify-custom（安全呈现）");
  lines.push("> 以下内容来自原始输入。为降低 XSS 风险，已按纯文本代码块输出（不会作为 Markdown/HTML 执行）。");
  for (const rawBlock of blocks) {
    const redacted = redactSecrets(rawBlock);
    const clipped =
      redacted.length > REPORTIFY_CUSTOM_MAX_CHARS_PER_BLOCK
        ? `${redacted.slice(0, REPORTIFY_CUSTOM_MAX_CHARS_PER_BLOCK)}\n...[truncated]...`
        : redacted;
    lines.push("");
    lines.push(toFencedCodeBlock(clipped, "reportify-custom"));
  }
  return lines;
}

export function formatQuestionnaireMarkdown(questionnaire) {
  const lines = [];
  lines.push("# 投资偏好问卷");
  lines.push("");
  for (const q of questionnaire.questions || []) {
    lines.push(`## ${q.prompt}`);
    for (const opt of q.options || []) lines.push(`- ${opt.id}: ${opt.label}`);
    lines.push("");
  }
  lines.push(`> ${questionnaire.instructions || ""}`);
  return lines.join("\n");
}

export function formatMarkdown(result) {
  if (result?.questionnaire && !result?.analysis) {
    return formatQuestionnaireMarkdown(result.questionnaire);
  }

  const { symbol, market, mode, data, quality, evolution, analysis } = result;
  const q = data.quote?.parsed || {};
  const f = data.fundamentals?.parsed || {};
  const t = data.technicals?.parsed || {};
  const s = data.sentiment?.parsed || {};
  const x = data.x_sentiment?.parsed || {};
  const scorecard = analysis?.scorecard || {};
  const safetyMargin = analysis?.safetyMargin || {};
  const chaseRisk = analysis?.chaseRisk || {};
  const recommendation = analysis?.recommendation || {};
  const thesis = analysis?.thesis || {};
  const valuationFrame = analysis?.valuationFrame || {};
  const eventRadar = analysis?.eventRadar || {};
  const now = new Date().toISOString();
  const summaryOnly = Boolean(result?.runtime?.summaryOnly);
  const lines = [];

  lines.push(`# ${symbol} 分析数据包`);
  lines.push(`> 数据截止时间: ${now}`);
  lines.push(`> 市场: ${market} | 模式: ${mode} | 质量置信度: ${quality.confidence}`);
  lines.push("");

  lines.push("## 核心快照");
  lines.push(`- 综合评级: ${scorecard.grade ?? "N/A"} (${scorecard.composite ?? "N/A"}/100)`);
  lines.push(`- 当前信号: ${recommendation.signal ?? "N/A"} | 时序风险: ${chaseRisk.risk ?? "unknown"} (${chaseRisk.classification ?? "N/A"})`);
  lines.push(`- 估值结论: ${valuationFrame.verdict || "N/A"} | 安全边际: ${formatPct(safetyMargin.margin)}`);
  lines.push(`- 最新价: ${formatNum(q.price)} | 当日涨跌: ${formatPct(q.percentChange)} | 近5日涨跌: ${formatPct(t.change5d)}`);
  lines.push("");

  lines.push("## 估值与财务");
  lines.push(`- 估值: PE ${formatNum(f.pe)} | PB ${formatNum(f.pb)} | 市值 ${formatAmountByMarket(f.marketCap, market)}`);
  lines.push(`- 财务: 营收 ${formatAmountByMarket(f.revenue, market)} | 净利润 ${formatAmountByMarket(f.netProfit, market)}`);
  lines.push(`- 现金与质量: 经营现金流 ${formatAmountByMarket(f.operatingCashflow, market)} | 利润率 ${formatRatioPct(f.profitMargin)}`);
  lines.push("");

  lines.push("## 事件与情绪");
  const events = eventRadar.events || [];
  if (events.length === 0) {
    lines.push("- 暂无高置信度事件");
  } else {
    for (const evt of events.slice(0, 3)) {
      lines.push(`- [${evt.source}] ${evt.title} (${evt.sentiment}, 主题: ${(evt.themeTags || []).join("/") || "N/A"})`);
    }
  }
  lines.push(`- 新闻热度: ${s.itemCount ?? "N/A"} | X热度: ${x.itemCount ?? "N/A"}`);
  lines.push("");

  lines.push("## 投资逻辑线索（供 OpenClaw 推理）");
  const bullishDrivers = Array.isArray(thesis?.drivers) ? thesis.drivers.slice(0, 2) : [];
  const bearishRisks = Array.isArray(thesis?.risks) ? thesis.risks.slice(0, 3) : [];
  lines.push(`- 看多驱动: ${bullishDrivers.length > 0 ? bullishDrivers.join("；") : "N/A"}`);
  lines.push(`- 看空风险: ${bearishRisks.length > 0 ? bearishRisks.join("；") : "N/A"}`);
  lines.push(`- 当前结论线索: 信号=${recommendation.signal ?? "N/A"}，估值=${valuationFrame.verdict || "N/A"}，追高风险=${chaseRisk.risk ?? "unknown"}`);
  lines.push("");

  lines.push("## 投资建议线索（供 OpenClaw 生成）");
  lines.push("- 空仓: 优先等待支撑确认后分批建仓，避免追高放量日。");
  lines.push("- 轻仓: 仅在事件与量价共振时加仓，否则保持观察仓位。");
  lines.push("- 重仓: 关注压力位与事件兑现节奏，必要时分批止盈/降风险。");
  lines.push("- 失效条件: 跌破关键支撑且放量，或核心基本面/政策逻辑被证伪。");
  lines.push("");

  if (!summaryOnly) {
    lines.push("## 补充证据");
    lines.push(`- 行业: ${thesis.businessSummary?.industry || "N/A"} | 主营: ${thesis.businessSummary?.mainBusiness || "N/A"}`);
    lines.push(`- 情景(基准): ${thesis.scenarios?.base?.condition || "N/A"}（概率 ${thesis.scenarios?.base?.probability || "N/A"}）`);
    lines.push(`- 透明度: route=${JSON.stringify(evolution?.route_source || {})} | template_hits=${evolution?.template_hits ?? 0}`);
    lines.push("");
  }

  lines.push("---");
  lines.push("*分析建议：请 OpenClaw 根据 SKILL.md 中的 Single Stock Analysis Guide 输出专业且不过长的报告（必须包含投资逻辑与投资建议）*");
  lines.push("");
  lines.push("## 风险提示与免责声明");
  for (const warning of quality.warnings || []) lines.push(`- ${warning}`);
  lines.push("- 本输出为研究参考，不构成投资建议。");
  lines.push("- 市场有风险，投资需谨慎。");

  const customSection = formatReportifyCustomBlocksSafe(result?.runtime?.resolvedInput?.original);
  if (customSection.length > 0) {
    lines.push("");
    lines.push(...customSection);
  }
  return lines.join("\n");
}

