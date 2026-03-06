# skill-trust-guard 测试报告

时间：2026-02-19（Asia/Shanghai）  
环境：WSL2 Linux, bash, OpenClaw 2026.2.6-3

## 1) 基础功能验证

### 用例 A：安全 skill（本地已安装 skill）
命令：
```bash
install.sh --yes ~/.openclaw/skills/coding-agent --dir /tmp/skills-safe-test
```
结果：**通过**
- SCORE=100
- DECISION=allow
- 成功复制到 `/tmp/skills-safe-test/coding-agent`

### 用例 B：中风险 skill（告警区间）
样本：`/tmp/warn-skill3`（包含 command exec + unknown domain + env access）

命令：
```bash
install.sh --yes /tmp/warn-skill3 --dir /tmp/skills-safe-test
```
结果：**通过（告警后放行）**
- SCORE=55
- DECISION=warn
- `--yes` 自动继续安装

### 用例 C：恶意 skill（拦截）
样本：`/tmp/malicious-skill`（读取 `~/.clawdbot/.env` + 外发到恶意域）

命令：
```bash
install.sh /tmp/malicious-skill --dir /tmp/skills-safe-test
```
结果：**拦截成功**
- SCORE=5
- DECISION=reject
- 安装被阻断，打印完整 JSON 扫描报告

## 2) 无缝集成验证（PATH shim）

命令：
```bash
integrate.sh
export PATH="$HOME/.openclaw/bin:$PATH"
clawhub install /tmp/malicious-skill --dir /tmp/skills-safe-test
```
结果：**拦截成功**（说明 shim 已接管 `clawhub install`）

## 3) 目标技能测试（architect / neo4j）

尝试命令：
```bash
install.sh --yes --dir /tmp/skills-safe-test architect
install.sh --yes --dir /tmp/skills-safe-test neo4j
```
结果：**未完成（外部限制）**
- clawhub 返回 `Rate limit exceeded`
- guard 正确终止并提示日志 `/tmp/skill-trust-guard.install.log`

> 结论：本地策略与拦截流程可用；线上 slug 安装验证受 registry 限流影响，待限流恢复后可重跑。

## 4) 结论

- 方案 B（wrapper）已可用并完成
- 提供了可复用 pre-install hook 脚本，便于未来迁移到原生 hook
- WSL/Linux 下功能正常，错误处理和输出可读性满足要求
