---
name: rssh2
description: SSH远程自动化工具 - 会话管理、隧道、文件传输。使用场景：需要远程执行命令、建立SSH隧道、传输文件时。
metadata: {"clawdbot":{"emoji":"🔐","requires":{"bins":[]},"dependencies":["ssh2"]}}
---

# Rssh2 - SSH远程自动化工具

基于 ssh2 的 SSH 远程自动化工具，提供会话管理、隧道管理、文件传输等功能。

## ⚠️ 安全提示

**重要：** 请勿在代码中硬编码敏感信息（密码、私钥内容等）。建议：
- 使用环境变量存储敏感配置
- 使用密钥文件路径而非密钥内容
- 将 test.js 中的配置替换为实际配置后再运行

## 功能特性

### 🔐 会话管理
- 连接池管理（复用连接，提升性能）
- 自动重连机制
- 心跳保持
- 命令队列
- 并发控制

### 🌉 隧道管理
- 本地端口转发
- 远程端口转发
- 动态端口转发（SOCKS代理）
- 多隧道管理
- 自动重连

### 📁 文件传输
- SFTP 上传/下载
- 目录同步
- 文件监控
- 断点续传

### ⚙️ 配置管理
- 多主机配置
- 密钥管理
- 环境变量支持
- 配置文件热加载

## 快速开始

### 基本连接

```javascript
const { Rssh2 } = require('./index.js');

const rssh2 = new Rssh2({
  host: 'bg.dlna.net',
  port: 38022,
  username: 'root',
  privateKey: '/home/yupeng/.ssh/id_ed25519'
});

// 执行命令
const result = await rssh2.exec('uptime');
console.log(result.output);
```

### 会话管理

```javascript
// 创建会话管理器
const sessionManager = rssh2.getSessionManager();

// 执行多个命令（复用连接）
const results = await Promise.all([
  sessionManager.exec('uptime'),
  sessionManager.exec('df -h'),
  sessionManager.exec('free -m')
]);

// 关闭会话
await sessionManager.close();
```

### 隧道管理

```javascript
// 本地端口转发
const tunnel = await rssh2.tunnel.local({
  localPort: 8080,
  remoteHost: 'localhost',
  remotePort: 80
});

console.log('隧道已建立: localhost:8080 -> remote:80');

// 关闭隧道
await tunnel.close();
```

### 文件传输

```javascript
// 上传文件
await rssh2.sftp.upload('./local.txt', '/remote/path/file.txt');

// 下载文件
await rssh2.sftp.download('/remote/path/file.txt', './local.txt');

// 同步目录
await rssh2.sftp.sync('./local-dir', '/remote/dir');
```

## 配置选项

### 连接配置

```javascript
{
  host: 'example.com',        // 主机地址
  port: 22,                   // SSH端口
  username: 'user',           // 用户名
  password: 'pass',           // 密码（可选）
  privateKey: '/path/to/key', // 私钥路径（可选）
  passphrase: 'keypass',      // 私钥密码（可选）
  timeout: 10000,             // 连接超时（毫秒）
  keepaliveInterval: 30000    // 心跳间隔（毫秒）
}
```

### 会话管理器配置

```javascript
{
  maxPoolSize: 5,             // 最大连接池大小
  maxConcurrent: 10,          // 最大并发命令数
  commandTimeout: 30000,      // 命令超时（毫秒）
  retryAttempts: 3,           // 重试次数
  retryDelay: 1000            // 重试延迟（毫秒）
}
```

### 隧道配置

```javascript
{
  localPort: 8080,            // 本地端口
  remoteHost: 'localhost',    // 远程主机
  remotePort: 80,             // 远程端口
  autoReconnect: true,        // 自动重连
  reconnectDelay: 5000        // 重连延迟（毫秒）
}
```

## API 参考

### Rssh2 主类

#### `constructor(config)`
创建 Rssh2 实例

#### `exec(command, options?)`
执行单个命令

#### `getSessionManager()`
获取会话管理器实例

#### `getTunnelManager()`
获取隧道管理器实例

#### `getSftpManager()`
获取 SFTP 管理器实例

#### `connect()`
建立连接

#### `disconnect()`
断开连接

### SessionManager

#### `exec(command, options?)`
执行命令（使用连接池）

#### `execMultiple(commands)`
执行多个命令

#### `close()`
关闭所有连接

### TunnelManager

#### `local(config)`
创建本地端口转发

#### `remote(config)`
创建远程端口转发

#### `dynamic(config)`
创建动态端口转发（SOCKS）

#### `closeAll()`
关闭所有隧道

### SftpManager

#### `upload(localPath, remotePath)`
上传文件

#### `download(remotePath, localPath)`
下载文件

#### `sync(localDir, remoteDir)`
同步目录

#### `list(path)`
列出文件

#### `delete(path)`
删除文件

## 使用场景

### 1. 远程运维

```javascript
const rssh2 = new Rssh2(config);

// 检查服务状态
const status = await rssh2.exec('systemctl status nginx');

// 重启服务
await rssh2.exec('systemctl restart nginx');

// 查看日志
const logs = await rssh2.exec('tail -n 100 /var/log/nginx/access.log');
```

### 2. 数据库隧道

```javascript
// 创建数据库隧道
const tunnel = await rssh2.tunnel.local({
  localPort: 3306,
  remoteHost: 'localhost',
  remotePort: 3306
});

// 现在可以通过 localhost:3306 访问远程数据库
```

### 3. 文件部署

```javascript
// 上传应用文件
await rssh2.sftp.upload('./app.zip', '/tmp/app.zip');

// 解压
await rssh2.exec('cd /var/www && unzip -o /tmp/app.zip');

// 重启服务
await rssh2.exec('systemctl restart app');
```

### 4. 批量操作

```javascript
const session = rssh2.getSessionManager();

// 并发执行多个命令
const results = await session.execMultiple([
  'uptime',
  'df -h',
  'free -m',
  'ps aux | head -20'
]);

console.log(results);
```

## 安全建议

1. **使用密钥认证** - 比密码更安全
2. **限制用户权限** - 不要使用 root 账号
3. **启用防火墙** - 限制 SSH 访问
4. **定期更新密钥** - 轮换 SSH 密钥
5. **日志审计** - 记录所有操作

## 故障排查

### 连接失败

```javascript
try {
  await rssh2.connect();
} catch (error) {
  console.error('连接失败:', error.message);
  // 检查主机、端口、认证信息
}
```

### 命令超时

```javascript
const result = await rssh2.exec('long-running-command', {
  timeout: 60000  // 60秒超时
});
```

### 隧道断开

```javascript
const tunnel = await rssh2.tunnel.local(config, {
  autoReconnect: true,
  reconnectDelay: 5000
});
```

## 依赖

- ssh2 ^1.17.0

## 许可证

MIT