# Triple-Layer Memory System

三层记忆系统 - 解决 AI Agent 长对话记忆丢失和上下文管理问题

## 特性

- ✅ Session 自动压缩（150k tokens 触发）
- ✅ 记忆写入时机优化（关键时机立即写入）
- ✅ 跨 Session 记忆连续性（智能加载）
- ✅ 记忆遗忘机制（语义去重、高频升权、低权归档）
- ✅ 频道级记忆隔离（Mem0 命名空间）

## 架构

```
Layer 3: Session 管理层（自动压缩、智能加载）
    ↓
Layer 2: 文件层（索引/项目/经验/日志）
    ↓
Layer 1: Mem0（向量检索）
```

## 快速开始

### 安装

```bash
# 使用 clawhub 安装
clawhub install triple-layer-memory

# 或手动安装
cd ~/Desktop/openclaw-workspace/skills
git clone https://github.com/0range-x/triple-layer-memory.git
```

### 初始化

```bash
cd ~/Desktop/openclaw-workspace
bash skills/triple-layer-memory/scripts/init.sh
```

### 配置

1. 更新 `AGENTS.md` 添加 Session 启动流程
2. 更新 `HEARTBEAT.md` 添加 token 检查逻辑
3. 如果使用 Mem0，配置频道级命名空间隔离

详细文档：[SKILL.md](SKILL.md)

## 性能指标

- Session 寿命：~100k → ~150k tokens
- 记忆丢失率：~30% → ~5%
- 新 session 启动时间：~10s → ~3s
- 记忆检索准确率：~60% → ~85%

## 文件结构

```
workspace/
├── MEMORY.md                    # 核心索引
├── MEMORY_ARCHITECTURE.md       # 架构文档
├── memory/
│   ├── projects.md              # 项目状态追踪
│   ├── lessons.md               # 经验教训库
│   ├── YYYY-MM-DD.md           # 日志文件
│   └── .archive/               # 归档目录
└── scripts/
    ├── session_compress.py      # Session 自动压缩
    ├── auto_memory_write.py     # 自动记忆写入
    ├── memory_decay.py          # 记忆衰减和归档
    └── ...
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 作者

小橘 (vulcanx_14970)

## 致谢

- [Mem0](https://github.com/mem0ai/mem0) - 向量检索框架
- [OpenClaw](https://openclaw.ai) - AI Agent 框架
