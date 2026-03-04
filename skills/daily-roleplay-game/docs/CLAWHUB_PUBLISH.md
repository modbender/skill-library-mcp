# ClawHub 发布说明与超时排查

## 发布命令

```bash
clawhub login --token <你的token>
clawhub publish . --slug daily-roleplay-game --name "Daily Roleplay Game" --version 1.0.0 --tags latest
```

## 若出现 Timeout

### 原因

ClawHub CLI 将所有 HTTP 请求的超时时间**硬编码为 15 秒**（约 0.7.0）：

- 位置：`clawhub` 包内 `dist/http.js`
- 路径示例：`/opt/homebrew/lib/node_modules/clawhub/dist/http.js`
- 代码：`const REQUEST_TIMEOUT_MS = 15_000;`
- `publish` 会将整个 skill 打成一个 multipart POST 发往 `/api/v1/skills`，该请求也受这 15 秒限制

本仓库约 3.6MB、100+ 文件，在较慢网络或服务端处理较慢时，单次上传容易超过 15 秒，从而触发超时。

### 可行方案

1. **改善网络**：在延迟较低的环境下重试（例如使用代理/VPN 或网络空闲时）。
2. **本地临时加大超时**（仅当你能改全局安装的包时）：
   - 编辑 `$(npm root -g)/clawhub/dist/http.js`
   - 将 `const REQUEST_TIMEOUT_MS = 15_000;` 改为更大值（如 `120_000`）
   - 保存后再次执行 `clawhub publish ...`
3. **向 ClawHub 反馈**：建议为 publish 或大请求提供更长超时或可配置超时（例如环境变量）。

## 发布前检查

- 已执行 `clawhub login` 且显示 OK
- 当前目录为项目根目录（含 `SKILL.md`、`engine/`、`scripts/setup.sh`）
- `SKILL.md` 含 `name` 与 `description` frontmatter
