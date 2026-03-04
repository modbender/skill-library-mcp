# MCP Emotions Review (Backend + Frontend)

Date: 2026-02-03
Repo: /users/danielgomez/code/mcp_server/mcp_emotions

## Backend findings (from prior review)
1. [P0] Secrets committed in docker-compose.yml (DB URL + frontend API key).
2. [P0] Frontend API key committed in backend .env.
3. [P1] API key validation dependency not executed in /tools/emotion-detector.
4. [P1] API key usage logger likely fails (invalid async usage + insert on string table).

## Frontend findings (this review)
1. [P0] Frontend API key committed in frontend .env (client-exposed secret).
2. [P1] Frontend API key is used as a shared secret on all requests; because it ships to browsers, it cannot secure backend access. Consider moving to server-to-server authentication or using user JWT only.
3. [P2] JWT stored in localStorage (susceptible to XSS token theft). Consider HttpOnly cookies + CSRF protection.

## Notes
- The UI is polished and comprehensive; the app flow is coherent (detect -> results -> feedback -> history).
- Authentication UX is clean, but refresh token support is stubbed; login failures force a full sign-in.

