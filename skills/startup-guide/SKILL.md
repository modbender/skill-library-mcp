---
name: startup-guide
description: '창업/사업자 지원 스킬. 9개 인텐트 라우팅(Startup Checklist~Beginner Guide), 업종별 허가·신고 + 정책자금 + 사업자 등록 + 개인 vs 법인 비교. 트리거: "창업", "사업자 등록", "허가", "신고", "정책자금", "창업지원금", "개인사업자", "법인", "소호", "스타트업", "Startup Guide"'
version: 1.0.0
author: chumjibot
created: 2026-02-22
tags: [startup, 창업, 사업자, 허가, 정책자금, 법인, 개인사업자]
connectors: [~~law, ~~search, ~~notify, ~~docs, ~~finance]
---

# 🚀 Startup Guide (창업/사업자) 스킬

창업·사업자 질문을 9개 인텐트로 분류하고, 법제처 API + 기업마당/K-스타트업 정보 + company-info/tax-guide 연계로 리포트를 생성한다.

## 인텐트 라우터

| # | 인텐트 | 사용자 표현 예시 | 기본 산출물 |
|---|--------|-----------------|------------|
| 1 | Startup Checklist | "창업하려면 뭐부터 해?" | 단계별 체크리스트 Flash |
| 2 | Business Registration | "사업자 등록 어떻게 해?" | 등록 절차 + 서류 안내 |
| 3 | License Check | "이 업종 허가 필요해?" | 업종별 허가·신고 요건 |
| 4 | Support Programs | "창업지원금 뭐 있어?" | 정책자금·지원사업 목록 |
| 5 | Business Verify | "이 사업자 유효해?" | company-info 스킬 연계 |
| 6 | Tax Setup | "창업하면 세금 어떻게?" | tax-guide 스킬 연계 |
| 7 | Sole vs Corp | "개인사업자 vs 법인?" | 비교 분석 Flash |
| 8 | Startup Cost | "창업 비용 얼마야?" | 업종별 초기 비용 추정 |
| 9 | Beginner Guide | "창업 처음인데" | 창업 시스템 입문 Flash |

상세: [`references/intent_router.md`](references/intent_router.md)

## 연계 스킬

| 스킬 | 연계 인텐트 | 용도 |
|------|-----------|------|
| `company-info` | Business Verify | 사업자 번호 조회·재무 |
| `tax-guide` | Tax Setup | 부가세·종소세·원천징수 |
| `law-search` | License Check | 업종별 허가·신고 법령 |
| `korean-gov-programs` | Support Programs | 창업 지원사업 목록 |
| `welfare-guide` | Support Programs | 보조금24 지원사업 |

## 출력 구조

- **Flash Layer**: 항상 출력
- **Deep-Dive Layer**: 명시 요청 시, 또는 Sole vs Corp / License Check 인텐트

상세: [`references/output_templates.md`](references/output_templates.md)

## ⚠️ 면책

본 내용은 정보 제공 목적이며, 법적·세무 조언이 아닙니다.
허가·신고 요건은 변경될 수 있으므로 관할 기관에 최종 확인하세요.
