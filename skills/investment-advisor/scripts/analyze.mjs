#!/usr/bin/env node
/**
 * Investment Advisor CLI (投资分析助手)
 * 数据源: 东方财富免费 API，无需 GATEWAY_URL
 * 
 * 用法:
 *   node scripts/analyze.mjs <symbol> [mode]
 * 
 * mode 参数:
 *   full         - 完整分析（技术面+基本面+综合建议）[默认]
 *   technical    - 仅技术面分析
 *   fundamental  - 仅基本面分析
 *   signal       - 交易信号
 *   portfolio    - 投资组合分析（symbol用逗号分隔多只股票）
 *   compare      - 股票对比（symbol用逗号分隔多只股票）
 * 
 * 示例:
 *   node scripts/analyze.mjs 600410 full
 *   node scripts/analyze.mjs 000001 technical
 *   node scripts/analyze.mjs 600410,000001,300750 portfolio
 * 
 * 输出: JSON 格式到 stdout
 */

import * as technical from './technical.mjs';
import * as fundamental from './fundamental.mjs';

// ==================== 综合分析逻辑 ====================

function r(v) { return Math.round(v * 100) / 100; }

function calculateSentimentScore(sentiment, analystRating) {
    let score = 50;
    if (sentiment.overall === 'positive') score += 20;
    else if (sentiment.overall === 'negative') score -= 20;
    score += sentiment.score * 20;
    if (analystRating.mean === 'buy') score += 20;
    else if (analystRating.mean === 'sell') score -= 20;
    const buyCount = analystRating.strongBuy + analystRating.buy;
    const sellCount = analystRating.sell + analystRating.strongSell;
    const total = buyCount + analystRating.hold + sellCount;
    if (total > 0) {
        if (buyCount / total > 0.6) score += 10;
        else if (buyCount / total < 0.3) score -= 10;
    }
    return Math.max(0, Math.min(100, score));
}

function determineRecommendation(overallScore, techScore, fundScore, financialHealth) {
    let grade, recommendation, confidence, riskLevel;

    if (overallScore >= 85) grade = 'A+'; else if (overallScore >= 80) grade = 'A';
    else if (overallScore >= 75) grade = 'A-'; else if (overallScore >= 70) grade = 'B+';
    else if (overallScore >= 65) grade = 'B'; else if (overallScore >= 60) grade = 'B-';
    else if (overallScore >= 55) grade = 'C+'; else if (overallScore >= 50) grade = 'C';
    else if (overallScore >= 45) grade = 'C-'; else if (overallScore >= 40) grade = 'D+';
    else if (overallScore >= 35) grade = 'D'; else grade = 'D-';

    if (overallScore >= 80) recommendation = 'strong_buy';
    else if (overallScore >= 65) recommendation = 'buy';
    else if (overallScore >= 40) recommendation = 'hold';
    else if (overallScore >= 25) recommendation = 'sell';
    else recommendation = 'strong_sell';

    const scoreDiff = Math.abs(techScore - fundScore);
    if (scoreDiff <= 10 && overallScore >= 70) confidence = 'high';
    else if (scoreDiff <= 20) confidence = 'medium_high';
    else if (scoreDiff <= 30) confidence = 'medium';
    else confidence = 'low';

    if (financialHealth.overallHealth === 'excellent' && fundScore >= 70) riskLevel = 'low';
    else if (financialHealth.overallHealth === 'good') riskLevel = 'moderate_low';
    else if (financialHealth.overallHealth === 'fair') riskLevel = 'moderate';
    else riskLevel = financialHealth.concerns?.length > 2 ? 'high' : 'moderate_high';

    return { grade, recommendation, confidence, riskLevel };
}

function generateAction(recommendation, currentPrice, support, resistance, fairValue, atr) {
    let signal = 'hold';
    let entryPrice = `${r(currentPrice * 0.98)}-${r(currentPrice * 1.02)}`;
    let stopLoss = currentPrice - 2 * atr.atr;
    const takeProfit = [resistance, fairValue].filter(p => p > currentPrice).slice(0, 2);
    let positionSize = 'moderate', holdingPeriod = '1-3 months';

    if (recommendation === 'strong_buy' || recommendation === 'buy') {
        signal = 'buy';
        entryPrice = `${r(support * 1.02)}-${r(currentPrice * 1.01)}`;
        stopLoss = support * 0.98;
        if (recommendation === 'strong_buy') { positionSize = 'large'; holdingPeriod = '3-6 months'; }
    } else if (recommendation === 'sell' || recommendation === 'strong_sell') {
        signal = 'sell'; positionSize = 'small'; stopLoss = currentPrice + 2 * atr.atr;
    }

    const finalTP = takeProfit.length > 0 ? takeProfit : [currentPrice * 1.1, currentPrice * 1.2];
    return { signal, entryPrice, stopLoss: r(stopLoss), takeProfit: finalTP.map(r), positionSize, holdingPeriod };
}

function generateReasoning(symbol, tech, fund, recommendation) {
    const parts = [];
    const supporting = [];
    if (tech.score.score >= 60) supporting.push('技术面表现良好');
    if (fund.score.score >= 60) supporting.push('基本面稳健');
    if (fund.profitability.roe.value > 15) supporting.push('ROE优秀');
    if (tech.score.signals.length > 0) supporting.push(tech.score.signals[0]);

    const risks = [];
    if (tech.score.warnings.length > 0) risks.push(tech.score.warnings[0]);
    if (fund.valuation.pe.status === 'overvalued') risks.push('估值偏高');
    if (fund.financialHealth.concerns.length > 0) risks.push(fund.financialHealth.concerns[0]);

    if (recommendation === 'buy' || recommendation === 'strong_buy') {
        parts.push(`基于综合分析，${symbol}的投资价值得到认可。${supporting.slice(0, 3).join('、')}等因素支持买入建议。`);
        if (risks.length > 0) parts.push(`需要注意的风险包括：${risks.join('、')}。建议设置合理止损，控制风险。`);
    } else if (recommendation === 'sell' || recommendation === 'strong_sell') {
        parts.push(`综合分析显示${symbol}存在较多不利因素。${risks.join('、')}等风险较为突出，建议谨慎操作或暂时回避。`);
    } else {
        parts.push(`${symbol}当前处于观望状态。技术面和基本面信号不够明确，建议等待更清晰的方向性信号再进行操作。`);
    }
    return parts.join('');
}

// ==================== 各模式实现 ====================

async function fullAnalysis(symbol) {
    // 使用东方财富 API 获取报价 + 分析
    const [technicalFull, fundamentalFull, quote] = await Promise.all([
        technical.getFullTechnicalAnalysis(symbol),
        fundamental.getFullFundamentalAnalysis(symbol),
        technical.fetchQuote(symbol)
    ]);

    const currentPrice = quote.price;
    const companyName = quote.name || symbol;

    const techScore = technicalFull.score.score;
    const fundScore = fundamentalFull.score.score;
    const sentScore = calculateSentimentScore(fundamentalFull.sentiment, fundamentalFull.analystRating);
    const overallScore = Math.round(techScore * 0.35 + fundScore * 0.45 + sentScore * 0.20);

    const { grade, recommendation, confidence, riskLevel } = determineRecommendation(
        overallScore, techScore, fundScore, fundamentalFull.financialHealth
    );

    const highlights = [];
    if (fundamentalFull.profitability.roe.value > 20) highlights.push(`ROE优秀(${fundamentalFull.profitability.roe.value}%)`);
    if (fundamentalFull.growth.revenueGrowth.yearly > 10) highlights.push(`营收增长强劲(${fundamentalFull.growth.revenueGrowth.yearly}%)`);
    if (fundamentalFull.financialHealth.strengths.length > 0) highlights.push(...fundamentalFull.financialHealth.strengths.slice(0, 3));
    if (fundamentalFull.valuation.pe.status === 'undervalued') highlights.push('估值偏低');

    const concerns = [];
    if (fundamentalFull.profitability.roe.value < 10) concerns.push(`ROE偏低(${fundamentalFull.profitability.roe.value}%)`);
    if (fundamentalFull.growth.revenueGrowth.yearly < 5) concerns.push(`增长放缓(${fundamentalFull.growth.revenueGrowth.yearly}%)`);
    if (fundamentalFull.financialHealth.concerns.length > 0) concerns.push(...fundamentalFull.financialHealth.concerns.slice(0, 3));
    if (fundamentalFull.valuation.pe.status === 'overvalued') concerns.push('估值偏高');

    const action = generateAction(
        recommendation, currentPrice,
        technicalFull.movingAverages.support, technicalFull.movingAverages.resistance,
        fundamentalFull.valuation.fairValue.estimated, technicalFull.atr
    );

    const reasoning = generateReasoning(symbol, technicalFull, fundamentalFull, recommendation);

    return {
        symbol, companyName, currentPrice, timestamp: new Date().toISOString(),
        summary: { overallScore, grade, recommendation, confidence, riskLevel },
        technical: {
            score: techScore, signals: technicalFull.score.signals,
            warnings: technicalFull.score.warnings,
            support: technicalFull.movingAverages.support,
            resistance: technicalFull.movingAverages.resistance,
            indicators: {
                rsi: technicalFull.rsi, macd: technicalFull.macd,
                bollingerBands: technicalFull.bollingerBands, movingAverages: technicalFull.movingAverages,
                kdj: technicalFull.kdj, atr: technicalFull.atr
            }
        },
        fundamental: {
            score: fundScore,
            highlights: highlights.slice(0, 5), concerns: concerns.slice(0, 5),
            fairValue: fundamentalFull.valuation.fairValue.estimated,
            details: {
                valuation: fundamentalFull.valuation, profitability: fundamentalFull.profitability,
                growth: fundamentalFull.growth, financialHealth: fundamentalFull.financialHealth,
                analystRating: fundamentalFull.analystRating
            }
        },
        sentiment: {
            score: sentScore, newsSentiment: fundamentalFull.sentiment.overall,
            analystRating: fundamentalFull.analystRating.mean,
            recentNews: fundamentalFull.sentiment.recentHeadlines.slice(0, 3)
        },
        action, reasoning
    };
}

async function tradeSignal(symbol) {
    const report = await fullAnalysis(symbol);
    const currentPrice = report.currentPrice;
    let strength = 'moderate';
    if (report.summary.overallScore >= 75 || report.summary.overallScore <= 25) strength = 'strong';
    else if (report.summary.overallScore >= 55 && report.summary.overallScore <= 65) strength = 'weak';

    const conf = report.summary.confidence === 'high' ? 0.85
        : report.summary.confidence === 'medium_high' ? 0.72
            : report.summary.confidence === 'medium' ? 0.60 : 0.45;

    let timing = 'immediate_or_pullback';
    if (report.technical.signals.some(s => s.includes('金叉') || s.includes('多头'))) timing = 'immediate';
    else if (report.technical.warnings.some(w => w.includes('超买'))) timing = 'pullback';

    const stopLoss = report.action.stopLoss;
    const profitTarget = report.action.takeProfit[0] || currentPrice * 1.1;
    let maxPos = '5% of portfolio';
    if (report.summary.riskLevel === 'low') maxPos = '10-15% of portfolio';
    else if (report.summary.riskLevel === 'moderate_low') maxPos = '8-10% of portfolio';
    else if (report.summary.riskLevel === 'moderate_high') maxPos = '3-5% of portfolio';
    else if (report.summary.riskLevel === 'high') maxPos = '1-2% of portfolio';

    return {
        symbol, signal: report.action.signal, strength, confidence: conf,
        entryStrategy: { suggestedEntry: r(currentPrice), entryRange: [r(currentPrice * 0.97), r(currentPrice * 1.01)], timing },
        riskManagement: {
            stopLoss, stopLossPercent: r(((currentPrice - stopLoss) / currentPrice) * 100),
            maxPositionSize: maxPos, riskRewardRatio: r((profitTarget - currentPrice) / (currentPrice - stopLoss))
        },
        profitTargets: report.action.takeProfit.map((price, i) => ({
            price, percent: r(((price - currentPrice) / currentPrice) * 100), probability: i === 0 ? 0.65 : 0.45
        })),
        supportingFactors: [...report.technical.signals.slice(0, 2), ...report.fundamental.highlights.slice(0, 2)],
        riskFactors: [...report.technical.warnings.slice(0, 2), ...report.fundamental.concerns.slice(0, 2)],
        reasoning: report.reasoning
    };
}

async function portfolioAnalysis(symbols) {
    const analyses = await Promise.all(symbols.map(async symbol => {
        try {
            const report = await fullAnalysis(symbol);
            return { symbol, score: report.summary.overallScore, recommendation: report.action.signal };
        } catch { return { symbol, score: 50, recommendation: 'hold' }; }
    }));

    const totalScore = Math.round(analyses.reduce((s, a) => s + a.score, 0) / analyses.length);
    const diversification = symbols.length >= 5 ? 'excellent' : symbols.length >= 3 ? 'good' : 'moderate';
    const riskLevel = totalScore >= 70 ? 'low' : totalScore >= 50 ? 'moderate' : 'high';

    const suggestions = [];
    const sells = analyses.filter(a => a.recommendation === 'sell');
    const buys = analyses.filter(a => a.recommendation === 'buy');
    if (sells.length > 0) suggestions.push(`考虑减持：${sells.map(x => x.symbol).join('、')}`);
    if (buys.length > 0) suggestions.push(`可考虑增仓：${buys.map(x => x.symbol).join('、')}`);
    if (symbols.length < 5) suggestions.push('建议增加持仓数量以提高分散度');

    return {
        portfolio: { totalScore, diversification, riskLevel },
        holdings: analyses, suggestions,
        rebalanceRecommendation: {
            needed: sells.length > analyses.length * 0.3 || buys.length > analyses.length * 0.3,
            reason: sells.length > analyses.length * 0.3 ? '组合中部分标的建议调整' : '当前配置较为均衡'
        }
    };
}

async function compareStocks(symbols) {
    const reports = await Promise.all(symbols.map(async symbol => {
        const report = await fullAnalysis(symbol);
        return { symbol, score: report.summary.overallScore, grade: report.summary.grade, recommendation: report.summary.recommendation };
    }));
    const sorted = [...reports].sort((a, b) => b.score - a.score);
    return {
        comparison: sorted, best: sorted[0].symbol, worst: sorted.at(-1).symbol,
        analysis: `在比较的${symbols.length}只股票中，${sorted[0].symbol}评分最高(${sorted[0].score}分)，建议${sorted[0].recommendation}；${sorted.at(-1).symbol}评分最低(${sorted.at(-1).score}分)，建议${sorted.at(-1).recommendation}。`
    };
}

// ==================== CLI 入口 ====================

const args = process.argv.slice(2);
const symbolArg = args[0];
const mode = args[1] || 'full';

if (!symbolArg) {
    console.error(JSON.stringify({ error: '请提供股票代码。用法: node scripts/analyze.mjs <symbol> [mode]' }));
    process.exit(1);
}

const symbols = symbolArg.split(',');

try {
    let result;
    switch (mode) {
        case 'technical': result = await technical.getFullTechnicalAnalysis(symbols[0]); break;
        case 'fundamental': result = await fundamental.getFullFundamentalAnalysis(symbols[0]); break;
        case 'signal': result = await tradeSignal(symbols[0]); break;
        case 'portfolio': result = await portfolioAnalysis(symbols); break;
        case 'compare': result = await compareStocks(symbols); break;
        case 'full':
        default: result = await fullAnalysis(symbols[0]); break;
    }
    console.log(JSON.stringify(result, null, 2));
} catch (error) {
    console.error(JSON.stringify({ error: error.message, stack: error.stack }));
    process.exit(1);
}
