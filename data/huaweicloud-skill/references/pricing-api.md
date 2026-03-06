# 华为云价格计算 API

本文档整理华为云价格查询和成本预估的方法。

## 目录

1. [概述](#概述)
2. [价格计算器 API](#价格计算器-api)
3. [常用产品价格公式](#常用产品价格公式)
4. [价格计算脚本](#价格计算脚本)
5. [成本优化建议](#成本优化建议)

---

## 概述

华为云提供多种价格查询方式：

| 方式 | 特点 | 适用场景 |
|------|------|----------|
| 控制台价格计算器 | 可视化、易用 | 手动估算 |
| BSS API | 编程查询 | 自动化集成 |
| 定价页面 | 静态价格表 | 快速参考 |
| 本脚本工具 | 离线估算 | Skill 内部调用 |

### 计费模式

| 模式 | 说明 | 折扣 | 适用场景 |
|------|------|------|----------|
| 按需 | 按小时计费 | 无 | 临时、测试 |
| 包年包月 | 预付费 | 15-40% | 长期稳定 |
| 竞价实例 | 竞价购买 | 60-90% | 可中断任务 |
| 预留实例 | 预留资源 | 30-50% | 可预测负载 |

---

## 价格计算器 API

### BSS API 端点

```
https://bss.myhuaweicloud.com
```

### 查询产品价格

**请求示例：**

```bash
curl -X POST "https://bss.myhuaweicloud.com/v2/products/prices" \
  -H "X-Auth-Token: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "product_infos": [
      {
        "id": "1",
        "cloud_service_type": "hws.service.type.ec2",
        "resource_type": "hws.resource.type.vm",
        "resource_spec": "s6.large.2.linux",
        "region": "cn-north-4",
        "usage_factor": "Duration",
        "usage_value": 1,
        "usage_measure_id": 4
      }
    ]
  }'
```

### 响应结构

```json
{
  "official_website_rating_results": [
    {
      "official_website_amount": "0.2",
      "measure_id": 1,
      "product_rating_results": [
        {
          "id": "1",
          "total_amount": "0.2"
        }
      ]
    }
  ]
}
```

### 参数说明

| 参数 | 说明 |
|------|------|
| cloud_service_type | 云服务类型代码 |
| resource_type | 资源类型代码 |
| resource_spec | 资源规格代码 |
| region | 区域代码 |
| usage_value | 使用量 |
| usage_measure_id | 计量单位ID |

### 常用云服务类型

| 服务 | cloud_service_type | resource_type |
|------|-------------------|---------------|
| ECS | hws.service.type.ec2 | hws.resource.type.vm |
| EVS | hws.service.type.ebs | hws.resource.type.volume |
| OBS | hws.service.type.obs | hws.resource.type.capacity |
| RDS | hws.service.type.rds | hws.resource.type.instance |
| EIP | hws.service.type.vpc | hws.resource.type.bandwidth |
| ELB | hws.service.type.elb | hws.resource.type.loadbalancer |

### 计量单位 ID

| ID | 单位 |
|----|------|
| 1 | 元 |
| 4 | 小时 |
| 10 | GB |
| 11 | MB |
| 13 | 个 |

---

## 常用产品价格公式

### ECS 云服务器

**按需计费：**
```
月费用 = 小时价格 × 24 × 30 × 实例数量
```

**包年包月：**
```
月费用 = 月价格 × 实例数量
年费用 = 年价格 × 实例数量（通常享折扣）
```

**参考价格（华北-北京四，按需）：**

| 规格 | vCPU | 内存 | 按需(元/小时) | 包月(元) |
|------|------|------|--------------|---------|
| s6.small.1 | 1 | 1 | 0.09 | 45 |
| s6.medium.2 | 1 | 2 | 0.13 | 68 |
| s6.large.2 | 2 | 4 | 0.26 | 130 |
| s6.xlarge.2 | 4 | 8 | 0.52 | 260 |
| s6.2xlarge.2 | 8 | 16 | 1.04 | 520 |
| c6.xlarge.4 | 4 | 16 | 0.80 | 400 |
| m6.xlarge.8 | 4 | 32 | 1.20 | 600 |

*价格仅供参考，以官网为准*

---

### RDS 数据库

**计费公式：**
```
费用 = 规格费用 + 存储费用 + 备份费用
```

**参考价格（MySQL，华北-北京四）：**

| 规格 | vCPU | 内存 | 按需(元/小时) | 包月(元) |
|------|------|------|--------------|---------|
| rds.mysql.c6.large.2 | 2 | 4 | 0.68 | 340 |
| rds.mysql.c6.xlarge.2 | 4 | 8 | 1.36 | 680 |
| rds.mysql.c6.2xlarge.2 | 8 | 16 | 2.72 | 1360 |

**存储：**
- SSD 云盘：约 0.35 元/GB/月
- 极速型SSD：约 0.50 元/GB/月

---

### OBS 对象存储

**计费公式：**
```
费用 = 存储费用 + 流量费用 + 请求费用
```

**参考价格：**

| 存储类型 | 价格(元/GB/月) |
|----------|---------------|
| 标准存储 | 0.12 |
| 低频存储 | 0.08 |
| 归档存储 | 0.033 |

**流量：**
- 内网流量：免费
- 公网流出：0.50 元/GB（阶梯递减）

---

### EVS 云硬盘

**参考价格：**

| 磁盘类型 | 价格(元/GB/月) |
|----------|---------------|
| 普通IO (SATA) | 0.20 |
| 高IO (SAS) | 0.30 |
| 通用型SSD | 0.35 |
| 极速型SSD | 0.50 |

---

### EIP 弹性公网IP

**按带宽计费：**
```
费用 = 带宽价格 + EIP保有费用
```

**按流量计费：**
```
费用 = 流量费用（无保有费）
```

**参考价格：**

| 带宽 | 按带宽(元/月) | 按流量(元/GB) |
|------|--------------|--------------|
| 1Mbps | 23 | 0.80 |
| 5Mbps | 115 | 0.80 |
| 10Mbps | 230 | 0.80 |
| 20Mbps | 460 | 0.80 |

---

### ELB 负载均衡

**参考价格：**

| 类型 | 按需(元/小时) | 包月(元) |
|------|--------------|---------|
| 共享型 | 0.05 | 36 |
| 独享型 | 0.30+ | 200+ |

---

### DCS Redis 缓存

**参考价格：**

| 规格 | 内存 | 按需(元/小时) | 包月(元) |
|------|------|--------------|---------|
| 单机 | 2GB | 0.08 | 58 |
| 主备 | 2GB | 0.16 | 116 |
| 集群 | 4GB | 0.40 | 290 |

---

## 价格计算脚本

详见 `scripts/hwc-pricing.py`，脚本功能：

1. 解析资源清单
2. 查询实时价格（需要 AK/SK）
3. 计算总成本
4. 输出 Markdown 报告

### 使用方法

```bash
# 设置凭证
export HWC_ACCESS_KEY="your-ak"
export HWC_SECRET_KEY="your-sk"

# 运行计算
python scripts/hwc-pricing.py --input resources.json --output cost.md
```

### 输入格式

```json
{
  "region": "cn-north-4",
  "billing_mode": "monthly",
  "resources": [
    {
      "type": "ecs",
      "spec": "s6.xlarge.2",
      "count": 2
    },
    {
      "type": "rds",
      "spec": "rds.mysql.c6.xlarge.2",
      "storage": 100
    },
    {
      "type": "eip",
      "bandwidth": 10
    }
  ]
}
```

### 输出格式

```markdown
## 成本预估（月度）

| 资源 | 规格 | 单价 | 数量 | 月费用 |
|------|------|------|------|--------|
| ECS | s6.xlarge.2 | ¥260 | 2 | ¥520 |
| RDS MySQL | c6.xlarge.2 | ¥680 | 1 | ¥680 |
| EIP | 10Mbps | ¥230 | 1 | ¥230 |
| EVS SSD | 100GB | ¥0.35/GB | 1 | ¥35 |
| **合计** | | | | **¥1,465** |

*价格仅供参考，以实际账单为准*
```

---

## 成本优化建议

### 1. 选择合适的计费模式

```
使用时长 < 3个月 → 按需
使用时长 > 6个月 → 包年包月
可中断任务 → 竞价实例
稳定负载 → 预留实例
```

### 2. 合理配置规格

- CPU 利用率 < 30%：考虑降配
- 内存利用率 < 40%：考虑降配
- 避免过度配置

### 3. 使用资源优化工具

- 云监控分析使用趋势
- CTS 审计资源使用
- 成本中心分析支出

### 4. 存储优化

- OBS 生命周期：自动转低频/归档
- EVS 快照：定期清理旧快照
- RDS 备份：设置合理保留期

### 5. 网络优化

- 内网通信优先（免费）
- EIP 按需绑定
- CDN 加速减少源站流量

### 6. 企业优惠

- 企业项目折扣
- 大客户专属优惠
- 长期使用返佣

---

## 价格查询链接

- [华为云价格计算器](https://www.huaweicloud.com/pricing.html)
- [ECS 价格](https://www.huaweicloud.com/pricing.html#/ecs)
- [RDS 价格](https://www.huaweicloud.com/pricing.html#/rds)
- [OBS 价格](https://www.huaweicloud.com/pricing.html#/obs)
- [价格详情 API](https://support.huaweicloud.com/api-bss/bss_10_0010.html)

---

*注：价格经常调整，本文档价格仅供参考，请以官网实时价格为准。*
