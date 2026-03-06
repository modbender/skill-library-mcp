---
name: worldquant-miner-cn
description: WorldQuant Alpha 挖掘器 - AI 驱动的 Alpha 因子生成、测试和提交系统
metadata:
  openclaw:
    emoji: "⛏️"
    category: "finance"
    tags: ["worldquant", "alpha", "trading", "quant", "ai"]
    requires:
      bins: ["python3", "docker"]
---

# WorldQuant Alpha 挖掘器

AI 驱动的 Alpha 因子生成、测试和提交系统。

## 功能

- ⛏️ **Alpha 生成** - Ollama 本地 LLM（3-5x 更快）
- 🧪 **自动测试** - WorldQuant Brain 平台模拟
- 📤 **智能提交** - 每日限制，自动过滤
- 🖥️ **Web Dashboard** - 实时监控和控制
- 🐳 **Docker 部署** - GPU 加速支持

## 架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Web Dashboard  │────▶│ Alpha Generator │────▶│ WorldQuant API  │
│    (Flask)      │     │    (Ollama)     │     │   (External)    │
│   Port 5000     │     │   Port 11434    │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                     ┌─────────────────┐
                     │    Results &    │
                     │   Logs Storage  │
                     └─────────────────┘
```

## 快速开始

### 1. 配置凭据

```bash
# 创建凭据文件
echo '["your.email@worldquant.com", "your_password"]' > credential.txt
```

### 2. 启动系统

```bash
# GPU 版本（推荐）
docker-compose -f docker-compose.gpu.yml up -d

# CPU 版本
docker-compose up -d
```

### 3. 访问 Dashboard

- 主界面：http://localhost:5000
- Ollama WebUI：http://localhost:3000

## 使用方法

### Alpha 生成

```python
from worldquant_miner import AlphaGenerator

# 初始化
generator = AlphaGenerator(
    model="llama3.2:3b",
    credential_path="credential.txt"
)

# 生成 Alpha
alpha = generator.generate()
print(alpha)
# 输出：
# rank(ts_corr(close, volume, 20)) * -1
```

### Alpha 挖掘

```python
from worldquant_miner import AlphaMiner

# 从现有表达式挖掘变体
miner = AlphaMiner(
    expression="rank(ts_corr(close, volume, 20))",
    params={"window": [10, 20, 30, 60]}
)

# 运行
results = miner.run()
# 测试 4 个变体
```

### 批量提交

```python
from worldquant_miner import AlphaSubmitter

submitter = AlphaSubmitter(credential_path="credential.txt")

# 提交成功的 Alpha
submitter.submit_best(
    results_dir="results/",
    min_sharpe=1.0,      # 最低夏普比率
    max_correlation=0.7   # 最大相关性
)
```

## Web Dashboard 功能

### 状态监控

- GPU 状态：内存使用、利用率、温度
- Ollama 状态：模型加载、API 连接
- 编排器状态：生成活动、挖掘计划
- WorldQuant 状态：API 连接、认证

### 手动控制

- Generate Alpha：触发单次 Alpha 生成
- Trigger Mining：运行 Alpha 表达式挖掘
- Trigger Submission：提交成功的 Alpha

### 实时日志

- Alpha 生成日志
- 系统日志
- 最近活动时间线

## 性能对比

| 指标 | Kimi API | 本地 Ollama |
|------|----------|-------------|
| 生成速度 | 10-15s | 3-5s |
| 成本 | 按次收费 | 免费 |
| 隐私 | 数据上传 | 本地处理 |
| 可用性 | 依赖网络 | 离线可用 |

## Alpha 101

WorldQuant 著名的 101 公式化 Alpha：

```python
# Alpha #1
(rank(Ts_ArgMax(SignedPower(((returns < 0) ? stddev(returns, 20) : close), 2.), 5)) - 0.5)

# Alpha #2
(-1 * correlation(rank(delta(log(volume), 2)), rank(((close - open) / open)), 6))

# Alpha #3
(-1 * correlation(rank(open), rank(volume), 10))
```

完整 101 个 Alpha 见 [Alpha101](https://github.com/yli188/WorldQuant_alpha101_code)

## 文件结构

```
worldquant-miner-cn/
├── SKILL.md
├── README.md
├── scripts/
│   ├── setup.sh         # 安装脚本
│   ├── start_gpu.sh     # GPU 启动
│   └── start_cpu.sh     # CPU 启动
└── references/
    └── README_en.md     # 原始英文版
```

## 注意事项

1. **每日限制** - WorldQuant 每天只能提交一次
2. **相关性测试** - 提交前检查相关性
3. **凭据安全** - 不要提交 credential.txt
4. **资源消耗** - GPU 推理需要显存

## 相关链接

- [WorldQuant Brain](https://platform.worldquantbrain.com/)
- [worldquant-miner](https://github.com/zhutoutoutousan/worldquant-miner)
- [Alpha101](https://github.com/yli188/WorldQuant_alpha101_code)

---

*版本: 1.0.0*
*来源: [worldquant-miner](https://github.com/zhutoutoutousan/worldquant-miner)*
