# 🧠 MindCore — 仿生潜意识心智引擎

[🇬🇧 English README](./README.md)

> 仿生潜意识心智引擎：让 AI 拥有像人类一样的自发念头、情绪底色和随机冲动。

MindCore 是一个独立运行的后台「潜意识引擎」。它不依赖用户输入，而是**每秒自主掷骰子**，模拟人类大脑中随机涌现的念头（"想喝奶茶"、"好无聊想刷手机"、"突然想找人聊天"）。

当某个念头的概率积累到突破阈值时，引擎会输出一个 JSON 信号，告诉你的 AI Agent：**"我现在有话想说了。"**

## ✨ 核心特性

- **5 层仿生架构**：噪声层 → 感知层 → 冲动层 → 性格闸门 → 输出模板
- **150 个日常冲动**：从"想喝咖啡"到"想发呆"，覆盖 9 大类真实人类行为
- **随机而非定时**：基于粉红噪声 + Hawkes 过程 + sigmoid 概率的随机触发，不是机械的定时器
- **昼夜节律**：真实时钟驱动的饥饿/口渴/睡眠波动
- **短期记忆**：5 槽 FIFO 对话缓冲，话题关键词自动影响冲动倾向（2 小时指数衰减）
- **心境底色**：mood_valence 持续影响正/负面冲动的触发概率
- **可调频率**：`BURST_BASE_OFFSET` 一个参数控制整体活跃度

## 📐 架构概览

```
Layer 0: 噪声发生器 (3000 节点)
    ├── 粉红噪声 (1/f，长程相关性)
    ├── Ornstein-Uhlenbeck (生理基线波动)
    ├── Hawkes 过程 (情绪连锁反应)
    └── 马尔可夫链 (离散潜意识状态)
         ↓
Layer 1: 感知层 (150 传感器)
    ├── 身体状态 (饥饿/疲劳/生理节律)
    ├── 环境感知 (时间/天气/噪音)
    └── 社交上下文 (互动/冷落/在线状态)
         ↓
Layer 2: 冲动涌现 (150 冲动节点)
    ├── Synapse Matrix (感知→冲动映射)
    ├── Sigmoid 概率转换
    ├── 心境调制 + 时段权重
    └── 掷骰子 → 随机触发！
         ↓
Layer 3: 性格闸门 (Softmax 采样)
    ├── 可学习的性格权重
    ├── 短期记忆话题加权
    └── 选出胜出的 1~2 个冲动
         ↓
Layer 4: 输出模板
    └── 生成 JSON → 落盘到 output/
```

详细架构请见 [ARCHITECTURE.md](./ARCHITECTURE.md)。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

> 需要 Python 3.8+。首次运行会自动下载 `all-MiniLM-L6-v2` 本地 NLP 模型（~80MB），用于自动生成突触矩阵。

### 2. 初始化数据

数据文件已包含在 `data/` 目录中，可以直接使用。如需重置为默认状态，参考 `data/` 下的 JSON 文件格式。

### 3. 启动引擎

```bash
python3 engine_supervisor.py
```

引擎将以 1 秒/Tick 的频率持续运行。当冲动突破阈值时，会在 `output/` 目录生成 JSON 文件。

### 4. 接入 OpenClaw

MindCore 通过 `js_bridge/` 与 [OpenClaw](https://openclaw.ai) 集成：

```bash
# 设置环境变量
export OPENCLAW_TARGET=<your_telegram_chat_id>
export OPENCLAW_COMMAND=openclaw

# 启动桥接
node js_bridge/OpenClawBridge.js
```

桥接程序会监听 `output/` 目录，当引擎产生冲动时，自动调用 `openclaw agent --deliver` 将念头注入 Agent，由 Agent 以自己的人格生成回复并发送到 Telegram。

### 5. 使用 PM2 管理（推荐）

```bash
npm install -g pm2
pm2 start ecosystem.config.js
pm2 logs
```

## ⚙️ 配置

### 调整触发频率

编辑 `engine/config.py` 中的 `BURST_BASE_OFFSET`：

| 值 | 模式 | 平均触发频率 |
|---|---|---|
| `12.5` | 正常模式 | ~2-3 次/小时 |
| `11.0` | 活跃模式 | ~1 次/10 分钟 |
| `10.0` | 测试爆字模式 | ~1 次/2 分钟 |

### 传感器状态

编辑 `data/Sensor_State.json` 可以手动设置当前的身体/环境/社交状态。引擎内置了真实时钟驱动的生理节律（饥饿、口渴、睡眠），无需手动维护。

### 短期记忆

`data/ShortTermMemory.json` 保存最近 5 条对话话题。话题关键词会自动影响相关冲动的触发概率（2 小时半衰期自然衰减）。

## 📁 项目结构

```
MindCore/
├── engine/                   # 核心引擎
│   ├── config.py             # 全局超参数
│   ├── layer0_noise.py       # 噪声发生器 (4 引擎)
│   ├── layer1_sensors.py     # 感知层 + 生物钟节律
│   ├── layer2_impulses.py    # 冲动涌现 + 概率引擎
│   ├── layer3_personality.py # 性格闸门 + 话题加权
│   ├── layer4_output.py      # 输出模板生成
│   ├── engine_loop.py        # 主循环编排
│   ├── short_term_memory.py  # 短期记忆管理
│   └── auto_topology.py      # 突触矩阵自动构建
├── js_bridge/                # OpenClaw 桥接层
│   ├── OpenClawBridge.js     # 主桥接程序
│   ├── MindObserver.js       # output/ 目录监听器
│   └── SensorWriter.js       # 传感器状态写入工具
├── data/                     # 运行时数据
│   ├── Sensor_State.json     # 当前传感器状态
│   ├── ShortTermMemory.json  # 短期记忆
│   ├── Synapse_Matrix.npy    # 突触连接矩阵
│   └── LongTermMemory.json   # 长期记忆 (预留)
├── output/                   # 冲动输出落盘目录
├── engine_supervisor.py      # 守护进程入口
├── ecosystem.config.js       # PM2 部署配置
├── ARCHITECTURE.md           # 详细架构文档
└── CHANGELOG.md              # 更新日志
```

## 📜 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

You are free to:
- ✅ 个人使用、学习、研究
- ✅ 修改代码并贡献回社区
- ✅ 在自己的非商业项目中使用

但是：
- ⚠️ 如果你修改了 MindCore 并部署为服务，**你必须开源你的修改**
- ⚠️ 基于 MindCore 的衍生作品也必须使用 AGPL-3.0 许可

### 🤝 商业授权

如果你希望在商业产品中使用 MindCore（例如：AI 陪伴硬件、商业 Bot 服务等），但不希望受 AGPL 的开源要求约束，请联系作者获取**商业许可证**：

📧 联系方式：[请在此填写你的联系邮箱]

---

_MindCore — 让你的 AI 不再只是被动回答，而是像一个活生生的人一样，会主动想、主动说。_
