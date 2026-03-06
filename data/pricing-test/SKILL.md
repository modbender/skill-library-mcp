---
name: pricing-test
description: 测试和校验 V3 API 模型的定价信息和实际扣费。当用户要测试模型价格、校验扣费、验证新模型定价、或提到"价格测试"、"扣费测试"时使用此 skill。
---

# V3 模型价格测试

测试和校验模型的定价信息展示与实际扣费是否正确。

## 价格换算规则

```
1 美元 = 400 积分
```

| Fal 定价 | 系统积分 | 计算公式 |
|---------|---------|---------|
| $0.05 | 20 | 0.05 × 400 |
| $0.075 | 30 | 0.075 × 400 |
| $0.10 | 40 | 0.10 × 400 |

## 测试流程

### 第一步：获取官方定价

访问模型的 fal.ai 定价页面，记录价格信息并换算为积分：

```
https://fal.ai/models/{MODEL_ID}
```

示例：https://fal.ai/models/wan/v2.6/image-to-video/flash

### 第二步：检查 Executor 配置

检查 `translate_api/app/api/v3/executors/` 下对应 Executor 的配置：

```python
# 检查项
PRICE_MAP = {...}           # 价格映射
DURATION_OPTIONS = [...]    # 时长选项
RESOLUTION_OPTIONS = [...]  # 分辨率选项

def get_price(self, model, params):
    # 价格计算逻辑
```

### 第三步：测试定价信息展示

```bash
curl -s 'http://127.0.0.1:8002/api/v3/models/{MODEL_ID}/docs' \
  -H 'Authorization: Bearer {API_KEY}' | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(json.dumps(d.get('data',{}).get('pricing',{}), indent=2, ensure_ascii=False))
"
```

**检查项**：
- `price_type` 应为 `duration_price`（视频模型）
- `price_description` 包含每秒价格
- `examples` 价格计算正确

### 第四步：测试实际扣费

```bash
curl -s 'http://127.0.0.1:8002/api/v3/tasks/create' \
  -H 'Authorization: Bearer {API_KEY}' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "model": "{MODEL_ID}",
    "params": {"prompt": "test", "image_url": "https://example.com/img.png", "duration": "5", "resolution": "1080p"}
  }' | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f\"扣费: {d['data']['price']} 积分\")
"
```

### 第五步：批量测试

运行测试脚本：

```bash
cd translate_api && python test_pricing.py
```

## 测试用例模板

| 参数 | 计算公式 | 预期 | 实际 | 结果 |
|------|---------|------|------|------|
| 5秒 720p | 5 × 20 | 100 | | |
| 5秒 1080p | 5 × 30 | 150 | | |
| 10秒 1080p | 10 × 30 | 300 | | |

## 新模型接入检查清单

```
- [ ] 获取官方定价信息
- [ ] 配置 Executor PRICE_MAP
- [ ] 实现 get_price() 方法
- [ ] 测试定价信息展示
- [ ] 测试实际扣费
- [ ] 添加测试用例
```

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 显示"按数量计费" | 未识别为视频模型 | 在 `_is_video_model()` 添加关键词 |
| 扣费固定 50 积分 | 数据库无配置且 Executor 未被调用 | 检查 Executor 注册 |
| 扣费与预期不符 | `get_price()` 计算错误 | 检查 PRICE_MAP 和计算逻辑 |

## 相关文件

- Executor 目录: `translate_api/app/api/v3/executors/`
- 计费逻辑: `translate_api/app/api/v2/pricing/fal_pricing.py`
- 测试脚本: `translate_api/test_pricing.py`
- 完整文档: [pricing-test-guide.md](../../../docs/pricing-test-guide.md)
