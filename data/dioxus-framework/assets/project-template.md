# Dioxus 项目模板

## 项目结构

```
my-dioxus-app/
├── Cargo.toml
├── index.html
├── src/
│   ├── main.rs
│   ├── App.rsx
│   ├── routes/
│   │   ├── mod.rs
│   │   ├── home.rsx
│   │   └── about.rsx
│   ├── components/
│   │   ├── mod.rs
│   │   └── counter.rsx
│   └── server_fn/
│       ├── mod.rs
│       └── api.rs
├── public/
│   └── styles.css
└── static/
    └── data.json
```

## Cargo.toml

```toml
[package]
name = "my-dioxus-app"
version = "0.1.0"
edition = "2021"

[dependencies]
dioxus = { version = "0.7", features = ["fullstack"] }
serde = { version = "1.0", features = ["derive"] }

[dev-dependencies]
dioxus-hot-reload = "0.5"
```

## main.rs

```rust
use dioxus::prelude::*;

fn main() {
    launch(App);
}
```

## App.rsx

```rust
use dioxus::prelude::*;
use crate::routes::{Home, About};

#[component]
fn App() -> Element {
    rsx! {
        div {
            class: "app",
            h1 { "My Dioxus App" }
            nav {
                a { href: "/" } { "Home" }
                a { href: "/about" } { "About" }
            }
            main {
                Home {}
                About {}
            }
            footer {
                p { "© 2024 My Dioxus App" }
            }
        }
    }
}
```

## routes/home.rsx

```rust
use dioxus::prelude::*;

#[component]
pub fn Home() -> Element {
    rsx! {
        div {
            h2 { "Welcome to Dioxus!" }
            p { "This is the home page." }
            button {
                onclick: |_| println!("Button clicked!")
            } { "Click me" }
        }
    }
}
```

## routes/about.rsx

```rust
use dioxus::prelude::*;

#[component]
pub fn About() -> Element {
    rsx! {
        div {
            h2 { "About" }
            p { "This is a Dioxus application." }
        }
    }
}
```

## components/counter.rsx

```rust
use dioxus::prelude::*;
use dioxus::hooks::*;

#[component]
pub fn Counter() -> Element {
    let mut count = use_signal(cx, || 0);

    rsx! {
        div {
            class: "counter",
            button {
                onclick: move |_| count += 1;
            } { "Increment" }
            p { "Count: {count}" }
            button {
                onclick: move |_| count -= 1;
            } { "Decrement" }
        }
    }
}
```

## server_fn/api.rs

```rust
use dioxus::prelude::*;

#[server_fn("/api/hello")]
pub async fn hello(name: String) -> String {
    format!("Hello, {}!", name)
}

#[server_fn("/api/data")]
pub async fn fetch_data() -> Json<Vec<String>> {
    Json(vec!["Item 1", "Item 2", "Item 3"])
}
```

## public/styles.css

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
}

.app {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

nav {
    background: #f5f5f5;
    padding: 1rem;
    margin-bottom: 2rem;
}

nav a {
    color: white;
    text-decoration: none;
    margin-right: 1rem;
}

main {
    min-height: calc(100vh - 150px);
}

footer {
    background: #f5f5f5;
    padding: 1rem;
    text-align: center;
    color: white;
}

.counter {
    display: flex;
    gap: 1rem;
    align-items: center;
    padding: 2rem;
}

button {
    padding: 0.5rem 1rem;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background: #0056b3;
}
```

## index.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Dioxus App</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
    <div id="app"></div>
    <script type="module">
        import init from '/src/main.js'
        init('/app')
    </script>
</body>
</html>
```

## 运行项目

### 开发模式

```bash
cargo install dioxus-cli
dioxus serve --hot-reload
```

### 构建生产版本

```bash
cargo build --release
```

### 运行生产版本

```bash
dioxus serve --serve-static
```
