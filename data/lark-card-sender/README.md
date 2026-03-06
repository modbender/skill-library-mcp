# 🎯 飞书卡片发送器 (Feishu Card Sender)

专业级飞书interactive卡片发送解决方案，绕过OpenClaw限制，直接调用飞书OpenAPI。

## ✨ 核心特性

- **🔧 完整API支持**: 直接调用飞书OpenAPI，支持所有卡片类型
- **📋 Schema 2.0标准**: 严格遵循飞书interactive卡片规范
- **🎨 丰富模板库**: 新闻简报、机票特价、任务管理等多种预设模板
- **⚡ 智能错误处理**: 完整的异常捕获和错误码处理机制
- **📊 大小自动验证**: 30KB限制自动检测，避免发送失败
- **🔑 Token自动管理**: tenant_access_token自动获取和缓存
- **👥 群组/单聊支持**: 同时支持群组和一对一私人消息

## 🚀 快速开始

### 1. 安装
```bash
# 克隆或下载技能包
cd skills/feishu-card-sender

# 运行安装脚本
./scripts/install.sh

# 设置环境变量
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
```

### 2. 基础使用
```python
# 导入发送器
from feishu_card_sender_advanced import AdvancedFeishuCardSender

# 初始化发送器
sender = AdvancedFeishuCardSender()

# 发送简单卡片
result = sender.send_simple_card(
    receive_id="ou_xxx",  # 用户open_id
    receive_id_type="open_id",
    title="🎉 欢迎使用",
    content="**飞书卡片**发送成功！"
)

print(f"消息ID: {result['message_id']}")
```

### 3. 高级功能
```python
# 发送新闻简报
news_items = [
    {"category": "🌍 国际新闻", "title": "重大科技突破", "source": "路透社", "time": "2小时前"},
    {"category": "💰 财经动态", "title": "市场分析", "source": "财经网", "time": "1小时前"}
]

result = sender.send_news_card(
    receive_id="oc_xxx",  # 群组chat_id
    receive_id_type="chat_id",
    news_items=news_items
)

# 发送机票特价信息
flight_info = {
    "route": "上海浦东 ✈️ 东京成田",
    "price": 899,
    "original_price": 2500,
    "date": "2024年3月15日",
    "discount": "3.6折 💰",
    "valid_until": "3月1日 23:59",
    "book_advance": "建议提前30天",
    "refund_policy": "免费改期一次",
    "booking_url": "https://example.com/book"
}

result = sender.send_flight_deal_card(
    receive_id="ou_xxx",
    receive_id_type="open_id",
    flight_info=flight_info
)
```

## 📋 支持的卡片类型

### 📰 新闻简报卡片
- 多段落布局，支持时间线
- 来源标注，分类清晰
- 分隔线组织，层次明确

### ✈️ 机票特价卡片
- 双列字段布局，信息对比明显
- 价格突出显示，优惠力度清晰
- 预订按钮集成，一键直达

### 📊 任务管理卡片
- 进度状态指示，完成情况一目了然
- 优先级颜色标识，重要程度分明
- 截止时间提醒，时间管理有效

### 🎯 基础信息卡片
- 简洁标题+内容，信息传达直接
- 多种主题颜色，视觉区分明显
- 灵活内容布局，适应各种场景

### 🖥️ 系统状态卡片
- 实时状态展示，系统健康透明
- 彩色模板区分，异常状态醒目
- 详细参数显示，技术信息完整

### 🎮 交互式卡片
- 按钮+选择器，用户交互友好
- 多种按钮类型，功能区分明确
- 动作响应支持，业务流程完整

## 🛠️ 核心工具

### 高级发送器 (`feishu_card_sender_advanced.py`)
- ✅ 完整的错误处理和重试机制
- ✅ 自动token缓存和管理
- ✅ 卡片大小验证（30KB限制）
- ✅ 多种预设发送方法
- ✅ 详细的错误信息和建议

### 模板库 (`feishu_card_templates.py`)
- ✅ 标准化卡片模板
- ✅ 可复用的构建函数
- ✅ 预设样式和布局
- ✅ 灵活的参数配置

### 集成指南 (`feishu_card_integration_guide.md`)
- ✅ 详细的集成步骤
- ✅ 现有系统升级指南
- ✅ 最佳实践建议
- ✅ 常见问题解决方案

## ⚡ 性能特性

- **🚀 快速发送**: 平均响应时间 < 500ms
- **💾 智能缓存**: Token自动缓存2小时
- **🔄 错误重试**: 内置重试机制，提高成功率
- **📊 大小优化**: 自动压缩和大小验证
- **🔒 安全传输**: HTTPS加密通信

## 🎨 设计指南

### 颜色主题
- `blue`: 蓝色主题（信息类）
- `green`: 绿色主题（成功类）
- `red`: 红色主题（警告类）
- `yellow`: 黄色主题（提醒类）
- `watchet`: 浅蓝色主题（中性类）

### 内容格式
- 支持完整的Markdown语法
- 支持@用户和@所有人
- 支持超链接和代码块
- 支持emoji图标增强视觉效果

### 布局建议
- 标题简洁明了（不超过30字）
- 内容层次清晰，重点突出
- 按钮操作明确，文案具体
- 整体大小控制在30KB以内

## 🔍 错误处理

常见错误及解决方案：

| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| 230013 | 用户不在应用可用范围内 | 检查应用权限设置，确认用户范围 |
| 230002 | 机器人不在群组中 | 将机器人添加到目标群组 |
| 230006 | 应用未开启机器人能力 | 在开发者后台开启机器人能力 |
| 230020 | 触发频率限制 | 降低发送频率，最大5QPS |
| 230025 | 内容超出长度限制 | 简化内容，控制在30KB以内 |
| 230099 | JSON格式错误 | 检查卡片结构是否符合规范 |

## 📚 相关资源

- [飞书API文档](https://open.larkoffice.com/document/server-docs/im-v1/message/create)
- [Interactive卡片格式](https://open.larkoffice.com/document/uAjLw4CM/ukTMukTMukTM/im-v1/message/create_json)
- [OpenClaw飞书扩展](https://github.com/openclaw/openclaw/tree/main/extensions/feishu)

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个技能包！

### 开发环境
```bash
# 安装开发依赖
pip install requests pytest

# 运行测试
python -m pytest tests/

# 代码格式化
black *.py
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 感谢飞书开放平台提供的优秀API
- 感谢OpenClaw社区的贡献者们
- 感谢所有使用和改进这个技能包的朋友们

---

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**