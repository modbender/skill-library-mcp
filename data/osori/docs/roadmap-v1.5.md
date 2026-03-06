# Osori v1.5 로드맵 (고정안)

작성일: 2026-02-16
상태: **FROZEN (기획 고정)**
기준 브랜치: `main`

---

## 0) 목표

v1.5는 "기능 추가"보다 **안정성 + 실사용 UX + 운영 효율**에 초점을 둔다.

핵심 방향:

1. 레지스트리/루트 운영의 안전성 강화
2. 프로젝트 전환(`/switch`) 경험 개선
3. GitHub 조회 비용/지연 감소
4. 팀/개인 모두에서 재사용 가능한 관리 기능 제공

---

## 1) 범위 (Scope)

## P0 (필수)

### A. `/doctor` 레지스트리 건강검진
- 검출 항목
  - path 미존재
  - 중복 project name/path
  - root 참조 불일치
  - repo 포맷 이상
  - registry schema/version 이상
- 출력
  - 요약(심각도별 count)
  - 항목별 fix 제안
- 옵션
  - `--fix` (안전 자동 수정)
  - `--json` (기계 파싱)

### B. `/root-remove <key>` 안전 삭제
- 제약
  - `default` 삭제 금지
  - 프로젝트가 남아있는 root 삭제 차단(기본)
- 옵션
  - `--reassign <target-root>`
  - `--force` (강제 삭제, 명시적 경고)

### C. `/switch` 다중 매치 UX 개선
- 동일/유사 이름 다수일 때 후보 목록 표시
- 후보 정보에 포함
  - name, root, path, 최근 커밋 시각, dirty 여부
- 선택 방식
  - `--index <n>` 직접 선택
  - 미선택 시 점수 기반 자동 선택(정책 아래 참고)

## P1 (권장)

### D. GitHub 조회 캐시
- 대상: PR/Issue open count
- TTL 기본값: 600초
- 캐시 저장: `$HOME/.openclaw/osori-cache.json`
- 실패 시 fallback: 기존 실시간 조회 유지

### E. Alias / Favorite
- alias 맵 지원: `aliases` 필드
- 즐겨찾기: `favorite: true`
- 명령
  - `/alias-add <alias> <project>`
  - `/alias-remove <alias>`
  - `/favorites`

---

## 2) 비범위 (Out of Scope)

- 원격 DB 도입
- 멀티 사용자 동시 편집 락 서버
- GUI 앱 제공
- GitHub 외 forge(GitLab/Bitbucket) 완전 지원

---

## 3) 설계 결정 (고정)

1. 레지스트리 단일 파일 유지 (`osori.json`)
2. multi-root는 `projects[*].root` + `roots[]` 메타 구조 유지
3. 저장 방식은 기존 원자적 replace + backup/rollback 유지
4. 신규 기능은 Telegram command + shell script 동시 지원

---

## 4) `/switch` 자동 선택 정책 (고정)

후보 점수 계산(높을수록 우선):

- +50: root 정확히 일치
- +30: 이름 정확 일치
- +20: 이름 prefix 일치
- +10: 최근 commit이 더 최신
- -10: path 미존재
- -5: repo 미설정

동점 시:
1. 최근 commit 최신
2. name 사전순

---

## 5) DoD (Definition of Done)

각 기능 공통 DoD:

1. 스크립트 도움말/usage 반영
2. SKILL.md 명령 문서 업데이트
3. 테스트 추가 및 통과
4. 하위 호환성(기존 레지스트리) 보장
5. 실패/예외 시 사용자 메시지 명확

추가 DoD:

- `/doctor`: 최소 8개 이상 검사 케이스 테스트
- `/root-remove`: 보호 규칙 + reassign/force 테스트
- `/switch` 다중매치: 후보 3개 이상 시나리오 테스트
- GitHub 캐시: TTL hit/miss 테스트

---

## 6) 테스트 계획

테스트 파일: `tests/run_tests.sh` 확장

추가 예정 테스트 그룹:

- `test_doctor_report_and_fix`
- `test_root_remove_safety_rules`
- `test_switch_multi_match_selection`
- `test_github_cache_ttl`
- `test_alias_and_favorites`

성공 기준:
- 전체 테스트 0 fail
- 신규 테스트 커버: 정상/오류/엣지 케이스 포함

---

## 7) 마이그레이션/호환성

- 기존 `projects[]` 중심 사용 패턴 유지
- 새 필드는 optional 추가
- 문서/명령은 점진적 도입
- 기존 사용자 명령은 깨지지 않아야 함

---

## 8) 릴리즈 플랜

### Phase 1 (v1.5.0-rc1)
- `/doctor`
- `/root-remove`
- `/switch` 후보 선택 UX

### Phase 2 (v1.5.0)
- GitHub 캐시
- alias/favorite
- 문서/테스트 확정

---

## 9) 리스크 및 대응

1. **복잡도 증가**
   - 대응: 명령별 책임 분리(`scripts/*-manager.sh`)
2. **캐시 일관성 이슈**
   - 대응: TTL 짧게 시작 + 실패 시 실시간 fallback
3. **사용자 혼란(옵션 증가)**
   - 대응: `/help` 예시 강화 + 안전 기본값 유지

---

## 10) 변경 관리 규칙

- 이 문서는 v1.5 구현 기준선이다.
- 범위 변경은 아래 절차로만 허용:
  1. `docs/roadmap-v1.5.md`에 변경 이력 추가
  2. 영향 범위(P0/P1, 테스트, 일정) 명시
  3. 커밋 메시지에 `roadmap:` prefix 사용

---

## 11) 변경 이력

- 2026-02-16: 초안 작성 및 FROZEN 고정