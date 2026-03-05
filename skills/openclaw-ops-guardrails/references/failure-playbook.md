# Failure Playbook（OpenClaw 运维）

## 1) `approval timed out`

### 症状
- system message: `exec denied: approval timed out`

### 根因
- 目标 node 仍在审批模式；无可交互审批端导致超时。

### 处理
1. 查看目标审批配置：
   - `openclaw approvals get --node <id|name>`
2. 需要无审批放行时，设置：
   - `security=full, ask=off, askFallback=full`
3. 复测最小命令：
   - `echo check && whoami`

---

## 2) `pairing required`

### 症状
- `gateway closed (1008): pairing required`

### 根因
- 连接到错误 gateway（sshTarget/HostName 错）
- token 未带上或不匹配

### 处理
1. 校验 ssh 目标：`ssh openclaw-gateway 'hostname; whoami'`
2. 校验 remote URL 必须是隧道本地端：`<api-endpoint>`
3. 带凭据探测：
   - `openclaw gateway probe --ssh <ssh-target> --token <gateway-token>`
4. 必要时在 gateway 侧执行：
   - `openclaw devices approve --latest`

---

## 3) `system.run requires a companion app or node host`

### 症状
- node 命令报目标不支持 system.run

### 根因
- 该节点会话处于不完整能力状态（短时）或 node host 服务异常

### 处理
1. `openclaw nodes status` 检查 commands 是否含 `system.run`
2. 重连/重启 node host 服务
3. 用 nodeId 重试，不用 displayName

---

## 4) `Address already in use`（SSH tunnel 端口冲突）

### 症状
- `cannot listen to port: 18789`

### 根因
- 已存在 SSH tunnel 或本地 gateway 占用 18789

### 处理
1. `lsof -nP -iTCP:18789 -sTCP:LISTEN`
2. 复用已有 tunnel 或 kill 旧隧道 PID
3. 若需并存，改本地转发端口（如 28789）并同步 remote.url

---

## 5) 误导性“先成功后失败”系统提示

### 现象
- 用户看到成功输出后又收到失败提示

### 解释
- 多条历史请求的失败事件延迟投递，非当前命令失败。

### 规避
- 同一 node 串行执行，失败后重试 1 次
- 记录 run id/时间，向用户标注“历史残留事件”
