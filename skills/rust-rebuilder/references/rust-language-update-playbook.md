# Rust Language Update Playbook

## 1. 使用目标

在每次 Rust 重写任务开始前，先建立“最新特性可用性 + 稳定替代方案”双轨决策，避免盲目追新或长期落后。

## 2. 查询顺序（必须按顺序）

1. 确认当前稳定版 Rust 发布信息（版本号、发布日期、Edition 状态）。
2. 确认本次重写会用到的语言/标准库能力是否稳定可用。
3. 确认关键生态库（序列化、异步、错误处理、测试）主流实践是否变化。
4. 给出“立即采用”与“暂缓采用”的判定理由。

## 3. 推荐查询模板（grok-search）

> 说明：不要只问“最新是什么”，要带上“是否稳定可用于生产”。

- `Rust stable release notes latest version production ready features`
- `Rust edition roadmap current stable status`
- `Rust async ecosystem best practices tokio 2026`
- `Rust error handling anyhow thiserror best practice`
- `Rust performance pitfalls clone allocation borrow checker`

## 4. 特性采用决策矩阵

对每个候选特性都做四维打分（1-5），总分低于 14 则默认不在本轮采用：

- 稳定性：是否已稳定进入 stable Rust。
- 可维护性：团队是否能长期维护。
- 收益密度：相较现有方案收益是否明显。
- 迁移成本：引入后对代码结构和测试体系的影响。

## 5. 常见源语言到 Rust 的方法映射

### 5.1 错误处理

- 例外模型（throw/catch）→ `Result<T, E>` + 分层错误类型。
- 在应用层使用统一错误出口，在库层保留精细错误语义。

### 5.2 并发模型

- 共享可变对象 + 锁 → 优先消息传递或所有权拆分。
- IO 密集任务使用 async runtime，CPU 密集任务使用专门线程池或 Rayon。

### 5.3 数据模型

- 可空/动态对象 → 枚举（`enum`）或 `Option<T>` 明确建模。
- 反射式处理 → trait + 泛型 + 显式边界约束。

### 5.4 资源生命周期

- GC 托管对象 → 明确所有权与借用边界。
- 跨线程共享对象 → `Arc<T>` + 最小化可变状态。

## 6. 输出要求

每次给出 Rust 方案时，必须同时输出：

1. 采用了哪些“当前稳定可用”的语言能力；
2. 如果未来版本变更，哪些实现会受影响；
3. 若不采用新特性，当前保守方案是什么；
4. 本次决策对可读性、性能、维护成本的影响。
