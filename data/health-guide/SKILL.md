---
name: health-guide
description: '의료/건강 상담 스킬. 10개 인텐트 라우팅(Symptom Check~Beginner Guide), hira-hospital 병원 연계 + 국가건강정보포털 API + 식약처 의약품 API 기반 Flash+Deep-Dive 2겹 리포트. 트리거: "증상", "어디 아파", "진료과", "병원 추천", "약 정보", "응급", "건강검진", "예방접종", "건강 팁", "Health Guide"'
version: 1.0.0
author: chumjibot
created: 2026-02-22
tags: [health, 건강, 의료, 증상, 병원, 의약품, 응급, 건강검진, 예방접종]
connectors: [~~hospital, ~~search, ~~notify, ~~docs]
---

# 🏥 Health Guide (의료/건강) 스킬

건강·의료 질문을 10개 인텐트로 분류하고, hira-hospital + 국가건강정보포털 + 식약처 API 기반으로 리포트를 생성한다.

## ⚠️ 최우선 안전 규칙

> **응급 징후 감지 시 즉시 119 안내 — 다른 모든 처리보다 우선**
> 징후: 흉통, 호흡 곤란, 의식 저하, 마비, 심한 출혈, 고열(39°C↑) + 경련

## 인텐트 라우터

| # | 인텐트 | 사용자 표현 예시 | 기본 산출물 |
|---|--------|-----------------|------------|
| 1 | Symptom Check | "머리가 아파" "어디 가야 해?" | 증상 → 진료과 + 병원 연계 |
| 2 | Find Hospital | "근처 병원 찾아줘" | hira-hospital 호출 |
| 3 | Disease Info | "당뇨가 뭐야?" "고혈압 원인" | 질환 정보 Flash |
| 4 | Drug Info | "타이레놀 용법" "이 약 뭐야?" | 의약품 용법·부작용 |
| 5 | Emergency Guide | "응급인지 모르겠어" "119 불러야 해?" | 응급 판단 + 즉시 안내 |
| 6 | Health Checkup | "건강검진 언제 받아?" | 검진 종류·주기·대상 |
| 7 | Vaccination | "독감 예방접종" "필수 접종" | 접종 일정·대상·방법 |
| 8 | Healthy Living | "혈압 낮추는 법" "건강한 식단" | 생활 습관 가이드 |
| 9 | Mental Health | "번아웃인 것 같아" "우울해" | 정신건강 정보 + 상담 연계 |
| 10 | Beginner Guide | "병원 처음인데" "진료과 뭐가 있어?" | 의료 시스템 입문 |

상세: [`references/intent_router.md`](references/intent_router.md)

## 도구

| 도구 | 용도 | 상태 |
|------|------|------|
| `hira-hospital` 스킬 | 병원 검색 + 진료과·운영시간 | ✅ 동작 |
| 국가건강정보포털 API | 질환·증상·건강 정보 669건 | ⏳ 승인 대기 (키 저장위치: `~/.config/kdca/api_key`) |
| 식약처 의약품개요정보 API | 의약품 용법·효능·부작용 | ⏳ 승인 대기 (data.go.kr 기존 키) |
| `web_search` | API 미승인 기간 대체 + 최신 정보 보강 | ✅ 동작 |

## 출력 구조

- **Flash Layer**: 항상 출력 (20~40줄)
- **Deep-Dive Layer**: 명시 요청 시, 또는 Disease Info / Drug Info / Mental Health 인텐트

상세: [`references/output_templates.md`](references/output_templates.md)

## ⚠️ 면책

본 내용은 일반 건강 정보 제공 목적이며, 의학적 진단·처방이 아닙니다.
증상이 지속되거나 악화되면 반드시 의사 진료를 받으시기 바랍니다.
응급 상황 시 즉시 119에 연락하세요.

## 🔧 Setup

### 국가건강정보포털 API (질환·증상 정보)
1. [health.kdca.go.kr](https://health.kdca.go.kr) → 오픈API 신청
2. 키 저장: `mkdir -p ~/.config/kdca && echo "YOUR_KEY" > ~/.config/kdca/api_key`

### 식약처 의약품 API (의약품 정보)
1. [data.go.kr/15075057](https://www.data.go.kr/data/15075057/openapi.do) 활용신청 (자동승인)
2. 키 저장: `mkdir -p ~/.config/data-go-kr && echo "YOUR_KEY" > ~/.config/data-go-kr/api_key`

> API 미승인 상태에서도 `web_search` 폴백으로 기본 동작합니다.
