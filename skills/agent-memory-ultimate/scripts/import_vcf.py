#!/usr/bin/env python3
"""
Import VCF (vCard) contacts into the knowledge base.
Updates existing contacts with names from phone export.

Usage: python3 import_vcf.py <path/to/contacts.vcf>
"""
import sqlite3
import sys
import re
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "db" / "jarvis.db"

def parse_vcf(vcf_path: Path) -> list[dict]:
    """Parse VCF file into list of contacts"""
    contacts = []
    current = {}
    
    with open(vcf_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            
            if line == "BEGIN:VCARD":
                current = {}
            elif line == "END:VCARD":
                if current.get("phone"):
                    contacts.append(current)
                current = {}
            elif line.startswith("FN:") or line.startswith("FN;"):
                # Full name
                name = line.split(":", 1)[1] if ":" in line else ""
                current["name"] = name.strip()
            elif line.startswith("N:") or line.startswith("N;"):
                # Structured name (Last;First;Middle;Prefix;Suffix)
                if "name" not in current:
                    parts = line.split(":", 1)[1].split(";") if ":" in line else []
                    # Combine last + first
                    name_parts = [p.strip() for p in parts[:2] if p.strip()]
                    if name_parts:
                        current["name"] = " ".join(reversed(name_parts))
            elif "TEL" in line and ":" in line:
                # Phone number
                phone = line.split(":", 1)[1].strip()
                # Normalize: remove spaces, dashes, parentheses
                phone = re.sub(r'[\s\-\(\)]', '', phone)
                # Ensure + prefix
                if phone and not phone.startswith("+"):
                    # Assume Spanish if starts with 6, 7, or 9
                    if phone.startswith(("6", "7", "9")) and len(phone) == 9:
                        phone = "+34" + phone
                    elif not phone.startswith("00"):
                        phone = "+" + phone
                    else:
                        phone = "+" + phone[2:]  # Convert 00 to +
                
                if phone and len(phone) >= 10:
                    if "phone" not in current:
                        current["phone"] = phone
                    elif "phones" not in current:
                        current["phones"] = [current["phone"], phone]
                    else:
                        current["phones"].append(phone)
    
    return contacts

def import_contacts(contacts: list[dict], conn: sqlite3.Connection) -> tuple[int, int]:
    """Import contacts into database, returns (updated, new)"""
    updated = 0
    new = 0
    
    for contact in contacts:
        name = contact.get("name", "")
        phones = contact.get("phones", [contact["phone"]] if contact.get("phone") else [])
        
        for phone in phones:
            # Check if exists
            existing = conn.execute(
                "SELECT id, name FROM contacts WHERE phone = ?", (phone,)
            ).fetchone()
            
            if existing:
                # Update name if we have one and existing doesn't
                if name and not existing[1]:
                    conn.execute(
                        "UPDATE contacts SET name = ?, source = 'vcf', updated_at = CURRENT_TIMESTAMP WHERE phone = ?",
                        (name, phone)
                    )
                    updated += 1
            else:
                # Insert new
                conn.execute(
                    "INSERT INTO contacts (phone, name, source) VALUES (?, ?, 'vcf')",
                    (phone, name or None)
                )
                new += 1
    
    conn.commit()
    return updated, new

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 import_vcf.py <path/to/contacts.vcf>")
        print("\nExport from Android:")
        print("  1. Open Contacts app")
        print("  2. Menu (⋮) → Settings → Export")
        print("  3. Save .vcf file")
        return
    
    vcf_path = Path(sys.argv[1])
    if not vcf_path.exists():
        print(f"❌ File not found: {vcf_path}")
        return
    
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        print("   Run init_db.py first")
        return
    
    print(f"📥 Importing contacts from {vcf_path.name}")
    
    # Parse VCF
    contacts = parse_vcf(vcf_path)
    print(f"   Found {len(contacts)} contacts in VCF")
    
    # Count phones
    total_phones = sum(len(c.get("phones", [c["phone"]] if c.get("phone") else [])) for c in contacts)
    print(f"   Total phone numbers: {total_phones}")
    
    # Import
    conn = sqlite3.connect(DB_PATH)
    updated, new = import_contacts(contacts, conn)
    
    # Stats
    named = conn.execute("SELECT COUNT(*) FROM contacts WHERE name IS NOT NULL").fetchone()[0]
    total = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
    
    conn.close()
    
    print(f"\n✅ Import complete:")
    print(f"   Updated with names: {updated}")
    print(f"   New contacts added: {new}")
    print(f"   Total contacts: {total}")
    print(f"   Contacts with names: {named} ({100*named//total}%)")

if __name__ == "__main__":
    main()
