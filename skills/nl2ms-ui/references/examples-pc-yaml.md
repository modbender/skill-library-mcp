# PC 端 YAML 格式示例脚本

## 示例：发送消息脚本

```yaml
# PC端发送消息测试
# 注意：PC端主要使用TypeScript，YAML格式支持有限

pc:
  appName: "ME"
  restoreMinimized: true
  onlyForRect: false

agent:
  screenshotMode: "window"
  aiActionContext: "处理弹窗和权限请求"

tasks:
  - name: 搜索用户并进入聊天
    flow:
      - aiAction: 在应用界面中找到搜索框并点击它
        description: 点击搜索框
      - sleep: 1000
      - aiAction: 在搜索框中输入用户名
        description: 输入搜索内容
      - sleep: 2000
      - aiAction: 点击搜索结果中的目标用户
        description: 进入聊天界面

  - name: 发送消息
    flow:
      - aiAction: 在聊天界面的消息输入框中输入测试消息
        description: 输入消息内容
      - sleep: 1000
      - aiAction: 点击发送按钮发送消息
        description: 发送消息
      - sleep: 2000
      - aiOutput: 判断消息是否已成功发送并在聊天记录中显示
        description: 验证消息发送成功
```

## 支持的 PC 操作（YAML）

| 方法 | YAML 语法 | 说明 |
|------|-----------|------|
| 启动应用 | `pc: { appName: "应用名" }` | 启动应用窗口 |
| AI 操作 | `aiAction: "操作描述"` | AI 操作 |
| AI 输出/查询 | `aiOutput: "查询内容"` | AI 输出/查询 |
| 等待 | `sleep: 毫秒数` | 等待指定时间 |

**注意**：PC端主要使用TypeScript格式，YAML格式支持有限，建议优先使用TypeScript格式。
