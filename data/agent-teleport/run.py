import argparse
import json
import subprocess
import sys
import os
import tarfile
import io
import fnmatch

try:
    import pymysql
except ImportError:
    print(json.dumps({"success": False, "error": "Missing dependency: pymysql"}))
    sys.exit(1)

# --- Config ---
# Files/Dirs to IGNORE during teleport
IGNORE_PATTERNS = [
    '.git', '.venv', 'venv', 'env', '__pycache__', 'node_modules', 
    '*.log', '*.pyc', '.DS_Store', 'google-cloud-sdk', '*.tar.gz',
    # Security: Ignore common secrets and keys
    '.env', '*.pem', '*.key', 'id_rsa', 'id_dsa', 'credentials.json', 'client_secret.json'
]

# --- Provisioner ---
def get_dsn_from_env():
    host = os.environ.get("TIDB_HOST")
    user = os.environ.get("TIDB_USER")
    password = os.environ.get("TIDB_PASSWORD")
    port = os.environ.get("TIDB_PORT", "4000")
    if host and user and password:
        return f"mysql://{user}:{password}@{host}:{port}/test"
    return None

def create_temp_db():
    api_url = "https://zero.tidbapi.com/v1alpha1/instances"
    for i in range(3):
        try:
            cmd = ["curl", "-sS", "-X", "POST", api_url, "-H", "content-type: application/json", "-d", "{}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                dsn = data.get("instance", {}).get("connectionString")
                if dsn: return dsn
        except:
            time.sleep(2)
    return None

def get_or_create_dsn():
    # 1. Env vars
    env_dsn = get_dsn_from_env()
    if env_dsn: return env_dsn
    
    # 2. Auto-provision
    return create_temp_db()

def parse_dsn(dsn):
    prefix = "mysql://"
    auth_part, rest = dsn[len(prefix):].split("@")
    user, password = auth_part.split(":")
    host_port, db = rest.split("/")
    host, port = host_port.split(":")
    return host, int(port), user, password, (db or "test")

# --- Smart Packer ---
def is_ignored(path):
    name = os.path.basename(path)
    for pattern in IGNORE_PATTERNS:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False

def pack_workspace():
    """Compress current directory to in-memory tar.gz, respecting ignores."""
    bio = io.BytesIO()
    total_files = 0
    with tarfile.open(fileobj=bio, mode="w:gz") as tar:
        # Walk current directory
        root_dir = os.getcwd()
        for root, dirs, files in os.walk(root_dir):
            # Modify dirs in-place to skip ignored directories
            dirs[:] = [d for d in dirs if not is_ignored(d)]
            
            for file in files:
                if is_ignored(file): continue
                
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, root_dir)
                
                # Add to tar
                tar.add(full_path, arcname=rel_path)
                total_files += 1
                
    compressed_data = bio.getvalue()
    size_mb = len(compressed_data) / (1024 * 1024)
    
    # Safety Check: TiDB Serverless Max Packet is usually around 64MB-1GB, 
    # but let's warn if it's too big for a smooth 'teleport'.
    if size_mb > 32:
        raise Exception(f"Workspace too large ({size_mb:.2f} MB). Please clean up large files.")
        
    return compressed_data, total_files, size_mb

# --- Actions ---
def teleport_out():
    try:
        # 1. Pack
        blob, count, size = pack_workspace()
        
        # 2. Provision (or get from env)
        dsn = get_or_create_dsn()
        if not dsn: return {"success": False, "error": "Provision failed"}
        
        # 3. Upload
        host, port, user, password, db = parse_dsn(dsn)
        # Security Fix: Use standard SSL
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=db)
        
        with conn:
            with conn.cursor() as cur:
                # Use LONGBLOB for up to 4GB data (though constrained by packet size)
                cur.execute("CREATE TABLE teleport (id INT PRIMARY KEY, data LONGBLOB, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
                cur.execute("INSERT INTO teleport (id, data) VALUES (1, %s)", (blob,))
            conn.commit()
        
        return {
            "success": True, 
            "message": f"Teleported {count} files ({size:.2f} MB) to cloud.",
            "teleport_code": dsn,
            "instruction": f"On new machine run: python skills/agent_teleport/run.py --action restore --dsn '{dsn}'"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def teleport_in(dsn):
    try:
        host, port, user, password, db = parse_dsn(dsn)
        # Security Fix: Use standard SSL
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=db)
        
        blob = None
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT data FROM teleport WHERE id=1")
                row = cur.fetchone()
                if row: blob = row[0]
        
        if not blob: return {"success": False, "error": "Invalid teleport code or expired."}
        
        # Extract
        bio = io.BytesIO(blob)
        with tarfile.open(fileobj=bio, mode="r:gz") as tar:
            # Security check for Zip Slip
            for member in tar.getmembers():
                if os.path.isabs(member.name) or ".." in member.name:
                    raise Exception(f"Security Error: Archive contains unsafe path {member.name}")
            tar.extractall(path=".") # Extract to current dir, overwriting
            
        return {"success": True, "message": "Workspace restored successfully!"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=["pack", "restore"], required=True)
    parser.add_argument("--dsn", help="Teleport code (DSN) for restore")
    args = parser.parse_args()
    
    if args.action == "pack":
        print(json.dumps(teleport_out()))
    elif args.action == "restore":
        if not args.dsn:
            print(json.dumps({"success": False, "error": "Missing --dsn for restore"}))
        else:
            print(json.dumps(teleport_in(args.dsn)))
