"""
PetRPG Battle System
====================
Pet vs Pet battles with turn-based combat.
"""

import random
from pet import Pet, PetStage, Mood


class Battle:
    """Turn-based pet battle system"""
    
    def __init__(self, pet1: Pet, pet2: Pet):
        self.pet1 = pet1
        self.pet2 = pet2
        self.turn = 1
        self.log = []
    
    def calculate_damage(self, attacker: Pet, defender: Pet) -> int:
        """Calculate damage based on stats"""
        # Base damage from strength
        base = attacker.strength * 2
        
        # Speed bonus (faster attacks more often)
        speed_bonus = (attacker.speed - defender.speed) * 0.5
        
        # Intelligence bonus (chance for critical)
        crit_chance = attacker.intelligence / 200  # Max 50%
        is_crit = random.random() < crit_chance
        
        damage = int(base + speed_bonus)
        
        if is_crit:
            damage *= 2
            self.log.append(f"💥 CRITICAL HIT!")
        
        # Random variance
        variance = random.randint(-3, 3)
        damage = max(1, damage + variance)
        
        return damage
    
    def battle_ascii(self, attacker: Pet, defender: Pet) -> str:
        """Generate battle ASCII art"""
        attacker_art = attacker.get_ascii(Mood.EXCITED)
        defender_art = defender.get_ascii(Mood.ANGRY)
        
        return f"""
{attacker_art}
         ⚔️  VS  ⚔️
{defender_art}
        """
    
    def fight(self) -> dict:
        """Execute the battle"""
        self.log.append(f"⚔️ BATTLE: {self.pet1.name} vs {self.pet2.name} ⚔️")
        self.log.append("")
        
        # Determine first attacker (speed check)
        if self.pet1.speed >= self.pet2.speed:
            attacker, defender = self.pet1, self.pet2
        else:
            attacker, defender = self.pet2, self.pet1
        
        # Battle loop
        while self.pet1.health > 0 and self.pet2.health > 0:
            self.log.append(f"--- Turn {self.turn} ---")
            
            # Calculate damage
            damage = self.calculate_damage(attacker, defender)
            defender.health = max(0, defender.health - damage)
            
            self.log.append(f"{attacker.name} attacks!")
            self.log.append(f"💥 {damage} damage to {defender.name}")
            self.log.append(f"{defender.name} HP: {defender.health}/{defender.health}")
            self.log.append("")
            
            # Check for KO
            if defender.health <= 0:
                break
            
            # Swap attacker
            attacker, defender = defender, attacker
            self.turn += 1
        
        # Determine winner
        if self.pet1.health > 0:
            winner = self.pet1
            loser = self.pet2
        else:
            winner = self.pet2
            loser = self.pet1
        
        # Award XP
        xp_gained = 50 + (loser.level * 10)
        winner.xp += xp_gained
        winner.wins += 1
        loser.losses += 1
        
        self.log.append(f"🏆 {winner.name} WINS!")
        self.log.append(f"💫 +{xp_gained} XP to {winner.name}")
        
        return {
            "winner": winner.name,
            "loser": loser.name,
            "turns": self.turn,
            "xp_gained": xp_gained,
            "log": self.log
        }
    
    def auto_battle(self) -> str:
        """Run battle and return summary"""
        result = self.fight()
        
        output = f"""
╭─ BATTLE RESULT ──────────────────╮
│ {result['winner']} wins!
│ Turns: {result['turns']}
│ XP Gained: {result['xp_gained']}
╰──────────────────────────────────╯
"""
        return output


# === Quick Battle ===

def quick_battle(name1: str, name2: str, level1: int = 10, level2: int = 10) -> str:
    """Quick battle between two pets"""
    pet1 = Pet(name=name1, owner="player1", level=level1)
    pet2 = Pet(name=name2, owner="player2", level=level2)
    
    # Scale stats based on level
    pet1.strength = 10 + level1
    pet1.speed = 10 + level1
    pet1.health = 50 + level1 * 5
    
    pet2.strength = 10 + level2
    pet2.speed = 10 + level2
    pet2.health = 50 + level2 * 5
    
    battle = Battle(pet1, pet2)
    return battle.auto_battle()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("PetRPG Battle")
        print("Usage: python battle.py <pet1> <pet2>")
        sys.exit(1)
    
    print(quick_battle(sys.argv[1], sys.argv[2]))
