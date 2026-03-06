# 发布到 ClawHub（Upload 要求对照）

根据 `clawhub.ai`/ClawHub v1 规范，上传前检查：

1. **必须包含 `SKILL.md`**
   - 含 YAML frontmatter
   - 至少包含：`name`、`description`

2. **每次上传是一个新版本**
   - `version` 必须唯一（不能和历史版本重复）

3. **changelog 必填**
   - 建议写清新增/修复/破坏性变更

4. **单版本总大小 ≤ 50MB**
   - 本 skill 为纯文本脚本，远低于限制

5. **文本文件为主**
   - 该 skill 仅包含 `SKILL.md` + `scripts/` + `references/`

6. **需要 GitHub 登录上传**
   - 账号龄通常需 ≥ 7 天（平台风控规则）

## 本 skill 建议发布信息

- slug/name: `openclaw-phone-receipt`
- summary: 失败/紧急任务自动电话回执，普通成功仅 Telegram 文本
- tags: `openclaw`, `automation`, `phone`, `twilio`, `elevenlabs`, `telegram`

## changelog 模板（可直接粘贴）

- Added fixed toggle commands: `电话回执=开/关`
- Added failure/urgent-only phone strategy
- Added standalone outbound call script (`scripts/trigger_call.sh`)
- Added full setup/troubleshooting guide for Twilio + ElevenLabs
