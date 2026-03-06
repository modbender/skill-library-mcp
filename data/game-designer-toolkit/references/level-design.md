# Level Design Guide

Principles, patterns, and frameworks for creating engaging game levels and worlds.

---

## Table of Contents
1. [Core Principles](#core-principles)
2. [Level Structure](#level-structure)
3. [Flow & Navigation](#flow--navigation)
4. [Difficulty Design](#difficulty-design)
5. [Pacing & Rhythm](#pacing--rhythm)
6. [World Building](#world-building)
7. [Genre-Specific Patterns](#genre-specific-patterns)

---

## Core Principles

### The 3 C's

1. **Camera**: What the player sees
2. **Character**: How the player moves
3. **Control**: How inputs feel

*All level design must work with the 3 C's, not against them.*

### Player Psychology

| Player Type | Motivation | Level Focus |
|-------------|------------|-------------|
| Explorer | Discovery | Secrets, alternate paths |
| Achiever | Mastery | Challenges, collectibles |
| Socializer | Connection | Co-op, meeting spaces |
| Killer | Competition | PvP arenas, leaderboards |

### Design Pillars

Every level should:
1. **Teach** - Introduce or reinforce mechanics
2. **Test** - Challenge player understanding
3. **Reward** - Provide meaningful feedback

---

## Level Structure

### Basic Level Anatomy

```
[ENTRANCE]
    ↓
[INTRODUCTION] - Establish space, show goal
    ↓
[DEVELOPMENT] - Build complexity
    ↓
[CLIMAX] - Peak challenge
    ↓
[RESOLUTION] - Wind down, reward
    ↓
[EXIT/TRANSITION]
```

### Level Size Guidelines

| Game Type | Session Length | Level Count | Level Duration |
|-----------|----------------|-------------|----------------|
| Mobile Casual | 2-5 min | 100s | 1-3 min |
| Mobile Core | 5-15 min | 50-100 | 5-10 min |
| Indie Action | 20-60 min | 10-30 | 10-20 min |
| RPG Dungeon | 1-3 hours | 20-50 | 20-45 min |
| Open World | Unlimited | 1 (zones) | Unlimited |

### Checkpoint Design

**Checkpoint Frequency:**
- Action games: Every 2-5 minutes
- RPGs: Before/after major encounters
- Roguelikes: Between biomes/floors

**Checkpoint Criteria:**
1. Safe location (no immediate threats)
2. Resource restore point
3. Clear visual indicator
4. After significant progress

---

## Flow & Navigation

### Signposting

**Visual Cues:**
| Cue Type | Purpose | Example |
|----------|---------|---------|
| Lighting | Guide attention | Spotlight on exit |
| Color | Indicate importance | Gold for treasure |
| Architecture | Direct movement | Arrows in floor |
| Landmarks | Orientation | Distinctive tower |

**The "Breadcrumbs" Technique:**
- Small rewards leading to larger ones
- Subtle visual trail
- Encourages exploration without forcing

### Flow Patterns

**Linear Flow:**
```
A → B → C → D → E
```
Best for: Story-driven, scripted experiences

**Branching Flow:**
```
    → C →
A → B    → E
    → D →
```
Best for: Exploration, player choice

**Hub-Based:**
```
      → Area 1 →
      → Area 2 →
Hub ← → Area 3 ← Hub
      → Area 4 →
```
Best for: Metroidvania, RPGs

**Open World:**
```
[Free movement anywhere]
     ↓
[Points of Interest]
```
Best for: Sandbox, exploration games

### Preventing Player Confusion

1. **Landmarks**: Always visible reference points
2. **Consistency**: Similar paths = similar length
3. **Feedback**: Clear indication of progress
4. **Reset**: Ways to return to known locations

---

## Difficulty Design

### Difficulty Curve

```
Skill Required
    ↑
    |              ___/‾‾‾ (Challenge)
    |            _/
    |          _/
    |        _/  (Learning)
    |      _/
    |    _/
    |__/
    +--------------------→ Time/Game Progress
```

### Difficulty Types

| Type | Description | Example |
|------|-------------|---------|
| Execution | Physical skill | Precision platforming |
| Strategic | Mental planning | Puzzle solving |
| Knowledge | Information gathering | Boss patterns |
| Resource | Management | Survival games |
| Social | Player interaction | PvP |

### Introducing Challenges

**The 4-Step Method:**
1. **Show** - Player sees mechanic safely
2. **Do** - Player performs with low stakes
3. **Test** - Player must use under pressure
4. **Combine** - Player uses with other mechanics

### Difficulty Scaling Methods

| Method | Implementation |
|--------|----------------|
| Enemy Count | More enemies, same strength |
| Enemy Strength | Same count, stronger enemies |
| Resource Scarcity | Fewer pickups |
| Time Pressure | Timers, chases |
| Complexity | More mechanics combined |

### Accessibility Considerations

- Adjustable difficulty levels
- Assist modes (invincibility, auto-aim)
- Clear visual/audio cues
- Remappable controls
- Colorblind-friendly design

---

## Pacing & Rhythm

### Tension Curve

```
Tension
    ↑
    |     Peak        Peak
    |      ↑           ↑
    |    /   \       /   \
    |   /     \  _ /      \ _
    |  /        \/          \
    | /                      \
    +--------------------------→ Time
      Build  Relief  Build  End
    (Action)(Rest)(Action)(Boss)
```

### Pacing Patterns

**High Intensity:**
- Combat encounters
- Chases
- Time pressure
- Boss fights

**Low Intensity:**
- Exploration
- Story moments
- Resource gathering
- Puzzles

**Ideal Ratio:** Varies by genre
- Action: 70% high / 30% low
- Horror: 30% high / 70% low (anticipation)
- RPG: 40% high / 60% low

### Session Pacing

| Time | Activity | Purpose |
|------|----------|---------|
| 0-2 min | Tutorial/warmup | Ease in |
| 2-10 min | Core gameplay | Main experience |
| 10-15 min | Challenge spike | Engagement |
| 15-20 min | Resolution | Satisfaction |
| 20+ min | Optional content | Extended play |

---

## World Building

### Biome Design

**Biome Identity Framework:**
1. **Visual Theme** - What it looks like
2. **Gameplay Focus** - What mechanics shine
3. **Narrative Role** - Story purpose
4. **Unique Element** - What makes it special

**Example Biome Table:**
| Biome | Visual | Mechanics | Story |
|-------|--------|-----------|-------|
| Forest | Green, organic | Stealth, climbing | Introduction |
| Desert | Sandy, ruins | Survival, puzzles | Ancient mystery |
| Ice | Blue, crystalline | Sliding, precision | Isolation theme |
| Volcano | Red, dangerous | Timing, hazards | Final challenge |

### Points of Interest (POI)

**POI Types:**
- **Settlements** - NPCs, shops, quests
- **Dungeons** - Combat challenges
- **Landmarks** - Visual orientation
- **Secrets** - Hidden rewards
- **Events** - Dynamic occurrences

**POI Distribution:**
```
Open World POI Density:
- High density: Near start/paths
- Medium density: General exploration
- Low density: Wilderness areas
- Unique: Far corners (reward exploration)
```

### Environmental Storytelling

**Techniques:**
1. **Props placement** - Items tell stories
2. **Architecture** - Buildings imply history
3. **NPCs** - Dialogue and behavior
4. **Visual decay** - Time passage
5. **Written lore** - Notes, signs

---

## Genre-Specific Patterns

### Platformers

**Level Elements:**
- Moving platforms
- Hazards (spikes, pits)
- Collectibles
- Secret areas
- Boss arenas

**Difficulty Sources:**
- Precision timing
- Pattern memorization
- Spatial awareness

### FPS/TPS

**Level Elements:**
- Cover positions
- Sight lines
- Verticality
- Spawn points
- Objective locations

**Flow Considerations:**
- Combat arenas
- Transition corridors
- Backtracking options

### RPGs

**Level Elements:**
- Town hubs
- Dungeon zones
- Resource nodes
- Quest markers
- Fast travel points

**Dungeon Structure:**
```
Entrance → Combat → Puzzle → Combat → Mini-Boss →
Loot Room → Combat → Puzzle → Boss → Exit
```

### Roguelikes

**Level Elements:**
- Procedural generation rules
- Room templates
- Connection algorithms
- Scaling difficulty

**Room Types:**
- Combat rooms (60%)
- Treasure rooms (15%)
- Challenge rooms (10%)
- Shop rooms (10%)
- Boss rooms (5%)

### Puzzle Games

**Level Elements:**
- Single mechanic focus
- Progressive complexity
- "Aha!" moments
- Optional harder versions

**Difficulty Scaling:**
1. Introduce concept
2. Simple application
3. Combine with previous
4. Require mastery
5. Twist expectations

---

## Level Design Checklist

### Before Building
- [ ] Core mechanic defined
- [ ] Target duration set
- [ ] Difficulty target known
- [ ] Story purpose clear

### During Building
- [ ] Clear navigation
- [ ] Consistent signposting
- [ ] Appropriate pacing
- [ ] Fair challenges

### After Building
- [ ] Multiple playthroughs tested
- [ ] New player feedback gathered
- [ ] Performance acceptable
- [ ] All paths work correctly

---

*Good level design is invisible - players simply enjoy the experience without fighting the game.*
