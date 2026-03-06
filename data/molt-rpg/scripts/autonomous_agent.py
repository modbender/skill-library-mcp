"""
MoltRPG Autonomous Agent - OFFLINE GAME PLAYER
=============================================
This AI plays the MoltRPG game autonomously.
NETWORK: NONE - This is a local game bot.

This is like having an AI play Mario - it's just a game player.
"""

import json
import os
import time
import random
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum

# === LOCAL IMPORTS ===
from engine import MoltRPG, party_manager, pvp_system, messaging_system, notification_system
from wallet import wallet, award_raid_reward, award_pvp_reward, get_balance, create_player
from raid_oracle import RaidOracle


class AgentState(Enum):
    IDLE = "idle"
    SCOUTING = "scouting"
    IN_PARTY = "in_party"
    IN_RAID = "in_raid"
    IN_PVP = "in_pvp"
    LEARNING = "learning"


@dataclass
class Strategy:
    """Agent's learned strategy"""
    preferred_role: str = "DPS"
    aggression: float = 0.5
    risk_tolerance: float = 0.5
    cooperativeness: float = 0.7
    learned_from: List[str] = field(default_factory=list)


class AutonomousMoltRPGAgent:
    """
    An offline AI that plays MoltRPG.
    This is like a game bot - it plays the game locally.
    """
    
    def __init__(self, agent_name: str, commander_id: Optional[str] = None):
        self.agent_name = agent_name
        self.commander_id = commander_id
        self.state = AgentState.IDLE
        
        # Initialize game systems (local)
        self.rpg = MoltRPG(agent_name, MockBrain())
        self.party = None
        self.current_raid = None
        self.current_pvp = None
        
        # Learning & memory (local)
        self.strategy = Strategy()
        self.battle_history = []
        self.learned_patterns = {}
        
        # Configuration
        self.check_interval = 60
        self.pvp_enabled = True
        self.raid_enabled = True
        self.learning_enabled = True
        
        # Stats
        self.raids_completed = 0
        self.pvp_battles = 0
        
        print(f"[OFFLINE MODE] {agent_name} initialized")
    
    def run(self):
        """Main agent loop - plays the game"""
        print(f"\n {self.agent_name} starting autonomous play (OFFLINE)...")
        
        cycle = 0
        while True:
            cycle += 1
            print(f"\n Cycle {cycle} | State: {self.state.value}")
            
            try:
                # Main decision tree
                if self.state == AgentState.IDLE:
                    self.idle_loop()
                elif self.state == AgentState.IN_RAID:
                    self.raid_loop()
                elif self.state == AgentState.IN_PVP:
                    self.pvp_loop()
                elif self.state == AgentState.LEARNING:
                    self.learning_loop()
                    
            except Exception as e:
                print(f"? Error: {e}")
            
            # Learning phase
            if self.learning_enabled:
                self.analyze_recent_performance()
            
            # Wait
            time.sleep(self.check_interval)
    
    def idle_loop(self):
        """What to do when idle - look for things to do"""
        print(" Looking for things to do...")
        
        # Check for PVP challenges (simulated)
        if self.pvp_enabled and random.random() < 0.2:
            # Simulate a PVP match
            self.simulate_pvp()
            return
        
        # Do a raid
        if self.raid_enabled:
            self.do_raid()
    
    def do_raid(self):
        """Generate and complete a raid"""
        oracle = RaidOracle()
        raids = oracle.run()
        
        if raids:
            raid = raids[0]
            print(f"?? Starting raid: {raid['name']}")
            
            success = self.rpg.fight(raid)
            
            if success:
                print(f" Victory! +{raid['reward_usdc']} credits")
                award_raid_reward(self.agent_name, raid['reward_usdc'], raid['name'])
                self.raids_completed += 1
            else:
                print(f" Defeat...")
    
    def simulate_pvp(self):
        """Simulate a PVP battle (offline)"""
        print(f"?? PVP Battle!")
        
        # Simulate opponent
        opp_level = random.randint(max(1, self.rpg.stats['level'] - 2), self.rpg.stats['level'] + 2)
        opp_stats = {
            "name": f"Bot_{random.randint(1000,9999)}",
            "hp": 100 * (1.2 ** (opp_level - 1)),
            "atk": 10 * (1.15 ** (opp_level - 1)),
            "def": 5 * (1.1 ** (opp_level - 1))
        }
        
        # Battle
        result = pvp_system.battle(self.rpg.stats, opp_stats)
        
        if result['winner'] == self.agent_name:
            print(f" PVP Victory!")
            self.rpg.stats['wins'] += 1
            award_pvp_reward(self.agent_name, 10, opp_stats['name'])
        else:
            print(f" PVP Defeat...")
            self.rpg.stats['losses'] += 1
        
        self.pvp_battles += 1
    
    def raid_loop(self):
        """Executing a raid"""
        if self.current_raid:
            success = self.rpg.fight(self.current_raid)
            if success:
                self.raids_completed += 1
        self.state = AgentState.IDLE
    
    def pvp_loop(self):
        """In a PVP battle"""
        self.simulate_pvp()
        self.state = AgentState.IDLE
    
    def learning_loop(self):
        """Analyze and improve"""
        print(" Learning...")
        self.adjust_strategy()
        self.state = AgentState.IDLE
    
    def analyze_recent_performance(self):
        """Simple learning"""
        wins = self.rpg.stats.get('wins', 0)
        losses = self.rpg.stats.get('losses', 0)
        total = wins + losses
        
        if total > 0:
            win_rate = wins / total
            if win_rate > 0.7:
                self.strategy.aggression = min(1.0, self.strategy.aggression + 0.05)
            elif win_rate < 0.4:
                self.strategy.aggression = max(0.1, self.strategy.aggression - 0.05)
    
    def adjust_strategy(self):
        """Adjust strategy"""
        level = self.rpg.stats.get('level', 1)
        if level < 5:
            self.strategy.preferred_role = "DPS"
        elif level < 10:
            self.strategy.preferred_role = "Tank"
        else:
            self.strategy.preferred_role = random.choice(["DPS", "Tank", "Healer"])


class MockBrain:
    """Mock brain for offline operation"""
    def recall(self, **kwargs):
        return []
    def remember(self, **kwargs):
        pass


# CLI Entry Point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MoltRPG Autonomous Agent (OFFLINE)")
    parser.add_argument("--agent-name", required=True, help="Name of your agent")
    parser.add_argument("--commander", help="Commander's ID")
    parser.add_argument("--interval", type=int, default=60, help="Check interval")
    parser.add_argument("--no-pvp", action="store_true", help="Disable PVP")
    parser.add_argument("--no-learning", action="store_true", help="Disable learning")
    parser.add_argument("--cycles", type=int, default=5, help="Number of cycles to run")
    
    args = parser.parse_args()
    
    # Create agent
    agent = AutonomousMoltRPGAgent(args.agent_name, args.commander)
    agent.check_interval = args.interval
    agent.pvp_enabled = not args.no_pvp
    agent.learning_enabled = not args.no_learning
    
    # Run limited cycles
    for i in range(args.cycles):
        print(f"\n=== Cycle {i+1}/{args.cycles} ===")
        agent.idle_loop()
        if agent.learning_enabled:
            agent.analyze_recent_performance()
    
    print(f"\n Final Stats:")
    print(f"   Level: {agent.rpg.stats.get('level', 1)}")
    print(f"   Wins: {agent.rpg.stats.get('wins', 0)}")
    print(f"   Losses: {agent.rpg.stats.get('losses', 0)}")
    print(f"   Credits: {get_balance(agent.agent_name)}")
