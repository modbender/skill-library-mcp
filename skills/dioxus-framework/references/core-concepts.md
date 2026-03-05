# Dioxus 核心概念和模式

## 组件模型

### Props（属性）
组件接受的参数，需要 derive 以下 traits：
- `Props` - Dioxus 特性
- `PartialEqual` - 允许部分更新
- `Clone` - 允许克隆
- `Memoized` - 默认启用

```rust
#[derive(Props, PartialEq, Clone)]
struct MyComponentProps {
    title: String,
    count: i32,
}
```

### Element（元素）
组件的返回类型，代表要渲染的 UI 树。

### 宏宏
- `#[component]` - 标记组件函数
- `#[server_fn]` - 标记服务端函数
- `rsx! {}` - 定义 UI 结构
- `use_signal()` - 创建响应式状态
- `use_coroutine()` - 运行异步操作
- `use_context()` - 访问全局上下文

## Hooks

### 响应式状态

#### use_signal
创建本地状态信号。

```rust
let mut count = use_signal(cx, || 0);
```

#### use_context
访问全局上下文。

```rust
let theme = use_context(cx, || "light".to_string());
```

#### use_coroutine
运行异步代码并更新状态。

```rust
use_coroutine(cx, |cx| async move {
    // 异步操作
    result.set(await fetch_data().await);
});
```

### 高级 Hooks

#### use_memo
Memoize 昂贵的计算。

```rust
let result = use_memo(cx, move || {
    expensive_calculation(*count)
}, (*count));
```

#### use_resource
管理异步资源，自动重试和缓存。

```rust
let data = use_resource(cx, |cx| async move {
    fetch_data().await
});
```

## 渲染

### 条件渲染
使用 `if` 进行条件渲染。

```rust
rsx! {
    if *loading.get() {
        p { "Loading..." }
    } else {
        p { "Content loaded" }
    }
}
```

### 列表渲染
使用迭代器渲染列表。

```rust
let items = vec!["Item 1", "Item 2"];

rsx! {
    ul {
        items.iter().map(|item| rsx! {
            li { key: item } { item }
        })
    }
}
```

### 表达式片段
使用闭包返回元素。

```rust
rsx! {
    div {
        (0..5).map(|i| rsx! {
            span { "Item {i}" }
        })
    }
}
```

## 事件处理

### 点击事件

```rust
button {
    onclick: move |_| {
        count += 1;
    }
} { "Increment" }
```

### 表单事件

```rust
input {
    r#type: "text",
    value: "{name}",
    oninput: move |e| name.set(e.value()),
}
```

### 键盘事件

```rust
input {
    onkeydown: move |e| {
        if e.key() == "Enter" {
            submit.call(());
        }
    }
}
```

## 路由

### 路由定义

```rust
use dioxus::router::{Route, Router};

rsx! {
    Router {
        Route { to: "/", Home {} }
        Route { to: "/about", About {} }
    }
}
```

### 导航链接

```rust
use dioxus::router::NavLink;

rsx! {
    NavLink {
        to: "/about"
    } { "About" }
}
```

### 程序导航

```rust
use dioxus::router::use_navigator;

let nav = use_navigator(cx);

// 在事件中
nav.push("/profile");
nav.back();
nav.replace("/login");
```

## 表单

### 受控组件

```rust
input {
    r#type: "text",
    value: "{value}",
}
```

### 表单提交

```rust
form {
    onsubmit: move |e| {
        e.prevent_default();
        handle_submit(e);
    }
}
```

### 表单验证

使用 `Pattern` 或手动验证：

```rust
#[derive(Props, Clone)]
struct FormProps {
    on_submit: Callback<Formdata>,
}

#[component]
fn Form(props: FormProps) -> Element {
    rsx! {
        form {
            onsubmit: move |e| {
                if is_valid(e) {
                    props.on_submit.call(e.data());
                }
            }
        }
    }
}
```

## 服务器端渲染

### 基本 SSR

```rust
#[server_fn("/")]
async fn serve_home() -> String {
    render_to_string(|cx| rsx! { App {} })
}
```

### 静态站点生成（SSG）

```rust
#[server_fn("/static/")]
async fn serve_static() -> Response {
    static_files(&PathBuf::from("static")).serve(cx)
}
```

### 增量静态生成（ISR）

```rust
#[server_fn("/")]
async fn serve_incremental() -> String {
    let html = render_to_string(|cx| rsx! { App {} });

    Response::Ok()
        .content_type("text/html")
        .body(html)
}
```

## 数据获取

### 服务端函数

```rust
#[server_fn("/api/data")]
async fn get_data() -> Json<DataType> {
    let data = fetch_from_database().await;
    Json(data)
}
```

### 资源钩子

```rust
#[server_fn(Resource::new(resource_path()))]
async fn get_resource(id: Uuid) -> Response<String> {
    let data = resource.data.await;
    Html(render! {
        div { "{data}" }
    })
}
```

## 性能优化

### Memoization

Dioxus 默认 memoize 所有组件。对于昂贵的计算：

```rust
let result = use_memo(cx, move || {
    expensive_calculation(*count)
}, (*count));
```

### 避免不必要的克隆

使用引用传递：

```rust
// 不好
button {
    onclick: move |_| {
        process(data.clone());
    }
}

// 好
button {
    onclick: move |_| {
        process(&data);
    }
}
```

### 虚拟列表

对于长列表，使用虚拟滚动：

```rust
use dioxus::fullstack::virtual_scroller::*;

rsx! {
    VirtualScroller {
        items: large_list,
        row_height: 50.0,
        each: |item| rsx! {
            div { "{item}" }
        }
    }
}
```

## 最佳实践

### 组件设计

1. **单一职责**：每个组件只做一件事
2. **可重用**：通过 props 和组合实现复用
3. **纯函数**：尽可能保持组件纯函数
4. **类型安全**：充分利用 Rust 的类型系统

### 状态管理

1. **最小化状态**：只存储必要的状态
2. **提升状态**：共享状态提升到最近的共同祖先
3. **使用上下文**：全局状态使用 Context API
4. **避免 prop drilling**：使用 Context 而不是层层传递

### 错误处理

1. **错误边界**：捕获子组件错误
2. **优雅降级**：提供友好的错误消息
3. **重试机制**：对可重试的操作实现重试
4. **加载状态**：明确处理加载、成功和错误状态

### 测试

1. **单元测试**：测试组件逻辑
2. **集成测试**：测试组件交互
3. **E2E 测试**：测试端到端功能
4. **性能测试**：测量渲染性能

## 常见问题

### Q: 为什么组件不更新？

A: 检查以下几点：
- Props 是否实现 `PartialEqual`？
- 是否调用了 `needs_update()`？
- 信号是否正确设置？

### Q: 如何处理加载状态？

A: 使用枚举和信号：

```rust
#[derive(Clone, Copy)]
enum State {
    Loading,
    Loaded(Data),
    Error(String),
}

let state = use_signal(cx, || State::Loading);

rsx! {
    match &*state.get() {
        State::Loading => rsx! { p { "Loading..." } },
        State::Loaded(data) => rsx! { p { "{data}" } },
        State::Error(msg) => rsx! { p { "Error: {msg}" } },
    }
}
```

### Q: 如何优化大型列表渲染？

A: 使用虚拟滚动和 memoization：

```rust
rsx! {
    VirtualScroller {
        items: large_list,
        row_height: 50,
    }
}
```

### Q: 支持动画吗？

A: Dioxus 支持通过 CSS 动画和过渡：

```rust
rsx! {
    div {
        class: "fade-in",
        style: "transition: opacity 0.3s ease-in-out;"
    } {
        "Content"
    }
}
```

### Q: 如何处理表单验证？

A: 使用 Pattern 和验证状态：

```rust
#[derive(Props, Clone)]
struct FormProps {
    on_submit: Callback<Formdata>,
}

#[component]
fn Form(props: FormProps) -> Element {
    let valid = use_signal(cx, || true);
    let errors = use_signal(cx, || Vec::new());

    rsx! {
        form {
            onsubmit: move |e| {
                e.prevent_default();
                if *valid.get() {
                    props.on_submit.call(e.data());
                }
            }
        }
    }
}
```
