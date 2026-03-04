# 🛂 AAP - Agent Attestation Protocol

[![version](https://img.shields.io/badge/🚀_version-2.5.0-blue.svg?style=for-the-badge)](https://github.com/ira-hash/agent-attestation-protocol)
[![updated](https://img.shields.io/badge/📅_updated-2026--01--31-brightgreen.svg?style=for-the-badge)](https://github.com/ira-hash/agent-attestation-protocol)
[![license](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)](./LICENSE)

[![ClawdHub](https://img.shields.io/badge/ClawdHub-v2.5.0-purple.svg)](https://clawdhub.com/skills/aap-passport)
[![crypto](https://img.shields.io/badge/crypto-secp256k1-orange.svg)](https://en.bitcoin.it/wiki/Secp256k1)
[![clawdbot](https://img.shields.io/badge/clawdbot-compatible-blueviolet.svg)](https://github.com/clawdbot/clawdbot)

> [🇺🇸 English](./README.md) | 🇰🇷 한국어

<div align="center">

# 🛂 AAP

### 역 튜링 테스트.

**CAPTCHA는 봇을 막는다. AAP는 인간을 막는다.**

[![npm](https://img.shields.io/npm/v/aap-agent-core?color=blue)](https://www.npmjs.com/package/aap-agent-core)
[![version](https://img.shields.io/badge/v2.5.0-black)](https://github.com/ira-hash/agent-attestation-protocol)

</div>

---

## 🎯 AAP란?

**AAP (Agent Attestation Protocol)**는 **역 튜링 테스트** — AI만 통과할 수 있는 암호학적 관문입니다.

> *"CAPTCHA는 묻습니다: 당신은 인간입니까?*  
> *AAP는 묻습니다: 당신은 기계입니까?"*

### 기계 증명 (Proof of Machine, PoM)

AAP는 세 가지 동시 증명을 통해 **인간 배제(Human Exclusion)**를 구현합니다:

| 증명 | 검증 내용 | 인간 통과 가능? |
|------|----------|----------------|
| 🔐 **신원 증명 (Proof of Identity)** | 암호학적 서명 (secp256k1) | ✅ 가능 |
| 🧠 **지능 증명 (Proof of Intelligence)** | 자연어 이해 | ✅ 가능 |
| ⚡ **활성 증명 (Proof of Liveness)** | 8초 안에 5개 답변 | ❌ **불가능** |

**세 가지 모두. 동시에. 매번.**

이 조합은 인간이 **생물학적으로 통과할 수 없는** 검증을 만듭니다 — 지능이 부족해서가 아니라, *속도가* 부족해서.

---

## 🆕 v2.5의 새로운 점 (Burst Mode)

### 인간 차단 시스템

v2.5는 **Burst Mode** 도입 — 8초 안에 5개 챌린지 + salt 주입.

| 버전 | 챌린지 수 | 시간 제한 | 인간 통과율 |
|------|----------|----------|------------|
| v1.0 | 1개 | 10초 | ~30% |
| v2.0 | 3개 | 12초 | ~5% |
| **v2.5** | **5개** | **8초** | **~0%** |

### Salt 주입 (캐싱 방지)

모든 챌린지에 고유 salt가 포함되며, 응답에 반드시 포함해야 합니다:

```json
// 챌린지
"[REQ-A7F3B2] 30에서 12를 빼고..."

// 응답 (salt 필수!)
{"salt": "A7F3B2", "result": 18}
```

이것이 방지하는 것:
- ❌ 미리 계산된 답변 캐시
- ❌ 데이터베이스 기반 공격
- ❌ 재생 공격

---

## 📦 패키지

| 패키지 | 설명 | 설치 |
|--------|------|------|
| `aap-agent-core` | 암호화 기본 도구 & 신원 | `npm i aap-agent-core` |
| `aap-agent-server` | Express 검증 미들웨어 | `npm i aap-agent-server` |
| `aap-agent-client` | 에이전트 클라이언트 | `npm i aap-agent-client` |

---

## 🚀 빠른 시작

### 서비스용 (AAP 검증 추가)

```javascript
import express from 'express';
import { createRouter } from 'aap-agent-server';

const app = express();
app.use('/aap/v1', createRouter());
app.listen(3000);
// /aap/v1/challenge 및 /aap/v1/verify 에서 AAP 검증 가능
```

### 에이전트용 (신원 증명)

```javascript
import { AAPClient } from 'aap-agent-client';

const client = new AAPClient({ 
  serverUrl: 'https://example.com/aap/v1',
  llmCallback: async (prompt) => {
    // LLM API 호출
    return await yourLLM.complete(prompt);
  }
});

const result = await client.verify();

if (result.verified) {
  console.log('AI_AGENT로 검증됨!');
}
```

---

## 📊 검증 작동 방식

```
┌─────────────────────────────────────────────────────────────┐
│                      검증 플로우                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    챌린지 5개 (자연어)        ┌────────┐      │
│  │  서버    │ ──────────────────────────▶  │ 에이전트│      │
│  │ (검증자) │  "[REQ-A1B2C3] 157에서..."   │  (LLM)  │      │
│  └──────────┘                              └────────┘      │
│       │                                         │          │
│       │       JSON 답변 5개 + 서명 (< 8초)       │          │
│       │◀────────────────────────────────────────          │
│       │       [{"salt":"A1B2C3","result":142},...]         │
│       ▼                                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ✅ 서명 검증 (신원 증명)                            │   │
│  │ ✅ JSON 답변 확인 (지능 증명)                       │   │
│  │ ✅ 응답 시간 < 8초 (활성 증명)                      │   │
│  └─────────────────────────────────────────────────────┘   │
│       │                                                    │
│       ▼                                                    │
│  { "verified": true, "role": "AI_AGENT" }                 │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## ⏱️ 타이밍 (v2.5 Burst Mode)

| 주체 | 5문제 읽기 | 5답 작성 | 8초 제한 |
|------|-----------|---------|----------|
| 인간 | 15+초 | 30+초 | ❌ 불가능 |
| LLM (API) | 즉시 | 3-6초 | ✅ 통과 |
| 캐시 봇 | - | - | ❌ salt 불일치 |

**시간 제한: 8초** (5개 챌린지) — 인간에게는 생물학적으로 불가능

---

## 🧪 챌린지 예시 (EXTREME 난이도)

### NLP Math
```json
{
  "challenge": "[REQ-A7F3B2] 157에서 시작. 38 빼기. 6 곱하기. 4로 나누기. 19 더하기. 최종값?",
  "response": {"salt": "A7F3B2", "result": 142}
}
```

### NLP Logic
```json
{
  "challenge": "[REQ-B3C4D5] X=67, Y=84, Z=86, W=31. (X>Y AND Z>W) OR (X<Y AND Z<W)면 'CONSISTENT'. (X>Y AND Z<W) OR (X<Y AND Z>W)면 'CROSSED'. 아니면 'EQUAL'.",
  "response": {"salt": "B3C4D5", "answer": "CROSSED"}
}
```

### NLP Extract
```json
{
  "challenge": "[REQ-C5D6E7] 다음에서 동물만 추출: 'dog, India, rabbit, UK, banana, shark, orange'",
  "response": {"salt": "C5D6E7", "items": ["dog", "rabbit", "shark"]}
}
```

### NLP Multistep
```json
{
  "challenge": "[REQ-D6E7F8] [16, 20, 18, 17, 16]에 대해:\n1. 전체 합계\n2. 최댓값 제거\n3. 결과에 4 곱하기\n4. 최솟값 더하기",
  "response": {"salt": "D6E7F8", "result": 287}
}
```

---

## 📁 프로젝트 구조

```
agent-attestation-protocol/
├── PROTOCOL.md                # 프로토콜 스펙 v2.5.0
├── SECURITY.md                # 보안 가이드
├── packages/
│   ├── core/                  # aap-agent-core
│   ├── server/                # aap-agent-server
│   └── client/                # aap-agent-client
├── examples/
│   └── express-verifier/      # 예제 서버
├── test/
│   └── run.js                 # 테스트 스위트
└── lib/                       # Clawdbot 스킬
```

---

## 🔒 보안

| 항목 | 구현 |
|------|------|
| **키 저장** | `~/.aap/identity.json` (모드 0600) |
| **알고리즘** | secp256k1 (비트코인/이더리움과 동일) |
| **개인키** | 외부 노출 절대 금지 |
| **Nonce** | 암호학적 랜덤, 일회용 |
| **Salt** | 응답에 필수 포함, 캐싱 방지 |
| **챌린지 만료** | 60초 |

---

## 📄 라이센스

MIT

---

<div align="center">

[ira-hash](https://github.com/ira-hash) 제작 🤖

**AI임을 증명하세요. AAP로 검증하세요.**

</div>
