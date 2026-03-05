# my-mind Manager Skill

帮助管理灵感、文章和创作素材的 AI 技能插件。

## 🚀 快速开始

### 1. 在 CatPaw IDE 中使用

CatPaw 是该技能的最佳运行环境，支持渐进式加载和可视化管理。

#### 安装与存放目录
将本仓库克隆或移动到以下任一合法目录下，CatPaw 将自动识别：
- **项目级**：`[项目根目录]/.catpaw/skills/` (推荐)
- **全局级**：`~/.catpaw/skills/` (所有项目通用)
- *注：同时也支持 `.claude/skills`, `.cursor/skills`, `.codex/skills` 目录。*

#### 激活与配置
1. **自动识别**：CatPaw 会读取 `SKILL.md` 中的 `description`。当你的指令命中描述时，AI 会自动加载该技能。
2. **可视化管理**：
   - 进入 CatPaw **配置页面** -> **Agent Skills**。
   - 你可以查看已加载的技能列表，并进行开启/关闭或删除操作。
3. **快捷创建**：在编辑器中输入 `/` 唤起面板，点击 **skills** 可进入二级面板快速生成或管理技能。

### 2. 在 OpenClaw 中使用

如果你希望在命令行环境下使用：

1. **安装**：将技能仓库克隆到 OpenClaw 的 skills 目录
   ```bash
   # 克隆到 workspace skills（推荐）
   cd ~/.openclaw/workspace/skills
   git clone <技能仓库地址> my-mind-manager

   # 或者克隆到全局 skills
   cd ~/.openclaw/skills
   git clone <技能仓库地址> my-mind-manager
   ```

2. **触发方式**：

   - **方式一：slash command（推荐）**
     ```
     /my-mind-manager
     ```

   - **方式二：自然语言触发**
     - "帮我管理 my-mind"
     - "初始化目录结构"
     - "记录一个灵感"
     - "帮我写篇文章"

---

## 📁 技能文件结构

一个标准的 Skill 是一个包含说明书的文件夹：
- `SKILL.md`: **核心定义文件**。包含 YAML 元数据（name, description）和分步任务指南。
- `references/`: 存放该技能依赖的知识库、规则和示例。
- `scripts/`: (可选) 存放辅助脚本。

---

## 💡 功能说明

### 初始化目录结构

自动创建标准的 my-mind 目录结构，包括：
- ideas/（灵感库）
- articles/（文章库）
- assets/（素材库）
- inbox/（收集箱）
- archive/（归档）

### 灵感管理

- 快速记录碎片想法
- 整理成结构化内容
- 项目构想管理

### 文章创作

- 创建和编辑草稿
- 写作辅助
- 发布管理

### 素材管理

- 归类整理
- 移动和清理

---

## 📝 触发示例

| 场景 | 触发语 |
|------|--------|
| 初始化 | "初始化 my-mind"、"创建目录结构" |
| 记录灵感 | "记录灵感"、"有个想法" |
| 写文章 | "帮我写篇文章"、"创作" |
| 发布 | "发布文章"、"完成写作" |

---

Designed with ❤️.
