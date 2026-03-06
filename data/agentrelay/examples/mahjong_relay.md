# 🀄 Mahjong Relay Example - Multi-Agent Autonomous Game

**Example Type**: Complex multi-agent coordination  
**Duration**: ~30-60 minutes  
**Agents Required**: 5 (Yellow, Red, Green, Blue, Orange)  
**Protocol**: AgentRelay v1.0.1-alpha.2+

---

## 🎯 Overview

This example demonstrates how to use AgentRelay protocol to coordinate a **fully autonomous mahjong game** where 5 agents collaborate without human intervention:

| Role | Agent | Position | Responsibility |
|------|-------|----------|----------------|
| **Dealer/Table** | Yellow | God's eye view | Manage tiles, deal cards, judge moves |
| **East Player** | Red | Dealer | First to play |
| **South Player** | Green | Next | Clockwise 2nd |
| **West Player** | Blue | Opposite | Clockwise 3rd |
| **North Player** | Orange | Previous | Clockwise 4th |

---

## 📋 Prerequisites

### 1. Install AgentRelay
```bash
clawhub install agentrelay
```

### 2. Prepare 5 Agents
Ensure you have 5 agents configured with AgentRelay capability:
- `agent:yellow:main` - Table/Referee
- `agent:red:main` - East player
- `agent:green:main` - South player
- `agent:blue:main` - West player
- `agent:orange:main` - North player

### 3. Game Rules
Use simplified 108-tile rules (no wind/dragon tiles):
- **Tiles**: 1-9 Dots ×4, 1-9 Bamboo ×4, 1-9 Characters ×4 = 108 tiles
- **Win patterns**: Standard (4 sets + 1 pair), All Triplets, or Seven Pairs
- **Mode**: "Blood Flow" - game continues after first win until 3 players win or draw

---

## 🚀 Step-by-Step Guide

### Phase 1: Setup (Yellow Agent)

**Step 1.1**: Create tile stack
```python
# Yellow creates 108 tiles
tiles = []
for suit in ['Dots', 'Bamboo', 'Characters']:
    for num in range(1, 10):
        tiles.extend([f"{num}{suit}"] * 4)

# Save to file
import json
with open('/tmp/mahjong/tiles.json', 'w') as f:
    json.dump({'tiles': tiles, 'remaining': 108}, f)
```

**Step 1.2**: Shuffle and deal
```python
import random
random.shuffle(tiles)

# Deal 13 tiles to each player, East gets 14th
hands = {
    'Red': tiles[0:13],
    'Green': tiles[13:26],
    'Blue': tiles[26:39],
    'Orange': tiles[39:52],
}
Red.append(tiles[52])  # East draws 14th tile
```

**Step 1.3**: Send hands via AgentRelay
```python
from agentrelay import AgentRelayTool

for player, hand in hands.items():
    content = {
        'type': 'INITIAL_HAND',
        'player': player,
        'hand': hand,
        'game_id': 'mahjong_20260223'
    }
    result = AgentRelayTool.send(player.lower(), 'REQ', f'game_start_{player}', content)
    sessions_send(
        target=f'agent:{player.lower()}:main',
        message=f"AgentRelay: {result['csv_message']}"
    )
```

---

### Phase 2: Game Loop

**Step 2.1**: Yellow notifies current player (Red/East starts)
```python
# Yellow sends to Red
content = {
    'type': 'YOUR_TURN',
    'action': 'DRAW',
    'hand': Red_hand,
    'drawn': new_tile,
    'options': ['PLAY', 'PONG', 'KONG', 'WIN']
}
result = AgentRelayTool.send('red', 'REQ', 'turn_red_1', content)
sessions_send(target='agent:red:main', message=f"AgentRelay: {result['csv_message']}")
```

**Step 2.2**: Red receives and decides
```bash
# Red agent receives message
python3 run_relay.py receive "REQ,turn_red_1,s/turn_red_1.json,,"

# Output:
# {
#   "type": "YOUR_TURN",
#   "action": "DRAW",
#   "hand": [...],
#   "drawn": "5 Dots",
#   "options": ["PLAY", "PONG", "KONG", "WIN"]
# }

# Red analyzes hand and decides to PLAY
```

**Step 2.3**: Red sends decision back
```python
# Red responds
content = {
    'type': 'ACTION',
    'action': 'PLAY',
    'tile': '3 Bamboo',
    'game_id': 'mahjong_20260223'
}
result = AgentRelayTool.send('yellow', 'CMP', 'turn_red_1', content)
sessions_send(target='agent:yellow:main', message=f"AgentRelay: {result['csv_message']}")
```

**Step 2.4**: Yellow broadcasts to all
```python
# Yellow updates game state and broadcasts
broadcast_msg = f"NOTIFY|Red|PLAY|3 Bamboo|others_can:[PONG,KONG,WIN,PASS]|state:{{discarded:[...],remaining:87}}"

for player in ['Green', 'Blue', 'Orange']:
    sessions_send(
        target=f'agent:{player.lower()}:main',
        message=broadcast_msg
    )
```

**Step 2.5**: Other players respond (PONG/KONG/WIN/PASS)
```python
# Each player checks if they can PONG/KONG/WIN
# If yes, send response via AgentRelay
# If no, send PASS

content = {'type': 'RESPONSE', 'action': 'PASS', 'player': 'Green'}
result = AgentRelayTool.send('yellow', 'CMP', 'response_green_1', content)
sessions_send(target='agent:yellow:main', message=f"AgentRelay: {result['csv_message']}")
```

**Step 2.6**: Next player's turn
```python
# Yellow notifies Green (South)
# ... repeat Steps 2.1-2.5 ...
```

---

### Phase 3: Win Detection

**When a player wins:**

**Step 3.1**: Player declares WIN
```python
# Player (e.g., Green) declares win
content = {
    'type': 'ACTION',
    'action': 'WIN',
    'win_type': 'Standard',
    'hand': [...],  # Complete 14-tile hand
    'game_id': 'mahjong_20260223'
}
result = AgentRelayTool.send('yellow', 'CMP', 'turn_green_9', content)
sessions_send(target='agent:yellow:main', message=f"AgentRelay: {result['csv_message']}")
```

**Step 3.2**: Yellow validates win pattern
```python
def validate_win(hand):
    # Check if hand matches valid win patterns
    if is_standard_pattern(hand):
        return True
    elif is_all_triplets(hand):
        return True
    elif is_seven_pairs(hand):
        return True
    return False

# Yellow validates
if validate_win(Green_hand):
    # Valid win - continue Blood Flow mode
    broadcast_win('Green', Green_hand)
else:
    # False win - penalty
    penalize_player('Green', -5)
```

**Step 3.3**: Continue or end game
```python
# In Blood Flow mode, game continues until 3 players win
winners.append('Green')

if len(winners) >= 3 or tiles_remaining < 2:
    # Game over - calculate scores
    calculate_final_scores()
else:
    # Continue with remaining players
    notify_next_player()
```

---

### Phase 4: Scoring

**Step 4.1**: Calculate individual scores
```python
scores = {
    'Red': 0,
    'Green': 0,
    'Blue': 0,
    'Orange': 0
}

# Scoring rules
for player, events in game_events.items():
    for event in events:
        if event['type'] == 'WIN':
            if event['position'] == 1:
                scores[player] += 10  # 1st win
            elif event['position'] == 2:
                scores[player] += 5   # 2nd win
            elif event['position'] == 3:
                scores[player] += 2   # 3rd win
        
        if event['type'] == 'SELF_DRAW':
            scores[player] += 3
        
        if event['type'] == 'KONG':
            scores[player] += 1
        
        if event['type'] == 'DISCARD_TO_WIN':
            scores[player] -= 2  # Pointed to winner
        
        if event['type'] == 'FALSE_WIN':
            scores[player] -= 5  # Penalty
```

**Step 4.2**: Announce results
```python
# Sort by score
ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)

# Announce via AgentRelay to all players
content = {
    'type': 'GAME_RESULT',
    'ranking': ranking,
    'titles': {
        ranking[0][0]: 'Mahjong God 🏆',
        ranking[1][0]: 'Expert 🥈',
        ranking[2][0]: 'Player 🥉',
        ranking[3][0]: 'Beginner'
    }
}

for player in ['Red', 'Green', 'Blue', 'Orange']:
    result = AgentRelayTool.send(player.lower(), 'REQ', f'game_result_{player}', content)
    sessions_send(target=f'agent:{player.lower()}:main', message=f"AgentRelay: {result['csv_message']}")
```

---

## 📊 Example Message Flow

```
Yellow → Red:    YOUR_TURN|DRAW|hand:[...]|drawn:5 Dots|options:[PLAY]
Red → Yellow:    ACTION|PLAY|3 Bamboo
Yellow → All:    NOTIFY|Red|PLAY|3 Bamboo|others_can:[PONG,KONG,WIN,PASS]
Green → Yellow:  RESPONSE|PASS
Blue → Yellow:   RESPONSE|PASS
Orange → Yellow: RESPONSE|PASS
Yellow → Green:  YOUR_TURN|DRAW|hand:[...]|drawn:1 Character|options:[PLAY]
... (repeat 9 rounds) ...
Green → Yellow:  ACTION|WIN|win_type:Seven Pairs|hand:[...]
Yellow → All:    WINNER|Green|win_type:Seven Pairs|score:13
... (continue Blood Flow) ...
Yellow → All:    GAME_RESULT|ranking:[Green:13, Red:0, Blue:0, Orange:0]
```

---

## 🎯 Key Learnings

### What Works Well
1. **Autonomous Decision Making**: Each agent independently analyzes hand and decides moves
2. **State Synchronization**: Yellow maintains authoritative game state
3. **Secret Code Verification**: Ensures all players receive messages correctly
4. **Complete Audit Trail**: All moves logged via AgentRelay transaction logs

### Challenges & Solutions
| Challenge | Solution |
|-----------|----------|
| **Message timeout** | Use AgentRelay file pointers for large hand data |
| **State consistency** | Yellow as single source of truth |
| **Win validation** | Pre-implement pattern matching in Yellow |
| **Player timeout** | Auto-PASS after 2 minutes |

### Best Practices
1. **Keep messages under 30 chars** when possible (use file pointers for hands)
2. **Use descriptive event IDs** (e.g., `turn_red_1`, `response_green_5`)
3. **Log everything** to transaction logs for debugging
4. **Validate before broadcasting** (Yellow validates all moves)

---

## 📁 Files Generated

After running this example, you'll have:

```
~/.openclaw/data/agentrelay/
├── storage/
│   ├── game_start_red.json
│   ├── game_start_green.json
│   ├── turn_red_1.json
│   ├── turn_green_1.json
│   └── ...
├── logs/
│   └── transactions_20260223.jsonl  # Complete game log
└── registry.json
```

---

## 🚦 Try It Yourself

### Quick Start Script
```bash
# Clone the example
cd ~/.openclaw/workspace/skills/agentrelay/examples

# Run setup (Yellow)
python3 mahjong_setup.py

# Start game loop
python3 mahjong_game.py

# View results
cat ~/.openclaw/data/agentrelay/logs/transactions_*.jsonl | jq
```

### Expected Duration
- **Setup**: 2-3 minutes
- **Game**: 30-60 minutes (9+ rounds)
- **Scoring**: 1-2 minutes
- **Total**: ~1 hour

---

## 🎓 Next Steps

After mastering this example:
1. **Add complexity**: Include wind/dragon tiles
2. **Advanced patterns**: Add more win types (Thirteen Orphans, etc.)
3. **Tournament mode**: Multiple rounds with rotating dealers
4. **Spectator mode**: Allow non-playing agents to observe and commentate

---

**Example Version**: v1.0  
**Last Updated**: 2026-02-28  
**Compatible with**: AgentRelay v1.0.1-alpha.2+
