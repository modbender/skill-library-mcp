---
name: welfare-guide
description: '육아/복지/정부지원금 스킬. 9개 인텐트 라우팅(Benefit Search~Beginner Guide), 보조금24+복지로 중앙/지자체 API 3-Layer 기반 맞춤형 혜택 조회. 트리거: "지원금", "복지", "혜택", "보조금", "육아", "출산", "보육료", "아동수당", "기초생활", "장애인 지원", "노인 복지", "청년 지원", "Welfare Guide"'
version: 1.0.0
author: chumjibot
created: 2026-02-22
tags: [welfare, 복지, 지원금, 보조금, 육아, 출산, 보육, 아동수당, 기초생활]
connectors: [~~search, ~~notify, ~~docs]
---

# 🍀 Welfare Guide (육아/복지/정부지원금) 스킬

복지·지원금 질문을 9개 인텐트로 분류하고, 보조금24 + 복지로 중앙부처/지자체 API 3-Layer로 맞춤형 혜택을 조회한다.

## 인텐트 라우터

| # | 인텐트 | 사용자 표현 예시 | 기본 산출물 |
|---|--------|-----------------|------------|
| 1 | Benefit Search | "받을 수 있는 혜택 뭐야?" | 조건 기반 맞춤 혜택 목록 |
| 2 | Childcare | "아이 키우면 지원금 뭐 있어?" | 육아·보육 지원 패키지 |
| 3 | Birth Support | "출산하면 뭐 받아?" | 출산 지원 총정리 Flash |
| 4 | Basic Living | "기초생활수급자 되려면?" | 수급 조건 + 신청 방법 |
| 5 | Youth Support | "청년 혜택 뭐 있어?" | 청년 전용 지원 목록 |
| 6 | Senior Support | "부모님 노인 혜택 뭐 있어?" | 노인 복지 서비스 목록 |
| 7 | Disability Support | "장애인 지원금 뭐 있어?" | 장애인 복지 서비스 목록 |
| 8 | How to Apply | "어떻게 신청해?" | 신청 절차 + 서류 안내 |
| 9 | Beginner Guide | "복지 처음인데" | 복지 시스템 입문 Flash |

상세: [`references/intent_router.md`](references/intent_router.md)

## API 3-Layer 구조

| API | 제공기관 | 내용 | 상태 |
|-----|---------|------|------|
| 보조금24 (`15113968`) | 행정안전부 | 정부부처+지자체+공공기관 수혜서비스 전체 | ⏳ 활용신청 필요 |
| 복지로 중앙부처 (`15090532`) | 한국사보원 | 중앙부처 복지사업 + 수급 조건 상세 | ⏳ 활용신청 필요 |
| 복지로 지자체 (`15108347`) | 한국사보원 | 지역별 지자체 복지서비스 | ⏳ 활용신청 필요 |

→ 3개 조합 시 중앙 + 지역 완전 커버. 조건(나이/지역/가구/소득) 기반 필터링 가능

## 출력 구조

- **Flash Layer**: 항상 출력
- **Deep-Dive Layer**: 명시 요청 시, 또는 Basic Living / Benefit Search 인텐트

상세: [`references/output_templates.md`](references/output_templates.md)

## ⚠️ 면책

본 내용은 정보 제공 목적이며, 실제 수급 여부는 해당 기관에서 결정합니다.
최신 정책은 복지로(www.bokjiro.go.kr) 또는 주민센터에서 확인하세요.

## 🔧 Setup (공공데이터 포털 API)

1. [data.go.kr](https://www.data.go.kr) 회원가입 → 일반 인증키(Decoding) 복사
2. 아래 3개 서비스 **활용신청** (모두 자동승인):
   - [복지로 중앙부처](https://www.data.go.kr/data/15090532/openapi.do) (15090532)
   - [복지로 지자체](https://www.data.go.kr/data/15108347/openapi.do) (15108347)
   - [보조금24](https://www.data.go.kr/data/15113968/openapi.do) (15113968)
3. 키 저장:
   ```bash
   mkdir -p ~/.config/data-go-kr
   echo "YOUR_API_KEY" > ~/.config/data-go-kr/api_key
   ```
> API 미등록 시에도 `web_search` 폴백으로 주요 복지 정보 조회 가능합니다.
