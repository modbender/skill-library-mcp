# 飞书卡片集成指南

## 🚀 快速集成步骤

### 1. 环境准备
```bash
# 设置飞书应用凭证
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"

# 验证权限
python3 -c "import os; print('APP_ID:', os.getenv('FEISHU_APP_ID')[:10]+'...')"
```

### 2. 基础集成
```python
# 导入发送器
from feishu_card_sender_advanced import AdvancedFeishuCardSender

# 初始化
sender = AdvancedFeishuCardSender()

# 发送简单卡片
result = sender.send_simple_card(
    receive_id="ou_xxx",  # 用户open_id
    receive_id_type="open_id",
    title="🎉 欢迎使用",
    content="**飞书卡片**发送成功！"
)
```

### 3. 高级功能集成
```python
# 新闻简报
news_items = [
    {"category": "科技", "title": "AI突破", "source": "TechNews", "time": "15:30"},
    {"category": "财经", "title": "市场分析", "source": "财经网", "time": "14:20"}
]

result = sender.send_news_card(
    receive_id="oc_xxx",  # 群组chat_id
    receive_id_type="chat_id",
    news_items=news_items
)

# 机票特价
flight_info = {
    "route": "上海 → 东京",
    "price": 899,
    "original_price": 2500,
    "date": "2024-03-15",
    "discount": "3.6折",
    "valid_until": "2024-03-01",
    "book_advance": 30,
    "refund_policy": "可免费改期",
    "booking_url": "https://example.com/book"
}

result = sender.send_flight_deal_card(
    receive_id="ou_xxx",
    receive_id_type="open_id",
    flight_info=flight_info
)
```

## 📋 现有系统升级指南

### 新闻推送系统升级
```python
# 原代码（文本消息）
def send_news_text(news_items):
    text = "📰 今日新闻\n"
    for item in news_items:
        text += f"• [{item['category']}] {item['title']}\n"
    return text

# 升级后（卡片消息）
def send_news_card(news_items):
    from feishu_card_sender_advanced import AdvancedFeishuCardSender
    sender = AdvancedFeishuCardSender()
    
    return sender.send_news_card(
        receive_id="ou_xxx",
        receive_id_type="open_id", 
        news_items=news_items
    )
```

### 机票提醒系统升级
```python
# 原代码（文本消息）
def send_flight_text(flight):
    return f"✈️ 特价机票：{flight['route']} ¥{flight['price']} (原价¥{flight['original_price']})"

# 升级后（卡片消息）
def send_flight_card(flight):
    from feishu_card_sender_advanced import AdvancedFeishuCardSender
    sender = AdvancedFeishuCardSender()
    
    return sender.send_flight_deal_card(
        receive_id="ou_xxx",
        receive_id_type="open_id",
        flight_info=flight
    )
```

### 任务提醒系统升级
```python
# 原代码（文本消息）
def send_task_text(tasks):
    text = "📋 今日任务\n"
    for task in tasks:
        status = "✅" if task['completed'] else "⏳"
        text += f"{status} {task['title']}\n"
    return text

# 升级后（卡片消息）
def send_task_card(tasks):
    from feishu_card_sender_advanced import AdvancedFeishuCardSender
    sender = AdvancedFeishuCardSender()
    
    return sender.send_task_management_card(
        receive_id="ou_xxx",
        receive_id_type="open_id",
        tasks=tasks
    )
```

## 🎨 卡片设计最佳实践

### 1. 新闻类卡片
```python
# 最佳实践
news_items = [
    {
        "category": "🌍 国际新闻",
        "title": "重大科技突破：AI领域新进展",
        "source": "路透社",
        "time": "2小时前"
    },
    {
        "category": "💰 财经动态", 
        "title": "市场分析：科技股表现强劲",
        "source": "财经网",
        "time": "1小时前"
    }
]

# 使用emoji增强视觉效果
# 时间显示相对时间更友好
# 分类信息清晰明确
```

### 2. 机票类卡片
```python
# 最佳实践
flight_info = {
    "route": "上海浦东 ✈️ 东京成田",
    "price": 899,
    "original_price": 2500,
    "date": "2024年3月15日",
    "discount": "3.6折 💰",
    "valid_until": "3月1日 23:59",
    "book_advance": "建议提前30天",
    "refund_policy": "免费改期一次",
    "booking_url": "https://booking.example.com/xxx"
}

# 使用emoji增强关键信息
# 价格对比突出优惠力度
# 时间信息具体明确
# 提供明确的行动指引
```

### 3. 任务类卡片
```python
# 最佳实践
tasks = [
    {
        "title": "完成飞书卡片技能开发",
        "status": "completed",
        "priority": "high",
        "deadline": "2024-02-28"
    },
    {
        "title": "集成新闻推送系统",
        "status": "in_progress", 
        "priority": "medium",
        "deadline": "2024-02-29"
    }
]

# 状态图标清晰可辨
# 优先级颜色区分明显
# 截止时间具体明确
# 进度统计一目了然
```

## ⚠️ 常见问题解决

### 1. 权限问题
```python
# 错误：230013 - 用户不在应用可用范围内
# 解决方案：
# 1. 检查应用权限设置
# 2. 确认用户是否在可用范围内
# 3. 联系管理员添加权限
```

### 2. 频率限制
```python
# 错误：230020 - 触发频率限制
# 解决方案：
# 1. 降低发送频率（最大5QPS）
# 2. 实现消息队列和重试机制
# 3. 批量发送时添加延迟
```

### 3. 大小限制
```python
# 错误：230025 - 消息内容超出长度限制
# 解决方案：
# 1. 简化卡片内容
# 2. 减少新闻条数（建议3-5条）
# 3. 使用更简洁的表达方式
```

### 4. JSON格式错误
```python
# 错误：230099 - JSON解析错误
# 解决方案：
# 1. 检查卡片结构是否符合规范
# 2. 确保所有必需字段都存在
# 3. 验证JSON格式有效性
```

## 🚀 性能优化建议

### 1. Token缓存
```python
# 发送器自动处理token缓存
# 无需每次重新获取
sender = AdvancedFeishuCardSender()
# token会自动缓存2小时
```

### 2. 批量发送
```python
# 批量发送时添加适当延迟
import time

for user in users:
    sender.send_simple_card(user_id, "open_id", title, content)
    time.sleep(0.2)  # 避免触发频率限制
```

### 3. 错误重试
```python
# 实现简单的重试机制
max_retries = 3
for attempt in range(max_retries):
    try:
        result = sender.send_interactive_card(...)
        break
    except Exception as e:
        if attempt < max_retries - 1:
            time.sleep(1)  # 等待1秒后重试
        else:
            raise e
```

## 📊 监控和日志

### 1. 发送记录
```python
# 记录发送结果
result = sender.send_news_card(...)
if result['success']:
    print(f"✅ 发送成功: {result['message_id']}")
    # 记录到数据库或日志文件
else:
    print(f"❌ 发送失败: {result.get('error')}")
    # 记录错误信息用于分析
```

### 2. 性能监控
```python
# 监控发送耗时
import time

start_time = time.time()
result = sender.send_interactive_card(...)
end_time = time.time()

print(f"发送耗时: {end_time - start_time:.2f}秒")
```

## 🎯 下一步优化方向

1. **模板库扩展**: 增加更多行业和应用场景的模板
2. **交互功能**: 实现按钮点击后的响应处理
3. **个性化定制**: 根据用户偏好调整卡片样式
4. **数据分析**: 收集卡片打开率和用户反馈
5. **多语言支持**: 支持中英文双语卡片

---

**集成状态**: ✅ 生产就绪  
**维护建议**: 定期检查飞书API更新，及时适配新功能