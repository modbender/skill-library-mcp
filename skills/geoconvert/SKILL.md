---
name: jisu-geoconvert
description: 使用极速数据经纬度地址转换 API，在百度/Google 坐标系下实现经纬度与地址的相互转换。
metadata: { "openclaw": { "emoji": "📍", "requires": { "bins": ["python3"], "env": ["JISU_API_KEY"] }, "primaryEnv": "JISU_API_KEY" } }
---

# 极速数据经纬度地址转换（Jisu GeoConvert）

基于 [经纬度地址转换 API](https://www.jisuapi.com/api/geoconvert/) 的 OpenClaw 技能，支持：

- **经纬度转地址**（`/geoconvert/coord2addr`）
- **地址转经纬度**（`/geoconvert/addr2coord`）

可选择使用 `baidu` 或 `google` 类型的地理编码服务。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/geoconvert/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/geoconvert/geoconvert.py`

## 使用方式

### 1. 经纬度转地址（/geoconvert/coord2addr）

```bash
python3 skills/geoconvert/geoconvert.py coord2addr '{"lat":"30.2812129803","lng":"120.11523398","type":"baidu"}'
```

请求 JSON：

```json
{
  "lat": "30.2812129803",
  "lng": "120.11523398",
  "type": "baidu"
}
```

### 2. 地址转经纬度（/geoconvert/addr2coord）

```bash
python3 skills/geoconvert/geoconvert.py addr2coord '{"address":"益乐路39号","type":"baidu"}'
```

请求 JSON：

```json
{
  "address": "益乐路39号",
  "type": "baidu"
}
```

`type` 说明：  
- `baidu`：使用百度地图坐标  
- `google`：使用 Google Maps 坐标  

## 请求参数

### 经纬度转地址

| 字段名 | 类型   | 必填 | 说明                        |
|--------|--------|------|-----------------------------|
| lat    | string | 是   | 纬度                        |
| lng    | string | 是   | 经度                        |
| type   | string | 否   | 类型，`baidu` 或 `google`，默认 baidu |

### 地址转经纬度

| 字段名  | 类型   | 必填 | 说明                        |
|---------|--------|------|-----------------------------|
| address | string | 是   | 地址                        |
| type    | string | 否   | 类型，`baidu` 或 `google`，默认 baidu |

## 返回结果示例（节选）

### 经纬度转地址

```json
{
  "lat": "30.2812129803",
  "lng": "120.11523398",
  "type": "google",
  "address": "中国浙江省杭州市西湖区文二西路11号 邮政编码: 310000",
  "country": "中国",
  "province": "浙江省",
  "city": "杭州市",
  "district": "西湖区",
  "description": ""
}
```

### 地址转经纬度

```json
{
  "address": "益乐路39号",
  "type": "google",
  "lat": "30.279864",
  "lng": "120.113885",
  "fulladdress": "中国浙江省杭州市西湖区益乐路39号 邮政编码: 310000",
  "precise": "",
  "confidence": "",
  "level": "street_address"
}
```

## 常见错误码

来源于 [官方经纬度文档](https://www.jisuapi.com/api/geoconvert/)：

| 代号 | 说明         |
|------|--------------|
| 201  | 经纬度为空   |
| 202  | 地址为空     |
| 203  | 经纬度不正确 |
| 210  | 没有信息     |

系统错误码：

| 代号 | 说明                 |
|------|----------------------|
| 101  | APPKEY 为空或不存在  |
| 102  | APPKEY 已过期        |
| 103  | APPKEY 无请求权限    |
| 104  | 请求超过次数限制     |
| 105  | IP 被禁止            |

## 在 OpenClaw 中的推荐用法

1. 用户给出坐标：「这个点 `30.2812129803,120.11523398` 是哪里？」  
2. 代理构造 JSON：`{"lat":"30.2812129803","lng":"120.11523398","type":"baidu"}` 并调用：  
   `python3 skills/geoconvert/geoconvert.py coord2addr '{"lat":"30.2812129803","lng":"120.11523398","type":"baidu"}'`  
3. 从返回结果中读取 `address/country/province/city/district` 字段，为用户总结清晰的地址描述；  
4. 反向场景下，可根据用户提供的地址调用 `addr2coord` 获取经纬度，用于后续地图或定位相关技能。  

