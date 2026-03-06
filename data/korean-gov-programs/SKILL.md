---
name: Korean Gov Programs
description: Collect Korean government support programs (TIPS, Small Business, R&D grants) into structured JSONL files. Supports incremental collection with checkpoints.
version: 1.0.8
author: raon
---

# korean-gov-programs

한국 정부지원사업(TIPS, 소상공인, R&D)을 구조화된 JSONL 파일로 수집하는 스킬.
체크포인트 기반 증분 수집으로 중복 없이 안전하게 운영.

---

## 수집 소스

| 소스 | 카테고리 | 방식 | 상태 |
|------|----------|------|------|
| 기업마당(BizInfo) | 소상공인 | 정적 HTML | ✅ 동작 |
| NIA 한국지능정보사회진흥원 | 정보화사업 | onclick 패턴 | ✅ 동작 |
| 기업마당 기술창업 필터 | 기술창업/R&D | 정적 HTML | ✅ 동작 |
| 소상공인시장진흥공단(SEMAS) | 소상공인 | JS 렌더링 필요 | ⚠️ 스킵 |
| 중소벤처기업부(MSS) | 정부지원 | JS 렌더링 필요 | ⚠️ 스킵 |
| K-Startup | 창업지원 | JS 렌더링 필요 | ⚠️ 스킵 |
| 연구개발특구진흥재단(Innopolis) | R&D | JS 렌더링 필요 | ⚠️ 스킵 |
| 창업진흥원(KISED) | 창업 | eGovFrame 오류 | ⚠️ 스킵 |

> JS 렌더링 필요 사이트는 Selenium/Playwright 환경에서 별도 수집 필요.

---

## 사용법

```bash
# 기본 수집 (./data 디렉토리에 저장)
python3 scripts/collect.py --output ./data

# 커스텀 출력 디렉토리
python3 scripts/collect.py --output /path/to/output

# 수집 현황 확인
bash scripts/stats.sh ./data
```

---

## JSONL 스키마

```json
{
  "title": "사업명",
  "category": "소상공인 | 기술창업 | 정보화사업 | R&D",
  "source": "수집 출처 기관명",
  "url": "상세 페이지 URL",
  "amount": "지원 금액 (있는 경우)",
  "deadline": "마감일 (예: ~2026-03-31)",
  "description": "부가 설명",
  "collected_at": "2026-02-19T08:53:00.000000"
}
```

---

## 체크포인트 & 안전 수집

- **APPEND 전용**: 기존 파일 덮어쓰기 절대 없음
- **중복 방지**: title 기준 중복 자동 스킵
- **체크포인트**: `.checkpoint.json`에 진행 상태 저장 → 재실행 시 이어서 수집
- **딜레이**: 요청 간 0.8초 대기 (서버 부하 방지)

---

## 출력 파일

```
data/
├── soho_programs.jsonl         # 소상공인 지원사업
├── gov_programs.jsonl          # 정부 R&D / 기술창업 지원사업
└── .checkpoint.json            # 체크포인트 (자동 생성)
```

---

## 파일 구조

```
korean-gov-programs/
├── SKILL.md                    # 이 파일
└── scripts/
    ├── collect.py              # 통합 수집 스크립트
    └── stats.sh                # 수집 현황 출력
```
