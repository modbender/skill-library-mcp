---
name: ragflow-kb
description: RAGFlow知识库问答与操作指导。调用RAGFlow知识库API进行智能问答，并基于知识库返回结果提供agent操作建议。支持流式输出，耐心等待完整响应生成。当用户提出技术问题、故障排查、操作指导或需要知识库检索时触发此技能。适用于容器/Docker问题、系统运维、开发相关问题等场景。
---

# RAGFlow知识库问答Skill

## 概述

此skill通过调用RAGFlow知识库API，为用户提供智能问答和操作指导。**API使用流式输出（Stream）方式返回结果，需要耐心等待完整响应生成**（通常5-10秒）。

## 工作流程

### 步骤1: 识别问题类型

判断用户的问题是否适合通过知识库查询：
- 技术问题（容器、Docker、Kubernetes等）
- 系统运维问题
- 故障排查
- 操作指导
- 其他需要专业知识库的场景

### 步骤2: 调用RAGFlow API

使用`scripts/query_ragflow.py`脚本查询知识库：

**标准查询**（适合正常使用）：
```bash
python3 /home/onestack/.openclaw/workspace/ragflow-kb/scripts/query_ragflow.py "用户的问题"
```

**调试模式**（查看详细信息）：
```bash
python3 /home/onestack/.openclaw/workspace/ragflow-kb/scripts/query_ragflow.py "用户的问题" -v
# 或
python3 /home/onestack/.openclaw/workspace/ragflow-kb/scripts/query_ragflow.py "用户的问题" --verbose
```

### 步骤3: 等待流式响应

**重要提示**：
- RAGFlow API使用流式输出，响应需要时间生成
- 无新数据超时：**15秒**（给流式生成足够时间）
- 最大总超时：**60秒**
- 请求超时：**120秒**
- 通常5-10秒能完成，复杂问题可能更久

脚本会显示进度点（`.`）表示正在接收数据，请耐心等待。

### 步骤4: 处理返回结果

API返回结果包含：
- **助手回复**：完整的AI生成答案
- **引用文档**：知识库中相关的文档来源
- **统计信息**：处理行数、数据块数量、耗时

### 步骤5: 总结和操作建议

根据返回结果：
- **直接回答**: 如果是简单问题，直接总结答案
- **操作指导**: 如果问题涉及具体操作（如容器挂了），提供步骤化的操作建议
- **建议执行agent操作**: 如果建议使用其他agent工具，明确指出

## API配置

**基本信息**:
- API地址: `http://172.28.20.46:30001/v1/conversation/completion`
- 认证方式: Bearer token + Cookie session
- 输出方式: **Server-Sent Events (SSE) 流式输出**

**请求格式**:
- 方法: POST
- Content-Type: application/json

**关键参数**:
- `conversation_id`: 会话ID（使用固定ID保持对话上下文）
- `messages`: 对话历史数组，每个消息包含：
  - `role`: "user" 或 "assistant"
  - `content`: 消息内容
  - `id`: 消息唯一标识

## 使用示例

### 示例1: 容器故障排查
```
用户: 容器挂了怎么办
→ 调用API查询"容器挂了怎么办"
→ 等待约6秒，接收完整流式响应（94行数据）
→ 返回故障排查步骤并引用文档
→ 总结操作建议：直接删除容器，重新创建并加版本号
```

**实际执行**：
```bash
python3 /home/onestack/.openclaw/workspace/ragflow-kb/scripts/query_ragflow.py "容器挂了怎么办"

# 输出：
[查询] 容器挂了怎么办
.........................................................................
# 完整答案
如果容器挂了，你需要直接删除这个容器，然后重新创建一个新的容器，
并且给新容器的名字后缀加上一个版本号[ID:0]。

[引用文档]
- 运维测试文档.doc
--------------------------------------------------------------------------------
[成功] 查询完成 (耗时: 6.19秒)
```

### 示例2: 技术知识查询
```
用户: Docker网络模式有哪些？
→ 调用API查询"Docker网络模式"
→ 等待流式响应
→ 返回bridge、host、overlay等模式的说明
→ 总结并简要说明各模式特点
→ 如果知识库没相关内容，返回"知识库中未找到您要的答案！"
```

### 示例3: 需要执行agent操作
```
用户: 怎么查看容器日志？
→ 调用API查询"查看容器日志"
→ API返回使用docker logs命令的方法
→ 总结：使用`docker logs <container_name>`查看日志
→ 建议用户提供容器名称，使用exec工具执行命令
```

## 超时配置说明

脚本已针对流式输出优化超时配置：

| 参数 | 值 | 说明 |
|------|-----|------|
| `STREAM_NO_DATA_TIMEOUT` | 15秒 | 无新数据则认为完成（给流式生成足够时间） |
| `STREAM_MAX_TIMEOUT` | 60秒 | 最大总等待时间（防止无限等待） |
| 请求超时 | 120秒 | HTTP连接超时 |

**如果超时**：
1. 使用调试模式（-v）查看详细信息
2. 检查网络连接到RAGFlow服务器
3. 确认API服务状态

## 调试模式

使用`-v`或`--verbose`参数获取详细调试信息：

```bash
python3 /home/onestack/.openclaw/workspace/ragflow-kb/scripts/query_ragflow.py "测试问题" -v
```

调试信息包括：
- 完整的请求URL和参数
- 响应状态码
- 数据接收过程
- 处理的行数、数据块数量、耗时
- 完整的JSON响应

## 注意事项

1. **流式输出等待**: RAGFlow使用流式输出，需要耐心等待，不要提前终止
2. **会话管理**: conversation_id可以复用，保持对话上下文
3. **错误处理**: 如果API调用失败，检查网络连接和API服务状态
4. **结果总结**: 不要只是复制返回结果，要进行总结和提炼
5. **操作建议**: 当API返回包含操作步骤时，转化为可执行的命令或明确指引
6. **安全性**: API认证信息已固化在脚本中，注意不要泄露

## 扩展使用

对于需要agent执行的命令：
- 明确告知用户可以执行的命令
- 如果用户确认，使用exec工具执行
- 反馈执行结果

对于需要多次查询的复杂问题：
- 拆分为多个子问题
- 逐步查询和确认
- 最后整合完整答案

## 故障排查

### API请求失败
```bash
# 测试连接
curl -I http://172.28.20.46:30001/v1/conversation/completion

# 查看详细错误
python3 scripts/query_ragflow.py "测试" -v
```

### 认证失败
- 检查Authorization token是否过期
- 检查session cookie是否有效
- 查看HTTP状态码（401/403表示权限问题）

### 返回"知识库中未找到"
- 知识库确实没有相关内容
- 或者检索关键词匹配不上
- 尝试更换问题描述方式
