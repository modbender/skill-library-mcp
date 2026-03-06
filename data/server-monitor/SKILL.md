---
name: server-monitor
description: 服务器监控技能 - 监控服务器状态、磁盘使用率、内存使用率、CPU负载等
version: 1.0.0
author: michaelhotss
metadata:
  category: monitoring
  tags:
    - server
    - monitoring
    - system
    - health
    - diagnostics
  performance: 快速响应，低资源消耗
  modules: 系统状态监控模块
---

# 服务器监控技能

这是一个用于监控服务器状态的技能，可以帮助你实时了解服务器的健康状况。

## 功能特性

- ✅ **系统状态监控**：检查服务器运行状态
- ✅ **磁盘使用率**：监控磁盘空间使用情况
- ✅ **内存监控**：查看内存使用率和可用内存
- ✅ **CPU负载**：监控CPU使用率和负载
- ✅ **进程监控**：查看运行中的关键进程
- ✅ **网络状态**：检查网络连接和端口状态

## 使用方法

当用户询问服务器状态时，自动运行系统检查并返回详细报告。

## 安装要求

- Linux 系统
- 基本的系统工具（df, free, top, ps, netstat等）

## 配置示例

无需特殊配置，开箱即用。

## 更新日志

### v1.0.0 (2026-02-10)
- 初始版本发布
- 基础系统监控功能
- 磁盘、内存、CPU监控