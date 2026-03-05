# Surrealism -- SurrealDB WASM Extension System

Surrealism is SurrealDB's plugin/extension system, introduced in v3.0.0. It enables developers to write custom functions in Rust, compile them to WebAssembly (WASM), and register them as database modules callable from SurrealQL queries.

---

## Overview

Surrealism bridges the Rust ecosystem with SurrealDB's query engine. You can write arbitrary Rust functions, use any Rust crate, compile to WASM, and expose the resulting functions as first-class SurrealQL functions.

Key properties:
- Functions run inside the SurrealDB process as WASM modules
- Sandboxed execution with controlled memory and CPU
- Access to the full Rust crate ecosystem
- Called from SurrealQL using the `module_name::function_name()` syntax
- Managed via the `surreal module` CLI command

---

## Development Workflow

### Step 1: Create a Rust Project

Create a new Rust library project with Surrealism support:

```bash
cargo new --lib my_module
cd my_module
```

### Step 2: Configure Cargo.toml

```toml
[package]
name = "my_module"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
surrealism = "3"
```

### Step 3: Configure surrealism.toml

Create a `surrealism.toml` in the project root:

```toml
[module]
name = "my_module"
version = "0.1.0"
description = "A custom SurrealDB module"
```

### Step 4: Write Functions

Annotate functions with the `#[surrealism]` attribute:

```rust
// src/lib.rs
use surrealism::prelude::*;

#[surrealism]
fn hello(name: String) -> String {
    format!("Hello, {}!", name)
}

#[surrealism]
fn add(a: f64, b: f64) -> f64 {
    a + b
}

#[surrealism]
fn reverse_string(input: String) -> String {
    input.chars().rev().collect()
}
```

### Step 5: Build the WASM Module

```bash
surreal module build --path ./my_module
```

This compiles the Rust project to a WASM binary optimized for SurrealDB.

### Step 6: Register in the Database

```surrealql
-- Define a bucket for storing WASM modules
DEFINE BUCKET wasm_modules;

-- Register the compiled module
DEFINE MODULE my_module FROM "wasm_modules/my_module.wasm";
```

### Step 7: Call from SurrealQL

```surrealql
-- Call module functions using module_name::function_name syntax
SELECT my_module::hello("World");
-- Returns: "Hello, World!"

SELECT my_module::add(10, 25.5);
-- Returns: 35.5

SELECT my_module::reverse_string("SurrealDB");
-- Returns: "BDlaerruS"

-- Use in WHERE clauses
SELECT * FROM product WHERE my_module::validate_sku(sku) = true;

-- Use in field projections
SELECT name, my_module::format_price(price) AS formatted_price FROM product;
```

---

## Type Mapping

Surrealism maps between Rust types and SurrealQL types:

| Rust Type | SurrealQL Type | Notes |
|-----------|---------------|-------|
| `String` | `string` | UTF-8 text |
| `bool` | `bool` | Boolean |
| `i64` | `int` | 64-bit integer |
| `f64` | `float` | 64-bit float |
| `Vec<T>` | `array` | Array of mapped type |
| `Option<T>` | `T \| NONE` | Nullable values |
| `HashMap<String, T>` | `object` | Key-value object |
| `()` | `NONE` | No return value |
| `Result<T, E>` | `T` or error | Errors propagate to SurrealQL |

---

## Error Handling

Use Rust's `Result` type to handle errors gracefully. Errors propagate as SurrealQL query errors.

```rust
use surrealism::prelude::*;

#[surrealism]
fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err("Division by zero".to_string())
    } else {
        Ok(a / b)
    }
}

#[surrealism]
fn parse_json(input: String) -> Result<String, String> {
    let parsed: serde_json::Value = serde_json::from_str(&input)
        .map_err(|e| format!("Invalid JSON: {}", e))?;
    Ok(parsed.to_string())
}
```

When called from SurrealQL:

```surrealql
SELECT my_module::divide(10, 0);
-- Error: "Division by zero"

SELECT my_module::divide(10, 3);
-- Returns: 3.3333333333333335
```

---

## Advanced Examples

### Fake Data Generation

Use the `fake` crate to generate test data:

```toml
[dependencies]
surrealism = "3"
fake = { version = "2", features = ["derive"] }
rand = "0.8"
```

```rust
use surrealism::prelude::*;
use fake::{Fake, faker::name::en::*, faker::internet::en::*, faker::address::en::*};
use rand::thread_rng;

#[surrealism]
fn fake_name() -> String {
    let mut rng = thread_rng();
    Name().fake_with_rng(&mut rng)
}

#[surrealism]
fn fake_email() -> String {
    let mut rng = thread_rng();
    FreeEmail().fake_with_rng(&mut rng)
}

#[surrealism]
fn fake_city() -> String {
    let mut rng = thread_rng();
    CityName().fake_with_rng(&mut rng)
}
```

```surrealql
-- Generate fake test data
CREATE person SET
    name = faker::fake_name(),
    email = faker::fake_email(),
    city = faker::fake_city();
```

### Custom Validation Logic

```rust
use surrealism::prelude::*;

#[surrealism]
fn validate_email(email: String) -> bool {
    let parts: Vec<&str> = email.split('@').collect();
    if parts.len() != 2 {
        return false;
    }
    let domain_parts: Vec<&str> = parts[1].split('.').collect();
    !parts[0].is_empty() && domain_parts.len() >= 2 && domain_parts.iter().all(|p| !p.is_empty())
}

#[surrealism]
fn validate_phone(phone: String) -> bool {
    let digits: String = phone.chars().filter(|c| c.is_ascii_digit()).collect();
    digits.len() >= 10 && digits.len() <= 15
}

#[surrealism]
fn sanitize_html(input: String) -> String {
    input
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#39;")
}
```

```surrealql
-- Use in field definitions for validation
DEFINE FIELD email ON person VALUE $value
    ASSERT validation::validate_email($value) = true;

-- Use to sanitize user input
UPDATE post SET content = validation::sanitize_html(content);
```

### Business Rule Engine

```rust
use surrealism::prelude::*;

#[surrealism]
fn calculate_discount(total: f64, customer_tier: String) -> f64 {
    let discount_rate = match customer_tier.as_str() {
        "platinum" => 0.20,
        "gold" => 0.15,
        "silver" => 0.10,
        "bronze" => 0.05,
        _ => 0.0,
    };

    let volume_discount = if total > 1000.0 {
        0.05
    } else if total > 500.0 {
        0.02
    } else {
        0.0
    };

    total * (discount_rate + volume_discount)
}

#[surrealism]
fn calculate_shipping(weight_kg: f64, zone: String) -> Result<f64, String> {
    let base_rate = match zone.as_str() {
        "domestic" => 5.0,
        "continental" => 15.0,
        "international" => 30.0,
        _ => return Err(format!("Unknown shipping zone: {}", zone)),
    };

    Ok(base_rate + (weight_kg * 2.5))
}
```

```surrealql
SELECT
    *,
    pricing::calculate_discount(total, customer.tier) AS discount,
    pricing::calculate_shipping(weight, shipping_zone) AS shipping_cost
FROM order
WHERE status = 'pending';
```

### Quantitative Finance

```rust
use surrealism::prelude::*;

#[surrealism]
fn compound_interest(principal: f64, rate: f64, periods: f64) -> f64 {
    principal * (1.0 + rate).powf(periods)
}

#[surrealism]
fn present_value(future_value: f64, rate: f64, periods: f64) -> f64 {
    future_value / (1.0 + rate).powf(periods)
}

#[surrealism]
fn moving_average(values: Vec<f64>, window: i64) -> Vec<f64> {
    let window = window as usize;
    if values.len() < window {
        return vec![];
    }

    values
        .windows(window)
        .map(|w| w.iter().sum::<f64>() / window as f64)
        .collect()
}
```

### Text Processing

```rust
use surrealism::prelude::*;

#[surrealism]
fn slug(input: String) -> String {
    input
        .to_lowercase()
        .chars()
        .map(|c| if c.is_alphanumeric() { c } else { '-' })
        .collect::<String>()
        .split('-')
        .filter(|s| !s.is_empty())
        .collect::<Vec<&str>>()
        .join("-")
}

#[surrealism]
fn word_count(text: String) -> i64 {
    text.split_whitespace().count() as i64
}

#[surrealism]
fn truncate(text: String, max_len: i64) -> String {
    let max_len = max_len as usize;
    if text.len() <= max_len {
        text
    } else if max_len > 3 {
        format!("{}...", &text[..max_len - 3])
    } else {
        text[..max_len].to_string()
    }
}
```

---

## Use Cases

- **Custom data generation**: Generate realistic test data using Rust crate ecosystem (fake, rand)
- **Domain-specific functions**: Financial calculations, scientific formulas, statistical functions
- **Validation logic**: Complex input validation beyond what SurrealQL assertions support natively
- **Business rule engines**: Pricing rules, discount calculations, eligibility checks
- **Text processing**: Slugification, templating, sanitization, NLP preprocessing
- **External library access**: Leverage any Rust crate compiled to WASM
- **Encoding and hashing**: Custom encoding schemes, checksums, hash functions
- **Data transformation**: Complex ETL transformations within queries

---

## Best Practices

**Keep modules small and focused.** Each module should serve a single domain. Prefer multiple small modules over one monolithic module. This improves build times, reduces WASM binary size, and makes version management simpler.

**Handle all errors gracefully.** Always use `Result` return types for functions that can fail. Provide descriptive error messages that help diagnose issues when viewed in SurrealQL query results.

**Version modules alongside database schemas.** When your database schema depends on module functions (e.g., in DEFINE FIELD assertions), keep module versions synchronized with schema migrations.

**Test modules independently before deployment.** Write standard Rust unit tests for your module functions. Test with edge cases, empty inputs, and boundary values before compiling to WASM and registering in the database.

**Be mindful of memory and execution time.** WASM modules run inside the database process. Functions that allocate large amounts of memory or perform long-running computations can affect query performance. For heavy computation, consider running it outside the database and storing results.

**Avoid side effects.** Surrealism functions should be pure -- given the same inputs, they produce the same outputs. Do not rely on global mutable state, file system access, or network calls within module functions.

**Use descriptive module and function names.** Since functions are called as `module_name::function_name()` in SurrealQL, choose names that clearly indicate the function's purpose without requiring documentation lookup.

---

## Limitations and Status

Surrealism was introduced in SurrealDB v3.0.0 and is under active development. Current considerations:

- The API may evolve in future SurrealDB releases
- WASM modules cannot make network calls or access the filesystem
- Module execution is sandboxed with memory and CPU limits
- Complex dependencies may increase WASM binary size significantly
- Debugging WASM modules requires Rust-level tooling (the database provides limited introspection)
- Community feedback is encouraged to shape the direction of the extension system
