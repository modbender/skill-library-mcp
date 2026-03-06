# 📦 Skill 发布记录

## SSH Batch Manager v2.0

**发布时间**: 2026-03-03  
**仓库**: https://gitee.com/subline/onepeace.git  
**目录**: `src/skills/ssh-batch-manager/`  
**分支**: `develop`

---

### 📋 发布文件

| 文件 | 说明 | 大小 |
|------|------|------|
| `SKILL.md` | Skill 元数据说明 | 2.7KB |
| `README.md` | 使用指南 | 5.3KB |
| `UPGRADE-v2.md` | v2.0 升级指南 | 5.0KB |
| `_meta.json` | 元数据 | 546B |
| `ssh-batch-manager.py` | 核心脚本 | 26.7KB |
| `ssh-manager.html` | Web UI 界面 | 37KB |
| `serve-ui.py` | HTTP 服务器 | 1.2KB |
| `ssh-batch.json.template` | 配置模板 | 608B |

**总计**: 8 个文件，2544 行代码

---

### 🎯 核心功能

1. **批量 SSH 管理**
   - Enable/Disable All 一键操作
   - 单台服务器独立管理
   - 支持自定义 SSH 端口

2. **双认证模式**
   - 密码登录（sshpass + 密码）
   - 证书登录（sshpass + 私钥密码）
   - 混合模式支持

3. **Web 可视化管理**
   - 服务器列表管理
   - 公钥读取/复制/下载
   - 实时操作日志
   - 进度条显示

4. **安全特性**
   - AES-256 加密存储密码
   - ed25519 密钥支持
   - Ubuntu 24.04 + Alpine 3.21+ 兼容
   - Systemd 开机自启

---

### 🚀 安装方式

```bash
# 1. 克隆仓库
git clone https://gitee.com/subline/onepeace.git
cd onepeace/src/skills/ssh-batch-manager

# 2. 安装依赖
sudo apt install python3-cryptography sshpass

# 3. 生成加密密钥
python3 ssh-batch-manager.py generate-key

# 4. 创建配置
python3 ssh-batch-manager.py create-config

# 5. 生成 SSH 密钥
python3 ssh-batch-manager.py generate-ed25519

# 6. 启动 Web UI 服务
python3 serve-ui.py &

# 访问 http://localhost:8765
```

---

### 📖 使用文档

- **快速开始**: `README.md`
- **升级到 v2.0**: `UPGRADE-v2.md`
- **Skill 说明**: `SKILL.md`

---

### 🔧 配置示例

```json
{
  "version": "2.0",
  "auth_method": "password",
  "servers": [
    {
      "user": "root",
      "host": "10.0.0.2",
      "port": 22,
      "auth": "password",
      "password": "AES256:加密后的密码"
    },
    {
      "user": "deploy",
      "host": "10.8.8.1",
      "port": 22,
      "auth": "key"
    }
  ]
}
```

---

### 📊 Git 提交记录

**Commit**: `73d21d6`  
**分支**: `develop`  
**信息**: feat: Add SSH Batch Manager skill

```
feat: Add SSH Batch Manager skill

- Support password and key-based authentication
- JSON configuration format (v2.0)
- Web UI for visual management
- Auto-start systemd service
- AES-256 encryption for passwords
- ed25519 key support for Ubuntu/Alpine compatibility
```

---

### 🎉 发布清单

- [x] 复制关键文件到仓库
- [x] 设置文件权限
- [x] Git 提交
- [x] 推送到 Gitee
- [x] 创建发布记录
- [x] 验证访问

---

### 📝 后续计划

1. **Web UI 增强**
   - [ ] 批量导入服务器
   - [ ] 服务器分组功能
   - [ ] 连接测试功能

2. **功能扩展**
   - [ ] 支持 SSH 代理跳转
   - [ ] 支持多私钥管理
   - [ ] 支持证书过期提醒

3. **文档完善**
   - [ ] 视频教程
   - [ ] 故障排查手册
   - [ ] 最佳实践指南

---

*最后更新：2026-03-03*
