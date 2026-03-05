# SSH Batch Manager - Web UI 使用指南

## 🎨 可视化界面

SSH Batch Manager 现在提供 Web 可视化管理界面！

---

## 🚀 启动方式

### 方式 1：Systemd 服务（✅ 已配置）

**服务已安装，开机自动启动！**

```bash
# 查看状态
./manage-service.sh status

# 启动/停止/重启
./manage-service.sh start
./manage-service.sh stop
./manage-service.sh restart

# 查看日志
./manage-service.sh logs

# 禁用开机自启（可选）
./manage-service.sh disable
```

**访问地址**: http://localhost:8765（随时访问）

---

### 方式 2：手动启动（可选）

```bash
# 启动服务（自动打开浏览器）
python3 /home/subline/.openclaw/workspace/skills/ssh-batch-manager/serve-ui.py
```

**访问地址**: http://localhost:8765

**停止服务**: `Ctrl+C`

---

### 方式 2：直接打开 HTML 文件

```bash
# 使用脚本打开
/home/subline/.openclaw/workspace/skills/ssh-batch-manager/start-ui.sh

# 或直接在浏览器中打开
file:///home/subline/.openclaw/workspace/skills/ssh-batch-manager/ssh-manager.html
```

---

### 方式 3：通过 OpenClaw Browser 工具

```bash
# 启动 HTTP 服务器（后台）
nohup python3 /home/subline/.openclaw/workspace/skills/ssh-batch-manager/serve-ui.py &

# 使用 OpenClaw browser 工具访问
openclaw browser open http://localhost:8765
```

---

## 📋 功能说明

### 1️⃣ 快速操作

| 按钮 | 功能 |
|------|------|
| 🚀 Enable All | 向所有服务器分发公钥 |
| 🛑 Disable All | 从所有服务器删除公钥 |
| 📊 检查状态 | 检查 SSH 密钥、配置文件状态 |

---

### 2️⃣ 服务器列表管理

**查看服务器**：
- 显示所有已配置的服务器
- 显示用户名、主机、配置状态

**添加服务器**：
1. 点击"➕ 添加服务器"
2. 输入用户名、主机 IP、密码
3. 点击"✅ 保存"
4. 密码会自动加密后存储

**删除服务器**：
- 点击服务器行的"删除"按钮
- 确认后从配置中移除

**单台操作**：
- "启用"：向该服务器分发公钥
- "禁用"：从该服务器删除公钥

---

### 3️⃣ 加密工具

**加密单个密码**：
1. 在"加密单个密码"区域输入密码
2. 点击"加密"
3. 复制加密结果到配置文件

**加密配置文件**：
- 将明文配置文件加密为 `.enc` 格式

---

### 4️⃣ 操作日志

- 实时显示所有操作记录
- 成功/错误/警告用不同颜色标识
- 可点击"清空日志"清除记录

---

## 🎨 界面预览

```
┌─────────────────────────────────────────────────┐
│  🔑 SSH Batch Manager                           │
│  批量管理 SSH 免密登录授权                        │
├─────────────────────────────────────────────────┤
│  ⚡ 快速操作                                     │
│  [🚀 Enable All] [🛑 Disable All] [📊 状态]    │
├─────────────────────────────────────────────────┤
│  🖥️ 服务器列表                                   │
│  ┌─────────────────────────────────────────┐   │
│  │ 服务器 │ 用户 │ 主机 │ 状态 │ 操作 │   │
│  ├─────────────────────────────────────────┤   │
│  │ root@10.0.0.2 │ root │ 10.0.0.2 │ ✅ │...│   │
│  └─────────────────────────────────────────┘   │
│                            [➕ 添加服务器]      │
├─────────────────────────────────────────────────┤
│  🔐 加密工具                                     │
│  [加密单个密码] [加密配置文件]                   │
├─────────────────────────────────────────────────┤
│  📋 操作日志                                     │
│  [12:00:00] ℹ️ 系统就绪...                      │
│  [12:00:05] ✅ 加载了 3 台服务器                 │
│  [12:01:00] 🚀 开始启用所有服务器...             │
└─────────────────────────────────────────────────┘
```

---

## 💡 使用场景

### 场景 1：新服务器上线

1. 打开 Web UI
2. 点击"添加服务器"
3. 输入服务器信息
4. 保存后点击"启用"

### 场景 2：批量授权

1. 在配置文件中添加多台服务器
2. 点击"Enable All"
3. 等待进度条完成
4. 查看日志确认结果

### 场景 3：员工离职

1. 找到该员工的服务器
2. 点击"禁用"
3. 或删除服务器配置

---

## 🔧 技术细节

### 架构

```
┌──────────────┐
│  Web Browser │
│   (HTML/JS)  │
└──────┬───────┘
       │
       │ JavaScript 调用
       │
┌──────▼───────┐
│ openclawExec │ (自定义桥接)
└──────┬───────┘
       │
       │ 执行系统命令
       │
┌──────▼───────┐
│ssh-batch-man│
│    .py       │
└──────────────┘
```

### 安全特性

- ✅ 密码 AES-256 加密存储
- ✅ 文件权限自动设置 600
- ✅ 本地运行，不联网
- ✅ 无后端服务，纯前端

---

## 🐛 故障排查

### 问题 1：页面无法打开

**解决**：
```bash
# 检查文件是否存在
ls -la /home/subline/.openclaw/workspace/skills/ssh-batch-manager/ssh-manager.html

# 重新启动服务
pkill -f serve-ui.py
python3 serve-ui.py
```

### 问题 2：操作无响应

**可能原因**：
- SSH 连接超时
- 密码错误
- 网络不通

**解决**：
- 查看日志区域的错误信息
- 检查服务器网络连接
- 验证密码是否正确

### 问题 3：配置加载失败

**解决**：
```bash
# 检查配置文件
cat ~/.openclaw/credentials/ssh-batch.conf

# 检查密钥文件
cat ~/.openclaw/credentials/ssh-batch.key
```

---

## 📝 配置文件格式

```
# ~/.openclaw/credentials/ssh-batch.conf

# 格式：user@host=encrypted_password
root@10.0.0.2=AES256:Z0FBQUFB...
user1@10.8.8.1=AES256:YWJjZGVm...
admin@192.168.1.100=AES256:MTIzNDU2...
```

---

## 🎯 下一步优化

- [ ] 支持批量导入服务器
- [ ] 添加服务器分组功能
- [ ] 支持测试连接
- [ ] 添加执行历史记录
- [ ] 支持自定义 SSH 端口

---

*最后更新：2026-03-03*
