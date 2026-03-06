# mac-notes-agent

macOS **Apple Notes** 앱과 연동하는 OpenClaw 스킬입니다.

- Apple Notes에 **노트를 생성/조회/수정/삭제/검색**할 수 있습니다.
- 내부 구현은 `osascript`(AppleScript)를 통해 Notes 앱을 제어하는 **Node.js CLI**입니다.

## 파일 구조

```text
mac-notes-agent/
├─ README.md       # 이 파일
├─ SKILL.md        # OpenClaw 스킬 메타데이터 + 사용법
├─ LICENSE         # CC-BY-NC-4.0
└─ cli.js          # Node.js CLI, AppleScript 브리지
```

## 설치 / 전제 조건

- macOS (Notes 앱 설치되어 있어야 함)
- Node.js (OpenClaw와 동일 환경)
- `osascript` 명령이 사용 가능해야 함 (기본 macOS 포함)

별도 npm 의존성 없음. Node.js 내장 `child_process`만 사용.

## 사용법

```bash
node cli.js <command> [options]
```

### 주요 명령

#### 1) 노트 추가 (add)

```bash
node cli.js add \
  --title "오늘 회의 메모" \
  --body "첫 줄\n둘째 줄\n셋째 줄" \
  --folder "Jarvis"
```

- `--title` (필수): 노트 제목
- `--body` (필수): 노트 본문. `\n`으로 줄바꿈.
- `--folder` (선택): Notes 폴더 이름. 없으면 기본 폴더 사용.

#### 2) 노트 목록 (list)

```bash
node cli.js list --folder "Jarvis"
```

#### 3) 노트 읽기 (get)

```bash
node cli.js get --folder "Jarvis" --title "회의 메모"
```

#### 4) 노트 수정 (update)

```bash
node cli.js update \
  --folder "Jarvis" \
  --title "회의 메모" \
  --body "새로운 내용으로 전체 교체"
```

#### 5) 노트에 내용 덧붙이기 (append)

```bash
node cli.js append \
  --folder "Jarvis" \
  --title "회의 메모" \
  --body "\n---\n추가 메모"
```

#### 6) 노트 삭제 (delete)

```bash
node cli.js delete --folder "Jarvis" --title "회의 메모"
```

#### 7) 검색 (search)

```bash
node cli.js search --query "키워드" --folder "Jarvis"
```

---

# mac-notes-agent (English)

OpenClaw skill that integrates with the macOS **Apple Notes** app.

- Create / list / read / update / append / delete / search notes in Apple Notes.
- Implemented as a **Node.js CLI** that talks to Notes via `osascript` (AppleScript).

## Requirements

- macOS with the built-in Notes app
- Node.js
- `osascript` available on PATH (default on macOS)

No external npm dependencies. Uses only Node.js built-in `child_process`.

## Usage

```bash
node cli.js <command> [options]
```

### Core commands

#### 1) Add note

```bash
node cli.js add \
  --title "Meeting notes" \
  --body "First line\nSecond line\nThird line" \
  --folder "Jarvis"
```

- `--title` (required): Note title
- `--body` (required): Note body. Use `\n` for line breaks.
- `--folder` (optional): Notes folder name.

#### 2) List notes

```bash
node cli.js list --folder "Jarvis"
```

#### 3) Get note

```bash
node cli.js get --folder "Jarvis" --title "Meeting notes"
```

#### 4) Update note

```bash
node cli.js update \
  --folder "Jarvis" \
  --title "Meeting notes" \
  --body "New full body"
```

#### 5) Append to note

```bash
node cli.js append \
  --folder "Jarvis" \
  --title "Meeting notes" \
  --body "\n---\nAdditional notes"
```

#### 6) Delete note

```bash
node cli.js delete --folder "Jarvis" --title "Meeting notes"
```

#### 7) Search notes

```bash
node cli.js search --query "keyword" --folder "Jarvis"
```

## License

CC-BY-NC-4.0
