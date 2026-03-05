# LinkedIn API Setup

## 1. Create a LinkedIn App
1. Go to https://www.linkedin.com/developers/apps
2. Click "Create app"
3. Fill in app name, LinkedIn Page, logo
4. Under Products, request "Share on LinkedIn" and "Sign In with LinkedIn using OpenID Connect"

## 2. Get OAuth 2.0 Credentials
- Note your **Client ID** and **Client Secret** from the Auth tab
- Add redirect URL: `http://localhost:3000/callback` (or your domain)

## 3. Generate Access Token
Request authorization:
```
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT&scope=openid%20profile%20w_member_social
```

Exchange code for token:
```bash
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -d "grant_type=authorization_code&code=AUTH_CODE&redirect_uri=YOUR_REDIRECT&client_id=YOUR_CLIENT_ID&client_secret=YOUR_SECRET"
```

## 4. Set Environment Variable
```bash
export LINKEDIN_ACCESS_TOKEN="your_token_here"
export LINKEDIN_PERSON_ID="your_person_urn_id"  # from /v2/userinfo endpoint
```

**Token expires in 60 days.** Set a reminder to refresh.
