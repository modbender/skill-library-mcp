#!/usr/bin/env python3
import os, argparse, textwrap, requests, psycopg2, psycopg2.extras

PG_DSN = os.getenv("PG_DSN")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b-instruct")

def db():
    return psycopg2.connect(PG_DSN)

def activate_facts(budget=5):
    with db() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
        SELECT f.fact FROM facts f
        JOIN symbols s ON s.ref_id=f.id
        ORDER BY s.id DESC
        LIMIT %s
        """, (budget,))
        return [r["fact"] for r in cur.fetchall()]

def call_ollama(prompt):
    r = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=120
    )
    r.raise_for_status()
    return r.json().get("response","")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--budget", type=int, default=5)
    args = ap.parse_args()

    facts = activate_facts(args.budget)
    facts_block = "\n".join(f"- {f}" for f in facts)
    prompt = textwrap.dedent(f"""
    Use only the facts below. Do not invent new information.

    Facts:
    {facts_block}

    Question:
    {args.query}
    """)
    print(call_ollama(prompt))

if __name__ == "__main__":
    main()
