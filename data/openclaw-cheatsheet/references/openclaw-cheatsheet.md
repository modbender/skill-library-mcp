> 팀 규칙: OpenClaw 설정을 변경하기 전에 반드시 이 문서를 먼저 읽고 작업할 것.
>
> (설정 변경: config set / apply / update / gateway 관련 작업 포함)

# OpenClaw CLI Cheatsheet

## Agent

```bash
# 에이전트 호출 (게이트웨이 경유)
openclaw agent --agent <id> --message "메시지" --json

# 로컬 실행 (게이트웨이 세션 격리)
openclaw agent --agent <id> --local --message "메시지" --json

# 타임아웃 지정 (초)
openclaw agent --agent <id> --message "..." --timeout 120

# 특정 세션 지정
openclaw agent --agent <id> --session-id <uuid> --message "..."

# thinking 레벨 지정
openclaw agent --agent <id> --message "..." --thinking medium
```

## Message

```bash
# 메시지 전송
openclaw message send --channel discord --target <channel_id> --message "내용"

# 스레드 생성
openclaw message thread create --channel discord --target <channel_id> \
  --thread-name "스레드명" --message "첫 메시지" --json

# 스레드 답장
openclaw message thread reply --channel discord --target <channel_id> \
  --message "답장" --reply-to <message_id>

# 스레드 목록
openclaw message thread list --channel discord --target <channel_id>

# 메시지 검색
openclaw message search --channel discord --target <channel_id> --query "검색어"

# 리액션 추가
openclaw message react --channel discord --target <channel_id> \
  --message-id <id> --emoji "✅"

# dry-run (전송 안 함, payload만 확인)
openclaw message thread create ... --dry-run
```

## Config

```bash
# 값 조회
openclaw config get <dot.path>
openclaw config get channels.discord

# 값 설정 (JSON 파싱)
openclaw config set <dot.path> '<json>' --json

# 값 삭제
openclaw config unset <dot.path>

# 배열 요소 접근
openclaw config get 'bindings[0]'
openclaw config set 'bindings[1]' '{"agentId":"echo"}' --json
```

## Sessions

```bash
# 전체 세션 목록
openclaw sessions

# 최근 N분간 활성 세션
openclaw sessions --active 30

# 특정 에이전트 세션 조회
openclaw sessions --store ~/.openclaw/agents/<id>/sessions/sessions.json

# JSON 출력
openclaw sessions --json
```

## Gateway (daemon)

```bash
openclaw daemon status     # 상태 확인
openclaw daemon start      # 시작
openclaw daemon stop       # 중지
openclaw daemon restart    # 재시작
openclaw daemon install    # 서비스 등록
openclaw daemon uninstall  # 서비스 해제
```

## Skills

```bash
openclaw skills list              # 스킬 목록
openclaw skills list --eligible   # 사용 가능한 것만
openclaw skills info <name>       # 스킬 상세
openclaw skills check             # 준비 상태 점검
```

## Agents 관리

```bash
openclaw agents list                          # 에이전트 목록
openclaw agents add                           # 추가
openclaw agents delete                        # 삭제
openclaw agents set-identity --agent <id>     # 이름/아바타 변경
```

## Obsidian (obsidian-cli)

```bash
# 노트 생성
obsidian-cli create "<경로>" --content "내용" --vault <vault명>

# 노트 덮어쓰기
obsidian-cli create "<경로>" --content "내용" --vault <vault명> --overwrite

# 노트 읽기
obsidian-cli print "<경로>" --vault <vault명>

# 검색
obsidian-cli search "<키워드>" --vault <vault명>

# 내용 검색
obsidian-cli search-content "<키워드>" --vault <vault명>

# 삭제
obsidian-cli delete "<경로>" --vault <vault명>
```

## 환경변수 (.env)

| 변수 | 용도 |
|------|------|
| `DISCORD_PANEL_WEBHOOK_URL` | 디스코드 웹훅 (에이전트 페르소나 전송) |
| `DISCORD_COUNCIL_CHANNEL_ID` | 토론 스레드 생성 채널 |
| `DISCORD_GUILD_ID` | 디스코드 서버 ID |
| `ECHO_AVATAR_URL` | 에코 아바타 (옵션) |
| `NOAH_AVATAR_URL` | 노아 아바타 (옵션) |
| `KAI_AVATAR_URL` | 케이 아바타 (옵션) |
| `DISCUSSION_LOG_DIR` | 토론 로그 저장 경로 (기본: ~/.openclaw/logs/) |

## Discussion Runner

```bash
# dryrun (더미 응답, CLI 호출 안 함)
node ~/.openclaw/workspace-shared/scripts/discussion/discussion_runner.js \
  --topic "주제" --mode dryrun --rounds 3

# 실제 실행
node ~/.openclaw/workspace-shared/scripts/discussion/discussion_runner.js \
  --topic "주제" --mode live --rounds 3
```
