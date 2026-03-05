---
name: feishu-message-fallback
description: |
  Feishu message fallback mechanism with retry logic. Automatically retries failed messages with exponential backoff and fallback from rich text to plain text.
---

# 飞书消息回退机制

## 功能

- **自动重试**：消息发送失败时自动重试（最多 3 次）
- **指数退避**：重试间隔递增（1s → 2s → 4s）
- **降级策略**：富文本失败 → 纯文本重试
- **错误日志**：记录失败原因和重试结果

## 使用场景

- 网络波动导致消息发送失败
- 富文本格式不被支持
- 消息队列积压

## 实现逻辑

```powershell
# 伪代码
function Send-FeishuMessageWithFallback {
    param($message, $retryCount = 3)
    
    for ($i = 0; $i -lt $retryCount; $i++) {
        try {
            # 尝试发送富文本
            $result = Send-FeishuRichText -message $message
            if ($result.success) { return $result }
        } catch {
            Write-Host "Attempt $($i+1) failed: $_"
        }
        
        # 指数退避等待
        if ($i -lt $retryCount - 1) {
            $waitTime = [Math]::Pow(2, $i)
            Start-Sleep -Seconds $waitTime
        }
    }
    
    # 所有重试失败，降级为纯文本
    Write-Host "Rich text failed, falling back to plain text..."
    return Send-FeishuPlainText -message $message
}
```

## 配置

在 `TOOLS.md` 中添加：

```markdown
### 飞书消息回退配置

- **最大重试次数：** 3
- **重试间隔：** 1s, 2s, 4s（指数退避）
- **降级策略：** 富文本 → 纯文本
```

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 网络超时 | 自动重试 |
| 格式错误 | 降级为纯文本 |
| 权限不足 | 立即失败，通知用户 |
| 消息过长 | 截断后重试 |

## 集成到定时任务

定时任务调用时自动启用回退机制：

```json
{
  "delivery": {
    "mode": "announce",
    "channel": "feishu",
    "to": "ou_faec8fadc584abfd18a2996f55d607b5",
    "retry": {
      "maxAttempts": 3,
      "backoffMs": 1000
    }
  }
}
```
