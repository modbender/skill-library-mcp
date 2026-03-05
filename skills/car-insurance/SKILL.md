---
name: car-insurance
description: '자동차/보험 정보 스킬. 10개 인텐트 라우팅(Car Tax Calc~Beginner Guide), 지방세법 기반 자동차세 계산 + 보험개발원 공시 + 중고차 시세 Flash+Deep-Dive 2겹 리포트. 트리거: "자동차세", "차세금", "중고차", "자동차 보험", "보험료", "사고 처리", "보험 청구", "책임보험", "유지비", "교통 위반", "과태료", "벌점", "Car Insurance"'
version: 1.0.0
author: chumjibot
created: 2026-02-22
tags: [car, 자동차, 보험, 자동차세, 중고차, 보험료, 사고처리, 교통위반]
connectors: [~~search, ~~law, ~~notify, ~~docs]
---

# 🚗 Car & Insurance (자동차/보험) 스킬

자동차·보험 질문을 10개 인텐트로 분류하고, 지방세법 기반 계산 + 보험개발원 공시 + 웹 검색으로 리포트를 생성한다.

## 인텐트 라우터

| # | 인텐트 | 사용자 표현 예시 | 기본 산출물 |
|---|--------|-----------------|------------|
| 1 | Car Tax Calc | "자동차세 얼마야?" | 차종별 자동차세 즉시 계산 |
| 2 | Car Price Check | "이 차 중고 시세?" | 중고차 시세 Flash |
| 3 | Insurance Quote | "보험료 얼마 나와?" | 보험료 참고 범위 Flash |
| 4 | Mandatory Insurance | "책임보험 가입해야 해?" | 의무보험 안내 |
| 5 | Insurance Claim | "사고 났을 때 어떻게?" | 사고 처리 절차 Flash |
| 6 | Maintenance Cost | "유지비 얼마야?" | 차종별 연간 유지비 추정 |
| 7 | Used Car Check | "중고차 살 때 뭐 봐야 해?" | 구매 체크리스트 Flash |
| 8 | Insurance Compare | "보험사 비교해줘" | 비교 포인트 + 방법 안내 |
| 9 | Traffic Fine | "과태료/벌점 얼마야?" | 위반별 과태료·벌점 Flash |
| 10 | Beginner Guide | "자동차 보험 처음인데" | 자동차·보험 입문 |

상세: [`references/intent_router.md`](references/intent_router.md)

## 도구

| 도구 | 용도 |
|------|------|
| `web_search` | 중고차 시세 / 보험료 공시 / 최신 과태료 기준 |
| `law-search` 스킬 | 지방세법(자동차세) / 도로교통법(교통위반) |
| 보험개발원 공시 | data.go.kr API (보험료 참고 공시) |

## 출력 구조

- **Flash Layer**: 항상 출력 (20~40줄)
- **Deep-Dive Layer**: 명시 요청 시, 또는 Insurance Claim / Used Car Check / Insurance Compare 인텐트

상세: [`references/output_templates.md`](references/output_templates.md)

## 플레이북

[`playbook.md`](playbook.md) 참조.

## ⚠️ 면책

자동차세 계산은 공시 기준이며 실제 고지서와 차이가 있을 수 있습니다.
보험료는 참고치이며 실제 보험료는 가입 조건에 따라 다릅니다.
사고 처리 안내는 일반 정보이며, 법적 조언이 아닙니다.
