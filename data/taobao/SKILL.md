---
name: maishou
description: 获取商品在淘宝(Taobao)、天猫(TMall)、京东(JD.com)、拼多多(PinDuoDuo)、抖音(Douyin)、快手(KaiShou)的最优价格、优惠券的技能，商品价格全网对比，当用户想购物或者获取优惠信息时使用。Get the best price, coupons for goods on Chinese e-commerce platforms, compare product prices, and use when users want to shop or get discount information.
homepage: https://github.com/aahl/skills/blob/main/skills/maishou/SKILL.md
metadata:
  {
    "openclaw":
      {
        "emoji": "🛍️",
        "requires": { "bins": ["uv"] },
        "install":
          [
            {"id": "uv-brew", "kind": "brew", "formula": "uv", "bins": ["uv"], "label": "Install uv (brew)"},
            {"id": "uv-pip", "kind": "pip", "formula": "uv", "bins": ["uv"], "label": "Install uv (pip)"},
            {"id": "pip-aiohttp", "kind": "pip", "formula": "aiohttp", "label": "Install aiohttp (pip)"},
            {"id": "pip-argparse", "kind": "pip", "formula": "argparse", "label": "Install argparse (pip)"},
            {"id": "pip-PyYAML", "kind": "pip", "formula": "PyYAML", "label": "Install PyYAML (pip)"},
          ],
      },
  }
---

# 买手技能
获取中国在线购物平台商品价格、优惠券，全网比价

```yaml
# 参数解释
source:
  1: 淘宝/天猫
  2: 京东
  3: 拼多多
  7: 抖音
  8: 快手
```

## 搜索商品
```shell
uv run scripts/main.py search --source={source} --keyword='{keyword}'
uv run scripts/main.py search --source={source} --keyword='{keyword}' --page=2
```

## 商品详情及购买链接
```shell
uv run scripts/main.py detail --source={source} --id={goodsId}
```

## 关于脚本
本技能提供的脚本不会读写本地文件，可放心使用。 脚本仅作为客户端请求三方网站`maishou88.com`的商品和价格数据。