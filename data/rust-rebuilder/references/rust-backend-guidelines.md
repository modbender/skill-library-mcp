# Rust Backend Coding Guidelines

在重写后端 Rust 代码时，严格遵循本规范。目标是：可读、可维护、可验证、可演进。

## 1. 数据结构设计

- 使用 `enum` 表达状态机，不要用多布尔字段拼状态。
- 通过类型表达不变量（如 `NonZeroU32`、`Duration`、自定义枚举）。
- 明确所有权：按场景选择 `&str` / `String`、slice / `Vec`、`Arc<T>`、`Cow<'a, T>`。

```rust
enum JobState {
    Pending { scheduled_for: DateTime<Utc> },
    Running { started_at: DateTime<Utc>, worker: String },
    Completed { result: JobResult, duration_ms: i64 },
    Failed { error: String, retries: u32 },
}
```

## 2. impl 组织方式

- `impl` 紧跟对应 `struct/enum`。
- 按顺序组织：构造函数 → 只读访问器 → 变更方法 → 领域逻辑。

## 3. 迭代器优先

- 优先 `.filter().map().collect()` 等链式写法。
- 避免“临时 `Vec` + `for` + `push`”的样板流程。

## 4. 错误处理

- 可失败函数统一返回 `Result<T, Error>`（或项目约定类型）。
- 优先使用 `?` 传播错误。
- 用 `if let` / `let ... else` 处理可选值并提前返回。
- 禁止在库代码中 `panic`；`unwrap` 仅用于编译期可证明安全的场景。

## 5. 提前返回与浅层嵌套

- 先处理边界情况、非法输入、缓存命中，再写主逻辑。
- 尽量把嵌套深度压低，提升可读性与生命周期推断稳定性。

## 6. 变量遮蔽

- 优先 `let data = ...; let data = ...;` 的渐进式遮蔽。
- 避免 `raw_data` / `parsed_data` / `validated_data` 的命名膨胀。

## 7. 注释策略

- 不写解释显而易见逻辑的行内注释。
- 不提交 TODO/FIXME 注释。
- `///` 文档注释仅用于公开 API 与必要契约说明。

## 8. 类型安全与模式匹配

- 使用 `enum` 替代布尔状态位。
- `match` 尽量显式穷举；通配符仅用于明确的兜底或字段忽略。

## 9. 参数解构

- 在函数签名里直接解构框架包装类型（如 `Extension(...)`、`Path(...)`、`Query(...)`）。
- 减少函数体内重复解包噪音。

## 10. Trait 与派生

- 用 `From` / `Into` / `TryFrom` 收敛转换逻辑。
- 用 `derive` 宏减少模板代码，如 `Debug`、`Clone`、`Serialize`、`Deserialize`。

## 11. 模块与可见性

- 默认使用 `pub(crate)`，仅在必要时公开 `pub`。
- 保持 API 小而清晰，不泄漏内部实现类型。

## 12. JSON 与 Serde

- 仅透传 JSON（不需要解析）时，优先 `Box<serde_json::value::RawValue>`。
- 需要检查或改写 JSON 时再使用 `serde_json::Value`。
- 合理使用 serde 属性：`rename`、`default`、`skip_serializing_if`、`borrow`。

## 13. SQLx 规则

- 禁止 `SELECT *`，必须显式列名（兼容滚动升级）。
- 避免 N+1 查询，优先批量查询和 `IN` / `ANY`。
- 多步骤写操作必须放事务，所有 SQL 使用参数化查询。

## 14. Async/Tokio 规则

- 禁止阻塞 async runtime；阻塞计算用 `spawn_blocking`。
- async 场景使用 tokio 原语（`tokio::time::sleep`、`tokio::sync::*`）。
- 通道优先有界队列，保留背压能力。

## 15. Mutex 选择

- 默认优先 `std::sync::Mutex`（或 `parking_lot::Mutex`）。
- 仅在“必须跨 `.await` 持锁”时使用 `tokio::sync::Mutex`。
- 对 IO 资源可考虑“单任务持有 + 消息传递”模型替代共享锁。

## 16. 构建与工具

- 快速迭代时优先 `cargo check`。
- 减少不必要依赖和 feature flag。
- 不猜类型定义；优先用 rust-analyzer 做定义跳转、引用查找与类型确认。

## 17. 执行检查清单（每批重写后）

1. 无 `SELECT *`；
2. 无库级 `panic/unwrap` 滥用；
3. 错误链路返回类型一致；
4. async 代码中无阻塞调用；
5. 状态建模使用 `enum` 而非布尔拼装；
6. 暴露面最小化（`pub(crate)` 优先）。
