# WebDAV 备份配置指南

## 支持的 WebDAV 服务配置

### 1. 坚果云 (推荐)

```bash
export WEBDAV_URL="https://dav.jianguoyun.com/dav/"
export WEBDAV_USERNAME="你的坚果云邮箱"
export WEBDAV_PASSWORD="你的坚果云应用密码"
```

**注意**: 必须使用"应用密码"，不是登录密码。
在坚果云网页版 → 安全选项 → 添加应用密码

### 2. Nextcloud

```bash
export WEBDAV_URL="https://your-nextcloud.com/remote.php/dav/files/username/"
export WEBDAV_USERNAME="username"
export WEBDAV_PASSWORD="password"
```

### 3. ownCloud

```bash
export WEBDAV_URL="https://your-owncloud.com/remote.php/webdav/"
export WEBDAV_USERNAME="username"
export WEBDAV_PASSWORD="password"
```

### 4. 阿里云盘（通过 WebDAV 插件）

需要先部署 aliyundrive-webdav：
```bash
export WEBDAV_URL="http://localhost:8080/"
export WEBDAV_USERNAME="admin"
export WEBDAV_PASSWORD="your-token"
```

## 持久化配置

将环境变量添加到 `~/.bashrc` 或 `~/.zshrc`：

```bash
echo 'export WEBDAV_URL="https://dav.jianguoyun.com/dav/"' >> ~/.bashrc
echo 'export WEBDAV_USERNAME="your-email"' >> ~/.bashrc
echo 'export WEBDAV_PASSWORD="your-password"' >> ~/.bashrc
source ~/.bashrc
```

## 测试连接

```bash
# 测试 WebDAV 连接
curl -u $WEBDAV_USERNAME:$WEBDAV_PASSWORD -X PROPFIND $WEBDAV_URL
```

## 备份策略建议

### 每日自动备份
```bash
# 添加到 crontab
crontab -e
# 添加行（根据实际路径调整）：
0 2 * * * /usr/bin/python3 ~/.openclaw/workspace/skills/openclaw-webdav-backup/scripts/backup.py >> /tmp/webdav-backup.log 2>&1
```

### 保留策略
- 本地保留最近7天备份
- WebDAV 保留最近30天备份
- 每月1日保留月备份

## 故障排除

### 1. 上传失败 "401 Unauthorized"
- 检查用户名和密码
- 坚果云用户确认使用的是"应用密码"

### 2. 上传失败 "403 Forbidden"
- 检查 WebDAV 目录是否有写入权限
- 确认 URL 路径正确

### 3. SSL 证书错误
```bash
# 临时忽略证书验证（不推荐用于生产）
export PYTHONHTTPSVERIFY=0
```

### 4. 备份文件太大
- 排除大文件：`--exclude-pattern "*.mp4,*.zip"`
- 只备份关键数据而非整个 workspace

## 安全建议

1. **不要将密码硬编码在脚本中**
2. **使用应用密码而非主密码**
3. **定期更换密码**
4. **备份文件建议加密**

## 加密备份（高级）

如需加密备份，在创建 tar.gz 前添加加密步骤：

```bash
# 加密
gpg --symmetric --cipher-algo AES256 backup.tar.gz
# 解密
gpg --decrypt backup.tar.gz.gpg
```
