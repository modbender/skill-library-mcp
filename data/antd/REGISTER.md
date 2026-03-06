# Ant Design Skill 注册指南

## 自动注册（推荐）

OpenClaw 会自动扫描工作区的 `skills/` 目录。antd skill 已位于正确位置：

```
~/.openclaw/workspace/skills/antd/
```

## 验证注册

### 1. 检查技能列表

```bash
openclaw skills list
```

应该能看到 `antd` 在列表中。

### 2. 检查技能状态

```bash
openclaw skills check
```

确认 antd skill 没有缺失依赖。

### 3. 查看技能信息

```bash
openclaw skills info antd
```

## 手动注册（如果需要）

如果自动扫描未生效，可以在配置中添加：

```json
{
  "skills": {
    "custom": [
      {
        "id": "antd",
        "name": "Ant Design 组件库",
        "path": "~/.openclaw/workspace/skills/antd",
        "enabled": true
      }
    ]
  }
}
```

## 使用方式

注册成功后，在对话中直接使用：

```
用 Ant Design 创建一个登录表单
帮我添加一个 Table 组件
用 Modal 做一个确认对话框
```

## 文件结构

```
~/.openclaw/workspace/skills/antd/
├── SKILL.md              # ✅ Skill 描述（必需）
├── README.md             # ✅ 快速开始（中文）
├── README.en-US.md       # ✅ 快速开始（英文）
├── COMPONENTS.md         # ✅ 组件参考（中文）
├── COMPONENTS.en-US.md   # ✅ 组件参考（英文）
├── EXAMPLES.md           # ✅ 基础示例
├── EXAMPLES-ENTERPRISE.md # ✅ 企业级示例
├── SUMMARY.md            # ✅ 文档说明
└── REGISTER.md           # 本文档
```

## 状态确认

- [x] SKILL.md 存在且格式正确
- [x] 位于正确的 skills 目录
- [x] 文档完整（中英文）
- [x] 示例代码完整
- [x] 无外部依赖（纯 Markdown）

## 状态：✅ 已注册

Ant Design Skill 已成功注册到 OpenClaw，可以立即使用！
