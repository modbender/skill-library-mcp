# Android 端 YAML 格式示例脚本

## 示例：发送消息脚本

```yaml
# Android端单聊消息发送
android:
  launch: "com.jd.oa"

agent:
  cache: true
  aiActionContext: "处理弹窗和权限请求。如果出现位置权限、用户协议等弹窗，点击同意。如果出现登录页面，请关闭它。"

tasks:
  - name: 搜索用户并进入聊天
    flow:

      - sleep: 8000
      - aiAction: 点击消息
        description: 点击底部的消息tab

      - aiTap: 搜索
        description: 点击顶部搜索框
      
      - aiInput: "zhencuicui"
        locate: "搜索框"
        description: 在搜索框中输入用户名zhencuicui
      
      - sleep: 3000
      
      - aiAssert: 搜索结果中显示甄翠翠
        description: 验证搜索结果包含目标用户
      
      - aiTap: "甄翠翠"
        description: 点击搜索结果中的甄翠翠用户

  - name: 发送消息
    flow:
      
      - aiTap: 消息输入框
        description: 点击消息输入框获得焦点
      
      - aiInput: "AI自动化测试"
        locate: "消息输入框"
        description: 在输入框中输入测试消息内容
      
      - aiTap: 发送
        description: 点击发送按钮发送消息
      
      - aiAssert: 消息"AI自动化测试"已发送成功
        description: 验证消息发送成功，在聊天记录中可见
      
      - aiAction: AndroidBackButton

      - sleep: 1000

      - aiAction: AndroidBackButton
```

## 支持的 Android 操作（YAML）

| 操作 | YAML 语法 | 说明 |
|------|-----------|------|
| 点击 | `aiTap: "按钮文本"` | 点击指定文本的元素 |
| 输入 | `aiInput: "内容"`<br>`locate: "输入框定位"` | 在指定输入框输入内容 |
| 操作 | `aiAction: "操作描述"` | AI 驱动的复杂操作 |
| 断言 | `aiAssert: "验证条件"` | 验证页面状态 |
| 查询 | `aiQuery: "查询内容"` | 提取页面信息 |
| 启动应用 | `android: { launch: "包名" }` | 启动指定应用 |
| 返回 | `aiAction: AndroidBackButton` | 触发系统返回键 |
| 等待 | `sleep: 毫秒数` | 等待指定时间 |
