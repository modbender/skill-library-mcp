---
name: katok
description: macOS 카카오톡 자동화 CLI. 친구 목록, 채팅방 목록, 메시지 읽기, 메시지 보내기를 지원합니다. 카카오톡 관련 작업이 필요할 때 사용하세요.
allowed-tools: Bash(katok *)
---

# KakaoTalk Automation with katok

macOS 접근성 API를 사용하여 카카오톡을 자동화합니다. 카카오톡 앱이 설치되어 있어야 하며, 접근성 권한이 필요합니다.

## Quick start

```bash
# 채팅방 목록 보기 (기본 명령)
katok chats
# 친구 목록 보기
katok friends
# 특정 채팅방 메시지 읽기
katok messages "홍길동"
# 메시지 보내기
katok send "홍길동" "안녕하세요"
```

## Commands

### chats (기본 명령)

채팅방 목록을 CSV 형식으로 출력합니다.

```bash
# 기본 (최근 50개)
katok chats
# 개수 제한
katok chats --limit 10
katok chats -l 10
# 건너뛰기 (페이지네이션)
katok chats --offset 20
katok chats -o 20
# 조합
katok chats -l 10 -o 20
```

출력 형식: `name,time,member_count,unread_count`

### friends

친구 목록을 CSV 형식으로 출력합니다. 섹션별로 `#` 구분자가 포함됩니다.

```bash
katok friends
```

출력 형식: `name,status_message`

### messages

특정 채팅방의 메시지를 CSV 형식으로 출력합니다. 시스템 메시지는 `#`으로 시작합니다.

```bash
# 기본 (최근 50개)
katok messages "채팅방 이름"
# 개수 제한
katok messages "채팅방 이름" --limit 20
katok messages "채팅방 이름" -l 20
```

출력 형식: `sender,content,time`

- 본인이 보낸 메시지의 sender는 `나`
- 이미지는 `[이미지]`로 표시
- 시스템 메시지는 `# 메시지 내용` 형식

### send

특정 채팅방에 메시지를 보냅니다.

```bash
katok send "채팅방 이름" "보낼 메시지"
```

## Example: 읽지 않은 채팅 확인

```bash
katok chats -l 10
# 출력에서 unread_count > 0인 채팅방 확인 후 메시지 읽기
katok messages "친구이름" -l 5
```

## Example: 메시지 읽고 답장

```bash
katok messages "친구이름" -l 10
katok send "친구이름" "확인했습니다!"
```

## Prerequisites

- **katok CLI**가 설치되어 있어야 합니다
  - 미설치 시: `brew install sunghyun-k/tap/katok`
- **카카오톡 macOS 앱**이 설치되어 있어야 합니다
  - 미설치 시: [카카오톡 다운로드 페이지](https://apps.apple.com/kr/app/kakaotalk/id869223134?mt=12)에서 설치하거나, `mas install 869223134` (mas-cli 필요)
  - 미실행 시 katok이 자동으로 실행합니다
- 터미널(또는 실행 환경)에 **macOS 접근성 권한**이 필요합니다
  - 시스템 설정 → 개인정보 보호 및 보안 → 접근성에서 터미널 앱을 허용하세요
- **화면보호기 또는 화면 잠김 상태에서는 작동하지 않습니다**
- 채팅방 이름은 정확히 일치해야 합니다
