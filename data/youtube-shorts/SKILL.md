---
name: youtube-shorts
description: "AI/DevOps 유튜브 숏츠 자동 생성. 트렌드 수집 → 스크립트 → 이미지 → Veo 영상 → TTS 나레이션 → Remotion 합성 → YouTube 업로드"
version: "2.0.0"
allowed-tools: Bash, Read, Write, Glob, Grep
metadata:
  openclaw:
    requires:
      tools:
        - bash
        - exec
      env:
        - GEMINI_API_KEY
      binaries:
        - python3
        - node
---

# YouTube Shorts 자동 생성

이 스킬은 AI/DevOps 주제의 60초 한국어 유튜브 숏츠를 자동으로 생성합니다.

## 사용법

사용자가 다음과 같이 요청하면 이 스킬을 실행하세요:
- "숏츠 만들어줘"
- "숏츠 주제 뽑아줘"
- "[주제명] 숏츠 만들어줘"
- "트렌드만 수집해줘"

## 설치

소스코드 전체가 필요합니다. GitHub에서 클론하세요:
```bash
git clone https://github.com/kangjjang/youtube-shorts-skill.git
cd youtube-shorts-skill
bash scripts/setup.sh
```

## 실행 방법

스킬 루트 디렉토리: `${CLAUDE_PLUGIN_ROOT}` (Claude Code) 또는 클론한 레포 디렉토리

### 1. 환경 확인
```bash
cd ${CLAUDE_PLUGIN_ROOT:-youtube-shorts-skill}
source .venv/bin/activate 2>/dev/null || { python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt; }
```

### 2. 명령어

| 요청 | 실행 명령 |
|------|-----------|
| 전체 파이프라인 (대화형) | `python main.py` |
| 자동 선택 + 비공개 업로드 | `python main.py --auto --upload` |
| 특정 주제로 생성 | `python main.py --auto generate --topic "주제명"` |
| 트렌드만 수집 | `python main.py trends` |
| 기존 영상 업로드 | `python main.py upload --dir outputs/디렉토리` |
| 고품질 모드 | `python main.py --auto --quality full` |

### 3. 파이프라인 흐름
```
트렌드 → 주제 → 스크립트 → 이미지 → Veo 클립 ─┐
                                                 ├→ Remotion 합성 → SEO → 업로드
                          스크립트 → Gemini TTS ──┘
```

9단계: 트렌드 수집 → 주제 선정 → 스크립트 작성 → 이미지 생성 → Veo 영상 → TTS 나레이션 → Remotion 합성 → SEO → 업로드

### 4. 필수 환경변수
- `GEMINI_API_KEY`: Gemini API 키 (텍스트, 이미지, 영상, TTS 모두 사용)

### 5. 비용 안내
- Veo 3.1 Fast: 숏츠 1편당 ~$2.40
- Veo 3.1 Full: 숏츠 1편당 ~$7.20
- 영상 생성 전 비용 체크포인트에서 확인 가능

### 6. 출력 결과
`outputs/YYYY-MM-DD-[slug]/` 디렉토리에:
- `script.json` — 스크립트
- `frames/` — 키프레임 이미지
- `clips/` — Veo 영상 클립
- `narration.wav` — TTS 나레이션
- `final_shorts.mp4` — 최종 합성 영상
- `seo.json` — SEO 메타데이터
