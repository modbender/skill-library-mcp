import { resolveToolPayloadSync } from "../infra/qveris-client.mjs";

function toNumber(value) {
  if (value == null || value === "") return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function pickFirst(...values) {
  for (const v of values) {
    if (v == null) continue;
    if (typeof v === "string" && v.trim() === "") continue;
    return v;
  }
  return null;
}

export function pickQuoteData(raw) {
  const data = raw?.result?.data || raw?.data || raw || {};
  if (Array.isArray(data) && Array.isArray(data[0]) && data[0][0]) {
    const row = data[0][0];
    return {
      symbol: row.thscode ?? null,
      price: toNumber(row.latest),
      open: toNumber(row.open),
      high: toNumber(row.high),
      low: toNumber(row.low),
      volume: toNumber(row.volume),
      percentChange: toNumber(row.changeRatio),
      marketCap: toNumber(row.mv ?? row.totalCapital),
      pe: toNumber(row.pe_ttm ?? row.pe),
      pb: toNumber(row.pb ?? row.pbr_lf),
      timestamp: row.time ?? row.tradeDate ?? null,
      raw: row,
    };
  }
  return {
    symbol: data.symbol ?? data.Symbol ?? null,
    price: toNumber(data.close ?? data.price ?? data.latestPrice),
    open: toNumber(data.open),
    high: toNumber(data.high),
    low: toNumber(data.low),
    volume: toNumber(data.volume),
    percentChange: toNumber(data.percent_change ?? data.changePercent),
    marketCap: toNumber(data.marketCap ?? data.mv ?? data.totalCapital),
    pe: toNumber(data.pe_ttm ?? data.pe ?? data.TrailingPE),
    pb: toNumber(data.pb ?? data.pbr_lf ?? data.PriceToBookRatio),
    timestamp: data.datetime ?? data.timestamp ?? data["07. latest trading day"] ?? null,
    raw: data,
  };
}

export function pickFundamentalData(raw) {
  const data = raw?.result?.data || raw?.data || raw || {};
  if (Array.isArray(data) && Array.isArray(data[0]) && data[0][0]) {
    const row = data[0][0];
    const statementType = row.statement_type || row.statementType || null;
    const period = row.time || row.end_date || row.report_date || null;
    const tagsRaw = pickFirst(
      row.ths_the_ths_concept_index_stock,
      row.ths_concept_stock,
      row.ths_concept_list_stock,
      row.concept,
      row.tags,
      row.tag_list,
      row.ths_tags_stock,
    );
    return {
      symbol: row.ths_thscode_stock ?? row.thscode ?? null,
      name: row.ths_corp_cn_name_stock ?? row.ths_short_name_stock ?? row.short_name ?? null,
      industry: pickFirst(
        row.ths_the_ths_industry_stock,
        row.ths_industry_stock,
        row.ths_industry_name_stock,
        row.ths_sw_industry_stock,
        row.industry,
        row.industry_name,
      ),
      mainBusiness: pickFirst(
        row.ths_main_businuess_stock,
        row.ths_main_business_stock,
        row.ths_business_scope_stock,
        row.ths_mo_product_name_stock,
        row.main_business,
        row.business_scope,
      ),
      tags: Array.isArray(tagsRaw)
        ? tagsRaw.filter(Boolean)
        : typeof tagsRaw === "string"
          ? tagsRaw
              .split(/[，,;；|]/)
              .map((x) => x.trim())
              .filter(Boolean)
          : null,
      marketCap: null,
      pe: null,
      forwardPe: null,
      pb: null,
      ps: null,
      profitMargin: null,
      revenueGrowthYoy: null,
      earningsGrowthYoy: null,
      week52High: null,
      week52Low: null,
      latestQuarter: period,
      statementType,
      reportPeriod: period,
      revenue: toNumber(row.ths_revenue_stock ?? row.ths_operating_total_revenue_stock),
      netProfit: toNumber(row.ths_np_atoopc_stock ?? row.ths_np_stock),
      totalAssets: toNumber(row.ths_total_assets_stock),
      totalLiabilities: toNumber(row.ths_total_liab_stock),
      operatingCashflow: toNumber(row.ths_ncf_from_oa_stock),
      raw: row,
    };
  }
  return {
    symbol: data.Symbol ?? data.symbol ?? null,
    name: data.Name ?? data.name ?? null,
    industry: pickFirst(data.Industry, data.industry, data.industry_name),
    mainBusiness: pickFirst(data.BusinessDescription, data.business_description, data.main_business),
    tags: Array.isArray(data.tags)
      ? data.tags
      : typeof (data.concept ?? data.ths_the_ths_concept_index_stock) === "string"
        ? String(data.concept ?? data.ths_the_ths_concept_index_stock)
            .split(/[，,;；|]/)
            .map((x) => x.trim())
            .filter(Boolean)
        : null,
    marketCap: toNumber(data.MarketCapitalization ?? data.marketCap),
    pe: toNumber(data.PERatio ?? data.pe ?? data.TrailingPE),
    forwardPe: toNumber(data.ForwardPE),
    pb: toNumber(data.PriceToBookRatio),
    ps: toNumber(data.PriceToSalesRatioTTM),
    profitMargin: toNumber(data.ProfitMargin),
    revenueGrowthYoy: toNumber(data.QuarterlyRevenueGrowthYOY),
    earningsGrowthYoy: toNumber(data.QuarterlyEarningsGrowthYOY),
    week52High: toNumber(data["52WeekHigh"] ?? data.fifty_two_week?.high),
    week52Low: toNumber(data["52WeekLow"] ?? data.fifty_two_week?.low),
    latestQuarter: data.LatestQuarter ?? null,
    raw: data,
  };
}

export function pickTechnicalData(raw) {
  const result = raw?.result || raw || {};
  const data = result?.data || result;
  if (Array.isArray(data) && Array.isArray(data[0]) && data[0][0]) {
    const rows = data[0];
    const row = rows[rows.length - 1];
    const prev5Index = Math.max(0, rows.length - 6);
    const prev5 = rows[prev5Index] || null;
    const closeNow = toNumber(row.close);
    const closePrev5 = toNumber(prev5?.close);
    const change5d =
      closeNow != null && closePrev5 != null && closePrev5 !== 0 ? ((closeNow - closePrev5) / closePrev5) * 100 : null;
    const currentVolume = toNumber(row.volume);
    const volumes = rows
      .slice(Math.max(0, rows.length - 6), rows.length - 1)
      .map((x) => toNumber(x.volume))
      .filter((x) => x != null);
    const avgPrev5Volume = volumes.length > 0 ? volumes.reduce((sum, x) => sum + x, 0) / volumes.length : null;
    const volumeRatio =
      currentVolume != null && avgPrev5Volume != null && avgPrev5Volume > 0 ? currentVolume / avgPrev5Volume : null;
    return {
      latestDate: row.time ?? null,
      rsi: null,
      close: closeNow,
      changeRatio: toNumber(row.changeRatio),
      change5d,
      volumeRatio,
      avgPrev5Volume,
      raw: row,
    };
  }
  if (data?.["Technical Analysis: RSI"]) {
    const entries = Object.entries(data["Technical Analysis: RSI"]);
    if (entries.length > 0) {
      const [date, value] = entries[0];
      return {
        latestDate: date,
        rsi: toNumber(value?.RSI),
        raw: data,
      };
    }
  }
  return {
    latestDate: null,
    rsi: null,
    raw: data,
  };
}

export function pickSentimentData(raw) {
  const payload = raw?.result || raw || {};
  const data = payload?.data || payload;
  const resolved = resolveToolPayloadSync(raw);
  const content = resolved.content ?? data;
  const hits = content?.data?.hits || content?.hits || [];
  if (Array.isArray(hits)) {
    const latest = hits[0]?.source || hits[0] || null;
    const sentimentScore = latest?.newsSentiment?.[0]?.sentimentScore ?? latest?.weChatSentiment?.[0]?.sentimentScore ?? null;
    const sourceLabel = latest?.type || latest?.sourceName || latest?.siteName || null;
    return {
      itemCount: hits.length,
      latestHeadline: latest?.title ?? null,
      latestTime: latest?.publishTime ?? latest?.effectiveTime ?? null,
      latestTickerSentiment: sentimentScore,
      sourceLabel,
      fullContentFileUrl: data?.full_content_file_url ?? null,
      raw: content,
    };
  }
  if (Array.isArray(content)) {
    const latest = content[0] || null;
    return {
      itemCount: content.length,
      latestHeadline: latest?.headline ?? null,
      latestTime: latest?.datetime ?? null,
      latestTickerSentiment: null,
      fullContentFileUrl: data?.full_content_file_url ?? null,
      raw: content,
    };
  }
  const feed = content?.feed || [];
  const latest = feed[0] || null;
  return {
    itemCount: toNumber(content?.items) ?? feed.length,
    latestHeadline: latest?.title ?? null,
    latestTime: latest?.time_published ?? null,
    latestTickerSentiment: latest?.ticker_sentiment?.[0]?.ticker_sentiment_label ?? null,
    fullContentFileUrl: data?.full_content_file_url ?? null,
    raw: content,
  };
}

export function pickXSentimentData(raw) {
  const payload = raw?.result || raw || {};
  const data = payload?.data ?? payload;
  const resolved = resolveToolPayloadSync(raw);
  const content = resolved.content ?? data;

  let posts = [];
  if (Array.isArray(content)) posts = content;
  else if (Array.isArray(content?.data)) posts = content.data;
  else if (Array.isArray(content?.posts)) posts = content.posts;
  else if (Array.isArray(content?.results)) posts = content.results;

  const first = posts[0] || null;
  return {
    itemCount: posts.length || toNumber(content?.total) || 0,
    topPostText: first?.text ?? first?.full_text ?? first?.title ?? first?.headline ?? null,
    topPostTime: first?.created_at ?? first?.time ?? first?.datetime ?? null,
    sourceMode: Array.isArray(content) ? "fallback" : "direct",
    fullContentFileUrl: data?.full_content_file_url ?? null,
    raw: content,
  };
}

export function parseCapability(capability, raw) {
  if (capability === "quote") return pickQuoteData(raw);
  if (capability === "fundamentals") return pickFundamentalData(raw);
  if (capability === "technicals") return pickTechnicalData(raw);
  if (capability === "sentiment") return pickSentimentData(raw);
  if (capability === "x_sentiment") return pickXSentimentData(raw);
  return raw;
}
