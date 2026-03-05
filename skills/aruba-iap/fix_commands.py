#!/usr/bin/env python3
"""
修复 Aruba-IAP 设备模式检测和命令选择逻辑

问题：
1. 单节点 Instant AP（配置了 virtual-controller-key 但只有一个 AP）的设备模式检测不正确
2. 对于这种设备，standalone 模式的命令（wlan, show ap info）返回解析错误
3. 需要使用 Instant AP 特定的命令（show ap bss-table, show ap association）

解决方案：
1. 改进设备模式检测，添加 "single-node-cluster" 模式
2. 为 single-node-cluster 模式添加特定的命令映射
3. 增强命令回退逻辑，尝试多个可能的命令
"""

设备模式总结：
==============

测试设备：192.168.20.56
型号：Aruba IAP 224
固件：ArubaOS 8.6.0.14
配置：有 virtual-controller-key，但只有一个 AP 在线

命令测试结果：
-------------

✅ 工作的命令：
- show version
- show running-config
- show interface
- show ap bss-table (WLAN/BSSID 信息)
- show ap association (关联的客户端)
- show ap port (端口信息)
- show users

❌ 不工作的命令（返回解析错误）：
- show wlan
- wlan
- show ap database
- show ap info
- show ap-role
- show ap-group
- show master
- show controller
- show user-table
- show ap radio-info
- show radio (Incomplete command)

❓ 需要子命令的命令：
- show ap (需要子命令)
- show ap debug (需要子命令)

设备模式分析：
============

当前检测逻辑：
1. 检查 show version 输出中的 "Virtual Controller" 或 "Master" 关键字 → 没有找到
2. 检查 show role 命令输出 → 命令不工作，返回解析错误
3. 尝试获取 AP 列表（show ap database 或 show ap info）→ 都返回解析错误
4. 默认为 standalone 模式

问题：
- standalone 模式的命令（wlan, show ap info）在这个设备上不工作
- 需要一个更细致的设备模式分类

建议的设备模式分类：
===================

1. **virtual-controller**：真正的 VC，有多个 AP 在线
   - show ap database 返回多个 AP
   - show wlan 工作正常

2. **single-node-cluster**：单节点集群（有 virtual-controller-key 配置）
   - 有 virtual-controller-key 配置
   - 只有 1-2 个 BSS（同一个 AP 的两个频段）
   - 使用 Instant AP 命令：show ap bss-table, show ap association

3. **standalone**：真正的独立 AP（没有 VC 配置）
   - 没有 virtual-controller-key 配置
   - 使用基本命令：show wlan, show ap info（如果支持）

改进的设备模式检测逻辑：
========================

def detect_device_mode() -> dict:
    version_info = self.get_version()

    # 检查 1: VC 关键字在版本输出中
    if version_info.get("is_vc"):
        return {
            "mode": "virtual-controller",
            "is_vc": True,
            "role": "virtual-controller",
        }

    # 检查 2: 配置中有 virtual-controller-key
    try:
        config_output = self.send_command("show running-config")
        if "virtual-controller-key" in config_output:
            # 有 VC 配置，检查 AP 数量
            try:
                bss_output = self.send_command("show ap bss-table")
                # 解析 BSS 数量
                if "Num APs:" in bss_output:
                    import re
                    match = re.search(r"Num APs:(\d+)", bss_output)
                    if match:
                        num_aps = int(match.group(1))
                        if num_aps > 2:  # 超过 2 个 BSS（考虑到同一个 AP 的两个频段）
                            return {
                                "mode": "virtual-controller",
                                "is_vc": True,
                                "role": "virtual-controller",
                                "ap_count": num_aps,
                            }
                        else:
                            return {
                                "mode": "single-node-cluster",
                                "is_vc": False,
                                "role": "single-node-cluster",
                                "ap_count": num_aps,
                            }
            except:
                pass

            # 如果无法确定 AP 数量，但有 VC 配置，默认为单节点集群
            return {
                "mode": "single-node-cluster",
                "is_vc": False,
                "role": "single-node-cluster",
            }
    except:
        pass

    # 检查 3: 尝试传统的 AP 数据库检查
    try:
        ap_list = self.get_ap_info()
        if len(ap_list) > 1:
            return {
                "mode": "virtual-controller",
                "is_vc": True,
                "role": "virtual-controller",
                "ap_count": len(ap_list),
            }
    except Exception:
        pass

    # 默认: standalone AP
    return {
        "mode": "standalone",
        "is_vc": False,
        "role": "standalone",
    }

改进的命令映射：
===============

| 操作 | VC 模式 | 单节点集群 | 独立 AP |
|------|---------|-----------|---------|
| AP 信息 | show ap database | show ap bss-table | show ap info |
| WLAN 信息 | show wlan | show ap bss-table | wlan |
| 关联的客户端 | show ap association | show ap association | show ap association |
| 用户表格 | show user-table | show users | show users |
| 端口信息 | show interface | show ap port | show interface |

实现优先级：
============

1. 立即：更新文档，说明单节点集群的特殊情况
2. 短期：实现改进的设备模式检测逻辑
3. 中期：为 single-node-cluster 模式添加完整的命令映射
4. 长期：增强命令回退逻辑，自动尝试多个可能的命令

测试计划：
=========

1. 测试改进的设备模式检测逻辑
2. 测试 single-node-cluster 模式的命令映射
3. 验证所有工件在单节点集群模式下正常生成
4. 确保向后兼容性（不破坏现有的 VC 和 standalone 模式）
