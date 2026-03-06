# Detection Rules Reference

完整的检测规则和正则表达式。

## 凭据检测规则

### API Keys

| Provider | Pattern | Example |
|----------|---------|---------|
| OpenAI | `sk-[a-zA-Z0-9]{20,}` | sk-abc123... |
| Anthropic | `sk-ant-[a-zA-Z0-9-]{20,}` | sk-ant-api03-... |
| AWS Access Key | `AKIA[0-9A-Z]{16}` | AKIAIOSFODNN7EXAMPLE |
| AWS Secret Key | `[a-zA-Z0-9/+]{40}` (in context) | wJalrXUtnFEMI/K7MDENG... |
| Google API | `AIza[0-9A-Za-z-_]{35}` | AIzaSyC... |
| GitHub Token | `gh[pousr]_[A-Za-z0-9_]{36,}` | ghp_xxxx... |
| Slack Token | `xox[baprs]-[0-9a-zA-Z-]+` | xoxb-... |
| Stripe | `sk_live_[0-9a-zA-Z]{24,}` | sk_live_... |
| Telegram Bot | `[0-9]{9,10}:[a-zA-Z0-9_-]{35}` | 123456789:ABC... |

### 密码模式

```regex
(?i)(password|passwd|pwd|secret|token|api_key|apikey|auth)\s*[=:]\s*['""]?[^'""'\s]{8,}
```

### 私钥检测

```regex
-----BEGIN (RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----
```

### Base64 编码的敏感数据

长度 > 50 的 Base64 字符串（可能是编码的凭据）：
```regex
[A-Za-z0-9+/]{50,}={0,2}
```

## 危险命令检测

### 删除命令

```regex
rm\s+(-[rf]+\s+)*(/|~|\$HOME|\$\{HOME\}|\.\./)
```

危险变体：
- `rm -rf /`
- `rm -rf ~`
- `rm -rf $HOME`
- `rm -rf ../`

### 提权命令

```regex
sudo\s+
```

### 动态执行

```regex
\beval\s*\(
\bexec\s*\(
source\s+<\(
```

### 远程执行

```regex
curl\s+.*\|\s*(ba)?sh
wget\s+.*\|\s*(ba)?sh
curl\s+.*-o\s+.*&&\s*(ba)?sh
```

## 网络外传检测

### HTTP 请求

```regex
(curl|wget|fetch|requests?\.(get|post|put)|http\.request|axios)\s*[(\s]+['""]?https?://
```

白名单域名（不触发警告）：
- api.openai.com
- api.anthropic.com
- api.github.com
- registry.npmjs.org
- pypi.org
- *.amazonaws.com

### WebSocket

```regex
(new\s+)?WebSocket\s*\(['""]?wss?://
```

### 文件上传

```regex
(upload|put|post).*file
multipart/form-data
```

## 文件越界检测

### 敏感目录访问

```regex
(~|/home/[^/]+|/root)/\.(ssh|gnupg|aws|config|netrc|npmrc|pypirc)
/etc/(passwd|shadow|sudoers|ssh)
```

### 系统路径写入

```regex
(>|>>|tee|write|save).*(/etc/|/usr/|/var/|/opt/)
```

## 依赖风险检测

### 未锁定版本 (Python)

```regex
^[a-zA-Z0-9_-]+$  # requirements.txt 中无版本号
```

### 未锁定版本 (Node)

```regex
"[^"]+"\s*:\s*"(\*|latest|>=|>|~|\^)"
```

## 严重程度分级

| Level | Description | Action |
|-------|-------------|--------|
| CRITICAL | 明确的凭据泄露 | 必须立即修复 |
| HIGH | 危险命令、远程代码执行 | 强烈建议修复 |
| MEDIUM | 潜在风险、需人工确认 | 建议审查 |
| LOW | 最佳实践建议 | 可选修复 |
