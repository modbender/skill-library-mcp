---
name: stripe-payments
description: Best practices for Stripe payment integration. Use when implementing payments, subscriptions, checkout flows, or any monetization feature in games or web apps. Covers CheckoutSessions, Payment Element, subscriptions, and Connect.
metadata:
  author: misskim
  version: "1.0"
  origin: Concept from Stripe official best practices, adapted for our game/app monetization
---

# Stripe Payments Integration

게임/웹앱 수익화를 위한 Stripe 결제 통합 가이드.

## 핵심 원칙

### 반드시 사용
- **CheckoutSessions API** — 원타임 결제 + 구독의 기본
- **Stripe 호스트 체크아웃** 또는 **임베디드 체크아웃** 우선
- **동적 결제 수단** — 대시보드에서 활성화 (payment_method_types 하드코딩 금지)
- **최신 API 버전 + SDK** 사용

### 절대 금지
- ❌ Charges API (레거시, PaymentIntents로 마이그레이션)
- ❌ Card Element / Payment Element card 모드 (레거시)
- ❌ Sources API (deprecated)
- ❌ Tokens API (SetupIntents 사용)
- ❌ payment_method_types 하드코딩 (동적 결제 수단 사용)

## 우리 게임/앱에 적용

### 시나리오별 선택

```
수익화 유형 → 무엇을 파는가?
├─ 일회성 게임 구매 → CheckoutSessions (one-time)
├─ 인앱 구매/아이템 → CheckoutSessions + metadata
├─ 월정액 구독 → Billing API + CheckoutSessions
├─ 기부/후원 → Payment Links (가장 간단)
└─ 마켓플레이스 → Stripe Connect (destination charges)
```

### 기본 구현 패턴

```javascript
// 서버 (Node.js)
const session = await stripe.checkout.sessions.create({
  mode: 'payment',  // 또는 'subscription'
  line_items: [{
    price_data: {
      currency: 'usd',
      product_data: { name: 'Game Premium' },
      unit_amount: 999,  // $9.99 (센트 단위!)
    },
    quantity: 1,
  }],
  success_url: 'https://eastsea.monster/thanks?session_id={CHECKOUT_SESSION_ID}',
  cancel_url: 'https://eastsea.monster/games/',
});
// session.url로 리다이렉트
```

### 구독 모델 (SaaS/게임 프리미엄)
- Billing API → 구독 설계 가이드: docs.stripe.com/billing/subscriptions/designing-integration
- CheckoutSessions + Billing 조합 우선
- 웹훅으로 구독 상태 변경 감지

### 플랫폼 (여러 게임 개발자) → Connect
- **destination charges** — 우리가 liability 수용
- **on_behalf_of** 파라미터로 merchant of record 제어
- charge type 혼합 금지

## 보안 체크리스트

- [ ] 서버사이드에서만 시크릿 키 사용
- [ ] 웹훅 시그니처 검증
- [ ] 클라이언트에 금액/가격 하드코딩 금지 (서버에서 생성)
- [ ] Go-live 체크리스트 완료: docs.stripe.com/get-started/checklist/go-live
- [ ] HTTPS 필수

## 참고 문서

- 통합 옵션: docs.stripe.com/payments/payment-methods/integration-options
- API 투어: docs.stripe.com/payments-api/tour
- Go-live 체크리스트: docs.stripe.com/get-started/checklist/go-live
