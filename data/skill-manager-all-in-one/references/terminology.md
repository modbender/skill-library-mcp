# 术语定义 | Terminology Definitions

## 本地技能目录 | Local Skill Directories

| 术语 | 路径 | 说明 |
|------|------|------|
| **本地技能内置目录** | `~/.npm-global/lib/node_modules/openclaw/skills` | OpenClaw 安装时自带的内置技能，随版本更新 |
| **本地技能正式目录** | `~/.openclaw/skills` | 用户安装的技能，**优先度最高**，会覆盖内置目录同名技能 |
| **本地技能临时目录** | `~/.openclaw/workspace/skill-temp` | 临时创建/编辑技能的工作目录，方便操作，定期清理 |

**优先级：** 正式目录 > 内置目录

---

## 操作术语 | Operation Terms

- **下载 / Download**: 从 ClawHub 网站下载技能到本地（`npx clawhub@latest install <slug>`）

- **整理 / Organize**: 将技能文件（SKILL.md、scripts、references、assets）按规范放入文件夹，准备好待用

- **安装 / Install**: 将技能放置到**本地技能正式目录**，使其可被加载。ClawHub 的 `install` 命令会自动完成此步骤

- **初始化 / Initialize**: 使用 `init_skill.py` 创建技能目录结构和模板文件

- **打包 / Package**: （可选）使用 `package_skill.py` 将技能文件夹压缩成 `.skill` 文件，用于手动分发或备份。ClawHub 官方发布流程不需要此步骤

- **上传 / Publish**: 使用 `npx clawhub@latest publish <path>` 将技能文件夹直接发布到 ClawHub

---

## `_meta.json` 元数据文件

ClawHub 发布后生成的元数据文件，记录 skill 在 ClawHub 上的信息。

### 字段含义

```json
{
  "ownerId": "***",
  "slug": "***",
  "version": "*.*.*",
  "publishedAt": ***
}
```

| 字段 | 含义 |
|------|------|
| `ownerId` | 发布关联 ID（⚠️ 同一用户的不同 skill 可能有不同的 ownerId） |
| `slug` | skill 在 ClawHub 上的唯一标识 |
| `version` | 当前发布的版本号 |
| `publishedAt` | 发布时间戳（毫秒） |

### ⚠️ 重要注意事项

1. **文件可能不存在** — 没有 `_meta.json` 不代表未发布
2. **ownerId 不可用于判断归属** — 判断归属应查看 ClawHub dashboard
3. **判断是否已发布** — 应通过 ClawHub API 或 dashboard 确认

---

## 技能命名规范

| 字段 | 格式 | 示例 |
|------|------|------|
| **slug** (部署名) | 全小写 + 连字符 | `weather-forecast` |
| **显示名** (--name) | 首字母大写 + 中文后缀 | `Weather Forecast \| 天气预报` |
| **描述** (description) | 英中文双语 | `Get weather info. 获取天气信息。` |

**示例 frontmatter：**
```yaml
---
name: weather-forecast
description: Get weather info. 获取天气信息。Use when user asks about weather.
---
```

---

## 本地技能临时目录使用规范

**所有技能的临时创建、打草稿、编辑操作，统一在临时目录进行：**

```
~/.openclaw/workspace/skill-temp/<skill-name>/
```

**标准工作流程：**
1. 在临时目录创建/编辑文件
2. 发送完整内容给用户审核
3. 用户确认后，移动到正式目录：
```bash
mv ~/.openclaw/workspace/skill-temp/<skill-name> ~/.openclaw/skills/
```
