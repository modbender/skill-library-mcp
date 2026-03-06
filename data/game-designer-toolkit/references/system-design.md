# Game System Design Guide

Patterns, formulas, and best practices for designing balanced game systems.

---

## Table of Contents
1. [Economy Systems](#economy-systems)
2. [Progression Systems](#progression-systems)
3. [Combat Systems](#combat-systems)
4. [Social Systems](#social-systems)
5. [Monetization Design](#monetization-design)
6. [Balance Formulas](#balance-formulas)

---

## Economy Systems

### Currency Types

| Type | Purpose | Examples |
|------|---------|----------|
| **Soft Currency** | Daily gameplay rewards | Gold, coins, credits |
| **Hard Currency** | Premium/money-linked | Gems, diamonds, premium |
| **Time Currency** | Energy, stamina, action points | Energy, AP, stamina |
| **Social Currency** | Community engagement | Reputation, guild points |

### Sink/Source Balance

**Golden Rule**: Sources ≈ Sinks (slightly more sources for positive feedback)

**Common Sinks:**
- Item upgrades
- Consumables
- Cosmetic purchases
- Feature unlocks
- Tax/fees (auction house)

**Common Sources:**
- Quest rewards
- Enemy drops
- Daily login
- Achievements
- Selling items

### Inflation Prevention

1. **Progressive Costs**: Higher levels = exponentially higher costs
2. **Limited Inventory**: Storage upgrades as currency sink
3. **Decay Systems**: Items that expire or degrade
4. **Tiered Currencies**: High-level items require special currency

### Economy Formulas

**Basic Drop Rate:**
```
Drop Rate = Base Rate × (1 + Luck Modifier) × Event Bonus
```

**Gold Scaling (per level):**
```
Gold = Base × (Level ^ 1.5)
```

**Price Scaling:**
```
Cost = Base × (Multiplier ^ Tier)
```
Example: Base=100, Multiplier=1.5 → T1=100, T2=150, T3=225, T4=338

---

## Progression Systems

### XP Curve Formulas

**Linear:**
```
XP Required = Base + (Level × Increment)
```
Use for: Short games, casual games

**Exponential:**
```
XP Required = Base × (Multiplier ^ Level)
```
Use for: MMOs, long-term games

**Polynomial:**
```
XP Required = Base × (Level ^ Power)
```
Use for: Balanced mid-length games

**Example Curves (to Level 50):**
| Level | Linear | Exponential (1.15x) | Polynomial (²) |
|-------|--------|---------------------|----------------|
| 1 | 100 | 100 | 100 |
| 10 | 1,000 | 351 | 1,000 |
| 25 | 2,500 | 2,862 | 6,250 |
| 50 | 5,000 | 82,984 | 25,000 |

### Progression Types

1. **Vertical**: Stats increase, numbers go up
2. **Horizontal**: More options, same power level
3. **Sidegrades**: Trade-offs, situational power
4. **Mastery**: Skill-based improvement

### Pacing Guidelines

| Timeframe | Player Goal | Reward |
|-----------|-------------|--------|
| 5 min | Complete task | Small currency |
| 15 min | Finish level | XP, item |
| 1 hour | Session milestone | Upgrade material |
| 1 day | Daily completion | Premium currency |
| 1 week | Weekly challenge | Exclusive item |
| 1 month | Season progress | Title, cosmetic |

---

## Combat Systems

### Damage Formula Templates

**Basic:**
```
Damage = Attack - Defense
```

**Percentage-based:**
```
Damage = Attack × (100 / (100 + Defense))
```

**Diminishing Returns:**
```
Damage = Attack × (1 - (Defense / (Defense + Constant)))
```

### Damage Types

| Type | Countered By | Effective Against |
|------|--------------|-------------------|
| Physical | Armor, Block | Light armor |
| Magical | Magic Resist | Heavy armor |
| True | None (direct) | High defense |
| Elemental | Specific resist | Weakness |

### Combat Pacing

**Time to Kill (TTK) Guidelines:**
| Game Type | TTK Range |
|-----------|-----------|
| FPS (Arcade) | 0.5-2 seconds |
| FPS (Tactical) | 2-5 seconds |
| RPG (Action) | 10-30 seconds |
| RPG (Turn-based) | 3-10 turns |
| MMO (Boss) | 5-15 minutes |

### Balance Checkpoints

1. **Level 1**: Establish baseline
2. **Level 10**: First power spike
3. **Level 25**: Mid-game balance
4. **Level 50**: End-game entry
5. **Max Level**: Ultimate power fantasy

---

## Social Systems

### Multiplayer Types

| Type | Design Focus |
|------|--------------|
| Co-op PvE | Shared objectives, complementary roles |
| Competitive PvP | Fair matchmaking, skill expression |
| Asynchronous | Time-flexible, low pressure |
| Social Hubs | Expression, meeting, minigames |

### Guild/Clan Systems

**Core Features:**
- Shared progression
- Group activities
- Leadership structure
- Identity/customization

**Engagement Mechanics:**
- Guild quests
- Shared resources
- Competitions
- Exclusive rewards

### Social Currency Design

```
Social Reward = Base × (Participation × Quality Factor)
```

- Participation: Did they contribute?
- Quality Factor: Was it helpful/positive?

---

## Monetization Design

### F2P Best Practices

**Do:**
- Sell time, not power (boosters vs advantages)
- Provide free paths to all content
- Focus on cosmetics and convenience
- Respect player time

**Don't:**
- Gate content behind paywalls
- Create pay-to-win mechanics
- Use predatory dark patterns
- Force ads

### Premium Game Pricing

| Tier | Price Range | Expectation |
|------|-------------|-------------|
| Indie | $5-20 | 5-15 hours |
| AA | $20-40 | 15-40 hours |
| AAA | $60-70 | 30-100+ hours |

### IAP Design Patterns

| Pattern | Description | Best For |
|---------|-------------|----------|
| Battle Pass | Time-limited reward track | Ongoing engagement |
| Cosmetics | Visual-only items | Self-expression |
| Convenience | Time-savers | Busy players |
| Expansion | New content | Long-term value |

---

## Balance Formulas

### Stat Scaling

**Linear Growth:**
```
Stat = Base + (Level × Growth)
```

**Exponential Growth:**
```
Stat = Base × (Growth ^ Level)
```

**Logarithmic (Diminishing):**
```
Stat = Base × ln(Level + 1) + Base
```

### Difficulty Scaling

**Enemy HP:**
```
HP = Base × (1 + (Level × 0.1)) × Zone Modifier
```

**Enemy Damage:**
```
Damage = Base × (1 + (Level × 0.08))
```

### Drop Rate Balancing

**Rarity Tiers:**
| Rarity | Drop Rate | Example |
|--------|-----------|---------|
| Common | 60-70% | White items |
| Uncommon | 20-25% | Green items |
| Rare | 5-10% | Blue items |
| Epic | 1-3% | Purple items |
| Legendary | 0.1-0.5% | Orange items |
| Mythic | 0.01-0.1% | Red items |

**Adjusted Drop Rate:**
```
Final Rate = Base Rate × (1 + Luck%) × (1 + Buff%) × (1 - BadLuckProtection%)
```

---

## Testing & Iteration

### Metrics to Track

1. **Economy Health**: Currency accumulation rate
2. **Progression Speed**: Time between levels
3. **Combat Feel**: TTK, damage taken
4. **Engagement**: Session length, DAU/MAU
5. **Monetization**: Conversion rate, ARPU

### A/B Testing Priorities

1. First-time user experience
2. Progression pacing
3. Economy balance
4. Difficulty curves
5. Reward frequency

---

*Use these patterns as starting points. Always playtest and iterate based on real player data.*
