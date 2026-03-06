---
name: flash-redeem-knight
description: Universal browser automation for prepaid H5 coupon redemption (food, beverage, pickup vouchers). Use when a user provides a prepaid redemption link and wants automatic store selection, option selection, final code extraction, and screenshot proof—without extra payment risk.
---

# 闪兑骑士（Flash Redeem Knight）

把“已支付券链接”自动兑换成最终可用的取餐码/核销码：开链接→选店→选品→确认→出码→回执。

## 标准流程

1. **先做安全前置**
   - 确认用户授权可消耗本次券。
   - 确认为“已支付/无额外支付”链接；若存在支付可能，先停下并二次确认。

2. **打开页面并判断状态**
   - 用 `browser` 打开兑换链接。
   - 若出现“无效/已使用/过期”，立即停止并回报。
   - 若页面已直接显示编码，跳到第 6 步。

3. **门店选择（禁止硬编码序号）**
   - 必须按门店名关键词匹配，不按“第一个”盲选。
   - 有地理上下文时（如某地铁站附近），先应用定位上下文再匹配门店。

4. **规格选择**
   - 主食只有一个默认选项时保持默认。
   - 饮品/配菜按用户偏好关键词选择（例：豆浆优先，避开咖啡）。
   - 取餐方式按用户默认（外带/堂食/得来速）；无默认则询问。

5. **确认兑换并等待出码**
   - 点击“兑换/确认”后等待 10–20 秒。
   - 加载异常时可重试 1 次；仍失败则截图并回报。

6. **结构化回执**
   - 必回：`取餐码/核销码`、`门店`、`商品摘要`、`实付/抵扣`。
   - 附带最终页面截图（优先）。

## 失败与异常处理

- 页面改版：用 `snapshot` 重新按按钮文本定位（如“兑换取餐码”“确认领取”）。
- 同名/近似门店：先比对完整门店名，再比对地址关键词。
- 编码未出现：检查弹窗、折叠区、滚动区域与延迟加载。
- 存在误兑风险：暂停并请用户确认，不自行猜测继续。

## 回执模板

- 兑换状态：成功/失败
- 取餐码：`<code>`
- 门店：`<store>`
- 套餐：`<items>`
- 金额：`实付 <x> / 优惠 <y>`
- 证据：最终页截图

## 参考文件

- 用户偏好模板：`references/profile-template.md`
