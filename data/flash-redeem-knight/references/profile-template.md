# Coupon Redemption Profile Template

按用户/场景记录可复用参数（避免每次重复确认）。

## 1) 门店匹配
- city:
- preferred_store_name_keywords:
- preferred_store_full_name:
- address_keywords:
- geolocation_hint:

## 2) 套餐偏好
- default_pickup_mode: (外带/堂食/得来速)
- drink_preference_keywords:
- drink_avoid_keywords:
- allow_default_main_item: true/false

## 3) 风险与确认
- can_consume_coupon_without_extra_confirmation: true/false
- requires_confirmation_if_possible_extra_payment: true/false
- retry_policy: (none/once/twice)

## 4) 回执格式
- include_screenshot: true/false
- include_order_id: true/false
- preferred_language: zh/en
