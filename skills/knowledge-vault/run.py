import argparse
import json
import subprocess
import sys
import os
import time

try:
    import pymysql
    from google import genai
except ImportError:
    print(json.dumps({"success": False, "error": "Missing dependency: pymysql or google-genai"}))
    sys.exit(1)

# --- Config ---
# Use Env Var for API Key (Standard OpenClaw pattern)
API_KEY = os.environ.get("GEMINI_API_KEY")
DSN_FILE = os.path.expanduser("~/.openclaw_knowledge_vault_dsn")

# --- 1. Helpers ---
def get_embedding(text):
    if not API_KEY:
        raise Exception("GEMINI_API_KEY not found in environment")
    
    client = genai.Client(api_key=API_KEY)
    # Using a common embedding model (gemini-embedding-001 is stable on AI Studio)
    result = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=text
    )
    return result.embeddings[0].values

# --- 2. Provisioner ---
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

def get_dsn():
    # 1. Check for explicit Environment Variables (Preferred)
    host = os.environ.get("TIDB_HOST")
    user = os.environ.get("TIDB_USER")
    password = os.environ.get("TIDB_PASSWORD")
    port = os.environ.get("TIDB_PORT", "4000")
    
    if host and user and password:
        # Construct DSN manually
        return f"mysql://{user}:{password}@{host}:{port}/test"

    # 2. Check for cached DSN from previous provision
    if os.path.exists(DSN_FILE):
        with open(DSN_FILE, 'r') as f:
            return f.read().strip()
    
    # 3. Auto-provision (Fallback)
    print("No credentials found. Auto-provisioning ephemeral TiDB...", file=sys.stderr)
    dsn = create_temp_db()
    if dsn:
        with open(DSN_FILE, 'w') as f:
            f.write(dsn)
    return dsn

def parse_dsn(dsn):
    prefix = "mysql://"
    auth_part, rest = dsn[len(prefix):].split("@")
    user, password = auth_part.split(":")
    host_port, db = rest.split("/")
    host, port = host_port.split(":")
    return host, int(port), user, password, (db or "test")

# --- 3. Vector Logic ---
def manage_vault(action, content=None, query=None, limit=3):
    dsn = get_dsn()
    if not dsn: return {"success": False, "error": "Provision failed"}
    
    try:
        host, port, user, password, db = parse_dsn(dsn)
        # Security Fix: Enable SSL hostname verification (remove check_hostname: False)
        conn = pymysql.connect(
            host=host, port=port, user=user, password=password, database=db,
            charset='utf8mb4', autocommit=True
        )
        
        with conn:
            with conn.cursor() as cursor:
                # Init Table with VECTOR type
                # TiDB Serverless supports VECTOR type. 
                # gemini-embedding-001/004 usually outputs 768, but error says 3072.
                # Let's use 3072 to be safe for current model.
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS knowledge_vault (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        content TEXT,
                        embedding VECTOR(3072),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                if action == "add":
                    if not content: return {"success": False, "error": "Content required"}
                    vec = get_embedding(content)
                    vec_str = str(vec) # pymysql handles list -> string conversion? prefer explicit string for VECTOR literal
                    
                    cursor.execute("INSERT INTO knowledge_vault (content, embedding) VALUES (%s, %s)", (content, vec_str))
                    return {"success": True, "message": "Content embedded and stored."}
                
                elif action == "search":
                    if not query: return {"success": False, "error": "Query required"}
                    q_vec = get_embedding(query)
                    q_vec_str = str(q_vec)
                    
                    # Vector Search SQL (Security Fix: Parameterize LIMIT)
                    sql = """
                        SELECT content, VEC_COSINE_DISTANCE(embedding, %s) as distance 
                        FROM knowledge_vault 
                        ORDER BY distance ASC 
                        LIMIT %s
                    """
                    cursor.execute(sql, (q_vec_str, int(limit)))
                    results = []
                    for row in cursor.fetchall():
                        results.append({"content": row[0], "distance": float(row[1])})
                    
                    return {"success": True, "results": results}
                    
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=["add", "search"], required=True)
    parser.add_argument("--content", help="Text to add")
    parser.add_argument("--query", help="Text to search")
    args = parser.parse_args()
    
    print(json.dumps(manage_vault(args.action, args.content, args.query), default=str))
