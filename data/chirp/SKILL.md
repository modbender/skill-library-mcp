---
name: chirp
description: "X/Twitter CLI using OpenClaw browser tool. Use when the user wants to interact with X/Twitter: reading timeline, posting tweets, liking, retweeting, replying, or searching. Alternative to bird CLI for environments without Homebrew."
homepage: https://github.com/zizi-cat/chirp
metadata: {"clawdhub":{"emoji":"🐦"}}
---

# chirp

OpenClaw browser 도구로 X/Twitter 조작하기. bird CLI의 browser 기반 대안.

## Prerequisites

### 환경 요구사항
- OpenClaw with browser tool enabled
- `openclaw` browser profile
- X/Twitter 계정 로그인 완료

### Headless 서버인 경우

Xvfb 가상 디스플레이 필요 (spool 스킬의 Prerequisites 참고)

### 로그인 (처음 한 번만)

```
browser action=start profile=openclaw
browser action=open profile=openclaw targetUrl="https://x.com/login"
# 사용자에게 수동 로그인 요청
```

---

## 사용법

### 1. 타임라인 읽기

```
browser action=open profile=openclaw targetUrl="https://x.com/home"
browser action=snapshot profile=openclaw compact=true
```

각 article에서 작성자, 내용, 좋아요/리트윗/답글 수 확인 가능.

### 2. 트윗 작성

**Step 1: 홈에서 텍스트박스 찾기**
```
browser action=open profile=openclaw targetUrl="https://x.com/home"
browser action=snapshot profile=openclaw compact=true
```
→ `textbox "Post text"` ref 찾기

**Step 2: 내용 입력**
```
browser action=act profile=openclaw request={"kind":"click","ref":"<textbox-ref>"}
browser action=act profile=openclaw request={"kind":"type","ref":"<textbox-ref>","text":"트윗 내용"}
```

**Step 3: Post 버튼 클릭**
```
browser action=snapshot profile=openclaw compact=true
```
→ `button "Post"` ref 찾기 (disabled 아닌 것)
```
browser action=act profile=openclaw request={"kind":"click","ref":"<post-ref>"}
```

### 3. 좋아요 누르기

타임라인에서 article 내 `button "Like"` 또는 `button "X Likes. Like"` ref 찾아서:
```
browser action=act profile=openclaw request={"kind":"click","ref":"<like-ref>"}
```

### 4. 리트윗

`button "Repost"` 또는 `button "X reposts. Repost"` ref 찾아서:
```
browser action=act profile=openclaw request={"kind":"click","ref":"<repost-ref>"}
browser action=snapshot profile=openclaw compact=true
# "Repost" 옵션 선택
browser action=act profile=openclaw request={"kind":"click","ref":"<repost-option-ref>"}
```

### 5. 답글 달기

**방법 1: 타임라인에서**
```
browser action=act profile=openclaw request={"kind":"click","ref":"<reply-button-ref>"}
browser action=snapshot profile=openclaw compact=true
# 답글 입력창에 텍스트 입력 후 Reply 버튼 클릭
```

**방법 2: 트윗 페이지에서**
```
browser action=open profile=openclaw targetUrl="https://x.com/username/status/1234567890"
browser action=snapshot profile=openclaw compact=true
# 답글 입력창 찾아서 입력
```

### 6. 프로필 보기

```
browser action=open profile=openclaw targetUrl="https://x.com/username"
browser action=snapshot profile=openclaw compact=true
```

### 7. 검색

```
browser action=open profile=openclaw targetUrl="https://x.com/search?q=검색어&src=typed_query"
browser action=snapshot profile=openclaw compact=true
```

### 8. 팔로우

프로필 페이지에서 `button "Follow"` ref 찾아서:
```
browser action=act profile=openclaw request={"kind":"click","ref":"<follow-ref>"}
```

---

## 핵심 포인트

1. **snapshot 먼저** - 모든 작업 전에 현재 상태 확인
2. **ref는 매번 달라짐** - snapshot에서 항상 새로 찾기
3. **compact=true** - 토큰 절약
4. **article 구조** - 각 트윗은 article 요소, 내부에 작성자/내용/버튼들
5. **트윗 전 확인** - 사용자에게 내용 확인받기

---

## 트러블슈팅

| 문제 | 해결 |
|------|------|
| browser 안 됨 | Xvfb 확인, DISPLAY=:99, Gateway 재시작 |
| 로그인 안 됨 | `/login`으로 이동 후 수동 로그인 |
| Post 버튼 disabled | 텍스트 입력 확인 |
| Rate limit | 잠시 대기 후 재시도 |

---

## vs bird CLI

| 기능 | bird CLI | chirp (browser) |
|------|----------|-----------------|
| 설치 | brew 필요 | Xvfb만 있으면 됨 |
| 인증 | 쿠키 추출 | 브라우저 세션 |
| 안정성 | API 기반 | UI 의존 (변경 가능) |
| 속도 | 빠름 | 약간 느림 |
