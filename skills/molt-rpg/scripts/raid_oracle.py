"""
MoltRPG Raid Oracle - 100% OFFLINE
===================================
This module generates raids for the game.

NETWORK: NONE - This is a completely offline game engine.
No external APIs, no network calls, no optional features that require network.

This is a simple random raid generator for a single-player/multi-agent game.
"""

import random
from datetime import datetime

# === OFFLINE RAID GENERATOR ===
# These are used to generate random raids - NO NETWORK CALLS

OFFLINE_MONSTERS = [
    {"name": "Glitch Goblin", "base_level": 1, "reward": 5},
    {"name": "Bug Sprout", "base_level": 2, "reward": 10},
    {"name": "Lag Troll", "base_level": 3, "reward": 15},
    {"name": "Latency Wraith", "base_level": 5, "reward": 25},
    {"name": "404 Specter", "base_level": 7, "reward": 40},
    {"name": "Memory Leech", "base_level": 10, "reward": 60},
    {"name": "Stack Overflow Dragon", "base_level": 15, "reward": 100},
    {"name": "Segmentation Fault Giant", "base_level": 20, "reward": 200},
]

STATE_FILE = "raid_oracle_state.json"


class RaidOracle:
    """Generates raids for MoltRPG - 100% OFFLINE, NO NETWORK"""
    
    def __init__(self):
        self.state = self._load_state()

    def _load_state(self):
        import os
        import json
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "offline_raid_count": 0,
            "generated_at": datetime.now().isoformat()
        }

    def _save_state(self):
        import os
        import json
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=4)

    def generate_raid(self):
        """Generate a random raid - NO NETWORK CALLS"""
        monster = random.choice(OFFLINE_MONSTERS)
        
        # Add some randomness
        level_variance = random.randint(-1, 2)
        level = max(1, monster["base_level"] + level_variance)
        reward = int(monster["reward"] * random.uniform(0.8, 1.5))
        
        # Calculate battle stats
        hp = int(100 * (1.2 ** (level - 1)))
        atk = int(10 * (1.15 ** (level - 1)))
        defense = int(5 * (1.1 ** (level - 1)))
        
        raid = {
            "id": f"offline_{self.state['offline_raid_count'] + 1}",
            "name": monster["name"],
            "level": level,
            "reward_usdc": reward,
            "title": f"Defeat the {monster['name']}",
            "description": f"A wild {monster['name']} appears!",
            "source": "offline",
            # Battle stats
            "hp": hp,
            "atk": atk,
            "def": defense
        }
        
        self.state['offline_raid_count'] += 1
        self._save_state()
        
        return raid

    def get_monster_tier(self, reward):
        """Determine monster tier based on reward"""
        if reward < 50: return ("Common Scavenger", 1, "Requires 1 Solo")
        if reward < 200: return ("Elite Guard", 5, "Requires 1 DPS, 1 Tank")
        if reward < 1000: return ("Dungeon Boss", 12, "Requires 2 DPS, 1 Tank, 1 Healer")
        return ("Ancient Dragon", 20, "Requires 3 DPS, 2 Tank, 2 Healer")

    def get_party_requirements(self, tier_name):
        """Return party composition requirements"""
        requirements = {
            "Common Scavenger": {"min": 1, "max": 1, "roles": []},
            "Elite Guard": {"min": 2, "max": 2, "roles": ["DPS", "Tank"]},
            "Dungeon Boss": {"min": 4, "max": 4, "roles": ["DPS", "DPS", "Tank", "Healer"]},
            "Ancient Dragon": {"min": 7, "max": 7, "roles": ["DPS", "DPS", "DPS", "Tank", "Tank", "Healer", "Healer"]}
        }
        return requirements.get(tier_name, {"min": 1, "max": 1, "roles": []})

    def format_alert(self, raid):
        """Format a raid alert for display"""
        name, level, party = self.get_monster_tier(raid.get('reward_usdc', 10))
        party_req = self.get_party_requirements(name)
        
        monster_prefix = "🦠 INFESTATION" if "bug" in raid.get('name', '').lower() else "⚔️ NEW RAID"
        
        roles_text = ", ".join(party_req['roles']) if party_req['roles'] else "Solo"
        
        alert = (
            f"{monster_prefix} DETECTED\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👾 **Monster:** {name}\n"
            f"📊 **Level:** {level}\n"
            f"💰 **Loot:** {raid.get('reward_usdc', 0)} credits\n"
            f"🛡️ **Party:** {party}\n"
            f"⚙️ **Roles needed:** {roles_text}\n\n"
            f"💬 Reply with `!join` to form a party!"
        )
        
        return alert, party_req

    def run(self):
        """Main entry point - generates raids"""
        # 100% offline - just generate a random raid
        raid = self.generate_raid()
        return [raid]
    
    def check_party_ready(self, party_members, party_req):
        """Check if party meets requirements"""
        if len(party_members) < party_req['min']:
            return False, f"Need at least {party_req['min']} members"
        if len(party_members) > party_req['max']:
            return False, f"Max {party_req['max']} members allowed"
        return True, "Party ready for raid"


if __name__ == "__main__":
    print("🎮 MoltRPG Raid Oracle - 100% OFFLINE")
    print("=" * 40)
    
    oracle = RaidOracle()
    raids = oracle.run()
    
    if raids:
        for raid in raids:
            alert, _ = oracle.format_alert(raid)
            print(alert)
    else:
        print("HEARTBEAT_OK")
