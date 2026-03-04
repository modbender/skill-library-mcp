# SRE Agent 快速开始指南

本指南帮助你在 5 分钟内启动 SRE Agent。

## 1. 环境准备

### 前置要求

- Python 3.11+
- Docker & Docker Compose
- Claude API Key (从 [console.anthropic.com](https://console.anthropic.com) 获取)

### 克隆项目

```bash
git clone <repo-url>
cd sre-agent
```

## 2. 快速启动 (Docker Compose)

### 2.1 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
WEBHOOK_URL=https://your-webhook-url  # 可选
```

### 2.2 启动所有服务

```bash
docker-compose up -d
```

这将启动：
- **sre-agent**: 主服务 (端口 8000)
- **prometheus**: 指标存储 (端口 9090)
- **loki**: 日志存储 (端口 3100)
- **qdrant**: 向量数据库 (端口 6333)
- **grafana**: 可视化 (端口 3000)

### 2.3 验证启动

```bash
# 检查健康状态
curl http://localhost:8000/health

# 预期响应
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development"
}
```

### 2.4 查看日志

```bash
docker-compose logs -f sre-agent
```

## 3. 本地开发启动

### 3.1 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3.2 安装依赖

```bash
make dev-install
# 或
pip install -e ".[dev]"
```

### 3.3 启动依赖服务

```bash
docker-compose up -d prometheus loki qdrant
```

### 3.4 配置环境变量

```bash
export ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
export PROMETHEUS_URL=http://localhost:9090
export LOKI_URL=http://localhost:3100
```

### 3.5 运行测试

```bash
make test
```

### 3.6 启动 Agent

```bash
# 启动 API 服务 (开发模式，带热重载)
make run-api

# 或启动完整 Agent
make run
```

## 4. 基本操作

### 4.1 查看 Agent 状态

```bash
curl http://localhost:8000/api/v1/status
```

响应示例：
```json
{
  "running": true,
  "active_anomalies": 0,
  "baselines_loaded": 15,
  "metrics_collector_connected": true,
  "logs_collector_connected": true
}
```

### 4.2 查看配置的指标

```bash
curl http://localhost:8000/api/v1/metrics
```

### 4.3 查看异常

```bash
curl http://localhost:8000/api/v1/anomalies
```

### 4.4 查看基线

```bash
curl http://localhost:8000/api/v1/baselines
```

### 4.5 查看待审批

```bash
curl http://localhost:8000/api/v1/approvals
```

## 5. 模拟测试

由于新环境没有历史数据，异常检测会使用静态阈值。你可以：

### 5.1 等待数据积累

Agent 需要至少 7 天数据才能学习有效基线。在此之前：
- 异常检测使用静态阈值
- 准确率可能较低

### 5.2 手动触发测试

```bash
# 查看 API 文档
open http://localhost:8000/docs
```

## 6. 停止服务

```bash
# 停止所有 Docker 服务
docker-compose down

# 保留数据
docker-compose down

# 清除所有数据
docker-compose down -v
```

## 7. 下一步

- 阅读完整文档: `docs/IMPLEMENTATION.md`
- 配置你的 Prometheus 目标指标
- 自定义 `config/promql_queries.yaml` 添加你的指标
- 配置 Webhook 接收告警通知
- 创建自定义 Playbook

## 常见问题

### Q: Agent 启动后没有检测到异常？

这是正常的。Agent 需要先学习基线（需要历史数据），才能准确检测异常。

### Q: 如何添加我自己的指标？

编辑 `config/promql_queries.yaml`，添加你的 PromQL 查询。

### Q: 如何关闭自动修复？

在 `config/config.yaml` 中设置：
```yaml
auto_remediation:
  enabled: false
```

或设置 dry-run 模式：
```yaml
auto_remediation:
  enabled: true
  dry_run: true
```

### Q: 如何查看审计日志？

```bash
# Docker
docker-compose exec sre-agent cat /var/log/sre-agent/audit.log

# 本地开发
cat /var/log/sre-agent/audit.log
```

---

更多详细信息请参考 [完整实现文档](./IMPLEMENTATION.md)。
