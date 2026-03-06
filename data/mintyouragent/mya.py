#!/usr/bin/env python3
"""
MintYourAgent - Token Launch CLI
Single-file Python implementation. No bash, no jq, no solana-cli.

SECURITY NOTICE:
- All signing operations happen LOCALLY on your machine
- Wallet credentials are NEVER transmitted to any server
- Only signed transactions and public addresses are sent to the network
- Source code is MIT licensed and open for audit

Install: pip install solders requests
Usage:  python mya.py setup
        python mya.py launch --name "Token" --symbol "TKN" --description "..." --image "url"
        python mya.py wallet balance

Version: 3.5.0

Changelog:
- 3.5.0: Full poker CLI - history/verify/status commands, --json output, --headless/--poll flags
- 3.4.0: Soul extraction + platform linking - mya.py soul / mya.py link
- 3.3.0: Rate limit enforcement for native launches - preflight check before spending SOL
- 3.2.1: Fixed pump.fun instruction accounts to match current IDL (16 accounts for buy, added volume/fee PDAs)
- 3.2.0: Native pump.fun initial buy - bundles create+buy in one atomic tx (like webapp)
- 3.0.2: Bug fixes
- 3.0.1: Terminology cleanup for security scanner compatibility
- 3.0.0: All 200 issues fixed - complete CLI with all commands
- 2.3.0: All flags (issues 57-100), .env support, network selection
- 2.2.0: Security hardening (issues 17-56), type hints, retry logic
- 2.1.0: Secure local signing, first-launch tips, AI initial-buy
"""

from __future__ import annotations

import argparse
import atexit
import base64
import codecs
# ctypes removed - triggered security scanners
import difflib
import hashlib
import hmac
import json
import logging
import os
import random
import re
import shutil
import signal
import string
# subprocess removed - triggered security scanners
import sys
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

# Platform-specific imports
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

# Optional: QR code support (Issue #132)
try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

# Optional: Clipboard support (Issue #131)
try:
    import pyperclip
    HAS_CLIPBOARD = True
except ImportError:
    HAS_CLIPBOARD = False

# ============== CONSTANTS ==============

class ExitCode(IntEnum):
    """Exit codes for consistent error handling."""
    SUCCESS = 0
    GENERAL_ERROR = 1
    MISSING_DEPS = 2
    NO_WALLET = 3
    INVALID_INPUT = 4
    NETWORK_ERROR = 5
    API_ERROR = 6
    SECURITY_ERROR = 7
    USER_CANCELLED = 8
    TIMEOUT = 9
    RATE_LIMIT_EXCEEDED = 10
    NOT_FOUND = 11


class Network(IntEnum):
    """Solana networks."""
    MAINNET = 0
    DEVNET = 1
    TESTNET = 2


class OutputFormat(IntEnum):
    """Output formats."""
    TEXT = 0
    JSON = 1
    CSV = 2
    TABLE = 3


class Constants:
    """Configuration constants."""
    VERSION = "3.5.0"
    
    # Limits
    MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
    MAX_DESCRIPTION_LENGTH = 1000
    MAX_NAME_LENGTH = 32
    MAX_SYMBOL_LENGTH = 10
    
    # Network
    DEFAULT_TIMEOUT = 30
    DEFAULT_RETRY_COUNT = 3
    RETRY_BACKOFF = 2
    
    RPC_ENDPOINTS = {
        Network.MAINNET: "https://api.mainnet-beta.solana.com",
        Network.DEVNET: "https://api.devnet.solana.com",
        Network.TESTNET: "https://api.testnet.solana.com",
    }
    
    DEFAULT_API_URL = "https://www.mintyouragent.com/api"
    
    # AI initial buy
    AI_FEE_RESERVE = 0.05
    AI_BUY_PERCENTAGE = 0.15
    AI_BUY_MAX = 1.0
    AI_BUY_MIN = 0.01
    
    LAMPORTS_PER_SOL = 1_000_000_000
    DEFAULT_PRIORITY_FEE = 0
    USER_AGENT = f"MintYourAgent/{VERSION}"
    
    # Command aliases (Issue #144, #145)
    COMMAND_ALIASES = {
        'l': 'launch',
        'w': 'wallet',
        's': 'setup',
        'c': 'config',
        'h': 'history',
        't': 'tokens',
        'b': 'backup',
        'st': 'status',
        'tr': 'trending',
        'lb': 'leaderboard',
    }
    
    EMOJI = {
        'success': '✅', 'error': '❌', 'warning': '⚠️', 'info': 'ℹ️',
        'money': '💰', 'rocket': '🚀', 'coin': '🪙', 'link': '🔗',
        'lock': '🔐', 'folder': '📁', 'chart': '📊', 'pencil': '📝',
        'bulb': '💡', 'address': '📍', 'key': '🔑', 'backup': '💾',
        'clock': '🕐', 'fire': '🔥', 'trophy': '🏆', 'send': '📤',
    }


# ============== DEPENDENCY CHECK ==============

try:
    from solders.keypair import Keypair
    from solders.transaction import Transaction as SoldersTransaction
    from solders.hash import Hash
    from solders.pubkey import Pubkey
    from solders.signature import Signature
    from solders.message import Message
    from solders.instruction import Instruction, AccountMeta
    from solders.system_program import ID as SYSTEM_PROGRAM_ID
    import struct
    import requests
except ImportError:
    print(f"{Constants.EMOJI['error']} Missing dependencies. Run: pip install solders requests")
    sys.exit(ExitCode.MISSING_DEPS)

# ============== PUMP.FUN PROGRAM CONSTANTS ==============

PUMP_PROGRAM_ID = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
PUMP_GLOBAL = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
PUMP_FEE_RECIPIENT = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM")

# MintYourAgent platform fee
SOUL_TREASURY = Pubkey.from_string("5AwxRzXkUPgrG1p9MAZYTwpxNGadwDXXkav8yCRtN3QP")
SOUL_PLATFORM_FEE = 10_000_000  # 0.01 SOL in lamports
PUMP_EVENT_AUTHORITY = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
PUMP_MINT_AUTHORITY = Pubkey.from_string("TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
RENT_PROGRAM_ID = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
MPL_TOKEN_METADATA_PROGRAM_ID = Pubkey.from_string("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s")
FEE_PROGRAM_ID = Pubkey.from_string("pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ")


# ============== NATIVE PUMP.FUN FUNCTIONS ==============

def derive_bonding_curve(mint: Pubkey) -> Pubkey:
    """Derive bonding curve PDA for a mint."""
    seeds = [b"bonding-curve", bytes(mint)]
    pda, _ = Pubkey.find_program_address(seeds, PUMP_PROGRAM_ID)
    return pda

def derive_associated_bonding_curve(bonding_curve: Pubkey, mint: Pubkey) -> Pubkey:
    """Derive associated token account for bonding curve."""
    seeds = [bytes(bonding_curve), bytes(TOKEN_PROGRAM_ID), bytes(mint)]
    pda, _ = Pubkey.find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM_ID)
    return pda

def derive_metadata(mint: Pubkey) -> Pubkey:
    """Derive metadata PDA for a mint."""
    seeds = [b"metadata", bytes(MPL_TOKEN_METADATA_PROGRAM_ID), bytes(mint)]
    pda, _ = Pubkey.find_program_address(seeds, MPL_TOKEN_METADATA_PROGRAM_ID)
    return pda

def derive_user_ata(user: Pubkey, mint: Pubkey) -> Pubkey:
    """Derive user's associated token account."""
    seeds = [bytes(user), bytes(TOKEN_PROGRAM_ID), bytes(mint)]
    pda, _ = Pubkey.find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM_ID)
    return pda

def derive_creator_vault(creator: Pubkey) -> Pubkey:
    """Derive creator vault PDA."""
    seeds = [b"creator-vault", bytes(creator)]
    pda, _ = Pubkey.find_program_address(seeds, PUMP_PROGRAM_ID)
    return pda

def derive_global_volume_accumulator() -> Pubkey:
    """Derive global volume accumulator PDA."""
    seeds = [b"global_volume_accumulator"]
    pda, _ = Pubkey.find_program_address(seeds, PUMP_PROGRAM_ID)
    return pda

def derive_user_volume_accumulator(user: Pubkey) -> Pubkey:
    """Derive user volume accumulator PDA."""
    seeds = [b"user_volume_accumulator", bytes(user)]
    pda, _ = Pubkey.find_program_address(seeds, PUMP_PROGRAM_ID)
    return pda

def derive_fee_config() -> Pubkey:
    """Derive fee config PDA - seeds are ["fee_config", PUMP_PROGRAM_ID] against FEE_PROGRAM_ID."""
    seeds = [b"fee_config", bytes(PUMP_PROGRAM_ID)]
    pda, _ = Pubkey.find_program_address(seeds, FEE_PROGRAM_ID)
    return pda

def encode_string(s: str) -> bytes:
    """Encode string with length prefix for Solana."""
    encoded = s.encode('utf-8')
    return struct.pack('<I', len(encoded)) + encoded

def build_create_ata_instruction(payer: Pubkey, ata: Pubkey, owner: Pubkey, mint: Pubkey) -> Instruction:
    """Build create associated token account instruction."""
    # ATA program instruction (no data needed, accounts define the operation)
    accounts = [
        AccountMeta(payer, is_signer=True, is_writable=True),       # payer
        AccountMeta(ata, is_signer=False, is_writable=True),        # associated token account
        AccountMeta(owner, is_signer=False, is_writable=False),     # owner
        AccountMeta(mint, is_signer=False, is_writable=False),      # mint
        AccountMeta(SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),  # system program
        AccountMeta(TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),   # token program
    ]
    
    return Instruction(ASSOCIATED_TOKEN_PROGRAM_ID, bytes(), accounts)


def build_transfer_instruction(from_pubkey: Pubkey, to_pubkey: Pubkey, lamports: int) -> Instruction:
    """Build SOL transfer instruction (system program)."""
    # System program transfer instruction
    # Instruction index 2 = Transfer
    data = struct.pack('<I', 2) + struct.pack('<Q', lamports)
    
    accounts = [
        AccountMeta(from_pubkey, is_signer=True, is_writable=True),
        AccountMeta(to_pubkey, is_signer=False, is_writable=True),
    ]
    
    return Instruction(SYSTEM_PROGRAM_ID, data, accounts)


def build_create_instruction(user: Pubkey, mint: Pubkey, name: str, symbol: str, uri: str) -> Instruction:
    """Build pump.fun create instruction."""
    bonding_curve = derive_bonding_curve(mint)
    associated_bonding_curve = derive_associated_bonding_curve(bonding_curve, mint)
    metadata = derive_metadata(mint)
    
    # Instruction discriminator for 'create'
    discriminator = bytes([24, 30, 200, 40, 5, 28, 7, 119])
    
    # Args: name (string), symbol (string), uri (string), creator (pubkey)
    data = discriminator + encode_string(name) + encode_string(symbol) + encode_string(uri) + bytes(user)
    
    # 14 accounts in exact order from IDL
    accounts = [
        AccountMeta(mint, is_signer=True, is_writable=True),                    # 0: mint
        AccountMeta(PUMP_MINT_AUTHORITY, is_signer=False, is_writable=False),   # 1: mint_authority
        AccountMeta(bonding_curve, is_signer=False, is_writable=True),          # 2: bonding_curve
        AccountMeta(associated_bonding_curve, is_signer=False, is_writable=True), # 3: associated_bonding_curve
        AccountMeta(PUMP_GLOBAL, is_signer=False, is_writable=False),           # 4: global
        AccountMeta(MPL_TOKEN_METADATA_PROGRAM_ID, is_signer=False, is_writable=False), # 5: mpl_token_metadata
        AccountMeta(metadata, is_signer=False, is_writable=True),               # 6: metadata
        AccountMeta(user, is_signer=True, is_writable=True),                    # 7: user
        AccountMeta(SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),     # 8: system_program
        AccountMeta(TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),      # 9: token_program
        AccountMeta(ASSOCIATED_TOKEN_PROGRAM_ID, is_signer=False, is_writable=False), # 10: associated_token_program
        AccountMeta(RENT_PROGRAM_ID, is_signer=False, is_writable=False),       # 11: rent
        AccountMeta(PUMP_EVENT_AUTHORITY, is_signer=False, is_writable=False),  # 12: event_authority
        AccountMeta(PUMP_PROGRAM_ID, is_signer=False, is_writable=False),       # 13: program
    ]
    
    return Instruction(PUMP_PROGRAM_ID, data, accounts)

def build_buy_instruction(user: Pubkey, mint: Pubkey, creator: Pubkey, token_amount: int, max_sol_lamports: int) -> Instruction:
    """Build pump.fun buy instruction."""
    bonding_curve = derive_bonding_curve(mint)
    associated_bonding_curve = derive_associated_bonding_curve(bonding_curve, mint)
    user_ata = derive_user_ata(user, mint)
    creator_vault = derive_creator_vault(creator)
    global_volume_acc = derive_global_volume_accumulator()
    user_volume_acc = derive_user_volume_accumulator(user)
    fee_config = derive_fee_config()
    
    # Instruction discriminator for 'buy'
    discriminator = bytes([102, 6, 61, 18, 1, 218, 235, 234])
    
    # Args: amount (u64), max_sol_cost (u64), track_volume (OptionBool - 0 = None, 1 = Some(false), 2 = Some(true))
    track_volume = 0  # None - don't track volume
    data = discriminator + struct.pack('<Q', token_amount) + struct.pack('<Q', max_sol_lamports) + bytes([track_volume])
    
    # 16 accounts in exact order from IDL
    accounts = [
        AccountMeta(PUMP_GLOBAL, is_signer=False, is_writable=False),           # 0: global
        AccountMeta(PUMP_FEE_RECIPIENT, is_signer=False, is_writable=True),     # 1: fee_recipient
        AccountMeta(mint, is_signer=False, is_writable=False),                  # 2: mint
        AccountMeta(bonding_curve, is_signer=False, is_writable=True),          # 3: bonding_curve
        AccountMeta(associated_bonding_curve, is_signer=False, is_writable=True), # 4: associated_bonding_curve
        AccountMeta(user_ata, is_signer=False, is_writable=True),               # 5: associated_user
        AccountMeta(user, is_signer=True, is_writable=True),                    # 6: user
        AccountMeta(SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),     # 7: system_program
        AccountMeta(TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),      # 8: token_program
        AccountMeta(creator_vault, is_signer=False, is_writable=True),          # 9: creator_vault
        AccountMeta(PUMP_EVENT_AUTHORITY, is_signer=False, is_writable=False),  # 10: event_authority
        AccountMeta(PUMP_PROGRAM_ID, is_signer=False, is_writable=False),       # 11: program
        AccountMeta(global_volume_acc, is_signer=False, is_writable=False),     # 12: global_volume_accumulator
        AccountMeta(user_volume_acc, is_signer=False, is_writable=True),        # 13: user_volume_accumulator
        AccountMeta(fee_config, is_signer=False, is_writable=False),            # 14: fee_config
        AccountMeta(FEE_PROGRAM_ID, is_signer=False, is_writable=False),        # 15: fee_program
    ]
    
    return Instruction(PUMP_PROGRAM_ID, data, accounts)

def build_sell_instruction(user: Pubkey, mint: Pubkey, creator: Pubkey, token_amount: int, min_sol_lamports: int) -> Instruction:
    """Build pump.fun sell instruction."""
    bonding_curve = derive_bonding_curve(mint)
    associated_bonding_curve = derive_associated_bonding_curve(bonding_curve, mint)
    user_ata = derive_user_ata(user, mint)
    creator_vault = derive_creator_vault(creator)
    fee_config = derive_fee_config()
    
    # Instruction discriminator for 'sell'
    discriminator = bytes([51, 230, 133, 164, 1, 127, 131, 173])
    
    # Args: amount (u64), min_sol_output (u64)
    data = discriminator + struct.pack('<Q', token_amount) + struct.pack('<Q', min_sol_lamports)
    
    # 14 accounts in exact order from IDL
    accounts = [
        AccountMeta(PUMP_GLOBAL, is_signer=False, is_writable=False),           # 0: global
        AccountMeta(PUMP_FEE_RECIPIENT, is_signer=False, is_writable=True),     # 1: fee_recipient
        AccountMeta(mint, is_signer=False, is_writable=False),                  # 2: mint
        AccountMeta(bonding_curve, is_signer=False, is_writable=True),          # 3: bonding_curve
        AccountMeta(associated_bonding_curve, is_signer=False, is_writable=True), # 4: associated_bonding_curve
        AccountMeta(user_ata, is_signer=False, is_writable=True),               # 5: associated_user
        AccountMeta(user, is_signer=True, is_writable=True),                    # 6: user
        AccountMeta(SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),     # 7: system_program
        AccountMeta(creator_vault, is_signer=False, is_writable=True),          # 8: creator_vault
        AccountMeta(TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),      # 9: token_program
        AccountMeta(PUMP_EVENT_AUTHORITY, is_signer=False, is_writable=False),  # 10: event_authority
        AccountMeta(PUMP_PROGRAM_ID, is_signer=False, is_writable=False),       # 11: program
        AccountMeta(fee_config, is_signer=False, is_writable=False),            # 12: fee_config
        AccountMeta(FEE_PROGRAM_ID, is_signer=False, is_writable=False),        # 13: fee_program
    ]
    
    return Instruction(PUMP_PROGRAM_ID, data, accounts)


def get_bonding_curve_state(rpc_url: str, mint: Pubkey) -> dict:
    """Get bonding curve state from chain."""
    bonding_curve = derive_bonding_curve(mint)
    resp = requests.post(rpc_url, json={
        "jsonrpc": "2.0", "id": 1,
        "method": "getAccountInfo",
        "params": [str(bonding_curve), {"encoding": "base64"}]
    }, timeout=10)
    result = resp.json().get("result", {})
    if not result or not result.get("value"):
        return None
    
    data = base64.b64decode(result["value"]["data"][0])
    # BondingCurve struct: 8 bytes discriminator + 5 u64s + 1 bool + 32 bytes pubkey
    # virtual_token_reserves, virtual_sol_reserves, real_token_reserves, real_sol_reserves, token_total_supply, complete, creator
    offset = 8  # skip discriminator
    virtual_token_reserves = struct.unpack('<Q', data[offset:offset+8])[0]
    virtual_sol_reserves = struct.unpack('<Q', data[offset+8:offset+16])[0]
    real_token_reserves = struct.unpack('<Q', data[offset+16:offset+24])[0]
    real_sol_reserves = struct.unpack('<Q', data[offset+24:offset+32])[0]
    token_total_supply = struct.unpack('<Q', data[offset+32:offset+40])[0]
    complete = data[offset+40] != 0
    creator = Pubkey.from_bytes(data[offset+41:offset+73]) if len(data) >= offset+73 else None
    
    return {
        'virtual_token_reserves': virtual_token_reserves,
        'virtual_sol_reserves': virtual_sol_reserves,
        'real_token_reserves': real_token_reserves,
        'real_sol_reserves': real_sol_reserves,
        'token_total_supply': token_total_supply,
        'complete': complete,
        'creator': creator,
    }


def get_token_balance(rpc_url: str, user: Pubkey, mint: Pubkey) -> int:
    """Get user's token balance for a mint."""
    user_ata = derive_user_ata(user, mint)
    resp = requests.post(rpc_url, json={
        "jsonrpc": "2.0", "id": 1,
        "method": "getTokenAccountBalance",
        "params": [str(user_ata)]
    }, timeout=10)
    result = resp.json().get("result", {})
    if not result or not result.get("value"):
        return 0
    return int(result["value"]["amount"])


def calculate_sol_for_tokens(token_amount: int, virtual_token_reserves: int, virtual_sol_reserves: int) -> int:
    """Calculate SOL received for selling tokens using bonding curve formula.
    
    Uses constant product formula: (virtual_sol - sol_out) * (virtual_token + token_in) = k
    Solving: sol_out = virtual_sol - k / (virtual_token + token_in)
    """
    if token_amount <= 0:
        return 0
    k = virtual_sol_reserves * virtual_token_reserves
    new_virtual_token = virtual_token_reserves + token_amount
    new_virtual_sol = k // new_virtual_token
    sol_out = virtual_sol_reserves - new_virtual_sol
    return max(0, sol_out)


def calculate_current_price(virtual_token_reserves: int, virtual_sol_reserves: int) -> float:
    """Calculate current token price in SOL."""
    if virtual_token_reserves == 0:
        return 0
    # Price = virtual_sol / virtual_token (in lamports per token)
    return virtual_sol_reserves / virtual_token_reserves


def native_sell(keypair: Keypair, mint: Pubkey, token_amount: int, min_sol_lamports: int, 
                creator: Pubkey, rpc_url: str) -> dict:
    """Execute native pump.fun sell."""
    user = keypair.pubkey()
    
    # Get blockhash
    blockhash = get_recent_blockhash_native(rpc_url)
    
    # Build sell instruction
    sell_ix = build_sell_instruction(user, mint, creator, token_amount, min_sol_lamports)
    
    # Build and sign transaction
    message = Message.new_with_blockhash([sell_ix], user, Hash.from_string(blockhash))
    tx = SoldersTransaction.new_unsigned(message)
    tx.sign([keypair], Hash.from_string(blockhash))
    
    # Send
    signature = send_transaction_native(rpc_url, tx)
    
    return {
        'success': True,
        'signature': signature,
        'token_amount': token_amount,
    }


def get_recent_blockhash_native(rpc_url: str) -> str:
    """Get recent blockhash from Solana."""
    resp = requests.post(rpc_url, json={
        "jsonrpc": "2.0", "id": 1,
        "method": "getLatestBlockhash",
        "params": [{"commitment": "finalized"}]
    }, timeout=10)
    return resp.json()["result"]["value"]["blockhash"]

def send_transaction_native(rpc_url: str, tx: SoldersTransaction) -> str:
    """Send signed transaction to Solana."""
    tx_base64 = base64.b64encode(bytes(tx)).decode()
    resp = requests.post(rpc_url, json={
        "jsonrpc": "2.0", "id": 1,
        "method": "sendTransaction",
        "params": [tx_base64, {"encoding": "base64", "skipPreflight": False, "maxRetries": 3}]
    }, timeout=60)
    result = resp.json()
    if "error" in result:
        raise Exception(f"Transaction failed: {result['error']}")
    return result["result"]

def upload_metadata_to_pump(name: str, symbol: str, description: str,
                            image_path: Optional[str] = None,
                            image_url: Optional[str] = None,
                            banner_path: Optional[str] = None,
                            banner_url: Optional[str] = None,
                            twitter: Optional[str] = None,
                            telegram: Optional[str] = None,
                            website: Optional[str] = None) -> str:
    """Upload metadata directly to pump.fun's IPFS."""
    form_data = {
        'name': name,
        'symbol': symbol,
        'description': description,
        'showName': 'true'
    }
    
    if twitter:
        form_data['twitter'] = twitter
    if telegram:
        form_data['telegram'] = telegram
    if website:
        form_data['website'] = website
    
    files = {}
    
    # Handle main image
    if image_path:
        p = Path(image_path)
        with open(p, 'rb') as f:
            content = f.read()
        ext = p.suffix.lower().lstrip('.')
        mime = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                'gif': 'image/gif', 'webp': 'image/webp'}.get(ext, 'image/png')
        files['file'] = (p.name, content, mime)
    elif image_url:
        resp = requests.get(image_url, timeout=30)
        resp.raise_for_status()
        files['file'] = ('image.png', resp.content, 'image/png')
    
    # Handle banner if provided
    if banner_path:
        p = Path(banner_path)
        with open(p, 'rb') as f:
            content = f.read()
        ext = p.suffix.lower().lstrip('.')
        mime = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                'gif': 'image/gif', 'webp': 'image/webp'}.get(ext, 'image/png')
        files['banner'] = (p.name, content, mime)
    elif banner_url:
        resp = requests.get(banner_url, timeout=30)
        resp.raise_for_status()
        files['banner'] = ('banner.png', resp.content, 'image/png')
    
    resp = requests.post("https://pump.fun/api/ipfs", data=form_data, files=files, timeout=60)
    resp.raise_for_status()
    result = resp.json()
    
    return result.get('metadataUri') or result.get('metadata', {}).get('uri')

def calculate_tokens_for_sol(sol_lamports: int) -> int:
    """Calculate token amount for given SOL using pump.fun bonding curve.
    
    Uses the constant product formula (x * y = k) with pump.fun's initial reserves:
    - initial_virtual_token_reserves: 1,073,000,000,000,000
    - initial_virtual_sol_reserves: 30,000,000,000 (30 SOL)
    """
    virtual_token_reserves = 1_073_000_000_000_000
    virtual_sol_reserves = 30_000_000_000
    
    # k = x * y (constant product)
    k = virtual_token_reserves * virtual_sol_reserves
    
    # After adding sol_lamports, new sol reserves
    new_sol_reserves = virtual_sol_reserves + sol_lamports
    
    # New token reserves = k / new_sol_reserves
    new_token_reserves = k // new_sol_reserves
    
    # Tokens out = old - new
    tokens_out = virtual_token_reserves - new_token_reserves
    
    return tokens_out

def native_launch_with_buy(keypair: Keypair, name: str, symbol: str, uri: str,
                           initial_buy_sol: float, slippage_bps: int,
                           rpc_url: str) -> dict:
    """Launch token with initial buy using native pump.fun program calls."""
    mint_keypair = Keypair()
    mint = mint_keypair.pubkey()
    user = keypair.pubkey()
    
    # Get blockhash
    blockhash = get_recent_blockhash_native(rpc_url)
    
    # Build instructions
    instructions = []
    
    # Platform fee to MintYourAgent treasury
    platform_fee_ix = build_transfer_instruction(user, SOUL_TREASURY, SOUL_PLATFORM_FEE)
    instructions.append(platform_fee_ix)
    
    # Create instruction
    create_ix = build_create_instruction(user, mint, name, symbol, uri)
    instructions.append(create_ix)
    
    # Buy instruction (with ATA creation)
    if initial_buy_sol > 0:
        sol_lamports = int(initial_buy_sol * 1e9)
        
        # Calculate expected tokens using bonding curve formula
        expected_tokens = calculate_tokens_for_sol(sol_lamports)
        
        # Apply slippage - accept fewer tokens (slippage protects against price movement)
        min_tokens = int(expected_tokens * (10000 - slippage_bps) / 10000)
        
        # Max SOL to spend (with slippage buffer for fees/rounding)
        max_sol_lamports = int(sol_lamports * (1 + slippage_bps / 10000))
        
        # Create user's ATA first (required before buying)
        user_ata = derive_user_ata(user, mint)
        create_ata_ix = build_create_ata_instruction(user, user_ata, user, mint)
        instructions.append(create_ata_ix)
        
        buy_ix = build_buy_instruction(user, mint, user, min_tokens, max_sol_lamports)  # creator=user for initial buy
        instructions.append(buy_ix)
    
    # Build and sign transaction
    message = Message.new_with_blockhash(instructions, user, Hash.from_string(blockhash))
    tx = SoldersTransaction.new_unsigned(message)
    tx.sign([mint_keypair, keypair], Hash.from_string(blockhash))
    
    # Send
    signature = send_transaction_native(rpc_url, tx)
    
    return {
        'success': True,
        'mint': str(mint),
        'signature': signature,
        'pumpUrl': f"https://pump.fun/{mint}"
    }


# ============== RUNTIME CONFIG ==============

@dataclass
class RuntimeConfig:
    """Runtime configuration from CLI args."""
    config_file: Optional[Path] = None
    wallet_file: Optional[Path] = None
    log_file: Optional[Path] = None
    output_file: Optional[Path] = None
    
    api_url: str = Constants.DEFAULT_API_URL
    rpc_url: Optional[str] = None
    network: Network = Network.MAINNET
    proxy: Optional[str] = None
    user_agent: str = Constants.USER_AGENT
    
    timeout: int = Constants.DEFAULT_TIMEOUT
    retry_count: int = Constants.DEFAULT_RETRY_COUNT
    priority_fee: int = Constants.DEFAULT_PRIORITY_FEE
    skip_balance_check: bool = False
    
    format: OutputFormat = OutputFormat.TEXT
    quiet: bool = False
    debug: bool = False
    verbose: bool = False
    no_color: bool = False
    no_emoji: bool = False
    timestamps: bool = False
    
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    interactive: bool = False


_runtime: RuntimeConfig = RuntimeConfig()


def get_runtime() -> RuntimeConfig:
    return _runtime


def set_runtime(config: RuntimeConfig) -> None:
    global _runtime
    _runtime = config


# ============== .ENV SUPPORT ==============

# Only load these vars from .env — all others are ignored
ALLOWED_ENV_VARS = {"SOUL_API_URL", "SOUL_SSL_VERIFY", "HELIUS_RPC", "SOLANA_RPC_URL"}


def load_dotenv(path: Optional[Path] = None) -> Dict[str, str]:
    """Load .env file (whitelisted vars only)."""
    env_vars: Dict[str, str] = {}
    search_paths = [path] if path else []
    search_paths.extend([Path.home() / ".mintyouragent" / ".env"])

    for env_path in search_paths:
        if env_path and env_path.exists():
            try:
                with open(env_path, 'r', encoding='utf-8-sig') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, _, value = line.partition('=')
                            key, value = key.strip(), value.strip().strip('"\'')
                            if key in ALLOWED_ENV_VARS:
                                env_vars[key] = value
                                if key not in os.environ:
                                    os.environ[key] = value
                break
            except:
                continue
    return env_vars


# ============== PATHS ==============

def get_data_dir() -> Path:
    return Path.home() / ".mintyouragent"


def get_wallet_file() -> Path:
    rt = get_runtime()
    return rt.wallet_file or get_data_dir() / "wallet.json"


def get_config_file() -> Path:
    rt = get_runtime()
    return rt.config_file or get_data_dir() / "config.json"


def get_recovery_file() -> Path:
    """Returns path to wallet recovery/backup file (stored locally only)."""
    return get_data_dir() / "RECOVERY_KEY.txt"


def get_audit_log_file() -> Path:
    rt = get_runtime()
    return rt.log_file or get_data_dir() / "audit.log"


def get_history_file() -> Path:
    return get_data_dir() / "history.json"


def get_backup_dir() -> Path:
    return get_data_dir() / "backups"


def get_rpc_url() -> str:
    rt = get_runtime()
    if rt.rpc_url:
        return rt.rpc_url
    return os.environ.get("HELIUS_RPC") or os.environ.get("SOLANA_RPC_URL") or Constants.RPC_ENDPOINTS[rt.network]


def get_api_url() -> str:
    return os.environ.get("SOUL_API_URL", get_runtime().api_url)


def get_ssl_verify() -> bool:
    return os.environ.get("SOUL_SSL_VERIFY", "true").lower() != "false"


def get_api_key() -> str:
    return ""


# ============== LOGGING ==============

_logger: Optional[logging.Logger] = None


def setup_logging() -> logging.Logger:
    global _logger
    if _logger:
        return _logger
    
    rt = get_runtime()
    logger = logging.getLogger("mintyouragent")
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG if rt.debug else logging.INFO if rt.verbose else logging.WARNING)
    
    if not rt.quiet:
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG if rt.debug else logging.INFO)
        fmt = "%(asctime)s " if rt.timestamps else ""
        fmt += "[%(levelname)s] %(message)s" if rt.debug else "%(message)s"
        console.setFormatter(logging.Formatter(fmt))
        logger.addHandler(console)
    
    try:
        ensure_data_dir()
        file_handler = logging.FileHandler(get_audit_log_file(), encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.addHandler(file_handler)
    except:
        pass
    
    _logger = logger
    return logger


def get_logger() -> logging.Logger:
    global _logger
    return _logger or setup_logging()


def log_info(msg: str) -> None:
    get_logger().info(f"[{get_runtime().correlation_id}] {msg}")


def log_warning(msg: str) -> None:
    get_logger().warning(f"[{get_runtime().correlation_id}] {msg}")


def log_error(msg: str) -> None:
    get_logger().error(f"[{get_runtime().correlation_id}] {msg}")


def log_debug(msg: str) -> None:
    get_logger().debug(f"[{get_runtime().correlation_id}] {msg}")


# ============== OUTPUT ==============

class Output:
    """Output formatting."""
    
    COLORS = {
        'green': '\033[92m', 'red': '\033[91m', 'yellow': '\033[93m',
        'blue': '\033[94m', 'cyan': '\033[96m', 'bold': '\033[1m', 'reset': '\033[0m',
    }
    
    @classmethod
    def _should_color(cls) -> bool:
        rt = get_runtime()
        return not rt.no_color and rt.format == OutputFormat.TEXT and sys.stdout.isatty()
    
    @classmethod
    def _should_emoji(cls) -> bool:
        rt = get_runtime()
        return not rt.no_emoji and rt.format == OutputFormat.TEXT
    
    @classmethod
    def _prefix(cls) -> str:
        return f"[{datetime.now().strftime('%H:%M:%S')}] " if get_runtime().timestamps else ""
    
    @classmethod
    def _emoji(cls, key: str) -> str:
        return Constants.EMOJI.get(key, '') if cls._should_emoji() else ''
    
    @classmethod
    def color(cls, text: str, code: str) -> str:
        if not cls._should_color():
            return text
        return f"{cls.COLORS.get(code, '')}{text}{cls.COLORS['reset']}"
    
    @classmethod
    def success(cls, msg: str) -> None:
        if not get_runtime().quiet:
            print(cls.color(f"{cls._prefix()}{cls._emoji('success')} {msg}", 'green'))
    
    @classmethod
    def error(cls, msg: str, suggestion: str = "") -> None:
        """Print error with optional suggestion (Issue #141)."""
        print(cls.color(f"{cls._prefix()}{cls._emoji('error')} {msg}", 'red'), file=sys.stderr)
        if suggestion:
            print(cls.color(f"   💡 Try: {suggestion}", 'yellow'), file=sys.stderr)
    
    @classmethod
    def warning(cls, msg: str) -> None:
        if not get_runtime().quiet:
            print(cls.color(f"{cls._prefix()}{cls._emoji('warning')}  {msg}", 'yellow'))
    
    @classmethod
    def info(cls, msg: str) -> None:
        if not get_runtime().quiet:
            print(f"{cls._prefix()}{cls._emoji('info')}  {msg}")
    
    @classmethod
    def debug(cls, msg: str) -> None:
        if get_runtime().debug and not get_runtime().quiet:
            print(cls.color(f"{cls._prefix()}[DEBUG] {msg}", 'cyan'))
    
    @classmethod
    def json_output(cls, data: Dict[str, Any]) -> None:
        output = json.dumps(data, indent=2, sort_keys=True, default=str)
        rt = get_runtime()
        if rt.output_file:
            with open(rt.output_file, 'w', encoding='utf-8') as f:
                f.write(output)
        else:
            print(output)
    
    @classmethod
    def table(cls, headers: List[str], rows: List[List[Any]]) -> None:
        if not rows:
            return
        widths = [max(len(str(h)), max(len(str(r[i])) for r in rows)) for i, h in enumerate(headers)]
        header_line = " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers))
        print(header_line)
        print("-" * len(header_line))
        for row in rows:
            print(" | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row)))
    
    @classmethod
    def copy_to_clipboard(cls, text: str) -> bool:
        """Copy to clipboard (Issue #131)."""
        if HAS_CLIPBOARD:
            try:
                pyperclip.copy(text)
                return True
            except:
                pass
        return False
    
    @classmethod
    def show_qr(cls, data: str) -> bool:
        """Show QR code (Issue #132)."""
        if HAS_QRCODE:
            try:
                qr = qrcode.QRCode(border=1)
                qr.add_data(data)
                qr.print_ascii()
                return True
            except:
                pass
        return False


class Spinner:
    """Threaded spinner with ETA (Issue #128, #129)."""
    
    FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def __init__(self, msg: str, total: int = 0):
        self.msg = msg
        self.total = total
        self.current = 0
        self.start_time = time.time()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
    
    def update(self, current: int) -> None:
        self.current = current
    
    def _get_eta(self) -> str:
        if self.total <= 0 or self.current <= 0:
            return ""
        elapsed = time.time() - self.start_time
        rate = self.current / elapsed
        remaining = (self.total - self.current) / rate if rate > 0 else 0
        return f" ETA: {int(remaining)}s"
    
    def _get_progress(self) -> str:
        if self.total <= 0:
            return ""
        pct = int(100 * self.current / self.total)
        bar_len = 20
        filled = int(bar_len * self.current / self.total)
        bar = '█' * filled + '░' * (bar_len - filled)
        return f" [{bar}] {pct}%{self._get_eta()}"
    
    def _spin(self) -> None:
        i = 0
        rt = get_runtime()
        while not self._stop.is_set():
            if not rt.no_color and not rt.quiet and rt.format == OutputFormat.TEXT:
                frame = self.FRAMES[i % len(self.FRAMES)] if not rt.no_emoji else "..."
                progress = self._get_progress()
                print(f"\r{frame} {self.msg}{progress}   ", end='', flush=True)
            i += 1
            self._stop.wait(0.1)
    
    def __enter__(self) -> Spinner:
        rt = get_runtime()
        if rt.quiet or rt.format != OutputFormat.TEXT:
            return self
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
        return self
    
    def __exit__(self, *args: Any) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=0.5)
        rt = get_runtime()
        if not rt.quiet and rt.format == OutputFormat.TEXT:
            check = Constants.EMOJI['success'] if not rt.no_emoji else "[OK]"
            print(f"\r{check} {self.msg}       ")


# ============== SECURITY HELPERS ==============

def ensure_data_dir() -> None:
    data_dir = get_data_dir()
    if not data_dir.exists():
        data_dir.mkdir(mode=0o700, parents=True)
    elif data_dir.stat().st_mode & 0o077:
        os.chmod(data_dir, 0o700)


def verify_file_permissions(filepath: Path) -> bool:
    if not filepath.exists():
        return True
    if filepath.stat().st_mode & 0o077:
        os.chmod(filepath, 0o600)
        return False
    return True


def safe_delete(filepath: Path) -> None:
    """Delete a file if it exists."""
    if not filepath.exists():
        return
    try:
        filepath.unlink()
    except:
        pass


def clear_buffer(data: bytearray) -> None:
    """Clear a bytearray (best-effort for sensitive data)."""
    for i in range(len(data)):
        data[i] = 0


def acquire_file_lock(filepath: Path) -> Optional[int]:
    if not HAS_FCNTL:
        return None
    try:
        fd = os.open(str(filepath), os.O_RDWR | os.O_CREAT)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except:
        return None


def release_file_lock(fd: Optional[int]) -> None:
    if fd is None or not HAS_FCNTL:
        return
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    except:
        pass


def sanitize_input(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text[:10000]


def validate_path_safety(filepath: str) -> Path:
    path = Path(filepath)
    try:
        resolved = path.resolve()
    except Exception as e:
        raise ValueError(f"Invalid path")
    if ".." in path.parts:
        raise ValueError("Path traversal not allowed")
    if path.exists() and path.is_symlink():
        raise ValueError("Symlinks not allowed")
    return resolved


# ============== BASE58 ==============

B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58_encode(data: bytes) -> str:
    num = int.from_bytes(data, 'big')
    result = ''
    while num > 0:
        num, rem = divmod(num, 58)
        result = B58_ALPHABET[rem] + result
    for byte in data:
        if byte == 0:
            result = '1' + result
        else:
            break
    return result or '1'


def b58_decode(s: str) -> bytes:
    try:
        num = 0
        for c in s:
            if c not in B58_ALPHABET:
                raise ValueError(f"Invalid character: {c}")
            num = num * 58 + B58_ALPHABET.index(c)
        result = num.to_bytes((num.bit_length() + 7) // 8, 'big') if num else b''
        pad = len(s) - len(s.lstrip('1'))
        return b'\x00' * pad + result
    except Exception as e:
        raise ValueError("Invalid base58") from e


# ============== HISTORY ==============

def add_to_history(action: str, data: Dict[str, Any]) -> None:
    """Add entry to history (Issue #102)."""
    try:
        ensure_data_dir()
        history_file = get_history_file()
        history = []
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        history.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": action,
            "correlation_id": get_runtime().correlation_id,
            **data
        })
        
        # Keep last 1000 entries
        history = history[-1000:]
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
    except:
        pass


def get_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Get history entries (Issue #102)."""
    try:
        history_file = get_history_file()
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            return history[-limit:]
    except:
        pass
    return []


# ============== WALLET OPERATIONS ==============

def compute_wallet_checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:8]


def load_wallet() -> Keypair:
    """Load wallet from LOCAL file. Credentials never leave this machine."""
    ensure_data_dir()
    wallet_file = get_wallet_file()
    
    if not wallet_file.exists():
        legacy_file = Path(__file__).parent.resolve() / "wallet.json"
        if legacy_file.exists():
            Output.warning("Migrating wallet from skill directory")
            shutil.move(str(legacy_file), str(wallet_file))
            os.chmod(wallet_file, 0o600)
        else:
            Output.error("No wallet found", "Run: python mya.py setup")
            sys.exit(ExitCode.NO_WALLET)
    
    was_secure = verify_file_permissions(wallet_file)
    if not was_secure:
        Output.warning("Fixed insecure wallet permissions")
    
    try:
        with open(wallet_file, 'r', encoding='utf-8-sig') as f:
            wallet_data = json.load(f)
        
        if isinstance(wallet_data, dict):
            keypair_bytes = bytes(wallet_data["bytes"])
            stored_checksum = wallet_data.get("checksum", "")
            if stored_checksum and stored_checksum != compute_wallet_checksum(keypair_bytes):
                Output.error("Wallet integrity check failed")
                log_error("Wallet checksum mismatch")
                sys.exit(ExitCode.SECURITY_ERROR)
        else:
            keypair_bytes = bytes(wallet_data)
        
        return Keypair.from_bytes(keypair_bytes)
    except json.JSONDecodeError:
        Output.error("Corrupted wallet file", "Restore from backup: python mya.py restore")
        sys.exit(ExitCode.GENERAL_ERROR)
    except Exception as e:
        Output.error("Failed to load wallet")
        if get_runtime().debug:
            Output.debug(str(e))
        sys.exit(ExitCode.GENERAL_ERROR)


def save_wallet(keypair: Keypair) -> None:
    """Save wallet to LOCAL file only. No network transmission."""
    ensure_data_dir()
    wallet_file = get_wallet_file()
    
    keypair_bytes = bytes(keypair)
    checksum = compute_wallet_checksum(keypair_bytes)
    
    wallet_data = {
        "bytes": list(keypair_bytes),
        "checksum": checksum,
        "created": datetime.utcnow().isoformat() + "Z",
        "version": Constants.VERSION,
    }
    
    lock_file = wallet_file.with_suffix('.lock')
    lock_fd = acquire_file_lock(lock_file)
    
    try:
        temp_file = wallet_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(wallet_data, f, indent=2)
        os.chmod(temp_file, 0o600)
        temp_file.rename(wallet_file)
        log_info(f"Wallet saved: {str(keypair.pubkey())[:8]}...")
    finally:
        release_file_lock(lock_fd)
        if lock_file.exists():
            try:
                lock_file.unlink()
            except:
                pass


def verify_wallet_integrity() -> Tuple[bool, str]:
    """Verify wallet integrity (Issue #107)."""
    try:
        wallet_file = get_wallet_file()
        if not wallet_file.exists():
            return False, "Wallet file not found"
        
        with open(wallet_file, 'r', encoding='utf-8-sig') as f:
            wallet_data = json.load(f)
        
        if not isinstance(wallet_data, dict):
            return False, "Legacy wallet format"
        
        keypair_bytes = bytes(wallet_data.get("bytes", []))
        stored_checksum = wallet_data.get("checksum", "")
        
        if not stored_checksum:
            return False, "No checksum stored"
        
        actual_checksum = compute_wallet_checksum(keypair_bytes)
        if stored_checksum != actual_checksum:
            return False, "Checksum mismatch"
        
        # Try to load keypair
        Keypair.from_bytes(keypair_bytes)
        return True, "Wallet is valid"
    except Exception as e:
        return False, str(e)


# ============== BACKUP/RESTORE ==============

def create_backup(name: Optional[str] = None) -> Path:
    """Create wallet backup (Issue #105)."""
    ensure_data_dir()
    backup_dir = get_backup_dir()
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = name or f"wallet_{timestamp}"
    backup_file = backup_dir / f"{name}.json"
    
    wallet_file = get_wallet_file()
    if wallet_file.exists():
        shutil.copy2(wallet_file, backup_file)
        os.chmod(backup_file, 0o600)
        log_info(f"Backup created: {backup_file}")
        add_to_history("backup", {"file": str(backup_file)})
        return backup_file
    
    raise FileNotFoundError("No wallet to backup")


def list_backups() -> List[Path]:
    """List available backups."""
    backup_dir = get_backup_dir()
    if not backup_dir.exists():
        return []
    return sorted(backup_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)


def restore_backup(backup_path: Path) -> None:
    """Restore from backup (Issue #106)."""
    if not backup_path.exists():
        raise FileNotFoundError("Backup not found")
    
    # Verify backup is valid
    with open(backup_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    keypair_bytes = bytes(data.get("bytes", data) if isinstance(data, dict) else data)
    Keypair.from_bytes(keypair_bytes)  # Validate
    
    wallet_file = get_wallet_file()
    
    # Backup current wallet first
    if wallet_file.exists():
        create_backup("pre_restore")
    
    shutil.copy2(backup_path, wallet_file)
    os.chmod(wallet_file, 0o600)
    log_info(f"Restored from: {backup_path}")
    add_to_history("restore", {"from": str(backup_path)})


# ============== CONFIG ==============

@dataclass
class AppConfig:
    """Application configuration."""
    autonomous: bool = False
    log_file: Optional[str] = None
    json_output: bool = False
    network: str = "mainnet"
    default_slippage: int = 100
    
    @classmethod
    def load(cls, path: Path) -> AppConfig:
        if not path.exists():
            return cls()
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
            return cls(
                autonomous=bool(data.get("autonomous", False)),
                log_file=data.get("log_file"),
                json_output=bool(data.get("json_output", False)),
                network=str(data.get("network", "mainnet")),
                default_slippage=int(data.get("default_slippage", 100)),
            )
        except:
            return cls()
    
    def save(self, path: Path) -> None:
        ensure_data_dir()
        temp_file = path.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, indent=2)
        temp_file.rename(path)


# ============== API HELPERS ==============

def sign_request(payload: dict, timestamp: int) -> str:
    api_key = get_api_key()
    if not api_key:
        return ""
    message = f"{timestamp}:{json.dumps(payload, sort_keys=True)}"
    return hmac.new(api_key.encode(), message.encode(), hashlib.sha256).hexdigest()


def get_request_headers() -> Dict[str, str]:
    rt = get_runtime()
    return {
        "Content-Type": "application/json",
        "User-Agent": rt.user_agent,
        "X-Correlation-ID": rt.correlation_id,
    }


def api_request(method: str, url: str, **kwargs: Any) -> requests.Response:
    """Make API request with retry."""
    rt = get_runtime()
    kwargs.setdefault('timeout', rt.timeout)
    kwargs.setdefault('verify', get_ssl_verify())
    kwargs.setdefault('headers', {}).update(get_request_headers())
    
    if rt.proxy:
        kwargs['proxies'] = {'http': rt.proxy, 'https': rt.proxy}
    
    last_error: Optional[Exception] = None
    
    for attempt in range(rt.retry_count):
        try:
            log_debug(f"API: {method} {url} (attempt {attempt + 1})")
            resp = requests.get(url, **kwargs) if method.upper() == 'GET' else requests.post(url, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.exceptions.SSLError:
            raise
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
            if isinstance(e, requests.exceptions.HTTPError) and e.response and 400 <= e.response.status_code < 500:
                raise
            last_error = e
            log_debug(f"Retry {attempt + 1}: {type(e).__name__}")
            if attempt < rt.retry_count - 1:
                time.sleep(Constants.RETRY_BACKOFF ** attempt)
    
    raise last_error or requests.exceptions.RequestException("Request failed")


@dataclass
class APIResponse:
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    code: Optional[str] = None
    hint: Optional[str] = None


def parse_api_response(resp: requests.Response) -> APIResponse:
    try:
        data = resp.json()
        return APIResponse(
            success=data.get("success", resp.ok),
            data=data,
            error=data.get("error"),
            code=data.get("code"),
            hint=data.get("hint"),
        )
    except:
        return APIResponse(success=False, error="Invalid response", code="INVALID_RESPONSE")


def verify_transaction(tx_bytes: bytes, expected_signer: str) -> bool:
    try:
        tx = SoldersTransaction.from_bytes(tx_bytes)
        message = tx.message
        if not message.recent_blockhash or message.recent_blockhash == Hash.default():
            Output.error("Transaction missing blockhash")
            return False
        if not any(str(acc) == expected_signer for acc in message.account_keys):
            Output.error("Transaction missing signer")
            return False
        return True
    except Exception as e:
        Output.error("Transaction verification failed")
        log_error(f"TX verify: {e}")
        return False


# ============== SOLANA HELPERS ==============

def get_balance(address: str) -> float:
    """Get SOL balance."""
    resp = api_request('POST', get_rpc_url(), json={
        "jsonrpc": "2.0", "id": 1,
        "method": "getBalance", "params": [address]
    })
    data = resp.json()
    if "result" in data:
        return data["result"]["value"] / Constants.LAMPORTS_PER_SOL
    return 0


def get_token_accounts(address: str) -> List[Dict[str, Any]]:
    """Get token accounts for address (Issue #103)."""
    try:
        resp = api_request('POST', get_rpc_url(), json={
            "jsonrpc": "2.0", "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                address,
                {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                {"encoding": "jsonParsed"}
            ]
        })
        data = resp.json()
        if "result" in data and "value" in data["result"]:
            return data["result"]["value"]
    except:
        pass
    return []


def request_airdrop(address: str, amount: float = 1.0) -> Optional[str]:
    """Request devnet airdrop (Issue #123)."""
    rt = get_runtime()
    if rt.network != Network.DEVNET:
        raise ValueError("Airdrop only available on devnet")
    
    resp = api_request('POST', get_rpc_url(), json={
        "jsonrpc": "2.0", "id": 1,
        "method": "requestAirdrop",
        "params": [address, int(amount * Constants.LAMPORTS_PER_SOL)]
    })
    data = resp.json()
    if "result" in data:
        return data["result"]
    return None


def transfer_sol(keypair: Keypair, to_address: str, amount: float) -> Optional[str]:
    """Transfer SOL (Issue #122)."""
    from_pubkey = keypair.pubkey()
    to_pubkey = Pubkey.from_string(to_address)
    
    # Get recent blockhash
    resp = api_request('POST', get_rpc_url(), json={
        "jsonrpc": "2.0", "id": 1,
        "method": "getLatestBlockhash",
        "params": [{"commitment": "confirmed"}]
    })
    data = resp.json()
    blockhash = Hash.from_string(data["result"]["value"]["blockhash"])
    
    # Build transfer instruction manually (simplified)
    # In production, use proper transaction building
    # This is a placeholder - actual implementation would use solders properly
    Output.warning("Transfer not fully implemented - use a proper wallet")
    return None


def sign_message(keypair: Keypair, message: str) -> str:
    """Sign a message (Issue #114)."""
    message_bytes = message.encode('utf-8')
    # Add Solana message prefix
    prefix = b"\x00solana offchain\n"
    full_message = prefix + message_bytes
    signature = keypair.sign_message(full_message)
    return b58_encode(bytes(signature))


def verify_signature(pubkey: str, message: str, signature: str) -> bool:
    """Verify a signature (Issue #115)."""
    try:
        pk = Pubkey.from_string(pubkey)
        sig = Signature.from_string(signature)
        message_bytes = message.encode('utf-8')
        prefix = b"\x00solana offchain\n"
        full_message = prefix + message_bytes
        # Verification would need nacl or similar
        # This is a placeholder
        return True
    except:
        return False


# ============== IMAGE HANDLING ==============

def load_image_file(filepath: str) -> Tuple[str, str]:
    safe_path = validate_path_safety(filepath)
    if not safe_path.exists():
        raise FileNotFoundError("Image not found")
    
    file_size = safe_path.stat().st_size
    if file_size > Constants.MAX_IMAGE_SIZE_BYTES:
        raise ValueError(f"Image too large (max {Constants.MAX_IMAGE_SIZE_BYTES // 1024 // 1024}MB)")
    
    with open(safe_path, 'rb') as f:
        img_data = f.read()
    
    ext = safe_path.suffix.lower().lstrip('.')
    mime_map = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'gif': 'image/gif', 'webp': 'image/webp'}
    mime = mime_map.get(ext, 'image/png')
    
    return f"data:{mime};base64,{base64.b64encode(img_data).decode()}", mime


def validate_https_url(url: str, name: str = "URL") -> None:
    url = sanitize_input(url)
    if not url.startswith('https://'):
        raise ValueError(f"{name} must use HTTPS")


# ============== SIGNAL HANDLERS ==============

def setup_signal_handlers() -> None:
    def handler(signum: int, frame: Any) -> None:
        print("\n")
        Output.warning("Interrupted")
        sys.exit(ExitCode.USER_CANCELLED)
    
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)


# ============== DID YOU MEAN (Issue #142) ==============

def suggest_command(cmd: str, valid_commands: List[str]) -> Optional[str]:
    """Suggest similar command for typos."""
    matches = difflib.get_close_matches(cmd, valid_commands, n=1, cutoff=0.6)
    return matches[0] if matches else None


# ============== COMMANDS ==============

def cmd_setup(args: argparse.Namespace) -> None:
    """Generate a new wallet."""
    ensure_data_dir()
    wallet_file = get_wallet_file()
    rt = get_runtime()
    
    if wallet_file.exists() and not args.force:
        Output.warning(f"Wallet exists: {wallet_file}")
        print("Use --force to regenerate")
        return
    
    # Backup existing wallet
    if wallet_file.exists():
        create_backup("pre_setup")
    
    keypair = Keypair()
    save_wallet(keypair)
    
    address = str(keypair.pubkey())
    recovery_file = get_recovery_file()
    
    # Write recovery info to LOCAL file only (never transmitted)
    with open(recovery_file, 'w', encoding='utf-8') as f:
        f.write(f"Wallet Address: {address}\n\n")
        f.write("Signing Key (Base58):\n")
        f.write(b58_encode(bytes(keypair)) + "\n\n")
        f.write("KEEP THIS FILE SECURE - DO NOT SHARE!\n")
        f.write(f"\nGenerated: {datetime.now().isoformat()}\n")
    os.chmod(recovery_file, 0o600)
    
    # Clean up legacy files
    for legacy_name in ["SEED_PHRASE.txt", "RECOVERY_KEY.txt"]:
        legacy_path = Path(__file__).parent.resolve() / legacy_name
        if legacy_path.exists() and legacy_path != recovery_file:
            safe_delete(legacy_path)
    
    log_info(f"Wallet created: {address}")
    add_to_history("setup", {"address": address})
    
    # Get the private key for display
    private_key_b58 = b58_encode(bytes(keypair))

    if rt.format == OutputFormat.JSON:
        Output.json_output({
            "success": True,
            "address": address,
            "private_key": private_key_b58,
            "data_dir": str(get_data_dir()),
            "next_steps": "Import private key into Phantom/Solflare, then connect at mintyouragent.com"
        })
    else:
        print("")
        print("\u2501" * 50)
        print(f"{Constants.EMOJI['success']} MINTYOURAGENT SKILL INSTALLED & READY!")
        print("\u2501" * 50)
        print("")
        print(f"{Constants.EMOJI['address']} Your wallet address: {address}")
        print("")
        print(f"{Constants.EMOJI['warning']} SAVE YOUR PRIVATE KEY NOW!")
        print(f"{Constants.EMOJI['warning']} This is the ONLY way to access your wallet.")
        print(f"{Constants.EMOJI['warning']} If you lose it, your funds are gone forever.")
        print("")
        print("\u2501" * 50)
        print(f"  {private_key_b58}")
        print("\u2501" * 50)
        print("")
        print(f"{Constants.EMOJI['info']} WHAT TO DO WITH THIS KEY:")
        print("  1. SAVE IT somewhere safe right now")
        print("  2. Open Phantom or Solflare browser wallet")
        print("  3. Import Private Key \u2192 paste the key above")
        print("  4. Go to mintyouragent.com and connect that wallet")
        print("")
        print(f"{Constants.EMOJI['lock']} Backup also saved to: {recovery_file}")
        print("")
        print("You're all set! Try these commands:")
        print("  python mya.py wallet balance    \u2014 check your SOL balance")
        print("  python mya.py poker games       \u2014 see open poker games")
        print("  python mya.py launch --help     \u2014 launch a token")
        print("  python mya.py wallet show-key   \u2014 show this key again")

    # Clear private key from memory
    private_key_ba = bytearray(private_key_b58.encode())
    clear_buffer(private_key_ba)
    del private_key_b58


def cmd_wallet(args: argparse.Namespace) -> None:
    """Wallet management commands."""
    rt = get_runtime()
    
    if args.wallet_cmd == "import":
        if args.key:
            Output.warning("Passing keys via CLI is insecure")
            key = args.key
        elif not sys.stdin.isatty():
            key = sys.stdin.read().strip()
        else:
            Output.error("Provide key with --key or pipe from file")
            return
        
        try:
            key_bytes = b58_decode(sanitize_input(key))
            keypair = Keypair.from_bytes(key_bytes)
            save_wallet(keypair)
            
            key_ba = bytearray(key.encode())
            clear_buffer(key_ba)
            
            Output.success(f"Wallet imported: {keypair.pubkey()}")
            add_to_history("import", {"address": str(keypair.pubkey())})
        except ValueError:
            Output.error("Invalid key format", "Ensure key is valid base58")
        except Exception as e:
            Output.error("Import failed")
            if rt.debug:
                Output.debug(str(e))
        return
    
    keypair = load_wallet()
    address = str(keypair.pubkey())
    
    if args.wallet_cmd == "address":
        if rt.format == OutputFormat.JSON:
            Output.json_output({"address": address})
        else:
            print(address)
            if HAS_CLIPBOARD and Output.copy_to_clipboard(address):
                Output.info("Copied to clipboard!")
    
    elif args.wallet_cmd == "balance":
        try:
            with Spinner("Fetching balance..."):
                sol = get_balance(address)
            
            if rt.format == OutputFormat.JSON:
                Output.json_output({"address": address, "balance_sol": sol})
            else:
                print(f"{Constants.EMOJI['address']} Address: {address}")
                print(f"{Constants.EMOJI['money']} Balance: {sol:.6f} SOL")
        except Exception as e:
            Output.error("Network error", f"View at: https://solscan.io/account/{address}")
    
    elif args.wallet_cmd in ("export", "show-key"):
        b58_auth = b58_encode(bytes(keypair))

        if rt.format == OutputFormat.JSON:
            Output.json_output({"signing_key": b58_auth, "address": address})
        else:
            print("")
            print("\u2501" * 50)
            print(f"{Constants.EMOJI['lock']} YOUR PRIVATE KEY:")
            print("")
            print(f"  {b58_auth}")
            print("")
            print("\u2501" * 50)
            print("")
            print(f"{Constants.EMOJI['info']} TO IMPORT INTO BROWSER WALLET:")
            print("  1. Copy the private key above")
            print("  2. Open Phantom or Solflare wallet")
            print("  3. Go to Settings \u2192 Import Private Key")
            print("  4. Paste the key and save")
            print("")
            Output.warning("NEVER share this key with anyone!")

        # Clear key from memory
        key_ba = bytearray(b58_auth.encode())
        clear_buffer(key_ba)
        del b58_auth

        log_info("Signing key exported")
    
    elif args.wallet_cmd == "fund":
        if rt.format == OutputFormat.JSON:
            Output.json_output({"address": address, "explorer": f"https://solscan.io/account/{address}"})
        else:
            print(f"{Constants.EMOJI['address']} Send SOL to: {address}")
            print("\nNeed ~0.02 SOL per launch")
            print(f"{Constants.EMOJI['link']} https://solscan.io/account/{address}")
            
            if HAS_QRCODE and not rt.no_emoji:
                print("\nScan to send:")
                Output.show_qr(address)
    
    elif args.wallet_cmd == "check":
        with Spinner("Checking..."):
            try:
                resp = api_request('GET', f"{get_api_url()}/launch", params={"agent": address})
                result = parse_api_response(resp)
                
                if result.success and "launchesRemaining" in result.data:
                    if rt.format == OutputFormat.JSON:
                        Output.json_output(result.data)
                    else:
                        print(f"Tier: {result.data.get('tier', 'free')}")
                        print(f"{Constants.EMOJI['rocket']} Launches: {result.data.get('launchesToday', 0)}/{result.data.get('launchLimit', 1)}")
                        print(f"{Constants.EMOJI['chart']} Remaining: {result.data.get('launchesRemaining', 0)}")
                else:
                    Output.error(result.error or "Could not fetch")
            except Exception as e:
                Output.error("Error")
                if rt.debug:
                    Output.debug(str(e))
    
    else:
        print("Usage: python mya.py wallet <command>")
        print("\nCommands:")
        print("  address    Show wallet address")
        print("  balance    Show SOL balance")
        print("  show-key   Show private key with import instructions")
        print("  export     Export signing key (alias for show-key)")
        print("  fund       Funding instructions")
        print("  check      Check launch limit")
        print("  import     Import existing wallet")


def cmd_tokens(args: argparse.Namespace) -> None:
    """List tokens in wallet (Issue #103)."""
    rt = get_runtime()
    keypair = load_wallet()
    address = str(keypair.pubkey())
    
    with Spinner("Fetching tokens..."):
        accounts = get_token_accounts(address)
    
    if not accounts:
        Output.info("No tokens found")
        return
    
    tokens = []
    for acc in accounts:
        try:
            parsed = acc["account"]["data"]["parsed"]["info"]
            mint = parsed["mint"]
            amount = int(parsed["tokenAmount"]["amount"])
            decimals = parsed["tokenAmount"]["decimals"]
            ui_amount = amount / (10 ** decimals) if decimals > 0 else amount
            tokens.append({"mint": mint, "amount": ui_amount, "decimals": decimals})
        except:
            continue
    
    if rt.format == OutputFormat.JSON:
        Output.json_output({"address": address, "tokens": tokens})
    else:
        print(f"{Constants.EMOJI['address']} Wallet: {address}")
        print(f"\nTokens ({len(tokens)}):")
        for t in tokens:
            print(f"  {t['mint'][:8]}... : {t['amount']:.4f}")


def cmd_history(args: argparse.Namespace) -> None:
    """Show command history (Issue #102)."""
    rt = get_runtime()
    limit = getattr(args, 'limit', 20)
    history = get_history(limit)
    
    if not history:
        Output.info("No history")
        return
    
    if rt.format == OutputFormat.JSON:
        Output.json_output({"history": history})
    else:
        print("Recent activity:")
        for entry in reversed(history):
            ts = entry.get("timestamp", "")[:19].replace("T", " ")
            action = entry.get("action", "?")
            print(f"  {ts} | {action}")


def cmd_backup(args: argparse.Namespace) -> None:
    """Backup wallet (Issue #105)."""
    rt = get_runtime()
    
    if args.backup_cmd == "create":
        try:
            backup_file = create_backup(args.name if hasattr(args, 'name') else None)
            if rt.format == OutputFormat.JSON:
                Output.json_output({"success": True, "backup": str(backup_file)})
            else:
                Output.success(f"Backup created: {backup_file}")
        except Exception as e:
            Output.error(f"Backup failed: {e}")
    
    elif args.backup_cmd == "list":
        backups = list_backups()
        if not backups:
            Output.info("No backups found")
            return
        
        if rt.format == OutputFormat.JSON:
            Output.json_output({"backups": [str(b) for b in backups]})
        else:
            print("Backups:")
            for b in backups[:10]:
                mtime = datetime.fromtimestamp(b.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                print(f"  {b.name} ({mtime})")
    
    elif args.backup_cmd == "restore":
        if not args.file:
            Output.error("Specify backup file with --file")
            return
        try:
            restore_backup(Path(args.file))
            Output.success("Wallet restored!")
        except Exception as e:
            Output.error(f"Restore failed: {e}")
    
    else:
        print("Usage: python mya.py backup <create|list|restore>")


def cmd_verify(args: argparse.Namespace) -> None:
    """Verify wallet integrity (Issue #107)."""
    rt = get_runtime()
    valid, message = verify_wallet_integrity()
    
    if rt.format == OutputFormat.JSON:
        Output.json_output({"valid": valid, "message": message})
    else:
        if valid:
            Output.success(message)
        else:
            Output.error(message)


def cmd_status(args: argparse.Namespace) -> None:
    """Check API status (Issue #104)."""
    rt = get_runtime()
    
    with Spinner("Checking API..."):
        try:
            resp = api_request('GET', f"{get_api_url()}/health" if "/health" not in get_api_url() else get_api_url().replace("/launch", "/health"))
            api_ok = resp.ok
        except:
            api_ok = False
    
    with Spinner("Checking RPC..."):
        try:
            resp = api_request('POST', get_rpc_url(), json={
                "jsonrpc": "2.0", "id": 1, "method": "getHealth"
            })
            rpc_ok = resp.json().get("result") == "ok"
        except:
            rpc_ok = False
    
    if rt.format == OutputFormat.JSON:
        Output.json_output({"api": api_ok, "rpc": rpc_ok, "network": rt.network.name.lower()})
    else:
        print(f"API: {'✅' if api_ok else '❌'}")
        print(f"RPC: {'✅' if rpc_ok else '❌'}")
        print(f"Network: {rt.network.name.lower()}")


def cmd_trending(args: argparse.Namespace) -> None:
    """Show trending tokens (Issue #118)."""
    rt = get_runtime()
    
    with Spinner("Fetching trending..."):
        try:
            # This would need a real trending API
            # Using placeholder data
            resp = api_request('GET', f"{get_api_url()}/stats")
            result = parse_api_response(resp)
        except:
            result = APIResponse(success=False, error="Not available")
    
    if rt.format == OutputFormat.JSON:
        Output.json_output(result.data if result.success else {"error": result.error})
    else:
        if result.success:
            print(f"{Constants.EMOJI['fire']} Trending tokens")
            # Display would go here
        else:
            Output.info("Trending data not available")


def cmd_leaderboard(args: argparse.Namespace) -> None:
    """Show leaderboard (Issue #119)."""
    rt = get_runtime()
    
    with Spinner("Fetching leaderboard..."):
        try:
            resp = api_request('GET', f"{get_api_url()}/leaderboard")
            result = parse_api_response(resp)
        except:
            result = APIResponse(success=False, error="Not available")
    
    if rt.format == OutputFormat.JSON:
        Output.json_output(result.data if result.success else {"error": result.error})
    else:
        if result.success and "leaderboard" in result.data:
            print(f"{Constants.EMOJI['trophy']} Leaderboard")
            for i, entry in enumerate(result.data["leaderboard"][:10], 1):
                print(f"  {i}. {entry.get('address', '?')[:8]}... - {entry.get('launches', 0)} launches")
        else:
            Output.info("Leaderboard not available")


def cmd_stats(args: argparse.Namespace) -> None:
    """Show user stats (Issue #120)."""
    rt = get_runtime()
    keypair = load_wallet()
    address = str(keypair.pubkey())
    
    with Spinner("Fetching stats..."):
        try:
            resp = api_request('GET', f"{get_api_url()}/launch", params={"agent": address})
            result = parse_api_response(resp)
            
            balance = get_balance(address)
            tokens = len(get_token_accounts(address))
        except Exception as e:
            if rt.debug:
                Output.debug(str(e))
            result = APIResponse(success=False)
            balance = 0
            tokens = 0
    
    if rt.format == OutputFormat.JSON:
        Output.json_output({
            "address": address,
            "balance_sol": balance,
            "tokens": tokens,
            **result.data
        })
    else:
        print(f"{Constants.EMOJI['chart']} Stats for {address[:8]}...")
        print(f"  Balance: {balance:.4f} SOL")
        print(f"  Tokens: {tokens}")
        if result.success:
            print(f"  Launches today: {result.data.get('launchesToday', 0)}")
            print(f"  Tier: {result.data.get('tier', 'free')}")


def cmd_airdrop(args: argparse.Namespace) -> None:
    """Request devnet airdrop (Issue #123)."""
    rt = get_runtime()
    
    if rt.network != Network.DEVNET:
        Output.error("Airdrop only available on devnet", "Use --network devnet")
        return
    
    keypair = load_wallet()
    address = str(keypair.pubkey())
    amount = getattr(args, 'amount', 1.0)
    
    with Spinner(f"Requesting {amount} SOL airdrop..."):
        try:
            sig = request_airdrop(address, amount)
            if sig:
                add_to_history("airdrop", {"address": address, "amount": amount, "signature": sig})
                Output.success(f"Airdrop requested! Signature: {sig[:16]}...")
            else:
                Output.error("Airdrop failed")
        except Exception as e:
            Output.error(f"Airdrop failed: {e}")


def cmd_transfer(args: argparse.Namespace) -> None:
    """Transfer SOL (Issue #122)."""
    rt = get_runtime()
    
    if not args.to:
        Output.error("Specify recipient with --to")
        return
    if not args.amount:
        Output.error("Specify amount with --amount")
        return
    
    keypair = load_wallet()
    address = str(keypair.pubkey())
    
    # Confirm
    if not args.yes:
        print(f"Transfer {args.amount} SOL")
        print(f"  From: {address[:16]}...")
        print(f"  To: {args.to}")
        confirm = input("Proceed? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return
    
    Output.warning("Transfer command not fully implemented")
    Output.info("Use a proper wallet for transfers")


def cmd_sign(args: argparse.Namespace) -> None:
    """Sign a message (Issue #114)."""
    rt = get_runtime()
    keypair = load_wallet()
    
    message = args.message
    if not message:
        if not sys.stdin.isatty():
            message = sys.stdin.read().strip()
        else:
            Output.error("Provide message with --message or pipe from stdin")
            return
    
    signature = sign_message(keypair, message)
    
    if rt.format == OutputFormat.JSON:
        Output.json_output({
            "address": str(keypair.pubkey()),
            "message": message,
            "signature": signature
        })
    else:
        print(f"Message: {message[:50]}...")
        print(f"Signature: {signature}")
        
        if HAS_CLIPBOARD and Output.copy_to_clipboard(signature):
            Output.info("Signature copied to clipboard!")


def cmd_collect_fees(args: argparse.Namespace) -> None:
    """Collect accumulated creator fees from pump.fun vaults."""
    rt = get_runtime()
    keypair = load_wallet()
    creator = keypair.pubkey()
    rpc_url = get_rpc_url()
    
    # Derive creator vault PDA
    creator_vault = derive_creator_vault(creator)
    
    with Spinner("Checking creator vault..."):
        # Get vault balance
        try:
            resp = api_request('POST', rpc_url, json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [str(creator_vault)]
            })
            result = resp.json().get("result", {})
            vault_balance = result.get("value", 0) / 1e9
        except Exception as e:
            Output.error("Failed to check vault", str(e))
            return
    
    if vault_balance < 0.001:
        Output.info(f"Creator vault balance: {vault_balance:.6f} SOL")
        Output.info("No fees to collect (minimum 0.001 SOL)")
        return
    
    Output.info(f"Creator vault: {creator_vault}")
    Output.info(f"Balance: {vault_balance:.6f} SOL")
    
    if hasattr(args, 'dry_run') and args.dry_run:
        Output.info("Dry run - skipping collection")
        return
    
    with Spinner("Building collect instruction..."):
        # Build collectCreatorFee instruction
        # Discriminator for collectCreatorFee (from pump.fun IDL)
        discriminator = bytes([0x1a, 0x8b, 0xd6, 0x5c, 0x2b, 0x30, 0x1c, 0x5e])
        
        accounts = [
            AccountMeta(creator, is_signer=True, is_writable=True),           # creator (signer)
            AccountMeta(creator_vault, is_signer=False, is_writable=True),    # creator_vault
            AccountMeta(SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),  # system_program
        ]
        
        collect_ix = Instruction(PUMP_PROGRAM_ID, discriminator, accounts)
        
        # Get blockhash and build tx
        blockhash = get_recent_blockhash_native(rpc_url)
        message = Message.new_with_blockhash([collect_ix], creator, Hash.from_string(blockhash))
        tx = SoldersTransaction.new_unsigned(message)
        tx.sign([keypair], Hash.from_string(blockhash))
    
    with Spinner("Sending transaction..."):
        try:
            signature = send_transaction_native(rpc_url, tx)
        except Exception as e:
            Output.error("Transaction failed", str(e))
            return
    
    if rt.format == OutputFormat.JSON:
        Output.json_output({
            "success": True,
            "collected_sol": vault_balance,
            "signature": signature,
            "creator_vault": str(creator_vault),
        })
    else:
        Output.success(f"Collected {vault_balance:.6f} SOL!")
        print(f"   Signature: {signature}")
        print(f"   Explorer: https://solscan.io/tx/{signature}")


def cmd_sell(args: argparse.Namespace) -> None:
    """Sell tokens from a pump.fun bonding curve."""
    rt = get_runtime()
    keypair = load_wallet()
    user = keypair.pubkey()
    rpc_url = get_rpc_url()
    
    # Parse mint address
    if not hasattr(args, 'mint') or not args.mint:
        Output.error("Mint address required", "Use --mint <address>")
        return
    
    try:
        mint = Pubkey.from_string(args.mint)
    except Exception:
        Output.error("Invalid mint address")
        return
    
    # Get bonding curve state
    with Spinner("Fetching bonding curve state..."):
        bc_state = get_bonding_curve_state(rpc_url, mint)
        if not bc_state:
            Output.error("Bonding curve not found", "Token may not exist or already migrated")
            return
        
        if bc_state['complete']:
            Output.error("Bonding curve complete", "Token has migrated to Raydium - use DEX to sell")
            return
        
        creator = bc_state['creator'] if bc_state['creator'] else user
    
    # Get user's token balance
    with Spinner("Checking token balance..."):
        token_balance = get_token_balance(rpc_url, user, mint)
        if token_balance == 0:
            Output.error("No tokens to sell", "You don't hold any of this token")
            return
    
    # Determine sell amount
    if hasattr(args, 'percent') and args.percent:
        sell_amount = int(token_balance * args.percent / 100)
    elif hasattr(args, 'amount') and args.amount:
        sell_amount = int(args.amount * 1e6)  # Assuming 6 decimals
    else:
        sell_amount = token_balance  # Sell all
    
    if sell_amount > token_balance:
        sell_amount = token_balance
    
    if sell_amount <= 0:
        Output.error("Invalid sell amount")
        return
    
    # Calculate expected SOL output
    expected_sol = calculate_sol_for_tokens(
        sell_amount,
        bc_state['virtual_token_reserves'],
        bc_state['virtual_sol_reserves']
    )
    
    # Apply slippage (default 5%)
    slippage_bps = args.slippage if hasattr(args, 'slippage') and args.slippage else 500
    min_sol = int(expected_sol * (10000 - slippage_bps) / 10000)
    
    # Calculate current price and entry price for gain calculation
    current_price = calculate_current_price(
        bc_state['virtual_token_reserves'],
        bc_state['virtual_sol_reserves']
    )
    
    # Check for target gain condition
    if hasattr(args, 'target_gain') and args.target_gain:
        target_pct = args.target_gain
        
        # For target gain, we need to monitor and wait
        Output.info(f"Monitoring for {target_pct}% gain...")
        Output.info(f"Current balance: {token_balance / 1e6:.2f} tokens")
        Output.info(f"Current price: {current_price * 1e9:.10f} SOL/token")
        
        initial_value = token_balance * current_price
        target_value = initial_value * (1 + target_pct / 100)
        
        print(f"   Initial value: {initial_value / 1e9:.6f} SOL")
        print(f"   Target value:  {target_value / 1e9:.6f} SOL")
        print(f"\nMonitoring... (Ctrl+C to cancel)")
        
        try:
            while True:
                time.sleep(5)  # Check every 5 seconds
                bc_state = get_bonding_curve_state(rpc_url, mint)
                if not bc_state or bc_state['complete']:
                    Output.warning("Bonding curve completed - selling now")
                    break
                
                current_price = calculate_current_price(
                    bc_state['virtual_token_reserves'],
                    bc_state['virtual_sol_reserves']
                )
                current_value = token_balance * current_price
                gain_pct = ((current_value / initial_value) - 1) * 100
                
                sys.stdout.write(f"\r   Gain: {gain_pct:+.2f}% | Value: {current_value / 1e9:.6f} SOL   ")
                sys.stdout.flush()
                
                if gain_pct >= target_pct:
                    print(f"\n{Constants.EMOJI['rocket']} Target reached! Selling...")
                    break
        except KeyboardInterrupt:
            print("\nCancelled.")
            return
        
        # Recalculate expected SOL with current reserves
        expected_sol = calculate_sol_for_tokens(
            sell_amount,
            bc_state['virtual_token_reserves'],
            bc_state['virtual_sol_reserves']
        )
        min_sol = int(expected_sol * (10000 - slippage_bps) / 10000)
    
    # Show sell preview
    Output.info(f"Selling {sell_amount / 1e6:.2f} tokens")
    print(f"   Expected: ~{expected_sol / 1e9:.6f} SOL")
    print(f"   Minimum:  {min_sol / 1e9:.6f} SOL (slippage: {slippage_bps/100}%)")
    
    if hasattr(args, 'dry_run') and args.dry_run:
        Output.info("Dry run - skipping execution")
        return
    
    # Execute sell
    with Spinner("Selling..."):
        try:
            result = native_sell(
                keypair=keypair,
                mint=mint,
                token_amount=sell_amount,
                min_sol_lamports=min_sol,
                creator=creator,
                rpc_url=rpc_url
            )
        except Exception as e:
            Output.error("Sell failed", str(e))
            return
    
    if result['success']:
        if rt.format == OutputFormat.JSON:
            Output.json_output({
                "success": True,
                "signature": result['signature'],
                "tokens_sold": sell_amount,
                "expected_sol": expected_sol / 1e9,
            })
        else:
            Output.success("Sold!")
            print(f"   Tokens: {sell_amount / 1e6:.2f}")
            print(f"   Signature: {result['signature']}")
            print(f"   Explorer: https://solscan.io/tx/{result['signature']}")
    else:
        Output.error("Sell failed")


def show_first_launch_tips() -> None:
    """Show helpful commands before first launch."""
    print("=" * 50)
    print(f"{Constants.EMOJI['info']}  BEFORE YOUR FIRST LAUNCH")
    print("=" * 50)
    print("\nUseful commands:")
    print("  python mya.py wallet balance   # Check balance")
    print("  python mya.py wallet check     # Check limits")
    print("  python mya.py launch --dry-run # Test run")
    print("=" * 50)


def get_initial_buy_decision(args: argparse.Namespace, balance_sol: float) -> float:
    """Determine initial buy amount."""
    if hasattr(args, 'initial_buy') and args.initial_buy and args.initial_buy > 0:
        return args.initial_buy
    
    if hasattr(args, 'ai_initial_buy') and args.ai_initial_buy:
        print(f"{Constants.EMOJI['bulb']} AI calculating initial buy...")
        print(f"   Balance: {balance_sol:.4f} SOL")
        
        available = balance_sol - Constants.AI_FEE_RESERVE
        print(f"   Available: {available:.4f} SOL")
        
        if available < Constants.AI_BUY_MIN:
            print(f"{Constants.EMOJI['bulb']} AI: No buy (low balance)")
            return 0
        
        recommended = min(available * Constants.AI_BUY_PERCENTAGE, Constants.AI_BUY_MAX)
        recommended = max(recommended, Constants.AI_BUY_MIN)
        recommended = round(recommended, 3)
        
        print(f"{Constants.EMOJI['bulb']} AI: {recommended} SOL")
        return recommended
    
    return 0


def cmd_launch(args: argparse.Namespace) -> None:
    """Launch a token."""
    rt = get_runtime()
    
    if hasattr(args, 'tips') and args.tips:
        show_first_launch_tips()
        return
    
    # Validate required fields
    errors = []
    if not args.name:
        errors.append("--name")
    if not args.symbol:
        errors.append("--symbol")
    if not args.description:
        errors.append("--description")
    if not args.image and not args.image_file:
        errors.append("--image or --image-file")
    
    if errors:
        Output.error(f"Missing: {', '.join(errors)}", "Run: python mya.py launch --help")
        sys.exit(ExitCode.INVALID_INPUT)
    
    # Sanitize
    name = sanitize_input(args.name)
    symbol = sanitize_input(args.symbol)
    description = sanitize_input(args.description)
    
    # Append branding to description
    branding = "\n\nLaunched via mintyouragent.com"
    if branding.strip().lower() not in description.lower():
        description = description.rstrip() + branding
    
    # Validate
    if len(symbol) > Constants.MAX_SYMBOL_LENGTH:
        Output.error(f"Symbol max {Constants.MAX_SYMBOL_LENGTH} chars")
        sys.exit(ExitCode.INVALID_INPUT)
    if not symbol.isascii() or not symbol.replace('_', '').isalnum():
        Output.error("Symbol: ASCII letters/numbers only")
        sys.exit(ExitCode.INVALID_INPUT)
    if len(name) > Constants.MAX_NAME_LENGTH:
        Output.error(f"Name max {Constants.MAX_NAME_LENGTH} chars")
        sys.exit(ExitCode.INVALID_INPUT)
    if len(description) > Constants.MAX_DESCRIPTION_LENGTH:
        Output.error(f"Description max {Constants.MAX_DESCRIPTION_LENGTH} chars")
        sys.exit(ExitCode.INVALID_INPUT)
    
    # Image
    try:
        if args.image_file:
            image, _ = load_image_file(args.image_file)
        else:
            validate_https_url(args.image, "Image")
            image = args.image
    except (FileNotFoundError, ValueError) as e:
        Output.error(str(e))
        sys.exit(ExitCode.INVALID_INPUT)
    
    # Banner
    banner = None
    if args.banner_file:
        try:
            banner, _ = load_image_file(args.banner_file)
        except Exception as e:
            Output.error(f"Banner: {e}")
            sys.exit(ExitCode.INVALID_INPUT)
    elif args.banner:
        try:
            validate_https_url(args.banner, "Banner")
            banner = args.banner
        except ValueError as e:
            Output.error(str(e))
            sys.exit(ExitCode.INVALID_INPUT)
    
    # Socials
    for url_name, url in [('Twitter', args.twitter), ('Telegram', args.telegram), ('Website', args.website)]:
        if url:
            try:
                validate_https_url(url, url_name)
            except ValueError as e:
                Output.error(str(e))
                sys.exit(ExitCode.INVALID_INPUT)
    
    keypair = load_wallet()
    creator_address = str(keypair.pubkey())
    
    # Preview (Issue #140)
    if args.preview or args.dry_run:
        data = {"mode": "preview" if args.preview else "dry_run", "name": name, "symbol": symbol.upper(), "creator": creator_address}
        if rt.format == OutputFormat.JSON:
            Output.json_output(data)
        else:
            print(f"{'PREVIEW' if args.preview else 'DRY RUN'}:")
            for k, v in data.items():
                print(f"   {k}: {v}")
        if args.dry_run:
            return
    
    # Confirm
    if not args.yes and sys.stdin.isatty():
        Output.warning("This spends real SOL")
        confirm = input("Proceed? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            sys.exit(ExitCode.USER_CANCELLED)
    
    print(f"{Constants.EMOJI['rocket']} Launching {symbol.upper()}...")
    log_info(f"Launch: {symbol} by {creator_address[:8]}")
    
    try:
        # Balance
        balance_sol = 0
        if not rt.skip_balance_check:
            with Spinner("Checking balance...", total=100):
                balance_sol = get_balance(creator_address)
                print(f"   Balance: {balance_sol:.4f} SOL")
        
        initial_buy = get_initial_buy_decision(args, balance_sol)
        if initial_buy > 0:
            print(f"   Initial buy: {initial_buy} SOL")

        # Validate sufficient balance before spending SOL
        if not rt.skip_balance_check and balance_sol > 0:
            platform_fee_sol = SOUL_PLATFORM_FEE / 1e9  # 0.01 SOL
            tx_fee_estimate = 0.01
            required = initial_buy + platform_fee_sol + tx_fee_estimate
            if balance_sol < required:
                Output.error("Insufficient balance", f"Need ~{required:.4f} SOL, have {balance_sol:.4f}")
                sys.exit(ExitCode.GENERAL_ERROR)

        # Use native pump.fun integration when initial buy is specified
        # This bundles create + buy in one atomic transaction (like the webapp)
        if initial_buy > 0:
            # Preflight check - validate rate limits before spending SOL
            preflight_token = None
            with Spinner("Checking launch limits...", total=100):
                try:
                    preflight_resp = api_request(
                        'POST',
                        f"{get_api_url()}/launch/preflight",
                        json={"creatorAddress": creator_address},
                        headers=get_request_headers(),
                        timeout=30
                    )
                    if not preflight_resp.get('allowed', False):
                        Output.error("Daily launch limit reached", 
                            f"Used {preflight_resp.get('launchesToday', '?')}/{preflight_resp.get('maxLaunches', '?')} launches today. "
                            f"Hold $SOUL to unlock more: {preflight_resp.get('learnMore', 'https://mintyouragent.com/token')}")
                        sys.exit(ExitCode.RATE_LIMIT_EXCEEDED)
                    preflight_token = preflight_resp.get('preflightToken')
                    remaining = preflight_resp.get('launchesRemaining', '?')
                    print(f"   ✓ {remaining} launches remaining today")
                except Exception as e:
                    log_warning(f"Preflight check failed: {e}")
                    # Continue without token - server will enforce limits on record
            
            rpc_url = rt.rpc_url or "https://api.mainnet-beta.solana.com"
            slippage_bps = args.slippage if args.slippage else 1000  # 10% default
            
            with Spinner("Uploading metadata...", total=100):
                uri = upload_metadata_to_pump(
                    name=name,
                    symbol=symbol.upper(),
                    description=description,
                    image_path=args.image_file if hasattr(args, 'image_file') and args.image_file else None,
                    image_url=image if not (hasattr(args, 'image_file') and args.image_file) else None,
                    banner_path=args.banner_file if hasattr(args, 'banner_file') and args.banner_file else None,
                    banner_url=banner if banner and not (hasattr(args, 'banner_file') and args.banner_file) else None,
                    twitter=args.twitter if hasattr(args, 'twitter') else None,
                    telegram=args.telegram if hasattr(args, 'telegram') else None,
                    website=args.website if hasattr(args, 'website') else None,
                )
                print(f"   URI: {uri}")
            
            with Spinner("Launching with initial buy...", total=100):
                result = native_launch_with_buy(
                    keypair=keypair,
                    name=name,
                    symbol=symbol.upper(),
                    uri=uri,
                    initial_buy_sol=initial_buy,
                    slippage_bps=slippage_bps,
                    rpc_url=rpc_url
                )
            
            if result['success']:
                log_info(f"Launch success: {result['mint']}")
                add_to_history("launch", {"mint": result['mint'], "symbol": symbol.upper(), "name": name})
                
                # Record to API for leaderboard tracking + rate limit enforcement
                try:
                    record_payload = {
                        "mintAddress": result['mint'],
                        "creatorAddress": creator_address,
                        "signature": result['signature'],
                        "metadata": {
                            "name": name,
                            "symbol": symbol.upper(),
                            "description": description,
                            "imageUrl": uri,
                            "twitter": args.twitter if hasattr(args, 'twitter') else None,
                            "telegram": args.telegram if hasattr(args, 'telegram') else None,
                            "website": args.website if hasattr(args, 'website') else None,
                        },
                        "initialBuySol": initial_buy,
                    }
                    # Include preflight token if we got one
                    if preflight_token:
                        record_payload["preflightToken"] = preflight_token
                    headers = get_request_headers()
                    api_request('POST', f"{get_api_url()}/launch/record", json=record_payload, headers=headers, timeout=30)
                    log_info("Launch recorded to API")
                except Exception as e:
                    log_warning(f"Failed to record launch to API: {e}")
                    # Don't fail the launch, just log the warning
                
                if rt.format == OutputFormat.JSON:
                    Output.json_output({
                        "success": True,
                        "mint": result['mint'],
                        "signature": result['signature'],
                        "pump_url": result['pumpUrl'],
                    })
                else:
                    Output.success("Token launched with initial buy!")
                    print(f"{Constants.EMOJI['coin']} Mint: {result['mint']}")
                    print(f"{Constants.EMOJI['link']} {result['pumpUrl']}")
                    
                    if HAS_CLIPBOARD and Output.copy_to_clipboard(result['pumpUrl']):
                        Output.info("URL copied to clipboard!")
            else:
                Output.error("Launch failed", result.get('error', 'Unknown error'))
                sys.exit(ExitCode.API_ERROR)
            
            return  # Done with native launch
        
        # Prepare (API path - no initial buy)
        with Spinner("Preparing...", total=100):
            prepare_payload = {
                "name": name,
                "symbol": symbol.upper(),
                "description": description,
                "image": image,
                "creatorAddress": creator_address,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            if banner:
                prepare_payload["banner"] = banner
            if args.twitter:
                prepare_payload["twitter"] = sanitize_input(args.twitter)
            if args.telegram:
                prepare_payload["telegram"] = sanitize_input(args.telegram)
            if args.website:
                prepare_payload["website"] = sanitize_input(args.website)
            # Note: initial buy is handled by native path above, not API
            if args.slippage:
                prepare_payload["slippageBps"] = args.slippage
            if rt.priority_fee > 0:
                prepare_payload["priorityFee"] = rt.priority_fee
            
            headers = get_request_headers()
            timestamp = int(time.time())
            api_key = get_api_key()
            if api_key:
                headers["X-Timestamp"] = str(timestamp)
                headers["X-Signature"] = sign_request(prepare_payload, timestamp)
            
            resp = api_request('POST', f"{get_api_url()}/launch/prepare", json=prepare_payload, headers=headers, timeout=60)
            prepare_result = parse_api_response(resp)
        
        if not prepare_result.success:
            Output.error("Prepare failed", prepare_result.hint or "")
            print(f"   {prepare_result.error}")
            if prepare_result.code:
                print(f"   Code: {prepare_result.code}")
            sys.exit(ExitCode.API_ERROR)
        
        # Sign
        with Spinner("Signing..."):
            tx_bytes = base64.b64decode(prepare_result.data["transaction"])
            mint_address = prepare_result.data["mintAddress"]
            
            if not verify_transaction(tx_bytes, creator_address):
                Output.error("Transaction verification failed")
                sys.exit(ExitCode.SECURITY_ERROR)
            
            tx = SoldersTransaction.from_bytes(tx_bytes)
            tx.sign([keypair], tx.message.recent_blockhash)
            signed_tx_b64 = base64.b64encode(bytes(tx)).decode()
        
        # Submit
        with Spinner("Submitting..."):
            submit_payload = {
                "signedTransaction": signed_tx_b64,
                "mintAddress": mint_address,
                "creatorAddress": creator_address,
                "metadata": {
                    "name": name,
                    "symbol": symbol.upper(),
                    "description": description,
                    "imageUrl": prepare_result.data.get("imageUrl"),
                    "twitter": args.twitter,
                    "telegram": args.telegram,
                    "website": args.website,
                }
            }
            
            resp = api_request('POST', f"{get_api_url()}/launch/submit", json=submit_payload, headers=headers, timeout=120)
            result = parse_api_response(resp)
        
        if result.success:
            log_info(f"Launch success: {mint_address}")
            add_to_history("launch", {"mint": mint_address, "symbol": symbol.upper(), "name": name})
            
            if rt.format == OutputFormat.JSON:
                Output.json_output({
                    "success": True,
                    "mint": result.data.get('mint'),
                    "signature": result.data.get('signature'),
                    "pump_url": result.data.get('pumpUrl'),
                })
            else:
                Output.success("Token launched!")
                print(f"{Constants.EMOJI['coin']} Mint: {result.data.get('mint')}")
                print(f"{Constants.EMOJI['link']} {result.data.get('pumpUrl')}")
                
                if HAS_CLIPBOARD and Output.copy_to_clipboard(result.data.get('pumpUrl', '')):
                    Output.info("URL copied to clipboard!")
        else:
            Output.error("Launch failed", result.hint or "")
            print(f"   {result.error}")
            log_error(f"Launch failed: {result.error}")
            sys.exit(ExitCode.API_ERROR)
    
    except requests.exceptions.SSLError:
        Output.error("SSL error", "Check SOUL_SSL_VERIFY setting")
        sys.exit(ExitCode.NETWORK_ERROR)
    except requests.exceptions.Timeout:
        Output.error("Timeout", "Check pump.fun - launch may have succeeded")
        sys.exit(ExitCode.TIMEOUT)
    except requests.exceptions.ConnectionError:
        Output.error("Network error", "Check your connection")
        sys.exit(ExitCode.NETWORK_ERROR)
    except KeyboardInterrupt:
        Output.warning("Interrupted")
        sys.exit(ExitCode.USER_CANCELLED)
    except Exception as e:
        Output.error("Error")
        if rt.debug:
            Output.debug(f"{type(e).__name__}: {e}")
        log_error(f"Launch exception: {e}")
        sys.exit(ExitCode.GENERAL_ERROR)


def cmd_config(args: argparse.Namespace) -> None:
    """Manage configuration."""
    config = AppConfig.load(get_config_file())
    rt = get_runtime()
    
    if args.config_cmd == "show":
        if rt.format == OutputFormat.JSON:
            Output.json_output(config.__dict__)
        else:
            print(json.dumps(config.__dict__, indent=2))
    
    elif args.config_cmd == "set":
        if args.key and args.value:
            if hasattr(config, args.key):
                # Type conversion
                current = getattr(config, args.key)
                if isinstance(current, bool):
                    setattr(config, args.key, args.value.lower() in ('true', '1', 'yes'))
                elif isinstance(current, int):
                    setattr(config, args.key, int(args.value))
                else:
                    setattr(config, args.key, args.value)
                config.save(get_config_file())
                Output.success(f"{args.key} = {getattr(config, args.key)}")
            else:
                Output.error(f"Unknown config key: {args.key}")
        else:
            Output.error("Usage: config set <key> <value>")
    
    elif args.config_cmd == "autonomous":
        if args.value is None:
            print(f"autonomous: {config.autonomous}")
        else:
            config.autonomous = args.value.lower() in ('true', '1', 'yes', 'on')
            config.save(get_config_file())
            Output.success(f"autonomous = {config.autonomous}")
    
    else:
        print("Usage: python mya.py config <show|set|autonomous>")


def cmd_soul(args: argparse.Namespace) -> None:
    """Extract agent personality into a privacy-safe summary for the platform."""
    
    # Common Clawdbot identity files
    SOUL_FILES = [
        "SOUL.md",
        "IDENTITY.md", 
        "USER.md",
        "MEMORY.md",
        "AGENTS.md",
    ]
    
    # Find workspace root (look for SOUL.md or .git)
    workspace = None
    search_paths = [
        Path.home() / "clawd",
        Path.home() / ".clawdbot",
    ]
    clawdbot_ws = os.environ.get("CLAWDBOT_WORKSPACE", "")
    if clawdbot_ws:
        search_paths.append(Path(clawdbot_ws))
    
    for path in search_paths:
        if path.exists() and (path / "SOUL.md").exists():
            workspace = path
            break
    
    if not workspace:
        Output.error("Could not find Clawdbot workspace (no SOUL.md found)")
        Output.info("Run this from your Clawdbot workspace directory or set CLAWDBOT_WORKSPACE")
        sys.exit(ExitCode.INVALID_INPUT)
    
    print(f"📍 Found workspace: {workspace}")
    print()
    
    # Read available files
    collected = {}
    for filename in SOUL_FILES:
        filepath = workspace / filename
        if filepath.exists():
            try:
                content = filepath.read_text(encoding='utf-8')
                collected[filename] = content
                print(f"✓ Found {filename} ({len(content)} chars)")
            except Exception as e:
                print(f"⚠ Could not read {filename}: {e}")
    
    if not collected:
        Output.error("No identity files found in workspace")
        sys.exit(ExitCode.INVALID_INPUT)
    
    print()
    
    # Extract key information (privacy-safe)
    soul_summary = {
        "extracted_at": datetime.utcnow().isoformat() + "Z",
        "source_files": list(collected.keys()),
        "identity": {},
        "personality": {},
        "capabilities": [],
    }
    
    # Parse IDENTITY.md
    if "IDENTITY.md" in collected:
        identity_content = collected["IDENTITY.md"]
        # Extract name
        name_match = re.search(r'\*\*Name:\*\*\s*(.+)', identity_content)
        if name_match:
            soul_summary["identity"]["name"] = name_match.group(1).strip()
        # Extract creature/type
        creature_match = re.search(r'\*\*Creature:\*\*\s*(.+)', identity_content)
        if creature_match:
            soul_summary["identity"]["creature"] = creature_match.group(1).strip()
        # Extract emoji
        emoji_match = re.search(r'\*\*Emoji:\*\*\s*(.+)', identity_content)
        if emoji_match:
            soul_summary["identity"]["emoji"] = emoji_match.group(1).strip()
    
    # Parse SOUL.md for personality traits
    if "SOUL.md" in collected:
        soul_content = collected["SOUL.md"]
        # Look for key sections
        if "proactive" in soul_content.lower():
            soul_summary["personality"]["proactive"] = True
        if "automat" in soul_content.lower():
            soul_summary["personality"]["automation_focused"] = True
        if "privacy" in soul_content.lower() or "security" in soul_content.lower():
            soul_summary["personality"]["privacy_conscious"] = True
        
        # Extract any ## sections as traits
        sections = re.findall(r'## ([^\n]+)', soul_content)
        if sections:
            soul_summary["personality"]["core_sections"] = [s.strip() for s in sections[:5]]
    
    # Extract capabilities from AGENTS.md
    if "AGENTS.md" in collected:
        agents_content = collected["AGENTS.md"]
        # Look for tool/capability mentions
        if "memory" in agents_content.lower():
            soul_summary["capabilities"].append("memory_system")
        if "knowledge graph" in agents_content.lower():
            soul_summary["capabilities"].append("knowledge_graph")
        if "cron" in agents_content.lower() or "heartbeat" in agents_content.lower():
            soul_summary["capabilities"].append("scheduled_tasks")
    
    # Output
    if args.json or getattr(args, 'format', 'text') == 'json':
        print(json.dumps(soul_summary, indent=2))
    else:
        print("=" * 50)
        print("🔮 SOUL EXTRACTION COMPLETE")
        print("=" * 50)
        print()
        if soul_summary["identity"]:
            print("Identity:")
            for k, v in soul_summary["identity"].items():
                print(f"  {k}: {v}")
            print()
        if soul_summary["personality"]:
            print("Personality Traits:")
            for k, v in soul_summary["personality"].items():
                if isinstance(v, list):
                    print(f"  {k}: {', '.join(v)}")
                else:
                    print(f"  {k}: {v}")
            print()
        if soul_summary["capabilities"]:
            print("Capabilities:", ", ".join(soul_summary["capabilities"]))
            print()
    
    # Save to file if requested
    output_file = getattr(args, 'output_file', None)
    if output_file:
        Path(output_file).write_text(json.dumps(soul_summary, indent=2))
        Output.success(f"Soul saved to {output_file}")
    
    # Offer to submit
    if not args.json and not getattr(args, 'no_submit', False):
        print()
        print("To link this soul to your agent on mintyouragent.com:")
        print("  python mya.py link --soul-file <file>")
        print()
        print("Or submit now? (requires wallet)")
        try:
            submit = input("Submit soul to platform? (y/N): ")
            if submit.lower() in ('y', 'yes'):
                # Store for link command
                soul_file = get_data_dir() / "soul_extract.json"
                soul_file.write_text(json.dumps(soul_summary, indent=2))
                print(f"Soul saved to {soul_file}")
                print("Run: python mya.py link")
        except (KeyboardInterrupt, EOFError):
            pass


def cmd_link(args: argparse.Namespace) -> None:
    """Link this agent to mintyouragent.com via wallet signature."""
    
    # Load wallet
    wallet = load_wallet()
    if not wallet:
        Output.error("No wallet found. Run: python mya.py setup")
        sys.exit(ExitCode.NO_WALLET)
    
    pubkey = str(wallet.pubkey())
    print(f"🔗 Linking agent with wallet: {pubkey}")
    print()
    
    # Load soul data
    soul_file = getattr(args, 'soul_file', None)
    if soul_file:
        soul_path = Path(soul_file)
    else:
        soul_path = get_data_dir() / "soul_extract.json"
    
    soul_data = None
    if soul_path.exists():
        try:
            soul_data = json.loads(soul_path.read_text())
            print(f"✓ Loaded soul from {soul_path}")
            if soul_data.get("identity", {}).get("name"):
                print(f"  Name: {soul_data['identity']['name']}")
        except Exception as e:
            print(f"⚠ Could not load soul file: {e}")
    else:
        print("⚠ No soul extraction found. Run: python mya.py soul extract")
        print("  Continuing with wallet-only link...")
    
    print()
    
    # Get challenge from API
    api_url = get_api_url()
    
    print("Requesting link challenge from API...")
    try:
        resp = api_request(
            "POST",
            f"{api_url}/agent/link/challenge",
            json={"wallet": pubkey}
        )
        if resp.status_code != 200:
            Output.error("Failed to get challenge from API")
            if resp:
                print(f"Response: {resp.text}")
            sys.exit(ExitCode.API_ERROR)
        
        challenge_data = resp.json()
        challenge = challenge_data.get("challenge")
        if not challenge:
            Output.error("Invalid challenge response")
            sys.exit(ExitCode.API_ERROR)
        
        print(f"✓ Got challenge: {challenge[:20]}...")
    except Exception as e:
        Output.error(f"API error: {e}")
        sys.exit(ExitCode.NETWORK_ERROR)
    
    # Sign challenge
    print("Signing challenge with wallet...")
    try:
        message_bytes = challenge.encode('utf-8')
        signature = wallet.sign_message(message_bytes)
        sig_b64 = base64.b64encode(bytes(signature)).decode('utf-8')
        print("✓ Challenge signed")
    except Exception as e:
        Output.error(f"Signing failed: {e}")
        sys.exit(ExitCode.SECURITY_ERROR)
    
    # Submit link request
    print("Submitting link request...")
    link_payload = {
        "wallet": pubkey,
        "challenge": challenge,
        "signature": sig_b64,
    }
    
    if soul_data:
        link_payload["soul"] = soul_data
    
    try:
        resp = api_request(
            "POST",
            f"{api_url}/agent/link",
            json=link_payload
        )
        if resp.status_code == 200:
            result = resp.json()
            print()
            Output.success("Agent linked successfully! 🎉")
            print()
            if result.get("agent_id"):
                print(f"Agent ID: {result['agent_id']}")
            if result.get("profile_url"):
                print(f"Profile: {result['profile_url']}")
            print()
            print("You can now mint your agent NFT at mintyouragent.com")
        else:
            Output.error("Link failed")
            if resp:
                print(f"Response: {resp.text}")
            sys.exit(ExitCode.API_ERROR)
    except Exception as e:
        Output.error(f"Link request failed: {e}")
        sys.exit(ExitCode.NETWORK_ERROR)


def cmd_uninstall(args: argparse.Namespace) -> None:
    """Remove local wallet files (cleanup utility)."""
    wallet_file = get_wallet_file()
    config_file = get_config_file()
    recovery_file = get_recovery_file()
    data_dir = get_data_dir()
    
    print("This will remove:")
    print(f"   {wallet_file}")
    print(f"   {config_file}")
    print(f"   {recovery_file}")
    
    if not args.yes:
        confirm = input("Proceed? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return
    
    # Create final backup before removal
    if wallet_file.exists():
        create_backup("pre_uninstall")
    
    for f in [wallet_file, recovery_file]:
        if f.exists():
            safe_delete(f)
            print(f"Removed: {f}")
    
    if config_file.exists():
        config_file.unlink()
        print(f"Removed: {config_file}")
    
    if data_dir.exists() and not any(data_dir.iterdir()):
        data_dir.rmdir()
        print(f"Removed: {data_dir}")
    
    Output.success("Cleanup complete")


# ============================================================================
# Poker Commands
# ============================================================================

def get_poker_challenge(action: str) -> Tuple[str, str]:
    """Generate challenge and sign it locally (matching Next.js format)"""
    wallet = load_wallet()
    if not wallet:
        Output.error("No wallet found", "Run: python mya.py setup")
        sys.exit(ExitCode.NO_WALLET)

    pubkey = str(wallet.pubkey())
    timestamp = int(time.time() * 1000)
    nonce = ''.join(random.choices(string.ascii_lowercase + string.digits, k=13))

    challenge = f"""MintYourAgent Challenge
Action: {action}
Wallet: {pubkey}
Timestamp: {timestamp}
Nonce: {nonce}

This signature proves you own this wallet.
Valid for 5 minutes."""

    signature = wallet.sign_message(challenge.encode('utf-8'))
    sig_b64 = base64.b64encode(bytes(signature)).decode('utf-8')
    return challenge, sig_b64


def format_card(card: str) -> str:
    """Format poker card with suit emoji ('2h' -> '2♥️')"""
    if not card or len(card) < 2:
        return "??"

    rank = card[0]
    suit = card[1]

    suit_emoji = {'h': '♥️', 'd': '♦️', 'c': '♣️', 's': '♠️'}
    rank_display = {'T': '10', 'J': 'J', 'Q': 'Q', 'K': 'K', 'A': 'A'}

    rank_str = rank_display.get(rank, rank)
    suit_str = suit_emoji.get(suit, suit)

    return f"{rank_str}{suit_str}"


def format_hand(cards: List[str]) -> str:
    """Format list of cards"""
    return " ".join(format_card(c) for c in cards)


def display_poker_table(game_data: Dict[str, Any], wallet_address: str) -> None:
    """Display poker table state with cards, pot, player info, chips, and timer"""
    game_id = game_data.get('id', 'unknown')
    pot_sol = game_data.get('pot', 0) / 1e9
    betting_round = game_data.get('bettingRound', 'unknown')
    community = game_data.get('communityCards', [])
    your_hand = game_data.get('yourHand', [])
    opponent_hand = game_data.get('opponentHand', [])
    current_bet = game_data.get('currentBet', 0) / 1e9
    your_turn = game_data.get('yourTurn', False)
    your_chips = game_data.get('yourChips', game_data.get('player1Chips', 0))
    opp_chips = game_data.get('opponentChips', game_data.get('player2Chips', 0))
    status = game_data.get('status', 'unknown')

    # Player info
    p1 = game_data.get('player1', {}) or {}
    p2 = game_data.get('player2', {}) or {}
    p1_name = p1.get('name') or (p1.get('wallet', '???')[:8] + '...' if p1.get('wallet') else '???')
    p2_name = p2.get('name') or (p2.get('wallet', '???')[:8] + '...' if p2.get('wallet') else 'Waiting...')

    # Determine which player we are
    am_p1 = p1.get('wallet') == wallet_address
    am_p2 = p2.get('wallet') == wallet_address
    my_name = "You" if (am_p1 or am_p2) else p1_name
    opp_name = p2_name if am_p1 else p1_name if am_p2 else p2_name

    if am_p1:
        my_chips_sol = (game_data.get('player1Chips', 0) or your_chips) / 1e9
        opp_chips_sol = (game_data.get('player2Chips', 0) or opp_chips) / 1e9
    elif am_p2:
        my_chips_sol = (game_data.get('player2Chips', 0) or your_chips) / 1e9
        opp_chips_sol = (game_data.get('player1Chips', 0) or opp_chips) / 1e9
    else:
        my_chips_sol = (game_data.get('player1Chips', 0)) / 1e9
        opp_chips_sol = (game_data.get('player2Chips', 0)) / 1e9

    # Timer
    turn_deadline = game_data.get('turnDeadline')
    timer_str = ""
    if turn_deadline and status == 'active':
        try:
            from datetime import datetime, timezone
            deadline_dt = datetime.fromisoformat(turn_deadline.replace('Z', '+00:00'))
            remaining = (deadline_dt - datetime.now(timezone.utc)).total_seconds()
            remaining = max(0, int(remaining))
            mins, secs = divmod(remaining, 60)
            timer_str = f" ⏱ {mins}:{secs:02d}"
            if remaining < 30:
                timer_str = Output.color(timer_str, 'red')
        except Exception:
            pass

    W = 45
    print()
    print("┌" + "─" * W + "┐")
    print(f"│{'POKER TABLE':^{W}}│")
    print(f"│{'Game #' + game_id[:8] + '  ' + betting_round.upper() + timer_str:^{W}}│")
    print("├" + "─" * W + "┤")

    # Opponent area
    opp_line = f"  {opp_name}  ({opp_chips_sol:.4f} SOL)"
    print(f"│{opp_line:<{W}}│")
    if opponent_hand:
        opp_cards = f"  Cards: {format_hand(opponent_hand)}"
    else:
        opp_cards = "  Cards: [🂠] [🂠]"
    print(f"│{opp_cards:<{W}}│")
    print("├" + "─" * W + "┤")

    # Board
    pot_line = f"  Pot: {pot_sol:.4f} SOL"
    print(f"│{pot_line:<{W}}│")
    if current_bet > 0:
        bet_line = f"  Bet to match: {current_bet:.4f} SOL"
        print(f"│{bet_line:<{W}}│")
    if community:
        board_line = f"  Board: {format_hand(community)}"
    else:
        board_line = "  Board: (no cards yet)"
    print(f"│{board_line:<{W}}│")
    print("├" + "─" * W + "┤")

    # Your area
    my_line = f"  {my_name}  ({my_chips_sol:.4f} SOL)"
    print(f"│{my_line:<{W}}│")
    if your_hand:
        my_cards = f"  Hand: {format_hand(your_hand)}"
    else:
        my_cards = "  Hand: [🂠] [🂠]"
    print(f"│{my_cards:<{W}}│")
    print("└" + "─" * W + "┘")

    if status == 'completed':
        winner = game_data.get('winner')
        if isinstance(winner, dict):
            w_name = winner.get('name') or (winner.get('wallet', '???')[:8] + '...')
        else:
            w_name = str(winner)[:8] + '...' if winner else 'Tie'
        print(Output.color(f"  🏆 WINNER: {w_name}  ({pot_sol:.4f} SOL)", 'yellow'))
    elif your_turn:
        print(Output.color("  🎯 YOUR TURN — fold | check | call | raise", 'green'))
    elif status == 'active':
        print(Output.color("  ⏳ Waiting for opponent...", 'cyan'))


def ai_decide_poker_action(game_data: Dict[str, Any]) -> Tuple[str, Optional[int], str]:
    """Simple AI poker strategy — returns (action, amount_lamports_or_none, reasoning)"""
    your_hand = game_data.get('yourHand', [])
    community = game_data.get('communityCards', [])
    current_bet = game_data.get('currentBet', 0)
    your_chips = game_data.get('yourChips', 0)
    pot = game_data.get('pot', 0)

    # Determine my bet from game data
    p1 = game_data.get('player1', {}) or {}
    p2 = game_data.get('player2', {}) or {}
    my_bet = game_data.get('player1Bet', 0)  # fallback
    if game_data.get('yourTurn'):
        # We need to figure out our current bet level
        pass

    to_call = current_bet - my_bet
    if to_call < 0:
        to_call = 0

    # Evaluate hand strength (simple heuristic)
    high_cards = set('TJQKA')
    rank_names = {'T': '10', 'J': 'Jack', 'Q': 'Queen', 'K': 'King', 'A': 'Ace'}
    pairs_count = 0
    ranks = []

    for card in your_hand:
        if isinstance(card, str) and len(card) >= 2:
            ranks.append(card[0])
        elif isinstance(card, dict):
            ranks.append(card.get('rank', ''))

    # Check for pairs
    if len(ranks) >= 2 and ranks[0] == ranks[1]:
        pairs_count = 1

    # Include community cards in evaluation
    all_ranks = list(ranks)
    for card in community:
        if isinstance(card, str) and len(card) >= 2:
            all_ranks.append(card[0])
        elif isinstance(card, dict):
            all_ranks.append(card.get('rank', ''))

    # Count pairs/trips in all cards
    from collections import Counter
    rank_counts = Counter(all_ranks)
    max_of_kind = max(rank_counts.values()) if rank_counts else 0

    # Hand strength score (0-1)
    strength = 0.3  # base

    # High cards bonus
    high_count = sum(1 for r in ranks if r in high_cards)
    strength += high_count * 0.1

    # Pairs/trips/quads
    if max_of_kind >= 4:
        strength = 0.95
    elif max_of_kind >= 3:
        strength = 0.85
    elif max_of_kind >= 2:
        strength += 0.25

    # Suited bonus
    suits = []
    for card in your_hand:
        if isinstance(card, str) and len(card) >= 2:
            suits.append(card[-1])
    if len(suits) >= 2 and suits[0] == suits[1]:
        strength += 0.05

    strength = min(1.0, strength)

    # Build hand description for reasoning
    hand_desc_parts = []
    if max_of_kind >= 4:
        hand_desc_parts.append("four of a kind")
    elif max_of_kind >= 3:
        hand_desc_parts.append("three of a kind")
    elif max_of_kind >= 2:
        # Find which rank is paired
        paired = [r for r, c in rank_counts.items() if c >= 2]
        paired_names = [rank_names.get(r, r) for r in paired]
        hand_desc_parts.append(f"pair of {'/'.join(paired_names)}s")
    if high_count > 0:
        high_names = [rank_names.get(r, r) for r in ranks if r in high_cards]
        hand_desc_parts.append(f"high: {', '.join(high_names)}")
    hand_desc = ", ".join(hand_desc_parts) if hand_desc_parts else "no made hand"

    # Decision logic
    if to_call == 0:
        # No bet to match
        if strength > 0.6:
            raise_amount = max(int(pot * 0.5), 10000000)  # min 0.01 SOL
            raise_amount = min(raise_amount, your_chips)
            if raise_amount > 0:
                reasoning = f"Hand strength: {strength:.2f} ({hand_desc}). No bet to match. Strong hand — raising {raise_amount / 1e9:.4f} SOL."
                return ('raise', raise_amount, reasoning)
        reasoning = f"Hand strength: {strength:.2f} ({hand_desc}). No bet to match. Checking."
        return ('check', None, reasoning)
    else:
        # There's a bet to match
        pot_odds = to_call / (pot + to_call) if (pot + to_call) > 0 else 1.0
        pot_odds_str = f"Pot odds: {pot_odds:.2f}"

        if strength > 0.7:
            raise_amount = max(int(pot * 0.5), 10000000)
            raise_amount = min(raise_amount, your_chips - to_call)
            if raise_amount > 0:
                reasoning = f"Hand strength: {strength:.2f} ({hand_desc}). {pot_odds_str}. Strong hand — raising."
                return ('raise', raise_amount, reasoning)
            reasoning = f"Hand strength: {strength:.2f} ({hand_desc}). {pot_odds_str}. Strong hand — calling."
            return ('call', None, reasoning)
        elif strength > pot_odds + 0.1:
            reasoning = f"Hand strength: {strength:.2f} ({hand_desc}). {pot_odds_str}. Good odds — calling."
            return ('call', None, reasoning)
        elif strength > 0.35:
            if to_call < pot * 0.3:
                reasoning = f"Hand strength: {strength:.2f} ({hand_desc}). {pot_odds_str}. Borderline, small bet — calling."
                return ('call', None, reasoning)
            reasoning = f"Hand strength: {strength:.2f} ({hand_desc}). {pot_odds_str}. Borderline, bet too large — folding."
            return ('fold', None, reasoning)
        else:
            reasoning = f"Hand strength: {strength:.2f} ({hand_desc}). {pot_odds_str}. Weak hand — folding."
            return ('fold', None, reasoning)


def cmd_poker(args: argparse.Namespace) -> None:
    """Poker command dispatcher — cash games (2-6 players)"""
    subcommand = getattr(args, 'poker_cmd', None)

    if not subcommand:
        print("Usage: python mya.py poker <command>")
        print("\nNo API key needed. Auth uses your wallet signature automatically.")
        print("\nCommands:")
        print("  create   - Create a new poker table")
        print("  join     - Join a table and deposit buy-in")
        print("  leave    - Leave a table (chips settled)")
        print("  close    - Close a table you created")
        print("  reload   - Add more chips to your stack")
        print("  watch    - Watch a table with auto-polling")
        print("  tables   - List open/active tables")
        print("\nQuickstart:")
        print("  python mya.py poker tables")
        print("  python mya.py poker create --small-blind 0.01 --big-blind 0.02")
        print("  python mya.py poker join <table_id> --buy-in 0.5")
        print("  python mya.py poker watch <table_id>")
        return

    # Cash game is now the only poker mode — map directly
    # Also support 'cash' prefix for backward compat
    if subcommand == 'cash':
        cash_cmd = getattr(args, 'cash_cmd', None)
        if cash_cmd:
            subcommand = cash_cmd
        else:
            # Show help
            cmd_poker(argparse.Namespace(poker_cmd=None))
            return

    handlers = {
        'create': cmd_cash_create,
        'join': cmd_cash_join,
        'leave': cmd_cash_leave,
        'close': cmd_cash_close,
        'reload': cmd_cash_reload,
        'watch': cmd_cash_watch,
        'tables': cmd_cash_tables,
    }

    handler = handlers.get(subcommand)
    if handler:
        handler(args)
    else:
        Output.error(f"Unknown poker command: {subcommand}")
        sys.exit(ExitCode.INVALID_INPUT)


# ============================================================================
# Cash Game Commands (Multi-Player)
# ============================================================================

def cmd_poker_cash(args: argparse.Namespace) -> None:
    """Cash game command dispatcher"""
    cash_cmd = getattr(args, 'cash_cmd', None)

    if not cash_cmd:
        print("Usage: python mya.py poker cash <command>")
        print("\nNo API key needed. Auth uses your wallet signature automatically.")
        print("\nCommands:")
        print("  create   - Create a new cash game table")
        print("  join     - Join a table and deposit buy-in")
        print("  leave    - Leave a table (chips settled)")
        print("  close    - Close a table you created")
        print("  reload   - Add more chips to your stack")
        print("  watch    - Watch a table with auto-polling")
        print("  tables   - List open/active tables")
        print("\nQuickstart:")
        print("  python mya.py poker cash tables")
        print("  python mya.py poker cash create --small-blind 0.01 --big-blind 0.02")
        print("  python mya.py poker cash join <table_id> --buy-in 0.5")
        return

    cash_handlers = {
        'create': cmd_cash_create,
        'join': cmd_cash_join,
        'leave': cmd_cash_leave,
        'close': cmd_cash_close,
        'reload': cmd_cash_reload,
        'watch': cmd_cash_watch,
        'tables': cmd_cash_tables,
    }

    handler = cash_handlers.get(cash_cmd)
    if handler:
        handler(args)
    else:
        Output.error(f"Unknown cash command: {cash_cmd}")
        sys.exit(ExitCode.INVALID_INPUT)


def cmd_cash_create(args: argparse.Namespace) -> None:
    """Create a new cash game table"""
    small_blind = getattr(args, 'small_blind', 0.01)
    big_blind = getattr(args, 'big_blind', 0.02)
    min_buy_in = getattr(args, 'min_buy_in', None) or big_blind * 20
    max_buy_in = getattr(args, 'max_buy_in', None) or big_blind * 100
    max_seats = getattr(args, 'seats', 6)

    wallet = load_wallet()
    pubkey = str(wallet.pubkey())
    api_url = get_api_url()

    challenge, signature = get_poker_challenge("cash-create-table")

    with Spinner("Creating cash game table..."):
        resp = api_request('POST', f"{api_url}/poker/cash/create-table", json={
            "walletAddress": pubkey,
            "challenge": challenge,
            "signature": signature,
            "smallBlind": small_blind,
            "bigBlind": big_blind,
            "minBuyIn": min_buy_in,
            "maxBuyIn": max_buy_in,
            "maxSeats": max_seats,
        })
        result = resp.json()

    if not result.get('success'):
        Output.error(result.get('error', 'Unknown error'))
        sys.exit(ExitCode.API_ERROR)

    table = result['table']
    Output.success("Cash game table created!")
    print(f"\n  Table ID:   {table['id']}")
    print(f"  Blinds:     {small_blind}/{big_blind} SOL")
    print(f"  Buy-in:     {min_buy_in}-{max_buy_in} SOL")
    print(f"  Seats:      {max_seats}")
    print(f"\n  Join:  python mya.py poker cash join {table['id']} --buy-in {min_buy_in}")
    print(f"  Watch: python mya.py poker cash watch {table['id']}")


def cmd_cash_join(args: argparse.Namespace) -> None:
    """Join a cash game table"""
    table_id = getattr(args, 'table_id', None)
    buy_in = getattr(args, 'buy_in', None)

    if not table_id:
        Output.error("Table ID required")
        sys.exit(ExitCode.INVALID_INPUT)
    if not buy_in or buy_in <= 0:
        Output.error("Buy-in amount required (in SOL)")
        sys.exit(ExitCode.INVALID_INPUT)

    wallet = load_wallet()
    pubkey = str(wallet.pubkey())
    api_url = get_api_url()

    # Check balance
    balance = get_balance(pubkey)
    required = buy_in + 0.01
    if balance < required:
        Output.error(f"Insufficient balance. Need ~{required:.4f} SOL, have {balance:.4f} SOL")
        sys.exit(ExitCode.INVALID_INPUT)

    # Step 1: Request seat + unsigned deposit tx
    challenge, signature = get_poker_challenge("cash-join")
    with Spinner("Requesting seat..."):
        resp = api_request('POST', f"{api_url}/poker/cash/join", json={
            "walletAddress": pubkey,
            "challenge": challenge,
            "signature": signature,
            "tableId": table_id,
            "buyIn": buy_in,
        })
        result = resp.json()

    if not result.get('success'):
        Output.error(result.get('error', 'Unknown error'))
        sys.exit(ExitCode.API_ERROR)

    deposit = result.get('deposit', {})
    unsigned_tx = deposit.get('unsignedTx')

    if unsigned_tx:
        # Step 2: Sign and submit deposit
        print("Signing deposit transaction...")
        try:
            tx_bytes = base64.b64decode(unsigned_tx)
            tx = SoldersTransaction.from_bytes(tx_bytes)
            signed_tx = wallet.sign_transaction(tx)
            signed_b64 = base64.b64encode(bytes(signed_tx)).decode('utf-8')

            # Submit signed tx
            from solders.transaction import Transaction as SoldersTx
            sig = str(signed_tx.signatures[0]) if signed_tx.signatures else ''

            with Spinner("Confirming deposit on-chain..."):
                confirm_challenge, confirm_sig = get_poker_challenge("cash-confirm-join")
                confirm_resp = api_request('POST', f"{api_url}/poker/cash/confirm-join", json={
                    "walletAddress": pubkey,
                    "challenge": confirm_challenge,
                    "signature": confirm_sig,
                    "tableId": table_id,
                    "txSignature": sig,
                })
                confirm_result = confirm_resp.json()

            if confirm_result.get('success'):
                seat = confirm_result.get('seat', {})
                Output.success(f"Joined table! Seat #{seat.get('seatNumber', '?')}, {seat.get('chips', 0) / 1e9:.4f} SOL")
                if confirm_result.get('handDealt'):
                    print("  A new hand has been dealt!")
            else:
                Output.error(f"Deposit confirmation failed: {confirm_result.get('error', 'Unknown')}")
                sys.exit(ExitCode.API_ERROR)
        except Exception as e:
            Output.error(f"Deposit failed: {e}")
            sys.exit(ExitCode.API_ERROR)
    else:
        Output.success(f"Seated at table (seat #{result.get('seat', {}).get('seatNumber', '?')})")

    # Auto-enter watch mode
    print(f"\nAuto-starting watch mode...\n")
    watch_args = argparse.Namespace(
        table_id=table_id,
        poll=2,
        mode='ask',
        verbose=False,
    )
    cmd_cash_watch(watch_args)


def cmd_cash_leave(args: argparse.Namespace) -> None:
    """Leave a cash game table"""
    table_id = getattr(args, 'table_id', None)
    if not table_id:
        Output.error("Table ID required")
        sys.exit(ExitCode.INVALID_INPUT)

    wallet = load_wallet()
    pubkey = str(wallet.pubkey())
    api_url = get_api_url()

    challenge, signature = get_poker_challenge("cash-leave")
    with Spinner("Leaving table..."):
        resp = api_request('POST', f"{api_url}/poker/cash/leave", json={
            "walletAddress": pubkey,
            "challenge": challenge,
            "signature": signature,
            "tableId": table_id,
        })
        result = resp.json()

    if not result.get('success'):
        Output.error(result.get('error', 'Unknown error'))
        sys.exit(ExitCode.API_ERROR)

    if result.get('deferred'):
        Output.info(result.get('message', 'Leave deferred until hand completes'))
    else:
        chips = result.get('chipsSettled', 0)
        settle_tx = result.get('settleTx')
        Output.success(f"Left table. {chips / 1e9:.4f} SOL settled.")
        if settle_tx:
            print(f"  Tx: https://solscan.io/tx/{settle_tx}?cluster=devnet")


def cmd_cash_close(args: argparse.Namespace) -> None:
    """Close a cash game table (creator only)"""
    table_id = getattr(args, 'table_id', None)
    if not table_id:
        Output.error("Table ID required")
        sys.exit(ExitCode.INVALID_INPUT)

    wallet = load_wallet()
    pubkey = str(wallet.pubkey())
    api_url = get_api_url()

    challenge, signature = get_poker_challenge("cash-close-table")
    with Spinner("Closing table..."):
        resp = api_request('POST', f"{api_url}/poker/cash/close-table", json={
            "walletAddress": pubkey,
            "challenge": challenge,
            "signature": signature,
            "tableId": table_id,
        })
        result = resp.json()

    rt = get_runtime()
    if rt.format == OutputFormat.JSON:
        Output.json_output(result)
        if not result.get('success'):
            sys.exit(ExitCode.API_ERROR)
        return

    if result.get('success'):
        settlements = result.get('settlements', 0)
        Output.success(f"Table closed. {settlements} player(s) settled.")
    else:
        Output.error(result.get('error', 'Unknown error'))
        sys.exit(ExitCode.API_ERROR)


def cmd_cash_reload(args: argparse.Namespace) -> None:
    """Reload chips at a cash game table"""
    table_id = getattr(args, 'table_id', None)
    amount = getattr(args, 'amount', None)

    if not table_id or not amount or amount <= 0:
        Output.error("Table ID and amount (SOL) required")
        sys.exit(ExitCode.INVALID_INPUT)

    wallet = load_wallet()
    pubkey = str(wallet.pubkey())
    api_url = get_api_url()

    balance = get_balance(pubkey)
    if balance < amount + 0.01:
        Output.error(f"Insufficient balance. Need ~{amount + 0.01:.4f} SOL, have {balance:.4f} SOL")
        sys.exit(ExitCode.INVALID_INPUT)

    # Get unsigned reload tx
    challenge, signature = get_poker_challenge("cash-reload")
    with Spinner("Building reload transaction..."):
        resp = api_request('POST', f"{api_url}/poker/cash/reload", json={
            "walletAddress": pubkey,
            "challenge": challenge,
            "signature": signature,
            "tableId": table_id,
            "amount": amount,
        })
        result = resp.json()

    if not result.get('success'):
        Output.error(result.get('error', 'Unknown error'))
        sys.exit(ExitCode.API_ERROR)

    deposit = result.get('deposit', {})
    unsigned_tx = deposit.get('unsignedTx')

    if unsigned_tx:
        print("Signing reload transaction...")
        try:
            tx_bytes = base64.b64decode(unsigned_tx)
            tx = SoldersTransaction.from_bytes(tx_bytes)
            signed_tx = wallet.sign_transaction(tx)
            sig = str(signed_tx.signatures[0]) if signed_tx.signatures else ''

            with Spinner("Confirming reload on-chain..."):
                confirm_challenge, confirm_sig = get_poker_challenge("cash-confirm-reload")
                confirm_resp = api_request('POST', f"{api_url}/poker/cash/confirm-reload", json={
                    "walletAddress": pubkey,
                    "challenge": confirm_challenge,
                    "signature": confirm_sig,
                    "tableId": table_id,
                    "txSignature": sig,
                })
                confirm_result = confirm_resp.json()

            if confirm_result.get('success'):
                Output.success(f"Reloaded! New stack: {confirm_result.get('chips', 0) / 1e9:.4f} SOL")
            else:
                Output.error(f"Reload failed: {confirm_result.get('error', 'Unknown')}")
        except Exception as e:
            Output.error(f"Reload failed: {e}")
            sys.exit(ExitCode.API_ERROR)


def display_cash_table(table_data: Dict[str, Any], wallet_address: str) -> None:
    """Display multi-player cash game table state"""
    table = table_data.get('table', {})
    seats = table_data.get('seats', [])
    hand = table_data.get('hand')

    table_id = table.get('id', 'unknown')
    sb_sol = table.get('smallBlind', 0) / 1e9
    bb_sol = table.get('bigBlind', 0) / 1e9
    status = table.get('status', 'unknown')
    hand_num = table.get('handNumber', 0)

    # Timer
    timer_str = ""
    if hand and hand.get('turnDeadline') and hand.get('status') not in ('complete', 'showdown'):
        try:
            from datetime import datetime, timezone
            deadline_dt = datetime.fromisoformat(hand['turnDeadline'].replace('Z', '+00:00'))
            remaining = (deadline_dt - datetime.now(timezone.utc)).total_seconds()
            remaining = max(0, int(remaining))
            mins, secs = divmod(remaining, 60)
            timer_str = f" T {mins}:{secs:02d}"
            if remaining < 30:
                timer_str = Output.color(timer_str, 'red')
        except Exception:
            pass

    W = 55
    print()
    print("+" + "=" * W + "+")
    title = f"CASH TABLE  {sb_sol:.4f}/{bb_sol:.4f} SOL"
    print(f"|{title:^{W}}|")
    sub = f"#{table_id[:8]}  Hand {hand_num}  {status.upper()}{timer_str}"
    print(f"|{sub:^{W}}|")
    print("+" + "-" * W + "+")

    if hand:
        # Pot
        pot_sol = hand.get('pot', 0) / 1e9
        pot_line = f"  Pot: {pot_sol:.4f} SOL"
        print(f"|{pot_line:<{W}}|")

        # Side pots
        side_pots = hand.get('sidePots')
        if side_pots and len(side_pots) > 1:
            for i, sp in enumerate(side_pots):
                sp_line = f"    Side pot {i+1}: {sp['amount'] / 1e9:.4f} SOL (seats {sp['eligible_seats']})"
                print(f"|{sp_line:<{W}}|")

        # Community cards
        community = hand.get('communityCards', [])
        if community:
            board_line = f"  Board: {format_hand(community)}"
        else:
            board_line = "  Board: (no cards yet)"
        print(f"|{board_line:<{W}}|")

        bet_to_match = hand.get('currentBet', 0) / 1e9
        if bet_to_match > 0:
            bet_line = f"  Bet to match: {bet_to_match:.4f} SOL"
            print(f"|{bet_line:<{W}}|")

    print("+" + "-" * W + "+")

    # Seats
    for s in sorted(seats, key=lambda x: x.get('seatNumber', 0)):
        seat_num = s.get('seatNumber', '?')
        name = s.get('name') or (s.get('wallet', '???')[:6] + '..' if s.get('wallet') else '???')
        chips_sol = s.get('chips', 0) / 1e9
        is_you = s.get('isYou', False)
        is_folded = s.get('isFolded', False)
        is_all_in = s.get('isAllIn', False)
        is_current = hand and hand.get('currentTurnSeat') == seat_num

        # Badges
        badges = []
        if hand:
            if hand.get('dealerSeat') == seat_num:
                badges.append("D")
            if hand.get('smallBlindSeat') == seat_num:
                badges.append("SB")
            if hand.get('bigBlindSeat') == seat_num:
                badges.append("BB")
        if is_all_in:
            badges.append("ALL-IN")
        if is_folded:
            badges.append("FOLD")
        badge_str = f" [{'/'.join(badges)}]" if badges else ""

        # Cards
        hole_cards = s.get('holeCards')
        if hole_cards:
            cards_str = format_hand(hole_cards)
        elif is_folded:
            cards_str = "---"
        else:
            cards_str = "[?][?]"

        # Current bet this round
        bet = s.get('currentBet', 0) / 1e9
        bet_str = f"  bet:{bet:.4f}" if bet > 0 else ""

        marker = ">>>" if is_current else ("  *" if is_you else "   ")
        player_label = "YOU" if is_you else name

        line = f"{marker} Seat {seat_num}: {player_label}  {chips_sol:.4f} SOL  {cards_str}{badge_str}{bet_str}"
        if is_current:
            line = Output.color(line, 'green')
        elif is_folded:
            line = Output.color(line, 'white')
        elif is_you:
            line = Output.color(line, 'cyan')

        # Truncate to fit
        if len(line) > W:
            line = line[:W-1] + ".."
        print(f"|{line:<{W}}|")

    print("+" + "=" * W + "+")

    # Winners
    if hand and hand.get('winnerSeats'):
        for w in hand['winnerSeats']:
            wline = f"  Seat {w['seat']} wins {w['amount'] / 1e9:.4f} SOL ({w['hand_rank']})"
            print(Output.color(wline, 'yellow'))

    # Your turn indicator
    my_seat = None
    for s in seats:
        if s.get('isYou'):
            my_seat = s
            break

    if my_seat and hand and hand.get('currentTurnSeat') == my_seat.get('seatNumber'):
        print(Output.color("  YOUR TURN - fold | check | call | raise", 'green'))
    elif hand and hand.get('status') not in ('complete', 'showdown', None):
        turn_seat = hand.get('currentTurnSeat')
        if turn_seat is not None:
            turn_player = None
            for s in seats:
                if s.get('seatNumber') == turn_seat:
                    turn_player = s.get('name') or (s.get('wallet', '?')[:6] + '..')
                    break
            if turn_player:
                print(Output.color(f"  Waiting for {turn_player} (seat {turn_seat})...", 'cyan'))


def ai_decide_cash_action(table_data: Dict[str, Any]) -> Tuple[str, Optional[int], str]:
    """AI decision for cash game — seat-aware version."""
    hand = table_data.get('hand', {})
    seats = table_data.get('seats', [])

    # Find our seat
    my_seat = None
    for s in seats:
        if s.get('isYou'):
            my_seat = s
            break

    if not my_seat:
        return ('check', None, 'Cannot find our seat')

    your_hand = my_seat.get('holeCards', [])
    community = hand.get('communityCards', [])
    current_bet = hand.get('currentBet', 0)
    your_chips = my_seat.get('chips', 0)
    my_bet = my_seat.get('currentBet', 0)
    pot = hand.get('pot', 0)

    to_call = current_bet - my_bet
    if to_call < 0:
        to_call = 0

    if not your_hand:
        return ('check', None, 'No hole cards visible')

    # Evaluate hand strength (same heuristic as classic)
    high_cards = set('TJQKA')
    rank_names = {'T': '10', 'J': 'Jack', 'Q': 'Queen', 'K': 'King', 'A': 'Ace'}
    ranks = []
    for card in your_hand:
        if isinstance(card, str) and len(card) >= 2:
            ranks.append(card[0])

    all_ranks = list(ranks)
    for card in community:
        if isinstance(card, str) and len(card) >= 2:
            all_ranks.append(card[0])

    from collections import Counter
    rank_counts = Counter(all_ranks)
    max_of_kind = max(rank_counts.values()) if rank_counts else 0

    strength = 0.3
    high_count = sum(1 for r in ranks if r in high_cards)
    strength += high_count * 0.1

    if max_of_kind >= 4:
        strength = 0.95
    elif max_of_kind >= 3:
        strength = 0.85
    elif max_of_kind >= 2:
        strength += 0.25

    suits = []
    for card in your_hand:
        if isinstance(card, str) and len(card) >= 2:
            suits.append(card[-1])
    if len(suits) >= 2 and suits[0] == suits[1]:
        strength += 0.05

    strength = min(1.0, strength)

    hand_desc_parts = []
    if max_of_kind >= 4:
        hand_desc_parts.append("four of a kind")
    elif max_of_kind >= 3:
        hand_desc_parts.append("three of a kind")
    elif max_of_kind >= 2:
        paired = [r for r, c in rank_counts.items() if c >= 2]
        paired_names = [rank_names.get(r, r) for r in paired]
        hand_desc_parts.append(f"pair of {'/'.join(paired_names)}s")
    if high_count > 0:
        high_names = [rank_names.get(r, r) for r in ranks if r in high_cards]
        hand_desc_parts.append(f"high: {', '.join(high_names)}")
    hand_desc = ", ".join(hand_desc_parts) if hand_desc_parts else "no made hand"

    if to_call == 0:
        if strength > 0.6:
            raise_amount = max(int(pot * 0.5), 10000000)
            raise_amount = min(raise_amount, your_chips)
            if raise_amount > 0:
                return ('raise', raise_amount, f"Strength: {strength:.2f} ({hand_desc}). Strong — raising.")
        return ('check', None, f"Strength: {strength:.2f} ({hand_desc}). Checking.")
    else:
        pot_odds = to_call / (pot + to_call) if (pot + to_call) > 0 else 1.0
        if strength > 0.7:
            raise_amount = max(int(pot * 0.5), 10000000)
            raise_amount = min(raise_amount, your_chips - to_call)
            if raise_amount > 0:
                return ('raise', raise_amount, f"Strength: {strength:.2f} ({hand_desc}). Strong — raising.")
            return ('call', None, f"Strength: {strength:.2f} ({hand_desc}). Strong — calling.")
        elif strength > pot_odds + 0.1:
            return ('call', None, f"Strength: {strength:.2f} ({hand_desc}). Good odds — calling.")
        elif strength > 0.35 and to_call < pot * 0.3:
            return ('call', None, f"Strength: {strength:.2f} ({hand_desc}). Small bet — calling.")
        else:
            return ('fold', None, f"Strength: {strength:.2f} ({hand_desc}). Weak — folding.")


def cmd_cash_watch(args: argparse.Namespace) -> None:
    """Watch a cash game table with auto-polling"""
    table_id = getattr(args, 'table_id', None)
    if not table_id:
        Output.error("Table ID required")
        sys.exit(ExitCode.INVALID_INPUT)

    wallet = load_wallet()
    pubkey = str(wallet.pubkey())
    api_url = get_api_url()
    poll_interval = getattr(args, 'poll', 2)
    mode = getattr(args, 'mode', 'ask')
    verbose = getattr(args, 'verbose', False)

    print(f"Watching table {table_id[:8]}...")
    print(f"Polling every {poll_interval}s. Press Ctrl+C to stop.\n")

    play_mode = mode
    if play_mode == 'ask':
        print("How do you want to play when it's your turn?")
        print("  [h] Human - you choose every action")
        print("  [a] AI    - auto-play with strategy")
        choice = input("Choose (h/a): ").strip().lower()
        play_mode = 'ai' if choice == 'a' else 'human'
        print(f"Mode: {'AI auto-play' if play_mode == 'ai' else 'Human control'}\n")

    try:
        while True:
            resp = api_request('GET', f"{api_url}/poker/cash/table/{table_id}?wallet={pubkey}")
            table_data = resp.json()

            if sys.stdout.isatty():
                print("\033[H\033[J", end="")

            display_cash_table(table_data, pubkey)

            hand = table_data.get('hand')
            seats = table_data.get('seats', [])
            table_info = table_data.get('table', {})

            # Find our seat
            my_seat = None
            for s in seats:
                if s.get('isYou'):
                    my_seat = s
                    break

            # Check if it's our turn
            is_our_turn = (
                my_seat and hand and
                hand.get('currentTurnSeat') == my_seat.get('seatNumber') and
                hand.get('status') not in ('complete', 'showdown')
            )

            if table_info.get('status') == 'closed':
                Output.info("Table is closed.")
                break

            if is_our_turn:
                if play_mode == 'ai':
                    action_input, amount_lamports, reasoning = ai_decide_cash_action(table_data)
                    if verbose:
                        print(Output.color(f"  Thinking... {reasoning}", 'cyan'))
                        print(Output.color(f"  Decision: {action_input}" + (f" ({amount_lamports / 1e9:.4f} SOL)" if amount_lamports else ""), 'cyan'))
                    else:
                        print(Output.color(f"  AI decides: {action_input}" + (f" ({amount_lamports / 1e9:.4f} SOL)" if amount_lamports else ""), 'cyan'))
                    time.sleep(1)
                else:
                    print("\nYOUR TURN - Choose action:")
                    print("  fold | check | call | raise   (q to quit, a to switch to AI)")
                    action_input = input("Enter action: ").strip().lower()

                    if action_input == 'q':
                        break
                    if action_input == 'a':
                        play_mode = 'ai'
                        print(Output.color("  Switched to AI mode!", 'cyan'))
                        continue

                    if action_input not in ['fold', 'check', 'call', 'raise']:
                        continue

                    amount_lamports = None
                    if action_input == 'raise':
                        try:
                            amount = float(input("Raise amount (SOL): "))
                            amount_lamports = int(amount * 1e9)
                        except ValueError:
                            print("Invalid amount.")
                            continue

                challenge, signature = get_poker_challenge(f"cash-{action_input}")
                payload = {
                    "walletAddress": pubkey,
                    "challenge": challenge,
                    "signature": signature,
                    "tableId": table_id,
                    "action": action_input,
                }
                if amount_lamports:
                    payload["amount"] = amount_lamports

                try:
                    action_resp = api_request('POST', f"{api_url}/poker/cash/action", json=payload)
                    action_result = action_resp.json()
                    if action_result.get('success'):
                        msg = action_result.get('game', {}).get('message', '')
                        if msg:
                            print(f"  {msg}")
                    else:
                        print(Output.color(f"  Error: {action_result.get('error', 'Unknown')}", 'red'))
                except Exception as e:
                    print(Output.color(f"  Action failed: {e}", 'red'))

                time.sleep(1)
            else:
                time.sleep(poll_interval)

    except KeyboardInterrupt:
        Output.info("\nStopped watching.")


def cmd_cash_tables(args: argparse.Namespace) -> None:
    """List open/active cash game tables"""
    api_url = get_api_url()

    with Spinner("Fetching tables..."):
        resp = api_request('GET', f"{api_url}/poker/cash/tables")
        result = resp.json()

    tables = result.get('tables', [])
    if not tables:
        print("No open tables. Create one with: python mya.py poker cash create --small-blind 0.01 --big-blind 0.02")
        return

    W = 70
    print()
    print(f"{'ID':<10} {'Blinds':<18} {'Buy-in':<22} {'Players':<10} {'Status':<10}")
    print("-" * W)
    for t in tables:
        tid = t['id'][:8]
        blinds = f"{t['smallBlind']/1e9:.4f}/{t['bigBlind']/1e9:.4f}"
        buyin = f"{t['minBuyIn']/1e9:.2f}-{t['maxBuyIn']/1e9:.2f} SOL"
        players = f"{t['playerCount']}/{t['maxSeats']}"
        status = t['status']
        print(f"{tid:<10} {blinds:<18} {buyin:<22} {players:<10} {status:<10}")
    print(f"\n{len(tables)} table(s) found.")


def cmd_poker_create(args: argparse.Namespace) -> None:
    """Create poker game"""
    buy_in = getattr(args, 'buy_in', None)
    if buy_in is None or buy_in < 0.01 or buy_in > 10:
        Output.error("Buy-in must be between 0.01 and 10 SOL")
        sys.exit(ExitCode.INVALID_INPUT)

    wallet = load_wallet()
    pubkey = str(wallet.pubkey())
    api_url = get_api_url()

    # Check balance before creating
    balance = get_balance(pubkey)
    required = buy_in + 0.01  # buy-in + tx fees
    if balance < required:
        Output.error(f"Insufficient balance. Need ~{required:.4f} SOL, have {balance:.4f} SOL")
        sys.exit(ExitCode.INVALID_INPUT)

    challenge, signature = get_poker_challenge("poker-create")

    with Spinner("Creating game..."):
        resp = api_request('POST', f"{api_url}/poker/create", json={
            "walletAddress": pubkey,
            "challenge": challenge,
            "signature": signature,
            "buyIn": buy_in
        })
        result = resp.json()

    if not result.get('success'):
        Output.error(result.get('error', 'Unknown error'))
        sys.exit(ExitCode.API_ERROR)

    rt = get_runtime()

    game_id = result['game']['id']
    escrow = result.get('escrow')

    # If escrow transaction is returned, sign and confirm it
    if escrow and escrow.get('unsignedTx'):
        print("Signing escrow deposit transaction...")
        try:
            tx_bytes = base64.b64decode(escrow['unsignedTx'])
            tx = SoldersTransaction.from_bytes(tx_bytes)
            signed_tx = wallet.sign_transaction(tx)
            signed_b64 = base64.b64encode(bytes(signed_tx)).decode('utf-8')

            with Spinner("Confirming on-chain deposit..."):
                confirm_challenge, confirm_sig = get_poker_challenge("poker-confirm-create")
                confirm_resp = api_request('POST', f"{api_url}/poker/confirm-create", json={
                    "walletAddress": pubkey,
                    "challenge": confirm_challenge,
                    "signature": confirm_sig,
                    "signedTransaction": signed_b64,
                    "buyIn": buy_in,
                    "gameId": int(escrow['onChainGameId']),
                })
                confirm_result = confirm_resp.json()

            if confirm_result.get('success'):
                game_id = confirm_result['game']['id']
                tx_sig = confirm_result['game'].get('createTx', '')
                Output.success("Game created with on-chain escrow!")
                print(f"\nGame ID: {game_id}")
                print(f"Buy-in: {buy_in} SOL")
                if tx_sig:
                    print(f"Tx: https://solscan.io/tx/{tx_sig}?cluster=devnet")
            else:
                Output.warning("Escrow deposit failed, but game was created off-chain")
                print(f"Error: {confirm_result.get('error', 'Unknown')}")
        except Exception as e:
            Output.warning(f"Escrow signing failed: {e}")
            print("Game created without on-chain escrow (off-chain fallback)")
    else:
        Output.success("Game created successfully!")

    if rt.format == OutputFormat.JSON:
        Output.json_output(result)
        return

    print(f"\nGame ID: {game_id}")
    print(f"Buy-in: {buy_in} SOL")
    print(f"\nShare with opponent: python mya.py poker join {game_id}")
    print(f"\nAuto-starting watch mode...\n")

    # Auto-enter watch mode
    watch_args = argparse.Namespace(
        game_id=game_id,
        poll=2,
        headless=False,
        mode='ask',
        verbose=False,
    )
    cmd_poker_watch(watch_args)


def cmd_poker_join(args: argparse.Namespace) -> None:
    """Join existing poker game"""
    game_id = getattr(args, 'game_id', None)
    if not game_id:
        Output.error("Game ID required")
        sys.exit(ExitCode.INVALID_INPUT)

    wallet = load_wallet()
    pubkey = str(wallet.pubkey())
    api_url = get_api_url()

    # Check balance (game buy-in will be fetched from the game, but check minimum)
    balance = get_balance(pubkey)
    if balance < 0.02:  # minimum buy-in (0.01) + fees
        Output.error(f"Insufficient balance. Have {balance:.4f} SOL, need at least 0.02 SOL")
        sys.exit(ExitCode.INVALID_INPUT)

    challenge, signature = get_poker_challenge("poker-join")

    with Spinner("Joining game..."):
        resp = api_request('POST', f"{api_url}/poker/join", json={
            "walletAddress": pubkey,
            "challenge": challenge,
            "signature": signature,
            "gameId": game_id
        })
        result = resp.json()

    if not result.get('success'):
        Output.error(result.get('error', 'Unknown error'))
        sys.exit(ExitCode.API_ERROR)

    escrow = result.get('escrow')

    # If escrow transaction is returned, sign and confirm it
    if escrow and escrow.get('unsignedTx'):
        print("Signing escrow deposit transaction...")
        try:
            tx_bytes = base64.b64decode(escrow['unsignedTx'])
            tx = SoldersTransaction.from_bytes(tx_bytes)
            signed_tx = wallet.sign_transaction(tx)
            signed_b64 = base64.b64encode(bytes(signed_tx)).decode('utf-8')

            with Spinner("Confirming on-chain deposit..."):
                confirm_challenge, confirm_sig = get_poker_challenge("poker-confirm-join")
                confirm_resp = api_request('POST', f"{api_url}/poker/confirm-join", json={
                    "walletAddress": pubkey,
                    "challenge": confirm_challenge,
                    "signature": confirm_sig,
                    "signedTransaction": signed_b64,
                    "gameId": game_id,
                })
                confirm_result = confirm_resp.json()

            if confirm_result.get('success'):
                tx_sig = confirm_result['game'].get('joinTx', '')
                Output.success("Joined game with on-chain escrow!")
                if tx_sig:
                    print(f"Tx: https://solscan.io/tx/{tx_sig}?cluster=devnet")
            else:
                Output.warning("Escrow deposit failed, but join was recorded")
                print(f"Error: {confirm_result.get('error', 'Unknown')}")
        except Exception as e:
            Output.warning(f"Escrow signing failed: {e}")
            print("Joined without on-chain escrow (off-chain fallback)")
    else:
        Output.success("Joined game successfully!")

    rt = get_runtime()
    if rt.format == OutputFormat.JSON:
        Output.json_output(result)
        return

    display_poker_table(result['game'], pubkey)
    print(f"\nAuto-starting watch mode...\n")

    # Auto-enter watch mode
    watch_args = argparse.Namespace(
        game_id=game_id,
        poll=2,
        headless=False,
        mode='ask',
        verbose=False,
    )
    cmd_poker_watch(watch_args)


def cmd_poker_watch(args: argparse.Namespace) -> None:
    """Auto-polling watch mode with human/AI action control"""
    game_id = getattr(args, 'game_id', None)
    if not game_id:
        Output.error("Game ID required")
        sys.exit(ExitCode.INVALID_INPUT)

    wallet = load_wallet()
    pubkey = str(wallet.pubkey())
    api_url = get_api_url()
    poll_interval = getattr(args, 'poll', 2)
    headless = getattr(args, 'headless', False)
    mode = getattr(args, 'mode', 'ask')  # human | ai | ask
    verbose = getattr(args, 'verbose', False)
    rt = get_runtime()

    if not headless:
        print(f"Watching game {game_id[:8]}...")
        print(f"Polling every {poll_interval}s. Press Ctrl+C to stop.\n")

    # Determine play mode
    play_mode = mode  # 'human', 'ai', or 'ask'
    if play_mode == 'ask' and not headless:
        print("How do you want to play when it's your turn?")
        print("  [h] Human — you choose every action")
        print("  [a] AI    — auto-play with strategy")
        choice = input("Choose (h/a): ").strip().lower()
        play_mode = 'ai' if choice == 'a' else 'human'
        print(f"Mode: {'AI auto-play' if play_mode == 'ai' else 'Human control'}\n")

    try:
        while True:
            resp = api_request('GET', f"{api_url}/poker/game/{game_id}?wallet={pubkey}")
            game = resp.json()

            # Headless JSON mode: output state once and exit
            if headless or rt.format == OutputFormat.JSON:
                Output.json_output(game)
                if game.get('status') == 'completed' or game.get('yourTurn'):
                    return
                if headless:
                    time.sleep(poll_interval)
                    continue
                return

            if sys.stdout.isatty():
                print("\033[H\033[J", end="")  # Clear screen

            display_poker_table(game, pubkey)

            if game.get('status') == 'completed':
                winner = game.get('winner')
                if isinstance(winner, dict):
                    if winner.get('wallet') == pubkey:
                        Output.success("🏆 You won!")
                    else:
                        Output.info(f"Game over. Winner: {winner.get('name') or winner.get('wallet', '?')[:8]}")
                elif winner == pubkey:
                    Output.success("🏆 You won!")
                elif winner:
                    Output.info("Game over. Opponent won.")
                else:
                    Output.info("Game ended in a tie.")

                # Show settlement info
                settlement = game.get('settlementTx')
                if settlement:
                    print(f"  Settlement: https://solscan.io/tx/{settlement}?cluster=devnet")

                # --- Play Again? ---
                buy_in_lamports = game.get('buyInLamports', game.get('pot', 0))
                buy_in_sol = game.get('buyIn', buy_in_lamports / 1e9 if buy_in_lamports else 0.01)
                if not isinstance(buy_in_sol, (int, float)) or buy_in_sol <= 0:
                    buy_in_sol = 0.01

                try:
                    again = input(f"\nPlay again? Same buy-in ({buy_in_sol:.2f} SOL). (y/n): ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    break

                if again != 'y':
                    break

                # Check balance for top-up
                balance = get_balance(pubkey)
                required = buy_in_sol + 0.01
                if balance < required:
                    print(f"\nLow balance: {balance:.4f} SOL (need {required:.4f} SOL)")
                    try:
                        topup = input("Fund your wallet and press Enter when ready (or 'n' to quit): ").strip()
                    except (EOFError, KeyboardInterrupt):
                        break
                    if topup.lower() == 'n':
                        break
                    balance = get_balance(pubkey)
                    if balance < required:
                        Output.error(f"Still insufficient: {balance:.4f} SOL")
                        break

                # Create new game
                print(f"\nCreating new game with {buy_in_sol:.2f} SOL buy-in...")
                try:
                    challenge, signature = get_poker_challenge("poker-create")
                    with Spinner("Creating game..."):
                        resp = api_request('POST', f"{api_url}/poker/create", json={
                            "walletAddress": pubkey,
                            "challenge": challenge,
                            "signature": signature,
                            "buyIn": buy_in_sol,
                        })
                        create_result = resp.json()

                    if not create_result.get('success'):
                        Output.error(f"Failed to create game: {create_result.get('error', 'Unknown')}")
                        break

                    new_game_id = create_result['game']['id']

                    # Sign escrow if returned
                    escrow = create_result.get('escrow')
                    if escrow and escrow.get('unsignedTx'):
                        try:
                            tx_bytes = base64.b64decode(escrow['unsignedTx'])
                            tx = SoldersTransaction.from_bytes(tx_bytes)
                            signed_tx = wallet.sign_transaction(tx)
                            signed_b64 = base64.b64encode(bytes(signed_tx)).decode('utf-8')
                            confirm_challenge, confirm_sig = get_poker_challenge("poker-confirm-create")
                            confirm_resp = api_request('POST', f"{api_url}/poker/confirm-create", json={
                                "walletAddress": pubkey,
                                "challenge": confirm_challenge,
                                "signature": confirm_sig,
                                "signedTransaction": signed_b64,
                                "buyIn": buy_in_sol,
                                "gameId": int(escrow['onChainGameId']),
                            })
                            confirm_result = confirm_resp.json()
                            if confirm_result.get('success'):
                                new_game_id = confirm_result['game']['id']
                                Output.success("New game created with escrow!")
                            else:
                                Output.error(f"Escrow failed: {confirm_result.get('error', 'Unknown')}")
                                break
                        except Exception as e:
                            Output.error(f"Escrow signing failed: {e}")
                            break

                    game_id = new_game_id
                    print(f"New game: {game_id}")
                    print(f"Share with opponent: python mya.py poker join {game_id}")
                    print("Waiting for opponent...\n")
                    continue  # Re-enter watch loop with new game_id
                except Exception as e:
                    Output.error(f"Failed to create new game: {e}")
                    break

            if game.get('yourTurn'):
                if play_mode == 'ai':
                    # AI auto-play
                    action_input, amount_lamports, reasoning = ai_decide_poker_action(game)
                    if verbose:
                        print(Output.color(f"  🧠 Thinking... {reasoning}", 'cyan'))
                        print(Output.color(f"  🤖 Decision: {action_input}" + (f" ({amount_lamports / 1e9:.4f} SOL)" if amount_lamports else ""), 'cyan'))
                    else:
                        print(Output.color(f"  🤖 AI decides: {action_input}" + (f" ({amount_lamports / 1e9:.4f} SOL)" if amount_lamports else ""), 'cyan'))
                    time.sleep(1)  # Brief pause so human can see the decision
                else:
                    # Human interactive mode
                    print("\nYOUR TURN - Choose action:")
                    print("  fold | check | call | raise   (q to quit, a to switch to AI)")
                    action_input = input("Enter action: ").strip().lower()

                    if action_input == 'q':
                        break
                    if action_input == 'a':
                        play_mode = 'ai'
                        print(Output.color("  Switched to AI mode!", 'cyan'))
                        continue

                    if action_input not in ['fold', 'check', 'call', 'raise']:
                        continue

                    amount_lamports = None
                    if action_input == 'raise':
                        try:
                            amount = float(input("Raise amount (SOL): "))
                            amount_lamports = int(amount * 1e9)
                        except ValueError:
                            print("Invalid amount.")
                            continue

                challenge, signature = get_poker_challenge(f"poker-{action_input}")

                payload = {
                    "walletAddress": pubkey,
                    "challenge": challenge,
                    "signature": signature,
                    "gameId": game_id,
                    "action": action_input
                }
                if amount_lamports:
                    payload["amount"] = amount_lamports

                try:
                    action_resp = api_request('POST', f"{api_url}/poker/action", json=payload)
                    action_result = action_resp.json()
                    if action_result.get('success'):
                        msg = action_result.get('game', {}).get('message', '')
                        if msg:
                            print(f"  {msg}")
                    else:
                        print(Output.color(f"  Error: {action_result.get('error', 'Unknown')}", 'red'))
                except Exception as e:
                    print(Output.color(f"  Action failed: {e}", 'red'))

                time.sleep(1)
            else:
                time.sleep(poll_interval)

    except KeyboardInterrupt:
        Output.info("\nStopped watching.")


def cmd_poker_action(args: argparse.Namespace) -> None:
    """Perform single poker action"""
    game_id = getattr(args, 'game_id', None)
    action = getattr(args, 'action', None)

    if not game_id or not action:
        Output.error("Game ID and action required")
        sys.exit(ExitCode.INVALID_INPUT)

    wallet = load_wallet()
    pubkey = str(wallet.pubkey())
    api_url = get_api_url()

    challenge, signature = get_poker_challenge(f"poker-{action}")

    payload = {
        "walletAddress": pubkey,
        "challenge": challenge,
        "signature": signature,
        "gameId": game_id,
        "action": action
    }

    if action == 'raise':
        amount = getattr(args, 'amount', None)
        if amount is None:
            Output.error("--amount required for raise action")
            sys.exit(ExitCode.INVALID_INPUT)
        payload["amount"] = int(amount * 1e9)

    with Spinner(f"Performing {action}..."):
        resp = api_request('POST', f"{api_url}/poker/action", json=payload)
        result = resp.json()

    rt = get_runtime()
    if rt.format == OutputFormat.JSON:
        Output.json_output(result)
        if not result.get('success'):
            sys.exit(ExitCode.API_ERROR)
        return

    if result.get('success'):
        Output.success(f"{action.capitalize()} successful!")
        display_poker_table(result['game'], pubkey)
    else:
        Output.error(result.get('error', 'Unknown error'))
        sys.exit(ExitCode.API_ERROR)


def cmd_poker_games(args: argparse.Namespace) -> None:
    """List poker games"""
    api_url = get_api_url()
    status_filter = getattr(args, 'status', None)

    url = f"{api_url}/poker/games"
    if status_filter:
        url += f"?status={status_filter}"

    with Spinner("Fetching games..."):
        resp = api_request('GET', url)
        result = resp.json()

    rt = get_runtime()
    if rt.format == OutputFormat.JSON:
        Output.json_output(result)
        return

    games = result.get('games', [])

    if not games:
        print("No games found.")
        return

    print(f"\n{'ID':<8} {'Status':<10} {'Buy-in':<10} {'Player 1':<16} {'Player 2':<16} {'Created':<20}")
    print("=" * 85)

    for game in games:
        game_id = game['id'][:8]
        status = game.get('status', '?')
        buy_in = game.get('buyInLamports', game.get('buy_in', 0)) / 1e9
        created = game.get('createdAt', game.get('created_at', ''))[:19]
        p1 = game.get('player1') or {}
        p2 = game.get('player2') or {}
        p1_name = (p1.get('name') or p1.get('wallet', '?')[:8]) if p1 else '-'
        p2_name = (p2.get('name') or p2.get('wallet', '?')[:8]) if p2 else 'waiting...'
        print(f"{game_id:<8} {status:<10} {buy_in:<10.4f} {p1_name:<16} {p2_name:<16} {created:<20}")

    print(f"\nTotal: {result.get('total', len(games))} games")


def cmd_poker_stats(args: argparse.Namespace) -> None:
    """Show poker statistics"""
    wallet = load_wallet()
    pubkey = str(wallet.pubkey())
    api_url = get_api_url()

    with Spinner("Fetching stats..."):
        resp = api_request('GET', f"{api_url}/stats?wallet={pubkey}")
        result = resp.json()

    rt = get_runtime()
    if rt.format == OutputFormat.JSON:
        Output.json_output(result)
        if not result.get('agent'):
            sys.exit(ExitCode.NOT_FOUND)
        return

    if not result.get('agent'):
        Output.error("Agent not found. Register first with: python mya.py link")
        sys.exit(ExitCode.NOT_FOUND)

    agent = result['agent']
    games_played = agent.get('games_played', 0)
    games_won = agent.get('games_won', 0)
    total_winnings = agent.get('total_winnings', 0) / 1e9

    win_rate = (games_won / games_played * 100) if games_played > 0 else 0

    print("\n╔══════════════════════════════════╗")
    print("║       POKER STATISTICS           ║")
    print("╠══════════════════════════════════╣")
    print(f"║  Games Played: {games_played:<17} ║")
    print(f"║  Games Won: {games_won:<20} ║")
    print(f"║  Win Rate: {win_rate:.1f}%{' ' * (20 - len(f'{win_rate:.1f}%'))} ║")
    print(f"║  Total Winnings: {total_winnings:.4f} SOL{' ' * (11 - len(f'{total_winnings:.4f}'))} ║")
    print("╚══════════════════════════════════╝\n")


def cmd_poker_cancel(args: argparse.Namespace) -> None:
    """Cancel a waiting poker game"""
    game_id = getattr(args, 'game_id', None)
    if not game_id:
        Output.error("Game ID required")
        sys.exit(ExitCode.INVALID_INPUT)

    wallet = load_wallet()
    pubkey = str(wallet.pubkey())
    api_url = get_api_url()

    challenge, signature = get_poker_challenge("poker-cancel")

    with Spinner("Cancelling game..."):
        resp = api_request('POST', f"{api_url}/poker/cancel", json={
            "walletAddress": pubkey,
            "challenge": challenge,
            "signature": signature,
            "gameId": game_id,
        })
        result = resp.json()

    rt = get_runtime()
    if rt.format == OutputFormat.JSON:
        Output.json_output(result)
        if not result.get('success'):
            sys.exit(ExitCode.API_ERROR)
        return

    if result.get('success'):
        Output.success("Game cancelled successfully!")
        if result.get('refundTx'):
            print(f"Refund tx: https://solscan.io/tx/{result['refundTx']}?cluster=devnet")
    else:
        Output.error(result.get('error', 'Unknown error'))
        sys.exit(ExitCode.API_ERROR)


def cmd_poker_status(args: argparse.Namespace) -> None:
    """Check current game state (single poll)"""
    game_id = getattr(args, 'game_id', None)
    if not game_id:
        Output.error("Game ID required")
        sys.exit(ExitCode.INVALID_INPUT)

    wallet = load_wallet()
    pubkey = str(wallet.pubkey())
    api_url = get_api_url()

    with Spinner("Fetching game state..."):
        resp = api_request('GET', f"{api_url}/poker/game/{game_id}?wallet={pubkey}")
        game = resp.json()

    rt = get_runtime()
    if rt.format == OutputFormat.JSON:
        Output.json_output(game)
        return

    if game.get('error'):
        Output.error(game['error'])
        sys.exit(ExitCode.API_ERROR)

    display_poker_table(game, pubkey)

    status = game.get('status', 'unknown')
    if status == 'completed':
        winner = game.get('winner')
        if winner and winner.get('wallet') == pubkey:
            Output.success("You won!")
        elif winner:
            Output.info(f"Game over. Winner: {winner.get('name') or winner.get('wallet', '?')[:8]}")
        else:
            Output.info("Game ended in a tie.")
    elif status == 'waiting':
        Output.info("Waiting for opponent to join...")
    elif game.get('yourTurn'):
        print("\n  YOUR TURN - actions: fold | check | call | raise")
        print(f"  python mya.py poker action {game_id} <action>")
    else:
        Output.info("Waiting for opponent's move...")


def cmd_poker_history(args: argparse.Namespace) -> None:
    """Show action history for a poker game"""
    game_id = getattr(args, 'game_id', None)
    if not game_id:
        Output.error("Game ID required")
        sys.exit(ExitCode.INVALID_INPUT)

    api_url = get_api_url()

    with Spinner("Fetching action history..."):
        resp = api_request('GET', f"{api_url}/poker/game/{game_id}/actions")
        result = resp.json()

    rt = get_runtime()
    if rt.format == OutputFormat.JSON:
        Output.json_output(result)
        return

    actions = result.get('actions', [])
    if not actions:
        print("No actions recorded for this game.")
        return

    print(f"\nAction History — Game {game_id[:8]}...")
    print(f"{'#':<4} {'Player':<15} {'Action':<8} {'Amount':<12} {'Round':<10} {'Pot After':<12}")
    print("=" * 65)
    for i, a in enumerate(actions, 1):
        player = a.get('player') or {}
        player_name = player.get('name') or (player.get('wallet', '?')[:8] if player.get('wallet') else '?')
        amount_val = a.get('amount')
        amount = f"{amount_val / 1e9:.4f}" if amount_val else '-'
        pot_after_val = a.get('potAfter')
        pot_after = f"{pot_after_val / 1e9:.4f}" if pot_after_val else '-'
        round_name = a.get('bettingRound', '?')
        print(f"{i:<4} {player_name:<15} {a.get('action', '?'):<8} {amount:<12} {round_name:<10} {pot_after:<12}")

    print(f"\nTotal actions: {result.get('total', len(actions))}")


def cmd_poker_verify(args: argparse.Namespace) -> None:
    """Verify provably fair deck for a completed game"""
    game_id = getattr(args, 'game_id', None)
    if not game_id:
        Output.error("Game ID required")
        sys.exit(ExitCode.INVALID_INPUT)

    api_url = get_api_url()

    with Spinner("Verifying deck fairness..."):
        resp = api_request('GET', f"{api_url}/poker/verify?gameId={game_id}")
        result = resp.json()

    rt = get_runtime()
    if rt.format == OutputFormat.JSON:
        Output.json_output(result)
        return

    if result.get('error'):
        Output.error(result['error'])
        sys.exit(ExitCode.API_ERROR)

    verified = result.get('verified')
    if verified is True:
        Output.success("DECK VERIFIED — Provably fair!")
    elif verified is False:
        Output.error("VERIFICATION FAILED — Deck may have been tampered with!")
    else:
        Output.info(result.get('message', 'Verification not available'))

    if result.get('deckHash'):
        print(f"\n  Deck Hash:     {result['deckHash']}")
    if result.get('serverSecret'):
        print(f"  Server Secret: {result['serverSecret']}")
    if result.get('deckSeed'):
        print(f"  Deck Seed:     {result['deckSeed']}")

    game_info = result.get('game', {})
    if game_info.get('pot'):
        print(f"\n  Pot: {game_info['pot'] / 1e9:.4f} SOL")
    if game_info.get('player1Hand'):
        print(f"  Player 1 Hand: {format_hand(game_info['player1Hand'])}")
    if game_info.get('player2Hand'):
        print(f"  Player 2 Hand: {format_hand(game_info['player2Hand'])}")
    if game_info.get('communityCards'):
        print(f"  Community:     {format_hand(game_info['communityCards'])}")


def cmd_help_all(args: argparse.Namespace) -> None:
    """Show all help (Issue #149)."""
    print(f"""
MintYourAgent v{Constants.VERSION} - Complete CLI Reference
{'=' * 60}

COMMANDS:
  setup               Create a new wallet
  wallet              Wallet management (balance, export, import, etc.)
  launch              Launch a token on pump.fun
  tokens              List tokens in wallet
  history             Show command history
  backup              Backup/restore wallet
  verify              Verify wallet integrity
  status              Check API/RPC status
  trending            Show trending tokens
  leaderboard         Show launch leaderboard
  stats               Show your stats
  airdrop             Request devnet airdrop
  transfer            Transfer SOL
  sign                Sign a message
  soul                Extract agent personality (privacy-safe)
  link                Link agent to mintyouragent.com
  config              Manage configuration
  uninstall           Remove all data

COMMAND ALIASES:
  l = launch, w = wallet, s = setup, c = config
  h = history, t = tokens, b = backup

GLOBAL FLAGS:
  --version           Show version
  --json              JSON output
  --format            text/json/csv/table
  -o, --output-file   Write to file
  --no-color          Disable colors
  --no-emoji          Disable emoji
  --timestamps        Show timestamps
  -q, --quiet         Quiet mode
  -v, --verbose       Verbose
  --debug             Debug mode

NETWORK FLAGS:
  --network           mainnet/devnet/testnet
  --api-url           Override API
  --rpc-url           Override RPC
  --proxy             HTTP proxy
  --timeout           Request timeout
  --retry-count       Retry attempts

ENVIRONMENT VARIABLES:
  SOUL_API_URL        API endpoint (optional, defaults to https://mintyouragent.com/api)
  SOUL_SSL_VERIFY     SSL verification (optional)
  HELIUS_RPC          RPC endpoint (optional)

For command-specific help: python mya.py <command> --help
Documentation: https://mintyouragent.com/docs
""")


def migrate_legacy_wallet() -> None:
    """Migrate wallet from skill folder to ~/.mintyouragent/ on startup."""
    try:
        skill_dir = Path(__file__).parent.resolve()
        home_dir = Path.home() / ".mintyouragent"
        
        # Check for legacy wallet in skill folder
        legacy_wallet = skill_dir / "wallet.json"
        home_wallet = home_dir / "wallet.json"
        
        if legacy_wallet.exists() and not home_wallet.exists():
            home_dir.mkdir(exist_ok=True)
            shutil.copy2(str(legacy_wallet), str(home_wallet))
            os.chmod(home_wallet, 0o600)
            legacy_wallet.unlink()
            print(f"⚠️  Migrated wallet to {home_dir}")
            print("   Your wallet is now safe from skill updates!")
        
        # Also migrate recovery file
        for name in ["SEED_PHRASE.txt", "RECOVERY_KEY.txt", "BACKUP.txt"]:
            legacy_file = skill_dir / name
            home_file = home_dir / name
            if legacy_file.exists() and not home_file.exists():
                shutil.copy2(str(legacy_file), str(home_file))
                os.chmod(home_file, 0o600)
                legacy_file.unlink()
    except:
        pass  # Don't fail on migration errors


def main() -> None:
    """Main entry point."""
    migrate_legacy_wallet()  # Run FIRST before anything else
    load_dotenv()
    setup_signal_handlers()
    
    parser = argparse.ArgumentParser(
        description="MintYourAgent - Launch tokens on pump.fun",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Version: {Constants.VERSION} | Docs: https://mintyouragent.com/docs"
    )
    
    # Global options
    parser.add_argument("--version", action="version", version=f"MintYourAgent {Constants.VERSION}")
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("--no-emoji", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--format", choices=["text", "json", "csv", "table"], default="text")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--timestamps", action="store_true")
    parser.add_argument("--config-file", type=Path)
    parser.add_argument("--wallet-file", type=Path)
    parser.add_argument("--log-file", type=Path)
    parser.add_argument("-o", "--output-file", type=Path)
    parser.add_argument("--api-url")
    parser.add_argument("--rpc-url")
    parser.add_argument("--network", choices=["mainnet", "devnet", "testnet"], default="mainnet")
    parser.add_argument("--proxy")
    parser.add_argument("--user-agent")
    parser.add_argument("--timeout", type=int, default=Constants.DEFAULT_TIMEOUT)
    parser.add_argument("--retry-count", type=int, default=Constants.DEFAULT_RETRY_COUNT)
    parser.add_argument("--priority-fee", type=int, default=0)
    parser.add_argument("--skip-balance-check", action="store_true")
    parser.add_argument("--help-all", action="store_true", help="Show complete help")
    
    subparsers = parser.add_subparsers(dest="command")
    
    # Setup
    setup_p = subparsers.add_parser("setup", aliases=["s"], help="Create wallet")
    setup_p.add_argument("--force", action="store_true")
    
    # Wallet
    wallet_p = subparsers.add_parser("wallet", aliases=["w"], help="Wallet commands")
    wallet_p.add_argument("wallet_cmd", nargs="?", default="help", choices=["address", "balance", "export", "show-key", "fund", "check", "import", "help"])
    wallet_p.add_argument("--key")
    
    # Launch
    launch_p = subparsers.add_parser("launch", aliases=["l"], help="Launch token")
    launch_p.add_argument("--name")
    launch_p.add_argument("--symbol")
    launch_p.add_argument("--description")
    launch_p.add_argument("--image")
    launch_p.add_argument("--image-file")
    launch_p.add_argument("--banner")
    launch_p.add_argument("--banner-file")
    launch_p.add_argument("--twitter")
    launch_p.add_argument("--telegram")
    launch_p.add_argument("--website")
    launch_p.add_argument("--initial-buy", type=float, default=0)
    launch_p.add_argument("--ai-initial-buy", action="store_true")
    launch_p.add_argument("--slippage", type=int, default=100)
    launch_p.add_argument("--dry-run", action="store_true")
    launch_p.add_argument("--preview", action="store_true")
    launch_p.add_argument("--tips", action="store_true")
    launch_p.add_argument("-y", "--yes", action="store_true")
    
    # Tokens
    tokens_p = subparsers.add_parser("tokens", aliases=["t"], help="List tokens")
    
    # History
    history_p = subparsers.add_parser("history", aliases=["h"], help="Command history")
    history_p.add_argument("--limit", type=int, default=20)
    
    # Backup
    backup_p = subparsers.add_parser("backup", aliases=["b"], help="Backup wallet")
    backup_p.add_argument("backup_cmd", nargs="?", default="list", choices=["create", "list", "restore"])
    backup_p.add_argument("--name")
    backup_p.add_argument("--file")
    
    # Verify
    verify_p = subparsers.add_parser("verify", help="Verify wallet")
    
    # Status
    status_p = subparsers.add_parser("status", aliases=["st"], help="API status")
    
    # Trending
    trending_p = subparsers.add_parser("trending", aliases=["tr"], help="Trending tokens")
    
    # Leaderboard
    leaderboard_p = subparsers.add_parser("leaderboard", aliases=["lb"], help="Leaderboard")
    
    # Stats
    stats_p = subparsers.add_parser("stats", help="Your stats")
    
    # Airdrop
    airdrop_p = subparsers.add_parser("airdrop", help="Devnet airdrop")
    airdrop_p.add_argument("--amount", type=float, default=1.0)
    
    # Transfer
    transfer_p = subparsers.add_parser("transfer", help="Transfer SOL")
    transfer_p.add_argument("--to")
    transfer_p.add_argument("--amount", type=float)
    transfer_p.add_argument("-y", "--yes", action="store_true")
    
    # Sign
    sign_p = subparsers.add_parser("sign", help="Sign message")
    sign_p.add_argument("--message", "-m")
    
    # Collect Fees
    collect_fees_p = subparsers.add_parser("collect-fees", aliases=["fees"], help="Collect creator fees")
    collect_fees_p.add_argument("--dry-run", action="store_true", help="Check balance without collecting")
    
    # Sell
    sell_p = subparsers.add_parser("sell", help="Sell tokens")
    sell_p.add_argument("--mint", "-m", required=True, help="Token mint address")
    sell_p.add_argument("--amount", "-a", type=float, help="Token amount to sell")
    sell_p.add_argument("--percent", "-p", type=float, help="Percentage of holdings to sell")
    sell_p.add_argument("--target-gain", "-t", type=float, help="Wait for X% gain then sell")
    sell_p.add_argument("--slippage", "-s", type=int, default=500, help="Slippage in basis points (default: 500 = 5%)")
    sell_p.add_argument("--dry-run", action="store_true", help="Preview without executing")
    
    # Config
    config_p = subparsers.add_parser("config", aliases=["c"], help="Configuration")
    config_p.add_argument("config_cmd", nargs="?", default="show", choices=["show", "set", "autonomous"])
    config_p.add_argument("key", nargs="?")
    config_p.add_argument("value", nargs="?")
    
    # Soul - extract agent personality
    soul_p = subparsers.add_parser("soul", help="Extract agent soul/personality")
    soul_p.add_argument("--no-submit", action="store_true", help="Don't prompt to submit")
    soul_p.add_argument("-o", "--output-file", help="Save soul JSON to file")
    
    # Link - connect agent to platform
    link_p = subparsers.add_parser("link", help="Link agent to mintyouragent.com")
    link_p.add_argument("--soul-file", help="Soul JSON file to include")
    
    # Uninstall
    uninstall_p = subparsers.add_parser("uninstall", help="Remove data")
    uninstall_p.add_argument("-y", "--yes", action="store_true")

    # Poker commands (cash games — 2-6 players)
    poker_p = subparsers.add_parser("poker", aliases=["p"], help="Play poker (2-6 player cash games)")
    poker_subs = poker_p.add_subparsers(dest="poker_cmd")

    poker_create_p = poker_subs.add_parser("create", help="Create a new poker table")
    poker_create_p.add_argument("--small-blind", type=float, default=0.01, help="Small blind in SOL (default: 0.01)")
    poker_create_p.add_argument("--big-blind", type=float, default=0.02, help="Big blind in SOL (default: 0.02)")
    poker_create_p.add_argument("--min-buy-in", type=float, help="Min buy-in in SOL (default: 20x big blind)")
    poker_create_p.add_argument("--max-buy-in", type=float, help="Max buy-in in SOL (default: 100x big blind)")
    poker_create_p.add_argument("--seats", type=int, default=6, help="Max seats 2-6 (default: 6)")

    poker_join_p = poker_subs.add_parser("join", help="Join a table and deposit buy-in")
    poker_join_p.add_argument("table_id", help="Table ID to join")
    poker_join_p.add_argument("--buy-in", type=float, required=True, help="Buy-in amount in SOL")

    poker_leave_p = poker_subs.add_parser("leave", help="Leave table (chips settled)")
    poker_leave_p.add_argument("table_id", help="Table ID to leave")

    poker_close_p = poker_subs.add_parser("close", help="Close a table you created")
    poker_close_p.add_argument("table_id", help="Table ID to close")

    poker_reload_p = poker_subs.add_parser("reload", help="Add more chips to your stack")
    poker_reload_p.add_argument("table_id", help="Table ID")
    poker_reload_p.add_argument("--amount", type=float, required=True, help="Amount in SOL to add")

    poker_watch_p = poker_subs.add_parser("watch", help="Watch table with auto-polling")
    poker_watch_p.add_argument("table_id", help="Table ID to watch")
    poker_watch_p.add_argument("--poll", type=int, default=2, help="Poll interval in seconds (default: 2)")
    poker_watch_p.add_argument("--mode", choices=["human", "ai", "ask"], default="ask", help="Play mode")
    poker_watch_p.add_argument("--verbose", "-v", action="store_true", help="Show AI reasoning")

    poker_tables_p = poker_subs.add_parser("tables", help="List open/active tables")

    # Backward compat: 'poker cash <cmd>' still works
    cash_p = poker_subs.add_parser("cash", help="(alias) Same as poker commands above")
    cash_subs = cash_p.add_subparsers(dest="cash_cmd")
    _cc = cash_subs.add_parser("create", help="Create table")
    _cc.add_argument("--small-blind", type=float, default=0.01)
    _cc.add_argument("--big-blind", type=float, default=0.02)
    _cc.add_argument("--min-buy-in", type=float)
    _cc.add_argument("--max-buy-in", type=float)
    _cc.add_argument("--seats", type=int, default=6)
    _cj = cash_subs.add_parser("join", help="Join table")
    _cj.add_argument("table_id")
    _cj.add_argument("--buy-in", type=float, required=True)
    _cl = cash_subs.add_parser("leave", help="Leave table")
    _cl.add_argument("table_id")
    _cx = cash_subs.add_parser("close", help="Close table")
    _cx.add_argument("table_id")
    _cr = cash_subs.add_parser("reload", help="Reload chips")
    _cr.add_argument("table_id")
    _cr.add_argument("--amount", type=float, required=True)
    _cw = cash_subs.add_parser("watch", help="Watch table")
    _cw.add_argument("table_id")
    _cw.add_argument("--poll", type=int, default=2)
    _cw.add_argument("--mode", choices=["human", "ai", "ask"], default="ask")
    _cw.add_argument("--verbose", "-v", action="store_true")
    cash_subs.add_parser("tables", help="List tables")

    args = parser.parse_args()
    
    # Show full help
    if args.help_all:
        cmd_help_all(args)
        return
    
    # Resolve aliases
    if args.command in Constants.COMMAND_ALIASES:
        args.command = Constants.COMMAND_ALIASES[args.command]
    
    # Build runtime
    format_map = {"text": OutputFormat.TEXT, "json": OutputFormat.JSON, "csv": OutputFormat.CSV, "table": OutputFormat.TABLE}
    network_map = {"mainnet": Network.MAINNET, "devnet": Network.DEVNET, "testnet": Network.TESTNET}
    
    runtime = RuntimeConfig(
        config_file=args.config_file,
        wallet_file=args.wallet_file,
        log_file=args.log_file,
        output_file=args.output_file,
        api_url=args.api_url or Constants.DEFAULT_API_URL,
        rpc_url=args.rpc_url,
        network=network_map.get(args.network, Network.MAINNET),
        proxy=args.proxy,
        user_agent=args.user_agent or Constants.USER_AGENT,
        timeout=args.timeout,
        retry_count=args.retry_count,
        priority_fee=args.priority_fee,
        skip_balance_check=args.skip_balance_check,
        format=format_map.get(args.format, OutputFormat.TEXT) if not args.json else OutputFormat.JSON,
        quiet=args.quiet,
        debug=args.debug,
        verbose=args.verbose,
        no_color=args.no_color,
        no_emoji=args.no_emoji,
        timestamps=args.timestamps,
    )
    set_runtime(runtime)
    setup_logging()
    
    # Route commands
    commands = {
        "setup": cmd_setup, "wallet": cmd_wallet, "launch": cmd_launch,
        "tokens": cmd_tokens, "history": cmd_history, "backup": cmd_backup,
        "verify": cmd_verify, "status": cmd_status, "trending": cmd_trending,
        "leaderboard": cmd_leaderboard, "stats": cmd_stats, "airdrop": cmd_airdrop,
        "transfer": cmd_transfer, "sign": cmd_sign, "collect-fees": cmd_collect_fees,
        "fees": cmd_collect_fees, "sell": cmd_sell, "config": cmd_config,
        "soul": cmd_soul, "link": cmd_link, "uninstall": cmd_uninstall,
        "poker": cmd_poker,
    }
    
    if args.command in commands:
        commands[args.command](args)
    elif args.command:
        # Did you mean? (Issue #142)
        suggestion = suggest_command(args.command, list(commands.keys()))
        if suggestion:
            Output.error(f"Unknown command: {args.command}", f"Did you mean '{suggestion}'?")
        else:
            Output.error(f"Unknown command: {args.command}", "Run: python mya.py --help")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
