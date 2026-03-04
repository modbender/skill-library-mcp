# Security & Privacy Guide

## 安全改进 (v1.0.4)

### 🔒 关键安全修复

#### 1. 隔离凭证存储 (Isolated Credential Storage)
**v1.0.3 问题**: API Key 存储在 `~/.openclaw/.env` (共享文件)  
**v1.0.4 修复**: 仅使用 `~/.cuecue/.env.secure` (技能隔离)

```
Before: ~/.openclaw/.env          (shared with all skills) ❌
After:  ~/.cuecue/.env.secure     (isolated storage) ✅
```

#### 2. 文件权限控制
- 目录权限: `700` (仅所有者可访问)
- 文件权限: `600` (仅所有者可读写)
- 自动设置，无需手动配置

#### 3. 无系统级修改
- ❌ 不修改系统 crontab
- ❌ 不写入共享配置文件
- ❌ 不需要 root 权限
- ✅ 使用 node-cron 内部调度
- ✅ 用户级安装路径

---

## 数据流说明

### 外部数据传输

| 端点 | 用途 | 发送数据 | 必要性 |
|------|------|---------|--------|
| `https://cuecue.cn` | 深度研究 | 研究主题、chat_id | 必需 |
| `https://api.tavily.com` | 新闻搜索 | 搜索查询 | 可选 |

### 本地数据存储

```
~/.cuecue/
├── .env.secure          # API Keys (权限 600)
├── users/
│   └── {chat_id}/
│       ├── tasks/       # 研究任务
│       ├── monitors/    # 监控配置
│       └── state.json   # 用户状态
└── logs/
    ├── cue-YYYY-MM-DD.log
    ├── error-YYYYMM.log
    └── info-YYYYMM.log
```

---

## 权限清单

### 声明的权限
✅ 创建 `~/.cuecue` 目录存储用户数据  
✅ 写入 `~/.cuecue/.env.secure` 存储 API Key  
✅ 运行内部定时任务 (node-cron)  
✅ 调用外部 API (cuecue.cn, tavily.com)

### 不请求的权限
❌ 修改系统 crontab  
❌ 写入 `/usr/lib/node_modules`  
❌ 修改 `~/.openclaw/.env`  
❌ 需要 root/sudo  
❌ 访问其他技能数据

---

## 安装与卸载

### 安装
```bash
# 用户级安装 (推荐)
clawhub install cue

# 或手动安装到用户目录
git clone ... ~/.openclaw/skills/cue
cd ~/.openclaw/skills/cue && npm install
```

### 卸载
```bash
# 完全清理
rm -rf ~/.cuecue                    # 删除所有数据
rm -rf ~/.openclaw/skills/cue       # 删除技能

# 验证清理
ls -la ~/.cuecue 2>/dev/null && echo "清理失败" || echo "清理完成"
```

---

## 安全验证

### 验证文件权限
```bash
# 检查目录权限
stat -c "%a %n" ~/.cuecue
# 期望输出: 700 /home/user/.cuecue

# 检查凭证文件权限
stat -c "%a %n" ~/.cuecue/.env.secure
# 期望输出: 600 /home/user/.cuecue/.env.secure
```

### 验证隔离性
```bash
# 确认不写入共享配置
grep -r "CUECUE_API_KEY" ~/.openclaw/.env 2>/dev/null && echo "❌ 发现共享配置" || echo "✅ 隔离正确"
```

---

## 最小权限建议

### API Key 最佳实践
1. **使用测试密钥**: 初次安装使用测试环境的 API Key
2. **限制密钥权限**: 为 CueCue 创建专用的只读 API Key
3. **定期轮换**: 每 90 天更换一次 API Key

### 网络隔离
```bash
# 可选：使用防火墙限制出站连接
# 仅允许访问必需端点
ufw allow out to cuecue.cn port 443
ufw allow out to api.tavily.com port 443
```

---

## 审计日志

所有安全相关操作都会记录：
- API Key 保存/更新
- 文件权限变更
- 监控任务执行
- 外部 API 调用

日志位置: `~/.cuecue/logs/`

---

## 报告安全问题

如发现安全漏洞，请：
1. 不要公开披露
2. 发送邮件至: security@example.com
3. 提供复现步骤和影响评估

---

## 版本历史

- **v1.0.4**: 修复共享文件写入问题，实现完全隔离存储
- **v1.0.3**: 基础版本，使用共享配置文件
