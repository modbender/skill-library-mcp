#!/usr/bin/env python3
import sqlite3
import argparse
import sys
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Path configurations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data/vault.db")
SALT_PATH = os.path.join(BASE_DIR, "data/salt.bin")

def get_master_key():
    key = os.environ.get("MEMA_VAULT_MASTER_KEY")
    if not key:
        print("CRITICAL: MEMA_VAULT_MASTER_KEY not found in environment.")
        sys.exit(1)
    return key.encode()

def get_fernet():
    password = get_master_key()
    if not os.path.exists(SALT_PATH):
        os.makedirs(os.path.dirname(SALT_PATH), exist_ok=True)
        salt = os.urandom(16)
        with open(SALT_PATH, 'wb') as f:
            f.write(salt)
    else:
        with open(SALT_PATH, 'rb') as f:
            salt = f.read()

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return Fernet(key)

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS credentials (id INTEGER PRIMARY KEY, service TEXT UNIQUE, username TEXT, encrypted_password TEXT, meta TEXT)")
    conn.commit()
    conn.close()

def encrypt(text):
    f = get_fernet()
    return f.encrypt(text.encode()).decode()

def decrypt(token):
    f = get_fernet()
    return f.decrypt(token.encode()).decode()

def add(service, username, password, meta=""):
    try:
        enc_pass = encrypt(password)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO credentials (service, username, encrypted_password, meta) VALUES (?, ?, ?, ?)", (service, username, enc_pass, meta))
        conn.commit()
        print(f"Stored & Encrypted: {service}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def get(service, show=False):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, encrypted_password, meta FROM credentials WHERE service LIKE ?", (f"%{service}%",))
    rows = c.fetchall()
    conn.close()
    if not rows:
        print("Not found")
        return
    for r in rows:
        try:
            dec_pass = decrypt(r[1])
            masked = dec_pass[:2] + "*" * (len(dec_pass)-4) + dec_pass[-2:] if len(dec_pass) > 4 else "****"
            print(f"Service: {service}")
            print(f"User: {r[0]}")
            print(f"Pass: {dec_pass if show else masked}")
            print(f"Meta: {r[2]}")
        except Exception as e:
            print(f"Decryption failed for {service}. Check Master Key.")

def list_creds():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT service, username FROM credentials")
    rows = c.fetchall()
    conn.close()
    print("Vault Contents:")
    for r in rows:
        print(f"- {r[0]} (User: {r[1]})")

if __name__ == "__main__":
    init_db()
    parser = argparse.ArgumentParser(description="Mema Vault CLI (AES-256)")
    subparsers = parser.add_subparsers(dest="command")
    
    add_p = subparsers.add_parser("set")
    add_p.add_argument("service")
    add_p.add_argument("username")
    add_p.add_argument("password")
    add_p.add_argument("--meta", default="")
    
    get_p = subparsers.add_parser("get")
    get_p.add_argument("service")
    get_p.add_argument("--show", action="store_true", help="Show raw password")
    
    list_p = subparsers.add_parser("list")
    
    args = parser.parse_args()
    
    if args.command == "set":
        add(args.service, args.username, args.password, args.meta)
    elif args.command == "get":
        get(args.service, args.show)
    elif args.command == "list":
        list_creds()
    else:
        parser.print_help()
