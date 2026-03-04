# Web 端 YAML 格式示例脚本

## 示例：autobot首页功能验证

```yaml
web:
  url: "https://dataagent.jd.com/#/dataagent/index"
  viewportWidth: 1358
  viewportHeight: 992
tasks:
  - name: "点击新建智能体按钮"
    flow:
      - click: "新建智能体"
      - sleep: 2000
      - aiAssert: "进入智能体创建页面"

  - name: "验证智能体创建页面基础元素"
    flow:
      - aiAssert: "页面显示 '未命名智能体' 标题"
      - aiAssert: "页面显示 '未上线' 状态"
      - aiAssert: "左侧显示导航菜单：体验、智能体、数据源、数据集"
      - aiAssert: "页面包含 '基本信息' 配置区域"
      - aiAssert: "页面包含 'PC端基础设置' 区域"
      - sleep: 1000

  - name: "测试基本信息配置"
    flow:
      - aiAssert: "显示 '应用名称' 输入框，占位符为 '请输入'"
      - type:
          selector: "input[placeholder='请输入']"
          text: "测试销售数据分析师"
      - aiAssert: "显示 '应用简介' 文本域"
      - type:
          selector: "textarea[placeholder='请输入']"
          text: "专业的销售数据分析智能体，提供深度数据洞察和报告生成服务"
      - sleep: 1000

  - name: "验证数据分析能力配置区域"
    flow:
      - aiAssert: "页面显示 '数据分析能力配置' 区域"
      - aiAssert: "包含 '数据问数' 选项"
      - aiAssert: "包含 '智能报告' 选项"
      - click: "数据问数"
      - sleep: 500
      - click: "智能报告"
      - sleep: 1000

  - name: "测试头像配置功能"
    flow:
      - aiAssert: "页面显示 '头像配置' 区域"
      - aiAssert: "显示 '选择头像' 提示"
      - aiAssert: "显示头像上传区域，包含 '+' 图标"
      - aiAssert: "显示 '选择' 按钮"
      - click: "选择"
      - sleep: 2000

  - name: "验证其他配置区域"
    flow:
      - aiAssert: "页面显示 '其他配置' 区域"
      - aiAssert: "包含 '帮助文档地址' 输入项"
      - sleep: 1000

  - name: "测试预览功能"
    flow:
      - aiAssert: "右侧显示 '预览' 区域"
      - aiAssert: "预览区显示智能体头像"
      - aiAssert: "显示 'Hi, ~我是应用名称' 问候语"
      - aiAssert: "显示 '应用简介' 文本"
      - aiAssert: "预览区包含发送按钮和输入框"
      - sleep: 1000

  - name: "验证左侧导航功能"
    flow:
      - aiAssert: "左侧导航显示 '基本信息' 选项"
      - aiAssert: "显示 '数据仓配置' 选项"
      - aiAssert: "显示 '预构内容配置' 选项"
      - click: "数据仓配置"
      - sleep: 1000
      - aiAssert: "切换到数据仓配置页面"

  - name: "测试表单验证功能"
    flow:
      - click: "基本信息"
      - sleep: 1000
      - clear: "input[placeholder='请输入']"
      - aiAssert: "应用名称为必填项，显示验证提示"
      - type:
          selector: "input[placeholder='请输入']"
          text: "销售数据分析师"
      - sleep: 1000

  - name: "测试智能体配置保存"
    flow:
      - aiAssert: "所有必填项已填写完成"
      - aiAssert: "页面配置项显示正常"
      - aiAssert: "预览效果符合预期"
      - sleep: 1000

  - name: "验证页面响应式和交互"
    flow:
      - aiAssert: "页面布局响应式设计正常"
      - aiAssert: "所有输入框和按钮可正常交互"
      - aiAssert: "预览区实时更新配置内容"
      - aiAssert: "页面加载和切换流畅"
      - sleep: 1000

  - name: "测试智能体列表页面功能"
    flow:
      - aiAssert: "智能体列表显示已创建的智能体"
      - aiAssert: "包含 '文件创建数据集', '评测数据分析师', '销售数据分析师【体验】' 等智能体"
      - aiAssert: "每个智能体显示状态：已上线/公共"
      - aiAssert: "显示创建者和更新时间信息"
      - aiAssert: "包含编辑和更多操作按钮"
      - sleep: 1000
```

## 支持的 Web 操作（YAML）

| 操作 | YAML 语法 | 说明 |
|------|-----------|------|
| 导航 | `navigate: { url: "URL" }` | 打开指定 URL |
| AI 点击 | `aiTap: "按钮文本"` | AI 驱动的点击操作（推荐） |
| 点击 | `click: "按钮文本"` | 直接点击指定文本的元素 |
| AI 输入 | `aiInput: { locate: "输入框", value: "内容" }` | AI 驱动的输入操作（推荐） |
| 输入 | `type: { selector: "选择器", text: "内容" }` | 使用选择器直接输入文本 |
| 清空 | `clear: "选择器"` | 清空指定输入框内容 |
| 断言 | `aiAssert: "验证条件"` | 验证页面状态 |
| 查询 | `aiQuery: { query: "查询", type: "string" }` | 提取页面信息 |
| 等待 | `aiWaitFor: "等待条件"` | 等待指定条件 |
| 悬停 | `aiHover: "元素"` | 鼠标悬停 |
| 滚动 | `aiScroll: { direction: "down" }` | 滚动页面 |
| 键盘 | `aiKeyboardPress: { key: "Enter" }` | 按下键盘按键 |
| 截图 | `screenshot: { path: "路径" }` | 保存截图 |
| 等待 | `sleep: 1000` | 等待指定毫秒 |
