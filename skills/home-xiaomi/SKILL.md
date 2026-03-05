---
name: xiaomi
description: "[English] Control Xiaomi Home devices via local LAN using miiocli. Supports status checks, toggling power, and MIOT property manipulation for devices like smart plugs, humidifiers, and rice cookers. | [中文] 通过局域网利用 miiocli 控制米家智能设备。支持查看状态、开关控制以及对智能插座、加湿器、电饭煲等 MIOT 设备的属性调优。"
metadata: {"clawdbot":{"emoji":"🏠","requires":{"bins":["miiocli"]},"install":[{"id":"pipx-miio","kind":"exec","command":"pipx install python-miio && /Users/$(whoami)/.local/pipx/venvs/python-miio/bin/python -m pip install 'click<8.1.0'","label":"Install python-miio via pipx (with click fix)"}]}}
---

# Xiaomi Home Control小米家居控制

[English] | [中文](#中文说明)

---

## English

Enable code-level control of Xiaomi (Mi Home) devices over the local network.

### 🚀 Features
- **Local Network Control**: Fast, direct communication without relying on heavy cloud APIs.
- **Built-in Token Extractor**: Includes a script to easily fetch your device IPs and Tokens from Xiaomi Cloud.
- **Pre-configured Workflows**: Ready-to-use commands for smart plugs (e.g., water heaters), humidifiers, and rice cookers.
- **Automatic Dependency Fix**: Solves common library conflicts (like the `click` version issue) automatically.

### 🛠️ Setup & Device Inventory

1. **Tokens**: Obtain device IPs and Tokens using the bundled script:
   ```bash
   python3 scripts/token_extractor.py
   ```
2. **Registry**: Store your device details in `references/devices.md` or `references/my_private_devices.md`.

## 🤖 Natural Language Intents

When the user gives a command, map it to the corresponding `miiocli` operation:

| User Intent | Device Type | Action | Technical Command (Example) |
| :--- | :--- | :--- | :--- |
| "Turn on water heater" | Smart Plug | Power ON | `miiocli miotdevice --ip <IP> --token <TOKEN> raw_command set_properties '[{"siid": 2, "piid": 1, "value": true}]'` |
| "Turn off water heater" | Smart Plug | Power OFF | `miiocli miotdevice --ip <IP> --token <TOKEN> raw_command set_properties '[{"siid": 2, "piid": 1, "value": false}]'` |
| "Humidifier to max" | Humidifier | Set Mode | `miiocli miotdevice --ip <IP> --token <TOKEN> set_property_by 2 5 3` |
| "Is rice cooked?" | Rice Cooker | Check Status | `miiocli cooker --ip <IP> --token <TOKEN> status` |

---

## 中文说明

实现在局域网内对小米（米家）智能家居设备的代码级直接控制。

### 🚀 核心特性
- **本地化控制**：直接在局域网内通信，响应极快，不完全依赖复杂的云端 API。
- **内置 Token 提取器**：自带提取脚本，轻松从小米账号同步所有设备的 IP 和 32 位 Token 密钥。
- **预设工作流**：支持智能插座（如热水器控制）、加湿器、米家小饭煲等多种常见设备。
- **自动环境优化**：安装时自动处理 Python 依赖冲突（如 `click` 版本问题），确保开箱即用。

### 🛠️ 快速开始
1. **获取钥匙**：运行内置的提取脚本：
   ```bash
   python3 scripts/token_extractor.py
   ```
2. **配置列表**：将您的设备信息填入 `references/devices.md`。
3. **下达指令**：对着机器人喊：“打开热水器”或“查看加湿器状态”。

---
