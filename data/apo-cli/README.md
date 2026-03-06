<h1 align="center">apo-cli 💊</h1>

<p align="center">
  <strong>Your pharmacy in the terminal — search products, manage cart, checkout in browser</strong>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/dependencies-none-brightgreen.svg" alt="Zero Dependencies">
</p>

---

## 🚀 Quick Start

```bash
uv tool install git+https://github.com/Lars147/apo-cli
apo search "Aspirin"
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Search** | Find products by name or PZN |
| 📦 **Product Details** | Prices, availability, descriptions |
| 🗂️ **Categories** | Browse product collections |
| 🛒 **Cart** | Add, remove, view items |
| 🌐 **Checkout** | Opens browser with your cart |
| 🤖 **AI-Friendly** | Designed for Claude, Codex, OpenClaw |

---

## 📖 Usage

```bash
# Search
apo search "Ibuprofen 400"

# Product details
apo product <handle>

# Categories
apo categories
apo list --category bestseller

# Cart
apo cart                      # Show
apo cart add <variant_id>     # Add
apo cart remove <variant_id>  # Remove
apo cart clear                # Clear
apo cart checkout             # Open browser
```

---

## ⚠️ Disclaimer

Unofficial tool for [apohealth.de](https://www.apohealth.de). Not affiliated with apohealth.

---

## 📄 License

MIT © [Lars Heinen](https://github.com/Lars147)
