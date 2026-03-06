---
name: ticktick-official-cli
description: 使用官方 Dida365 OAuth 与 Open API 管理滴答清单（项目/任务查询、创建、更新、完成、删除）。当用户要求安全地直连 dida365.com（不经过第三方 OAuth 中转）时使用。
---

在本技能目录执行命令。

## Onboarding（最少手动步骤）

1. 在 Dida365 开发者中心创建应用：`https://developer.dida365.com/manage`
2. 在应用里配置回调地址：`http://127.0.0.1:8765/callback`
3. 一次性保存应用配置：

```bash
./scripts/ticktick_oauth.py setup \
  --client-id "<client_id>" \
  --client-secret "<client_secret>" \
  --redirect-uri "http://127.0.0.1:8765/callback"
```

4. 一键登录（自动打开浏览器授权、自动换 token、自动保存 token）：

```bash
./scripts/ticktick_oauth.py login
```

5. 验证：

```bash
./scripts/ticktick_cli.py doctor
./scripts/ticktick_cli.py --json project list
```

> token 会自动保存到 `~/.config/ticktick-official/token.env`，后续一般不需要再手动 `export`。

## 备用流程（手动）

```bash
./scripts/ticktick_oauth.py auth-url --client-id "$TICKTICK_CLIENT_ID" --redirect-uri "$TICKTICK_REDIRECT_URI"
./scripts/ticktick_oauth.py exchange --code "<code>"
```

## 常用命令

```bash
# 项目
./scripts/ticktick_cli.py --json project list
./scripts/ticktick_cli.py --json project create --name "收件箱"

# 任务
./scripts/ticktick_cli.py --json task create --project-id <pid> --title "测试任务"
./scripts/ticktick_cli.py --json task complete --project-id <pid> --task-id <tid>
```

## 说明

- 始终优先使用官方域名：`dida365.com` / `api.dida365.com`
- 删除操作（project/task delete）属于危险操作，执行前确认
- 参数与字段细节见 `references/dida365-openapi.md`
