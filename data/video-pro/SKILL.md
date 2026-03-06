---
name: video-pro
description: MiniPC 노드(Remotion + FFmpeg)를 활용한 실전형 비디오 에디팅 스킬. 프로그래밍 방식의 영상 제작부터 컷 편집, 자막 합성, 포맷 변환까지 지원합니다.
---

# 🎬 Video Pro (Miss Kim Edition)

MiniPC 노드의 강력한 리소스를 사용하여 고성능 비디오 에디팅을 수행합니다. Remotion을 이용한 코드 기반 영상 생성과 FFmpeg을 이용한 정밀 가공을 결합합니다.

## 🏗️ 환경 설정 (MiniPC)

- **IP:** `<MINIPC_IP>` (Tailscale)
- **Remotion 프로젝트:** `$HOME/remotion-videos`
- **FFmpeg:** 전역 설치됨

---

## 🚀 주요 기능

### 1. Remotion 컴포넌트 렌더링
React 코드를 MP4 영상으로 렌더링합니다. 데이터 기반의 개인화 영상 제작에 탁월합니다.

**실행 방법:**
```bash
# MiniPC에서 실행
cd $HOME/remotion-videos
npx remotion render <CompositionId> out/video.mp4 --props '{"title": "안녕, 미스 김!"}'
```

### 2. FFmpeg 정밀 가공
가장 빈번하게 사용되는 실전용 명령어 모음입니다.

| 작업 | 명령어 |
|------|-------|
| **컷 편집** | `ffmpeg -y -i input.mp4 -ss 00:00:10 -to 00:00:20 -c copy output.mp4` |
| **자막 합성(Burn-in)** | `ffmpeg -y -i input.mp4 -vf "subtitles='input.srt'" output.mp4` |
| **포맷 변환 (MOV→MP4)** | `ffmpeg -y -i input.mov -c:v libx264 -c:a aac output.mp4` |
| **오디오 추출 (MP3)** | `ffmpeg -y -i input.mp4 -vn -acodec libmp3lame output.mp3` |
| **영상 음소거** | `ffmpeg -y -i input.mp4 -an -c:v copy output.mp4` |
| **GIF 변환** | `ffmpeg -y -i input.mp4 -vf "fps=15,scale=480:-1" -loop 0 output.gif` |
| **해상도 변경 (720p)** | `ffmpeg -y -i input.mp4 -vf "scale=1280:720" -c:a copy output.mp4` |

### 3. AI 자막 (Whisper) 연동 설계
오디오를 텍스트로 변환하여 자막 파일을 생성하고 영상에 입히는 워크플로우입니다.

1. **오디오 추출:** FFmpeg을 사용하여 영상에서 오디오만 추출합니다.
2. **전사 (Transcription):** Whisper 모델(Mac Studio 또는 MiniPC)을 사용하여 `.srt` 파일을 생성합니다.
3. **자막 합성:** FFmpeg의 `subtitles` 필터를 사용하여 영상에 자막을 영구적으로 입힙니다 (Burn-in).

---

## 🛠️ 실전 활용 패턴 (nodes.run)

서브에이전트가 MiniPC에 명령을 내릴 때 다음 패턴을 사용합니다.

```javascript
// MiniPC에서 렌더링 후 결과물 확인
await nodes.run({
  node: "MiniPC",
  command: "cd $HOME/remotion-videos && npx remotion render MyComp out/result.mp4"
});
```

## ⚠️ 주의사항

1. **MiniPC 경로:** 항상 `$HOME/` 기준 절대 경로를 확인하세요.
2. **성능:** Remotion 렌더링은 CPU 집약적입니다. 가급적 서브에이전트를 통해 백그라운드에서 실행하세요.
3. **자막 경로:** FFmpeg `subtitles` 필터 사용 시 경로에 특수문자가 있다면 이스케이프 처리가 필요할 수 있습니다.
4. **대용량 파일:** 노드 간 대용량 파일 전송은 가급적 피하고, MiniPC 내부에서 가공을 완료한 후 최종 결과물만 가져오세요.

---
*미스 김의 비디오 스킬은 실전에서의 효율성과 결과물의 품질을 최우선으로 합니다.* 💋
