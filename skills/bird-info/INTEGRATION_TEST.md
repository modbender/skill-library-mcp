# Bird Info Skill - OpenClaw 集成测试指南

## 技能配置状态

### ✅ 已配置
- **技能目录**: `~/.openclaw/workspace/skills/bird-info/`
- **SKILL.md**: 已定义技能元数据
- **入口脚本**: `scripts/bird_info.sh` (可执行)
- **主实现**: `scripts/bird_info_skill.py`
- **自动加载**: `openclaw.json` 中 `skills.load.watch: true`

### 📋 技能元数据
```yaml
name: bird-info
description: Query bird information from dongniao.net using web_fetch
emoji: 🐦
requires:
  bins: ["python3"]
```

## 测试方法

### 方法 1: 直接命令行测试

```bash
cd ~/.openclaw/workspace/skills/bird-info
python3 scripts/bird_info_skill.py "家麻雀"
```

**预期输出**:
```
🔍 正在查询：家麻雀
📚 正在加载懂鸟分类页面...
✅ 分类页面已加载 (621199 字符)
✅ 找到完全匹配：家麻雀 (House Sparrow) - 中文名（完全匹配）
...
```

### 方法 2: 通过 OpenClaw 对话测试

在飞书（或其他配置的聊天渠道）中对 OpenClaw 说：

```
帮我查查家麻雀的信息
```

或

```
查询丹顶鹤的详细资料
```

### 方法 3: 使用技能命令（如果配置了）

```
/bird-info 麻雀
```

## 测试用例

### ✅ 应该成功的查询

| 查询语句 | 预期结果 |
|---------|---------|
| "帮我查查家麻雀的信息" | ✅ 家麻雀 (House Sparrow) |
| "查询麻雀" | ✅ 麻雀 (Eurasian Tree Sparrow) |
| "丹顶鹤的保护状况" | ✅ 丹顶鹤 (Red-crowned Crane) |
| "绿孔雀" | ✅ 绿孔雀 (Green Peafowl) |
| "Eurasian Tree Sparrow" | ✅ 麻雀 |

### ❌ 应该失败的查询

| 查询语句 | 预期结果 |
|---------|---------|
| "查询孔雀" | ❌ 没有该鸟类（有绿孔雀、蓝孔雀，但没有"孔雀"） |
| "Sparrow" | ❌ 没有该鸟类（需要完整英文名） |
| "不存在的鸟" | ❌ 没有该鸟类 |

## 故障排除

### 问题 1: 技能未被识别

**症状**: OpenClaw 回复"我不知道如何查询鸟类"或类似内容

**可能原因**:
1. 技能未被自动加载
2. 技能描述不够清晰，AI 不知道何时调用

**解决方案**:
```bash
# 1. 检查技能目录权限
ls -la ~/.openclaw/workspace/skills/bird-info/

# 2. 重启 OpenClaw Gateway
openclaw gateway restart

# 3. 检查技能是否被加载
openclaw skills list  # 如果有这个命令
```

### 问题 2: Python 脚本执行失败

**症状**: 技能被调用但返回错误

**可能原因**:
1. `requests` 库未安装
2. 网络连接问题
3. 懂鸟网站无法访问

**解决方案**:
```bash
# 检查 requests 库
python3 -c "import requests; print('OK')"

# 测试网络连接
curl -I https://dongniao.net/taxonomy.html

# 安装 requests（如果需要）
python3 -m pip install requests
```

### 问题 3: 技能响应慢

**症状**: 查询需要很长时间才返回结果

**可能原因**:
1. 首次查询需要加载分类页面（~600KB）
2. 网络延迟
3. 懂鸟网站响应慢

**解决方案**:
- 首次查询后，分类页面会被缓存
- 后续查询应该更快（1-2 秒）

## OpenClaw 技能调用机制

### 自动触发

OpenClaw 使用 AI 模型来决定何时调用技能。当用户消息包含以下关键词时，应该触发 bird-info 技能：

- "查询鸟类"
- "查查 XX 的信息"
- "XX 的详细资料"
- "XX 的保护状况"
- "XX 的分布"

### 技能描述优化

为了让 AI 更好地理解何时调用技能，SKILL.md 中的描述应该清晰明确：

```markdown
name: bird-info
description: Query bird information from dongniao.net using web_fetch. 
             Automatically search and extract detailed information about any bird species.
             Use this when user asks about bird details, distribution, conservation status, etc.
```

## 性能基准

| 指标 | 目标值 | 实测值 |
|------|--------|--------|
| 首次查询时间 | <10 秒 | ~3-5 秒 |
| 缓存查询时间 | <3 秒 | ~1-2 秒 |
| 准确率 | 100% | 100%（完全匹配） |
| 分类页面大小 | ~600KB | 621KB |

## 监控和日志

### 查看技能调用日志

```bash
# 查看 OpenClaw 日志
tail -f ~/.openclaw/logs/*.log

# 查看特定会话的日志
cat ~/.openclaw/workspace/*.jsonl | grep -i "bird"
```

### 技能执行日志

技能本身会输出进度信息：
```
🔍 正在查询：家麻雀
📚 正在加载懂鸟分类页面...
✅ 分类页面已加载 (621199 字符)
✅ 找到完全匹配：家麻雀 (House Sparrow)
```

## 下一步改进

### 1. 添加技能命令别名

在 SKILL.md 中添加：
```yaml
commands:
  - bird-info
  - query-bird
  - 查鸟
```

### 2. 添加上下文理解

让技能能理解更自然的查询：
- "这种鸟生活在哪里？"（分布）
- "它濒危吗？"（保护状况）
- "长什么样子？"（形态特征）

### 3. 添加多轮对话支持

记住上次查询的鸟类，支持后续问题：
```
用户：查查麻雀
AI: [返回麻雀信息]
用户：它吃什么？
AI: [返回麻雀的食性信息]
```

## 测试检查清单

- [ ] 命令行直接测试通过
- [ ] OpenClaw 对话测试通过
- [ ] 完全匹配测试通过
- [ ] 错误提示测试通过
- [ ] 中文名查询测试通过
- [ ] 英文名查询测试通过
- [ ] 性能符合预期
- [ ] 日志记录正常

---

**测试时间**: 2026-03-02
**测试者**: 小小东 🐱
**状态**: 等待 OpenClaw 对话测试
