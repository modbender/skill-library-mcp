# Workflow Runbook

## 1) 소스 선택
- 기본: `Trend/QuickView-YYMM-주차주.md`
- URL 입력 시 로컬 8.quartz markdown으로 매핑
- 운영 원칙: **매주 1개 WK 자료를 선정해 컨셉 1개를 잡고 제작**
  - 형식: "이번 주 컨셉: [핵심 문제] → [OpenClaw로 해결 행동]"

## 2) 대본 생성
- 템플릿: `references/podcast_prompt_template_ko.md`
- 저장: `archive/YYMMDD_*.txt`
- 모드 선택:
  - Full: 15~20분
  - Compressed: 5~7분
- 필수 점검:
  - 시스템/메타 문구 제거
  - 오프닝 소개 1회만
  - 짧은 구어체, 즉시 실행 가능한 팁 중심

## 3) 오디오 생성 (Gemini 멀티스피커, 권장)

### 권장: chunked 빌더 (타임아웃 방지)
```bash
# API 키를 환경변수로 설정 (NANO_BANANA_KEY 또는 GEMINI_API_KEY)
export GEMINI_API_KEY="$NANO_BANANA_KEY"

python3 scripts/build_dualvoice_audio.py \
  --input <script.txt> \
  --outdir <outdir> \
  --basename podcast_full_dualvoice \
  --chunk-lines 6
```

### 짧은 입력일 때 단일 호출
```bash
python3 scripts/gemini_multispeaker_tts.py \
  --input-file <dialogue.txt> \
  --outdir <outdir> \
  --basename podcast_dualvoice \
  --retries 3 \
  --timeout-seconds 120
```

기본 voice 매핑(수정 반영):
- Callie(여) → `Kore`
- Nick(남) → `Puck`

## 4) 자막 생성 (전체 문장 보존)
```bash
python3 scripts/build_korean_srt.py \
  --script <script.txt> \
  --audio <final.mp3> \
  --output <outdir>/podcast.srt \
  --max-chars 22
```

## 5) 자막 MP4 렌더
```bash
python3 scripts/render_subtitled_video.py \
  --image <thumbnail.png> \
  --audio <final.mp3> \
  --srt <outdir>/podcast.srt \
  --output <outdir>/final.mp4 \
  --font-name "Do Hyeon" \
  --font-size 27 \
  --shift-ms -250
```

권장값:
- 자막 폰트: `Do Hyeon` (가독성)
- 폰트 크기: 25~27
- 타이밍 보정: `-150 ~ -300ms`

## 6) 썸네일 + 메타 생성
```bash
# API 키를 환경변수로 설정
export GEMINI_API_KEY="$NANO_BANANA_KEY"

python3 scripts/build_podcast_assets.py \
  --source "<QuickView path or URL>"
```

## 7) 전달
또우에게 최소 5개 전달:
1. source
2. MP3
3. subtitle MP4
4. 썸네일
5. 제목 3개 + 설명

## 8) 문제 해결 빠른 가이드
- Gemini timeout 발생 → chunked 빌더 사용
- 자막 `...` 생략 문제 → `build_korean_srt.py` 사용 (전체 문장)
- 자막 잘림 → 폰트 크기 축소 + MarginV 증가
- 자막 밀림 → `--shift-ms` 음수로 보정
