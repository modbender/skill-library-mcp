---
name: kr-document-reviewer
description: "한국 비즈니스 서류(세금계산서, 계약서, 통장사본, 견적서, 거래명세서, 사업자등록증, 사업비 요청 공문, 지원금 신청서, 검수조서, 이체확인증, 결과보고서) 검토 및 검증. Use when reviewing Korean business documents for format compliance, required fields, value accuracy, and cross-document consistency. Triggers on: 서류 검토, 문서 확인, 세금계산서 검증, 계약서 리뷰, 견적서 확인, 통장사본 검증, 거래명세서 확인, 사업자등록증 확인, 검수조서 검토, 이체확인증 검증, 결과보고서 검토, document review, invoice check."
---

# 한국 비즈니스 서류 검토 스킬

서류를 이미지 또는 PDF로 받아 검토한다. 각 서류 유형별 필수 항목과 검증 규칙을 따른다.

## 워크플로우 — 서브에이전트 분산 처리 (권장)

서류가 3종 이상이면 **Sonnet 서브에이전트 분산 처리** 방식을 사용한다.
비용이 약 1/30로 절감되며 병렬 처리로 속도도 빠르다.

### Phase 1: 전처리

1. PDF를 이미지로 변환 (`pdftoppm -png -r 200`)
2. **문서 유형 확인**: UUID 파일명인 경우 파일명만으로 문서 유형 판별 불가 → Phase 2에서 자동 판별하도록 지시
3. 서류를 2~3종씩 그룹으로 묶는다 (관련 서류끼리)
   - 파일-문서 매핑이 불확실하면, 그룹 구분 없이 전체를 2~3개씩 나눠서 "읽고 문서 유형부터 판별하라"고 지시

### Phase 2: Sonnet 서브에이전트 OCR + 개별 검토

각 그룹을 `sessions_spawn`으로 Sonnet 서브에이전트에 위임한다:

```
sessions_spawn(
  model: "anthropic/claude-sonnet-4-5",
  task: "이미지 파일을 read tool로 읽고, 체크리스트 기반 검토 후 JSON 반환"
)
```

**그룹 분배 예시 (11종 기준):**
- 그룹1: 세금계산서 + 이체확인증 (금액 대조 가능)
- 그룹2: 계약서 + 견적서 (금액/품목 대조 가능)
- 그룹3: 검수조서 + 거래명세서 (납품/검수 대조 가능)
- 그룹4: 통장사본×2 + 사업자등록증 (기관 정보 대조 가능)
- 그룹5: 지원금 신청서 (또는 사업비 요청 공문, 결과보고서)

**서브에이전트 태스크 작성 규칙:**
- 이미지 파일 경로를 명시하고 "Read tool로 읽어라"고 지시
- 서류 유형별 체크리스트를 태스크에 포함
- **반환 형식을 JSON으로 지정** (교차 검증에 필요한 핵심 값)
- 핵심 필드: 사업자등록번호, 상호, 대표자, 금액, 날짜, 계좌번호
- **문서 유형 자동 판별** 지시 포함 (UUID 파일명이면 유형 모를 수 있음)
- 문서 유형이 예상과 다르면 실제 유형으로 추출하라고 지시

### Phase 3: 교차 검증 (Sonnet 서브에이전트)

서브에이전트 결과가 도착하면:
1. JSON 결과를 수집하고 실제 문서 유형 기준으로 재정리
2. **교차검증 전용 Sonnet 서브에이전트를 추가 스폰** — 추출 데이터 전체 + 검증 항목을 텍스트로 전달
3. 교차검증 에이전트가 최종 리포트 생성

**교차검증 에이전트에 전달할 내용:**
- Phase 2의 추출 JSON 전체 (텍스트로)
- 검증 항목 목록 (사업자번호, 금액, 날짜, 당사자, 계좌, 누락서류)
- 리포트 출력 형식 지정

**주의:** 교차검증 에이전트에는 이미지를 보내지 않는다 (텍스트만 → 토큰 절약).
의심스러운 OCR 결과는 메인 세션에서 원본 이미지를 직접 확인한다.

### 비용 비교

| 방식 | 비용 | 비고 |
|------|------|------|
| Opus 메인에서 직접 처리 | ~$12 | 컨텍스트 누적으로 비용 급증 |
| Sonnet 서브에이전트 분산 | ~$0.7 | **약 94% 절감** (실측, 11종 14페이지 기준) |

---

## 워크플로우 — 단일 세션 (서류 1~2종)

서류가 1~2종이면 메인 세션에서 직접 처리해도 무방하다:

1. 서류 유형 판별
2. 해당 유형의 체크리스트 로드: `references/<type>.md`
3. OCR 또는 텍스트 추출 (이미지→vision, PDF→pdftoppm+read)
4. 체크리스트 항목별 검증
5. 검토 결과 리포트 출력

---

## 서류 유형별 레퍼런스

- **세금계산서**: [references/tax-invoice.md](references/tax-invoice.md)
- **계약서**: [references/contract.md](references/contract.md)
- **통장사본**: [references/bank-account.md](references/bank-account.md)
- **견적서**: [references/estimate.md](references/estimate.md)
- **거래명세서**: [references/transaction-statement.md](references/transaction-statement.md)
- **사업자등록증**: [references/business-registration.md](references/business-registration.md)
- **사업비 요청 공문**: [references/expense-request.md](references/expense-request.md)
- **지원금 신청서**: [references/subsidy-application.md](references/subsidy-application.md)
- **검수조서**: [references/inspection-report.md](references/inspection-report.md)
- **이체확인증**: [references/transfer-confirmation.md](references/transfer-confirmation.md)
- **결과보고서**: [references/result-report.md](references/result-report.md)

## 검토 결과 출력 형식

### JSON 정형 출력 (기본)

JSON 스키마: [`schema/review-result.schema.json`](schema/review-result.schema.json)
샘플 출력: [`schema/sample-output.json`](schema/sample-output.json)

**구조:**
```
{
  "meta": { reviewDate, reviewId, transaction: { summary, buyer, supplier, totalAmount } },
  "documents": [
    {
      docId, docType, party, status(pass|warning|fail),
      extractedData: { businessRegNo, companyName, representative, address,
                       supplyAmount, taxAmount, totalAmount, date,
                       bankName, accountNo, accountHolder, items },
      checklist: [ { item, status(pass|warning|fail|na), value?, note? } ]
    }
  ],
  "crossValidation": [
    {
      category(금액흐름|당사자정보|계좌정보|날짜정합성|누락서류),
      item, status, expected, actual, docs[], note?
    }
  ],
  "summary": { totalDocs, pass, warning, fail, criticalIssues[], actionRequired[], opinion }
}
```

**서브에이전트에 JSON 스키마를 포함하여 지시:**
- Phase 2 OCR 서브에이전트: `documents[]` 배열만 반환하도록 지시
- Phase 3 교차검증 서브에이전트: `crossValidation[]` + `summary` 반환하도록 지시
- 메인 세션에서 `meta` 추가 후 최종 JSON 조립

**출력 파일:**
- JSON 결과를 workspace에 저장: `reviews/REV-{YYYYMMDD}-{NNN}.json`
- 채팅에는 summary 기반 요약만 전달 (Discord 등 채널 특성에 맞게 포매팅)

### 채팅용 요약 출력 (보조)

JSON 결과의 summary를 기반으로 채팅 채널에 맞는 형태로 요약:

```
## 📋 서류 검토 결과 (N건)

**거래 개요**: (요약)

### ✅ 일치 확인 항목
- (항목): (설명)

### ⚠️ 주의 항목
- (항목): (설명)

### ❌ 누락/오류 항목
- (항목): (설명)

### 💡 조치 필요
1. 🔴 (high) ...
2. 🟡 (medium) ...
```

## 교차 검증 항목

여러 서류가 함께 제출된 경우 서류 간 교차 검증 수행:

### 금액 흐름
- 견적서 실행가 ↔ 계약서 계약금액
- 계약서 금액 ↔ 세금계산서 공급가액
- 세금계산서 합계(VAT포함) ↔ 이체확인증 금액
- 검수조서 금액 ↔ 세금계산서 공급가액
- 거래명세서 공급가액 ↔ 세금계산서 공급가액
- 신청서 집행내역 ↔ 세금계산서/계약서 금액
- 결과보고서 사업비 ↔ 계약서/세금계산서

### 당사자 정보
- 사업자등록번호 일치 (모든 서류 간)
- 업체명/대표자명 일치
- 사업자등록증 ↔ 세금계산서/계약서/견적서 정보
- 법인/개인 사업자 유형 일치 (사업자등록증 ↔ 계약서)

### 계좌 정보
- 이체확인증 출금계좌 ↔ 지원기업 통장사본
- 이체확인증 입금계좌 ↔ 공급기관 통장사본
- 신청서 입금계좌 ↔ 지원기업 통장사본
- 통장 예금주 ↔ 계약 당사자

### 날짜 정합성
- 견적일 → 계약일 → 세금계산서/이체일 → 검수일 → 신청일 (순서 확인)
- 선급 구조인 경우 세금계산서가 검수보다 선행 가능 (소명 필요 표시)

### Sonnet OCR 오류 보정 패턴 (실측 기반)
- 계좌번호 앞자리 누락 (601- → 01-)
- 한글 인명 오독 ("홍길동" → "홍길등", "김철수" → "김첼수", "박영희" → "박영의")
- 상호명 오독 ("대성테크" → "대상테크", "대성데코")
- 업태 오독 ("제조업" → "현대")
- 관리점명/전화번호 혼동
- 예금종류 오독
- 주소 세부 오독 ("외동읍" → "안동읍", "문산산단" → "문산2산1")
- **대조 원칙**: OCR 결과가 다른 문서와 불일치 시, 원본 이미지 직접 확인 후 판정
