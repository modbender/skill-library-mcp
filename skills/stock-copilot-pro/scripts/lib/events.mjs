function inferThemeTags(text) {
  const raw = String(text || "").toLowerCase();
  const themes = [];
  if (/ai|算力|gpu|大模型|芯片|semiconductor/.test(raw)) themes.push("AI算力");
  if (/新能源|光伏|储能|电池|ev|wind|solar/.test(raw)) themes.push("新能源");
  if (/消费|零售|餐饮|旅游|消费复苏/.test(raw)) themes.push("消费复苏");
  if (/监管|政策|罚款|审批|牌照/.test(raw)) themes.push("监管政策");
  if (/并购|收购|重组|merger|acquisition/.test(raw)) themes.push("并购重组");
  if (/业绩|财报|盈利预警|guidance|earnings/.test(raw)) themes.push("业绩指引");
  return themes.length ? themes : ["市场情绪"];
}

function inferSentiment(text) {
  const raw = String(text || "").toLowerCase();
  if (/增长|超预期|创新高|利好|beat|strong|surge|record/.test(raw)) return "positive";
  if (/下滑|不及预期|风险|利空|warn|drop|decline|lawsuit/.test(raw)) return "negative";
  return "neutral";
}

export function extractEvents(sentiment, xSentiment, options = {}) {
  const events = [];
  const maxEvents = Number(options.maxEvents || 8);
  const sentItems = sentiment?.raw?.data?.hits || sentiment?.raw?.hits || sentiment?.raw?.feed || [];
  const xItems = Array.isArray(xSentiment?.raw)
    ? xSentiment.raw
    : Array.isArray(xSentiment?.raw?.data)
      ? xSentiment.raw.data
      : Array.isArray(xSentiment?.raw?.posts)
        ? xSentiment.raw.posts
        : [];

  for (const item of sentItems.slice(0, maxEvents)) {
    const src = item?.source || item || {};
    const title = src.title || src.headline || src.summary || null;
    if (!title) continue;
    const text = `${title} ${src.content || ""}`;
    events.push({
      title,
      time: src.publishTime || src.effectiveTime || src.datetime || null,
      source: src.type || src.sourceName || "news",
      themeTags: inferThemeTags(text),
      sentiment: inferSentiment(text),
      impactPath: "事件可能通过预期变化影响估值与交易情绪",
      confidence: "medium",
      counterpoints: ["需等待后续数据验证事件持续性"],
    });
  }

  for (const post of xItems.slice(0, maxEvents)) {
    const text = post?.text || post?.full_text || post?.title || null;
    if (!text) continue;
    events.push({
      title: text.slice(0, 140),
      time: post?.created_at || post?.datetime || null,
      source: "x",
      themeTags: inferThemeTags(text),
      sentiment: inferSentiment(text),
      impactPath: "社交热度变化可能先于价格波动，但噪音较大",
      confidence: "low",
      counterpoints: ["社交媒体观点存在样本偏差与情绪噪音"],
    });
  }

  return events.slice(0, maxEvents);
}

export function clusterEventsByTheme(events = []) {
  const grouped = new Map();
  for (const evt of events) {
    const tags = evt.themeTags?.length ? evt.themeTags : ["市场情绪"];
    for (const tag of tags) {
      if (!grouped.has(tag)) grouped.set(tag, []);
      grouped.get(tag).push(evt);
    }
  }
  return [...grouped.entries()].map(([name, items]) => ({
    name,
    eventCount: items.length,
    keyEvents: items.slice(0, 3).map((x) => x.title),
    trackingIndicator: "事件后3-10个交易日的量价与业绩预期变化",
  }));
}

export function buildEventRadarIdeas(events = [], inputSymbol, market = "GLOBAL") {
  const ideas = [];
  if (inputSymbol) {
    ideas.push({
      ticker: inputSymbol,
      market,
      direction: "long",
      rationale: "主标的事件关注度上升，可跟踪催化兑现情况",
      entryTrigger: "回踩关键均线后放量转强",
      positionSize: "首仓 20%-30%，分批加仓",
      stopLoss: "-8% 或趋势破位",
      invalidation: "核心事件被证伪或业绩不及预期",
    });
  }
  const themeCounter = new Map();
  for (const evt of events) {
    for (const tag of evt.themeTags || []) themeCounter.set(tag, (themeCounter.get(tag) || 0) + 1);
  }
  const topThemes = [...themeCounter.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([x]) => x);
  for (const theme of topThemes) {
    ideas.push({
      ticker: `${theme}-basket`,
      market: "GLOBAL",
      direction: "long",
      rationale: `主题“${theme}”事件密度较高，具备阶段性交易机会`,
      entryTrigger: "主题相关标的出现趋势共振与成交放大",
      positionSize: "主题仓位不超过总仓位 30%",
      stopLoss: "主题热度快速衰减且领涨股破位",
      invalidation: "政策/基本面数据与主题叙事背离",
    });
  }
  return ideas.slice(0, 5);
}

