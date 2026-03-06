# soul-pack

一组用于 **导出/导入 SOUL 包** 并自动创建 OpenClaw agent 的脚本与 Skill 骨架。

## 目录结构

```text
soul-pack-skill/
├─ SKILL.md
├─ README.md
├─ schema/
│  └─ manifest.schema.v0.1.json
└─ scripts/
   ├─ export-soul.sh
   ├─ import-soul.sh
   └─ list-souls.sh
```

## 功能

- `export-soul.sh`：从 workspace 导出 `SOUL.md` 为标准包目录 + `.tar.gz`
- `import-soul.sh`：导入 soul 包到新/已有 workspace，并自动 `openclaw agents add`
- `list-souls.sh`：列出本地 soul 包与 manifest

## 快速开始

### 1) 导出 soul 包

```bash
bash scripts/export-soul.sh \
  --workspace /Users/feifei/.openclaw/workspace \
  --out /Users/feifei/projects/soul-packages \
  --name edith-soul
```

输出：
- `/Users/feifei/projects/soul-packages/edith-soul/`
- `/Users/feifei/projects/soul-packages/edith-soul.tar.gz`

### 2) 导入 soul 包并创建 agent

```bash
bash scripts/import-soul.sh \
  --package /Users/feifei/projects/soul-packages/edith-soul.tar.gz \
  --agent my-soul \
  --workspace /Users/feifei/projects/agents/my-soul
```

可选：
- `--force`：允许覆盖已存在的 `SOUL.md`

### 3) 列出本地 soul 包

```bash
bash scripts/list-souls.sh --dir /Users/feifei/projects/soul-packages
```

## 包规范

导出包结构：

```text
my-soul-package/
├─ SOUL.md
├─ preview.md
└─ manifest.json
```

`manifest.json` 最小字段：

- `name`
- `version`（`x.y.z`）
- `createdAt`（ISO 时间）
- `files`（必须包含 `SOUL.md`, `preview.md`, `manifest.json`）

校验 schema：`schema/manifest.schema.v0.1.json`

## 依赖

- bash
- python3（用于 manifest 基础校验）
- openclaw CLI（用于 `openclaw agents add`）

## 注意事项

- 默认不覆盖已有 `SOUL.md`，防止误操作
- 请勿在包内放 API Key / token
- 建议先在测试 agent 上验证导入效果
