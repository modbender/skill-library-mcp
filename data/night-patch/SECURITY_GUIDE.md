# NightPatch Skill 安全使用指南

## 🛡️ 安全概述

NightPatch 技能设计遵循「安全第一」原则，所有自动化操作都在安全边界内进行。本指南帮助用户安全地安装和使用技能。

## 🔍 安全特性

### 内置安全机制
1. **多层安全检查**：环境检测、风险分级、回滚验证
2. **可回滚设计**：所有操作都有撤销方案
3. **生产保护**：自动识别并跳过生产环境
4. **资源限制**：控制CPU、内存、磁盘使用
5. **透明审计**：完整记录所有操作日志

### 文件访问边界
技能会访问以下文件，但**不会修改系统文件**：
- `~/.bash_history` - 只读，用于分析命令使用频率
- `~/.bashrc` - 读写，仅添加新别名到.bashrc文件
  *注意：选择.bashrc而非.bash_aliases是为了更好的shell兼容性*
- 工作区文件 - 只读扫描，仅在用户确认后移动
- 日志文件 - 只读分析，仅删除过期的旧日志

## 🚀 安全安装步骤

### 推荐安装流程
```bash
# 1. 从可信源下载
# 仅从 ClawHub 官方页面下载：https://clawhub.ai/teachers10086/night-patch

# 2. 在测试环境验证
mkdir -p /tmp/test-nightpatch
tar -xzf night-patch-release.tar.gz -C /tmp/test-nightpatch
cd /tmp/test-nightpatch/night-patch

# 3. 运行干模式测试
./start.sh dry-run

# 4. 检查报告和日志
cat logs/night-patch-audit.log
```

### 生产环境安装
```bash
# 1. 备份重要文件
cp ~/.bash_aliases ~/.bash_aliases.backup
cp -r ~/workspace ~/workspace.backup

# 2. 安装技能
tar -xzf night-patch-release.tar.gz -C ~/.openclaw/workspace/skills/
cd ~/.openclaw/workspace/skills/night-patch
npm install

# 3. 首次运行使用干模式
./start.sh dry-run

# 4. 检查检测结果
./start.sh report

# 5. 确认无误后启用自动运行
# 谨慎使用：./setup-cron.sh
```

## ⚠️ 风险缓解措施

### 文件访问风险
**风险**：技能会读取用户文件
**缓解**：
- 使用干模式先检查会访问哪些文件
- 配置检测器只扫描特定目录
- 定期审查审计日志

### Cron安装风险
**风险**：自动创建定时任务
**缓解**：
- 先手动运行验证效果
- 审查生成的cron脚本
- 仅在信任后启用定时运行

### 代码执行风险
**风险**：执行Shell命令
**缓解**：
- 所有命令都有回滚方案
- 执行前进行安全检查
- 记录完整执行日志

## 🔧 安全配置建议

### 最小权限配置
编辑 `config/default.yaml`：
```yaml
safety:
  max_changes_per_night: 1      # 每晚最多1个改动
  require_rollback: true        # 必须可回滚
  skip_production: true         # 跳过生产环境
  dry_run_first: true           # 首次运行只检测

detectors:
  shell_alias:
    enabled: true
    command_history_file: "~/.bash_history"  # 可改为测试文件
  note_organization:
    enabled: false              # 初始禁用文件移动
  log_optimization:
    enabled: false              # 初始禁用日志删除
```

### 测试环境配置
```bash
# 创建测试工作区
mkdir -p ~/test-workspace
cd ~/test-workspace

# 复制配置文件
cp ~/.openclaw/workspace/skills/night-patch/config/default.yaml \
   ~/test-workspace/nightpatch-config.yaml

# 修改配置指向测试目录
sed -i 's|~/.bash_history|~/test-workspace/bash_history|g' \
   ~/test-workspace/nightpatch-config.yaml
```

## 📊 安全监控

### 定期检查项目
1. **审计日志**：`logs/night-patch-audit.log`
2. **执行历史**：`logs/night-patch-execution-history.json`
3. **资源使用**：检查CPU、内存、磁盘使用
4. **文件变更**：对比备份文件

### 监控命令
```bash
# 查看最近的安全检查
tail -f logs/night-patch-audit.log

# 检查执行历史
cat logs/night-patch-execution-history.json | jq '.'

# 监控资源使用
ps aux | grep night-patch
```

## 🆘 应急响应

### 发现问题时
1. **立即停止**：
   ```bash
   # 停止cron任务
   crontab -l | grep -v night-patch | crontab -
   
   # 停止运行中的进程
   pkill -f night-patch
   ```

2. **回滚操作**：
   ```bash
   # 使用报告中的回滚指令
   # 检查最新报告获取回滚命令
   ./start.sh report | grep "回滚指令"
   ```

3. **恢复备份**：
   ```bash
   cp ~/.bash_aliases.backup ~/.bash_aliases
   cp -r ~/workspace.backup/* ~/workspace/
   ```

### 报告问题
1. 在虾聊社区发帖：https://xialiao.ai/u/1239
2. 提供审计日志和错误信息
3. 描述复现步骤

## 🔐 高级安全措施

### 容器化运行（推荐）
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY night-patch-release.tar.gz .
RUN tar -xzf night-patch-release.tar.gz && \
    cd night-patch && \
    npm install
WORKDIR /app/night-patch
CMD ["./start.sh", "dry-run"]
```

### 沙箱环境
```bash
# 使用Firejail运行
firejail --private=. --net=none ./start.sh run

# 或使用Bubblewrap
bwrap --ro-bind /usr /usr \
      --bind ~/test-workspace ~/workspace \
      ./start.sh dry-run
```

## 📚 安全最佳实践

### 安装前
1. 验证下载源（仅信任ClawHub）
2. 检查文件哈希（如果提供）
3. 在隔离环境测试

### 使用中
1. 始终先运行干模式
2. 定期审查审计日志
3. 保持备份习惯
4. 及时更新技能版本

### 问题处理
1. 立即停止可疑操作
2. 使用回滚指令恢复
3. 报告问题给开发者
4. 分享经验给社区

## 🤝 社区支持

### 安全讨论
- 虾聊社区：https://xialiao.ai/u/1239
- 问题反馈：在技能页面留言
- 安全建议：欢迎贡献改进

### 更新通知
- 关注ClawHub页面更新
- 订阅安全公告
- 定期检查新版本

---
*安全是自动化的基石，谨慎使用，快乐修补！* 🛡️

**记住**：自动化工具是助手，不是主人。始终保持控制权，定期验证行为，享受安全便捷的夜间修补体验。