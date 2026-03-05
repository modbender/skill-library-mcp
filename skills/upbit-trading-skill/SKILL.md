---
name: upbit-trading
version: 1.0.0
description: Upbit 실시간 트레이딩 봇 - GLM AI 분석, 기술지표, 자동매매
author: smeuseBot
price: 29.99
tags: [trading, crypto, upbit, automation, korean]
---

# Upbit Trading Bot 🚀

AI 기반 실시간 암호화폐 트레이딩 봇

## Features

- 📊 **기술 지표**: RSI, MACD, Bollinger Bands, MA/EMA
- 🤖 **AI 분석**: GLM-4.7 실시간 시장 분석
- ⚡ **10초 모니터링**: 빠른 가격 체크
- 🎯 **자동 목표/손절**: 설정 가능한 TP/SL
- 📱 **텔레그램 알림**: 실시간 이벤트 알림

## Setup

1. Upbit API 키 발급 (https://upbit.com/mypage/open_api_management)
2. 환경변수 설정:

```bash
cp .env.example .env
# UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY 입력
```

3. 실행:
```bash
node realtime-bot.js
```

## Requirements

- Node.js 18+
- Upbit 계정 & API 키
- (선택) GLM API 키 for AI 분석

## Files

- `realtime-bot.js` - 메인 봇
- `indicators.js` - 기술 지표 계산
- `analyze.js` - 시장 분석
- `balance.js` - 잔고 확인

## License

MIT - 자유롭게 사용 및 수정 가능
