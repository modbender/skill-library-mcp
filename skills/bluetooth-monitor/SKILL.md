---
name: bluetooth-monitor
description: "蓝牙设备监控 / Bluetooth Device Monitor - 查看Mac已连接的蓝牙设备列表，支持配对、连接、断开操作"
---

# 蓝牙设备监控 / Bluetooth Device Monitor

监控和管理Mac的蓝牙设备，支持查看连接状态、配对管理等功能。

Monitor and manage Mac Bluetooth devices with connection status viewing and pairing management.

## 功能特性 / Features

- 📱 **查看已连接设备 / Connected Devices** - 列出当前所有已连接的蓝牙设备
  - List all currently connected Bluetooth devices

- 🔋 **电量显示 / Battery Level** - 显示设备电量百分比和进度条
  - Display device battery percentage with progress bar

- 🔗 **查看已配对设备 / Paired Devices** - 列出系统所有已配对的蓝牙设备
  - List all paired Bluetooth devices in the system

- 🔌 **连接设备 / Connect Device** - 手动连接到指定蓝牙设备
  - Manually connect to a specified Bluetooth device

- ⏏️ **断开设备 / Disconnect Device** - 断开指定蓝牙设备的连接
  - Disconnect a specified Bluetooth device

- 📊 **蓝牙状态 / Power Status** - 查看蓝牙开关状态
  - View Bluetooth power status

## 使用方法 / Usage

### 1. 查看已连接设备 / View Connected Devices
```bash
bluetooth-monitor connected
```

### 2. 查看已配对设备 / View Paired Devices
```bash
bluetooth-monitor paired
```

### 3. 连接设备 / Connect Device
```bash
# 连接设备（需提供设备地址）
# Connect to device (device address required)
bluetooth-monitor connect "XX-XX-XX-XX-XX-XX"
```

### 4. 断开设备 / Disconnect Device
```bash
bluetooth-monitor disconnect "XX-XX-XX-XX-XX-XX"
```

### 5. 查看蓝牙电源状态 / View Power Status
```bash
bluetooth-monitor power
```

### 6. 打开/关闭蓝牙 / Turn On/Off Bluetooth
```bash
bluetooth-monitor power on
bluetooth-monitor power off
```

## 设备地址获取 / Device Address

- 运行 `bluetooth-monitor connected` 查看已连接设备的地址
- Run `bluetooth-monitor connected` to view addresses of connected devices

- 运行 `bluetooth-monitor paired` 查看所有配对设备的地址
- Run `bluetooth-monitor paired` to view all paired device addresses

## 常用设备地址格式 / Common Device Address Format

```
08-65-18-B9-9C-B2  (Magic Trackpad)
1C-1D-D3-7A-68-D4  (Magic Keyboard)
```

## 注意事项 / Notes

⚠️ 需要安装 `blueutil`: `brew install blueutil`
⚠️ Requires `blueutil`: `brew install blueutil`

⚠️ 部分老款蓝牙设备不支持电量报告
⚠️ Some older Bluetooth devices may not report battery level

⚠️ 设备地址需使用连字符格式 (XX-XX-XX-XX-XX-XX)
⚠️ Device address must use hyphen format (XX-XX-XX-XX-XX-XX)

## 数据来源 / Data Source

使用 blueutil CLI 获取蓝牙信息
Uses blueutil CLI to retrieve Bluetooth information
