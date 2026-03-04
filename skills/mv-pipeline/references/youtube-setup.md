# YouTube Setup

YouTube Data API v3 のセットアップ手順。

## 1. GCP プロジェクト

既存: `gen-lang-client-0383477693` (nanobanana)

### API 有効化
- YouTube Data API v3 を有効化（Cloud Console → APIs → Enable）

### OAuth 2.0 認証情報
1. Cloud Console → Credentials → Create → OAuth client ID
2. Application type: Desktop application
3. JSON をダウンロード → `~/.clawd-youtube/credentials.json` に保存

### API Key
1. Credentials → Create → API Key
2. コピー → `~/.clawd-youtube/config.env` に記入

## 2. 環境設定

```bash
mkdir -p ~/.clawd-youtube
```

`~/.clawd-youtube/config.env`:
```
YOUTUBE_API_KEY=your_key
YOUTUBE_CLIENT_ID=your_id.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=your_secret
YOUTUBE_REDIRECT_URI=http://localhost:8888/oauth2callback
YOUTUBE_CHANNEL_ID=UCwRKII0cuPtXiHhGLMHlO5A
YOUTUBE_CHANNEL_NAME=AutomaticBliss
```

## 3. 初回認証

```bash
cd skills/youtube-studio
node scripts/youtube-studio.js auth
```

ブラウザが開く → Google アカウントでログイン → トークンが `~/.clawd-youtube/tokens.json` に保存。

以降はリフレッシュトークンで自動認証。

## 4. 依存関係

```bash
cd skills/youtube-studio
npm install
```

googleapis, google-auth-library, axios, express が必要。

## Channel Info

- **Channel**: [Automatic Bliss](https://www.youtube.com/channel/UCwRKII0cuPtXiHhGLMHlO5A)
- **ID**: UCwRKII0cuPtXiHhGLMHlO5A
