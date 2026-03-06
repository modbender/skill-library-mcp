# 断点续传指南

> 支持大型项目文档生成的中断恢复和进度追踪

---

## 🎯 问题场景

**场景 1: 子代理超时**
```
处理 2000 个文件的项目，预计 3 小时
第 1.5 小时时某个子代理超时
❌ 无断点续传：需要重新开始
✅ 有断点续传：从断点继续
```

**场景 2: 手动中断**
```
生成过程中需要处理紧急任务
手动停止生成流程
❌ 无断点续传：进度丢失
✅ 有断点续传：保存进度，稍后恢复
```

**场景 3: 系统异常**
```
生成过程中遇到系统重启/网络中断
❌ 无断点续传：全部重来
✅ 有断点续传：恢复到最后状态
```

---

## 📋 状态追踪设计

### 状态文件结构

```json
{
  "projectPath": "E:\\projects\\infypower-energy-ai",
  "outputPath": "E:\\projects\\infypower-energy-ai\\.ai-doc",
  "startedAt": "2026-03-03T10:00:00+08:00",
  "lastUpdatedAt": "2026-03-03T10:30:00+08:00",
  "status": "running|completed|failed|paused",
  
  "currentStage": "L3|L2|L1",
  
  "L3": {
    "totalFiles": 149,
    "completedFiles": 86,
    "failedFiles": [],
    "chunks": [
      {
        "moduleName": "energy-ai-api",
        "chunkIndex": 1,
        "totalChunks": 6,
        "status": "completed",
        "files": ["File1.java", "File2.java"],
        "completedAt": "2026-03-03T10:15:00+08:00"
      },
      {
        "moduleName": "energy-ai-api",
        "chunkIndex": 2,
        "totalChunks": 6,
        "status": "running",
        "files": ["File3.java"],
        "startedAt": "2026-03-03T10:16:00+08:00"
      }
    ]
  },
  
  "L2": {
    "totalModules": 7,
    "completedModules": 0,
    "modules": []
  },
  
  "L1": {
    "status": "pending",
    "completedAt": null
  },
  
  "errors": [
    {
      "timestamp": "2026-03-03T10:20:00+08:00",
      "stage": "L3",
      "module": "energy-ai-api",
      "chunk": 3,
      "error": "Timeout after 300s",
      "retryCount": 1
    }
  ]
}
```

### 状态文件位置

```
<项目根目录>/.ai-doc/.generate-state.json
```

---

## 🔄 断点续传流程

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: 检查状态文件                                             │
│   if (Test-Path .ai-doc/.generate-state.json)                   │
│   → 读取上次进度                                                 │
│   → 询问用户是否恢复                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: 恢复进度                                                 │
│   读取 state.json                                                │
│   ├─→ L3 未完成 → 从最后一个完成的 chunk 继续                      │
│   ├─→ L3 完成，L2 未完成 → 开始 L2                                │
│   └─→ L2 完成，L1 未完成 → 开始 L1                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: 跳过已完成的 chunk                                       │
│   foreach ($chunk in $chunks) {                                 │
│     if ($chunk.status -eq "completed") {                        │
│       Write-Host "跳过已完成：$chunk"                            │
│       continue                                                   │
│     }                                                            │
│     # 处理未完成的 chunk                                         │
│   }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: 更新状态文件                                             │
│   每完成一个 chunk → 更新 state.json                             │
│   确保随时可以恢复                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ 实现示例

### PowerShell 状态管理

```powershell
# 状态文件路径
$statePath = Join-Path $OutputPath ".generate-state.json"

# 初始化状态
function Initialize-State {
    param([string]$ProjectPath, [string]$OutputPath)
    
    $state = @{
        projectPath = $ProjectPath
        outputPath = $OutputPath
        startedAt = Get-Date -Format "o"
        lastUpdatedAt = Get-Date -Format "o"
        status = "running"
        currentStage = "L3"
        L3 = @{
            totalFiles = 0
            completedFiles = 0
            chunks = @()
        }
        L2 = @{
            totalModules = 0
            completedModules = 0
            modules = @()
        }
        L1 = @{
            status = "pending"
        }
        errors = @()
    }
    
    $state | ConvertTo-Json -Depth 10 | Set-Content $statePath
    return $state
}

# 更新状态
function Update-State {
    param($State, [string]$Stage, [string]$ChunkIndex, [string]$Status)
    
    $state.lastUpdatedAt = Get-Date -Format "o"
    $state.currentStage = $Stage
    
    # 更新对应 chunk 状态
    $chunk = $state.L3.chunks | Where-Object { $_.chunkIndex -eq $ChunkIndex }
    if ($chunk) {
        $chunk.status = $Status
        $chunk.completedAt = Get-Date -Format "o"
    }
    
    $state | ConvertTo-Json -Depth 10 | Set-Content $statePath
}

# 检查并恢复
function Check-And-Resume {
    param([string]$OutputPath)
    
    $statePath = Join-Path $OutputPath ".generate-state.json"
    
    if (Test-Path $statePath) {
        $state = Get-Content $statePath | ConvertFrom-Json
        
        Write-Host "发现未完成的生成任务:" -ForegroundColor Yellow
        Write-Host "  开始时间：$($state.startedAt)"
        Write-Host "  当前阶段：$($state.currentStage)"
        Write-Host "  L3 进度：$($state.L3.completedFiles)/$($state.L3.totalFiles)"
        
        $response = Read-Host "是否恢复进度？(y/n)"
        if ($response -eq "y") {
            return $state
        }
    }
    
    return $null
}
```

### 子代理任务中的状态更新

```powershell
# 在每个子代理任务中
task {
    param($ChunkInfo, $StatePath)
    
    try {
        # 开始处理
        Update-State -StatePath $StatePath -ChunkIndex $ChunkInfo.Index -Status "running"
        
        # 生成文档...
        foreach ($file in $ChunkInfo.Files) {
            # 每处理一个文件更新一次
            Generate-L3Doc -File $file
            
            # 更新进度
            $completedCount++
            Update-State -StatePath $StatePath -CompletedCount $completedCount
        }
        
        # 完成
        Update-State -StatePath $StatePath -ChunkIndex $ChunkInfo.Index -Status "completed"
        
    } catch {
        # 失败
        Update-State -StatePath $StatePath -ChunkIndex $ChunkInfo.Index -Status "failed"
        
        # 记录错误
        Log-Error -StatePath $StatePath -Error $_
        
        throw
    }
}
```

---

## 📊 进度显示

### 实时进度条

```powershell
Write-Progress `
  -Activity "L3 文档生成" `
  -Status "处理 $($module.Name) 模块" `
  -CurrentOperation "$completed/$total 文件" `
  -PercentComplete ($completed / $total * 100)
```

### 完成报告

```
✅ 文档生成完成！

进度统计:
  开始时间：2026-03-03 10:00:00
  结束时间：2026-03-03 10:30:00
  总耗时：30 分钟

L3 文档:
  总文件数：149
  已完成：149
  失败：0
  重试：2

L2 文档:
  总模块数：7
  已完成：7

L1 文档:
  状态：已完成

输出路径：E:\projects\infypower-energy-ai\.ai-doc\
```

---

## ⚠️ 错误恢复策略

### 超时重试

```powershell
$maxRetries = 3
$retryCount = 0

while ($retryCount -lt $maxRetries) {
    try {
        # 执行任务
        Invoke-Task -Timeout 300
        break
    } catch {
        $retryCount++
        if ($retryCount -lt $maxRetries) {
            Write-Host "重试 $retryCount/$maxRetries" -ForegroundColor Yellow
            Start-Sleep -Seconds 5
        } else {
            # 记录失败
            Log-Error -Error $_
            throw
        }
    }
}
```

### 失败文件跳过

```powershell
# 对于失败的文件，记录但继续
if ($failedFiles.Count -gt 0) {
    Write-Host "`n以下文件生成失败:" -ForegroundColor Yellow
    $failedFiles | ForEach-Object { Write-Host "  - $_" }
    
    Write-Host "`n继续生成其他文档..." -ForegroundColor Gray
}
```

---

## 🎯 最佳实践

1. **频繁保存状态**: 每完成一个 chunk 立即更新 state.json
2. **原子写入**: 使用临时文件 + 重命名，避免写入中断导致损坏
3. **错误详情**: 记录完整的错误信息，便于调试
4. **用户友好**: 提供清晰的进度和恢复选项
5. **自动清理**: 完成后删除 state.json，或移动到历史记录

---

*本文档为 project-analyzer-generate-doc skill 的参考指南*
