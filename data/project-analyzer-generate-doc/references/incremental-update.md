# 增量更新流程

> 当代码变更时，只更新受影响的文档，而非全量重新生成

---

## 🔄 完整流程

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Git diff 检测变更文件                                    │
│   git diff --name-only HEAD~1 HEAD                               │
│   → 获取变更文件列表：["Service.java", "Controller.java"]        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: 定位受影响的 L3 文档                                      │
│   Service.java → .ai-doc/module/Service.java.md                 │
│   Controller.java → .ai-doc/module/Controller.java.md           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: 判断变更类型                                             │
│ ├─ 函数签名变更 → 标记 L3 + L2 需要更新                           │
│ ├─ 逻辑变更 → 只标记 L3 需要更新                                 │
│ ├─ 新增文件 → 创建 L3 + 更新 L2                                  │
│ └─ 删除文件 → 标记 L3 为 deleted + 更新 L2                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: 批量更新 L3 文档                                          │
│   spawn 子代理 (每片 10-15 个变更文件)                              │
│   → 生成/更新对应的 L3 文档                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: 更新 L2 模块文档                                          │
│   读取变更模块的所有 L3 摘要                                       │
│   → 重新生成 module.md                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: 更新 L1 项目文档 (仅当模块结构变化时)                       │
│   如果有新增/删除模块 → 更新 project.md                           │
│   否则 → 只更新统计数字                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 变更类型判断规则

| 变更内容 | L3 | L2 | L1 |
|----------|----|----|----|
| 函数签名变更 | ✅ 更新 | ✅ 更新 | ❌ |
| 函数逻辑变更 | ✅ 更新 | ❌ | ❌ |
| 新增文件 | ✅ 创建 | ✅ 更新 | ❌ |
| 删除文件 | ✅ 标记 deleted | ✅ 更新 | ❌ |
| 新增模块 | - | ✅ 创建 | ✅ 更新 |
| 删除模块 | - | ✅ 标记 deleted | ✅ 更新 |
| 配置文件变更 | ✅ 更新 | ✅ 更新 | ✅ 更新 (如影响全局) |

---

## 🔍 Git Diff 调用方式

### PowerShell 示例

```powershell
# 获取上次提交的变更文件
$changedFiles = git diff --name-only HEAD~1 HEAD

# 过滤 Java 文件
$javaFiles = $changedFiles | Where-Object { $_ -like "*.java" }

# 定位模块
foreach ($file in $javaFiles) {
    $moduleName = $file.Split('/')[0]
    $relativePath = $file -replace "$moduleName/", ""
    
    Write-Host "变更：$moduleName / $relativePath"
}
```

### 变更传播规则

```
文件变更 → 传播路径
─────────────────────────────────────────
Service.java
  → L3: .ai-doc/energy-ai-api/Service.java.md ✅
  → L2: .ai-doc/energy-ai-api.md ✅
  → L1: .ai-doc/project.md ❌ (仅统计数字更新)

pom.xml (依赖变更)
  → L3: (无)
  → L2: .ai-doc/energy-ai-api.md ✅
  → L1: .ai-doc/project.md ✅ (技术栈更新)

新增模块 new-module/
  → L3: .ai-doc/new-module/*.java.md ✅
  → L2: .ai-doc/new-module.md ✅
  → L1: .ai-doc/project.md ✅ (模块列表更新)
```

---

## ⚙️ 增量更新命令

```powershell
# 完整增量更新
.\scripts\generate_docs.ps1 `
  -ProjectPath "E:\projects\infypower-energy-ai" `
  -OutputPath "D:\workspace\docs\infypower-energy-ai" `
  -Mode incremental

# 单模块更新
.\scripts\generate_docs.ps1 `
  -ProjectPath "E:\projects\infypower-energy-ai" `
  -OutputPath "D:\workspace\docs\infypower-energy-ai" `
  -Mode single-module `
  -ModuleName "energy-ai-api"
```

---

## 📊 性能对比

| 场景 | 全量生成 | 增量更新 | 提升 |
|------|----------|----------|------|
| 1 个文件变更 | ~30 分钟 | ~30 秒 | 60x |
| 1 个模块变更 (10 文件) | ~30 分钟 | ~2 分钟 | 15x |
| 配置变更 | ~30 分钟 | ~1 分钟 | 30x |

---

*本文档为 project-analyzer-generate-doc skill 的参考指南*
