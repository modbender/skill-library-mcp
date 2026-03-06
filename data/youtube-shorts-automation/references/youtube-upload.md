# YouTube Shorts 업로드

## 사전 요구사항
- Google Cloud Console에서 OAuth 클라이언트 생성 (YouTube Data API v3 활성화)
- `client_secret.json` 다운로드
- 첫 실행 시 브라우저 OAuth 인증 → `token.json` 생성됨
- Python 패키지: `google-api-python-client`, `google-auth-oauthlib`

## 업로드 스크립트 사용법
```bash
python3 scripts/youtube_upload.py \
  --file video.mp4 \
  --title "제목 #shorts" \
  --description "설명" \
  --tags "tag1,tag2"
```

## Shorts 조건
- 60초 이하
- 9:16 세로 비율
- 제목 또는 태그에 `#shorts` 포함

## 주의사항
- `token.json` 만료 시 자동 갱신 (refresh_token 있으면)
- 업로드 후 반환값: video_id → `https://youtube.com/shorts/{video_id}`
- 기본 공개(public) 설정, `--privacy` 옵션으로 변경 가능
