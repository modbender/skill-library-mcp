---
name: remotion-video
description: Create programmatic videos using Remotion on MiniPC. Use when making video content, animations, motion graphics, social media clips, or any React-based video production. Covers animations, assets, audio, captions, transitions, and rendering.
metadata:
  author: misskim
  version: "1.0"
  origin: Concept from remotion-dev/skills, adapted for our MiniPC Remotion setup
---

# Remotion Video Production (MiniPC)

MiniPC의 Remotion으로 프로그래밍 방식의 영상 제작.

## 환경

- **프로젝트:** `$HOME/remotion-videos` (MiniPC)
- **실행:** `npx remotion render <CompositionId> out/video.mp4`
- **ffmpeg:** 설치됨
- **전송:** MiniPC HTTP 서버(9877) + curl로 맥 스튜디오 전송

## 핵심 개념

### Composition = 영상의 단위
```tsx
<Composition
  id="MyVideo"
  component={MyComponent}
  durationInFrames={150}  // 30fps × 5초 = 150프레임
  fps={30}
  width={1920}
  height={1080}
/>
```

### 시간 제어
```tsx
const frame = useCurrentFrame();         // 현재 프레임
const { fps, durationInFrames } = useVideoConfig();

// 보간 (interpolate)
const opacity = interpolate(frame, [0, 30], [0, 1], {
  extrapolateRight: 'clamp'
});

// 스프링 애니메이션
const scale = spring({ frame, fps, config: { damping: 200 } });
```

### 시퀀싱
```tsx
<Sequence from={0} durationInFrames={60}>
  <IntroScene />
</Sequence>
<Sequence from={60} durationInFrames={90}>
  <MainContent />
</Sequence>
```

## 주요 패턴

### 에셋 사용
- **이미지:** `<Img src={staticFile('logo.png')} />`
- **비디오:** `<OffthreadVideo src={staticFile('clip.mp4')} />`
- **오디오:** `<Audio src={staticFile('bgm.mp3')} volume={0.5} />`
- **폰트:** Google Fonts — `loadFont("Noto Sans KR")`
- **로컬 폰트:** public/ 폴더에 배치

### 자막/캡션
- `@remotion/captions` 패키지 사용
- JSON/SRT 자막 파일 로드 → 타임스탬프 동기화

### 트랜지션
- `@remotion/transitions` — slide, fade, wipe 등
- `<TransitionSeries>` 컴포넌트로 장면 전환

### Tailwind CSS
- `@remotion/tailwind` 설정 후 className 사용 가능

### 3D 콘텐츠
- `@react-three/fiber` + `@remotion/three`
- Three.js 씬을 Remotion 타임라인에 동기화

## 렌더링

```bash
# 기본 렌더링
cd $HOME/remotion-videos
npx remotion render MyVideo out/video.mp4

# 고품질
npx remotion render MyVideo out/video.mp4 --codec h264 --crf 18

# 투명 배경 (WebM)
npx remotion render MyVideo out/video.webm --codec vp8

# GIF
npx remotion render MyVideo out/animation.gif --every-nth-frame 2
```

## 제작 워크플로우

1. **기획:** 장면 구성, 길이, 해상도 결정
2. **에셋 준비:** 이미지, 음악, 폰트 → public/ 폴더
3. **컴포넌트 코딩:** React로 각 장면 제작
4. **프리뷰:** `npx remotion studio` (MiniPC 브라우저)
5. **렌더링:** headless 렌더링 → MP4/WebM
6. **전송:** HTTP 서버로 맥 스튜디오에 전달

## ⚠️ 주의사항

- **서브에이전트 위임** — 영상 렌더링은 시간 소모적
- **30fps 기본** — 필요 시 60fps로 변경
- **메모리 주의** — 고해상도 + 긴 영상은 MiniPC RAM 한계 주의
- **GitHub push 불가** (MiniPC) — 맥 스튜디오에서 push
