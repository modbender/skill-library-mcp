# 语义检查声明格式规范

## 触发条件
每次执行 semantic_check.py 后自动注入声明（由 message-injector 插件完成，无需手动输出）。

## 声明格式

### B分支（延续当前会话）
```
【语义检查】PX-延续｜模型池:【XXX池】｜实际模型:model-id
```

**示例：**
```
【语义检查】P2-延续｜模型池:【高速池】｜实际模型:claude-haiku-4.5
【语义检查】P2-延续｜模型池:【智能池】｜实际模型:claude-opus-4.6
```

### C分支（新会话 + 模型切换）
```
【语义检查】PX-任务描述｜新会话→XXX池｜实际模型:model-id
```

**示例：**
```
【语义检查】P1-执行开发任务｜新会话→智能池｜实际模型:claude-opus-4.6
【语义检查】P2-执行信息检索｜新会话→高速池｜实际模型:claude-haiku-4.5
【语义检查】P3-内容生成｜新会话→人文池｜实际模型:claude-sonnet-4.6
```

## 字段说明

| 字段 | 说明 |
|------|------|
| `PX` | 优先级：P1=开发/自动化/运维，P2=信息检索/协调，P3=内容生成/问答 |
| `模型池:【XXX池】` | 始终输出当前所属模型池中文名 |
| `实际模型:` | 始终输出当前实际调用的模型 ID 末段（去掉 provider 前缀） |
| `新会话→` | C分支专用，表示触发了 session reset |

## P等级映射

| P等级 | 任务类型 |
|-------|----------|
| P1 | development, automation, system_ops |
| P2 | info_retrieval, coordination, web_search, continue |
| P3 | content_generation, reading, q_and_a, training, multimodal |

## 实现机制

声明由 `message-injector` TypeScript 插件通过 `before_agent_start` hook 自动注入：
1. 调用 `semantic_check.py` 获取路由结果
2. B分支：不切换模型，声明显示当前池和模型
3. C分支：通过 `modelOverride`/`providerOverride` 100% 切换模型 + 调用 `sessions.reset` 创建新会话
