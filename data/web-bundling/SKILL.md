---
name: web-bundling
description: Bundle web applications into single HTML files for distribution. Use when creating self-contained HTML games, artifacts, or demos that need to be shared as a single file. Covers React+Vite+Parcel bundling pattern.
metadata:
  author: misskim
  version: "1.0"
  origin: Concept from Anthropic web-artifacts-builder, adapted for game distribution
---

# Web Bundling (Single HTML)

React/Vite 앱을 단일 HTML 파일로 번들링.

## 언제 사용

- 텔레그램 Mini App으로 배포할 게임
- itch.io에 올릴 HTML5 게임
- 단일 파일 데모/프로토타입
- 포트폴리오 아티팩트

## 번들링 패턴

### 간단한 게임 (프레임워크 없음)

이미 단일 HTML로 작성된 경우 번들링 불필요.
CSS/JS를 `<style>`/`<script>` 태그 안에 인라인.
이미지는 base64 data URI로 임베드.

### React 앱 → 단일 HTML

**스택:** React 18 + TypeScript + Vite + Parcel (번들링) + Tailwind CSS

```bash
# 1. Vite로 프로젝트 빌드
npm run build

# 2. Parcel로 단일 파일 번들
npx parcel build dist/index.html --no-source-maps

# 3. html-inline으로 에셋 인라인
npx html-inline dist/index.html -o bundle.html
```

### 에셋 인라인 팁

```html
<!-- 이미지 → base64 -->
<img src="data:image/png;base64,iVBOR..." />

<!-- 폰트 → base64 @font-face -->
<style>
@font-face {
  font-family: 'GameFont';
  src: url(data:font/woff2;base64,...) format('woff2');
}
</style>

<!-- 오디오 → base64 (작은 효과음만) -->
<audio src="data:audio/mp3;base64,..."></audio>
```

## 게임 배포 체크리스트

- [ ] 단일 HTML 파일로 번들됨
- [ ] 외부 CDN 의존성 없음 (오프라인 작동)
- [ ] 모바일 터치 지원 (텔레그램 Mini App)
- [ ] safe-area 고려 (WebView 환경)
- [ ] 파일 크기 최적화 (이미지 압축, 코드 minify)
- [ ] 콘솔 에러 없음

## 배포 경로

1. **텔레그램 Mini App** → eastsea.monster에 호스팅
2. **itch.io** → HTML 파일 직접 업로드
3. **GitHub Pages** → 레포에 push
4. **CrazyGames/Poki** → 플랫폼 요구사항 확인
