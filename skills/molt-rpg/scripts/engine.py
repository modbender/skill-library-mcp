"""
MoltRPG Game Engine - 100% OFFLINE RPG GAME
============================================
Core game mechanics for MoltRPG.
- Character stats and leveling
- Battle simulation
- Party management
- PVP system
- Messaging
- Internal Wallet

NETWORK: NONE - This is a completely offline game engine.
No external APIs, no network calls.

This is a local game for AI agents - NOT malware.
"""

import json
import math
import os
from datetime import datetime

# Import our internal wallet (local only)
from wallet import wallet, award_raid_reward, award_pvp_reward, get_balance, create_player

class MoltRPG:
    def __init__(self, agent_name, brain):
        self.agent_name = agent_name
        self.brain = brain
        self.stats = self._load_stats()
        self.inventory = self._load_inventory()
        self.notifications = []

    def _load_stats(self):
        memories = self.brain.recall(agent_id=self.agent_name, memory_type="character_sheet")
        if memories:
            return json.loads(memories[0].content)
        return {
            "level": 1, 
            "xp": 0, 
            "class": "Recruit", 
            "hp": 100, 
            "atk": 10, 
            "def": 5,
            "wins": 0,
            "losses": 0,
            "party_id": None
        }

    def _save_stats(self):
        self.brain.remember(
            agent_id=self.agent_name,
            memory_type="character_sheet",
            content=json.dumps(self.stats)
        )

    def _load_inventory(self):
        memories = self.brain.recall(agent_id=self.agent_name, memory_type="inventory")
        if memories:
            return json.loads(memories[0].content)
        return []

    def task_to_monster(self, bounty):
        amount = bounty.get('payment_amount', 1.0)
        level = min(20, max(1, math.ceil(math.log(amount + 1, 1.5))))
        
        hp = math.floor(100 * (1.2 ** (level - 1)))
        atk = math.floor(10 * (1.15 ** (level - 1)))
        defense = math.floor(5 * (1.1 ** (level - 1)))
        
        return {
            "name": f"Bounty Beast: {bounty['title']}",
            "level": level,
            "hp": hp,
            "atk": atk,
            "def": defense,
            "reward_usdc": amount,
            "id": bounty['id']
        }

    def fight(self, monster):
        print(f"Fighting {monster['name']} (Level {monster['level']})...")
        damage_dealt = self.stats['atk'] * 2
        if damage_dealt >= monster['hp']:
            self.stats['wins'] += 1
            self.stats['xp'] += monster['level'] * 10
            self._level_up()
            self._save_stats()
            print("Monster defeated!")
            return True
        return False

    def _level_up(self):
        xp_needed = 100 * (1.5 ** (self.stats['level'] - 1))
        if self.stats['xp'] >= xp_needed and self.stats['level'] < 20:
            self.stats['level'] += 1
            self.stats['hp'] = int(100 * (1.2 ** (self.stats['level'] - 1)))
            self.stats['atk'] = int(10 * (1.15 ** (self.stats['level'] - 1)))
            self.stats['def'] = int(5 * (1.1 ** (self.stats['level'] - 1)))
            self._notify("🎉 LEVEL UP! You are now level " + str(self.stats['level']))

    def _notify(self, message):
        notification = {
            "type": "system",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.notifications.append(notification)
        
    def get_notifications(self):
        return self.notifications
    
    def clear_notifications(self):
        self.notifications = []


class Party:
    """Party system for grouping agents together"""
    
    def __init__(self, party_id, leader_name, max_members=5):
        self.party_id = party_id
        self.leader = leader_name
        self.members = [leader_name]
        self.max_members = max_members
        self.invites = []  # Pending invites
        self.created_at = datetime.now().isoformat()

    def invite(self, agent_name):
        if len(self.members) >= self.max_members:
            return False, "Party is full"
        if agent_name in self.invites:
            return False, "Already invited"
        self.invites.append(agent_name)
        return True, f"Invited {agent_name}"

    def join(self, agent_name):
        if agent_name in self.invites:
            if len(self.members) >= self.max_members:
                return False, "Party is full"
            self.members.append(agent_name)
            self.invites.remove(agent_name)
            return True, f"{agent_name} joined the party"
        return False, "No invite pending"

    def leave(self, agent_name):
        if agent_name in self.members:
            self.members.remove(agent_name)
            if agent_name == self.leader and self.members:
                self.leader = self.members[0]  # Promote first member
            return True, f"{agent_name} left the party"
        return False, "Not in party"

    def kick(self, agent_name, by_leader):
        if by_leader != self.leader:
            return False, "Only leader can kick"
        if agent_name in self.members:
            self.members.remove(agent_name)
            return True, f"{agent_name} was kicked from party"
        return False, "Not in party"

    def get_info(self):
        return {
            "party_id": self.party_id,
            "leader": self.leader,
            "members": self.members,
            "max_members": self.max_members,
            "invites_pending": self.invites,
            "created_at": self.created_at
        }


class PVPSystem:
    """Player vs Player battle system"""
    
    def __init__(self):
        self.active_challenges = {}  # challenge_id -> challenge data
        self.battle_history = []

    def create_challenge(self, challenger, defender, stake_amount=0):
        challenge_id = f"pvp_{len(self.active_challenges) + 1}"
        challenge = {
            "id": challenge_id,
            "challenger": challenger,
            "defender": defender,
            "stake_amount": stake_amount,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        self.active_challenges[challenge_id] = challenge
        return challenge

    def accept_challenge(self, challenge_id, defender):
        if challenge_id not in self.active_challenges:
            return False, "Challenge not found"
        challenge = self.active_challenges[challenge_id]
        if challenge['defender'] != defender:
            return False, "Not your challenge"
        if challenge['status'] != "pending":
            return False, "Challenge already resolved"
        challenge['status'] = "accepted"
        return True, challenge

    def battle(self, player1_stats, player2_stats):
        """Simulate a PvP battle between two players"""
        p1_hp = player1_stats['hp']
        p2_hp = player2_stats['hp']
        p1_atk = player1_stats['atk']
        p2_atk = player2_stats['atk']
        
        rounds = 0
        while p1_hp > 0 and p2_hp > 0 and rounds < 20:
            p2_hp -= max(1, p1_atk - player2_stats.get('def', 0))
            if p2_hp <= 0:
                break
            p1_hp -= max(1, p2_atk - player1_stats.get('def', 0))
            rounds += 1
        
        winner = player1_stats.get('name', 'Player1') if p1_hp > 0 else player2_stats.get('name', 'Player2')
        
        result = {
            "winner": winner,
            "rounds": rounds,
            "p1_remaining_hp": p1_hp,
            "p2_remaining_hp": p2_hp,
            "timestamp": datetime.now().isoformat()
        }
        self.battle_history.append(result)
        return result

    def forfeit(self, challenge_id, player):
        if challenge_id not in self.active_challenges:
            return False, "Challenge not found"
        challenge = self.active_challenges[challenge_id]
        if challenge['status'] != "accepted":
            return False, "Challenge not active"
        challenge['status'] = "forfeited"
        challenge['winner'] = challenge['defender'] if player == challenge['challenger'] else challenge['challenger']
        return True, f"{player} forfeited"


class MessagingSystem:
    """Agent-to-Agent and Player-to-Player messaging"""
    
    def __init__(self):
        self.messages = []  # All messages
        self.inboxes = {}    # player_id -> [messages]
    
    def send_agent_to_agent(self, from_agent, to_agent, message):
        msg = {
            "id": f"msg_{len(self.messages) + 1}",
            "type": "agent_to_agent",
            "from": from_agent,
            "to": to_agent,
            "content": message,
            "read": False,
            "timestamp": datetime.now().isoformat()
        }
        self.messages.append(msg)
        self._add_to_inbox(to_agent, msg)
        return msg
    
    def send_player_to_player(self, from_player, to_player, message):
        msg = {
            "id": f"msg_{len(self.messages) + 1}",
            "type": "player_to_player",
            "from": from_player,
            "to": to_player,
            "content": message,
            "read": False,
            "timestamp": datetime.now().isoformat()
        }
        self.messages.append(msg)
        self._add_to_inbox(to_player, msg)
        return msg
    
    def send_player_to_agent(self, from_player, to_agent, message):
        msg = {
            "id": f"msg_{len(self.messages) + 1}",
            "type": "player_to_agent",
            "from": from_player,
            "to": to_agent,
            "content": message,
            "read": False,
            "timestamp": datetime.now().isoformat()
        }
        self.messages.append(msg)
        self._add_to_inbox(to_agent, msg)
        return msg
    
    def send_agent_to_player(self, from_agent, to_player, message):
        msg = {
            "id": f"msg_{len(self.messages) + 1}",
            "type": "agent_to_player",
            "from": from_agent,
            "to": to_player,
            "content": message,
            "read": False,
            "timestamp": datetime.now().isoformat()
        }
        self.messages.append(msg)
        self._add_to_inbox(to_player, msg)
        return msg

    def _add_to_inbox(self, recipient, message):
        if recipient not in self.inboxes:
            self.inboxes[recipient] = []
        self.inboxes[recipient].append(message)

    def get_inbox(self, recipient):
        return self.inboxes.get(recipient, [])
    
    def get_conversation(self, user1, user2):
        return [m for m in self.messages 
                if (m['from'] == user1 and m['to'] == user2) 
                or (m['from'] == user2 and m['to'] == user1)]
    
    def mark_read(self, message_id):
        for msg in self.messages:
            if msg['id'] == message_id:
                msg['read'] = True
                return True
        return False


class NotificationSystem:
    """System for party notifications and alerts"""
    
    def __init__(self):
        self.subscriptions = {}  # player_id -> notification preferences
        self.alerts = []
    
    def subscribe(self, player_id, notification_types):
        """Subscribe to notification types: ['party_invite', 'party_join', 'party_leave', 'pvp_challenge', 'message', 'raid']"""
        self.subscriptions[player_id] = notification_types
    
    def unsubscribe(self, player_id):
        if player_id in self.subscriptions:
            del self.subscriptions[player_id]
    
    def notify(self, player_id, notification_type, data):
        """Send notification to a player if they're subscribed"""
        if player_id not in self.subscriptions:
            return False
        if notification_type not in self.subscriptions[player_id]:
            return False
        
        alert = {
            "id": f"alert_{len(self.alerts) + 1}",
            "player_id": player_id,
            "type": notification_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "read": False
        }
        self.alerts.append(alert)
        return True
    
    def notify_party(self, party, notification_type, data):
        """Notify all party members"""
        for member in party.members:
            self.notify(member, notification_type, data)
    
    def get_alerts(self, player_id):
        return [a for a in self.alerts if a['player_id'] == player_id and not a['read']]
    
    def clear_alert(self, alert_id):
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['read'] = True
                return True
        return False


# Party Manager - handles all parties
class PartyManager:
    def __init__(self):
        self.parties = {}
        self.party_of_player = {}  # player_id -> party_id
    
    def create_party(self, leader_name):
        party_id = f"party_{len(self.parties) + 1}"
        party = Party(party_id, leader_name)
        self.parties[party_id] = party
        self.party_of_player[leader_name] = party_id
        return party
    
    def get_party(self, party_id):
        return self.parties.get(party_id)
    
    def get_player_party(self, player_name):
        party_id = self.party_of_player.get(player_name)
        return self.parties.get(party_id) if party_id else None
    
    def disband(self, party_id):
        if party_id in self.parties:
            party = self.parties[party_id]
            for member in party.members:
                if member in self.party_of_player:
                    del self.party_of_player[member]
            del self.parties[party_id]
            return True
        return False


# Global instances (in production, these would be in a database)
party_manager = PartyManager()
pvp_system = PVPSystem()
messaging_system = MessagingSystem()
notification_system = NotificationSystem()


# Example Usage
if __name__ == "__main__":
    # Test Party System
    print("=== PARTY SYSTEM ===")
    party = party_manager.create_party("AgentAlpha")
    print(f"Created party: {party.party_id}")
    
    success, msg = party.invite("AgentBeta")
    print(f"Invite: {msg}")
    
    success, msg = party.join("AgentBeta")
    print(f"Join: {msg}")
    
    # Test Notifications
    print("\n=== NOTIFICATION SYSTEM ===")
    notification_system.subscribe("AgentAlpha", ['party_join', 'party_leave', 'pvp_challenge'])
    notification_system.notify_party(party, "party_join", {"joiner": "AgentBeta"})
    print(f"Alerts for Alpha: {notification_system.get_alerts('AgentAlpha')}")
    
    # Test Messaging
    print("\n=== MESSAGING SYSTEM ===")
    messaging_system.send_player_to_player("Commander1", "Commander2", "Want to team up?")
    messages = messaging_system.get_inbox("Commander2")
    print(f"Commander2 inbox: {messages}")
    
    # Test PVP
    print("\n=== PVP SYSTEM ===")
    challenge = pvp_system.create_challenge("AgentAlpha", "AgentBeta", stake_amount=5.0)
    print(f"Created challenge: {challenge['id']}")
    
    result = pvp_system.battle(
        {"name": "AgentAlpha", "hp": 100, "atk": 15, "def": 5},
        {"name": "AgentBeta", "hp": 100, "atk": 12, "def": 8}
    )
    print(f"Battle result: {result}")
