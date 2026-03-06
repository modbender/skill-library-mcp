#!/usr/bin/env python3
"""
Agent Identity - Cryptographic Identity for AI Agents
v1.0.0

Sign and verify agent messages with Ed25519 or RSA
"""

import argparse
import base64
import hashlib
import json
import os
import sys

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519, rsa, padding
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("ERROR: cryptography library not installed", file=sys.stderr)
    print("Run: pip install cryptography", file=sys.stderr)
    sys.exit(1)


KEY_DIR = "keys"


def generate_ed25519(name, password=None):
    """Generate Ed25519 key pair"""
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    os.makedirs(KEY_DIR, exist_ok=True)
    
    if password:
        # Encrypt private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
        )
    else:
        # No encryption (for convenience, but less secure)
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    private_path = os.path.join(KEY_DIR, f"{name}_private.pem")
    public_path = os.path.join(KEY_DIR, f"{name}_public.pem")
    
    with open(private_path, "wb") as f:
        f.write(private_pem)
    
    with open(public_path, "wb") as f:
        f.write(public_pem)
    
    agent_id = get_agent_id(public_path)
    
    print(f"Generated Ed25519 key pair for: {name}")
    print(f"Private key: {private_path}")
    print(f"Public key: {public_path}")
    print(f"Agent ID: {agent_id}")
    
    return agent_id


def generate_rsa(name, bits=2048, password=None):
    """Generate RSA key pair"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=bits,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    
    os.makedirs(KEY_DIR, exist_ok=True)
    
    if password:
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
        )
    else:
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    private_path = os.path.join(KEY_DIR, f"{name}_private.pem")
    public_path = os.path.join(KEY_DIR, f"{name}_public.pem")
    
    with open(private_path, "wb") as f:
        f.write(private_pem)
    
    with open(public_path, "wb") as f:
        f.write(public_pem)
    
    agent_id = get_agent_id(public_path)
    
    print(f"Generated RSA-{bits} key pair for: {name}")
    print(f"Private key: {private_path}")
    print(f"Public key: {public_path}")
    print(f"Agent ID: {agent_id}")
    
    return agent_id


def sign_message(message, private_key_path, password=None):
    """Sign a message"""
    with open(private_key_path, "rb") as f:
        private_pem = f.read()
    
    pwd = password.encode() if password else None
    private_key = serialization.load_pem_private_key(private_pem, password=pwd, backend=default_backend())
    
    # Ed25519 doesn't use padding
    if isinstance(private_key, ed25519.Ed25519PrivateKey):
        signature = private_key.sign(message.encode("utf-8"))
    else:
        signature = private_key.sign(
            message.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
    
    signature_b64 = base64.b64encode(signature).decode("utf-8")
    print(f"Message: {message}")
    print(f"Signature: {signature_b64}")
    
    return signature_b64


def verify_message(message, signature_b64, public_key_path):
    """Verify a signature"""
    with open(public_key_path, "rb") as f:
        public_pem = f.read()
    
    signature = base64.b64decode(signature_b64)
    public_key = serialization.load_pem_public_key(public_pem, backend=default_backend())
    
    # Ed25519 doesn't use padding
    if isinstance(public_key, ed25519.Ed25519PublicKey):
        try:
            public_key.verify(signature, message.encode("utf-8"))
            print("[OK] Signature VERIFIED")
            return True
        except Exception:
            print("[ERR] Signature INVALID")
            return False
    else:
        try:
            public_key.verify(
                signature,
                message.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            print("[OK] Signature VERIFIED")
            return True
        except Exception:
            print("[ERR] Signature INVALID")
            return False


def get_agent_id(public_key_path):
    """Generate deterministic Agent ID from public key"""
    with open(public_key_path, "rb") as f:
        public_pem = f.read()
    
    # SHA-256 hash of public key
    agent_id = hashlib.sha256(public_pem).hexdigest()[:32]
    return agent_id


def cmd_generate(args):
    if args.key_type == "ed25519":
        generate_ed25519(args.name, args.password)
    else:
        generate_rsa(args.name, args.bits, args.password)


def cmd_sign(args):
    sign_message(args.message, args.private_key, args.password)


def cmd_verify(args):
    verify_message(args.message, args.signature, args.public_key)


def cmd_id(args):
    agent_id = get_agent_id(args.public_key)
    print(f"Agent ID: {agent_id}")


def sign_agent_card(public_key_path, private_key_path, name, description, capabilities, endpoint, password=None):
    """Sign an Agent Card"""
    # Load private key
    with open(private_key_path, "rb") as f:
        private_pem = f.read()
    
    if password:
        private_key = serialization.load_pem_private_key(private_pem, password=password.encode(), backend=default_backend())
    else:
        private_key = serialization.load_pem_private_key(private_pem, password=None, backend=default_backend())
    
    # Create Agent Card
    agent_card = {
        "agent_id": get_agent_id(public_key_path),
        "name": name,
        "description": description,
        "capabilities": capabilities.split(",") if isinstance(capabilities, str) else capabilities,
        "endpoint": endpoint,
        "version": "1.0.0"
    }
    
    # Sign the card
    card_json = json.dumps(agent_card, sort_keys=True)
    signature = private_key.sign(card_json.encode("utf-8"))
    signature_b64 = base64.b64encode(signature).decode("utf-8")
    
    # Add signature to card
    agent_card["signature"] = signature_b64
    
    return agent_card


def cmd_card(args):
    card = sign_agent_card(
        args.public_key,
        args.private_key,
        args.name,
        args.description,
        args.capabilities,
        args.endpoint,
        args.password
    )
    print(json.dumps(card, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Agent Identity - Cryptographic Identity for AI Agents")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # generate
    gen_parser = subparsers.add_parser("generate", help="Generate key pair")
    gen_parser.add_argument("--name", required=True, help="Agent name")
    gen_parser.add_argument("--key-type", default="ed25519", choices=["ed25519", "rsa"], help="Key type")
    gen_parser.add_argument("--bits", type=int, default=2048, help="RSA key size (if RSA)")
    gen_parser.add_argument("--password", help="Password to encrypt private key")
    
    # sign
    sign_parser = subparsers.add_parser("sign", help="Sign message")
    sign_parser.add_argument("--message", required=True, help="Message to sign")
    sign_parser.add_argument("--private-key", required=True, help="Path to private key")
    sign_parser.add_argument("--password", help="Private key password (if encrypted)")
    
    # verify
    ver_parser = subparsers.add_parser("verify", help="Verify signature")
    ver_parser.add_argument("--message", required=True, help="Original message")
    ver_parser.add_argument("--signature", required=True, help="Base64 signature")
    ver_parser.add_argument("--public-key", required=True, help="Path to public key")
    
    # id
    id_parser = subparsers.add_parser("id", help="Get Agent ID from public key")
    id_parser.add_argument("--public-key", required=True, help="Path to public key")
    
    # card
    card_parser = subparsers.add_parser("card", help="Sign Agent Card")
    card_parser.add_argument("--public-key", required=True, help="Path to public key")
    card_parser.add_argument("--private-key", required=True, help="Path to private key")
    card_parser.add_argument("--name", required=True, help="Agent name")
    card_parser.add_argument("--description", required=True, help="Agent description")
    card_parser.add_argument("--capabilities", required=True, help="Comma-separated capabilities")
    card_parser.add_argument("--endpoint", required=True, help="Agent endpoint URL")
    card_parser.add_argument("--password", help="Private key password (if encrypted)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    handlers = {
        "generate": cmd_generate,
        "sign": cmd_sign,
        "verify": cmd_verify,
        "id": cmd_id,
        "card": cmd_card
    }
    
    handlers[args.command](args)


if __name__ == "__main__":
    main()
