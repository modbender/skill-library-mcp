---
name: pension-guide
description: '연금/노후설계 스킬. 9개 인텐트 라우팅(National Pension~Beginner Guide), 국민연금 예상 수령액 계산 + IRP/연금저축 절세 비교 + 노후 자금 역산 시뮬레이터. 트리거: "국민연금", "예상 수령액", "연금저축", "IRP", "퇴직금", "노후 준비", "은퇴 계획", "기초연금", "FIRE", "Pension Guide"'
version: 1.0.0
author: chumjibot
created: 2026-02-22
tags: [pension, 연금, 노후, IRP, 연금저축, 퇴직금, 기초연금, 은퇴]
connectors: [~~finance, ~~search, ~~notify, ~~docs, ~~law]
---

# 🏦 Pension Guide (연금/노후설계) 스킬

연금·노후 질문을 9개 인텐트로 분류하고, 국민연금 계산 + IRP/연금저축 비교 + 노후 시뮬레이션으로 리포트를 생성한다.

## 인텐트 라우터

| # | 인텐트 | 사용자 표현 예시 | 기본 산출물 |
|---|--------|-----------------|------------|
| 1 | Pension Estimate | "국민연금 얼마 받아?" | 예상 수령액 계산 Flash |
| 2 | Pension Guide | "국민연금 납부 방법" | 가입·납부·크레딧 안내 |
| 3 | IRP vs Savings | "IRP가 나아? 연금저축이 나아?" | 절세 효과 비교 Flash |
| 4 | Retirement Sim | "노후에 얼마 필요해?" | 필요 자금 역산 시뮬레이터 |
| 5 | Severance Pay | "퇴직금 얼마야?" | 퇴직금 계산 Flash |
| 6 | Basic Pension | "기초연금 얼마 받아?" | 수급 조건 + 금액 안내 |
| 7 | FIRE | "조기 은퇴 가능해?" | FIRE 전략 + 필요 자산 계산 |
| 8 | Retirement Portfolio | "은퇴 포트폴리오 짜줘" | finance-portfolio-counseling 연계 |
| 9 | Beginner Guide | "연금 처음인데" | 한국 연금 체계 입문 |

상세: [`references/intent_router.md`](references/intent_router.md)

## 연계 스킬

| 스킬 | 연계 인텐트 |
|------|-----------|
| `finance-portfolio-counseling` | Retirement Portfolio — 은퇴 포트폴리오 |
| `yahoo-finance-cli` | ETF/연금펀드 수익률 조회 |
| `welfare-guide` | Basic Pension — 기초연금 상세 |
| `tax-guide` | IRP/연금저축 세액공제 상세 |

## 출력 구조

- **Flash Layer**: 항상 출력
- **Deep-Dive Layer**: 명시 요청 시, 또는 Retirement Sim / IRP vs Savings / FIRE 인텐트

상세: [`references/output_templates.md`](references/output_templates.md)

## ⚠️ 면책

본 내용은 정보 제공 목적이며, 투자·재무 조언이 아닙니다.
국민연금 정확한 예상액은 국민연금공단(www.nps.or.kr) 또는 내연금(csa.nps.or.kr)에서 확인하세요.
