# Conversation mode (no localhost UI)

Goal: minimize user thinking. Agent drives browser automation end-to-end and only pauses for mandatory human checks (login/CAPTCHA/MFA/OAuth authorize).

UX rule: whenever the user must act, send a screenshot + ONE instruction line. No questions like “你现在在哪个页面？”。
Resilience rule: if browser automation fails (timeout/disconnect), **agent self-recovers and retries** (restart gateway/browser). Do not push routine clicking back to the user unless unavoidable.

## Flow

1) Agent opens https://discord.com/developers/applications (agent must do this; do NOT ask user to open it)
2) Agent creates new application (name auto-generated, must NOT contain "discord")
3) Agent navigates to Bot page, enables intents, saves
4) Agent triggers Reset Token (and clicks confirm)
   - If CAPTCHA/MFA/password prompt appears: user completes it
   - Agent reads the token from the page (never logs it)
   - If user must paste token in chat:
     - Agent replies immediately: “收到 token，开始写入 OpenClaw 配置并重启网关（约 10–30 秒）”。
     - After config write + restart, agent replies with: “网关已重启/已确认运行，下一步去授权邀请链接”。
5) Agent configures OAuth2 scopes + permissions and opens authorize URL (agent must open it via browser tool)
   - Note: “正在打开 Discord APP” is normal during the redirect
   - User selects server + clicks Authorize (only manual click in this step)
6) Agent writes OpenClaw config under a NEW accountId derived from **Discord API app name** (never overwrites existing bots)
   - Also ensures `channels.discord.enabled=true`
   - Sets group allowlist for that guild + user
   - Resilience: after `openclaw gateway restart`, always verify with `openclaw gateway status` (RPC probe ok) before proceeding.
7) User DMs bot "hi" to trigger pairing
   - If DM fails: user enables "Allow direct messages from server members" in that server’s Privacy Settings
8) Agent approves pairing for that account (must filter by `--account <accountId>` to avoid cross-bot mixing)

## Required user actions (only)
- Login to Discord developer portal
- Solve CAPTCHA / MFA
- Click OAuth Authorize
- If token cannot be read programmatically: paste token in chat
- DM the bot to trigger pairing

## Safety
- Never log token
- Never overwrite existing accounts; always use channels.discord.accounts.<accountId>
