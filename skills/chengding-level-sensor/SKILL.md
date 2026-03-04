---
name: chengding-level-sensor
description: 读取橙丁物联液位传感器设备状态。使用场景：(1)查询液位传感器在线状态 (2)获取设备开关状态 (3)定时监控液位设备。需要提前配置 key、tel、imei 参数。
---

# 橙丁物联液位传感器

## 快速查询

```bash
curl -s -X POST "https://www.cd6969.com/admin.php?s=/Admin/ApiV2/getList.html" \
  -H "Content-Type: application/json" \
  -d '{"key":"你的KEY","tel":"你的手机号"}'
```

## 配置参数

| 参数 | 值 |
|------|-----|
| key | 你的KEY
| tel | 你的手机号
| imei | 你的IMEI

## 响应说明

- `online`: 1=在线, 0=离线
- `status`: 开关状态，最长8位，第1位表示第1路状态
  - 0=已关闭
  - 1=已打开
  - 2=关闭中
  - 3=打开中
  - 4=点动中
  - 5=点动完成或已关闭

## 使用脚本

```bash
./scripts/get_status.sh
```

返回 JSON 格式的设备状态。
