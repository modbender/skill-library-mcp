#!/usr/bin/env node
/**
 * 기술적 지표 계산 모듈 (V2 - 최적화 및 표준화 버전)
 */

/**
 * 데이터 정제 유틸리티
 * @param {any[]} data - 입력 데이터
 * @param {Object} options - { newestFirst: false }
 */
function sanitizePrices(data, options = {}) {
  if (!Array.isArray(data)) return [];

  const { newestFirst = false } = options;
  let prices = data.map(v => {
    if (typeof v === 'object' && v !== null && 'close' in v) return Number(v.close);
    return Number(v);
  });

  // NaN, Infinity 제거
  prices = prices.filter(v => Number.isFinite(v));

  if (newestFirst) {
    prices.reverse();
  }

  return prices;
}

/**
 * 캔들 데이터 정제 유틸리티 (ATR 등용)
 */
function sanitizeCandles(data, options = {}) {
  if (!Array.isArray(data)) return [];
  const { newestFirst = false } = options;

  let candles = data.map(c => ({
    high: Number(c.high),
    low: Number(c.low),
    close: Number(c.close),
    open: Number(c.open)
  })).filter(c =>
    Number.isFinite(c.high) &&
    Number.isFinite(c.low) &&
    Number.isFinite(c.close)
  );

  if (newestFirst) {
    candles.reverse();
  }
  return candles;
}

/**
 * RSI (Relative Strength Index)
 */
function calculateRSI(data, period = 14, options = {}) {
  const prices = sanitizePrices(data, options);
  if (prices.length < period + 1) return { value: null };

  let gains = 0;
  let losses = 0;

  for (let i = 1; i <= period; i++) {
    const change = prices[i] - prices[i - 1];
    if (change > 0) gains += change;
    else losses -= change;
  }

  let avgGain = gains / period;
  let avgLoss = losses / period;

  for (let i = period + 1; i < prices.length; i++) {
    const change = prices[i] - prices[i - 1];
    if (change > 0) {
      avgGain = (avgGain * (period - 1) + change) / period;
      avgLoss = (avgLoss * (period - 1)) / period;
    } else {
      avgGain = (avgGain * (period - 1)) / period;
      avgLoss = (avgLoss * (period - 1) - change) / period;
    }
  }

  if (avgLoss === 0) return { value: 100, meta: { avgGain, avgLoss } };
  if (avgGain === 0) return { value: 0, meta: { avgGain, avgLoss } };

  const rs = avgGain / avgLoss;
  const rsi = 100 - (100 / (1 + rs));
  return { value: rsi, meta: { avgGain, avgLoss } };
}

/**
 * EMA (지수이동평균) - O(N)
 */
function calculateEMA(data, period, options = {}) {
  const prices = sanitizePrices(data, options);
  const { returnSeries = false } = options;
  if (prices.length < period) return returnSeries ? [] : { value: null };

  const multiplier = 2 / (period + 1);
  let ema = prices.slice(0, period).reduce((a, b) => a + b, 0) / period;
  const series = [ema];

  for (let i = period; i < prices.length; i++) {
    ema = (prices[i] - ema) * multiplier + ema;
    if (returnSeries) series.push(ema);
  }

  return returnSeries ? series : { value: ema };
}

/**
 * MACD (Moving Average Convergence Divergence) - O(N)
 */
function calculateMACD(data, fastPeriod = 12, slowPeriod = 26, signalPeriod = 9, options = {}) {
  const prices = sanitizePrices(data, options);
  if (prices.length < slowPeriod + signalPeriod) return { value: null };

  const fastEMAs = calculateEMA(prices, fastPeriod, { returnSeries: true });
  const slowEMAs = calculateEMA(prices, slowPeriod, { returnSeries: true });

  const diff = slowPeriod - fastPeriod;
  const macdLine = [];
  for (let i = 0; i < slowEMAs.length; i++) {
    macdLine.push(fastEMAs[i + diff] - slowEMAs[i]);
  }

  const signalLineSeries = calculateEMA(macdLine, signalPeriod, { returnSeries: true });
  const currentMACD = macdLine[macdLine.length - 1];
  const currentSignal = signalLineSeries[signalLineSeries.length - 1];

  return {
    value: currentMACD,
    signal: currentSignal,
    histogram: currentMACD - currentSignal,
    meta: { fastPeriod, slowPeriod, signalPeriod }
  };
}

/**
 * Bollinger Bands
 */
function calculateBollingerBands(data, period = 20, multiplier = 2, options = {}) {
  const prices = sanitizePrices(data, options);
  if (prices.length < period) return { value: null };

  const slice = prices.slice(-period);
  const ma = slice.reduce((a, b) => a + b, 0) / period;
  const squaredDiffs = slice.map(p => Math.pow(p - ma, 2));
  const variance = squaredDiffs.reduce((a, b) => a + b, 0) / period;
  const stdDev = Math.sqrt(variance);

  if (stdDev === 0) {
    return { value: ma, upper: ma, lower: ma, meta: { stdDev: 0 } };
  }

  return {
    value: ma,
    upper: ma + (multiplier * stdDev),
    lower: ma - (multiplier * stdDev),
    meta: { stdDev, period, multiplier }
  };
}

/**
 * ATR (Average True Range)
 */
function calculateATR(data, period = 14, options = {}) {
  const candles = sanitizeCandles(data, options);
  if (candles.length < period + 1) return { value: null };

  const trs = [];
  for (let i = 1; i < candles.length; i++) {
    const tr = Math.max(
      candles[i].high - candles[i].low,
      Math.abs(candles[i].high - candles[i - 1].close),
      Math.abs(candles[i].low - candles[i - 1].close)
    );
    trs.push(tr);
  }

  let atr = trs.slice(0, period).reduce((a, b) => a + b, 0) / period;
  for (let i = period; i < trs.length; i++) {
    atr = (atr * (period - 1) + trs[i]) / period;
  }

  return { value: atr, meta: { period } };
}

module.exports = {
  sanitizePrices,
  sanitizeCandles,
  calculateRSI,
  calculateEMA,
  calculateMACD,
  calculateBollingerBands,
  calculateATR
};

// CLI 및 단위 테스트
if (require.main === module) {
  const args = process.argv.slice(2);
  const isJson = args.includes('--json');
  const newestFirst = args.includes('--newest-first');

  const testPrices = [
    44, 44.5, 43.5, 44.5, 44, 43.5, 44, 44.5, 44, 43.5,
    44.5, 45, 45.5, 46, 45.5, 46, 46.5, 47, 46.5, 47,
    47.5, 48, 48.5, 49, 48.5, 48, 47.5, 47, 46.5, 46,
    45.5, 45, 44.5, 44, 43.5, 43, 42.5, 42, 41.5, 41
  ];

  const testCandles = testPrices.map(p => ({ high: p + 1, low: p - 1, close: p }));

  const results = {
    rsi: calculateRSI(testPrices, 14, { newestFirst }),
    macd: calculateMACD(testPrices, 12, 26, 9, { newestFirst }),
    atr: calculateATR(testCandles, 14, { newestFirst }),
    bb: calculateBollingerBands(testPrices, 20, 2, { newestFirst })
  };

  if (isJson) {
    console.log(JSON.stringify(results, null, 2));
  } else {
    console.log('=== Indicators V2 Unit Tests ===');
    console.log('데이터 방향:', newestFirst ? '최신 -> 과거' : '과거 -> 최신');
    console.log('RSI(14):', results.rsi.value?.toFixed(2));
    console.log('MACD Line:', results.macd.value?.toFixed(2));
    console.log('MACD Signal:', results.macd.signal?.toFixed(2));
    console.log('ATR(14):', results.atr.value?.toFixed(2));
    console.log('BB Upper:', results.bb.upper?.toFixed(2));
  }
}
