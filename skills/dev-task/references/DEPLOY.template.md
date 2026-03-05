# DEPLOY - vX.Y.Z

## 部署环境

- **服务器**: VPS / 云服务器
- **操作系统**: Ubuntu 20.04 / CentOS 8
- **运行时**: Node.js >= 18 / Python >= 3.9
- **端口**: XXXX

## 部署步骤

### 1. 安装依赖

```bash
cd /path/to/project
npm install  # 或 pip install -r requirements.txt
```

### 2. 配置环境

```bash
# 编辑配置文件
cp .env.example .env
vim .env
```

### 3. 启动服务

```bash
npm start  # 或 python server.py
```

### 4. 后台运行（生产环境）

使用 PM2：

```bash
npm install -g pm2
pm2 start server.js --name project-name
pm2 save
pm2 startup
```

或使用 systemd：

```bash
cat > /etc/systemd/system/project-name.service << EOF
[Unit]
Description=Project Name
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/node server.js
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl enable project-name
systemctl start project-name
```

## 回滚方案

如需要回滚到 vX.Y.Z：

```bash
cd /path/to/project

# 停止服务
pm2 stop project-name

# 恢复代码
cp -r versions/vX.Y.Z/src/* ./

# 重新安装依赖
npm install

# 启动服务
pm2 start project-name
```

## 监控

### 查看日志

```bash
# PM2 日志
pm2 logs project-name

# 直接查看
journalctl -u project-name -f
```

### 健康检查

```bash
curl http://localhost:PORT/health
```

## 备份策略

定期备份 versions 目录：

```bash
tar czf backup-project-$(date +%Y%m%d).tar.gz versions/
```
