# 快速开始指南

## 5 分钟上手

### 第一步：获取抖音 Cookie（2 分钟）

1. 打开浏览器，访问 https://www.douyin.com
2. 登录你的抖音账号
3. 按 F12 打开开发者工具
4. 点击 **Network**（网络）标签
5. 刷新页面（F5）
6. 在左侧请求列表中点击任意一个
7. 在右侧找到 **Request Headers**（请求头）
8. 复制 **cookie** 字段的全部内容

### 第二步：安装和配置（2 分钟）

```bash
# 1. 进入技能目录
cd douyin-auto-reply

# 2. 安装依赖（如果需要）
pip install requests

# 3. 设置你的抖音 cookie
python scripts/config_manager.py cookie "粘贴你刚才复制的 cookie"

# 4. 测试配置
python scripts/douyin_bot.py test
```

看到以下输出表示配置成功：
```
✓ 配置文件：True
✓ Cookie 配置：✓
✓ 关键词数量：10 个
```

### 第三步：自定义关键词（1 分钟）

查看默认关键词：
```bash
python scripts/config_manager.py list
```

添加你的自定义关键词：
```bash
# 格式：python scripts/config_manager.py add "关键词" "回复内容"

python scripts/config_manager.py add "多少钱" "价格已私信发送，请注意查收哦~ 💰"
python scripts/config_manager.py add "怎么买" "购买链接已私信，注意查看消息~ 📩"
```

### 第四步：启动自动回复

```bash
# 启动程序
python scripts/douyin_bot.py start
```

程序启动后会显示：
```
==================================================
抖音自动回复助手启动中...
每日限制：100 条
回复延迟：30 秒
==================================================
```

## 常用命令

### 查看状态
```bash
python scripts/douyin_bot.py status
```

### 查看配置
```bash
python scripts/config_manager.py show
```

### 查看数据分析报告
```bash
python scripts/analytics.py report
```

### 修改回复延迟
```bash
# 设置为 60 秒
python scripts/config_manager.py delay 60
```

### 修改每日限制
```bash
# 设置为 200 条
python scripts/config_manager.py limit 200
```

## 典型使用场景

### 场景 1：电商卖家
```bash
# 添加商品咨询关键词
python scripts/config_manager.py add "包邮吗" "亲，全国包邮哦~ 具体运费私信告诉您~ 📦"
python scripts/config_manager.py add "有优惠吗" "现在下单享 9 折~ 优惠券已私信发送！🎉"
```

### 场景 2：知识付费
```bash
# 添加课程咨询关键词
python scripts/config_manager.py add "课程" "课程详情和优惠已私信~ 前 10 名立减 100 元！📚"
python scripts/config_manager.py add "学习" "欢迎加入学习群~ 入群方式已私信~ 👥"
```

### 场景 3：品牌活动
```bash
# 添加活动咨询关键词
python scripts/config_manager.py add "抽奖" "已帮您登记~ 开奖结果私信通知~ 🍀"
python scripts/config_manager.py add "活动" "活动详情已私信~ 抽 3 人送免单！🎁"
```

## 注意事项

### ⚠️ 安全使用建议

1. **新号慎用** - 新注册账号建议先养号 1-2 周
2. **控制频率** - 建议回复延迟 30-60 秒
3. **限制数量** - 每日不超过 100-200 条
4. **内容多样** - 避免完全相同的回复
5. **定期更新** - Cookie 有效期 7-30 天

### 📊 建议配置

**保守配置（新号）：**
```bash
python scripts/config_manager.py delay 60
python scripts/config_manager.py limit 50
```

**标准配置（老号）：**
```bash
python scripts/config_manager.py delay 30
python scripts/config_manager.py limit 100
```

**激进配置（谨慎使用）：**
```bash
python scripts/config_manager.py delay 15
python scripts/config_manager.py limit 200
```

## 故障排查

### 问题：程序无法启动
```bash
# 测试配置
python scripts/douyin_bot.py test

# 如果提示 cookie 问题，重新设置
python scripts/config_manager.py cookie "新的 cookie"
```

### 问题：回复不生效
1. 检查 cookie 是否过期
2. 查看日志文件 `douyin_bot.log`
3. 确认关键词设置正确

### 问题：提示操作频繁
```bash
# 增加延迟时间
python scripts/config_manager.py delay 60

# 降低每日限制
python scripts/config_manager.py limit 50
```

## 获取帮助

### 查看完整文档
```bash
# API 文档
cat references/api_docs.md

# 故障排查
cat references/troubleshooting.md
```

### 查看日志
```bash
# 实时查看日志
tail -f douyin_bot.log

# 查看最近 100 行
tail -100 douyin_bot.log
```

## 下一步

- 📖 阅读完整文档：`references/api_docs.md`
- 📊 查看数据分析：`python scripts/analytics.py report`
- 🔧 高级配置：编辑 `config.json` 文件
- 💬 技术支持：查看 `assets/marketplace_listing.md` 中的联系方式

---

**祝你使用愉快！如有问题随时联系技术支持。** 🎉
