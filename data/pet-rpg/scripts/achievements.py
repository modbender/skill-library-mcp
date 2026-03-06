"""
PetRPG Achievement System
=========================
Track and award achievements for pet milestones.
"""

import json
from datetime import datetime
from typing import List, Dict
from pet import Pet, ACHIEVEMENTS


class AchievementManager:
    """Manage achievements for pets"""
    
    def __init__(self, storage_file: str = "data/achievements.json"):
        self.storage_file = storage_file
        self.load()
    
    def load(self):
        """Load achievements from storage"""
        try:
            with open(self.storage_file, 'r') as f:
                self.data = json.load(f)
        except:
            self.data = {"achievements": {}}
    
    def save(self):
        """Save achievements to storage"""
        import os
        os.makedirs("data", exist_ok=True)
        with open(self.storage_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def check_achievements(self, pet: Pet) -> List[Dict]:
        """Check for new achievements"""
        new_achievements = []
        
        # Check each achievement
        for ach_id, ach in ACHIEVEMENTS.items():
            if ach_id in pet.achievements:
                continue  # Already earned
            
            earned = False
            
            # First steps - hatch egg
            if ach_id == "first_steps" and pet.eggs_hatched > 0:
                earned = True
            
            # Baby steps - level 5
            elif ach_id == "baby_steps" and pet.level >= 5:
                earned = True
            
            # Teen spirit - evolve to teen
            elif ach_id == "teen_spirit" and pet.stage.value in ["teen", "adult", "legendary"]:
                earned = True
            
            # Grown up - evolve to adult
            elif ach_id == "grown_up" and pet.stage.value in ["adult", "legendary"]:
                earned = True
            
            # Legendary - reach legendary
            elif ach_id == "legendary" and pet.stage.value == "legendary":
                earned = True
            
            # Battle winner - win first battle
            elif ach_id == "battle_winner" and pet.wins >= 1:
                earned = True
            
            # Warrior - win 10 battles
            elif ach_id == "warrior" and pet.wins >= 10:
                earned = True
            
            # Care taker - high care score
            elif ach_id == "care_taker" and pet.care_score >= 90:
                earned = True
            
            # Speed demon - high speed
            elif ach_id == "speed_demon" and pet.speed >= 80:
                earned = True
            
            # Brainiac - high intelligence
            elif ach_id == "brainiac" and pet.intelligence >= 80:
                earned = True
            
            if earned:
                pet.achievements.append(ach_id)
                pet.xp += ach["xp"]
                new_achievements.append({
                    "id": ach_id,
                    "name": ach["name"],
                    "desc": ach["desc"],
                    "xp": ach["xp"]
                })
        
        return new_achievements
    
    def get_all_achievements(self, pet: Pet) -> Dict:
        """Get all achievements (earned and not)"""
        return {
            ach_id: {
                "name": ach["name"],
                "desc": ach["desc"],
                "xp": ach["xp"],
                "earned": ach_id in pet.achievements
            }
            for ach_id, ach in ACHIEVEMENTS.items()
        }
    
    def achievements_ascii(self, pet: Pet) -> str:
        """Display achievements as ASCII"""
        achievements = self.get_all_achievements(pet)
        
        lines = ["╭─ ACHIEVEMENTS ──────────────────╮"]
        
        earned_count = 0
        for ach_id, ach in achievements.items():
            if ach["earned"]:
                earned_count += 1
                lines.append(f"│ 🏆 {ach['name']}")
                lines.append(f"│    {ach['desc']}")
        
        if earned_count == 0:
            lines.append("│ No achievements yet!")
        
        lines.append("├──────────────────────────────────")
        lines.append(f"│ {earned_count}/{len(ACHIEVEMENTS)} earned")
        lines.append("╰──────────────────────────────────╯")
        
        return "\n".join(lines)


# === Test ===

if __name__ == "__main__":
    from pet import Pet
    
    # Create a pet with some stats
    pet = Pet(name="TestPet", owner="tester", level=10, wins=5, eggs_hatched=1)
    pet.care_score = 95
    pet.speed = 85
    pet.intelligence = 70
    
    # Check achievements
    mgr = AchievementManager()
    new = mgr.check_achievements(pet)
    
    print(f"New achievements: {len(new)}")
    for ach in new:
        print(f"  + {ach['name']}: {ach['xp']} XP")
    
    print("")
    print(mgr.achievements_ascii(pet))
