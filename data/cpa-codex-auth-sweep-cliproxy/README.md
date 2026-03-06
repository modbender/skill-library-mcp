# cpa-codex-auth-sweep-cliproxy

基于 CLI Proxy Management API 的 Codex 授权巡检/清理技能。

## 功能

- 从管理端读取认证文件（`/v0/management/auth-files`）
- 通过管理端 `api-call` + `auth_index` + `$TOKEN$` 探测每个授权
- 统计：
  - 总数
  - 失效（401）
  - 周限额为 0（weekly quota）
  - 状态码分布
- 可选：自动删除 401 对应认证文件

## 安全说明（重要）

`api-call` 模式会让管理端将真实 token 带到 `probe-url` 指向的目标。
因此本脚本默认启用以下保护：

- 仅允许 `https` probe URL
- 默认仅允许 host=`chatgpt.com`
- 非白名单 host 需显式 `--allow-unsafe-probe-host`（高风险）
- `--insecure` 需要二次确认 `--allow-insecure-tls`（高风险）

### 凭据声明

- **Primary credential**：`CLIPROXY_MANAGEMENT_KEY`
- **Required endpoint config**：`CLIPROXY_BASE_URL`
- 以上两项为执行必需输入

## 目录结构

```text
cpa-codex-auth-sweep-cliproxy/
├── SKILL.md
├── README.md
└── scripts/
    └── cliproxy_scanner.py
```

## 使用方式

### 1) 仅扫描

```bash
python3 scripts/cliproxy_scanner.py \
  --base-url "https://your-cliproxy.example.com" \
  --management-key "YOUR_MANAGEMENT_KEY" \
  --workers 120 \
  --output-json
```

### 2) 扫描并删除 401

```bash
python3 scripts/cliproxy_scanner.py \
  --base-url "https://your-cliproxy.example.com" \
  --management-key "YOUR_MANAGEMENT_KEY" \
  --workers 120 \
  --delete-401 --yes \
  --output-json
```

### 3) 自签证书环境

```bash
python3 scripts/cliproxy_scanner.py ... --insecure
```

## 关键参数

- `--base-url`：CLI Proxy 管理端地址（必填）
- `--management-key`：管理密钥（必填）
- `--workers`：并发数（默认 80）
- `--delete-401 --yes`：启用并确认删除 401
- `--insecure`：关闭 TLS 校验（仅内网调试建议）
- `--allowed-probe-hosts`：probe host 白名单（默认 `chatgpt.com`）
- `--allow-unsafe-probe-host`：允许使用非白名单 probe host（危险）

## 输出说明

`summary` 主要字段：

- `total`：参与探测的总数
- `unauthorized_401`：判定失效数量
- `weekly_quota_zero`：周限额为 0 数量
- `ok`：2xx 数量
- `errors`：请求失败数量
- `management_quota_exhausted`：管理端状态视角 quota exhausted 数量
- `status_code_buckets`：状态码分布

## 安全声明

> 本技能使用 CLI Proxy Management API 的 `api-call` 机制对授权做探测。该机制会将真实 token 按 `probe-url` 转发到目标主机。为降低风险：
> 1) 默认仅允许 `https://chatgpt.com`；
> 2) 非白名单主机必须显式危险确认；
> 3) 禁止默认关闭 TLS 校验，`--insecure` 需二次确认；
> 4) 执行前必须提供并确认 `CLIPROXY_BASE_URL` 与 `CLIPROXY_MANAGEMENT_KEY`。
