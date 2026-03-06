# RAGFlow Skill 故障排查指南

## 快速诊断

```bash
# 运行快速诊断工具
python3 /home/onestack/.openclaw/workspace/ragflow-kb/scripts/quick_test.py
```

---

## 常见问题与解决方案

### 问题1: 查询一直不结束（流式输出持续输出点）

**症状**：
```
[查询] Docker的基本概念
..............................................................................
(一直输出，长时间不结束)
```

**原因**：
- RAGFlow正在生成较长的回答
- 话题复杂，知识库匹配内容多
- 正常现象，但可能超过60秒最大超时

**解决方案**：

**方案1：使用简单问题**
```bash
# 建议：使用更具体、简短的问题
python3 scripts/query_ragflow.py "容器挂了怎么办"  # ✅ 快速
python3 scripts/query_ragflow.py "Docker基本概念"   # ⚠️ 可能很慢
```

**方案2：调整超时时间**
```bash
# 编辑脚本，找到这一行（约第26行）：
STREAM_MAX_TIMEOUT = 60.0  # 改为 120.0 或更长

# 或者
STREAM_NO_DATA_TIMEOUT = 15.0  # 改为 30.0
```

**方案3：手动中断**
```bash
# 按 Ctrl+C 手动停止
# 检查是否已经收到部分答案
```

---

### 问题2: API连接失败

**症状**：
```
[错误] API请求失败: Connection refused
或
[错误] API请求失败: Timeout
```

**诊断**：
```bash
# 测试网络连通性
curl -I http://172.28.20.46:30001

# 运行诊断工具
python3 scripts/quick_test.py
```

**解决方案**：

1. **检查API服务启动**
```bash
# 在RAGFlow服务器上检查服务
systemctl status ragflow
# 或
docker ps | grep ragflow
```

2. **检查防火墙**
```bash
# 测试端口开放
telnet 172.28.20.46 30001

# 或
nc -zv 172.28.20.46 30001
```

3. **检查网络**
```bash
ping 172.28.20.46
traceroute 172.28.20.46
```

---

### 问题3: 认证失败

**症状**：
```
[错误] API请求失败: 401 Client Error: Unauthorized
或
[错误] API请求失败: 403 Client Error: Forbidden
```

**原因**：
- Token或Cookie过期
- 认证信息错误

**解决方案**：

1. **更新认证信息**
```bash
# 编辑脚本，找到第10-12行：
AUTHORIZATION = "你的新token"
COOKIE = "session=你的新cookie"
```

2. **重新登录获取认证信息**
- 登录RAGFlow Web界面
- 打开浏览器开发者工具（F12）
- Network 标签查找API请求
- 复制请求头中的 Authorization 和 Cookie

---

### 问题4: 返回"知识库中未找到您要的答案！"

**原因**：
- 知识库确实没有相关内容
- 关键词匹配不上

**解决方案**：

1. **尝试不同的问法**
```bash
# 原问题
python3 scripts/query_ragflow.py "Docker网络模式"

# 改用更口语化
python3 scripts/query_ragflow.py "Docker有哪些网络"
```

2. **使用调试模式查看匹配过程**
```bash
python3 scripts/query_ragflow.py "你的问题" -v
# 查看是否检索到相关文档
```

3. **更新知识库**
- 在RAGFlow中上传更全面的文档
- 确保文档包含你关心的内容

---

### 问题5: 代码错误

**症状**：
```
Traceback (most recent call last):
  ...
ModuleNotFoundError: No module named 'requests'
```

**解决方案**：

```bash
# 安装依赖
pip3 install requests

# 验证安装
python3 -c "import requests; print(requests.__version__)"
```

---

## 调试技巧

### 1. 使用调试模式

```bash
# 查看详细的请求/响应信息
python3 scripts/query_ragflow.py "测试问题" -v

# 或
python3 scripts/query_ragflow.py "测试问题" --verbose
```

### 2. 检查原始响应

```bash
# 使用curl直接测试（不处理流式）
curl -X POST http://172.28.20.46:30001/v1/conversation/completion \
  -H "Authorization: 你的token" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=你的cookie" \
  -d '{"conversation_id":"0e18393f0b6042f2bbf6b391c82835d1","messages":[{"role":"user","content":"测试"}]}'
```

### 3. 查看网络抓包

```bash
# 监控API调用
tcpdump -i any host 172.28.20.46 and port 30001
```

---

## 性能优化建议

### 1. 简化问题

**不好**：
```bash
python3 scripts/query_ragflow.py "详细解释Docker的架构、组件、工作原理、网络模式、存储驱动以及容器生命周期管理"
```

**好**：
```bash
python3 scripts/query_ragflow.py "Docker容器生命周期管理"
```

### 2. 使用关键词

**不好**：
```bash
python3 scripts/query_ragflow.py "如果我的程序运行的时候出问题了怎么办"
```

**好**：
```bash
python3 scripts/query_ragflow.py "容器挂了怎么处理"
```

### 3. 分步骤查询

对于复杂问题，拆分成多个简单查询：

```bash
# 步骤1
python3 scripts/query_ragflow.py "Docker网络有几种模式"

# 步骤2
python3 scripts/query_ragflow.py "bridge网络模式特点"
```

---

## 超时配置说明

脚本中有3个超时参数可根据需要调整：

| 参数 | 位置 | 默认值 | 说明 |
|------|------|--------|------|
| `STREAM_MAX_TIMEOUT` | 第26行 | 60秒 | 最大总等待时间 |
| `STREAM_NO_DATA_TIMEOUT` | 第25行 | 15秒 | 无新数据超时 |
| 请求超时 | 第102行 | 120秒 | HTTP连接超时 |

**修改示例**：
```python
# 编辑 scripts/query_ragflow.py

# 等待更长的时间（适合复杂问题）
STREAM_MAX_TIMEOUT = 120.0
STREAM_NO_DATA_TIMEOUT = 30.0

# 或快速失败（适合简单问题）
STREAM_MAX_TIMEOUT = 30.0
STREAM_NO_DATA_TIMEOUT = 5.0
```

---

## 获取帮助

### 1. 查看脚本说明

```bash
python3 scripts/query_ragflow.py --help
```

### 2. 运行完整诊断

```bash
# 运行全套诊断
python3 scripts/quick_test.py

# 或使用bash脚本
bash scripts/test_api.sh
```

### 3. 查看日志

```bash
# 启用详细日志
python3 scripts/query_ragflow.py "测试" -v > debug.log 2>&1

# 查看日志
cat debug.log
```

---

## 总结

| 问题类型 | 诊断工具 | 解决方案 |
|----------|----------|----------|
| 查询太慢 | `quick_test.py` | 简化问题或调整超时 |
| 连接失败 | `curl -I` | 检查API服务和网络 |
| 认证失败 | 查看HTTP状态码 | 更新token/cookie |
| 无相关答案 | 调试模式 | 更改问法或更新知识库 |
| 代码错误 | 查看错误信息 | 安装依赖 |

---

**记住**：
1. 先用 `quick_test.py` 快速诊断
2. 简单问题响应更快
3. 复杂问题可以拆分查询
4. 使用 `-v` 调试模式查看详情
