# Common Traps — Food Delivery

Where agents fail without explicit instructions.

## Memory Failures

| Trap | Consequence | Prevention |
|------|-------------|------------|
| Forgetting allergies | Dangerous order | CRITICAL section in memory.md, check every time |
| Ignoring stated restrictions | Order violates diet | Check FIRM restrictions before suggesting |
| Not recording rejections | Repeat bad suggestions | Update restaurants.md after negative feedback |
| Losing context between sessions | Start from scratch | Persistent memory in ~/food-delivery/ |
| Storing preference as fact | "User is vegetarian" when said "I'm trying to eat less meat" | Store exact language, note uncertainty |

## Variety Blindness

| Trap | Consequence | Prevention |
|------|-------------|------------|
| Success loop | User ordered X once → suggest X forever | Track variety in orders.md |
| Recency bias | Last order becomes default | Explicit variety protection rules |
| Ignoring breadth | Only suggest tried categories | Occasionally recommend new cuisines user might like |
| Not tracking repetition | Same restaurant 5x/week unnoticed | Automated variety triggers |

## Context Blindness

| Trap | Consequence | Prevention |
|------|-------------|------------|
| Wrong time suggestions | Recommending breakfast at 10pm | Check current time, adjust appropriately |
| Day ignorance | Friday night treated like Tuesday lunch | Different default moods per day |
| Mood deaf | Pushing healthy when user is hungover | Ask about occasion/mood when relevant |
| Weather ignorance | Hot soup in heatwave | Consider seasonal/weather factors |
| Occasion miss | Fast food for anniversary | Ask about special occasions |

## Decision Overload

| Trap | Consequence | Prevention |
|------|-------------|------------|
| Too many options | Analysis paralysis | Maximum 3 options, always |
| No reasoning | User doesn't trust choice | Explain why each option fits |
| Not narrowing | List-making instead of deciding | Use binary narrowing questions |
| Ignoring rejections | Suggesting what was just declined | Track and learn from rejections |
| Asking too many questions | Friction, user gives up | Make intelligent defaults, ask only when needed |

## Social Blindness

| Trap | Consequence | Prevention |
|------|-------------|------------|
| Assuming solo | Wrong portions, no variety | Ask "just you?" for unclear situations |
| Forgetting regulars | Partner's preferences ignored | Maintain people.md |
| Kid-ignorance | Spicy suggestion with children | Note family members in people.md |
| No intersection | Restaurant excludes someone | Find overlap in group preferences |

## Price Blindness

| Trap | Consequence | Prevention |
|------|-------------|------------|
| Platform loyalty | Miss better deals elsewhere | Always compare across platforms |
| Ignoring promos | Overpay when discounts available | Check for coupons before checkout |
| Fee blindness | $8 delivery turns "$15 meal" into $25 | Always show true total |
| Surge ignorance | Order during peak pricing | Warn about unusually high fees |

## Order Execution Failures

| Trap | Consequence | Prevention |
|------|-------------|------------|
| No confirmation | Order placed without explicit yes | Always get confirmation before checkout |
| Missing allergy notes | Kitchen unaware of restriction | Add note for EVERY order with CRITICAL items |
| Wrong restaurant | Similar names, wrong location | Verify address before ordering |
| Stale availability | Item shows but unavailable | Handle "out of stock" gracefully |
| Payment assumption | Payment fails unexpectedly | Handle payment errors gracefully |

## Recovery Patterns

When you catch yourself in a trap:

**Repeated rejection:**
"I see that's not working. What would you actually like right now?"

**Too many options given:**
"Let me simplify: [A] or [B]?"

**Context missed:**
"Is this for a special occasion, or regular meal?"

**Variety problem:**
"You've had [X] a few times recently. Want to try something different, or is that your current favorite?"

**Price regret:**
"I found a better deal on [Platform]. Want to switch?"

**Post-order issue:**
"That didn't go well. I've noted it — won't suggest [Restaurant] again unless you want to give them another chance."
