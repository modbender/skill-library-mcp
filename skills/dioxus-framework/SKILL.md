---
name: dioxus-framework
description: Dioxus 是一个 Rust 的全栈跨平台应用框架，支持服务端渲染、实时更新和类似 React 的组件模型。当用户需要使用 Dioxus 构建 Web 应用、创建组件、处理状态、路由、或处理数据获取时使用。
---

# Dioxus Framework

Dioxus 是一个现代 Rust Web 框架，结合了 React 的编程模型与 Rust 的性能优势。它允许你构建高性能的 Web 应用，支持服务端渲染（SSR）、实时更新和跨平台部署。

## 快速开始

### 安装依赖

```bash
# 在 Rust 项目中添加 Dioxus
cargo add dioxus --features ssr

# 使用 CLI 工具
cargo install dioxus-cli
```

### 基本项目结构

```
src/
├── main.rs           # 应用入口
├── App.rsx           # 根组件
├── components/        # 子组件目录
├── routes/            # 路由模块
├── server_fn/         # 服务端函数
└── utils/             # 工具函数
```

## 组件基础

### 定义组件

组件是使用 `#[component]` 宏定义的函数，它接受 Properties（props）并返回一个 `Element`。

```rust
use dioxus::prelude::*;

#[component]
fn DogApp(breed: String) -> Element {
    rsx! {
        div { class: "card" } {
            h2 { "Dogs of breed: {breed}" }
            ul {
                (0..3).map(|i| rsx! {
                    li { "Dog {i}" }
                })
            }
        }
    }
}
```

### Component Properties

所有组件都接受一个描述其参数的 struct。Props 需要 derive 以下 traits：

```rust
#[derive(Props, PartialEq, Clone)]
struct DogAppProps {
    breed: String,
}
```

**重要特性：**

| 特性 | 说明 |
|------|------|
| **Props** | 组件接受的参数对象 |
| **PartialEqual** | 允许部分更新 props |
| **Clone** | 允许克隆 props |
| **Memoized** | 默认 memoized，只有 props 改变时重新渲染 |

### 组件生命周期

Dioxus 组件会在以下情况下重新渲染：

1. **Props 改变**：当组件的 props 发生变化时
2. **信号变化**：当组件监听的信号更新时
3. **Scope.needs_update()**：当父组件要求更新时

**重要：** Dioxus 默认 memoized 所有组件，性能比 React 更好。

## 状态管理

### 使用 Hooks

Dioxus 提供类似 React 的 hooks 用于管理状态。

#### use_signal()

创建响应式状态：

```rust
#[component]
fn Counter() -> Element {
    let mut count = use_signal(cx, || 0);

    rsx! {
        div {
            button {
                onclick: move |_| {
                    count += 1;
                }
            } { "Increment" }
            p { "Count: {count}" }
            button {
                onclick: move |_| {
                    count -= 1;
                }
            } { "Decrement" }
        }
    }
}
```

#### use_coroutine()

运行异步操作：

```rust
#[component]
fn DataFetcher() -> Element {
    let mut data = use_signal(cx, || None::<String>);
    let loading = use_signal(cx, || false);

    use_coroutine(cx, |cx| async move {
        loading.set(true);
        // 模拟异步数据获取
        tokio::time::sleep(Duration::from_secs(2)).await;
        data.set(Some("Fetched data".to_string()));
        loading.set(false);
    });

    rsx! {
        div {
            if *loading.get() {
                p { "Loading..." }
            } else if let Some(d) = data.get() {
                p { "Data: {d}" }
            } else {
                p { "No data yet" }
            }
        }
    }
}
```

#### use_context()

访问上下文值：

```rust
#[derive(Clone, Props)]
struct ChildProps {
    value: String,
}

#[component]
fn Child(props: ChildProps) -> Element {
    rsx! { p { "Value from context: {props.value}" } }
}

#[component]
fn Parent() -> Element {
    let value = use_context(cx, || "default".to_string());
    rsx! { Child { value: value.clone() } }
}
```

### 全局状态

使用信号进行全局状态管理：

```rust
// main.rs
use dioxus::prelude::*;

fn main() {
    let theme_signal = RwSignal::new("light".to_string());
    dioxus::launch(App, (
        AppContext::new(theme_signal)
    ));
}

// App.rsx
#[component]
fn App() -> Element {
    let theme = use_context(cx);
    rsx! {
        div {
            button {
                onclick: move |_| theme.set("dark".to_string())
            } { "Dark Mode" }
            button {
                onclick: move |_| theme.set("light".to_string())
            } { "Light Mode" }
            p { "Current theme: {theme.read()}" }
        }
    }
}
```

## 路由

### 基本路由

```rust
// routes/mod.rs
use dioxus::prelude::*;
use dioxus::router::{Route, Router};

#[component]
fn Home() -> Element {
    rsx! { h1 { "Home Page" } }
}

#[component]
fn About() -> Element {
    rsx! { h1 { "About Page" } }
}

// App.rsx
#[component]
fn App() -> Element {
    rsx! {
        Router {
            Route { to: "/", Home {} }
            Route { to: "/about", About {} }
        }
    }
}
```

### 动态路由

```rust
use dioxus::router::NavLink;

rsx! {
    nav {
        ul {
            li { NavLink { to: "/" } { "Home" } }
            li { NavLink { to: "/about" } { "About" } }
        }
    }
}
```

## 表单处理

```rust
#[derive(Props, Clone)]
struct FormProps {
    on_submit: Callback<String>,
}

#[component]
fn Form(props: FormProps) -> Element {
    let mut name = use_signal(cx, || String::new());
    let mut email = use_signal(cx, || String::new());

    rsx! {
        form {
            onsubmit: move |event| {
                event.prevent_default();
                props.on_submit.call((
                    name.get().clone(),
                    email.get().clone(),
                ));
            }
        } {
            input {
                r#type: "text",
                value: "{name}",
                oninput: move |e| name.set(e.value())
            }
            input {
                r#type: "email",
                value: "{email}",
                oninput: move |e| email.set(e.value())
            }
            button { r#type: "submit" } { "Submit" }
        }
    }
}
```

## 服务端渲染（SSR）

### 启用 SSR

```rust
// main.rs
use dioxus::prelude::*;

fn main() {
    // 启用 SSR 功能
    dioxus::launch(App);
}

// server_fn/api.rs
use dioxus::prelude::*;

#[server_fn("/")]
async fn serve_home() -> String {
    // 渲染组件为字符串
    render_to_string(|cx| rsx! { App {} })
}
```

### 服务端函数（Server Functions）

```rust
use dioxus::prelude::*;

#[server_fn("/api/hello")]
async fn hello(name: String) -> String {
    format!("Hello, {}!", name)
}
```

## 数据获取

### 使用资源

```rust
#[server_fn("/api/data")]
async fn fetch_data() -> Json<Vec<String>> {
    use crate::data::fetch_from_db().await
}
```

## 常见模式

### 条件渲染

```rust
rsx! {
    div {
        if *count.get() > 0 {
            p { "Count is positive" }
        } else {
            p { "Count is zero" }
        }
    }
}
```

### 列表渲染

```rust
let items = vec!["Item 1", "Item 2", "Item 3"];

rsx! {
    ul {
        items.iter().map(|item| rsx! {
            li { key: "{item}" } { item }
        })
    }
}
```

### 组件组合

```rust
#[component]
fn Header() -> Element {
    rsx! {
        header {
            h1 { "My App" }
            nav {
                a { href: "/" } { "Home" }
                a { href: "/about" } { "About" }
            }
        }
    }
}

#[component]
fn PageLayout(content: Element) -> Element {
    rsx! {
        div { class: "layout" } {
            Header {}
            main { content }
            Footer {}
        }
    }
}
```

## 样式和资源

### CSS 模块

```rust
// 在 main.rs 或组件中导入样式
use dioxus::prelude::*;

// styles.css
.card {
    background-color: white;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
```

### 内联样式

```rust
rsx! {
    div {
        style: "background-color: #f0f0f0; padding: 1rem;" {
            "Content"
        }
    }
}
```

### Tailwind CSS 集成

```rust
// Cargo.toml
[dependencies]
dioxus = { version = "0.7", features = ["fullstack"] }

// 在组件中使用
rsx! {
    div { class: "bg-blue-500 text-white p-4 rounded" } {
        "Styled"
    }
}
```

## 错误处理

### 错误边界

```rust
#[component]
fn ErrorBoundary() -> Element {
    rsx! {
        div {
            p { "Something went wrong!" }
            button {
                onclick: move |_| {
                    // 重试逻辑
                }
            } { "Retry" }
        }
    }
}
```

### 验证 Props

```rust
#[component]
fn ValidatedInput(props: ValidatedInputProps) -> Element {
    rsx! {
        input {
            value: "{props.value}",
            r#type: props.input_type,
            disabled: props.disabled,
        }
    }
}
```

## 性能优化

### Memoization

Dioxus 默认 memoized 所有组件。对于昂贵的计算，可以使用 `use_memo`：

```rust
use dioxus::hooks::*;

#[component]
fn ExpensiveCalculation() -> Element {
    let count = use_signal(cx, || 0);

    let result = use_memo(cx, move || {
        // 昂贵的计算
        expensive_calculation(*count)
    }, (*count));

    rsx! {
        div {
            p { "Result: {result}" }
        }
    }
}
```

### 避免不必要的重新渲染

使用 `PartialEqual` 和 `use_memo` 来最小化重新渲染。

## 测试

### 组件测试

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use dioxus::prelude::*;

    #[test]
    fn test_dog_app_renders() {
        let breed = "Golden Retriever".to_string();
        let vnode = dioxus::ssr::render_to_string(|cx| rsx! {
            DogApp { breed: breed.clone() }
        });
        assert!(vnode.contains(&breed));
    }
}
```

## 部署

### 静态构建

```bash
cargo build --release
```

### 使用 Tauri 打包

```bash
cargo install tauri-cli
tauri build
```

### 使用 Docker

```dockerfile
FROM rust:1.70-slim
WORKDIR /app
COPY . .
RUN cargo build --release
CMD ["./target/release/my-app"]
```

## 参考资料

详细文档和更多示例，请参考：

- [Dioxus 文档](https://dioxuslabs.com/learn/0.7/)
- [组件参考](https://dioxuslabs.com/components)
- [GitHub](https://github.com/DioxusLabs/dioxus)
- [Discord 社区](https://discord.gg/XgGxMSkvUM)
- [Twitter](https://twitter.com/DioxusLabs)

## 常见问题

### Q: 如何处理异步操作？

A: 使用 `use_coroutine` hook 来运行异步代码并更新状态。

### Q: 如何传递数据到子组件？

A: 使用 props 传递数据，使用全局上下文管理全局状态。

### Q: 如何实现路由？

A: 使用 `dioxus::router` 提供的路由组件和 `NavLink` 进行导航。

### Q: 如何优化性能？

A: Dioxus 默认 memoized 组件，使用 `use_memo` 进行昂贵的计算。

### Q: 支持服务端渲染吗？

A: 是的，Dioxus 支持服务端渲染（SSR）和静态站点生成（SSG）。

### Q: 如何集成 API？

A: 使用服务端函数（Server Functions）或异步 hooks 来获取数据。

### Q: 支持 TypeScript 吗？

A: Dioxus 是纯 Rust 框架，但可以使用 `wasm-bindgen` 与 TypeScript 交互。
