# 故障排查指南

## 常见问题及解决方案

### 1. 程序无法启动

#### 问题：提示"配置文件不存在"
**解决方案：**
```bash
# 运行测试模式自动创建配置
python scripts/douyin_bot.py test

# 或手动创建 config.json
python scripts/config_manager.py show
```

#### 问题：提示"未配置抖音 cookie"
**解决方案：**
1. 登录抖音网页版
2. 复制浏览器 cookie
3. 运行命令设置：
```bash
python scripts/config_manager.py cookie "你的 cookie"
```

### 2. 回复功能异常

#### 问题：评论获取失败
**可能原因：**
- Cookie 已失效
- 网络问题
- API 接口变更

**解决方案：**
1. 更新 cookie
2. 检查网络连接
3. 查看日志文件 `douyin_bot.log`

#### 问题：回复发送失败
**可能原因：**
- 账号被限制
- 回复频率过高
- 内容包含敏感词

**解决方案：**
1. 降低回复频率（增加 delay）
2. 减少每日回复上限
3. 检查黑名单设置

### 3. 性能问题

#### 问题：程序运行缓慢
**解决方案：**
```bash
# 增加检查间隔
# 编辑 config.json，修改相关参数
"reply_delay": 60,      # 增加到 60 秒
"daily_limit": 50       # 降低到 50 条
```

#### 问题：日志文件过大
**解决方案：**
```bash
# 定期清理日志
> douyin_bot.log

# 或修改日志级别
# 编辑 douyin_bot.py，将 level 改为 WARNING
```

### 4. 关键词匹配问题

#### 问题：关键词不触发回复
**可能原因：**
- 关键词设置错误
- 评论内容包含特殊字符
- 大小写问题

**解决方案：**
```bash
# 查看当前关键词
python scripts/config_manager.py list

# 添加新关键词
python scripts/config_manager.py add "新关键词" "回复内容"

# 删除无效关键词
python scripts/config_manager.py remove "无效关键词"
```

### 5. 数据统计问题

#### 问题：统计数据不准确
**解决方案：**
```bash
# 查看统计报告
python scripts/analytics.py report

# 清空统计数据重新开始
python scripts/analytics.py clear
```

## 日志分析

### 日志位置
```
douyin_bot.log
```

### 常见日志信息

| 日志内容 | 含义 | 处理 |
|---------|------|------|
| 获取到 0 条评论 | 正常，暂无新评论 | 无需处理 |
| 评论包含黑名单词汇 | 评论被跳过 | 检查黑名单设置 |
| 已达到每日回复上限 | 今日回复已达限制 | 等待次日或增加限制 |
| Cookie 验证失败 | 认证失效 | 更新 cookie |
| 网络请求超时 | 网络问题 | 检查网络连接 |

### 日志级别说明

- **INFO**: 正常操作信息
- **WARNING**: 警告信息，不影响运行
- **ERROR**: 错误信息，需要处理
- **DEBUG**: 调试信息（默认不显示）

## 恢复步骤

### 完全重置

如果问题无法解决，可以完全重置：

```bash
# 1. 备份当前配置
cp config.json config.json.bak
cp stats.json stats.json.bak

# 2. 删除配置文件
rm config.json stats.json

# 3. 重新生成配置
python scripts/douyin_bot.py test

# 4. 重新设置 cookie
python scripts/config_manager.py cookie "你的 cookie"

# 5. 启动程序
python scripts/douyin_bot.py start
```

## 获取帮助

### 查看帮助信息
```bash
python scripts/douyin_bot.py
python scripts/config_manager.py
python scripts/analytics.py
```

### 检查系统状态
```bash
# 测试配置
python scripts/douyin_bot.py test

# 查看统计
python scripts/douyin_bot.py status

# 分析报告
python scripts/analytics.py report
```

## 预防措施

1. **定期更新 cookie** - 每 7-15 天更新一次
2. **监控回复数量** - 避免超过平台限制
3. **备份配置文件** - 定期备份重要配置
4. **查看日志** - 每天检查日志文件
5. **更新关键词** - 根据实际效果优化关键词

## 联系支持

如遇到无法解决的问题：

1. 收集日志文件 `douyin_bot.log`
2. 记录问题发生时间和操作步骤
3. 保存配置文件（移除敏感信息）
4. 提交问题反馈
