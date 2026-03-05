# 服务器监控技能

一个简单的服务器监控技能，用于监控服务器状态和性能指标。

## 安装

```bash
# 通过 ClawHub 安装
clawhub install server-monitor
```

## 使用方法

### 作为独立脚本运行
```bash
node index.js
```

### 在 OpenClaw 中使用
当用户询问服务器状态时，技能会自动运行并返回监控报告。

## 监控指标

1. **系统信息**
   - 主机名
   - 操作系统
   - 内核版本
   - 运行时间
   - CPU核心数

2. **内存使用情况**
   - 总内存
   - 已使用内存
   - 可用内存
   - 使用率百分比

3. **磁盘使用情况**
   - 文件系统
   - 总大小
   - 已使用空间
   - 可用空间
   - 使用率百分比
   - 挂载点

4. **CPU负载**
   - 1分钟负载
   - 5分钟负载
   - 15分钟负载

5. **运行中的进程**
   - CPU使用率最高的前5个进程

## 示例输出

```json
{
  "timestamp": "2026-02-10T13:45:30.123Z",
  "system": {
    "hostname": "myserver",
    "platform": "linux x64",
    "kernel": "6.8.0-90-generic",
    "uptime": "15天 3小时 25分钟",
    "nodeVersion": "v22.22.0",
    "cpus": 4
  },
  "memory": {
    "total": "15.68 GB",
    "used": "8.24 GB",
    "free": "7.44 GB",
    "usagePercent": "52.58%"
  },
  "disk": {
    "filesystem": "/dev/sda1",
    "size": "100G",
    "used": "45G",
    "available": "55G",
    "usagePercent": "45%",
    "mounted": "/"
  },
  "cpu": {
    "1min": "0.85",
    "5min": "0.72",
    "15min": "0.68"
  },
  "topProcesses": "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\nroot      1234  5.2  2.1 123456 78900 ?        Ss   09:00   5:23 /usr/bin/python3\n..."
}
```

## 开发

### 项目结构
```
server-monitor/
├── SKILL.md          # 技能元数据
├── README.md         # 说明文档
├── package.json      # 项目配置
├── index.js          # 主程序
└── tests/            # 测试文件（可选）
```

### 测试
```bash
# 运行测试
npm test
```

## 许可证

MIT License