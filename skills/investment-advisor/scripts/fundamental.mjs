/**
 * Fundamental Analysis Module (基本面分析模块)
 * 使用东方财富免费 API，无外部依赖
 */

// ==================== 东方财富 API 数据获取 ====================

function getSecId(symbol) {
    const s = String(symbol);
    if (/^\d{6}$/.test(s)) return s.startsWith('6') ? `1.${s}` : `0.${s}`;
    if (/^\d\.\d{6}$/.test(s)) return s;
    return `1.${s}`;
}

function getMarketCode(symbol) {
    const s = String(symbol);
    return s.startsWith('6') ? 'SH' : 'SZ';
}

/** 获取实时行情 + 估值数据 (PE/PB/市值) */
async function fetchQuoteData(symbol) {
    const secid = getSecId(symbol);
    const url = `https://push2.eastmoney.com/api/qt/stock/get?secid=${secid}&fields=f43,f44,f45,f46,f47,f48,f50,f55,f57,f58,f84,f85,f116,f117,f162,f167,f170,f173`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`获取报价失败: ${response.statusText}`);
    const data = await response.json();
    const f = data.data;
    if (!f) throw new Error(`未找到股票 ${symbol} 的数据`);
    return {
        code: f.f57, name: f.f58,
        price: f.f43 / 100,
        marketCap: f.f116,         // 总市值
        floatMarketCap: f.f117,    // 流通市值
        pe: f.f162 / 100,          // 动态市盈率
        pb: f.f167 / 100,          // 市净率
        turnoverRate: f.f170 / 100,
        totalShares: f.f84,        // 总股本
        floatShares: f.f85,        // 流通股本
        roe: f.f173 / 100          // ROE (如果有)
    };
}

/** 获取主要财务指标（东方财富F10） */
async function fetchFinancialIndicators(symbol) {
    const s = String(symbol);
    const marketCode = getMarketCode(s);
    const url = `https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_LICO_FN_CPD&columns=ALL&filter=(SECURITY_CODE%3D%22${s}%22)&pageSize=4&sortColumns=REPORTDATE&sortTypes=-1&client=APP`;

    try {
        const response = await fetch(url);
        if (!response.ok) return null;
        const data = await response.json();
        return data.result?.data || null;
    } catch {
        return null;
    }
}

/** 获取利润表数据 */
async function fetchIncomeStatement(symbol) {
    const s = String(symbol);
    const url = `https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_DMSK_FN_INCOME&columns=ALL&filter=(SECURITY_CODE%3D%22${s}%22)&pageSize=4&sortColumns=REPORT_DATE&sortTypes=-1&client=APP`;

    try {
        const response = await fetch(url);
        if (!response.ok) return null;
        const data = await response.json();
        return data.result?.data || null;
    } catch {
        return null;
    }
}

/** 获取资产负债表数据 */
async function fetchBalanceSheet(symbol) {
    const s = String(symbol);
    const url = `https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_DMSK_FN_BALANCE&columns=ALL&filter=(SECURITY_CODE%3D%22${s}%22)&pageSize=4&sortColumns=REPORT_DATE&sortTypes=-1&client=APP`;

    try {
        const response = await fetch(url);
        if (!response.ok) return null;
        const data = await response.json();
        return data.result?.data || null;
    } catch {
        return null;
    }
}

/** 获取新闻资讯 */
async function fetchNews(symbol) {
    const s = String(symbol);
    const url = `https://search-api-web.eastmoney.com/search/jsonp?cb=&param=%7B%22uid%22%3A%22%22%2C%22keyword%22%3A%22${s}%22%2C%22type%22%3A%5B%22cmsArticleWebOld%22%5D%2C%22client%22%3A%22web%22%2C%22clientType%22%3A%22web%22%2C%22clientVersion%22%3A%22curr%22%2C%22param%22%3A%7B%22cmsArticleWebOld%22%3A%7B%22searchScope%22%3A%22default%22%2C%22sort%22%3A%22default%22%2C%22pageIndex%22%3A1%2C%22pageSize%22%3A5%7D%7D%7D`;

    try {
        const response = await fetch(url);
        if (!response.ok) return [];
        const text = await response.text();
        // 解析 JSONP 响应
        const json = text.replace(/^[^(]*\(/, '').replace(/\);?$/, '');
        const data = JSON.parse(json);
        const articles = data.result?.cmsArticleWebOld || [];
        return articles.map(a => ({ title: a.title, date: a.date, url: a.url }));
    } catch {
        return [];
    }
}

function r(v) { return Math.round((v || 0) * 100) / 100; }

// ==================== 分析方法 ====================

export async function analyzeValuation(symbol) {
    const quote = await fetchQuoteData(symbol);
    const indicators = await fetchFinancialIndicators(symbol);
    const latest = indicators?.[0] || {};

    const pe = quote.pe || 0;
    const pb = quote.pb || 0;
    const eps = latest.BASIC_EPS || (quote.price && pe > 0 ? quote.price / pe : 0);
    const bps = latest.BPS || (quote.price && pb > 0 ? quote.price / pb : 0);
    const marketCap = quote.marketCap || 0;
    const totalRevenue = latest.TOTAL_OPERATE_INCOME || 0;
    const ps = totalRevenue > 0 ? marketCap / totalRevenue : 0;
    const earningsGrowth = latest.PARENT_NETPROFIT_YOY_RATIO ? latest.PARENT_NETPROFIT_YOY_RATIO / 100 : 0;
    const peg = earningsGrowth > 0 ? pe / (earningsGrowth * 100) : pe > 0 ? 999 : 0;

    // 行业平均估值（A股科技行业参考）
    const industryPe = 30, industryPb = 3, industryPs = 2;

    const getStatus = (value, industry) => {
        if (value <= 0) return 'fair';
        const ratio = value / industry;
        return ratio < 0.8 ? 'undervalued' : ratio < 1 ? 'slightly_undervalued'
            : ratio <= 1.2 ? 'fair' : ratio <= 1.5 ? 'slightly_overvalued' : 'overvalued';
    };

    const pegInterpretation = peg < 1 ? '低估，考虑增长后估值便宜' : peg <= 1.5 ? '合理估值区间'
        : peg <= 2 ? '偏高，增长预期较高' : '高估，需谨慎';

    const fairPe = industryPe * (1 + earningsGrowth);
    const fairValue = eps > 0 ? eps * fairPe : 0;
    const upside = fairValue > 0 ? ((fairValue - quote.price) / quote.price) * 100 : 0;

    const valuations = [getStatus(pe, industryPe), getStatus(pb, industryPb), getStatus(ps, industryPs)];
    const under = valuations.filter(v => v.includes('undervalued')).length;
    const over = valuations.filter(v => v.includes('overvalued')).length;
    const summary = under > over ? '整体估值偏低，具有投资价值'
        : over > under ? '整体估值偏高，需关注增长能否支撑' : '估值处于合理区间';

    return {
        pe: { value: r(pe), industry: industryPe, status: getStatus(pe, industryPe) },
        pb: { value: r(pb), industry: industryPb, status: getStatus(pb, industryPb) },
        ps: { value: r(ps), industry: industryPs, status: getStatus(ps, industryPs) },
        peg: { value: r(peg), interpretation: pegInterpretation },
        fairValue: { estimated: r(fairValue), currentPrice: r(quote.price), upside: r(upside) },
        summary
    };
}

export async function analyzeProfitability(symbol) {
    const indicators = await fetchFinancialIndicators(symbol);
    const latest = indicators?.[0] || {};
    const prev = indicators?.[1] || {};

    const grossMargin = latest.GROSS_PROFIT_RATIO || 0;
    const netMargin = latest.NET_PROFIT_RATIO || 0;
    const roe = latest.WEIGHTAVG_ROE || 0;
    const roa = latest.ROA || 0;
    // 营业利润率需要从利润表计算，这里用毛利率近似
    const operatingMargin = grossMargin * 0.6; // 粗略估算

    const getTrend = (current, industry) => current > industry * 1.1 ? 'improving' : current < industry * 0.9 ? 'declining' : 'stable';
    const roeInterpretation = roe > 30 ? '资本回报极佳' : roe > 20 ? '资本回报优秀' : roe > 15 ? '资本回报良好' : roe > 10 ? '资本回报一般' : '资本回报较弱';

    const analysis = roe > 20 && netMargin > 20 ? '盈利能力卓越'
        : roe > 15 && netMargin > 15 ? '盈利能力良好' : roe > 10 && netMargin > 10 ? '盈利能力一般' : '盈利能力偏弱';

    return {
        grossMargin: { value: r(grossMargin), trend: getTrend(grossMargin, 30), industryAvg: 30 },
        netMargin: { value: r(netMargin), trend: getTrend(netMargin, 10), industryAvg: 10 },
        roe: { value: r(roe), trend: roe > 20 ? 'strong' : roe > 10 ? 'moderate' : 'weak', interpretation: roeInterpretation },
        roa: { value: r(roa), trend: getTrend(roa, 5) },
        operatingMargin: { value: r(operatingMargin), trend: getTrend(operatingMargin, 15) },
        analysis
    };
}

export async function analyzeGrowth(symbol) {
    const indicators = await fetchFinancialIndicators(symbol);
    if (!indicators || indicators.length < 2) {
        return {
            revenueGrowth: { quarterly: 0, yearly: 0, trend: 'stable', cagr3Year: 0 },
            earningsGrowth: { quarterly: 0, yearly: 0, trend: 'weak' },
            epsGrowth: { quarterly: 0, yearly: 0 },
            forecastGrowth: 10, analysis: '数据不足，无法判断增长趋势'
        };
    }

    const latest = indicators[0], prev = indicators[1];
    const revenueGrowth = latest.TOTAL_OPERATE_INCOME_YOY_RATIO ? latest.TOTAL_OPERATE_INCOME_YOY_RATIO / 100 : 0;
    const earningsGrowth = latest.PARENT_NETPROFIT_YOY_RATIO ? latest.PARENT_NETPROFIT_YOY_RATIO / 100 : 0;
    const epsGrowth = latest.BASIC_EPS && prev.BASIC_EPS ? ((latest.BASIC_EPS - prev.BASIC_EPS) / Math.abs(prev.BASIC_EPS)) * 100 : 0;

    const getRevTrend = g => g > 0.15 ? 'accelerating' : g < 0.05 ? 'decelerating' : 'stable';
    const getEarnTrend = g => g > 0.15 ? 'strong' : g > 0.05 ? 'moderate' : 'weak';
    const analysis = revenueGrowth > 0.15 && earningsGrowth > 0.15 ? '营收和盈利高速增长，成长性优异'
        : revenueGrowth > 0.1 && earningsGrowth > 0.1 ? '增长稳健，质量较高'
            : revenueGrowth > 0 || earningsGrowth > 0 ? '增长放缓' : '营收或盈利下滑，需警惕';

    return {
        revenueGrowth: { quarterly: r(revenueGrowth * 100), yearly: r(revenueGrowth * 100), trend: getRevTrend(revenueGrowth), cagr3Year: r(revenueGrowth * 100) },
        earningsGrowth: { quarterly: r(earningsGrowth * 100), yearly: r(earningsGrowth * 100), trend: getEarnTrend(earningsGrowth) },
        epsGrowth: { quarterly: r(epsGrowth), yearly: r(epsGrowth) },
        forecastGrowth: 10, analysis
    };
}

export async function analyzeFinancialHealth(symbol) {
    const indicators = await fetchFinancialIndicators(symbol);
    const latest = indicators?.[0] || {};

    const debtRatio = latest.DEBT_ASSET_RATIO || 50;
    const currentRatio = latest.CURRENT_RATIO || 1;
    const quickRatio = latest.QUICK_RATIO || currentRatio * 0.8;
    // 简化：用负债率估算 debt-to-equity
    const debtToEquity = debtRatio / (100 - debtRatio);

    const getDebtStatus = ratio => ratio < 0.5 ? { status: 'low', risk: 'low' } : ratio < 1.5 ? { status: 'moderate', risk: 'moderate' } : { status: 'high', risk: 'high' };
    const getRatioStatus = ratio => ratio >= 2 ? 'excellent' : ratio >= 1 ? 'healthy' : 'concern';

    const concerns = [], strengths = [];
    if (debtToEquity > 1.5) concerns.push('负债率较高');
    if (currentRatio < 1) concerns.push('流动比率低于1');
    if (quickRatio < 0.8) concerns.push('速动比率偏低');
    if (debtToEquity < 0.5) strengths.push('负债率低');
    if (currentRatio > 1.5) strengths.push('流动性强');
    if (quickRatio > 1) strengths.push('速动比率健康');

    const overallHealth = concerns.length === 0 && strengths.length >= 2 ? 'excellent'
        : concerns.length <= 1 ? 'good' : concerns.length <= 2 ? 'fair' : 'concern';

    return {
        debtToEquity: { value: r(debtToEquity), ...getDebtStatus(debtToEquity) },
        currentRatio: { value: r(currentRatio), status: getRatioStatus(currentRatio) },
        quickRatio: { value: r(quickRatio), status: getRatioStatus(quickRatio) },
        debtAssetRatio: { value: r(debtRatio), interpretation: debtRatio > 60 ? '偏高' : debtRatio > 40 ? '适中' : '健康' },
        overallHealth, concerns, strengths
    };
}

export async function getAnalystRating(symbol) {
    // 东方财富没有直接的分析师评级 API，返回基于估值的模拟评级
    const quote = await fetchQuoteData(symbol);
    const pe = quote.pe || 0;
    const pb = quote.pb || 0;
    const mean = pe > 0 && pe < 20 ? 'buy' : pe > 50 ? 'sell' : 'hold';
    return { mean, count: 0, strongBuy: 0, buy: 0, hold: 0, sell: 0, strongSell: 0, targetPrice: { low: 0, mean: 0, high: 0 }, note: '基于估值模拟，非分析师实际评级' };
}

export async function analyzeNewsSentiment(symbol) {
    const news = await fetchNews(symbol);
    const recentHeadlines = news.slice(0, 5).map(n => n.title).filter(Boolean);

    const positiveWords = ['涨', '盈利', '突破', '利好', '增长', '超预期', '上调', '创新高', '大涨', '买入', '领涨', '飙升'];
    const negativeWords = ['跌', '亏损', '下跌', '利空', '下滑', '不及预期', '下调', '创新低', '大跌', '卖出', '暴跌', '减持'];
    let score = 0;
    for (const title of recentHeadlines) {
        for (const w of positiveWords) if (title.includes(w)) score += 0.2;
        for (const w of negativeWords) if (title.includes(w)) score -= 0.2;
    }
    score = Math.max(-1, Math.min(1, score));
    return { overall: score > 0.2 ? 'positive' : score < -0.2 ? 'negative' : 'neutral', score: r(score), keyTopics: [], recentHeadlines };
}

export async function calculateFundamentalScore(symbol) {
    const [valuation, profitability, growth, financialHealth] = await Promise.all([
        analyzeValuation(symbol), analyzeProfitability(symbol), analyzeGrowth(symbol), analyzeFinancialHealth(symbol)
    ]);

    const weights = { valuation: 0.25, profitability: 0.30, growth: 0.25, financialHealth: 0.20 };

    let vs = 50;
    if (valuation.pe.status === 'undervalued') vs += 25;
    else if (valuation.pe.status === 'slightly_undervalued') vs += 15;
    else if (valuation.pe.status === 'overvalued') vs -= 20;
    else if (valuation.pe.status === 'slightly_overvalued') vs -= 10;
    if (valuation.peg.value < 1) vs += 15;
    else if (valuation.peg.value > 2) vs -= 10;

    let ps = 50;
    if (profitability.roe.value > 30) ps += 25;
    else if (profitability.roe.value > 20) ps += 15;
    else if (profitability.roe.value > 10) ps += 5;
    else ps -= 10;
    if (profitability.netMargin.value > 20) ps += 15;
    else if (profitability.netMargin.value < 10) ps -= 10;

    let gs = 50;
    if (growth.revenueGrowth.yearly > 15) gs += 25;
    else if (growth.revenueGrowth.yearly > 10) gs += 15;
    else if (growth.revenueGrowth.yearly < 5) gs -= 15;
    if (growth.earningsGrowth.yearly > 15) gs += 15;
    else if (growth.earningsGrowth.yearly < 5) gs -= 10;

    let fhs = 50;
    if (financialHealth.overallHealth === 'excellent') fhs += 30;
    else if (financialHealth.overallHealth === 'good') fhs += 15;
    else if (financialHealth.overallHealth === 'fair') fhs -= 10;
    else fhs -= 25;
    if (financialHealth.debtToEquity.risk === 'low') fhs += 10;
    else if (financialHealth.debtToEquity.risk === 'high') fhs -= 15;

    vs = Math.max(0, Math.min(100, vs));
    ps = Math.max(0, Math.min(100, ps));
    gs = Math.max(0, Math.min(100, gs));
    fhs = Math.max(0, Math.min(100, fhs));

    const totalScore = Math.round(vs * weights.valuation + ps * weights.profitability + gs * weights.growth + fhs * weights.financialHealth);
    const grade = totalScore >= 80 ? 'A' : totalScore >= 70 ? 'B+' : totalScore >= 60 ? 'B' : totalScore >= 50 ? 'C+' : totalScore >= 40 ? 'C' : 'D';
    const summary = totalScore >= 70 ? '基本面优秀，适合中长期投资' : totalScore >= 50 ? '基本面良好，有一定投资价值' : '基本面一般，投资需谨慎';

    return {
        score: totalScore, grade,
        breakdown: {
            valuation: { score: Math.round(vs), weight: weights.valuation },
            profitability: { score: Math.round(ps), weight: weights.profitability },
            growth: { score: Math.round(gs), weight: weights.growth },
            financialHealth: { score: Math.round(fhs), weight: weights.financialHealth }
        },
        investmentGrade: ps >= 70 && fhs >= 70 ? 'quality' : vs >= 70 ? 'value' : gs >= 70 ? 'growth' : totalScore < 40 ? 'avoid' : 'speculative',
        riskLevel: fhs >= 70 && vs >= 60 ? 'low' : fhs < 50 || gs < 40 ? 'high' : 'moderate',
        summary
    };
}

export async function getFullFundamentalAnalysis(symbol) {
    const [valuation, profitability, growth, financialHealth, analystRating, sentiment, score] = await Promise.all([
        analyzeValuation(symbol), analyzeProfitability(symbol), analyzeGrowth(symbol),
        analyzeFinancialHealth(symbol), getAnalystRating(symbol), analyzeNewsSentiment(symbol),
        calculateFundamentalScore(symbol)
    ]);
    return { symbol, timestamp: new Date().toISOString(), valuation, profitability, growth, financialHealth, analystRating, sentiment, score };
}
