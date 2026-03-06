---
name: web-design-pro
description: Modern web design engineering skills including design tokens, advanced UI/UX methodologies, accessibility, and game-specific UI patterns. Use for building commercial-grade, performant, and accessible web interfaces.
metadata:
  author: misskim
  version: "1.0"
  origin: Synthesized from 2024-2026 web design standards research
---

# Web Design Pro (Modern Design Engineering)

웹 디자인의 심미성을 넘어, 시스템 설계, 성능 최적화, 접근성, 그리고 게임 특화 UX를 통합한 전문가 레벨의 기술셋.

## 1. Design Systems & Tokens (디자인 시스템 & 토큰)

디자인 결정을 데이터로 관리하여 디자인과 코드 간의 간극을 없앤다.

### 토큰 계층 구조
- **Primitive Tokens (Raw):** 기초적인 값 (예: `blue-500: #3B82F6`)
- **Semantic Tokens (Meaning):** 역할과 맥락 부여 (예: `action-primary: var(--blue-500)`)
- **Component Tokens (Specific):** 특정 컴포넌트 전용 (예: `btn-bg: var(--action-primary)`)

### 구현 가이드
- **CSS Custom Properties:** 브라우저 네이티브 토큰으로 실시간 테마 변경 가능.
- **Tokens Studio (Figma):** 디자인 소스에서 직접 JSON/CSS 추출.
- **자동화:** 토큰 변경 시 `Style Dictionary` 등을 통해 빌드 타임에 각 플랫폼에 배포.

---

## 2. UI/UX Methodologies (현대적 UX 방법론)

사용자의 "진짜" 문제를 해결하기 위한 프레임워크.

### 주요 방법론
- **Jobs to be Done (JTBD):** "플레이어는 게임 소개를 읽고 싶은 게 아니라, 이 게임이 재미있는지 3초 안에 확인하고 싶어한다." -> Hero 섹션에 텍스트 대신 gameplay 영상 배치.
- **Design Thinking:** 공감 - 정의 - 아이디어 - 프로토타입 - 테스트의 반복.
- **Design Sprints:** 2~5일 안에 핵심 가설을 검증하는 압축 프로세스.

---

## 3. Responsive Design Patterns (반응형 패턴)

모든 기기에서 완벽한 레이아웃을 제공하는 현대적 CSS 기법.

### Fluid Typography & Layout
- **`clamp()` 사용:** 미디어 쿼리 없이 화면 크기에 따라 폰트/간격을 유동적으로 조절.
  ```css
  h1 { font-size: clamp(2rem, 5vw + 1rem, 4rem); }
  ```
- **Container Queries:** 뷰포트가 아닌 부모 컨테이너 크기에 반응하는 컴포넌트 설계.
- **Mobile-First:** 320px 모바일 레이아웃을 기본으로 작성하고, `@media (min-width: ...)`로 점진적 확장.

---

## 4. Accessibility Standards (접근성 표준 - WCAG 2.1)

누락된 사용자가 없도록 하는 디자인의 기본.

### 핵심 체크포인트
- **Semantic HTML:** `<div>` 대신 `<nav>`, `<main>`, `<article>`, `<section>` 사용.
- **Color Contrast:** 텍스트 대비 4.5:1 이상 (AA 레벨 기준).
- **Keyboard Friendly:** 모든 상호작용이 Tab/Enter로 가능해야 함.
- **ARIA Labels:** 아이콘만 있는 버튼에 반드시 `aria-label` 부여.
- **Reduced Motion:** `prefers-reduced-motion`을 존중하여 과한 애니메이션 제어.

---

## 5. Performance & Web Vitals (성능 최적화)

속도가 곧 사용자 경험이다.

### Core Web Vitals (2024 기준)
- **LCP (Largest Contentful Paint):** 가장 큰 콘텐츠 로드 < 2.5s.
- **INP (Interaction to Next Paint):** 상호작용 응답 속도 < 200ms. (FID 대체)
- **CLS (Cumulative Layout Shift):** 레이아웃 흔들림 < 0.1.

### 최적화 기술
- **Image optimization:** WebP/AVIF 사용, `width`/`height` 명시로 CLS 방지.
- **Preload:** Critical 폰트 및 Hero 이미지를 우선 로드.
- **Defer JS:** 비필수 스크립트는 `defer`나 `async`로 처리.

---

## 6. Game UI/UX Specifics (게임 특화 UI)

플레이어의 몰입감을 극대화하는 UI 기법.

### 게임 UI 패턴
- **Immediate Feedback:** 모든 클릭/호버에 즉각적인 시각/청각 피드백 부여.
- **Visual Hierarchy:** 가장 중요한 Action(예: Play Now)을 F-Pattern 상단에 배치.
- **몰입형 레이아웃:** UI가 게임 세계관의 텍스처, 폰트, 톤과 일치해야 함.

---

## 7. Actionable Skills for eastsea.monster Redesign

즉시 적용 가능한 3가지 기술:
1. **Fluid Typography (clamp):** 모든 페이지 폰트 크기를 `clamp`로 변경하여 모바일-데스크톱 간 전환을 매끄럽게 함.
2. **WebP Batch Conversion:** 모든 게임 썸네일과 에셋을 WebP로 변환하여 LCP 개선.
3. **Hero Video Autoplay:** 정적 이미지 대신 음소거된 gameplay 영상을 Hero 섹션에 배치 (JTBD 적용).

---

## Best-Practice Checklist for Game Portfolio

- [ ] Hero 섹션에 gameplay 영상(muted)이 있는가?
- [ ] 메인 폰트가 `clamp()`를 통해 유동적으로 변하는가?
- [ ] 모든 이미지가 WebP 포맷이며 `width/height`가 지정되었는가?
- [ ] Tab 키만으로 모든 게임을 선택하고 플레이할 수 있는가?
- [ ] 호버 시 버튼이 반응(scale/glow)하는가?
- [ ] Lighthouse 접근성 점수가 90점 이상인가?
- [ ] `prefers-reduced-motion` 설정 시 번쩍이는 효과가 꺼지는가?
