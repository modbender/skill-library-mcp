---
name: react-perf
description: React and Next.js performance optimization patterns. Use when writing, reviewing, or optimizing React code for web apps, Remotion videos, or any React-based UI. Covers waterfall elimination, bundle optimization, re-render prevention, and server-side patterns.
metadata:
  author: misskim
  version: "1.0"
  origin: Concept from Vercel react-best-practices (57 rules), distilled to essentials
---

# React Performance Patterns

React 코드 작성 시 성능 최적화 핵심 패턴.

## 우선순위별 핵심 규칙

### 🔴 CRITICAL: 워터폴 제거

```javascript
// ❌ 순차 await — 각 요청이 이전을 기다림
const user = await getUser();
const posts = await getPosts();

// ✅ 병렬 — 독립 요청은 Promise.all
const [user, posts] = await Promise.all([getUser(), getPosts()]);
```

- `await`를 실제 사용 브랜치로 이동 (불필요한 대기 제거)
- Suspense 경계로 콘텐츠 스트리밍

### 🔴 CRITICAL: 번들 크기

```javascript
// ❌ barrel import — 전체 모듈 로드
import { Button } from '@/components';

// ✅ 직접 import
import { Button } from '@/components/ui/Button';
```

- `next/dynamic`으로 무거운 컴포넌트 지연 로드
- 분석/로깅은 hydration 후 로드
- hover/focus 시 preload로 체감 속도 향상

### 🟡 HIGH: 서버사이드

- `React.cache()`로 요청 내 중복 제거
- 클라이언트로 전달하는 데이터 최소화
- 컴포넌트 구조 변경으로 fetch 병렬화

### 🟢 MEDIUM: 리렌더 방지

```javascript
// ❌ 콜백에서만 쓰는 state를 구독
const [items, setItems] = useState([]);
const handleClick = () => process(items);

// ✅ ref로 전환 (리렌더 방지)
const itemsRef = useRef([]);
const handleClick = () => process(itemsRef.current);
```

- 비용 높은 작업은 memo 컴포넌트로 분리
- `useState` 초기값에 함수 전달 (lazy init)
- `startTransition`으로 긴급하지 않은 업데이트 분리
- 파생 state는 effect 대신 렌더 중 계산

### 🔵 LOW: JS 성능

- 반복 조회 → `Map`/`Set` 사용 (O(1))
- `filter().map()` → 하나의 루프로 결합
- RegExp는 루프 밖에서 생성
- `array.length` 먼저 체크 후 비싼 비교

## Remotion에서의 React

Remotion 비디오 컴포넌트도 React이므로 동일 원칙 적용:
- `interpolate()`는 매 프레임 호출 → 비싸면 캐싱
- 무거운 계산은 `useMemo` / `useCallback`
- 오프스크린 요소 렌더링 최소화
