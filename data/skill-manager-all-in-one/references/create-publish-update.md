# 创建、发布与更新 | Create, Publish & Update

## 创建 Skill

### 流程：先本地，后网络

1. 检查本地是否有 skill-creator（本地技能内置目录）：
```bash
ls ~/.npm-global/lib/node_modules/openclaw/skills/skill-creator
```

2. 本地有 → 读取并使用：
```
读取：本地技能内置目录/skill-creator/SKILL.md
```

3. 本地没有 → 提示用户：
```
未找到 skill-creator。这是 OpenClaw 内置 skill，请检查安装。
```

### 重要提示

- **双语描述**：制作技能时，描述及重要内容必须使用**英中文双语**（先英文再中文）
- **审核流程**：用户要求更新技能时，**不要立即执行**。必须先将修改后的完整内容发给用户审核，用户确认后再执行
- **操作透明化**：所有操作必须向用户报告**具体路径和操作细节**

---

## 发布到 ClawHub

### 发布流程

1. **确认命名规范**
   - slug: 全小写 + 连字符（从 SKILL.md 的 `name` 字段读取）

2. **生成显示名**
   - 将 slug 转为首字母大写：`weather-forecast` → `Weather Forecast`
   - 建议加中文后缀：`Weather Forecast | 天气预报`

3. **changelog 版本更新内容**
   - 必须用英中文双语（先英文再中文）描述

4. **执行发布**
```bash
npx clawhub@latest publish ~/.openclaw/skills/<slug> \
  --slug <slug> \
  --name "<Display Name>" \
  --version <version> \
  --changelog "<changelog>"
```

5. **发布后汇报**
   - 简要汇报，并提供相关网址

### 示例

```bash
# 发布 weather-forecast v1.0.0
npx clawhub@latest publish ~/.openclaw/skills/weather-forecast \
  --slug weather-forecast \
  --name "Weather Forecast | 天气预报" \
  --version 1.0.0 \
  --changelog "Initial release. 首次发布。"
```

### ⚠️ 注意事项

- 发布可能就是在 ClawHub 去更新或升版
- 存在用户已经发布了同名技能的情况
- 如果版本已存在，会报错 "Version already exists"，需要升版号

---

## 更新本地技能

### 单个 Skill 更新

**步骤 1：获取版本信息**
1. 查看本地版本（检查 `_meta.json` 或 SKILL.md）
2. 搜索 ClawHub 获取远程版本：
```bash
npx clawhub@latest search <skill-name>
```

**步骤 2：对比版本**
- 本地版本 < 远程版本 → 有更新
- 本地版本 = 远程版本 → 已是最新

**步骤 3：执行更新**
```bash
npx clawhub@latest install <skill-name>
```

---

### 批量更新本地技能

**步骤 1：扫描本地技能正式目录**
```bash
ls ~/.openclaw/skills/
```

**步骤 2：逐个检测**

对每个本地 skill 重复：
1. 读取本地 `_meta.json` 获取当前版本
2. 搜索 ClawHub 获取远程版本
3. 对比版本号和更新日期

**步骤 3：生成报告**

| Skill | 本地版本 | 远程版本 | 状态 | 更新日期 |
|-------|----------|----------|------|----------|
| weather-forecast | 1.0.0 | 1.1.0 | ⬆️ 可更新 | 2026-03-01 |
| task-reminder | 1.1.0 | 1.1.0 | ✅ 最新 | 2026-02-28 |

**步骤 4：询问用户**
```
发现 2 个可更新的 skill：
1. weather-forecast (1.0.0 → 1.1.0)
2. another-skill (1.0.0 → 1.2.0)

是否全部更新？输入：
- all: 更新全部
- 1,2: 仅更新指定
- skip: 跳过
```

**步骤 5：执行更新**
```bash
npx clawhub@latest install <slug>
```

**步骤 6：更新后报告**
```
✅ 更新完成：
- weather-forecast: 1.0.0 → 1.1.0

请重启会话以加载新版本。
```
