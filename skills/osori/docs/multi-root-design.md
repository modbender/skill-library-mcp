# Osori Multi-root 지원 설계안 (work/personal)

작성일: 2026-02-16

## 목표

- `work`, `personal` 같은 루트를 분리해서 프로젝트를 관리
- 기존 단일 레지스트리와의 호환 유지
- 검색/스캔/상태 조회 시 루트 기준 필터 가능

---

## 설계 옵션 비교

## 옵션 A) 단일 인덱스 + 프로젝트별 `root` 필드

레지스트리 하나(`osori.json`)에 모든 프로젝트를 저장하되, 각 프로젝트에 `root` 값을 둔다.

예시:

```json
{
  "schema": "osori.registry",
  "version": 2,
  "roots": [
    { "key": "work", "label": "Work", "paths": ["/Volumes/eyedisk/develop/kakao"] },
    { "key": "personal", "label": "Personal", "paths": ["/Volumes/eyedisk/develop/oozoofrog"] }
  ],
  "projects": [
    { "name": "TalkiOSDashboard", "root": "work", "path": "..." },
    { "name": "RunnersHeart", "root": "personal", "path": "..." }
  ]
}
```

장점:
- 검색/중복검사/마이그레이션 로직이 단순
- 기존 단일 파일 워크플로와 자연스럽게 연결
- cross-root 조회가 쉬움 (`status all`, 전역 검색)

단점:
- 파일이 커질수록 merge conflict 가능성 증가
- 루트별 권한/동기화 정책 분리 시 제약

---

## 옵션 B) 루트별 인덱스 분리 (`osori-work.json`, `osori-personal.json`)

루트별로 레지스트리를 분리 저장하고, 상위 인덱스(혹은 설정)로 묶는다.

장점:
- 루트별 백업/권한/동기화 분리가 쉬움
- 대규모 환경에서 파일 충돌 완화

단점:
- 전역 검색/중복검사 구현 복잡
- 명령마다 멀티 파일 aggregate 필요
- 기존 단일 파일 사용자에게 마이그레이션 비용 증가

---

## 추천안

**옵션 A(단일 인덱스 + `root` 필드)** 추천.

이유:
1. 기존 사용자 호환성이 가장 높음
2. 마이그레이션 리스크가 낮음
3. 현재 Osori 사용 패턴(빠른 검색/전환)에 적합

단, 장기적으로 팀 단위 대규모 사용이 늘면 옵션 B 또는 하이브리드(읽기 전용 aggregate) 검토 가능.

---

## 단계별 구현 제안

### 1단계 (이번 릴리스)
- 레지스트리 v2 도입
- `projects[*].root` 추가 (기본값: `default`)
- `roots` 메타 필드 추가
- `OSORI_ROOT_KEY`로 add/scan 시 루트 지정

### 2단계
- `/list --root work` 필터
- `/status --root personal` 필터
- `/scan --root work <path>` 형태 지원

### 3단계
- 루트별 기본 탐색 경로(`roots[].paths`) 자동 사용
- 루트별 우선순위 검색/추천 전환

---

## 오픈 이슈

- 동일 프로젝트명이 다른 루트에 존재할 때 name 충돌 처리 정책
- root 미지정 프로젝트를 자동 분류할지 여부
- 루트 이름 변경 시 프로젝트 일괄 업데이트 UX
