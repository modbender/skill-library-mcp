---
name: Instagram API
description: Post to Instagram (Feed, Story, Reels, Carousel) and Threads using the official Meta Graph API. Requires Imgur for media hosting.
version: 1.1.1
author: raon
requires_env:
  - INSTAGRAM_ACCESS_TOKEN
  - INSTAGRAM_BUSINESS_ACCOUNT_ID
  - IMGUR_CLIENT_ID
---

# instagram-api

Meta Graph API를 사용해 Instagram과 Threads에 직접 포스팅하는 스킬.
미디어 호스팅은 Imgur API를 사용 (이미지/영상 공개 URL 생성).

---

## Imgur Client ID 발급

Instagram Graph API는 공개 URL로만 미디어를 업로드할 수 있어 Imgur가 필요합니다.

1. https://api.imgur.com/oauth2/addclient 접속
2. **Application name**: 원하는 이름 (예: `raon-instagram`)
3. **Authorization type**: `Anonymous usage without user authorization` 선택
4. **Authorization callback URL**: `https://localhost` (Anonymous이므로 형식만 맞추면 됨)
5. 이메일 입력 후 제출 → **Client ID** 확인
6. 환경변수 설정:
   ```bash
   export IMGUR_CLIENT_ID="your_client_id_here"
   ```

---

## 환경변수 설정

```bash
# ~/.openclaw/.env 또는 ~/.zshrc에 추가
export INSTAGRAM_ACCESS_TOKEN="your_token_here"
export INSTAGRAM_BUSINESS_ACCOUNT_ID="your_account_id_here"

# Threads (선택)
export THREADS_ACCESS_TOKEN="your_threads_token_here"
export THREADS_USER_ID="your_threads_user_id_here"

# Imgur (이미지 호스팅용 — 피드/릴스 업로드 시 필요)
export IMGUR_CLIENT_ID="your_imgur_client_id_here"
```

---

## Meta Graph API 토큰 발급

1. [Meta for Developers](https://developers.facebook.com/) 접속
2. 앱 생성 → Business 유형 선택
3. Instagram Graph API 제품 추가
4. **권한 요청**:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
5. **Access Token** 발급:
   - Graph API Explorer: https://developers.facebook.com/tools/explorer/
   - 장기 토큰(Long-lived token)으로 교환: 60일 유효
6. **Business Account ID** 확인:
   ```bash
   curl "https://graph.facebook.com/v21.0/me/accounts?access_token=YOUR_TOKEN"
   ```

> 💡 **Imgur Client ID**: https://api.imgur.com/oauth2/addclient (Anonymous usage 선택)

---

## 스크립트 사용법

### 피드 포스팅
```bash
bash scripts/post-feed.sh <이미지경로> <캡션파일>

# 예시
bash scripts/post-feed.sh ./photo.jpg ./caption.txt
```

### 스토리 포스팅
```bash
bash scripts/post-story.sh <이미지경로>

# 예시
bash scripts/post-story.sh ./story.jpg
```

### 릴스 포스팅
```bash
bash scripts/post-reels.sh <영상경로> <캡션파일>

# 예시
bash scripts/post-reels.sh ./reel.mp4 ./caption.txt
```

### 캐러셀 포스팅
```bash
bash scripts/post-carousel.sh <캡션파일> <이미지1> <이미지2> [이미지3...]

# 예시
bash scripts/post-carousel.sh ./caption.txt ./img1.jpg ./img2.jpg ./img3.jpg
```

### Threads 포스팅
```bash
bash scripts/post-threads.sh <캡션파일> [이미지URL]

# 예시 (텍스트만)
bash scripts/post-threads.sh ./caption.txt

# 예시 (이미지 포함)
bash scripts/post-threads.sh ./caption.txt "https://example.com/image.jpg"
```

---

## 파일 구조

```
instagram-api/
├── SKILL.md                    # 이 파일
└── scripts/
    ├── post-feed.sh            # 피드 포스팅
    ├── post-story.sh           # 스토리 포스팅
    ├── post-reels.sh           # 릴스 포스팅
    ├── post-carousel.sh        # 캐러셀 포스팅
    └── post-threads.sh         # Threads 포스팅
```

---

## 주의사항

- Instagram은 **공개 URL**로만 미디어 업로드 가능 (로컬 파일 직접 업로드 불가)
- 이 스킬은 Imgur를 통해 임시 공개 URL 생성
- 릴스 동영상 처리에는 수분 소요될 수 있음
- API 호출 실패 시 `~/logs/sns/` 로그 확인
