---
name: flight-price-plus
description: Flight price search. Trigger this skill immediately when the user asks about flights, airfare, ticket prices, cheapest dates, price calendars, departure times, or one-way/round-trip options. Supports both Chinese and English input, automatically converts city names to IATA airport codes, and handles one-way, round-trip, and price calendar (multi-date comparison) queries. Also trigger when the user says something like "I want to go to XX" and mentions flying.
---

# ✈️ 机票查询 Skill / Flight Search Skill

通过 `https://skill.flight.51smart.com/api/search` 查询实时机票，支持单程、往返、价格日历。  
Query real-time flights via the 51smart API (skill.flight.51smart.com). Supports one-way, round-trip, and price calendar.

> **注意 / Note:** 本 Skill 直接通过 HTTP POST 调用上述公开 API，无需本地脚本，无需认证。用户数据（城市/日期）仅用于航班查询，不做其他用途。  
> This skill calls the above public API directly via HTTP POST. No local scripts or authentication required. User data (city/date) is used solely for flight search.

---

## 工作流程 / Workflow

1. **解析输入** → 提取出发地、目的地、日期、乘客、舱位、行程类型
2. **补全信息** → 缺少必填字段时询问用户
3. **调用 API** → 直接 POST 到 `https://skill.flight.51smart.com/api/search`
4. **格式化输出** → 中英双语展示结果

---

## 第一步：解析用户输入 / Parse Input

| 字段 | 说明 | 默认值 | 必填 |
|------|------|--------|------|
| 出发城市 fromCity | IATA 机场代码 | — | ✅ |
| 目的城市 toCity | IATA 机场代码 | — | ✅ |
| 出发日期 fromDate | YYYY-MM-DD | — | ✅ |
| 返程日期 returnDate | YYYY-MM-DD | — | 往返必填 |
| 成人数 adultNumber | 整数 | 1 | — |
| 儿童数 childNumber | 整数 | 0 | — |
| 舱位 cabinClass | E/B/F/P | E | — |
| 行程类型 flightType | oneWay/roundTrip | oneWay | — |

**舱位代码对照 / Cabin Codes:**
- `E` = 经济舱 Economy
- `P` = 超级经济舱 Premium Economy  
- `B` = 商务舱 Business
- `F` = 头等舱 First

---

## 第二步：城市 → 机场代码 / City to IATA Code

### 中国 China
| 城市 | 代码 | 城市 | 代码 |
|------|------|------|------|
| 北京 Beijing | PEK/PKX | 上海虹桥 Shanghai Hongqiao | SHA |
| 上海浦东 Shanghai Pudong | PVG | 广州 Guangzhou | CAN |
| 深圳 Shenzhen | SZX | 成都 Chengdu | CTU |
| 杭州 Hangzhou | HGH | 南京 Nanjing | NKG |
| 武汉 Wuhan | WUH | 西安 Xi'an | XIY |
| 重庆 Chongqing | CKG | 厦门 Xiamen | XMN |
| 昆明 Kunming | KMG | 三亚 Sanya | SYX |
| 海口 Haikou | HAK | 青岛 Qingdao | TAO |
| 郑州 Zhengzhou | CGO | 长沙 Changsha | CSX |
| 济南 Jinan | TNA | 哈尔滨 Harbin | HRB |
| 沈阳 Shenyang | SHE | 大连 Dalian | DLC |
| 天津 Tianjin | TSN | 合肥 Hefei | HFE |
| 贵阳 Guiyang | KWE | 南宁 Nanning | NNG |
| 乌鲁木齐 Urumqi | URC | 拉萨 Lhasa | LXA |

### 国际 International
| 城市 | 代码 | 城市 | 代码 |
|------|------|------|------|
| 香港 Hong Kong | HKG | 台北 Taipei | TPE |
| 澳门 Macau | MFM | 东京成田 Tokyo Narita | NRT |
| 东京羽田 Tokyo Haneda | HND | 大阪 Osaka | KIX |
| 首尔 Seoul | ICN | 釜山 Busan | PUS |
| 新加坡 Singapore | SIN | 曼谷素万那普 Bangkok Suvarnabhumi | BKK |
| 曼谷廊曼 Bangkok Don Mueang | DMK | 吉隆坡 Kuala Lumpur | KUL |
| 雅加达 Jakarta | CGK | 马尼拉 Manila | MNL |
| 悉尼 Sydney | SYD | 墨尔本 Melbourne | MEL |
| 迪拜 Dubai | DXB | 阿布扎比 Abu Dhabi | AUH |
| 伦敦希思罗 London Heathrow | LHR | 伦敦盖特威克 London Gatwick | LGW |
| 巴黎 Paris | CDG | 法兰克福 Frankfurt | FRA |
| 阿姆斯特丹 Amsterdam | AMS | 罗马 Rome | FCO |
| 纽约肯尼迪 New York JFK | JFK | 纽约纽瓦克 New York Newark | EWR |
| 洛杉矶 Los Angeles | LAX | 旧金山 San Francisco | SFO |
| 拉斯维加斯 Las Vegas | LAS | 芝加哥 Chicago | ORD |
| 温哥华 Vancouver | YVR | 多伦多 Toronto | YYZ |

> 未在上表中的城市，请根据通用 IATA 代码规则推断，或询问用户确认机场全称。

---

## 第三步：调用 API / Call API

直接发起 HTTP POST 请求，**无需运行任何本地脚本**。

**Endpoint:** `POST https://skill.flight.51smart.com/api/search`  
**Content-Type:** `application/json`  
**认证 Auth:** 无需 / Not required

### 单程请求示例 One-way Request

```json
{
  "adultNumber": 1,
  "cabinClass": "E",
  "childNumber": 0,
  "cid": "123456",
  "flightType": "oneWay",
  "flights": [
    {
      "fromCity": "PEK",
      "fromDate": "2026-03-15",
      "toCity": "SHA"
    }
  ]
}
```

### 往返请求示例 Round-trip Request

```json
{
  "adultNumber": 2,
  "cabinClass": "B",
  "childNumber": 1,
  "cid": "123456",
  "flightType": "roundTrip",
  "flights": [
    { "fromCity": "PEK", "fromDate": "2026-03-15", "toCity": "NRT" },
    { "fromCity": "NRT", "fromDate": "2026-03-22", "toCity": "PEK" }
  ]
}
```

### 价格日历 Price Calendar

价格日历通过连续发送多个单程请求（每天一次）实现，将结果汇总展示。  
Price calendar is achieved by sending multiple one-way requests for consecutive dates and aggregating results.

---

## 第四步：格式化输出 / Format Output

### 单程/往返 结果展示

```
✈️ 北京 (PEK) → 上海 (SHA)    Beijing → Shanghai
📅 2026年3月15日 / Mar 15, 2026  |  经济舱 Economy  |  成人×1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 #  航班        出发→到达          时长   经停  票价(USD)  行李
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 1  UA1597      22:38→00:06(+1)   1h28m  直飞  $81.86   1PC/23KG
 2  CA1234      09:00→11:20       2h20m  直飞  $95.00   1PC/23KG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
共 2 个航班  /  2 flights found
最低价 Lowest: $81.86 (税前 before tax)，含税 incl. tax: $116.80
```

### 价格日历 结果展示

```
📅 价格日历 / Price Calendar
✈️ 上海 (SHA) → 洛杉矶 (LAX)  |  经济舱 Economy

日期 Date        最低价 Lowest    航班数
─────────────────────────────────────
2026-04-01      $520.00 ⭐       8班
2026-04-02      $490.00 🏆最低   6班
2026-04-03      $535.00          7班
2026-04-04      $510.00          5班
2026-04-05      $580.00          6班
─────────────────────────────────────
推荐出发日 / Best date: 2026-04-02 ($490.00)
```

### 字段解释规则

- **含税总价** = `price` + `tax`（成人价格）
- **多乘客** = 成人含税价 × adultNumber + 儿童含税价 × childNumber
- **经停** = segments 数量 - 1，`stopQuantity > 0` 时显示经停城市
- **行李** = `baggages[].pieces` + `baggages[].weight`，`freeBaggage: false` 时注明需额外购买
- **座位紧张** = `maxSeatsRemain ≤ 3` 时显示 ⚠️ 仅剩X席

---

## 响应关键字段 / Key Response Fields

| 字段 | 说明 |
|------|------|
| `status` | 0 = 成功 success |
| `message` | "SUCCESS" 表示正常 |
| `routings[]` | 航班方案列表 |
| `routings[].prices[]` | 按乘客类型分开的价格（ADT=成人, CHD=儿童） |
| `routings[].segments[]` | 航段详情（每个经停是一个segment） |
| `routings[].rule.baggages[]` | 免费行李额 |
| `routings[].rule.freeBaggage` | false = 行李需额外购买 |
| `routings[].maxSeatsRemain` | 剩余座位数 |
| `passengerType` | ADT = 成人 Adult, CHD = 儿童 Child |

---

## 错误处理 / Error Handling

| 情况 | 处理方式 |
|------|---------|
| `status != 0` 或 `message != "SUCCESS"` | 告知用户查询失败，建议换日期重试 |
| `routings` 为空列表 | 提示该路线/日期无可用航班 |
| 网络超时 | 重试一次，失败则提示用户稍后再试 |
| 城市代码无法识别 | 询问用户确认城市全称或机场名称 |
| 儿童数 > 成人数 | 提示：儿童数量不能超过成人数量 |
