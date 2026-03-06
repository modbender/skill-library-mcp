---
name: postgres-perf
description: PostgreSQL performance optimization and best practices. Use when writing SQL queries, designing schemas, implementing indexes, or debugging database performance. Covers query optimization, connection management, schema design, and RLS.
metadata:
  author: misskim
  version: "1.0"
  origin: Concept from Supabase postgres-best-practices, distilled for our use
---

# PostgreSQL Performance

DB 쿼리/스키마 작성 시 성능 최적화 가이드.

## 우선순위별 핵심 규칙

### 🔴 CRITICAL: 쿼리 성능

```sql
-- ❌ 인덱스 없는 WHERE
SELECT * FROM orders WHERE customer_email = 'user@example.com';

-- ✅ 인덱스 생성
CREATE INDEX idx_orders_email ON orders(customer_email);
```

- **EXPLAIN ANALYZE** 습관화 — 실행 계획 항상 확인
- Seq Scan이 큰 테이블에 나타나면 인덱스 필요
- `SELECT *` 금지 → 필요한 컬럼만 선택
- N+1 쿼리 → JOIN 또는 배치 조회로 교체

### 🔴 CRITICAL: 커넥션 관리

- 커넥션 풀 사용 (직접 연결 금지)
- Supabase → pgBouncer (transaction mode)
- 서버리스 환경 → 커넥션 풀 필수
- 유휴 커넥션 정리

### 🟡 HIGH: 스키마 설계

```sql
-- ❌ 무분별한 인덱스
CREATE INDEX idx_everything ON orders(a, b, c, d, e);

-- ✅ 부분 인덱스 (자주 쓰는 조건)
CREATE INDEX idx_active_orders ON orders(created_at)
WHERE status = 'active';
```

- 정규화 vs 비정규화 — 읽기 패턴에 맞게 결정
- UUID vs serial → UUID가 분산 환경에 유리하나 인덱스 크기 큼
- JSONB → 구조화 불가능한 데이터만, 쿼리 대상이면 컬럼으로

### 🟢 MEDIUM: 동시성/잠금

- 대량 UPDATE/DELETE → 배치 처리
- `SELECT ... FOR UPDATE` → 필요한 행만 잠금
- 트랜잭션 최소화 (짧게 유지)
- 데드락 방지 — 일관된 잠금 순서

### 🔵 LOW: RLS (Row Level Security)

```sql
-- 보안 정책 예시
CREATE POLICY user_data ON user_profiles
  FOR SELECT USING (auth.uid() = user_id);
```

- RLS 정책은 인덱스와 함께 설계 (성능 임팩트!)
- `auth.uid()` 호출 최소화
- 복잡한 정책 → EXPLAIN으로 성능 확인

## 실무 팁

- **개발 중:** `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)`
- **프로덕션:** 슬로우 쿼리 로그 활성화
- **마이그레이션:** 대용량 테이블 ALTER는 비동기로
- **백업:** NAS에 pg_dump 자동화 가능
