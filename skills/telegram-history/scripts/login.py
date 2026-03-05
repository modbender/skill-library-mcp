#!/usr/bin/env python3
"""Simple login script - pass phone and code as args."""
import asyncio
import json
import os
import sys

from telethon import TelegramClient

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_PATH = os.path.join(SKILL_DIR, "session", "user")
CREDS_PATH = os.path.join(SKILL_DIR, "api_credentials.json")

async def main():
    with open(CREDS_PATH) as f:
        creds = json.load(f)
    
    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
    client = TelegramClient(SESSION_PATH, int(creds["api_id"]), creds["api_hash"])
    
    if len(sys.argv) >= 3 and sys.argv[1] == "check":
        phone = sys.argv[2]
        await client.connect()
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"Already logged in as {me.first_name} ({me.phone})")
        else:
            print("Not logged in. Sending code...")
            await client.send_code_request(phone)
            print("Code sent! Run: python3 login.py verify <phone> <code> <phone_code_hash>")
        await client.disconnect()
        return
    
    if len(sys.argv) >= 3 and sys.argv[1] == "send":
        phone = sys.argv[2]
        await client.connect()
        result = await client.send_code_request(phone)
        print(f"Code sent! phone_code_hash: {result.phone_code_hash}")
        print(f"Run: python3 login.py verify {phone} <code> {result.phone_code_hash}")
        await client.disconnect()
        return
    
    if len(sys.argv) >= 5 and sys.argv[1] == "verify":
        phone = sys.argv[2]
        code = sys.argv[3]
        phone_code_hash = sys.argv[4]
        password = sys.argv[5] if len(sys.argv) > 5 else None
        await client.connect()
        try:
            await client.sign_in(phone, code, phone_code_hash=phone_code_hash)
        except Exception as e:
            if "Two-steps" in str(e) and password:
                await client.sign_in(password=password)
            elif "Two-steps" in str(e):
                print("2FA required. Run: python3 login.py verify <phone> <code> <hash> <2fa_password>")
                await client.disconnect()
                return
            else:
                print(f"Error: {e}")
                await client.disconnect()
                return
        me = await client.get_me()
        print(f"Logged in as {me.first_name} ({me.phone})")
        await client.disconnect()
        return
    
    print("Usage:")
    print("  python3 login.py send <phone>              - Send verification code")
    print("  python3 login.py check <phone>             - Check if logged in")
    print("  python3 login.py verify <phone> <code> <hash> [2fa_password]  - Complete login")

asyncio.run(main())
