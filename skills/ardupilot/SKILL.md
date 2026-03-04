---
name: ardupilot
description: 通过 pymavlink 连接并控制 ArduPilot 无人机。使用此 skill 来操作无人机起飞、降落、移动等。
---

# ArduPilot 无人机控制 Skill

通过 pymavlink 连接并控制 ArduPilot 无人机 (如 CubeOrange 等)。

## ⚠️ 重要：起飞核心流程

**起飞必须连续发送命令，不要等待！**

```python
# 1. 等待飞控稳定 (status=3)
while True:
    msg = master.wait_heartbeat(timeout=3)
    if msg and msg.system_status == 3:
        break

# 2. 连续发送：ARM → GUIDED → TAKEOFF (不要等待!)
master.mav.command_long_send(1, 1, 400, 0, 1, 21196, 0, 0, 0, 0, 0)  # ARM (force=21196)
mode_map = master.mode_mapping()
master.set_mode(mode_map['GUIDED'])  # GUIDED
master.mav.command_long_send(1, 1, 22, 0, 0, 0, 0, 0, 0, 0, 5)  # TAKEOFF 5m

# 3. 监控高度
for i in range(40):
    msg = master.recv_match(type='GLOBAL_POSITION_INT', timeout=0.5)
    if msg:
        alt = msg.relative_alt / 1000
        if alt >= 4.5:
            print('✅ 到达目标高度!')
            break
```

**关键点**：
- 发送 ARM 后立即发送 GUIDED 和 TAKEOFF，不要等待
- 如果等待，飞控会重新上锁
- force=21196 是 ArduPilot 的 magic value

---

## 连接

```python
from pymavlink import mavutil

master = mavutil.mavlink_connection('tcp:localhost:5762')
master.wait_heartbeat(timeout=10)

system_id = master.target_system  # 通常是 1
component_id = master.target_component
```

## 1. 检查状态

```python
# 获取飞控状态
msg = master.wait_heartbeat(timeout=5)
print(f'status: {msg.system_status}')  # 0=boot, 3=standby, 4=armed

# 获取高度
msg = master.recv_match(type='GLOBAL_POSITION_INT', timeout=1)
print(f'高度: {msg.relative_alt / 1000}m')

# 获取 GPS
msg = master.recv_match(type='GPS_RAW_INT', timeout=1)
print(f'GPS: {msg.satellites_visible}颗, fix={msg.fix_type}')

# 获取电池
msg = master.recv_match(type='SYS_STATUS', timeout=1)
print(f'电池: {msg.voltage_battery / 1000}V')
```

## 2. 起飞 (关键流程)

```python
# ⚠️ 必须等待飞控稳定 (status=3)
while True:
    msg = master.wait_heartbeat(timeout=3)
    if msg and msg.system_status == 3:
        break

# ⚠️ 连续发送命令，不要等待!
master.mav.command_long_send(1, 1, 400, 0, 1, 21196, 0, 0, 0, 0, 0)  # ARM
mode_map = master.mode_mapping()
master.set_mode(mode_map['GUIDED'])  # GUIDED
master.mav.command_long_send(1, 1, 22, 0, 0, 0, 0, 0, 0, 0, 8)  # TAKEOFF 8m

# 闭环监控
for i in range(40):
    msg = master.recv_match(type='GLOBAL_POSITION_INT', timeout=0.5)
    if msg:
        alt = msg.relative_alt / 1000
        print(f'{i*0.5:.1f}s → {alt:.2f}m')
        if alt >= 7.2:  # 90% 目标
            print('✅ 到达!')
            break
```

## 3. 降落

```python
# 切换到 LAND 模式
mode_map = master.mode_mapping()
master.set_mode(mode_map['LAND'])

# ⚠️ 必须持续发送 LAND 命令
for i in range(60):
    master.mav.command_long_send(1, 1, 21, 0, 0, 0, 0, 0, 0, 0, 0)
    import time
    time.sleep(0.5)
    
    msg = master.recv_match(type='GLOBAL_POSITION_INT', timeout=0.3)
    if msg:
        alt = msg.relative_alt / 1000
        if alt < 0.3:
            print('✅ 降落完成!')
            break
```

## 4. 相对移动 (LOCAL_POSITION_NED)

```python
# 获取当前位置
local = master.recv_match(type='LOCAL_POSITION_NED', timeout=1)

# X轴前进2米 (NED: X=北)
master.mav.set_position_target_local_ned_send(
    0, system_id, component_id,
    mavutil.mavlink.MAV_FRAME_LOCAL_NED,
    0b0000111111111000,
    local.x + 2, local.y, local.z,
    0, 0, 0, 0, 0, 0, 0, 0
)
```

## 坐标系 (NED)

- **X轴**: 北 (正=北)
- **Y轴**: 东 (正=东)
- **Z轴**: 向下 (负值=向上=高度)

---

## 完整示例

```python
from pymavlink import mavutil
import time

master = mavutil.mavlink_connection('tcp:localhost:5762')
master.wait_heartbeat(timeout=10)

print('=== 起飞到 5m ===')

# 1. 等待飞控稳定
while True:
    msg = master.wait_heartbeat(timeout=3)
    if msg and msg.system_status == 3:
        break
print('飞控就绪')

# 2. 连续发送: ARM → GUIDED → TAKEOFF
master.mav.command_long_send(1, 1, 400, 0, 1, 21196, 0, 0, 0, 0, 0)
mode_map = master.mode_mapping()
master.set_mode(mode_map['GUIDED'])
master.mav.command_long_send(1, 1, 22, 0, 0, 0, 0, 0, 0, 0, 5)
print('ARM + GUIDED + TAKEOFF')

# 3. 闭环监控
for i in range(40):
    msg = master.recv_match(type='GLOBAL_POSITION_INT', timeout=0.5)
    if msg:
        alt = msg.relative_alt / 1000
        print(f'{i*0.5:.1f}s → {alt:.2f}m')
        if alt >= 4.5:
            print('✅ 5m!')
            break
```

```python
# === 降落 ===
mode_map = master.mode_mapping()
master.set_mode(mode_map['LAND'])

for i in range(60):
    master.mav.command_long_send(1, 1, 21, 0, 0, 0, 0, 0, 0, 0, 0)
    time.sleep(0.5)
    
    msg = master.recv_match(type='GLOBAL_POSITION_INT', timeout=0.3)
    if msg:
        alt = msg.relative_alt / 1000
        if alt < 0.3:
            print('✅ 降落完成!')
            break
```

---

## 注意事项

1. **起飞**：连续发送命令，不要等待
2. **降落**：持续发送 LAND 命令
3. **闭环检查**：每次操作前后获取状态
4. **GUIDED 模式**：自主飞行必须用 GUIDED
5. **GPS**：确保 fix_type >= 3
6. **端口**：常用 TCP 5762

---

## 依赖

```bash
pip install pymavlink
```
