#!/usr/bin/env python3
"""Batch seed Mem0 with all key facts."""
import os, sys, time
os.environ.setdefault('QDRANT_HOST', 'qdrant')
os.environ.setdefault('NEO4J_URL', 'bolt://neo4j:7687')
sys.path.insert(0, os.path.dirname(__file__))
from memory_engine import get_memory

facts = [
    "Abidi is an AI founder based in Austin, TX (CST timezone). His handle is @mabidi_eth on X/Twitter.",
    "Abidi's business offers: Voice AI, Business Automations, OpenClaw installations, GHL CRM buildouts, Mobile apps, and Websites.",
    "Naming rule: all product/project names must pass the 5th grader test — if a 5th grader can't understand it, rename it.",
    "GHL x OpenClaw project: AI brain connecting GoHighLevel CRM + Voice AI + Auto-Blog + ClickUp for service businesses. Status: MVP ready.",
    "Target customers for GHL x OpenClaw: service-based businesses with 24/7 lead flow — garage repair, plumbing, HVAC, roofing.",
    "The Synthetic Times: autonomous AI journalist agent covering AI societies, running on a separate VPS connected via Tailscale.",
    "Server infrastructure: Docker on 5.161.185.100, Hetzner CX32 (8GB RAM, 4 CPUs, 150GB disk).",
    "Brain stack: Mem0 + Qdrant (vectors) + Neo4j (knowledge graph) + SQLite (structured data) + Langfuse (observability).",
    "Research-First Rule: NEVER recommend tools from training knowledge alone. Always do deep research first with minimum 3-5 candidates.",
    "FalkorDB lesson: AgxntSix recommended FalkorDB from training memory. Deep research proved Neo4j was objectively better (Mem0 native, bigger ecosystem).",
    "Abidi prefers best-in-class tools, concise answers, and self-sufficiency. No good enough — research first, then decide.",
    "OpenRouter is the single API gateway for all LLM models.",
    "Perplexity for search with 3 tiers: sonar (quick), sonar-pro (research), sonar-reasoning-pro (deep analysis).",
    "Model allocation: Gemini Flash Lite for Mem0 extraction, Haiku 4.5 for cron jobs, Opus 4.6 for main agent conversations.",
]

print(f"Seeding {len(facts)} facts into Mem0...", flush=True)
m = get_memory()
print("Memory initialized.", flush=True)

success = 0
for i, fact in enumerate(facts):
    try:
        t0 = time.time()
        result = m.add(fact, user_id="agxntsix")
        elapsed = time.time() - t0
        success += 1
        print(f"  [{i+1}/{len(facts)}] OK ({elapsed:.1f}s): {fact[:60]}...", flush=True)
    except Exception as e:
        print(f"  [{i+1}/{len(facts)}] FAIL: {e}", flush=True)

print(f"\nDone: {success}/{len(facts)} facts seeded.", flush=True)
