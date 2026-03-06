# iOS 端 YAML 格式示例脚本

## 示例：发送消息脚本

```yaml
# iOS端单聊消息发送
ios:
  launch: com.testjdme
  wdaPort: 8100

agent:
  cache: true
  aiActionContext: "处理弹窗和权限请求。如果出现位置权限、用户协议等弹窗，点击同意。如果出现登录页面，请关闭它。"

tasks:
  - name: 搜索用户并进入聊天
    flow:

      - aiAction: 点击界面底部的‘消息‘
        description: 点击底部的消息tab

      - aiTap: 搜索
        description: 点击顶部搜索框

      - sleep: 3000

      - aiTap: 联系人
        description: 点击搜索联系人分类
      
      - aiAction: 在搜索框中输入'zhencuicui'
        locate: "搜索框"
        description: 在搜索框中输入zhencuicui
      
      - sleep: 3000
      
      - aiAssert: 搜索结果中显示甄翠翠
        description: 验证搜索结果包含目标用户
      
      - aiTap: 甄翠翠
        description: 点击搜索结果中的甄翠翠用户

  - name: 发送消息
    flow:
      
      - aiTap: 请输入消息
        description: 点击消息输入框获得焦点
      
      - aiInput: AI自动化测试
        locate: 请输入消息
        description: 在输入框中输入测试消息内容

      - aiTap: AI自动化测试
        description: 点击消息输入框获得焦点
      
      - aiTap: 发送
        description: 点击发送按钮发送消息
      
      - aiAssert: 消息"AI自动化测试"已发送成功
        description: 验证消息发送成功，在聊天记录中可见
      
      - aiAction: Back

      - sleep: 1000

      - aiAction: Back
```

## 支持的 iOS 操作（YAML）

| 方法 | YAML 语法 | 说明 |
|------|-----------|------|
| 启动应用 | `ios: { launch: "BundleID" }` | 启动应用 |
| 点击 | `aiTap: "按钮文本"` | 点击元素 |
| 输入 | `aiInput: "内容"`<br>`locate: "输入框"` | 输入文本 |
| 操作 | `aiAction: "操作描述"` | AI 操作 |
| 断言 | `aiAssert: "验证条件"` | 断言验证 |
| 查询 | `aiQuery: "查询内容"` | 查询信息 |
| 布尔判断 | `aiBoolean: "判断条件"` | 布尔判断 |
| 返回 | `aiAction: Back` | 返回上一页 |
| 等待 | `sleep: 毫秒数` | 等待指定时间 |
