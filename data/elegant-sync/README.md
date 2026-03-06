# Elegant Sync

优雅安全的 OpenClaw 配置同步工具

## 安装

```bash
# 复制到 skills 目录
cp -r elegant-sync ~/.openclaw/skills/
```

## 配置

```bash
# 创建配置文件
cat > ~/.openclaw/.backup.env << EOF
BACKUP_REPO=https://github.com/你的用户名/openclaw-backup
BACKUP_TOKEN=ghp_你的token
EOF
```

## 使用

```bash
# 同步
node index.js sync

# 预览
node index.js sync --dry-run

# 只同步 memory
node index.js sync memory

# 只同步 skills
node index.js sync skills

# 状态
node index.js status
```

## 安全特性

- 不上传 .env 和 openclaw.json
- URL 验证
- Token 不出现在错误信息中
- 本地备份后再恢复
