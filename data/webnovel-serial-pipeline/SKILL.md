---
name: webnovel-serial-pipeline
version: 0.1.4
description: Build and publish a Quartz-hosted Korean web-novel serial (draft→cover→webp→episode md→lint→publish). Uses Nano Banana Pro + ffmpeg.
---

# WebNovel Serial Pipeline (Quartz)

## ⚠️ Security Notice

This skill may trigger antivirus false positives due to:
- **Shell scripts (.sh)**: Used ONLY for ffmpeg image conversion and dependency checks
- **subprocess calls**: Used ONLY to invoke Python linting scripts
- **prepublish_check.py**: Security scanner that looks for malicious patterns (ironically flagged by AV)
  - Contains regex patterns like `curl`, `wget` to DETECT (not execute) malicious code
  - This is a SECURITY FEATURE, not malware

All code is open source and auditable. No malicious behavior.

---

This skill documents the end-to-end workflow we used for **Quartz-hosted** Korean web-novel serials (e.g., `Drama/야간조`).

## Quick Start (copy/paste)
From a terminal:
```bash
# 1) Install
clawhub install webnovel-serial-pipeline

# 2) Go to the skill folder
cd skills/webnovel-serial-pipeline

# 3) Set your Quartz root (env var)
export WEBNOVEL_QUARTZ_ROOT="/absolute/path/to/8.quartz"

# 4) Verify deps
bash scripts/check_deps.sh

# 5) After you say “검수 완료”, publish + sync index
bash scripts/publish_review_ok.sh --series "야간조" --episode 2 --slug "불-꺼지면-가지-마세요" --draft-file "/path/to/draft.md"
```

## Goals

- Episodes are **readable** (no "writer commentary" tone)
- Every episode has **at least 1 image**
- Images are **lightweight** for the web: `1K → webp (q 70~80, max 1200px)`
- Publishing is safe: **draft in archive → move to Quartz only after review**

## Design & Requirements (before writing)

This section captures the **proposal + requirements analysis** process we used (the part *before* the pipeline).

### Kickoff 질문(한 번에 던지기, 선택형)
아래 질문을 **한 메시지로** 던지고, 사용자가 선택/응답하면 그걸로 톤을 고정한다.

- **장르(선택)**: 드라마 / 오피스 스릴러 / 블랙코미디 / 로맨스(현실톤)
- **레퍼런스(선택)**: (이게 KICK) 사용자가 *이미 아는 드라마 톤*을 고르면, 설명 없이도 문장/연출/감정선이 바로 고정된다.
  - 예시: 나의 아저씨 / 미생 / D.P. / 나의 해방일지 / 더 글로리(톤만) / 시그널 / 비밀의 숲 / 나쁜 녀석들 / 괴물 / 마이 네임
  - 추천 방식: **메인 1개 + 보조 1개** 선택
- **수위(선택)**: 12세 / 15세 / 청불
- **에피소드 길이(선택)**: 3~5분 분량 / 5~10분 분량(웹소설 체감 길이)
- **배경(선택)**: 구도심 / 강남 오피스 / 주거지 / 공공기관
- **캐릭터(필수)**: 2~6명 (이름 + 한 줄 성격)

### 유치함 방지(기본값 8룰)
- 현실 기반 갈등(일/돈/윤리/관계). 초능력·과장 금지.
- 밈/유행어/오글 멘트 금지.
- 설명충 금지: “말로 설명” 대신 “행동/선택”으로 보여주기.
- 서브텍스트(겉말≠속마음) 1~2번은 반드시 넣기.
- 선악 이분법 금지: 결함+욕망+두려움 3요소로 캐릭터 설계.
- 코미디는 ‘사람을 조롱’하지 말고 상황/아이러니로.
- 과한 효과/폰트/감정 과장 금지(문장 톤도 포함).
- 엔딩은 해피/불행보다 “후폭풍(대가)”를 남기기.

### 성숙도(퀄리티) 루브릭 — 자동 체크
- 오글/밈 대사 0개
- 설명 대사 비율 20% 이하(대부분 행동/선택)
- 인물 2명 이상이 서로 다른 목표로 충돌
- 사건의 결과(대가)가 최소 1개 남음(돈/관계/신뢰/평판)

### 시즌(10부작) 설계 템플릿
- EP01: 훅/트리거(사건 씨앗을 “확정”으로 박기)
- EP02: 첫 사건(한 단계 전진)
- EP03~04: 구조/연결고리 드러남(우연→패턴)
- EP05: ‘왜 신고하지 못하는가’ 같은 현실적 제약 공개
- EP06~07: 선택 강요(관계/돈/윤리의 대가)
- EP08: 정체/구조의 윤곽(내부자/책임 전가)
- EP09: 한 번만(돌이킬 수 없는 선택)
- EP10: 해결보다 “이후”로 마무리(과장 없이)

### 관계 설계 규칙(절제된 애틋함)
- “스몰토크로 친해지기” 금지 → **작은 빚 2번**으로 관계를 앞으로 당긴다.
  - A→B: 사소한 배려 1번(말보다 행동)
  - B→A: 말 없는 현실 도움 1번(영웅 금지)
- 호칭은 현실적으로:
  - 이름을 알기 전: 최소한(직업/기능 대사 위주)
  - 이름을 확인한 뒤: “아저씨” 같은 호칭은 피하고 **이름(도현 씨)**로.

---

## Setup for distribution (paths + optional APIs)

### 1) Set your Quartz root (deploy folder)
For distribution we **do not hardcode** machine-specific paths.

Required environment variable:
- `WEBNOVEL_QUARTZ_ROOT` = your Quartz vault root (published content folder)

Optional:
- `WEBNOVEL_DRAFT_ROOT` = where you keep drafts
- `NANO_BANANA_KEY` (only if you generate covers using nano-banana-pro)

Example:
```bash
export WEBNOVEL_QUARTZ_ROOT="/absolute/path/to/8.quartz"
export WEBNOVEL_DRAFT_ROOT="/absolute/path/to/drafts"   # optional
```

### 2) Dependency check
From inside this skill folder:
```bash
bash scripts/check_deps.sh
```

### 3) Pre-publish safety check (ClawHub)
Before `clawhub publish`, run:
```bash
python3 scripts/prepublish_check.py
```
This fails if obvious exfil/download markers are found.

## Folder convention

- Quartz vault root (published):
  - `$WEBNOVEL_QUARTZ_ROOT` (example: `/path/to/8.quartz`)
- Example series folder:
  - `Drama/<series>/index.md` (landing + 제작 규칙)
  - `Drama/<series>/<series>-01-....md` (published episodes)
  - `Drama/<series>/images/*.webp` (covers)
- Drafts (NOT published):
  - `$WEBNOVEL_DRAFT_ROOT/<series>_serial_drafts/` (example: `/path/to/drafts/yaganjo_serial_drafts/`)

## Workflow (recommended)

### 0) Decide the "episode job"
- EP01: **hook/trigger** (plant the seed)
- EP02+: **progress** (one new event per episode)

### 1) Create an episode draft
Write the episode in the drafts folder first.

### 2) Cover image (1K)
Generate cover PNG (1K) using Nano Banana Pro, then convert to WebP.

### 3) Embed + tags
- Ensure frontmatter tags include the 6-axis tags:
  - `domain/topic/format/audience/intent/lang`
- Embed cover early in the episode body using a Quartz wikilink:
  - `![[Drama/<series>/images/<cover>.webp]]`

### 4) Lint (style checks)
Before publishing, run a quick linter:
- ban repetitive patterns: `같아서/것 같아서`
- avoid writer commentary tone: overuse of generalizations
- keep dialogue natural and short

### 5) Publish (move to Quartz)
Only after the user says OK.

Recommended publish command (copies draft into Quartz and normalizes filename):
```bash
python3 scripts/publish_episode.py \
  --draft-file /path/to/draft.md \
  --quartz-root "$WEBNOVEL_QUARTZ_ROOT" \
  --series-dir "$WEBNOVEL_QUARTZ_ROOT/Drama/<series>" \
  --series "<series>" \
  --episode 2 \
  --slug "불-꺼지면-가지-마세요"
```

### 6) Sync index.md episode list (optional, recommended)
Add markers once in `Drama/<series>/index.md`:

```md
## 에피소드
<!-- episodes:start -->
<!-- episodes:end -->
```

Then run:
```bash
python3 scripts/sync_index.py \
  --index-file "$WEBNOVEL_QUARTZ_ROOT/Drama/<series>/index.md" \
  --series-dir "$WEBNOVEL_QUARTZ_ROOT/Drama/<series>" \
  --series "<series>"
```

### One-shot publish workflow (ONLY after chat confirmation: “검수 완료”)
This is the recommended human-safe workflow: wait for the user to explicitly say **검수 완료**, then run:

```bash
bash scripts/publish_review_ok.sh \
  --series "야간조" \
  --episode 2 \
  --slug "불-꺼지면-가지-마세요" \
  --draft-file "/path/to/drafts/yaganjo_serial_drafts/야간조-연재-02-불-꺼지면-가지-마세요.md"
```

It will:
- lint + asset-check + copy into Quartz (public)
- sync `Drama/<series>/index.md` between episode markers

## Scripts

### A) Create episode stub
```bash
python3 scripts/new_episode.py \
  --series "야간조" \
  --series-dir "$WEBNOVEL_QUARTZ_ROOT/Drama/야간조" \
  --episode 2 \
  --slug "불-꺼지면-가지-마세요" \
  --draft-dir "/path/to/drafts/yaganjo_serial_drafts"
```

### B) Convert PNG→WebP (fast)
```bash
bash scripts/to_webp.sh \
  /path/to/cover.png \
  /path/to/cover.webp
```

### C) Lint an episode
```bash
python3 scripts/lint_episode.py \
  --file /path/to/episode.md
```

## Production rules (the ones we actually used)

- **No writer commentary**: remove lines like “그래서 더 진짜였다”
- **Show, don’t explain**: replace intention-explanations with actions
- **No pattern spam**: especially `~같아서` chains
- **Relationship progression**: use **two small debts** (A→B and B→A), not long small talk
- **Hook**: end every episode with a single, sharp next-step trigger
