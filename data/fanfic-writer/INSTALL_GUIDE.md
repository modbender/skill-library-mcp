# Fanfic Writer v2.0 - 安装指南 / Installation Guide

自动化小说写作助手 v2.0 - 基于证据的状态管理、多视角QC、原子I/O

---

## 📦 安装要求 / Installation Requirements

### 环境要求 / Environment Requirements

- **OpenClaw**: 最新版本
- **模型**: 由 OpenClaw 自动提供（skill 不硬编码模型）

### 重要说明

这个 skill **不包含任何模型配置**。当 OpenClaw 调用此 skill 时，自动使用 OpenClaw 当前配置的模型。

---

## 📥 安装步骤 / Installation Steps

### 方式一：通过 ClawHub 安装 / Install via ClawHub (Recommended)

```bash
# 搜索 fanfic-writer 技能
clawhub search fanfic-writer

# 安装
clawhub install fanfic-writer
```

### 方式二：手动安装 / Manual Installation

**步骤1: 复制技能文件到 OpenClaw 目录**

**Windows:**
```powershell
# 复制整个 fanfic-writer 目录到
C:\Users\<用户名>\.openclaw\skills\
# 或
C:\Users\<用户名>\clawd\skills\
```

**Linux/macOS:**
```bash
# 复制整个 fanfic-writer 目录到
~/.openclaw/skills/
# 或
~/.clawd/skills/
```

**步骤2: 确保目录结构完整**

```
fanfic-writer/
├── SKILL.md                    # 技能说明 (本文件)
├── INSTALL_GUIDE.md            # 安装指南
├── prompts/
│   ├── v1/                     # 核心模板 (Auto模式必需)
│   │   ├── chapter_outline.md
│   │   ├── chapter_draft_first.md
│   │   ├── chapter_draft_continue.md
│   │   ├── chapter_plan.md
│   │   ├── main_outline.md
│   │   └── world_building.md
│   └── v2_addons/              # 扩展模板
│       ├── critic_editor.md
│       ├── critic_logic.md
│       ├── critic_continuity.md
│       ├── reader_feedback.md
│       ├── qc_evaluate.md
│       ├── backpatch_plan.md
│       └── sanitizer.md
├── scripts/
│   ├── v2/                     # v2.0 核心代码
│   │   ├── __init__.py
│   │   ├── utils.py
│   │   ├── atomic_io.py
│   │   ├── workspace.py
│   │   ├── config_manager.py
│   │   ├── state_manager.py
│   │   ├── prompt_registry.py
│   │   ├── prompt_assembly.py
│   │   ├── price_table.py
│   │   ├── resume_manager.py
│   │   ├── phase_runner.py
│   │   ├── writing_loop.py
│   │   ├── safety_mechanisms.py
│   │   ├── cli.py
│   │   └── test_v2.py
│   ├── v1/                     # v1.0 兼容代码 (可选)
│   └── test_v2.py
└── requirements.txt            # Python依赖 (如需要)
```

**步骤3: 安装 Python 依赖 (如需要)**

```bash
# 进入技能目录
cd fanfic-writer

# 安装依赖 (v2.0 主要使用标准库，通常无需额外安装)
pip install -r requirements.txt
```

**步骤4: 重启 OpenClaw**

安装完成后重启 OpenClaw，技能会自动加载。

```bash
# 重启 OpenClaw
openclaw restart
# 或
openclaw gateway restart
```

---

## 🚀 快速开始 / Quick Start

### 1. 初始化新书 / Initialize a New Book

```bash
# 使用 CLI
python -m scripts.v2.cli init --title "我的小说" --genre "都市灵异" --words 100000

# 或通过 OpenClaw 对话
写一本都市灵异小说
```

### 2. 运行写作 / Run Writing

```bash
# 自动模式写作 (推荐)
python -m scripts.v2.cli write --run-dir <path> --mode auto --chapters 1-10

# 手动模式 (每步需确认)
python -m scripts.v2.cli write --run-dir <path> --mode manual
```

### 3. 断点续写 / Resume Writing

```bash
# 自动检测并续写
python -m scripts.v2.cli write --run-dir <path> --resume auto

# 强制恢复
python -m scripts.v2.cli write --run-dir <path> --resume force
```

### 4. 完成写作 / Finalize

```bash
# 合并章节并生成最终报告
python -m scripts.v2.cli finalize --run-dir <path>
```

---

## 📋 CLI 命令参考 / CLI Command Reference

| 命令 Command | 说明 Description | 示例 Example |
|------------|-----------------|--------------|
| `init` | 初始化新书 | `init --title "书名" --genre "类型"` |
| `setup` | 运行阶段1-5 | `setup --run-dir <path>` |
| `write` | 写作 (阶段6) | `write --run-dir <path> --mode auto` |
| `backpatch` | 回补修复 | `backpatch --run-dir <path>` |
| `finalize` | 最终化 (阶段8-9) | `finalize --run-dir <path>` |
| `status` | 查看状态 | `status --run-dir <path>` |
| `test` | 自测 | `test` |

### 常用参数 / Common Options

| 参数 Option | 说明 Description | 默认值 Default |
|------------|-----------------|----------------|
| `--run-dir, -r` | 运行目录 | 必需 |
| `--mode` | 模式: auto/manual | manual |
| `--chapters` | 章节范围 | 全部 |
| `--resume` | 恢复: off/auto/force | off |
| `--budget` | 成本预算 (元) | 无限制 |
| `--max-words` | 最大字数 | 500000 |

---

## ⚙️ 配置说明 / Configuration

### 0-book-config.json

在初始化时会自动生成，核心字段：

```json
{
  "version": "2.0.0",
  "book": {
    "title": "书名",
    "title_slug": "shu_ming",
    "book_uid": "a1b2c3d4",
    "genre": "都市灵异",
    "target_word_count": 100000,
    "chapter_target_words": 2500
  },
  "generation": {
    "model": "nvidia/moonshotai/kimi-k2.5",
    "mode": "auto",
    "max_attempts": 3,
    "auto_threshold": 85,
    "auto_rescue_enabled": true,
    "auto_rescue_max_rounds": 3
  },
  "qc": {
    "pass_threshold": 85,
    "warning_threshold": 75,
    "weights": {...}
  }
}
```

---

## 💰 成本管理 / Cost Management

### 费率表 / Price Table

v2.0 内置费率表，支持多平台：

```bash
# 查看当前费率
cat 0-config/price-table.json

# 更新费率 (运行时)
# 编辑 price-table.json 后自动热更新
```

### 成本报告 / Cost Report

```bash
# 查看成本日志
cat logs/cost-report.jsonl

# 成本统计
# 在 final/quality-report.md 中查看
```

---

## 🔧 高级功能 / Advanced Features

### 1. 状态面板 / State Panels

v2.0 使用7个状态面板追踪写作进度：

- `4-writing-state.json` - 核心状态
- `characters.json` - 角色状态
- `plot_threads.json` - 剧情线索
- `timeline.json` - 时间线
- `inventory.json` - 道具
- `locations_factions.json` - 地点/势力
- `session_memory.json` - 滚动记忆

### 2. 证据链 / Evidence Chain

所有状态变更需要证据：

```json
{
  "value": "...",
  "evidence_chapter": "第015章",
  "evidence_snippet": "张大胆说：...",
  "confidence": 0.85
}
```

### 3. 安全机制 / Safety Mechanisms

- **Auto-Rescue**: 自动尝试恢复可恢复错误
- **Auto-Abort**: 检测卡死循环并暂停
- **Backpatch**: FORCED章节的回补修复
- **Forced Streak**: 连续FORCED触发熔断

---

## 🐛 故障排查 / Troubleshooting

### 技能未加载 / Skill Not Loading

```bash
# 检查目录结构
ls -la ~/.openclaw/skills/fanfic-writer/

# 重启 OpenClaw
openclaw restart
```

### 模型调用失败 / Model Call Failed

```bash
# 检查 API 配置
openclaw config get

# 确认模型可用
# 查看错误日志
cat <run-dir>/logs/errors.jsonl
```

### 断点续写失败 / Resume Failed

```bash
# 检查状态文件
cat <run-dir>/4-state/4-writing-state.json

# 强制恢复
python -m scripts.v2.cli write --run-dir <path> --resume force
```

---

## 📊 性能优化 / Performance Optimization

### 减少Token消耗

1. **使用高效模型**: 推荐 `moonshot/kimi-k2.5`
2. **调整上下文窗口**: 在配置中设置 `context_bucket`
3. **批量处理**: 使用 `--chapters 1-10` 批量写作

### 成本控制

1. **设置预算**: `--budget 100` (100元)
2. **监控成本**: 查看 `logs/cost-report.jsonl`
3. **使用缓存**: 启用 `cache_mode`

---

## 📄 文件结构 / File Structure

```
novels/
└── {book_title_slug}__{book_uid}/
    └── runs/
        └── {run_id}/
            ├── 0-config/              # 配置
            ├── 1-outline/             # 大纲
            ├── 2-planning/           # 规划
            ├── 3-world/              # 世界观
            ├── 4-state/              # 运行时状态 (7面板)
            ├── drafts/                # 草稿
            ├── chapters/              # 正式章节
            ├── anchors/               # 锚点
            ├── logs/                  # 日志 (token/cost/事件)
            ├── archive/               # 归档 (快照/回滚)
            └── final/                 # 最终输出
```

---

## 🔄 从 v1.0 迁移 / Migration from v1.0

v2.0 保持向后兼容：

```bash
# v1.0 书籍可用 v2.0 继续写作
python -m scripts.v2.cli write --run-dir <v1_book_path> --resume auto
```

注意: v1.0 目录结构不同，需要复制到新的 `runs/{run_id}/` 结构中。

---

## 📞 支持 / Support

- **文档**: 参见 `SKILL.md`
- **问题反馈**: GitHub Issues
- **社区**: OpenClaw Discord

---

## 📄 许可证 / License

MIT License - 可自由使用、修改、分发。

---

**Happy Writing! 🎉**

**创作愉快! 🎉**
