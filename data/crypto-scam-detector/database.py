"""
Database layer for Crypto Scam Detector
Stores address data, transactions, and risk assessments
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
from contextlib import contextmanager

class CryptoDatabase:
    """Manages local database of crypto address data"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to user's config directory
            config_dir = Path.home() / ".config" / "crypto-scam-detector"
            config_dir.mkdir(parents=True, exist_ok=True)
            db_path = config_dir / "crypto_data.db"
        
        self.db_path = str(db_path)
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Addresses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS addresses (
                    address TEXT PRIMARY KEY,
                    chain TEXT NOT NULL DEFAULT 'ethereum',
                    risk_score INTEGER NOT NULL DEFAULT 0,
                    risk_level TEXT NOT NULL DEFAULT 'unknown',
                    is_known_scam BOOLEAN DEFAULT FALSE,
                    is_contract BOOLEAN DEFAULT FALSE,
                    is_verified BOOLEAN DEFAULT FALSE,
                    scam_type TEXT,
                    reputation TEXT,
                    balance_wei TEXT,
                    balance_eth REAL,
                    transaction_count INTEGER,
                    first_seen_block INTEGER,
                    last_seen_block INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_etherscan_sync TIMESTAMP,
                    metadata JSON
                )
            """)
            
            # Transactions table (store suspicious transactions)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    tx_hash TEXT PRIMARY KEY,
                    address TEXT NOT NULL,
                    block_number INTEGER,
                    timestamp INTEGER,
                    from_address TEXT,
                    to_address TEXT,
                    value TEXT,
                    input_data TEXT,
                    decoded_message TEXT,
                    is_suspicious BOOLEAN DEFAULT FALSE,
                    suspicion_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (address) REFERENCES addresses(address)
                )
            """)
            
            # Scam indicators table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scam_indicators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    address TEXT NOT NULL,
                    indicator_type TEXT NOT NULL,
                    indicator_value TEXT,
                    confidence INTEGER,
                    source TEXT,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (address) REFERENCES addresses(address)
                )
            """)
            
            # Sync queue table (addresses to check with Etherscan)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_queue (
                    address TEXT PRIMARY KEY,
                    chain TEXT NOT NULL DEFAULT 'ethereum',
                    priority INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    retry_count INTEGER DEFAULT 0,
                    last_attempt TIMESTAMP,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_addresses_risk ON addresses(risk_score)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_addresses_scam ON addresses(is_known_scam)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_address ON transactions(address)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_suspicious ON transactions(is_suspicious)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sync_queue_status ON sync_queue(status)")
    
    def get_address(self, address: str) -> Optional[Dict]:
        """Get address data from database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM addresses WHERE LOWER(address) = LOWER(?)", (address,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def upsert_address(self, address_data: Dict) -> bool:
        """Insert or update address data"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Prepare data
                address = address_data.get('address', '').lower()
                metadata = address_data.get('metadata', {})
                
                cursor.execute("""
                    INSERT INTO addresses (
                        address, chain, risk_score, risk_level, is_known_scam,
                        is_contract, is_verified, scam_type, reputation,
                        balance_wei, balance_eth, transaction_count,
                        first_seen_block, last_seen_block, last_etherscan_sync,
                        metadata, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(address) DO UPDATE SET
                        chain = excluded.chain,
                        risk_score = excluded.risk_score,
                        risk_level = excluded.risk_level,
                        is_known_scam = excluded.is_known_scam,
                        is_contract = excluded.is_contract,
                        is_verified = excluded.is_verified,
                        scam_type = excluded.scam_type,
                        reputation = excluded.reputation,
                        balance_wei = excluded.balance_wei,
                        balance_eth = excluded.balance_eth,
                        transaction_count = excluded.transaction_count,
                        first_seen_block = excluded.first_seen_block,
                        last_seen_block = excluded.last_seen_block,
                        last_etherscan_sync = excluded.last_etherscan_sync,
                        metadata = excluded.metadata,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    address,
                    address_data.get('chain', 'ethereum'),
                    address_data.get('risk_score', 0),
                    address_data.get('risk_level', 'unknown'),
                    address_data.get('is_known_scam', False),
                    address_data.get('is_contract', False),
                    address_data.get('is_verified', False),
                    address_data.get('scam_type'),
                    address_data.get('reputation'),
                    address_data.get('balance_wei'),
                    address_data.get('balance_eth'),
                    address_data.get('transaction_count'),
                    address_data.get('first_seen_block'),
                    address_data.get('last_seen_block'),
                    datetime.utcnow().isoformat() if address_data.get('synced') else None,
                    json.dumps(metadata)
                ))
                
                return True
        except Exception as e:
            print(f"Error upserting address: {e}")
            return False
    
    def add_transaction(self, tx_data: Dict) -> bool:
        """Add transaction to database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO transactions (
                        tx_hash, address, block_number, timestamp,
                        from_address, to_address, value, input_data,
                        decoded_message, is_suspicious, suspicion_reason
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tx_data.get('tx_hash'),
                    tx_data.get('address', '').lower(),
                    tx_data.get('block_number'),
                    tx_data.get('timestamp'),
                    tx_data.get('from_address'),
                    tx_data.get('to_address'),
                    tx_data.get('value'),
                    tx_data.get('input_data'),
                    tx_data.get('decoded_message'),
                    tx_data.get('is_suspicious', False),
                    tx_data.get('suspicion_reason')
                ))
                
                return True
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False
    
    def add_scam_indicator(self, address: str, indicator_type: str, 
                          indicator_value: str, confidence: int, source: str) -> bool:
        """Add scam indicator for an address"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO scam_indicators (
                        address, indicator_type, indicator_value, confidence, source
                    ) VALUES (?, ?, ?, ?, ?)
                """, (address.lower(), indicator_type, indicator_value, confidence, source))
                
                return True
        except Exception as e:
            print(f"Error adding indicator: {e}")
            return False
    
    def get_scam_indicators(self, address: str) -> List[Dict]:
        """Get all scam indicators for an address"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM scam_indicators 
                WHERE LOWER(address) = LOWER(?)
                ORDER BY confidence DESC, detected_at DESC
            """, (address,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_suspicious_transactions(self, address: str) -> List[Dict]:
        """Get suspicious transactions for an address"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM transactions 
                WHERE LOWER(address) = LOWER(?) AND is_suspicious = TRUE
                ORDER BY block_number DESC
            """, (address,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def add_to_sync_queue(self, address: str, chain: str = 'ethereum', 
                         priority: int = 0) -> bool:
        """Add address to sync queue for background worker"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR IGNORE INTO sync_queue (address, chain, priority)
                    VALUES (?, ?, ?)
                """, (address.lower(), chain, priority))
                
                return True
        except Exception as e:
            print(f"Error adding to sync queue: {e}")
            return False
    
    def get_next_sync_job(self) -> Optional[Dict]:
        """Get next address to sync from queue"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get highest priority pending job
            cursor.execute("""
                SELECT * FROM sync_queue 
                WHERE status = 'pending' AND retry_count < 3
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if row:
                # Mark as processing
                cursor.execute("""
                    UPDATE sync_queue 
                    SET status = 'processing', last_attempt = CURRENT_TIMESTAMP
                    WHERE address = ?
                """, (row['address'],))
                
                return dict(row)
            return None
    
    def update_sync_status(self, address: str, status: str, 
                          error_message: str = None) -> bool:
        """Update sync queue status"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if status == 'failed':
                    cursor.execute("""
                        UPDATE sync_queue 
                        SET status = ?, error_message = ?, retry_count = retry_count + 1
                        WHERE LOWER(address) = LOWER(?)
                    """, (status, error_message, address))
                else:
                    cursor.execute("""
                        UPDATE sync_queue 
                        SET status = ?, error_message = NULL
                        WHERE LOWER(address) = LOWER(?)
                    """, (status, address))
                
                return True
        except Exception as e:
            print(f"Error updating sync status: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total addresses
            cursor.execute("SELECT COUNT(*) as count FROM addresses")
            stats['total_addresses'] = cursor.fetchone()['count']
            
            # Known scams
            cursor.execute("SELECT COUNT(*) as count FROM addresses WHERE is_known_scam = TRUE")
            stats['known_scams'] = cursor.fetchone()['count']
            
            # High risk addresses
            cursor.execute("SELECT COUNT(*) as count FROM addresses WHERE risk_score >= 80")
            stats['high_risk'] = cursor.fetchone()['count']
            
            # Pending syncs
            cursor.execute("SELECT COUNT(*) as count FROM sync_queue WHERE status = 'pending'")
            stats['pending_syncs'] = cursor.fetchone()['count']
            
            # Recent syncs (last 24h)
            cursor.execute("""
                SELECT COUNT(*) as count FROM addresses 
                WHERE last_etherscan_sync > datetime('now', '-1 day')
            """)
            stats['synced_24h'] = cursor.fetchone()['count']
            
            return stats


if __name__ == "__main__":
    # Test database
    db = CryptoDatabase()
    print("✅ Database initialized successfully!")
    print(f"📁 Location: {db.db_path}")
    print("\n📊 Stats:", db.get_stats())
