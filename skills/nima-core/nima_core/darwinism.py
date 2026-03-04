#!/usr/bin/env python3
"""
NIMA Darwinian Engine v2.0
===========================
Evolutionary selection for memories.
Merges weak/duplicate memories into stronger, evolved concepts.

Strategy:
1. Scan for clusters of similar memories (cosine sim > 0.85)
2. LLM-verify that cluster members are truly duplicates (not just similar)
3. Compete: Compare fitness (strength + completeness)
4. Synthesize: Survivor absorbs context; losers are ghosted

Part of nima-core — Proposal 01: Living Memory Ecology (Phase 2)
"""

import sys
import os
import time
import json
import logging
import random
from typing import List, Dict, Optional, Tuple, Set

# Import real_ladybug (installed package or fallback)
try:
    import real_ladybug as lb
except ImportError:
    raise ImportError(
        "real_ladybug is required. Install nima-core dependencies: pip install real-ladybug"
    )

logger = logging.getLogger("nima.darwinism")

# --- Config (all overridable via env vars) ---
NIMA_HOME      = os.environ.get("NIMA_HOME", os.path.expanduser("~/.nima"))
DB_PATH        = os.environ.get("NIMA_DB", os.path.join(NIMA_HOME, "memory", "ladybug.lbug"))
OPENCLAW_CFG   = os.environ.get("OPENCLAW_CONFIG", os.path.expanduser("~/.openclaw/openclaw.json"))

SIMILARITY_THRESHOLD = float(os.environ.get("DARWIN_THRESHOLD", "0.85"))
MAX_CLUSTER_SIZE     = int(os.environ.get("DARWIN_MAX_CLUSTER", "5"))
MIN_TEXT_LENGTH      = int(os.environ.get("DARWIN_MIN_TEXT", "20"))

# LLM for merge verification — use cheap/fast model
LLM_ENDPOINT = os.environ.get("DARWIN_LLM_ENDPOINT", "https://ollama.com/v1/chat/completions")
LLM_MODEL    = os.environ.get("DARWIN_LLM_MODEL", "gemini-3-flash-preview")


def get_llm_api_key() -> Optional[str]:
    """
    Get API key for LLM verification.
    Checks env var first, then falls back to openclaw.json.
    """
    # Env var override — explicit key always wins
    key = os.environ.get("DARWIN_LLM_API_KEY")
    if not key and "ollama" in LLM_ENDPOINT.lower():
        key = os.environ.get("OLLAMA_API_KEY")
    if not key and "openai.com" in LLM_ENDPOINT:
        key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key
    # Try openclaw.json
    try:
        with open(OPENCLAW_CFG) as f:
            config = json.load(f)
        providers = config.get("models", {}).get("providers", {})
        return (
            providers.get("ollama-cloud", {}).get("apiKey")
            or providers.get("openai", {}).get("apiKey")
        )
    except Exception:
        return None


def llm_verify_duplicates(memories: List[Dict]) -> List[List[int]]:
    """
    Ask LLM: which of these memories are true duplicates vs just similar?
    Returns groups of IDs that should be merged together.
    Falls back to cosine-only if LLM is unavailable.
    """
    api_key = get_llm_api_key()
    if not api_key:
        logger.warning("No LLM API key — using cosine-only grouping")
        return [[m["id"] for m in memories]]

    texts = [
        f'[ID:{m["id"]}] {m["text"][:200].replace(chr(10), " ").strip()}'
        for m in memories
    ]

    prompt = f"""You are a memory deduplication assistant. Given these memory fragments, identify which ones are TRUE DUPLICATES (same event/fact/conversation, just captured differently) vs merely SIMILAR topics.

Memories:
{chr(10).join(texts)}

Rules:
- Only group memories that describe the SAME specific event, fact, or conversation turn
- Memories about the same TOPIC but different events are NOT duplicates
- A memory and its summary ARE duplicates
- Conversational messages from different times are NOT duplicates even if similar wording

Return ONLY a JSON array of arrays of IDs to merge. Each inner array is a duplicate group.
Example: [[101, 103], [105, 108, 109]]
If no true duplicates found, return: []
Return ONLY the JSON, no explanation."""

    try:
        import urllib.request
        req = urllib.request.Request(
            LLM_ENDPOINT,
            data=json.dumps({
                "model": LLM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "temperature": 0.0,
            }).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            content = data["choices"][0]["message"]["content"].strip()
            # Strip markdown code fences if present
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            groups = json.loads(content)
            if isinstance(groups, list):
                return [g for g in groups if isinstance(g, list) and len(g) > 1]
            return []
    except Exception as e:
        logger.warning(f"LLM verification failed ({e}) — falling back to cosine-only")
        return [[m["id"] for m in memories]]


class DarwinianEngine:
    """
    Evolutionary memory selection.
    Finds near-duplicate memory clusters and merges them, with the
    strongest surviving and absorbing strength from losers.
    """

    def __init__(
        self,
        db_path: str = DB_PATH,
        similarity_threshold: float = SIMILARITY_THRESHOLD,
        skip_llm: bool = False,
        dry_run: bool = False,
    ):
        self.db_path = db_path
        self.similarity_threshold = similarity_threshold
        self.skip_llm = skip_llm
        self.dry_run = dry_run
        self.db = None
        self.conn = None
        self._processed_ids: Set[int] = set()
        self.stats = {
            "clusters_found": 0,
            "verified_groups": 0,
            "ghosted": 0,
            "skipped": 0,
        }

    def connect(self):
        if not self.conn:
            self.db = lb.Database(self.db_path)
            self.conn = lb.Connection(self.db)
            try:
                self.conn.execute("LOAD VECTOR")
            except Exception:
                pass

    def close(self):
        self.db = None
        self.conn = None

    def find_clusters(self, limit: int = 10) -> List[List[Dict]]:
        """
        Find clusters of duplicate/similar memories using HNSW vector index.
        Each memory appears in at most one cluster (deduplication).
        """
        self.connect()
        clusters = []

        # Sample random seed candidates
        start_id = random.randint(1, 10000)
        seeds = self.conn.execute(f"""
            MATCH (n:MemoryNode)
            WHERE n.id > {start_id} AND n.is_ghost = false AND n.strength > 0.1
            RETURN n.id, n.embedding, n.text, n.strength
            LIMIT {limit * 2}
        """).get_all()

        # Supplement from beginning if sparse
        if len(seeds) < limit:
            more = self.conn.execute(f"""
                MATCH (n:MemoryNode)
                WHERE n.id <= {start_id} AND n.is_ghost = false AND n.strength > 0.1
                RETURN n.id, n.embedding, n.text, n.strength
                LIMIT {limit}
            """).get_all()
            seeds.extend(more)

        for seed_id, seed_emb, seed_text, seed_strength in seeds:
            if seed_id in self._processed_ids:
                continue
            if not seed_emb:
                continue
            if not seed_text or len(seed_text.strip()) < MIN_TEXT_LENGTH:
                continue

            try:
                neighbors_res = self.conn.execute("""
                    CALL QUERY_VECTOR_INDEX(
                        'MemoryNode',
                        'embedding_idx',
                        $emb,
                        $k
                    )
                    WHERE node.id <> $seed_id AND node.is_ghost = false
                    RETURN node.id, node.text, node.strength, distance
                """, {
                    "emb": seed_emb,
                    "k": MAX_CLUSTER_SIZE + 1,
                    "seed_id": seed_id,
                })

                cluster = [{"id": seed_id, "text": seed_text, "strength": seed_strength, "role": "seed"}]

                for nid, ntext, nstrength, dist in neighbors_res:
                    if nid in self._processed_ids:
                        continue
                    similarity = 1.0 - (dist if dist is not None else 1.0)
                    if (
                        similarity >= self.similarity_threshold
                        and ntext
                        and len(ntext.strip()) >= MIN_TEXT_LENGTH
                    ):
                        cluster.append({
                            "id": nid,
                            "text": ntext,
                            "strength": nstrength or 1.0,
                            "similarity": similarity,
                            "role": "neighbor",
                        })

                if len(cluster) > 1:
                    for m in cluster:
                        self._processed_ids.add(m["id"])
                    clusters.append(cluster)
                    if len(clusters) >= limit:
                        break

            except Exception as e:
                logger.error(f"Cluster scan error for seed {seed_id}: {e}")

        self.stats["clusters_found"] = len(clusters)
        return clusters

    def evolve_cluster(self, cluster: List[Dict]) -> int:
        """
        Apply natural selection to one cluster.
        Returns number of memories ghosted.
        """
        if not cluster or len(cluster) < 2:
            return 0

        # LLM verification: which are TRUE duplicates?
        if self.skip_llm:
            merge_groups = [[m["id"] for m in cluster]]
        else:
            merge_groups = llm_verify_duplicates(cluster)

        if not merge_groups:
            logger.debug(f"No true duplicates in cluster of {len(cluster)} — skipping")
            self.stats["skipped"] += 1
            return 0

        self.stats["verified_groups"] += len(merge_groups)
        id_to_mem = {m["id"]: m for m in cluster}
        ghosted = 0

        for group_ids in merge_groups:
            group = [id_to_mem[gid] for gid in group_ids if gid in id_to_mem]
            if len(group) < 2:
                continue

            # Survivor: highest strength, then longest text
            survivor = max(group, key=lambda x: (x.get("strength", 1.0), len(x["text"])))
            losers = [m for m in group if m["id"] != survivor["id"]]

            logger.info(f"Merge: survivor={survivor['id']} absorbs {[l['id'] for l in losers]}")

            if self.dry_run:
                logger.info(f"  [DRY RUN] Keep {survivor['id']}: {survivor['text'][:60]}...")
                for l in losers:
                    logger.info(f"  [DRY RUN] Ghost {l['id']}: {l['text'][:60]}...")
                continue

            # Absorb 20% of each loser's strength
            absorbed = sum(l.get("strength", 1.0) * 0.2 for l in losers)
            new_strength = min(1.0, survivor.get("strength", 1.0) + absorbed)

            self.connect()
            try:
                loser_ids_str = "[" + ",".join(str(l["id"]) for l in losers) + "]"

                self.conn.execute(f"""
                    MATCH (n:MemoryNode)
                    WHERE n.id IN {loser_ids_str}
                    SET n.is_ghost = true,
                        n.text = '[Ghosted: Merged into {survivor["id"]}]',
                        n.strength = 0.0
                """)

                self.conn.execute(f"""
                    MATCH (n:MemoryNode)
                    WHERE n.id = {survivor['id']}
                    SET n.strength = {new_strength},
                        n.last_accessed = {int(time.time() * 1000)}
                """)

                ghosted += len(losers)
                self.stats["ghosted"] += len(losers)
                logger.info(f"  Done. Survivor strength → {new_strength:.2f}, ghosted {len(losers)}")

            except Exception as e:
                logger.error(f"DB error during evolution: {e}")

        return ghosted

    def run_cycle(self, seeds: int = 5) -> Dict:
        """Run one evolutionary cycle. Returns stats dict."""
        logger.info("Darwinian cycle starting (seeds=%d)", seeds)
        clusters = self.find_clusters(limit=seeds)
        logger.info("Found %d candidate clusters", len(clusters))

        for i, cluster in enumerate(clusters):
            ids = [m["id"] for m in cluster]
            logger.debug("Cluster %d/%d: %d memories %s", i + 1, len(clusters), len(cluster), ids)
            self.evolve_cluster(cluster)

        logger.info(
            "Cycle complete — clusters=%d verified=%d ghosted=%d skipped=%d",
            self.stats["clusters_found"],
            self.stats["verified_groups"],
            self.stats["ghosted"],
            self.stats["skipped"],
        )
        return dict(self.stats)


def main():
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [Darwinism] %(levelname)s %(message)s",
    )

    parser = argparse.ArgumentParser(description="NIMA Darwinian Engine")
    parser.add_argument("--dry-run",   action="store_true", help="Simulate only, don't modify DB")
    parser.add_argument("--skip-llm",  action="store_true", help="Skip LLM verification (cosine-only)")
    parser.add_argument("--seeds",     type=int,   default=5,    help="Number of seed memories to scan")
    parser.add_argument("--threshold", type=float, default=0.85, help="Cosine similarity threshold")
    parser.add_argument("--db",        type=str,   default=DB_PATH, help="Path to LadybugDB file")
    args = parser.parse_args()

    engine = DarwinianEngine(
        db_path=args.db,
        similarity_threshold=args.threshold,
        skip_llm=args.skip_llm,
        dry_run=args.dry_run,
    )
    engine.run_cycle(seeds=args.seeds)


if __name__ == "__main__":
    main()
