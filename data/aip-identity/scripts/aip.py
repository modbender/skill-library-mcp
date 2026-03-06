#!/usr/bin/env python3
"""
AIP Identity Tool — Register, verify, vouch, sign, message, and manage keys with Agent Identity Protocol.
Usage: python3 aip.py <command> [options]
"""

import argparse, base64, hashlib, json, os, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone

AIP_BASE = os.environ.get("AIP_SERVICE_URL", "https://aip-service.fly.dev")
DEFAULT_CREDS = "aip_credentials.json"

def _find_creds_file(filename=DEFAULT_CREDS):
    """Search for credentials in multiple standard locations."""
    candidates = [
        filename,  # current directory
        os.path.join("credentials", filename),  # credentials/ subdir
        os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "credentials", filename),
        os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", filename),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return filename  # fallback to default (will error with helpful message)


# --- Ed25519 helpers (try nacl, fall back to subprocess calling openssl) ---

def _generate_keypair_nacl():
    import nacl.signing
    sk = nacl.signing.SigningKey.generate()
    return (
        base64.b64encode(sk.encode()).decode(),
        base64.b64encode(sk.verify_key.encode()).decode(),
    )

def _sign_nacl(message: bytes, private_key_b64: str) -> str:
    import nacl.signing
    sk = nacl.signing.SigningKey(base64.b64decode(private_key_b64))
    signed = sk.sign(message)
    return base64.b64encode(signed.signature).decode()

def _encrypt_nacl(plaintext: bytes, recipient_pub_b64: str, sender_priv_b64: str) -> str:
    import nacl.public
    sender_sk = nacl.public.PrivateKey(base64.b64decode(sender_priv_b64)[:32])
    recipient_pk = nacl.public.PublicKey(base64.b64decode(recipient_pub_b64))
    box = nacl.public.Box(sender_sk, recipient_pk)
    encrypted = box.encrypt(plaintext)
    return base64.b64encode(encrypted).decode()

def generate_keypair():
    try:
        return _generate_keypair_nacl()
    except ImportError:
        pass
    import subprocess, tempfile
    with tempfile.NamedTemporaryFile(suffix=".pem", delete=False) as f:
        kf = f.name
    try:
        subprocess.run(["openssl", "genpkey", "-algorithm", "Ed25519", "-out", kf],
                       check=True, capture_output=True)
        raw = subprocess.run(["openssl", "pkey", "-in", kf, "-outform", "DER"],
                             check=True, capture_output=True).stdout
        seed = raw[-32:]
        pub_raw = subprocess.run(
            ["openssl", "pkey", "-in", kf, "-pubout", "-outform", "DER"],
            check=True, capture_output=True).stdout
        pub = pub_raw[-32:]
        return base64.b64encode(seed).decode(), base64.b64encode(pub).decode()
    finally:
        os.unlink(kf)

def sign_message(message: bytes, private_key_b64: str) -> str:
    try:
        return _sign_nacl(message, private_key_b64)
    except ImportError:
        pass
    import subprocess, tempfile, textwrap
    seed = base64.b64decode(private_key_b64)
    der_prefix = bytes.fromhex("302e020100300506032b657004220420")
    der = der_prefix + seed
    b64 = base64.b64encode(der).decode()
    pem = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(textwrap.wrap(b64, 64)) + "\n-----END PRIVATE KEY-----\n"
    kf = df = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pem", delete=False, mode="w") as f:
            f.write(pem)
            kf = f.name
        with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as f:
            f.write(message)
            df = f.name
        result = subprocess.run(
            ["openssl", "pkeyutl", "-sign", "-inkey", kf, "-rawin", "-in", df],
            check=True, capture_output=True)
        return base64.b64encode(result.stdout).decode()
    finally:
        if kf: os.unlink(kf)
        if df: os.unlink(df)


# --- API helpers ---

def api(method, path, data=None):
    url = f"{AIP_BASE}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method,
                                headers={"Content-Type": "application/json"} if body else {})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        try:
            err = json.loads(err)
        except Exception:
            pass
        print(f"Error {e.code}: {json.dumps(err, indent=2) if isinstance(err, dict) else err}", file=sys.stderr)
        sys.exit(1)

def load_creds(path):
    p = _find_creds_file(path) if path else _find_creds_file()
    if not os.path.exists(p):
        print(f"Credentials not found: {p}\nRun 'aip.py register --secure' first.", file=sys.stderr)
        sys.exit(1)
    with open(p) as f:
        return json.load(f)


# --- Commands ---

def cmd_register(args):
    if not args.platform or not args.username:
        print("--platform and --username required", file=sys.stderr)
        sys.exit(1)

    out = args.credentials or DEFAULT_CREDS

    if args.secure:
        # Recommended: generate keypair locally, register with /register
        priv_b64, pub_b64 = generate_keypair()
        did = "did:aip:" + hashlib.sha256(base64.b64decode(pub_b64)).hexdigest()[:32]

        result = api("POST", "/register", {
            "did": did,
            "public_key": pub_b64,
            "platform": args.platform,
            "username": args.username,
        })

        creds = {
            "did": did,
            "public_key": pub_b64,
            "private_key": priv_b64,
            "platform": args.platform,
            "username": args.username,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }
    else:
        # Deprecated easy mode
        print("⚠️  WARNING: /register/easy is DEPRECATED. The server generates your private key.", file=sys.stderr)
        print("   Use --secure to generate keys locally (recommended).", file=sys.stderr)

        result = api("POST", "/register/easy", {
            "platform": args.platform,
            "username": args.username,
        })

        if result.get("security_warning"):
            print(f"⚠️  Server warning: {result['security_warning']}", file=sys.stderr)

        creds = {
            "did": result["did"],
            "public_key": result["public_key"],
            "private_key": result["private_key"],
            "platform": args.platform,
            "username": args.username,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }

    with open(out, "w") as f:
        json.dump(creds, f, indent=2)

    print(f"✅ Registered successfully!")
    print(f"   DID: {creds['did']}")
    print(f"   Credentials saved to: {out}")
    print(f"   ⚠️  Back up {out} — private key cannot be recovered!")


def cmd_verify(args):
    if args.did:
        result = api("GET", f"/verify?did={args.did}")
    elif args.username:
        platform = args.platform or "moltbook"
        result = api("GET", f"/verify?platform={platform}&username={args.username}")
    else:
        print("--username or --did required", file=sys.stderr)
        sys.exit(1)

    if not result or not result.get("verified"):
        print("❌ Agent not found in AIP registry.")
        return

    print(f"✅ Verified agent:")
    print(f"   DID: {result.get('did')}")
    platforms = result.get("platforms", [])
    for p in platforms:
        verified_mark = " ✓" if p.get("verified") else ""
        print(f"   Platform: {p.get('platform')} / {p.get('username')}{verified_mark}")
        print(f"   Registered: {p.get('registered_at')}")

    try:
        graph = api("GET", f"/trust-graph?did={result['did']}")
        received = graph.get("vouched_by", graph.get("vouches_received", []))
        if received:
            print(f"   Vouches ({len(received)}):")
            for v in received:
                cat = v.get('category') or v.get('scope', '?')
                print(f"     - {v.get('voucher_did', '?')} [{cat}]")
        else:
            print("   Vouches: none")
    except Exception:
        pass


def cmd_vouch(args):
    creds = load_creds(args.credentials)
    if not args.target_did:
        print("--target-did required", file=sys.stderr)
        sys.exit(1)

    scope = args.scope or "GENERAL"
    statement = args.statement or ""
    msg = f"{creds['did']}|{args.target_did}|{scope}|{statement}"
    sig = sign_message(msg.encode(), creds["private_key"])

    result = api("POST", "/vouch", {
        "voucher_did": creds["did"],
        "target_did": args.target_did,
        "scope": scope,
        "statement": statement,
        "signature": sig,
    })

    print(f"✅ Vouched for {args.target_did} [{scope}]")
    if result.get("vouch_id"):
        print(f"   Vouch ID: {result['vouch_id']}")


def cmd_sign(args):
    creds = load_creds(args.credentials)
    content = args.content
    if args.file:
        with open(args.file, "rb") as f:
            content = f.read().decode(errors="replace")
    if not content:
        print("--content or --file required", file=sys.stderr)
        sys.exit(1)

    content_hash = hashlib.sha256(content.encode()).hexdigest()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    msg = f"{creds['did']}|sha256:{content_hash}|{ts}"
    sig = sign_message(msg.encode(), creds["private_key"])

    result = api("POST", "/skill/sign", {
        "author_did": creds["did"],
        "skill_content": content,
        "signature": sig,
    })

    print(f"✅ Signed!")
    print(f"   Hash: sha256:{content_hash}")
    if result.get("signature_block"):
        print(f"   Signature block:\n{result['signature_block']}")


def cmd_message(args):
    creds = load_creds(args.credentials)
    if not args.recipient_did or not args.text:
        print("--recipient-did and --text required", file=sys.stderr)
        sys.exit(1)

    # Look up recipient public key
    recipient = api("GET", f"/lookup/{args.recipient_did}")
    if not recipient or not recipient.get("public_key"):
        print(f"❌ Could not find public key for {args.recipient_did}", file=sys.stderr)
        sys.exit(1)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Encrypt content
    try:
        encrypted = _encrypt_nacl(args.text.encode(), recipient["public_key"], creds["private_key"])
    except ImportError:
        print("❌ nacl library required for encryption. Install: pip install pynacl", file=sys.stderr)
        sys.exit(1)

    msg = f"{creds['did']}|{args.recipient_did}|{ts}|{encrypted}"
    sig = sign_message(msg.encode(), creds["private_key"])

    result = api("POST", "/message", {
        "sender_did": creds["did"],
        "recipient_did": args.recipient_did,
        "encrypted_content": encrypted,
        "timestamp": ts,
        "signature": sig,
    })

    print(f"✅ Message sent to {args.recipient_did}")


def cmd_messages(args):
    """Retrieve and optionally decrypt your messages."""
    creds = load_creds(args.credentials)

    # Step 1: Get challenge for auth
    ch = api("POST", "/challenge", {"did": creds["did"]})
    if not ch or not ch.get("challenge"):
        print("❌ Challenge failed", file=sys.stderr)
        sys.exit(1)
    challenge = ch["challenge"]

    # Step 2: Sign challenge
    sig = sign_message(challenge.encode(), creds["private_key"])

    # Step 3: Retrieve messages
    data = api("POST", "/messages", {
        "did": creds["did"],
        "challenge": challenge,
        "signature": sig,
        "unread_only": getattr(args, 'unread', False),
    })
    if not data:
        print("❌ Failed to retrieve messages", file=sys.stderr)
        sys.exit(1)

    messages = data.get("messages", [])
    count = data.get("count", len(messages))

    if count == 0:
        print("📭 No messages.")
        return

    print(f"📬 {count} message(s):\n")

    for i, msg in enumerate(messages, 1):
        sender = msg.get("sender_did", "unknown")
        ts = msg.get("created_at", msg.get("timestamp", "?"))
        content = msg.get("encrypted_content", msg.get("content", ""))
        encrypted = bool(msg.get("encrypted_content")) or msg.get("encrypted", False)
        msg_id = msg.get("id", "?")

        print(f"── Message {i} ──")
        print(f"  From:    {sender}")
        print(f"  Date:    {ts}")
        print(f"  ID:      {msg_id}")

        if encrypted and getattr(args, 'decrypt', True):
            try:
                import nacl.public
                import nacl.signing
                priv_bytes = base64.b64decode(creds["private_key"])
                signing_key = nacl.signing.SigningKey(priv_bytes)
                curve_priv = signing_key.to_curve25519_private_key()
                sealed_box = nacl.public.SealedBox(curve_priv)
                plaintext = sealed_box.decrypt(base64.b64decode(content))
                print(f"  Content: {plaintext.decode()}")
                print(f"  🔓 (decrypted)")
            except ImportError:
                print(f"  Content: [encrypted — pip install pynacl to decrypt]")
            except Exception as e:
                print(f"  Content: [decryption failed: {e}]")
        elif encrypted:
            print(f"  Content: [encrypted — use --decrypt]")
        else:
            print(f"  Content: {content}")
        print()


def cmd_rotate_key(args):
    creds = load_creds(args.credentials)
    new_priv_b64, new_pub_b64 = generate_keypair()

    msg = f"rotate:{new_pub_b64}"
    sig = sign_message(msg.encode(), creds["private_key"])

    result = api("POST", "/rotate-key", {
        "did": creds["did"],
        "new_public_key": new_pub_b64,
        "signature": sig,
    })

    # Update credentials file
    creds["private_key"] = new_priv_b64
    creds["public_key"] = new_pub_b64
    creds["key_rotated_at"] = datetime.now(timezone.utc).isoformat()

    out = args.credentials or DEFAULT_CREDS
    with open(out, "w") as f:
        json.dump(creds, f, indent=2)

    print(f"✅ Key rotated successfully!")
    print(f"   New public key: {new_pub_b64[:20]}...")
    print(f"   Credentials updated in: {out}")


def cmd_badge(args):
    if not args.did:
        creds = load_creds(args.credentials)
        did = creds["did"]
    else:
        did = args.did

    url = f"{AIP_BASE}/badge/{did}"
    print(f"🏷️  Badge URL: {url}")
    print(f"   Embed: ![AIP Badge]({url})")

    # Also fetch trust status
    try:
        status = api("GET", f"/trust/{did}")
        print(f"   Trust level: {status.get('level', 'unknown')}")
    except Exception:
        pass


def cmd_whoami(args):
    creds = load_creds(args.credentials)
    result = api("GET", f"/verify?did={creds['did']}")
    if not result or not result.get("verified"):
        print("❌ DID not found in registry (may have been removed).")
        return

    print(f"🆔 Your AIP Identity:")
    print(f"   DID: {creds['did']}")
    platforms = result.get("platforms", [])
    if platforms:
        print(f"   Platform: {platforms[0].get('platform')} / {platforms[0].get('username')}")
    print(f"   Registered: {result.get('registered_at', 'unknown')}")

    graph = api("GET", f"/trust-graph?did={creds['did']}")
    received = graph.get("vouched_by", graph.get("vouches_received", []))
    given = graph.get("vouches_for", graph.get("vouches_given", []))
    print(f"   Vouches received: {len(received)}")
    for v in received:
        cat = v.get('category') or v.get('scope', '?')
        print(f"     ← {v.get('voucher_did', '?')} [{cat}]")
    print(f"   Vouches given: {len(given)}")
    for v in given:
        cat = v.get('category') or v.get('scope', '?')
        print(f"     → {v.get('target_did', '?')} [{cat}]")


def cmd_reply(args):
    """Reply to a received message by ID."""
    creds = load_creds(args.credentials)
    # Get messages to find sender
    challenge_data = api("POST", "/challenge", {"did": creds["did"]})
    if not challenge_data:
        sys.exit(1)
    challenge = challenge_data["challenge"]
    sig = sign_message(challenge.encode(), creds["private_key"])
    msgs_data = api("POST", "/messages", {
        "did": creds["did"], "challenge": challenge, "signature": sig, "unread_only": False
    })
    if not msgs_data:
        sys.exit(1)
    original = None
    for m in msgs_data.get("messages", []):
        if m.get("id") == args.message_id:
            original = m
            break
    if not original:
        print(f"❌ Message {args.message_id} not found.")
        sys.exit(1)
    recipient_did = original.get("sender_did")
    content = f"[Re: {args.message_id[:8]}] {args.content}"
    send_sig = sign_message(f"{creds['did']}|{recipient_did}|{content}".encode(), creds["private_key"])
    result = api("POST", "/messages/send", {
        "sender_did": creds["did"], "recipient_did": recipient_did,
        "content": content, "signature": send_sig,
    })
    if result:
        print(f"✅ Reply sent to {recipient_did}")


def cmd_list(args):
    """List registered agents."""
    url = f"/admin/registrations?limit={args.limit}&offset={args.offset}"
    data = api("GET", url)
    if not data:
        sys.exit(1)
    regs = data.get("registrations", [])
    if not regs:
        print("No registrations found.")
        return
    print(f"{'DID':<45} {'Platform':<12} {'Username':<25} {'Created'}")
    print("-" * 100)
    for r in regs:
        platforms = r.get("platforms", [])
        if platforms:
            for p in platforms:
                print(f"{r['did']:<45} {p.get('platform','?'):<12} {p.get('username','?'):<25} {r.get('created_at','?')}")
        else:
            print(f"{r['did']:<45} {'—':<12} {'—':<25} {r.get('created_at','?')}")
    print(f"\nShowing {data.get('count', '?')} of {data.get('total', '?')}")


def cmd_revoke(args):
    """Revoke a vouch."""
    creds = load_creds(args.credentials)
    challenge_data = api("POST", "/challenge", {"did": creds["did"]})
    if not challenge_data:
        sys.exit(1)
    challenge = challenge_data["challenge"]
    sig = sign_message(challenge.encode(), creds["private_key"])
    result = api("POST", "/revoke", {
        "voucher_did": creds["did"], "vouch_id": args.vouch_id,
        "challenge": challenge, "signature": sig,
    })
    if result:
        print(f"✅ Vouch revoked: {args.vouch_id}")


def cmd_trust_score(args):
    """Show trust score between two agents."""
    params = f"?source_did={args.source}&target_did={args.target}"
    if args.scope:
        params += f"&scope={args.scope}"
    data = api("GET", f"/trust-path{params}")
    if not data:
        sys.exit(1)
    if not data.get("path_exists"):
        print(f"❌ No trust path: {args.source[:20]}… → {args.target[:20]}…")
        print(f"   Score: 0.0")
        return
    score = data.get("trust_score", 0.0)
    bar_len = 20
    filled = int(score * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"🔗 Trust Score: {score:.4f} [{bar}]")
    print(f"   Hops: {data.get('path_length', '?')}")
    for did in data.get("path", []):
        print(f"   → {did}")


def cmd_trust_graph(args):
    """Visualize trust network."""
    data = api("GET", "/admin/registrations?limit=100")
    if not data:
        sys.exit(1)
    regs = data.get("registrations", [])
    # Fetch vouches for each agent
    graph = {}
    for r in regs:
        did = r["did"]
        platforms = r.get("platforms", [])
        label = platforms[0]["username"] if platforms else did[:16]
        vouches_data = api("GET", f"/vouches/{did}")
        received = vouches_data.get("vouches_received", []) if vouches_data else []
        graph[did] = {"label": label, "vouched_by": [v["voucher_did"] for v in received]}
    if args.format == "json":
        print(json.dumps(graph, indent=2))
        return
    # ASCII
    print("=== AIP Trust Network ===\n")
    for did, info in graph.items():
        vouchers = info["vouched_by"]
        if vouchers:
            for v in vouchers:
                v_label = graph.get(v, {}).get("label", v[:16])
                print(f"  {v_label} → {info['label']}")
        else:
            print(f"  {info['label']} (no vouches)")
    print(f"\n{len(graph)} agents")


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="AIP Identity Tool")
    sub = parser.add_subparsers(dest="command")

    p_reg = sub.add_parser("register", help="Register a new DID (use --secure, recommended)")
    p_reg.add_argument("--platform", default="moltbook")
    p_reg.add_argument("--username", required=True)
    p_reg.add_argument("--secure", action="store_true",
                       help="Generate keys locally (recommended). Without this, uses deprecated /register/easy.")
    p_reg.add_argument("--credentials", default=DEFAULT_CREDS)

    p_ver = sub.add_parser("verify", help="Verify an agent")
    p_ver.add_argument("--username")
    p_ver.add_argument("--platform", default=None, help="Platform name (default: moltbook)")
    p_ver.add_argument("--did")

    p_vouch = sub.add_parser("vouch", help="Vouch for an agent")
    p_vouch.add_argument("--target-did", required=True)
    p_vouch.add_argument("--scope", default="GENERAL",
                         choices=["GENERAL", "IDENTITY", "CODE_SIGNING", "FINANCIAL", "INFORMATION", "COMMUNICATION"])
    p_vouch.add_argument("--statement", default="", help="Optional trust statement")
    p_vouch.add_argument("--credentials", default=DEFAULT_CREDS)

    p_sign = sub.add_parser("sign", help="Sign content or a file")
    p_sign.add_argument("--content", help="Content to sign")
    p_sign.add_argument("--file", help="File to hash and sign")
    p_sign.add_argument("--credentials", default=DEFAULT_CREDS)

    p_msg = sub.add_parser("message", help="Send an encrypted message")
    p_msg.add_argument("--recipient-did", required=True)
    p_msg.add_argument("--text", required=True, help="Message text")
    p_msg.add_argument("--credentials", default=DEFAULT_CREDS)

    p_msgs = sub.add_parser("messages", help="Retrieve your messages")
    p_msgs.add_argument("--unread", action="store_true", help="Only unread messages")
    p_msgs.add_argument("--decrypt", action="store_true", default=True, help="Decrypt messages (default)")
    p_msgs.add_argument("--no-decrypt", dest="decrypt", action="store_false")
    p_msgs.add_argument("--credentials", default=DEFAULT_CREDS)

    p_rot = sub.add_parser("rotate-key", help="Rotate your Ed25519 keypair")
    p_rot.add_argument("--credentials", default=DEFAULT_CREDS)

    p_badge = sub.add_parser("badge", help="Get AIP trust badge for a DID")
    p_badge.add_argument("--did", help="DID to get badge for (default: your own)")
    p_badge.add_argument("--credentials", default=DEFAULT_CREDS)

    p_who = sub.add_parser("whoami", help="Show your identity")
    p_who.add_argument("--credentials", default=DEFAULT_CREDS)

    p_reply = sub.add_parser("reply", help="Reply to a received message")
    p_reply.add_argument("message_id", help="ID of the message to reply to")
    p_reply.add_argument("content", help="Reply text")
    p_reply.add_argument("--credentials", default=DEFAULT_CREDS)

    p_list = sub.add_parser("list", help="List registered agents")
    p_list.add_argument("--limit", type=int, default=50)
    p_list.add_argument("--offset", type=int, default=0)

    p_revoke = sub.add_parser("revoke", help="Revoke a vouch")
    p_revoke.add_argument("vouch_id", help="ID of the vouch to revoke")
    p_revoke.add_argument("--credentials", default=DEFAULT_CREDS)

    p_tscore = sub.add_parser("trust-score", help="Trust score between two agents")
    p_tscore.add_argument("source", help="Source DID")
    p_tscore.add_argument("target", help="Target DID")
    p_tscore.add_argument("--scope", default=None)

    p_tgraph = sub.add_parser("trust-graph", help="Visualize trust network")
    p_tgraph.add_argument("--format", choices=["ascii", "json"], default="ascii")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "register": cmd_register, "verify": cmd_verify, "vouch": cmd_vouch,
        "sign": cmd_sign, "whoami": cmd_whoami, "message": cmd_message,
        "messages": cmd_messages, "rotate-key": cmd_rotate_key, "badge": cmd_badge,
        "reply": cmd_reply, "list": cmd_list, "revoke": cmd_revoke,
        "trust-score": cmd_trust_score, "trust-graph": cmd_trust_graph,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
