# Dioxus 快速入门

## 第一步：安装 Dioxus

```bash
# 使用 Cargo 安装
cargo install dioxus-cli

# 或者使用 bun/pnpm
bun install -g dioxus-cli
```

## 第二步：创建新项目

```bash
dioxus init my-dioxus-app
cd my-dioxus-app
```

## 第三步：启动开发服务器

```bash
dioxus serve --hot-reload
```

浏览器打开 http://localhost:8080

## 第四步：修改主组件

打开 `src/App.rsx`，修改为：

```rust
use dioxus::prelude::*;

#[component]
fn App() -> Element {
    rsx! {
        div {
            h1 { "Hello, Dioxus!" }
            p { "Welcome to your first Dioxus app." }
        }
    }
}
```

## 第五步：添加状态

修改 `src/App.rsx`：

```rust
use dioxus::prelude::*;
use dioxus::hooks::*;

#[component]
fn App() -> Element {
    let mut count = use_signal(cx, || 0);

    rsx! {
        div {
            h1 { "Hello, Dioxus!" }
            p { "Count: {count}" }
            button {
                onclick: move |_| count += 1;
            } { "Increment" }
        }
    }
}
```

## 第六步：添加路由

1. 安装路由依赖：

```bash
cargo add dioxus-router
```

2. 修改 `src/main.rs`：

```rust
use dioxus::prelude::*;
use dioxus::router::{Route, Router, Link};

fn main() {
    launch(App);
}

#[component]
fn App() -> Element {
    rsx! {
        Router {
            Route { to: "/", Home {} }
            Route { to: "/about", About {} }
        }
    }
}
}
```

## 第七步：添加样式

创建 `public/styles.css`：

```css
body {
    font-family: Arial, sans-serif;
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

h1 {
    color: #333;
    border-bottom: 2px solid #007bff;
    padding-bottom: 0.5rem;
}
```

在 `src/App.rsx` 中引入：

```rust
use dioxus::prelude::*;

#[component]
fn App() -> Element {
    rsx! {
        link {
            rel: "stylesheet",
            href: "/styles.css"
        }
        // ... 组件代码
    }
}
```

## 第八步：构建和部署

```bash
# 开发构建
cargo build

# 生产构建
cargo build --release

# 使用 Dioxus 部署
cargo install dioxus-cli
dioxus build
dioxus serve
```

## 下一步

- [添加路由](https://dioxuslabs.com/learn/0.7/essentials/router/)
- [添加状态](https://dioxuslabs.com/learn/0.7/essentials/basics/)
- [添加后端](https://dioxuslabs.com/learn/0.7/tutorial/backend)
- [数据库集成](https://dioxuslabs.com/learn/0.7/tutorial/databases)
- [打包应用](https://dioxuslabs.com/learn/0.7/tutorial/bundle)
