/**
 * Technical Analysis Module (技术面分析模块)
 * 使用东方财富免费 API，无外部依赖，node 直接执行
 */

// ==================== 东方财富 API 数据获取 ====================

/**
 * 判断股票市场前缀
 * 沪市(6开头): secid=1.XXXXXX
 * 深市(0/3开头): secid=0.XXXXXX
 * 美股等直接用代号
 */
function getSecId(symbol) {
    const s = String(symbol);
    if (/^\d{6}$/.test(s)) {
        return s.startsWith('6') ? `1.${s}` : `0.${s}`;
    }
    // 如果已含前缀（如 1.600410）直接返回
    if (/^\d\.\d{6}$/.test(s)) return s;
    // 其他情况（美股等）尝试沪市
    return `1.${s}`;
}

async function fetchHistoricalData(symbol, limit = 200) {
    const secid = getSecId(symbol);
    const url = `https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=${secid}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&end=20500101&lmt=${limit}`;

    const response = await fetch(url);
    if (!response.ok) throw new Error(`获取历史数据失败: ${response.statusText}`);
    const data = await response.json();

    if (!data.data?.klines?.length) throw new Error(`未找到股票 ${symbol} 的历史数据`);

    // 解析K线数据: "日期,开盘,收盘,最高,最低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率"
    return data.data.klines.map(line => {
        const parts = line.split(',');
        return {
            date: parts[0],
            open: parseFloat(parts[1]),
            close: parseFloat(parts[2]),
            high: parseFloat(parts[3]),
            low: parseFloat(parts[4]),
            volume: parseInt(parts[5]),
            turnover: parseFloat(parts[6]),
            changePercent: parseFloat(parts[8])
        };
    });
}

export async function fetchQuote(symbol) {
    const secid = getSecId(symbol);
    const url = `https://push2.eastmoney.com/api/qt/stock/get?secid=${secid}&fields=f43,f44,f45,f46,f47,f48,f50,f55,f57,f58,f116,f117,f162,f167,f170`;

    const response = await fetch(url);
    if (!response.ok) throw new Error(`获取报价失败: ${response.statusText}`);
    const data = await response.json();
    const f = data.data;
    if (!f) throw new Error(`未找到股票 ${symbol} 的报价数据`);

    return {
        code: f.f57,
        name: f.f58,
        price: f.f43 / 100,       // 当前价（单位：分→元）
        high: f.f44 / 100,        // 最高
        low: f.f45 / 100,         // 最低
        open: f.f46 / 100,        // 开盘
        prevClose: f.f55 / 100,   // 昨收（注意：可能是小数格式）
        volume: f.f47,            // 成交量
        turnover: f.f48,          // 成交额
        volumeRatio: f.f50 / 100, // 量比
        marketCap: f.f116,        // 总市值
        floatMarketCap: f.f117,   // 流通市值
        pe: f.f162 / 100,         // 市盈率
        pb: f.f167 / 100,         // 市净率
        turnoverRate: f.f170 / 100 // 换手率
    };
}

// ==================== 指标计算（纯数学，无 API 依赖）====================

function calculateSMA(data, period) {
    const result = [];
    for (let i = 0; i < data.length; i++) {
        if (i < period - 1) { result.push(NaN); continue; }
        let sum = 0;
        for (let j = 0; j < period; j++) sum += data[i - j];
        result.push(sum / period);
    }
    return result;
}

function calculateEMA(data, period) {
    const result = [];
    const multiplier = 2 / (period + 1);
    let sum = 0;
    for (let i = 0; i < period; i++) { sum += data[i]; result.push(NaN); }
    result[period - 1] = sum / period;
    for (let i = period; i < data.length; i++) {
        result.push((data[i] - result[i - 1]) * multiplier + result[i - 1]);
    }
    return result;
}

function calculateRSI(data, period = 14) {
    const result = [];
    const gains = [], losses = [];
    for (let i = 1; i < data.length; i++) {
        const change = data[i] - data[i - 1];
        gains.push(change > 0 ? change : 0);
        losses.push(change < 0 ? Math.abs(change) : 0);
    }
    for (let i = 0; i < data.length; i++) {
        if (i < period) { result.push(NaN); continue; }
        const avgGain = gains.slice(i - period, i).reduce((a, b) => a + b, 0) / period;
        const avgLoss = losses.slice(i - period, i).reduce((a, b) => a + b, 0) / period;
        result.push(avgLoss === 0 ? 100 : 100 - (100 / (1 + avgGain / avgLoss)));
    }
    return result;
}

function calculateMACD(data) {
    const ema12 = calculateEMA(data, 12);
    const ema26 = calculateEMA(data, 26);
    const macd = data.map((_, i) => isNaN(ema12[i]) || isNaN(ema26[i]) ? NaN : ema12[i] - ema26[i]);
    const validMacd = macd.filter(v => !isNaN(v));
    const signal = calculateEMA(validMacd, 9);
    const paddedSignal = []; let si = 0;
    for (let i = 0; i < data.length; i++) {
        if (isNaN(macd[i])) paddedSignal.push(NaN);
        else { paddedSignal.push(signal[si] || NaN); si++; }
    }
    const histogram = data.map((_, i) => isNaN(macd[i]) || isNaN(paddedSignal[i]) ? NaN : macd[i] - paddedSignal[i]);
    return { macd, signal: paddedSignal, histogram };
}

function calculateBollingerBands(data, period = 20, stdDev = 2) {
    const middle = calculateSMA(data, period);
    const upper = [], lower = [];
    for (let i = 0; i < data.length; i++) {
        if (isNaN(middle[i])) { upper.push(NaN); lower.push(NaN); continue; }
        let sumSq = 0;
        for (let j = 0; j < period; j++) sumSq += Math.pow(data[i - j] - middle[i], 2);
        const std = Math.sqrt(sumSq / period);
        upper.push(middle[i] + stdDev * std);
        lower.push(middle[i] - stdDev * std);
    }
    return { upper, middle, lower };
}

function calculateKDJ(highs, lows, closes, period = 9) {
    if (closes.length < period) throw new Error('数据不足以计算KDJ');
    const rH = highs.slice(-period), rL = lows.slice(-period);
    const close = closes.at(-1);
    const hh = Math.max(...rH), ll = Math.min(...rL);
    const rsv = ((close - ll) / (hh - ll)) * 100;
    const k = rsv, d = k * 0.67 + 50 * 0.33, j = 3 * k - 2 * d;

    let signal = 'neutral', crossover = 'none', recommendation = '';
    if (k > 80 && d > 80) { signal = 'overbought'; recommendation = 'KDJ超买区域，注意回调风险'; }
    else if (k < 20 && d < 20) { signal = 'oversold'; recommendation = 'KDJ超卖区域，可能存在反弹机会'; }
    else if (k > d && k > 50) { signal = 'bullish'; recommendation = 'KDJ多头趋势'; }
    else if (k < d && k < 50) { signal = 'bearish'; recommendation = 'KDJ空头趋势'; }

    return { k: r(k), d: r(d), j: r(j), signal, crossover, recommendation };
}

function calculateATR(highs, lows, closes, period = 14) {
    if (closes.length < period + 1) throw new Error('数据不足以计算ATR');
    const trueRanges = [];
    for (let i = 1; i < closes.length; i++) {
        trueRanges.push(Math.max(highs[i] - lows[i], Math.abs(highs[i] - closes[i - 1]), Math.abs(lows[i] - closes[i - 1])));
    }
    const atr = trueRanges.slice(-period).reduce((a, b) => a + b, 0) / period;
    const price = closes.at(-1);
    const atrPercent = (atr / price) * 100;
    const volatility = atrPercent > 3 ? 'high' : atrPercent < 1 ? 'low' : 'moderate';
    const interpretation = volatility === 'high' ? '波动率较高，建议适当放宽止损空间'
        : volatility === 'low' ? '波动率较低，可设置较紧止损' : '波动率正常，止损位可按常规设置';
    return { atr: r(atr), atrPercent: r(atrPercent), volatility, stopLossSuggestion: r(price - 2 * atr), interpretation };
}

function r(v) { return Math.round(v * 100) / 100; }
const last = arr => arr.filter(v => !isNaN(v)).pop();

// ==================== 公开分析方法 ====================

export async function analyzeRSI(symbol, period = 14) {
    const history = await fetchHistoricalData(symbol);
    const closes = history.map(d => d.close);
    const rsiValues = calculateRSI(closes, period);
    const currentRSI = last(rsiValues) || 50;

    let signal = 'neutral', interpretation = '', divergence = 'none', recommendation = '';
    if (currentRSI >= 70) {
        signal = 'overbought'; interpretation = `RSI=${currentRSI.toFixed(2)}，超买区域`;
        recommendation = 'RSI超买，建议谨慎追高';
    } else if (currentRSI <= 30) {
        signal = 'oversold'; interpretation = `RSI=${currentRSI.toFixed(2)}，超卖区域`;
        recommendation = 'RSI超卖，可关注反弹机会';
    } else if (currentRSI >= 50) {
        signal = 'bullish'; interpretation = `RSI=${currentRSI.toFixed(2)}，多头区域`;
        recommendation = 'RSI显示多头动能';
    } else {
        signal = 'bearish'; interpretation = `RSI=${currentRSI.toFixed(2)}，空头区域`;
        recommendation = 'RSI显示空头动能';
    }

    const recentRSI = rsiValues.filter(v => !isNaN(v)).slice(-20);
    const recentPrices = closes.slice(-20);
    if (recentPrices.at(-1) > recentPrices[0] && recentRSI.at(-1) < recentRSI[0]) {
        divergence = 'bearish'; recommendation += '。注意：存在顶背离信号';
    } else if (recentPrices.at(-1) < recentPrices[0] && recentRSI.at(-1) > recentRSI[0]) {
        divergence = 'bullish'; recommendation += '。注意：存在底背离信号';
    }

    return { rsi: r(currentRSI), signal, interpretation, divergence, recommendation };
}

export async function analyzeMACD(symbol) {
    const history = await fetchHistoricalData(symbol);
    const closes = history.map(d => d.close);
    const { macd, signal, histogram } = calculateMACD(closes);
    const vm = macd.filter(v => !isNaN(v)), vs = signal.filter(v => !isNaN(v)), vh = histogram.filter(v => !isNaN(v));
    const cm = vm.at(-1), cs = vs.at(-1), ch = vh.at(-1), ph = vh.at(-2) || 0;

    let trend = cm > 0 && cs > 0 ? 'bullish' : cm < 0 && cs < 0 ? 'bearish' : 'neutral';
    let crossover = 'none', momentum = 'stable', recommendation = '';

    if (cm > cs && vm.at(-2) <= vs.at(-2)) {
        crossover = 'golden_cross'; recommendation = 'MACD金叉，买入信号';
    } else if (cm < cs && vm.at(-2) >= vs.at(-2)) {
        crossover = 'death_cross'; recommendation = 'MACD死叉，卖出信号';
    } else if (cm > cs) {
        recommendation = 'MACD位于信号线上方，多头延续';
    } else {
        recommendation = 'MACD位于信号线下方，空头延续';
    }

    if (ch > 0 && ch > ph) { momentum = 'strengthening'; recommendation += '，多头动量增强'; }
    else if (ch < 0 && ch < ph) { momentum = 'weakening'; recommendation += '，空头动量增强'; }

    return { macd: r(cm), signal: r(cs), histogram: r(ch), trend, crossover, momentum, recommendation };
}

export async function analyzeBollingerBands(symbol, period = 20, stdDev = 2) {
    const history = await fetchHistoricalData(symbol);
    const closes = history.map(d => d.close);
    const { upper, middle, lower } = calculateBollingerBands(closes, period, stdDev);
    const cp = closes.at(-1), cu = last(upper) || cp, cm = last(middle) || cp, cl = last(lower) || cp;
    const bandwidth = ((cu - cl) / cm) * 100;

    let position = cp > cu ? 'above_upper' : cp > cm ? 'upper_half' : cp > cl ? 'lower_half' : 'below_lower';
    const rbw = upper.slice(-10).map((u, i) => {
        const l = lower[upper.length - 10 + i], m = middle[upper.length - 10 + i];
        return isNaN(u) || isNaN(l) || isNaN(m) ? 0 : ((u - l) / m) * 100;
    });
    const avgBw = rbw.reduce((a, b) => a + b, 0) / rbw.filter(b => b > 0).length;
    const squeeze = bandwidth < avgBw * 0.7;

    let signal = 'neutral', recommendation = '';
    if (cp > cu) { signal = 'breakout_up'; recommendation = '突破布林带上轨，强势或超买'; }
    else if (cp < cl) { signal = 'breakout_down'; recommendation = '跌破布林带下轨，弱势或超卖'; }
    else if (cp > cm) { recommendation = '价格位于布林带中轨上方'; }
    else { recommendation = '价格位于布林带中轨下方'; }
    if (squeeze) recommendation += '。布林带收窄，可能即将突破';

    return { upper: r(cu), middle: r(cm), lower: r(cl), currentPrice: r(cp), position, bandwidth: r(bandwidth), squeeze, signal, recommendation };
}

export async function analyzeMovingAverages(symbol) {
    const history = await fetchHistoricalData(symbol);
    const closes = history.map(d => d.close);
    const sma5 = calculateSMA(closes, 5), sma10 = calculateSMA(closes, 10);
    const sma20 = calculateSMA(closes, 20), sma50 = calculateSMA(closes, 50), sma200 = calculateSMA(closes, 200);
    const ema12 = calculateEMA(closes, 12), ema26 = calculateEMA(closes, 26);
    const cp = closes.at(-1);
    const cs5 = last(sma5) || cp, cs10 = last(sma10) || cp, cs20 = last(sma20) || cp;
    const cs50 = last(sma50) || cp, cs200 = last(sma200) || cp;
    const ce12 = last(ema12) || cp, ce26 = last(ema26) || cp;

    let arrangement = cp > cs5 && cs5 > cs10 && cs10 > cs20 && cs20 > cs50 ? 'bullish_alignment'
        : cp < cs5 && cs5 < cs10 && cs10 < cs20 && cs20 < cs50 ? 'bearish_alignment' : 'mixed';

    const crosses = [];
    const vs5 = sma5.filter(v => !isNaN(v)), vs20 = sma20.filter(v => !isNaN(v));
    for (let i = vs5.length - 2; i >= Math.max(0, vs5.length - 10); i--) {
        if (vs5[i] <= vs20[i] && vs5[i + 1] > vs20[i + 1]) {
            crosses.push({ type: 'golden_cross', line1: 'sma5', line2: 'sma20', daysAgo: vs5.length - 1 - i }); break;
        } else if (vs5[i] >= vs20[i] && vs5[i + 1] < vs20[i + 1]) {
            crosses.push({ type: 'death_cross', line1: 'sma5', line2: 'sma20', daysAgo: vs5.length - 1 - i }); break;
        }
    }

    const support = Math.min(cs20, cs50), resistance = Math.max(cs10, cs5);
    let trend = cp > cs200 && arrangement === 'bullish_alignment' ? 'uptrend'
        : cp < cs200 && arrangement === 'bearish_alignment' ? 'downtrend' : 'sideways';

    let recommendation = arrangement === 'bullish_alignment' ? '均线多头排列，趋势向上'
        : arrangement === 'bearish_alignment' ? '均线空头排列，趋势向下' : '均线交织，趋势不明朗';
    if (crosses.length > 0) {
        const c = crosses[0];
        recommendation += `。${c.line1}与${c.line2}发生${c.type === 'golden_cross' ? '金叉' : '死叉'}(${c.daysAgo}日前)`;
    }

    return {
        sma: { sma5: r(cs5), sma10: r(cs10), sma20: r(cs20), sma50: r(cs50), sma200: r(cs200) },
        ema: { ema12: r(ce12), ema26: r(ce26) },
        arrangement, crosses, support: r(support), resistance: r(resistance), trend, recommendation
    };
}

export async function calculateTechnicalScore(symbol) {
    const history = await fetchHistoricalData(symbol);
    const closes = history.map(d => d.close), highs = history.map(d => d.high);
    const lows = history.map(d => d.low), volumes = history.map(d => d.volume);

    const [rsi, macd, bollinger, ma] = await Promise.all([
        analyzeRSI(symbol), analyzeMACD(symbol), analyzeBollingerBands(symbol), analyzeMovingAverages(symbol)
    ]);
    const kdj = calculateKDJ(highs, lows, closes);
    const atr = calculateATR(highs, lows, closes);

    const signals = [], warnings = [];
    let trendScore = 50;
    if (ma.arrangement === 'bullish_alignment') { trendScore += 25; signals.push('均线多头排列'); }
    else if (ma.arrangement === 'bearish_alignment') { trendScore -= 20; warnings.push('均线空头排列'); }
    if (ma.trend === 'uptrend') trendScore += 15;
    if (ma.crosses.some(c => c.type === 'golden_cross')) { trendScore += 10; signals.push('均线金叉'); }
    trendScore = Math.max(0, Math.min(100, trendScore));

    let momentumScore = 50;
    if (macd.crossover === 'golden_cross') { momentumScore += 20; signals.push('MACD金叉'); }
    else if (macd.crossover === 'death_cross') { momentumScore -= 20; warnings.push('MACD死叉'); }
    if (macd.momentum === 'strengthening') momentumScore += 10;
    if (rsi.signal === 'bullish') momentumScore += 10;
    else if (rsi.signal === 'bearish') momentumScore -= 10;
    if (rsi.divergence === 'bearish') { momentumScore -= 15; warnings.push('RSI顶背离'); }
    else if (rsi.divergence === 'bullish') { momentumScore += 15; signals.push('RSI底背离'); }
    momentumScore = Math.max(0, Math.min(100, momentumScore));

    let volatilityScore = 50;
    if (atr.volatility === 'low') volatilityScore += 20;
    else if (atr.volatility === 'high') volatilityScore -= 20;
    if (bollinger.squeeze) { volatilityScore += 10; signals.push('布林带收窄'); }
    volatilityScore = Math.max(0, Math.min(100, volatilityScore));

    let volumeScore = 50;
    const avgVol = volumes.slice(-20).reduce((a, b) => a + b, 0) / 20;
    const curVol = volumes.at(-1);
    if (curVol > avgVol * 1.5) { volumeScore += 20; signals.push('成交量放大'); }
    else if (curVol < avgVol * 0.5) { volumeScore -= 20; warnings.push('成交量萎缩'); }
    volumeScore = Math.max(0, Math.min(100, volumeScore));

    const totalScore = Math.round(trendScore * 0.35 + momentumScore * 0.30 + volatilityScore * 0.15 + volumeScore * 0.15);
    const grade = totalScore >= 80 ? 'A' : totalScore >= 70 ? 'B+' : totalScore >= 60 ? 'B' : totalScore >= 50 ? 'C+' : totalScore >= 40 ? 'C' : 'D';
    const overallRecommendation = totalScore >= 70 ? '技术面整体偏多，可考虑逢低布局'
        : totalScore >= 50 ? '技术面中性，建议观望' : '技术面偏空，谨慎操作';

    return {
        score: totalScore, grade, breakdown: {
            trend: { score: Math.round(trendScore), signal: ma.trend },
            momentum: { score: Math.round(momentumScore), signal: macd.trend },
            volatility: { score: Math.round(volatilityScore), signal: atr.volatility },
            volume: { score: Math.round(volumeScore), signal: curVol > avgVol ? 'above_avg' : 'below_avg' }
        }, signals, warnings, overallRecommendation
    };
}

export async function getFullTechnicalAnalysis(symbol) {
    const history = await fetchHistoricalData(symbol);
    const closes = history.map(d => d.close), highs = history.map(d => d.high), lows = history.map(d => d.low);

    const [rsi, macd, bollingerBands, movingAverages, score] = await Promise.all([
        analyzeRSI(symbol), analyzeMACD(symbol), analyzeBollingerBands(symbol),
        analyzeMovingAverages(symbol), calculateTechnicalScore(symbol)
    ]);
    const kdj = calculateKDJ(highs, lows, closes);
    const atr = calculateATR(highs, lows, closes);

    return { symbol, timestamp: new Date().toISOString(), rsi, macd, bollingerBands, movingAverages, kdj, atr, score };
}
