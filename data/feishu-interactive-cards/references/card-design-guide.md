# 飞书交互式卡片设计指南

## 卡片结构

每个飞书交互式卡片由以下部分组成：

```json
{
  "config": {
    "wide_screen_mode": true  // 宽屏模式
  },
  "header": {
    "title": { "content": "标题", "tag": "plain_text" },
    "template": "blue"  // 颜色主题
  },
  "elements": [
    // 卡片内容元素
  ]
}
```

## 可用元素类型

### 1. 文本元素 (div)

```json
{
  "tag": "div",
  "text": {
    "content": "**粗体文本** 或 *斜体文本*",
    "tag": "lark_md"  // 支持 Markdown
  }
}
```

### 2. 分隔线 (hr)

```json
{
  "tag": "hr"
}
```

### 3. 按钮组 (action)

```json
{
  "tag": "action",
  "actions": [
    {
      "tag": "button",
      "text": { "content": "按钮文字", "tag": "plain_text" },
      "type": "primary",  // primary, default, danger
      "value": {
        "action": "action_name",
        "param1": "value1"
      }
    }
  ]
}
```

### 4. 表单 (form)

```json
{
  "tag": "form",
  "name": "form_name",
  "elements": [
    {
      "tag": "input",
      "name": "field_name",
      "placeholder": { "content": "提示文字", "tag": "plain_text" },
      "max_length": 100
    },
    {
      "tag": "textarea",
      "name": "field_name",
      "placeholder": { "content": "提示文字", "tag": "plain_text" },
      "rows": 3
    },
    {
      "tag": "select_static",
      "name": "field_name",
      "placeholder": { "content": "请选择", "tag": "plain_text" },
      "options": [
        { "text": { "content": "选项1", "tag": "plain_text" }, "value": "opt1" }
      ]
    }
  ]
}
```

## 颜色主题

header.template 可用值：
- `blue` - 蓝色（默认）
- `green` - 绿色（成功）
- `orange` - 橙色（警告）
- `red` - 红色（危险）
- `purple` - 紫色
- `yellow` - 黄色

## 按钮类型

button.type 可用值：
- `primary` - 主要按钮（蓝色）
- `default` - 默认按钮（白色）
- `danger` - 危险按钮（红色）

## 设计原则

### 1. 清晰的视觉层次

```json
{
  "elements": [
    {
      "tag": "div",
      "text": { "content": "**主标题**", "tag": "lark_md" }
    },
    {
      "tag": "div",
      "text": { "content": "详细说明文字", "tag": "lark_md" }
    },
    {
      "tag": "hr"
    },
    {
      "tag": "action",
      "actions": [/* 按钮 */]
    }
  ]
}
```

### 2. 合理的按钮布局

- 每行最多 3-4 个按钮
- 主要操作使用 `primary` 类型
- 危险操作使用 `danger` 类型
- 取消操作使用 `default` 类型

### 3. 状态携带

在按钮的 `value` 中携带完整状态：

```json
{
  "tag": "button",
  "text": { "content": "确认删除", "tag": "plain_text" },
  "type": "danger",
  "value": {
    "action": "confirm_delete",
    "file_path": "/path/to/file.txt",
    "file_size": 1024,
    "timestamp": 1234567890
  }
}
```

这样回调处理时无需额外查询。

## 常见模式

### 确认对话框

```json
{
  "header": {
    "title": { "content": "⚠️ 确认操作", "tag": "plain_text" },
    "template": "orange"
  },
  "elements": [
    {
      "tag": "div",
      "text": { "content": "**确认执行此操作？**\n\n此操作不可撤销。", "tag": "lark_md" }
    },
    {
      "tag": "hr"
    },
    {
      "tag": "action",
      "actions": [
        {
          "tag": "button",
          "text": { "content": "✅ 确认", "tag": "plain_text" },
          "type": "danger",
          "value": { "action": "confirm" }
        },
        {
          "tag": "button",
          "text": { "content": "❌ 取消", "tag": "plain_text" },
          "type": "default",
          "value": { "action": "cancel" }
        }
      ]
    }
  ]
}
```

### 多选一

```json
{
  "header": {
    "title": { "content": "🎯 请选择", "tag": "plain_text" },
    "template": "blue"
  },
  "elements": [
    {
      "tag": "div",
      "text": { "content": "**请选择一个选项：**", "tag": "lark_md" }
    },
    {
      "tag": "hr"
    },
    {
      "tag": "action",
      "actions": [
        {
          "tag": "button",
          "text": { "content": "选项 A", "tag": "plain_text" },
          "type": "primary",
          "value": { "action": "select", "option": "A" }
        },
        {
          "tag": "button",
          "text": { "content": "选项 B", "tag": "plain_text" },
          "type": "primary",
          "value": { "action": "select", "option": "B" }
        },
        {
          "tag": "button",
          "text": { "content": "选项 C", "tag": "plain_text" },
          "type": "primary",
          "value": { "action": "select", "option": "C" }
        }
      ]
    }
  ]
}
```

### 进度追踪

```json
{
  "header": {
    "title": { "content": "📊 任务进度", "tag": "plain_text" },
    "template": "blue"
  },
  "elements": [
    {
      "tag": "div",
      "text": { "content": "**当前进度：** 2/5 已完成", "tag": "lark_md" }
    },
    {
      "tag": "hr"
    },
    {
      "tag": "div",
      "text": { "content": "✅ 任务 1 - 已完成", "tag": "lark_md" }
    },
    {
      "tag": "div",
      "text": { "content": "✅ 任务 2 - 已完成", "tag": "lark_md" }
    },
    {
      "tag": "div",
      "text": { "content": "⏳ 任务 3 - 进行中", "tag": "lark_md" }
    },
    {
      "tag": "div",
      "text": { "content": "⬜ 任务 4 - 待开始", "tag": "lark_md" }
    },
    {
      "tag": "div",
      "text": { "content": "⬜ 任务 5 - 待开始", "tag": "lark_md" }
    }
  ]
}
```

## 最佳实践

### 1. 使用 Emoji 增强可读性

- ✅ 成功/确认
- ❌ 失败/取消
- ⚠️ 警告
- 📊 数据/统计
- 📋 列表/清单
- 🎯 目标/选择
- ⏳ 进行中
- ⬜ 待完成

### 2. 文字简洁明确

- ❌ "是否要执行这个操作？"
- ✅ "确认删除文件？"

### 3. 防止误操作

- 危险操作使用 `danger` 类型
- 添加二次确认
- 在文字中说明后果

### 4. 响应式设计

- 使用 `wide_screen_mode: true` 适配宽屏
- 按钮文字不要太长
- 考虑移动端显示效果

## 限制和注意事项

1. **按钮数量**：每个 action 最多 5 个按钮
2. **文字长度**：按钮文字建议不超过 10 个字符
3. **嵌套深度**：避免过深的嵌套结构
4. **表单字段**：每个表单建议不超过 10 个字段
5. **卡片大小**：整个卡片 JSON 不要超过 30KB

## 调试技巧

### 1. 使用测试脚本

```bash
node scripts/send-card.js custom --template test-card.json --chat-id oc_xxx
```

### 2. 检查 JSON 格式

使用在线 JSON 验证工具检查格式是否正确。

### 3. 查看错误日志

飞书 API 会返回详细的错误信息，注意查看。

### 4. 渐进式开发

从简单的卡片开始，逐步添加复杂功能。
