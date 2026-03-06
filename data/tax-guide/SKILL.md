---
name: tax-guide
description: '세금/절세 가이드 스킬. 10개 인텐트 라우팅(Quick Tax Check~Beginner Guide), 법제처 API+국세청 지식베이스 기반 Flash+Deep-Dive 2겹 리포트. 트리거: "세금", "절세", "연말정산", "종합소득세", "부가세", "재산세", "종부세", "상속세", "증여세", "원천징수", "세액공제", "소득공제", "Tax Guide"'
version: 1.0.0
author: chumjibot
created: 2026-02-22
tags: [tax, 세금, 절세, 연말정산, 종합소득세, 부가세, 재산세, 종부세, 상속세, 증여세]
connectors: [~~law, ~~search, ~~notify, ~~docs]
---

# 💰 Tax Guide (세금/절세 가이드) 스킬

세금 질문을 10개 인텐트로 분류하고, 법제처 API + 국세청 지식베이스 기반으로 리포트를 생성한다.

## 인텐트 라우터

| # | 인텐트 | 사용자 표현 예시 | 기본 산출물 |
|---|--------|-----------------|------------|
| 1 | Quick Tax Check | "이거 세금 내야 해?" | 과세 여부 + 세율 Flash |
| 2 | Year-end Settlement | "연말정산 어떻게 해?" | 절차 + 공제 항목 가이드 |
| 3 | Income Tax Filing | "종합소득세 신고" | 신고 절차 + 세액 계산 |
| 4 | Tax Deduction | "절세 방법 알려줘" | 절세 수단 목록 + 효과 비교 |
| 5 | VAT Guide | "부가세 신고 방법" | 계산 + 신고 절차 |
| 6 | Property Tax | "재산세 얼마야?" | 보유세 계산 + 납부 일정 |
| 7 | Inheritance/Gift Tax | "증여세 얼마야?" | 세액 계산 + 절세 전략 |
| 8 | Withholding Tax | "3.3% 원천징수" | 세율 + 납부 절차 |
| 9 | Tax Dispute | "세금 이의신청" | 불복 절차 + 기한 안내 |
| 10 | Beginner Guide | "세금 처음인데" | 세금 구조 입문 |

상세: [`references/intent_router.md`](references/intent_router.md)

## 도구

| 도구 | 용도 |
|------|------|
| `law-search` 스킬 | 소득세법·부가세법·상속세법 조문 조회 |
| `web_search` | 국세청 최신 가이드·납부 일정 보강 |

## 시즌 트리거

| 시기 | 이벤트 | 관련 인텐트 |
|------|--------|------------|
| 1~2월 | 연말정산 간소화 서비스 오픈 | Year-end Settlement |
| 5월 | 종합소득세 신고 기간 | Income Tax Filing |
| 7월 / 9월 | 재산세 납부 | Property Tax |
| 1월 / 7월 | 부가세 신고 | VAT Guide |

## 출력 구조

- **Flash Layer**: 항상 출력 (20~40줄)
- **Deep-Dive Layer**: 명시 요청 시, 또는 Year-end/Income Tax/Tax Dispute 인텐트

상세: [`references/output_templates.md`](references/output_templates.md)

## 플레이북

[`playbook.md`](playbook.md) 참조.

## ⚠️ 면책

본 내용은 일반 세금 정보 제공 목적이며, 세무 자문이 아닙니다.
구체적인 사안은 세무사 또는 국세청 상담(☎126)을 받으시기 바랍니다.
