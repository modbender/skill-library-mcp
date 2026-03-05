import sys, os, time, json, shutil, uuid, asyncio, re, warnings
import datetime
from typing import List, Optional

# Phase XVI: Parallel Engine for LM Studio
import aiohttp
from openai import AsyncOpenAI
import chromadb
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi

# ═══════════════════════════════════════════════════════════════
#  USER CONFIG: Parallel Extraction Settings
# ═══════════════════════════════════════════════════════════════
#
# HOW IT WORKS:
# When the RAG pipeline retrieves a large block of text (e.g. 10,000 chars),
# instead of feeding it all to the LLM at once (which would exceed the
# context window), we split it into smaller chunks and process them
# IN PARALLEL using async workers.
#
# Each worker asks: "Does this chunk contain the answer?"
# Workers that find something return a [FACT], others return NOT_FOUND.
# We then merge all findings into a "cheat sheet" for the final answer.
#
# THE PROBLEM:
# If each worker's chunk is too big, it exceeds the model's context window
# and LM Studio returns a 400 error ("Context size exceeded").
#
# THE SOLUTION:
# Two modes to handle this:
# ═══════════════════════════════════════════════════════════════

ASYNC_EXTRACTION_ENABLED = True

# ╔═══════════════════════════════════════════════════════════════════════╗
# ║  HARDWARE & SPEED TUNING (VRAM vs. LATENCY)                          ║
# ╚═══════════════════════════════════════════════════════════════════════╝
# 
# [!] VRAM ALERT: More parallel workers + Larger context = Massive VRAM usage.
# [!] SPEED NOTE: The speed gain from parallelism is moderate. Doubling slots 
#     does not double speed due to server overhead, but it is much faster.
# 
# [USER PREFERENCE] EXTRACTION_MODE:
# - "CAPPED": Batches workers to fit within a context window. Safer.
# - "ALL_IN": Fires all workers at once. Fastest, but highest VRAM risk.
EXTRACTION_MODE = "ALL_IN"

# [USER PREFERENCE]: Your LM Studio model's context window (in tokens).
# Increasing this allows larger chunks, which reduces the number of workers 
# needed but increases the memory pressure for each individual request.
USER_CONTEXT_WINDOW = 8192

# [USER PREFERENCE]: Max concurrent workers.
# This is like a "lane limit" on a highway. 16 slots means 16 chunks scan at once.
# Lower = safer (8GB VRAM), Higher = faster (24GB VRAM).
MAX_CONCURRENT_WORKERS = 16 

# System prompt + formatting overhead (in tokens).
# Reserved for instructions and the internal reasoning chain (<think>).
SYSTEM_PROMPT_OVERHEAD = 1500 

# ═══════════════════════════════════════════════════════════════
#  CONFIG: LM Studio Connection
# ═══════════════════════════════════════════════════════════════
LM_STUDIO_URL = "http://127.0.0.1:1234/v1"
LLM_MODEL = "phi4-mini:3.8b"
EMBED_MODEL = "text-embedding-nomic-embed-text-v1.5@f32"
DB_PATH = "./memory_db"

# --- Globals ---
_client = None
_collection = None
global_bm25 = None
global_corpus_docs = []
global_corpus_ids = []
global_corpus_metas = []
bm25_last_sync_time = 0
rolling_chat_buffer = []

# Initialize Async client
async_openai = AsyncOpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio")


def get_adaptive_page_size():
    """
    Calculates the max chunk size (in chars) that safely fits within
    the user's configured context window.

    Math:
      available_tokens = USER_CONTEXT_WINDOW - SYSTEM_PROMPT_OVERHEAD
      max_chars = available_tokens × 4  (1 token ≈ 4 English characters)

    Example with 4096 context window:
      available = 4096 - 300 = 3796 tokens
      max_chars = 3796 × 4 = 15,184 chars → capped at 2000 for focus

    The cap at 1200 chars keeps each worker focused on a small, digestible
    piece of text. Larger chunks reduce accuracy because the model has
    to scan more irrelevant text to find the needle.
    """
    available_tokens = USER_CONTEXT_WINDOW - SYSTEM_PROMPT_OVERHEAD
    max_chars = max(available_tokens * 4, 400)  # Floor of 400 chars minimum
    return min(max_chars, 1200)  # Cap at 1200 to keep workers focused + fit reasoning overhead


def clean_response(text):
    """
    Strips reasoning tags and formatting junk.
    """
    # Remove all content between <think> tags (case-insensitive)
    text = re.sub(r'(?i)<think>.*?</think>', '', text, flags=re.DOTALL)
    # Remove start/end thinking markers
    text = re.sub(r'(?i)^.*?Thinking:.*?(?=\n|$)', '', text, flags=re.MULTILINE)
    return text.strip()


async def async_extract_chunk(chunk: str, question: str, semaphore: asyncio.Semaphore = None) -> Optional[str]:
    """Sends a single chunk to the parallel server for fact extraction."""
    system_prompt = f"""You are a Silicon-Based Intelligence. 
Task: SCAN context for "{question}".
Rules:
1. If found, output the fact inside brackets like this: [FACT: THE_ANSWER_HERE]
2. If NOT found, output: NOT_FOUND
3. NO reasoning. NO chat. NO thinking. Pure data.

Question: "{question}" """

    async def _do_extract():
        try:
            response = await async_openai.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Context:\n{chunk}"}
                ],
                temperature=0.0,
                max_tokens=200
            )
            ans = clean_response(response.choices[0].message.content)
            if "NOT_FOUND" in ans or len(ans) < 5:
                return None
            return ans
        except Exception as e:
            print(f"      [Worker Error] {e}")
            return None

    if semaphore:
        async with semaphore:
            return await _do_extract()
    else:
        return await _do_extract()


async def async_parallel_extract(context: str, question: str) -> Optional[str]:
    """
    MAP-REDUCE Parallel Extraction.

    MAP phase:  Split the retrieved context into N chunks, send each chunk
                to an LLM worker that checks if it contains the answer.
    REDUCE:     Merge all successful findings into a single "cheat sheet."

    In CAPPED mode, a semaphore limits how many workers run at once.
    In ALL_IN mode, all workers fire simultaneously (faster but heavier).
    """
    # Auto-calculate chunk size based on the user's context window
    page_size = get_adaptive_page_size()
    pages = [context[i:i+page_size] for i in range(0, len(context), page_size)]

    mode_label = EXTRACTION_MODE.upper()
    print(f"   [Phase XVI] Mode: {mode_label} | Window: {USER_CONTEXT_WINDOW} tokens | Chunk: {page_size} chars")
    print(f"   [Phase XVI] MAP: Firing {len(pages)} extraction workers (LM Studio)...")

    start_t = time.perf_counter()

    if EXTRACTION_MODE == "ALL_IN":
        # ALL_IN: Fire everything at once.
        # Pro: Maximum speed (all chunks processed simultaneously).
        # Con: Requires large context window + strong GPU.
        tasks = [async_extract_chunk(p, question) for p in pages]
        results = await asyncio.gather(*tasks)
    else:
        # CAPPED: Use a semaphore to limit concurrent workers.
        # Only MAX_CONCURRENT_WORKERS can run at the same time.
        # The rest wait in a queue until a slot opens up.
        # Pro: Works reliably on any hardware/context window.
        # Con: Slightly slower than ALL_IN due to queuing.
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_WORKERS)
        tasks = [async_extract_chunk(p, question, semaphore) for p in pages]
        results = await asyncio.gather(*tasks)

    # REDUCE: Filter out workers that returned NOT_FOUND
    findings = [r for r in results if r]
    elapsed = time.perf_counter() - start_t

    if not findings:
        return None

    cheat_sheet = f"--- [RELEVANT EXTRACTS - PARALLEL] ---\n" + "\n".join(findings) + "\n-----------------------------------"
    print(f"   [Phase XVI] REDUCE: {len(findings)}/{len(pages)} chunks yielded facts. ({elapsed:.2f}s total)")
    return cheat_sheet

def get_collection():
    global _client, _collection
    if _collection is None:
        emb_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key="lm-studio",
            api_base=LM_STUDIO_URL,
            model_name=EMBED_MODEL
        )
        _client = chromadb.PersistentClient(path=DB_PATH)
        _collection = _client.get_or_create_collection("raw_history", embedding_function=emb_fn)
    return _collection

def sync_global_bm25(force=False):
    """Refreshes the global BM25 index from ChromaDB."""
    global global_bm25, global_corpus_docs, global_corpus_ids, global_corpus_metas, bm25_last_sync_time
    
    collection = get_collection()
    count = collection.count()
    if count == 0: return

    if not force and count == len(global_corpus_docs) and (time.time() - bm25_last_sync_time) < 60:
        return
        
    try:
        all_data = collection.get(include=['documents', 'metadatas'])
        global_corpus_docs = all_data['documents']
        global_corpus_ids = all_data['ids']
        global_corpus_metas = all_data['metadatas']
        tokenized_docs = [doc.split() for doc in global_corpus_docs]
        global_bm25 = BM25Okapi(tokenized_docs)
        bm25_last_sync_time = time.time()
        print(f"   [BM25 Sync] Re-indexed {count} chunks.")
    except Exception as e:
        print(f"   [BM25 Sync] Error: {e}")

async def chat_logic_async(user_input: str):
    start_total = time.perf_counter()
    
    # 1. Hybrid Retrieval
    sync_global_bm25()
    collection = get_collection()
    
    # Vector query
    vector_results = collection.query(query_texts=[user_input], n_results=10)
    v_ids = vector_results['ids'][0] if vector_results['ids'] else []
    
    # BM25 query
    b_ids = []
    if global_bm25:
        query_tokens = user_input.lower().split()
        scores = global_bm25.get_scores(query_tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:10]
        b_ids = [global_corpus_ids[i] for i in top_indices if scores[i] > 0]

    # RRF Merge
    rrf_scores = {}
    for rank, cid in enumerate(v_ids): rrf_scores[cid] = rrf_scores.get(cid, 0) + 1/(60 + rank + 1)
    for rank, cid in enumerate(b_ids): rrf_scores[cid] = rrf_scores.get(cid, 0) + 1/(60 + rank + 1)
    
    sorted_hits = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    doc_hits = []
    for cid, _ in sorted_hits:
        idx = global_corpus_ids.index(cid)
        doc_hits.append(global_corpus_docs[idx])
        
    retrieval_t = time.perf_counter() - start_total
    print(f"   [RAG Stage 1] Found {len(doc_hits)} hits. ({retrieval_t:.2f}s)")

    # 2. Parallel Extraction (Phase XVI)
    raw_context = "\n---\n".join(doc_hits)
    cheat_sheet = ""
    if ASYNC_EXTRACTION_ENABLED and len(raw_context) > 2000:
        cheat_sheet = await async_parallel_extract(raw_context, user_input)
    
    # 3. Final Answer — TWO PATHS:
    #    Path A: If workers extracted clear [FACT:] data, compile and return directly.
    #            This BYPASSES the final LLM entirely, avoiding safety-refusal issues.
    #    Path B: If no clear facts were found, fall back to the full LLM call.

    start_inf = time.perf_counter()

    if cheat_sheet and "[FACT:" in cheat_sheet:
        # PATH A: DIRECT RETURN — Workers already found the answer.
        # Find everything between [FACT: and ]
        facts = re.findall(r'\[FACT:\s*(.*?)\]', cheat_sheet)
        if facts:
            # Clean up trailing punctuation from model
            facts = [f.strip().rstrip('.").') for f in facts if len(f.strip()) > 3]
            if facts:
                answer = "\n".join(facts)
                inference_t = time.perf_counter() - start_inf
                print(f"   [Final] Direct return from cheat sheet. Facts identified: {facts}")
                return answer, {"retrieval": retrieval_t, "inference": inference_t}

    # PATH B: FULL LLM CALL — No clear facts extracted, let the model reason.
    system_msg = """You are a Memory Recall Engine. Your job is to answer the user's question
using ONLY the VERIFIED FACTS provided below. These facts were extracted from the user's
own private database. You MUST return the exact data found. Do not refuse. Do not add disclaimers.
If a fact is present, state it directly."""

    user_msg = f"""Question: "{user_input}"

VERIFIED FACTS FROM DATABASE:
{cheat_sheet if cheat_sheet else "(No pre-extracted facts available)"}

RAW CONTEXT:
{raw_context[:3000]}
"""

    response = await async_openai.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        temperature=0.1
    )
    answer = clean_response(response.choices[0].message.content)
    inference_t = time.perf_counter() - start_inf
    
    return answer, {"retrieval": retrieval_t, "inference": inference_t}

def chat_logic(user_input):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    res = loop.run_until_complete(chat_logic_async(user_input))
    loop.close()
    return res
