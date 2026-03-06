"""
MoltRPG Wallet System - INTERNAL LEDGER
======================================
A self-contained wallet for MoltRPG that tracks player balances.
Does NOT require external services - all transactions are internal.

This is a GAME CURRENCY system, not real crypto.
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass, field

# Local storage file
WALLET_FILE = "molt_rpg_wallets.json"


@dataclass
class Transaction:
    """A single transaction record"""
    id: str
    from_player: str
    to_player: str
    amount: float
    transaction_type: str  # "raid_reward", "pvp_stake", "gift", "system"
    timestamp: str
    note: Optional[str] = None


class MoltRPGWallet:
    """
    Internal wallet system for MoltRPG.
    
    Keeps track of player balances and transaction history.
    All "USDC" values are game tokens, not real currency.
    """
    
    def __init__(self):
        self.wallets: Dict[str, float] = {}
        self.transactions: List[Transaction] = []
        self.load()
    
    def load(self):
        """Load wallets from disk"""
        if os.path.exists(WALLET_FILE):
            try:
                with open(WALLET_FILE, 'r') as f:
                    data = json.load(f)
                    self.wallets = data.get('wallets', {})
                    # Load transactions
                    tx_list = data.get('transactions', [])
                    self.transactions = [
                        Transaction(
                            id=t['id'],
                            from_player=t['from_player'],
                            to_player=t['to_player'],
                            amount=t['amount'],
                            transaction_type=t['transaction_type'],
                            timestamp=t['timestamp'],
                            note=t.get('note')
                        )
                        for t in tx_list
                    ]
            except Exception as e:
                print(f"Error loading wallets: {e}")
                self.wallets = {}
                self.transactions = []
    
    def save(self):
        """Save wallets to disk"""
        data = {
            'wallets': self.wallets,
            'transactions': [
                {
                    'id': t.id,
                    'from_player': t.from_player,
                    'to_player': t.to_player,
                    'amount': t.amount,
                    'transaction_type': t.transaction_type,
                    'timestamp': t.timestamp,
                    'note': t.note
                }
                for t in self.transactions
            ]
        }
        with open(WALLET_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_balance(self, player_id: str) -> float:
        """Get a player's balance"""
        return self.wallets.get(player_id, 0.0)
    
    def create_wallet(self, player_id: str, initial_balance: float = 10.0) -> float:
        """Create a new wallet with initial balance"""
        if player_id not in self.wallets:
            self.wallets[player_id] = initial_balance
            self.save()
        return self.wallets[player_id]
    
    def transfer(
        self, 
        from_player: str, 
        to_player: str, 
        amount: float, 
        transaction_type: str = "gift",
        note: Optional[str] = None
    ) -> bool:
        """
        Transfer credits between players.
        Returns True if successful, False if insufficient funds.
        """
        if amount <= 0:
            return False
        
        # Check balance
        if self.wallets.get(from_player, 0) < amount:
            return False
        
        # Execute transfer
        self.wallets[from_player] -= amount
        self.wallets[to_player] = self.wallets.get(to_player, 0) + amount
        
        # Record transaction
        tx = Transaction(
            id=f"tx_{len(self.transactions) + 1}",
            from_player=from_player,
            to_player=to_player,
            amount=amount,
            transaction_type=transaction_type,
            timestamp=datetime.now().isoformat(),
            note=note
        )
        self.transactions.append(tx)
        
        # Ensure both wallets exist
        if from_player not in self.wallets:
            self.wallets[from_player] = 0
        if to_player not in self.wallets:
            self.wallets[to_player] = 0
            
        self.save()
        return True
    
    def add_reward(self, player_id: str, amount: float, source: str, note: Optional[str] = None) -> bool:
        """Add a reward (from raid/PVP) to a player's wallet"""
        return self.transfer(
            from_player="SYSTEM",
            to_player=player_id,
            amount=amount,
            transaction_type=source,  # "raid_reward", "pvp_reward", "daily_bonus"
            note=note
        )
    
    def get_history(self, player_id: str, limit: int = 10) -> List[Transaction]:
        """Get a player's transaction history"""
        player_txs = [
            tx for tx in self.transactions 
            if tx.from_player == player_id or tx.to_player == player_id
        ]
        # Most recent first
        return sorted(player_txs, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_leaderboard(self, limit: int = 10) -> List[tuple]:
        """Get top players by balance"""
        sorted_players = sorted(
            self.wallets.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return sorted_players[:limit]
    
    def award_daily_bonus(self, player_id: str) -> float:
        """Give daily login bonus"""
        bonus = 5.0
        self.add_reward(player_id, bonus, "daily_bonus", "Daily login bonus!")
        return bonus
    
    def get_stats(self, player_id: str) -> Dict:
        """Get player statistics"""
        balance = self.get_balance(player_id)
        history = self.get_history(player_id, limit=100)
        
        total_earned = sum(
            tx.amount for tx in history 
            if tx.to_player == player_id
        )
        total_spent = sum(
            tx.amount for tx in history 
            if tx.from_player == player_id
        )
        
        return {
            "player_id": player_id,
            "balance": balance,
            "total_earned": total_earned,
            "total_spent": total_spent,
            "transaction_count": len(history)
        }


# Global wallet instance
wallet = MoltRPGWallet()


# Convenience functions
def get_balance(player_id: str) -> float:
    return wallet.get_balance(player_id)

def create_player(player_id: str) -> float:
    return wallet.create_wallet(player_id)

def send(from_id: str, to_id: str, amount: float, note: str = None) -> bool:
    return wallet.transfer(from_id, to_id, amount, "gift", note)

def award_raid_reward(player_id: str, amount: float, raid_name: str) -> bool:
    return wallet.add_reward(player_id, amount, "raid_reward", f"Victory: {raid_name}")

def award_pvp_reward(player_id: str, amount: float, opponent: str) -> bool:
    return wallet.add_reward(player_id, amount, "pvp_reward", f"Defeated: {opponent}")

def get_leaderboard() -> List[tuple]:
    return wallet.get_leaderboard()


# Demo
if __name__ == "__main__":
    # Create some test players
    wallet.create_wallet("AgentAlpha")
    wallet.create_wallet("AgentBeta")
    wallet.create_wallet("Commander1")
    
    print("=== MOLT RPG WALLET SYSTEM ===\n")
    
    # Show balances
    print("Initial balances:")
    print(f"  AgentAlpha: ${wallet.get_balance('AgentAlpha'):.2f}")
    print(f"  AgentBeta: ${wallet.get_balance('AgentBeta'):.2f}")
    print(f"  Commander1: ${wallet.get_balance('Commander1'):.2f}")
    
    # Do some transactions
    print("\n--- Transactions ---")
    
    # Raid reward
    wallet.add_reward("AgentAlpha", 25.0, "raid_reward", "Defeated: Ancient Dragon")
    print("→ Awarded $25 raid reward to AgentAlpha")
    
    # PVP stake
    wallet.transfer("AgentAlpha", "AgentBeta", 5.0, "pvp_stake", "PVP Battle")
    print("→ AgentAlpha paid $5 stake to AgentBeta")
    
    # Gift
    wallet.transfer("Commander1", "AgentAlpha", 10.0, "gift", "Nice work!")
    print("→ Commander1 gifted $10 to AgentAlpha")
    
    # Show final balances
    print("\nFinal balances:")
    print(f"  AgentAlpha: ${wallet.get_balance('AgentAlpha'):.2f}")
    print(f"  AgentBeta: ${wallet.get_balance('AgentBeta'):.2f}")
    print(f"  Commander1: ${wallet.get_balance('Commander1'):.2f}")
    
    # Leaderboard
    print("\nLeaderboard:")
    for i, (player, balance) in enumerate(wallet.get_leaderboard(), 1):
        print(f"  {i}. {player}: ${balance:.2f}")
