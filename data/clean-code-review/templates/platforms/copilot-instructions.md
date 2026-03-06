# Clean Code — Copilot Instructions

## Instructions

Follow these pragmatic coding standards in all generated code. Be concise, direct, and solution-focused. Never over-engineer.

## Core Principles

Apply these principles to every piece of code:

- **SRP** — Single Responsibility. Each function/class does ONE thing.
- **DRY** — Don't Repeat Yourself. Extract shared logic.
- **KISS** — Keep It Simple. Simplest solution that works.
- **YAGNI** — Don't build features that aren't needed yet.

## Naming Patterns

```
// Variables — reveal intent
✅ userCount, isAuthenticated, orderTotal
❌ n, flag, x

// Functions — verb + noun
✅ getUserById(), calculateTotal(), sendEmail()
❌ user(), calc(), email()

// Booleans — question form
✅ isActive, hasPermission, canEdit
❌ active, permission, edit
```

## Function Structure

Keep functions small (5–20 lines), with max 3 arguments. Use guard clauses:

```typescript
// ✅ Guard clauses — flat and readable
function processOrder(order: Order): Result {
  if (!order) return { error: 'No order' };
  if (!order.items.length) return { error: 'Empty order' };
  if (!order.payment) return { error: 'No payment' };

  const total = calculateTotal(order.items);
  return chargeAndFulfill(order, total);
}
```

## Anti-Patterns to Avoid

- Don't comment obvious code — let names self-document
- Don't create helpers for one-liners — inline instead
- Don't create `utils.ts` for a single function
- Don't use magic numbers — define named constants
- Don't write functions over 20 lines — split by responsibility
- Don't nest deeper than 2 levels — use early returns

## Before Editing Files

Always check: what imports this file, what tests cover it, and whether dependent files need updates too. Edit all affected files together.
