# 上下文压缩指南

> 在 L3 文档生成过程中管理上下文使用率，避免超时和上下文爆炸

---

## 🎯 核心原则

**目标**: 在有限的上下文窗口内完成大量文件的文档生成

**策略**: 定期压缩已处理内容，只保留关键信息

---

## 📊 上下文阈值

| 使用率 | 状态 | 动作 |
|--------|------|------|
| <30% | ✅ 正常 | 继续处理 |
| 30-40% | ⚠️ 预警 | 准备压缩 |
| 40-50% | 🟡 警告 | 软压缩 |
| 50-60% | 🔴 危险 | **强制压缩** |
| >60% | ❌ 紧急 | 停止任务，分片 |

---

## 🔧 压缩操作

### 软压缩 (40-50%)

**保留**:
- 文件路径列表
- 每文件 1 行摘要
- 函数签名（仅复杂文件）
- 当前任务描述
- 输出路径

**丢弃**:
- 已生成文档的完整内容
- 中间思考过程
- 详细示例
- 完整函数体

**示例**:
```markdown
# 压缩前 (占用大量上下文)
已处理文件 1:
- 路径：com/example/Service.java
- 完整文档内容：(2000 字...)
  # Service.java - 代码详解
  ## 基本信息
  - 文件路径：com/example/Service.java
  - 行数：150
  ... (完整 L3 文档)

已处理文件 2:
- 路径：com/example/Controller.java
- 完整文档内容：(1800 字...)
  ...

# 压缩后 (只保留关键信息)
已处理文件：
1. com/example/Service.java - 服务层基类，150 行，复杂
2. com/example/Controller.java - REST 控制器，120 行，中等

待处理文件：
1. com/example/Repository.java
2. com/example/Entity.java
```

---

### 强制压缩 (50-60%)

**保留**:
- 文件路径列表（仅路径）
- 每文件 5 字超简短摘要
- 输出路径
- 当前进度 (X/Y)

**丢弃**:
- 所有已生成文档的内容
- 函数签名
- 依赖关系
- 配置项
- 任何详细说明

**示例**:
```markdown
# 强制压缩后
进度：3/10
已完成：Service.java (服务), Controller.java (控制器), Repository.java (数据)
待处理：Entity.java, DTO.java, Config.java, ...
输出：D:\docs\module\
```

---

## ⏱️ 压缩时机

### 按文件数量

```
每处理 2-3 个文件 → 执行一次压缩

处理文件 1 → 生成文档 → 不压缩
处理文件 2 → 生成文档 → 不压缩
处理文件 3 → 生成文档 → 压缩 (保留摘要)
处理文件 4 → 生成文档 → 不压缩
处理文件 5 → 生成文档 → 不压缩
处理文件 6 → 生成文档 → 压缩 (保留摘要)
...
```

### 按上下文使用率

```javascript
// 伪代码
afterEachFile(() => {
  const usage = getContextUsage();
  
  if (usage > 0.60) {
    forceCompress();  // 强制压缩
    if (getContextUsage() > 0.60) {
      stopAndReport(); // 仍超过 60%，停止并报告
    }
  } else if (usage > 0.40) {
    softCompress();    // 软压缩
  }
});
```

---

## 🎯 压缩技巧

### 1. 使用缩写

```
压缩前：ChatClientAdvisorFactory.java - RAG 顾问工厂类，根据意图动态创建检索 Advisor
压缩后：ChatClientAdvisorFactory - RAG 工厂
```

### 2. 使用表格代替描述

```markdown
# 压缩前（文字描述）
已处理文件 1: Service.java，这是一个服务层类，有 150 行代码，复杂度中等，包含 5 个方法
已处理文件 2: Controller.java，这是一个控制器类，有 120 行代码，复杂度简单，包含 3 个方法

# 压缩后（表格）
| 文件 | 类型 | 行数 | 复杂度 |
|------|------|------|--------|
| Service.java | 服务 | 150 | 中等 |
| Controller.java | 控制器 | 120 | 简单 |
```

### 3. 使用路径树

```markdown
# 压缩前（完整列表）
- com/example/service/Service.java
- com/example/service/ServiceImpl.java
- com/example/controller/Controller.java
- com/example/controller/RestController.java

# 压缩后（路径树）
com/example/
├── service/ (2 文件)
└── controller/ (2 文件)
```

---

## ⚠️ 注意事项

1. **不要压缩待处理文件列表**: 需要知道还有哪些文件要处理
2. **不要压缩输出路径**: 需要知道文档写到哪里
3. **不要压缩当前进度**: 需要知道完成了多少
4. **压缩后验证**: 确保仍能继续处理剩余文件

---

## 📝 压缩检查清单

压缩前确认：
- [ ] 已记录所有已处理文件的路径
- [ ] 已记录每文件的 1 行摘要
- [ ] 已记录当前进度 (X/Y)
- [ ] 已记录输出路径
- [ ] 待处理文件列表完整

压缩后确认：
- [ ] 上下文使用率降至 40% 以下
- [ ] 仍能访问已处理文件的路径列表
- [ ] 仍能继续处理剩余文件
- [ ] 没有丢失关键状态信息

---

## 🔄 压缩流程

```
开始处理文件 1
    │
    ▼
生成 L3 文档
    │
    ▼
检查上下文使用率
    │
    ├─ <40% → 继续处理下一个
    │
    ├─ 40-50% → 软压缩 → 继续
    │
    └─ >50% → 强制压缩
            │
            ▼
        检查仍>60%?
            │
            ├─ 是 → 停止并报告进度
            │
            └─ 否 → 继续处理
```

---

*本文档为 project-analyzer-generate-doc skill 的参考指南*
