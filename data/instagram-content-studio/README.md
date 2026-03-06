# instagram-api

An [Agent Skills](https://agentskills.io) skill for managing an Instagram account. Works with both **Claude Code** and **OpenAI Codex**.

Agents execute individual scripts under `scripts/` and interpret JSON results — no interactive CLI involved.

## Features

- View profile and posts
- Publish single images or carousels (up to 10)
- Publish videos as Reels or video carousels (up to 10)
- Post from URLs or local files (via cloudflared tunnel)
- HEIC/HEIF auto-conversion to JPEG
- Read, write, and reply to comments
- Automatic token refresh on every command

## Setup

### 1. Install dependencies

```bash
npm install
```

### 2. Configure credentials

```bash
cp .env.example .env
```

Fill in your `.env`:

```
INSTAGRAM_ACCESS_TOKEN=<your-access-token>

# Recommended for comment/reply flows (uses Facebook Graph API)
FACEBOOK_USER_ACCESS_TOKEN=<your-fb-user-token>

# Required for FB token refresh
FACEBOOK_APP_ID=<fb-app-id>
FACEBOOK_APP_SECRET=<fb-app-secret>
```

To obtain these credentials:

1. Create a **Meta App** at [developers.facebook.com](https://developers.facebook.com/) and add the **Instagram** product.
2. In the App Dashboard, find your **App ID** and **App Secret** under App Settings > Basic (used as `FACEBOOK_APP_ID` / `FACEBOOK_APP_SECRET`).
3. Generate a **short-lived access token** via the Instagram Graph API Explorer or the Token Generator in the App Dashboard.
4. Exchange it for a **long-lived access token** (valid for 60 days, auto-refreshed by this skill):
   ```
   GET https://graph.instagram.com/access_token
     ?grant_type=ig_exchange_token
     &client_secret=<APP_SECRET>
     &access_token=<SHORT_LIVED_TOKEN>
   ```

### 3. Install cloudflared (for local image/video posting)

```bash
# macOS
brew install cloudflared

# Ubuntu / Debian
curl -L -o cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-$(dpkg --print-architecture).deb
sudo dpkg -i cloudflared.deb
```

## Install as a Skill

### Claude Code

```bash
ln -s "$(pwd)" ~/.claude/skills/instagram-api
```

Then use `/instagram-api` or let Claude invoke it automatically.

### OpenAI Codex

```bash
ln -s "$(pwd)" ~/.agents/skills/instagram-api
```

## Scripts

All scripts output JSON to stdout and logs to stderr.
All scripts support `--env <path>` to use a custom `.env` file.

| Script | Description |
|--------|-------------|
| `node scripts/get-profile.js` | View profile |
| `node scripts/get-posts.js [--limit N]` | List posts |
| `node scripts/get-post.js <media-id>` | View post detail |
| `node scripts/post-image.js --caption "..." <images>` | Publish image(s) |
| `node scripts/post-video.js --caption "..." <videos>` | Publish video(s) / Reels |
| `node scripts/get-comments.js <media-id>` | View comments |
| `node scripts/post-comment.js <media-id> --text "..."` | Post comment |
| `node scripts/reply-comment.js <comment-id> --text "..."` | Reply to comment |
| `node scripts/refresh-token.js` | Manually refresh IG token |
| `node scripts/refresh-facebook-token.js` | Manually refresh FB user token |

### Image publishing examples

```bash
# Single image from URL
node scripts/post-image.js --caption "Hello" https://example.com/photo.jpg

# Single local image
node scripts/post-image.js --caption "Hello" ./photo.png

# Carousel from local files
node scripts/post-image.js --caption "Hello" ./a.png ./b.jpg ./c.heic
```

### Video publishing examples

```bash
# Single video from URL (Reels)
node scripts/post-video.js --caption "Hello" https://example.com/video.mp4

# Single local video with cover image
node scripts/post-video.js --caption "Hello" --cover ./cover.jpg ./clip.mp4

# Video carousel from local files
node scripts/post-video.js --caption "Hello" ./a.mp4 ./b.mov
```

### Note on local video posting

Local file posting uses a cloudflared Quick Tunnel to temporarily expose files so that Instagram's servers can download them. This works well for images and small videos, but large video files (30MB+) may experience instability — Quick Tunnels have no uptime SLA, and slow transfer speeds can cause Instagram to timeout during the download. For reliable large video posting, consider uploading the video to a public URL first and passing the URL directly.

## Security

- **Token storage**: Token refresh overwrites values in `.env` in plaintext. Never commit `.env` to version control.
- **Local file upload**: A temporary cloudflared tunnel exposes files during upload only. The tunnel shuts down immediately after. Only provide file paths you are comfortable briefly exposing.
- **Minimum permissions**: Create a dedicated Meta app and grant only: `instagram_business_basic`, `instagram_content_publish`, `instagram_manage_comments`, `pages_read_engagement`, `pages_show_list`.

## Requirements

- Node.js v22+
- `cloudflared` — for local image/video posting only
- Instagram Graph API credentials (long-lived access token)

## Project Structure

```
instagram-api/
├── SKILL.md              # Skill entrypoint (agent instructions)
├── SPEC.md               # Technical specification
├── agents/
│   └── openai.yaml       # Codex config
├── scripts/
│   ├── _common.js        # Shared module (API, auth, tunnel, media)
│   ├── get-profile.js
│   ├── get-posts.js
│   ├── get-post.js
│   ├── post-image.js
│   ├── post-video.js
│   ├── get-comments.js
│   ├── post-comment.js
│   ├── reply-comment.js
│   ├── refresh-token.js
│   └── refresh-facebook-token.js
├── .env                  # Credentials (not committed)
└── package.json
```

---

# instagram-api (한국어)

Instagram 계정을 관리하는 [Agent Skills](https://agentskills.io) 스킬. **Claude Code**와 **OpenAI Codex** 모두에서 동작한다.

에이전트가 `scripts/` 하위의 개별 스크립트를 실행하고 JSON 결과를 해석하는 구조이다.

## 기능

- 프로필 및 게시물 조회
- 단일 이미지 또는 캐러셀 게시 (최대 10장)
- 비디오(Reels) 또는 비디오 캐러셀 게시 (최대 10개)
- URL 또는 로컬 파일로 게시 (cloudflared 터널 사용)
- HEIC/HEIF 이미지 자동 JPEG 변환
- 댓글 조회, 작성, 답글
- 매 명령 실행 시 자동 토큰 갱신

## 설정

### 1. 의존성 설치

```bash
npm install
```

### 2. 인스타그램 자격 증명 발급 및 설정

이 스킬을 사용하려면 **Meta 앱**과 **Instagram 장기 액세스 토큰**이 필요하다.

#### Meta 앱 생성

1. [developers.facebook.com](https://developers.facebook.com/)에서 **Meta 앱**을 생성하고 **Instagram** 제품을 추가한다.
2. 앱 대시보드의 앱 설정 > 기본에서 **앱 ID**와 **앱 시크릿**을 확인한다.

#### 장기 액세스 토큰 발급

1. Instagram Graph API 탐색기 또는 앱 대시보드의 토큰 생성기에서 **단기 액세스 토큰**을 발급받는다.
2. 아래 API를 호출하여 **장기 액세스 토큰**으로 교환한다 (유효기간 60일, 이 스킬이 자동 갱신):
   ```
   GET https://graph.instagram.com/access_token
     ?grant_type=ig_exchange_token
     &client_secret=<앱_시크릿>
     &access_token=<단기_토큰>
   ```

#### .env 설정

```bash
cp .env.example .env
```

```
INSTAGRAM_ACCESS_TOKEN=<장기-액세스-토큰>

# 댓글/답글 흐름에 권장 (Facebook Graph API 사용)
FACEBOOK_USER_ACCESS_TOKEN=<FB-사용자-토큰>

# FB 토큰 갱신 시 필수
FACEBOOK_APP_ID=<FB-앱-ID>
FACEBOOK_APP_SECRET=<FB-앱-시크릿>
```

### 3. cloudflared 설치 (로컬 이미지/비디오 게시 시 필요)

```bash
# macOS
brew install cloudflared

# Ubuntu / Debian
curl -L -o cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-$(dpkg --print-architecture).deb
sudo dpkg -i cloudflared.deb
```

## 스킬 설치

### Claude Code

```bash
ln -s "$(pwd)" ~/.claude/skills/instagram-api
```

이후 `/instagram-api`로 호출하거나 Claude가 자동으로 사용한다.

### OpenAI Codex

```bash
ln -s "$(pwd)" ~/.agents/skills/instagram-api
```

## 스크립트

모든 스크립트는 stdout에 JSON을 출력하고, 로그는 stderr로 보낸다.
모든 스크립트는 `--env <경로>`로 커스텀 `.env` 파일을 지정할 수 있다.

| 스크립트 | 설명 |
|----------|------|
| `node scripts/get-profile.js` | 프로필 조회 |
| `node scripts/get-posts.js [--limit N]` | 게시물 목록 조회 |
| `node scripts/get-post.js <media-id>` | 게시물 상세 조회 |
| `node scripts/post-image.js --caption "..." <이미지>` | 이미지 게시 |
| `node scripts/post-video.js --caption "..." <비디오>` | 비디오(Reels) 게시 |
| `node scripts/get-comments.js <media-id>` | 댓글 조회 |
| `node scripts/post-comment.js <media-id> --text "..."` | 댓글 작성 |
| `node scripts/reply-comment.js <comment-id> --text "..."` | 답글 작성 |
| `node scripts/refresh-token.js` | IG 수동 토큰 갱신 |
| `node scripts/refresh-facebook-token.js` | FB 사용자 토큰 수동 갱신 |

### 이미지 게시 예시

```bash
# URL 단일 이미지
node scripts/post-image.js --caption "안녕" https://example.com/photo.jpg

# 로컬 단일 이미지
node scripts/post-image.js --caption "안녕" ./photo.png

# 로컬 캐러셀 (여러 장)
node scripts/post-image.js --caption "안녕" ./a.png ./b.jpg ./c.heic
```

### 비디오 게시 예시

```bash
# URL 단일 비디오 (Reels)
node scripts/post-video.js --caption "안녕" https://example.com/video.mp4

# 로컬 단일 비디오 (커버 이미지 포함)
node scripts/post-video.js --caption "안녕" --cover ./cover.jpg ./clip.mp4

# 로컬 비디오 캐러셀 (여러 개)
node scripts/post-video.js --caption "안녕" ./a.mp4 ./b.mov
```

### 로컬 비디오 게시 시 참고사항

로컬 파일 게시는 cloudflared Quick Tunnel을 사용하여 파일을 임시로 노출하고, Instagram 서버가 이를 다운로드하는 방식이다. 이미지나 작은 비디오에는 문제없이 동작하지만, 대용량 비디오(30MB 이상)의 경우 Quick Tunnel의 불안정성(SLA 없음)과 느린 전송 속도로 인해 Instagram 측 다운로드 타임아웃이 발생할 수 있다. 대용량 비디오를 안정적으로 게시하려면 먼저 공개 URL에 업로드한 뒤 URL을 직접 전달하는 것을 권장한다.

## 보안

- **토큰 저장**: 토큰 갱신 시 `.env` 파일에 평문으로 덮어쓴다. `.env`를 버전 관리에 절대 커밋하지 말 것.
- **로컬 파일 업로드**: 업로드 중에만 cloudflared 터널로 파일이 임시 노출된다. 업로드 완료 즉시 터널이 종료된다. 인터넷에 잠시 노출되어도 괜찮은 파일만 사용할 것.
- **최소 권한**: 전용 Meta 앱을 생성하고 필요한 최소 권한만 부여할 것: `instagram_business_basic`, `instagram_content_publish`, `instagram_manage_comments`, `pages_read_engagement`, `pages_show_list`.

## 요구사항

- Node.js v22+
- `cloudflared` — 로컬 이미지/비디오 게시 시에만 필요
- Instagram Graph API 자격 증명 (장기 액세스 토큰)
