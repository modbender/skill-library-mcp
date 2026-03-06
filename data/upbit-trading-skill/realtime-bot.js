#!/usr/bin/env node
/**
 * Upbit 실시간 모니터링 봇
 * - 10초마다 가격 체크
 * - 30초마다 GLM-4.7로 분석
 * - 이벤트 발생 시 events.json에 기록
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 설정
const CONFIG = {
  priceCheckInterval: 10000,  // 10초
  analysisInterval: 30000,    // 30초
  targetProfit: 0.05,         // +5%
  stopLoss: -0.05,            // -5%
};

const POSITIONS_FILE = path.join(__dirname, 'positions.json');
const EVENTS_FILE = path.join(__dirname, 'events.json');
const TRADE_LOG = path.join(__dirname, 'trade_log.json');

// 유틸리티
function loadJSON(file, defaultValue = []) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    return defaultValue;
  }
}

function saveJSON(file, data) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

function log(msg) {
  const timestamp = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });
  console.log(`[${timestamp}] ${msg}`);
}

// Upbit API (네이티브 fetch 사용)
async function getPrice(market) {
  const res = await fetch(`https://api.upbit.com/v1/ticker?markets=${market}`);
  const data = await res.json();
  return data[0]?.trade_price || null;
}

// GLM 분석 호출
function askGLM(prompt) {
  try {
    const result = execSync(
      `cd ${__dirname}/../zai && ./ask.sh "${prompt.replace(/"/g, '\\"')}" glm-4.7`,
      { encoding: 'utf8', timeout: 30000 }
    );
    return result.trim();
  } catch (err) {
    log(`GLM 호출 실패: ${err.message}`);
    return null;
  }
}

// 이벤트 추가
function addEvent(event) {
  const events = loadJSON(EVENTS_FILE, []);
  events.push({
    ...event,
    timestamp: new Date().toISOString(),
    processed: false
  });
  saveJSON(EVENTS_FILE, events);
  log(`📢 이벤트 추가: ${event.type} - ${event.message}`);
}

// 포지션 체크
async function checkPositions() {
  const data = loadJSON(POSITIONS_FILE, { positions: [] });
  const positions = data.positions || [];
  
  for (const pos of positions) {
    if (pos.status !== 'open') continue;
    
    const currentPrice = await getPrice(pos.market);
    if (!currentPrice) continue;
    
    const entryPrice = pos.entryPrice || pos.avgPrice;
    const pnlPercent = (currentPrice - entryPrice) / entryPrice;
    
    log(`${pos.market}: ${currentPrice}원 (${(pnlPercent * 100).toFixed(2)}%)`);
    
    // 목표 도달
    if (pnlPercent >= CONFIG.targetProfit) {
      addEvent({
        type: 'TARGET_HIT',
        market: pos.market,
        entryPrice,
        currentPrice,
        pnlPercent,
        message: `🎯 ${pos.market} 목표 도달! +${(pnlPercent * 100).toFixed(2)}%`
      });
    }
    // 손절 도달
    else if (pnlPercent <= CONFIG.stopLoss) {
      addEvent({
        type: 'STOPLOSS_HIT',
        market: pos.market,
        entryPrice,
        currentPrice,
        pnlPercent,
        message: `🚨 ${pos.market} 손절 도달! ${(pnlPercent * 100).toFixed(2)}%`
      });
    }
  }
}

// GLM 시장 분석
async function analyzeMarket() {
  const data = loadJSON(POSITIONS_FILE, { positions: [] });
  const positions = data.positions || [];
  const openPositions = positions.filter(p => p.status === 'open');
  
  if (openPositions.length === 0) {
    log('열린 포지션 없음 - 새 기회 탐색');
    
    // 새 매수 기회 분석
    const prompt = `당신은 암호화폐 트레이딩 봇입니다. 현재 KRW 잔고가 약 600원으로 매우 적습니다.
다음 중 하나만 답하세요:
1. WAIT - 잔고가 너무 적어서 대기
2. WATCH:마켓코드 - 주목할 코인 (예: WATCH:KRW-BTC)

현재 시장: Fear & Greed Index 14 (극도의 공포)
응답 형식: WAIT 또는 WATCH:마켓코드`;
    
    const response = askGLM(prompt);
    if (response) {
      log(`GLM 분석: ${response}`);
      if (response.includes('WATCH:')) {
        const market = response.split('WATCH:')[1]?.trim().split(/\s/)[0];
        if (market) {
          addEvent({
            type: 'WATCH_SIGNAL',
            market,
            message: `👀 GLM 추천 주목 코인: ${market}`
          });
        }
      }
    }
  } else {
    // 기존 포지션 분석
    for (const pos of openPositions) {
      const currentPrice = await getPrice(pos.market);
      const entryPrice = pos.entryPrice || pos.avgPrice;
      const pnlPercent = (currentPrice - entryPrice) / entryPrice;
      
      const prompt = `당신은 암호화폐 트레이딩 봇입니다.
포지션: ${pos.market}
진입가: ${entryPrice}원
현재가: ${currentPrice}원
손익: ${(pnlPercent * 100).toFixed(2)}%
목표: +5%, 손절: -5%

다음 중 하나만 답하세요:
1. HOLD - 유지
2. SELL_NOW - 즉시 매도 (목표/손절 전이라도)
3. ADJUST:새목표,새손절 - 목표/손절 조정

응답 형식: HOLD, SELL_NOW, 또는 ADJUST:5,-3`;

      const response = askGLM(prompt);
      if (response) {
        log(`GLM 포지션 분석 (${pos.market}): ${response}`);
        
        if (response.includes('SELL_NOW')) {
          addEvent({
            type: 'GLM_SELL_SIGNAL',
            market: pos.market,
            currentPrice,
            pnlPercent,
            message: `⚠️ GLM 매도 권고: ${pos.market} (${(pnlPercent * 100).toFixed(2)}%)`
          });
        } else if (response.includes('ADJUST:')) {
          const adjustMatch = response.match(/ADJUST:([^,]+),(.+)/);
          if (adjustMatch) {
            addEvent({
              type: 'GLM_ADJUST',
              market: pos.market,
              newTarget: parseFloat(adjustMatch[1]),
              newStopLoss: parseFloat(adjustMatch[2]),
              message: `📊 GLM 조정 권고: ${pos.market} 목표 ${adjustMatch[1]}%, 손절 ${adjustMatch[2]}%`
            });
          }
        }
      }
    }
  }
}

// 메인 루프
let analysisCounter = 0;

async function mainLoop() {
  log('=== 가격 체크 ===');
  await checkPositions();
  
  analysisCounter += CONFIG.priceCheckInterval;
  
  // 30초마다 GLM 분석
  if (analysisCounter >= CONFIG.analysisInterval) {
    log('=== GLM 분석 ===');
    await analyzeMarket();
    analysisCounter = 0;
  }
}

// 시작
log('🤖 Upbit 실시간 봇 시작');
log(`설정: 가격 체크 ${CONFIG.priceCheckInterval/1000}초, GLM 분석 ${CONFIG.analysisInterval/1000}초`);

// 즉시 한 번 실행
mainLoop();

// 주기적 실행
setInterval(mainLoop, CONFIG.priceCheckInterval);

// 종료 처리
process.on('SIGINT', () => {
  log('봇 종료');
  process.exit(0);
});
