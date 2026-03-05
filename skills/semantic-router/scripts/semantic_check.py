#!/usr/bin/env python3
"""
Semantic Router - 可配置的语义检查与模型路由脚本
支持从配置文件读取模型池和任务类型
支持自动模型切换 (--execute / -e)
"""

import json
import sys
import os
import subprocess
import argparse
from datetime import datetime

# ── Force offline mode for HuggingFace BEFORE any HF imports ──────────────
# The local embedding model is fully cached; no network access needed.
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'

# Keep proxy envs by default (avoid side effects on sibling capabilities).
# Explicitly disable with: SEMANTIC_CHECK_DISABLE_PROXY=1
if os.environ.get('SEMANTIC_CHECK_DISABLE_PROXY') == '1':
    for _proxy_key in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY',
                        'http_proxy', 'https_proxy', 'all_proxy'):
        os.environ.pop(_proxy_key, None)

# 获取脚本目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 配置目录：先检查 ~/.openclaw/workspace/.lib，再检查脚本同目录
CONFIG_DIR = os.path.expanduser('~/.openclaw/workspace/.lib')
if not os.path.exists(os.path.join(CONFIG_DIR, 'pools.json')):
    CONFIG_DIR = SCRIPT_DIR

def load_json(filename, default=None):
    """加载 JSON 配置文件"""
    path = os.path.join(CONFIG_DIR, filename)
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load {filename}: {e}", file=sys.stderr)
    return default or {}

def _sanitize_context_text(text: str) -> str:
    """清洗上下文文本，降低 envelope/声明噪声。"""
    if not text:
        return ""

    cleaned = unwrap_semantic_router_envelope(text).strip()
    lines = []
    for raw in cleaned.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("【语义检查】"):
            continue
        if line.startswith("Conversation info"):
            continue
        if line.startswith("Replied message"):
            continue
        lines.append(line)

    return "\n".join(lines).strip()


def _select_context_layers(messages: list[str], limit: int) -> list[str]:
    """分层窗口：近窗 + 中窗 + 远窗，缓解“只看最近几条”盲区。"""
    if not messages or limit <= 0:
        return []
    if len(messages) <= limit:
        return messages[:limit]

    near_n = min(4, limit)
    far_n = min(2, max(0, limit - near_n))
    mid_n = max(0, limit - near_n - far_n)

    near = messages[:near_n]
    pool = messages[near_n: max(near_n, len(messages) - far_n)]
    far = messages[-far_n:] if far_n > 0 else []

    mid = []
    if mid_n > 0 and pool:
        step = max(1, len(pool) // mid_n)
        mid = [pool[i] for i in range(0, len(pool), step)][:mid_n]

    layered = near + mid + far

    # 保序去重
    seen = set()
    out = []
    for m in layered:
        key = m.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(m)
        if len(out) >= limit:
            break

    return out


def get_recent_messages(limit: int = 9, exclude_input: str = None, session_key: str = None) -> list:
    """从会话 jsonl 获取用户上下文（会话隔离 + 分层窗口）。"""
    import glob

    sessions_dir = os.path.expanduser('~/.openclaw/agents/main/sessions')

    target_key = (session_key or '').strip()
    if target_key:
        jsonl_files = [os.path.join(sessions_dir, f"{target_key}.jsonl")]
    else:
        jsonl_files = glob.glob(f"{sessions_dir}/*.jsonl")
        jsonl_files.sort(key=os.path.getmtime, reverse=True)
        jsonl_files = jsonl_files[:1]

    raw_user_messages = []
    skipped_self = False

    for jsonl_file in jsonl_files:
        if not os.path.exists(jsonl_file):
            continue
        try:
            with open(jsonl_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            for line in reversed(lines[-400:]):
                try:
                    data = json.loads(line)
                    msg = data.get('message', {})
                    role = msg.get('role', '')
                    content_list = msg.get('content', [])

                    if role != 'user' or not content_list:
                        continue

                    content = content_list[0].get('text', '')
                    if not content:
                        continue

                    if exclude_input and not skipped_self:
                        content_s = content.strip()
                        ex_raw = exclude_input.strip()
                        ex_unwrapped = unwrap_semantic_router_envelope(exclude_input).strip() if exclude_input else ""
                        ex_sanitized = _sanitize_context_text(exclude_input).strip() if exclude_input else ""
                        if content_s in {ex_raw, ex_unwrapped, ex_sanitized}:
                            skipped_self = True
                            continue

                    cleaned = _sanitize_context_text(content)
                    if cleaned:
                        raw_user_messages.append(cleaned)

                    if len(raw_user_messages) >= max(limit * 4, 24):
                        break
                except Exception:
                    continue
            break
        except Exception:
            continue

    return _select_context_layers(raw_user_messages, limit)

# 加载配置
MODEL_POOLS = load_json('pools.json', {})
TASK_PATTERNS = load_json('tasks.json', {})

# 备用硬编码（配置文件不存在时）
if not MODEL_POOLS:
    MODEL_POOLS = {
        "Intelligence": {"name": "智能池", "primary": "openai-codex/gpt-5.3-codex", "fallback_1": "kimi-k2.5", "fallback_2": "zai/glm-5"},
        "Highspeed": {"name": "高速池", "primary": "openai/gpt-4o-mini", "fallback_1": "glm-4.7-flashx", "fallback_2": "zai/glm-5"},
        "Humanities": {"name": "人文池", "primary": "openai/gpt-4o", "fallback_1": "kimi-k2.5", "fallback_2": "zai/glm-5"}
    }

if not TASK_PATTERNS:
    TASK_PATTERNS = {
        "continue": {"keywords": ["继续", "接着"], "pool": None, "action": "延续"},
        "development": {"keywords": ["开发", "写代码"], "pool": "Intelligence", "action": "执行开发任务"},
    }

# 指示词配置
CONTINUATION_INDICATORS = {
    # 仅保留高置信“承接语”，移除低信息量代词/连接词，降低误 continue
    "pronouns": ["这个问题", "那个问题", "这件事", "那件事"],
    "possessives": ["你说的", "你提的", "你建议的", "刚说的", "上面说的"],
    "supplements": ["再补充", "继续补充", "补充一点", "在此基础上"],
    "confirmations": ["对的", "是的", "同意", "就这样"],
    "references": ["按照", "根据", "按你", "用你", "基于刚才"]
}

import re as _re

# ── System Message Filter (v7.4) ──────────────────────────────────────────
# System-level messages (heartbeat polls, cron events, slash commands,
# "continue where you left off", etc.) should NOT be treated as user topic
# input for context relevance scoring.  They are either:
#   - Transparent signals → force "continue" (no model switch, no /new)
#   - Internal machinery → skip semantic scoring entirely
#
# This filter runs BEFORE keyword/indicator/embedding checks.

# Regex patterns that identify system / internal messages
_SYSTEM_MESSAGE_PATTERNS: list[_re.Pattern] = [
    # Heartbeat poll prompt (exact or prefix)
    _re.compile(r'^Read HEARTBEAT\.md', _re.IGNORECASE),
    _re.compile(r'^Heartbeat\b', _re.IGNORECASE),
    # OpenClaw internal: "continue where you left off" variants
    _re.compile(r'^continue\s+where\s+you\s+left', _re.IGNORECASE),
    _re.compile(r'^pick\s+up\s+where', _re.IGNORECASE),
    _re.compile(r'^resume\s+(the\s+)?(previous|last|prior)', _re.IGNORECASE),
    # Slash commands (e.g. /new, /model, /status, /help, /reasoning, etc.)
    _re.compile(r'^/[a-zA-Z]'),
    # Cron event system messages
    _re.compile(r'^\[cron:', _re.IGNORECASE),
    _re.compile(r'^\[System\s+Message\]', _re.IGNORECASE),
    # Subagent completion notifications
    _re.compile(r'^\[Subagent\b', _re.IGNORECASE),
]


def is_system_message(text: str) -> bool:
    """
    Return True if the message is a system/internal signal that should
    bypass semantic topic detection and be treated as a continuation.
    """
    stripped = text.strip()
    if not stripped:
        return False
    for pattern in _SYSTEM_MESSAGE_PATTERNS:
        if pattern.search(stripped):
            return True
    return False


def extract_session_key_from_input(text: str) -> str:
    """从 envelope/system message 中提取 sessionId/sessionKey。"""
    if not text:
        return None

    m = _re.search(r'\[sessionId:\s*([0-9a-fA-F\-]{8,})\]', text)
    if m:
        return m.group(1)

    m = _re.search(r'"session(?:Id|Key)"\s*:\s*"([0-9a-fA-F\-]{8,})"', text)
    if m:
        return m.group(1)

    return None


def _extract_json_block_after_label(text: str, label_prefix: str):
    lines = text.splitlines()
    capture = False
    in_fence = False
    buf = []

    for raw in lines:
        line = raw.strip()

        if not capture and line.startswith(label_prefix):
            capture = True
            continue

        if capture and line.startswith("```"):
            in_fence = not in_fence
            continue

        if capture and in_fence:
            buf.append(raw)
            continue

        if capture and not in_fence and line:
            break

    if not buf:
        return None

    payload = "\n".join(buf).strip()
    try:
        return json.loads(payload)
    except Exception:
        return None


def strip_declaration_injection(text: str) -> str:
    """移除用户输入中的伪声明/指令声明（输出层内容不得回流输入层）。"""
    if not text:
        return ""

    out = []
    for raw in str(text).splitlines():
        line = raw.strip()
        if not line:
            out.append(raw)
            continue

        if line.startswith("【语义检查】"):
            continue
        if "请在你回复的第一行原样输出以下声明" in line:
            continue
        out.append(raw)

    return "\n".join(out).strip()


def unwrap_semantic_router_envelope(text: str) -> str:
    """结构化提取 envelope 里的真实当前用户消息。

    关键规则：
      - 只信任“当前消息正文”
      - 不把 Replied message.body 当作本轮输入（避免输出回流输入）
    """
    stripped = (text or "").strip()
    if not stripped.startswith("[语义路由]"):
        return strip_declaration_injection(text)

    lines = text.splitlines()
    in_code_fence = False
    body_lines = []

    for raw in lines:
        line = raw.strip()

        if line.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue
        if not line:
            continue

        # envelope/meta labels
        if line.startswith("[语义路由]"):
            continue
        if line.startswith("Conversation info"):
            continue
        if line.startswith("Replied message"):
            continue
        if "请在你回复的第一行原样输出以下声明" in line:
            continue
        if line.startswith("【语义检查】"):
            continue

        # obvious metadata/json remnants
        if line in {"{", "}", "[", "]"}:
            continue
        if line.startswith('"') and (":" in line or line.endswith('",') or line.endswith('"')):
            continue

        body_lines.append(line)

    if body_lines:
        return strip_declaration_injection("\n".join(body_lines).strip())

    # 若 envelope 无正文，返回空字符串而非 replied body，避免伪上下文污染
    return ""


# Keywords requiring strict boundary matching (short/ambiguous)
_WORD_BOUNDARY_KEYWORDS = {"code", "coding"}


def _is_ascii_word(s: str) -> bool:
    return bool(_re.fullmatch(r'[a-zA-Z0-9_\-]+', s or ""))


def _contains_term_with_boundary(text: str, term: str, strict_short_cjk: bool = False) -> bool:
    """边界匹配：ASCII 用词边界；CJK 用“非字母数字中文”边界，降低子串误击。"""
    if not term:
        return False

    t = term.lower().strip()
    if not t:
        return False

    # 单字中文指示词噪声极高（这/那），默认忽略
    if strict_short_cjk and len(t) == 1 and _re.match(r'[\u4e00-\u9fff]', t):
        return False

    if _is_ascii_word(t):
        return bool(_re.search(r'(?<![a-zA-Z0-9_])' + _re.escape(t) + r'(?![a-zA-Z0-9_])', text))

    # Pure CJK terms (len>=2): allow substring match (Chinese has no whitespace boundary)
    if _re.fullmatch(r'[\u4e00-\u9fff]+', t):
        return t in text

    # Mixed token boundary
    return bool(_re.search(r'(?<![\u4e00-\u9fffA-Za-z0-9_])' + _re.escape(t) + r'(?![\u4e00-\u9fffA-Za-z0-9_])', text))


def keyword_match(user_input: str, include_continue: bool = True, include_non_continue: bool = True):
    """关键词匹配（v7.6：支持 continue/non-continue 分流）。"""
    text = user_input.lower().strip()

    for task_type, config in TASK_PATTERNS.items():
        is_continue_task = task_type == "continue"
        if is_continue_task and not include_continue:
            continue
        if (not is_continue_task) and not include_non_continue:
            continue

        is_standalone = config.get("standalone", False)

        for kw in config.get("keywords", []):
            kw_norm = (kw or "").lower().strip()
            if not kw_norm:
                continue

            if is_standalone:
                if text == kw_norm or text.startswith(kw_norm + " ") or text.startswith(kw_norm + "?"):
                    return task_type, config.get("action"), config.get("pool"), is_continue_task
                continue

            if kw_norm in _WORD_BOUNDARY_KEYWORDS:
                if _contains_term_with_boundary(text, kw_norm):
                    return task_type, config.get("action"), config.get("pool"), is_continue_task
            else:
                if _contains_term_with_boundary(text, kw_norm):
                    return task_type, config.get("action"), config.get("pool"), is_continue_task

    return None, None, None, False


def indicator_match(user_input: str) -> bool:
    """指示词检测（v7.5：边界匹配 + 忽略单字中文噪声）。"""
    text = user_input.lower().strip()
    for indicators in CONTINUATION_INDICATORS.values():
        for indicator in indicators:
            if _contains_term_with_boundary(text, indicator, strict_short_cjk=True):
                return True
    return False


# ── Local Embedding Model (sentence-transformers, zero API cost) ──────────

_LOCAL_MODEL_PATH = os.path.expanduser(
    '~/.cache/huggingface/hub/models--BAAI--bge-base-zh-v1.5/'
    'snapshots/f03589ceff5aac7111bd60cfc7d497ca17ecac65'
)

_st_model = None  # lazy singleton

def _get_local_model():
    """Lazy-load local sentence-transformers model (bge-base-zh-v1.5, 768-dim)."""
    global _st_model
    if _st_model is not None:
        return _st_model

    # Force offline mode — never hit network
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'

    try:
        import warnings
        warnings.filterwarnings('ignore')
        from sentence_transformers import SentenceTransformer
        _st_model = SentenceTransformer(_LOCAL_MODEL_PATH, local_files_only=True)
        return _st_model
    except Exception as e:
        print(f"Warning: Local embedding model load failed: {e}", file=sys.stderr)
        return None


def get_embedding_client():
    """获取 embedding 客户端 — 优先本地模型，无需 API key"""
    model = _get_local_model()
    if model is not None:
        return model, "local"

    # Fallback: try OpenAI API (legacy path)
    api_key = os.environ.get("OPENAI_API_KEY", "")
    api_base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
    try:
        from openai import OpenAI
        if api_key:
            return OpenAI(api_key=api_key, base_url=api_base), "openai"
    except ImportError:
        pass

    print("Warning: No embedding backend available, falling back to Jaccard", file=sys.stderr)
    return None, "fallback"


def embed_text(text: str, client=None, provider: str = "local") -> list:
    """
    获取文本的向量表示。
    Local model: bge-base-zh-v1.5 (768-dim), ~1.6ms/call, zero API cost.
    Returns: list of floats or None on failure.
    """
    if not text or not text.strip():
        return None

    if client is None:
        client, provider = get_embedding_client()

    if client is None:
        return None

    try:
        if provider == "local":
            # sentence-transformers model — returns numpy array
            vec = client.encode(text.strip())
            return vec.tolist()
        elif provider == "openai":
            response = client.embeddings.create(
                input=text.strip(),
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
    except Exception as e:
        print(f"Warning: Embedding failed ({provider}): {e}", file=sys.stderr)
        return None

    return None


def cosine_similarity(vec1: list, vec2: list) -> float:
    """计算两个向量的余弦相似度"""
    if not vec1 or not vec2:
        return 0.0

    try:
        import numpy as np
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        denom = np.linalg.norm(v1) * np.linalg.norm(v2)
        if denom == 0:
            return 0.0
        return float(np.dot(v1, v2) / denom)
    except ImportError:
        import math
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

def jaccard_similarity(text1: str, text2: str) -> float:
    """Jaccard 相似度 (legacy fallback, used when embedding unavailable)"""
    tokens1 = set(_re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text1.lower()))
    tokens2 = set(_re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text2.lower()))
    if not tokens1 or not tokens2:
        return 0.0
    intersection = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)
    return intersection / union if union > 0 else 0.0

# ── Context Relevance (双通道: Embedding (Primary) + Entity Overlap (Secondary)) ──────────

# Thresholds for graded session action (based on embedding cosine similarity or Jaccard fallback)
THRESHOLD_CONTINUE = 0.55   # ≥ 0.55 → 延续（提高 continue 门槛，增强新话题识别）
THRESHOLD_WARN = 0.35       # 0.35~0.55 → 延续但警告；<0.35 更容易进入 new_session
# < 0.30 → 建议 /new (Branch C-auto) — bge-base-zh low均分0.30，此处为明确新话题

def tokenize_zh_enhanced(text: str) -> set:
    """中文字符级(unigram + bigram + trigram) + 英文词级 分词"""
    text = text.lower().strip()
    tokens = set()
    # 英文单词（含下划线、连字符、点号的标识符）
    tokens.update(_re.findall(r'[a-zA-Z][a-zA-Z0-9_\-\.]+', text))
    # 英文短词（单字母的也要，但通过 entity 通道处理）
    tokens.update(_re.findall(r'[a-zA-Z]+', text))
    # 中文单字
    cn_chars = _re.findall(r'[\u4e00-\u9fff]', text)
    tokens.update(cn_chars)
    # 中文 bigram
    for i in range(len(cn_chars) - 1):
        tokens.add(cn_chars[i] + cn_chars[i + 1])
    # 中文 trigram（抓名词短语）
    for i in range(len(cn_chars) - 2):
        tokens.add(cn_chars[i] + cn_chars[i + 1] + cn_chars[i + 2])
    return tokens

def extract_entities(text: str) -> set:
    """提取关键实体（英文标识符、路径名、大写缩写、版本号等）"""
    entities = set()
    # 英文标识符（webhook, semantic_check, etc），2+ 字符
    entities.update(w for w in _re.findall(r'[a-zA-Z][a-zA-Z0-9_\-]+', text.lower()) if len(w) >= 2)
    # 路径A/B/C 这种标识
    entities.update(_re.findall(r'路径[A-Za-z0-9]', text))
    # Branch X
    entities.update(_re.findall(r'branch\s*[a-zA-Z]', text.lower()))
    # 版本号 v2.0 等
    entities.update(_re.findall(r'v\d+\.\d+', text.lower()))
    # 数字+单位 (端口号、阈值等) — 不作为entity，噪声太多
    return entities

def detect_task_type_fast(text: str) -> str | None:
    """
    轻量级任务类型判断（不读上下文，只做关键词匹配）。
    用于 task_type_jump 检测，避免递归调用完整 detect_task_type。
    返回 task_type 字符串，无匹配时返回 None。
    """
    for task_type, cfg in TASK_PATTERNS.items():
        if task_type == "continue":
            continue
        for kw in cfg.get("keywords", []):
            if kw in text:
                return task_type
    return None


def task_jump_penalty(current_input: str, context_messages: list) -> float:
    """
    计算任务类型跳变惩罚系数（方案C实现）。

    逻辑：
      1. 用 detect_task_type_fast 判断当前消息的 task_type
      2. 对历史消息中出现最多的 task_type 做统计（主导类型）
      3. 若当前类型 != 主导类型 → 返回惩罚系数（默认 0.55）
         同类型 → 返回 1.0（不惩罚）
         任一侧无法判断 → 返回 1.0（保守，不惩罚）

    Returns:
        penalty: float (0.55 if jump detected, else 1.0)
    """
    if not context_messages:
        return 1.0

    current_type = detect_task_type_fast(current_input)
    if current_type is None:
        return 1.0  # 无关键词，无法判断当前类型，不惩罚

    # 统计历史消息的主导 task_type
    type_counts: dict[str, int] = {}
    for ctx in context_messages:
        t = detect_task_type_fast(ctx)
        if t:
            type_counts[t] = type_counts.get(t, 0) + 1

    if not type_counts:
        return 1.0  # 历史无关键词消息，无法判断，不惩罚

    dominant_type = max(type_counts, key=lambda k: type_counts[k])

    if current_type != dominant_type:
        return 0.55  # 任务类型跳变，降低相似度
    return 1.0  # 同类型，不惩罚


def context_relevance_score(user_input: str, context_messages: list) -> tuple:
    """
    分层上下文关联度评分（v7.3: Embedding Primary → Jaccard Safety Net）。
    
    Architecture:
        Layer 1: Embedding (local all-MiniLM-L6-v2) — primary, semantic-aware
        Layer 2: Jaccard (token overlap) — safety net when embedding unavailable
        Layer 3: Entity overlap — supplementary signal in both layers
        
    Layered Fallback (P0 fix from QA audit):
        - Embedding available: use embed score directly (no Jaccard needed)
        - Embedding unavailable + Jaccard < 0.30: conservative → grade as "warn" not "new_session"
          (prevents aggressive context reset when only using token overlap)
    
    Returns:
        (score: float, method: str, grade: str)
        - score: 0.0 ~ 1.0
        - method: 'embed' | 'jaccard_fallback' | 'no_context'
        - grade: 'continue' | 'warn' | 'new_session'
    """
    if not context_messages:
        return 0.0, "no_context", "continue"  # 无上下文时保守延续

    # ── 方案B：窗口收窄到4（减少远距历史污染）─────────────────
    context_messages = context_messages[:4]

    # ── 方案C：任务类型跳变惩罚系数 ──────────────────────────────
    jump_penalty = task_jump_penalty(user_input, context_messages)

    # 获取客户端（重用或创建）
    client, provider = get_embedding_client()
    
    # Channel 1: 尝试 Embedding（精准语义匹配）
    msg_embedding = embed_text(user_input, client, provider) if client else None
    msg_entities = extract_entities(user_input)
    
    best_score = 0.0
    method = "jaccard_fallback"  # 默认降级方案
    embedding_available = False
    
    if msg_embedding:
        # Embedding 可用 — 使用语义向量匹配
        for ctx in context_messages:
            ctx_embedding = embed_text(ctx, client, provider)
            
            if ctx_embedding:
                embedding_available = True
                # Channel 1: Cosine similarity（向量空间中的语义相似度）
                embed_score = cosine_similarity(msg_embedding, ctx_embedding)
                
                # Channel 2: Entity overlap（关键词匹配补充）
                ctx_entities = extract_entities(ctx)
                if msg_entities and ctx_entities:
                    intersection_e = len(msg_entities & ctx_entities)
                    union_e = len(msg_entities | ctx_entities)
                    entity_score = intersection_e / union_e if union_e > 0 else 0.0
                else:
                    entity_score = 0.0
                
                # 综合：embed 权重 0.85，entity 权重 0.15
                # 方案C：乘以任务跳变惩罚系数（同类型=1.0，跳变=0.55）
                combined = min(1.0, (embed_score * 0.85 + entity_score * 0.15) * jump_penalty)

                if combined > best_score:
                    best_score = combined
                    method = "embed"
    
    if not embedding_available:
        # Embedding 不可用，降级到 Jaccard（兼容模式）
        msg_tokens = tokenize_zh_enhanced(user_input)
        
        for ctx in context_messages:
            ctx_tokens = tokenize_zh_enhanced(ctx)
            ctx_entities = extract_entities(ctx)
            
            # Channel 1: token Jaccard（降级）
            intersection_t = len(msg_tokens & ctx_tokens)
            union_t = len(msg_tokens | ctx_tokens)
            token_score = intersection_t / union_t if union_t > 0 else 0.0
            
            # Channel 2: entity overlap
            if msg_entities and ctx_entities:
                intersection_e = len(msg_entities & ctx_entities)
                union_e = len(msg_entities | ctx_entities)
                entity_score = intersection_e / union_e if union_e > 0 else 0.0
            else:
                entity_score = 0.0
            
            # 方案C：乘以任务跳变惩罚系数
            combined = min(1.0, max(token_score, entity_score * 1.5) * jump_penalty)

            if combined > best_score:
                best_score = combined
                method = "jaccard_fallback"
    
    # ── 分级判定（v7.3 分层 Fallback） ──────────
    if best_score >= THRESHOLD_CONTINUE:
        grade = "continue"
    elif best_score >= THRESHOLD_WARN:
        grade = "warn"
    else:
        if embedding_available:
            # Embedding 判定为低关联 — 可信度高，允许 new_session
            grade = "new_session"
        else:
            # Jaccard-only 判定低关联 — 可信度低（语义近义盲区）
            # P0 safety net: 保守降级为 warn 而非 new_session
            # 防止 Jaccard 无法识别的语义关联导致误触 C-auto
            if best_score > 0.03:
                grade = "warn"  # 有少量词重叠，保守延续
            else:
                grade = "new_session"  # 几乎无关联才允许 new_session
    
    return best_score, method, grade

def detect_task_type(user_input: str, context_messages: list = None):
    """
    检测任务类型（v7.6：两轴决策）

    Axis-1: task keyword confidence（决定目标池）
    Axis-2: context novelty（决定 C vs C-auto）

    Returns:
        (task_type, action, pool, branch, detection, context_score, context_grade)
    """
    if is_system_message(user_input):
        return "continue", "系统信号(透传)", None, "B", "system_passthrough", 1.0, "continue"

    ctx_msgs = context_messages or []
    score, method, grade = context_relevance_score(user_input, ctx_msgs)

    # A. 明确延续意图：仅 continue 关键词优先
    cont_type, cont_action, cont_pool, _ = keyword_match(
        user_input,
        include_continue=True,
        include_non_continue=False,
    )
    if cont_type:
        if grade == "new_session":
            return "continue", "延续(低关联警告)", cont_pool, "B+", "keyword_continue", score, "warn"
        return cont_type, cont_action, cont_pool, "B", "keyword_continue", max(score, 1.0), "continue"

    # B. 非 continue 任务关键词优先于指示词（修复“这个+动作词”误延续）
    task_type, action, pool, _ = keyword_match(
        user_input,
        include_continue=False,
        include_non_continue=True,
    )
    if task_type:
        if grade == "new_session":
            return "new_topic", "自动/new+切池", pool or "Highspeed", "C-auto", "keyword", score, grade
        return task_type, action, pool, "C", "keyword", score, grade

    # C. 指示词仅在无任务关键词时生效
    if indicator_match(user_input):
        if grade == "new_session":
            return "continue", "延续(低关联警告)", None, "B+", "indicator", score, "warn"
        return "continue", "延续", None, "B", "indicator", max(score, 1.0), "continue"

    # D. 无关键词，完全由上下文新颖度决定
    if grade == "continue":
        return "continue", "延续", None, "B", f"context_{method}", score, grade
    if grade == "warn":
        return "continue", "延续(话题可能漂移)", None, "B+", f"context_{method}", score, grade

    return "new_topic", "自动/new+切池", "Highspeed", "C-auto", f"context_{method}", score, grade

def get_pool_info(pool_name: str):
    if pool_name and pool_name in MODEL_POOLS:
        return MODEL_POOLS[pool_name]
    return None

def get_current_pool():
    return os.environ.get("CURRENT_POOL", "Highspeed")

def generate_declaration(result: dict, current_pool: str, current_model: str = None) -> str:
    task_type = result["task_type"]
    action = result["action"]
    branch = result.get("branch", "C")
    detection_method = result.get("detection_method", "unknown")
    ctx_score = result.get("context_score", 0)

    p_level = {
        "development": "P1", "automation": "P1", "system_ops": "P1",
        "info_retrieval": "P2", "coordination": "P2", "web_search": "P2",
        "content_generation": "P3", "reading": "P3", "q_and_a": "P3", "training": "P3", "multimodal": "P3",
        "continue": "P2", "new_session": "P4"
    }.get(task_type, "P2")

    # 标记检测方法（embed/jaccard_fallback/keyword/indicator/system）
    method_marker = {
        "context_embed": "📊",
        "embed": "📊",
        "context_jaccard_fallback": "⚙️",
        "jaccard_fallback": "⚙️",
        "context_token": "⚙️",
        "keyword_continue": "🔑",
        "indicator": "🔍",
        "keyword": "🔑",
        "no_context": "○",
        "system_passthrough": "🛡️"
    }.get(detection_method, "")

    if branch == "B":
        # B分支: 延续（高关联度 ≥0.40）
        pool_chinese = MODEL_POOLS.get(current_pool, {}).get("name", current_pool)
        model_short = (current_model or "").split("/")[-1] or current_pool
        score_str = f" {ctx_score:.2f}" if ctx_score > 0 else ""
        return f"【语义检查 by DeepEye@halfmoon82】{p_level}-延续{method_marker}{score_str}｜模型池:【{pool_chinese}】｜实际模型:{model_short}"
    elif branch == "B+":
        # B+分支: 延续但警告话题漂移（中关联度 0.20~0.40）
        pool_chinese = MODEL_POOLS.get(current_pool, {}).get("name", current_pool)
        model_short = (current_model or "").split("/")[-1] or current_pool
        return f"【语义检查 by DeepEye@halfmoon82】{p_level}-延续(漂移⚠️{method_marker}{ctx_score:.2f})｜模型池:【{pool_chinese}】｜实际模型:{model_short}"
    elif branch == "C-auto":
        # C-auto分支: 低关联度（<0.30），自动 /new + 切换到目标池 primary
        target_pool_key = result.get("pool", "Highspeed")
        pool_info = get_pool_info(target_pool_key)
        pool_chinese = pool_info.get("name", target_pool_key) if pool_info else (target_pool_key or "高速池")
        primary = result.get("primary_model", "")
        model_short = primary.split("/")[-1] if primary else "未知"
        return f"【语义检查 by DeepEye@halfmoon82】{p_level}-新话题({method_marker}{ctx_score:.2f}<0.30)｜/new→{pool_chinese}｜实际模型:{model_short}"
    else:
        # C分支: 新任务类型（关键词匹配），建议切模型但不切会话
        target_pool_key = result.get("pool")
        pool_info = get_pool_info(target_pool_key)
        pool_chinese = pool_info.get("name", target_pool_key) if pool_info else (target_pool_key or "未知池")
        primary = result.get("primary_model", "")
        model_short = primary.split("/")[-1] if primary else "未知"
        return f"【语义检查 by DeepEye@halfmoon82】{p_level}-{action}({method_marker})｜新池→{pool_chinese}｜实际模型:{model_short}"

def build_context_archive_prompt():
    return """[上下文截止符] 之前的对话已归档。从本条消息开始作为新的上下文起点。"""

def execute_model_switch(model: str, session_key: str = None) -> bool:
    """执行模型切换（自动+真实执行）。

    Strategy:
      1) openclaw session_status --model <model> [--sessionKey <key>]
      2) fallback: openclaw status --model <model>
    """
    if not model:
        return False

    candidates = []
    if session_key:
        candidates.append(["openclaw", "session_status", "--model", model, "--sessionKey", session_key])
    candidates.append(["openclaw", "session_status", "--model", model])
    candidates.append(["openclaw", "status", "--model", model])

    for cmd in candidates:
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
            if proc.returncode == 0:
                print(f"✅ 模型切换成功: {model} via {' '.join(cmd[:2])}", file=sys.stderr)
                return True
            else:
                print(f"⚠️ 模型切换尝试失败({proc.returncode}): {' '.join(cmd)} | {proc.stderr[:160]}", file=sys.stderr)
        except FileNotFoundError:
            print("❌ openclaw CLI 不存在，无法自动切换模型", file=sys.stderr)
            return False
        except subprocess.TimeoutExpired:
            print(f"⚠️ 模型切换超时: {' '.join(cmd)}", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ 模型切换异常: {' '.join(cmd)} | {e}", file=sys.stderr)

    return False

def execute_fallback_chain(primary: str, fallback_1: str = None, fallback_2: str = None) -> dict:
    """
    执行 Fallback 回路
    返回: {"attempted": [...], "success": bool, "current_model": str}
    """
    results = {
        "attempted": [],
        "success": False,
        "current_model": primary
    }
    
    models_to_try = [primary]
    if fallback_1:
        models_to_try.append(fallback_1)
    if fallback_2:
        models_to_try.append(fallback_2)
    
    for model in models_to_try:
        print(f"🔄 Trying model: {model}", file=sys.stderr)
        results["attempted"].append(model)

        if execute_model_switch(model):
            results["success"] = True
            results["current_model"] = model
            print(f"✅ Fallback success: {model}", file=sys.stderr)
            return results
    
    print(f"❌ All fallback attempts failed", file=sys.stderr)
    return results

def main():
    parser = argparse.ArgumentParser(description="Semantic Router - 模型路由脚本")
    parser.add_argument("user_input", nargs="?", help="用户输入消息")
    parser.add_argument("current_pool", nargs="?", help="当前模型池")
    parser.add_argument("context_messages", nargs="*", help="上下文消息列表")
    parser.add_argument("--current-model", default=None, help="当前实际使用的模型 ID（用于B分支声明）")
    parser.add_argument("--session-key", default=None, help="当前会话 key（用于上下文隔离读取）")
    parser.add_argument("-e", "--execute", action="store_true", help="自动执行模型切换（主模型）")
    parser.add_argument("-f", "--fallback", action="store_true", help="执行 Fallback 回路（主模型失败时自动切换备用）")
    
    args = parser.parse_args()
    
    # 如果没有参数，显示用法
    if len(sys.argv) < 2:
        print("Usage: semantic_check.py <user_input> [current_pool] [context1] [context2] ...] [-e|--execute] [-f|--fallback]")
        print("Example: semantic_check.py '查一下天气' 'Intelligence' -e")
        print("Example: semantic_check.py --fallback 'openai/gpt-4o-mini' 'glm-4.7-flashx' 'MiniMax-M2.5'")
        sys.exit(1)
    
    # Fallback 模式：手动指定模型链
    if args.fallback:
        fallback_models = []
        if args.user_input:
            fallback_models.append(args.user_input)
        if args.current_pool:
            fallback_models.append(args.current_pool)
        fallback_models.extend(args.context_messages)
        
        fallback_results = execute_fallback_chain(
            fallback_models[0] if len(fallback_models) > 0 else None,
            fallback_models[1] if len(fallback_models) > 1 else None,
            fallback_models[2] if len(fallback_models) > 2 else None
        )
        print(json.dumps(fallback_results, ensure_ascii=False, indent=2))
        return
    
    raw_input = args.user_input
    user_input = unwrap_semantic_router_envelope(raw_input)
    current_pool = args.current_pool if args.current_pool else get_current_pool()
    current_model = args.current_model

    session_key = (
        args.session_key
        or os.environ.get("OPENCLAW_SESSION_KEY")
        or os.environ.get("SESSION_KEY")
        or extract_session_key_from_input(raw_input)
    )

    context_messages = args.context_messages if args.context_messages else get_recent_messages(
        limit=9,
        exclude_input=raw_input,
        session_key=session_key,
    )
    
    task_type, action, pool_name, branch, detection, ctx_score, ctx_grade = detect_task_type(user_input, context_messages)
    
    # B/B+ 分支延续时，pool_name 可能为 None（continue 类型没有定义 pool）
    # 此时应保持 current_pool
    if pool_name is None and branch in ("B", "B+"):
        pool_name = current_pool
    
    pool_info = get_pool_info(pool_name)
    
    # 判断是否需要切换模型
    need_switch = bool(task_type not in ("continue",) and pool_info and pool_info.get("primary"))
    target_model = pool_info.get("primary") if (need_switch or branch == "C-auto") else None
    if branch == "C-auto" and pool_info:
        need_switch = True
        target_model = pool_info.get("primary")
    
    # action_command: 代理必须无条件执行的原子指令
    # "continue"       → 不切换，直接回复
    # "continue_warn"  → 延续但在声明中标注漂移警告
    # "switch"         → 切换到 target_model，然后回复（同会话内切模型）
    # "new_and_switch"  → 执行 /new 清空上下文 + 切换到目标池 primary（C-auto 专用）
    if branch == "B":
        action_command = "continue"
    elif branch == "B+":
        action_command = "continue_warn"
    elif branch == "C-auto":
        action_command = "new_and_switch"  # v7.2: 自动 /new + 切到目标池 primary
    else:  # C
        action_command = "switch"
    
    result = {
        "branch": branch,
        "task_type": task_type,
        "action": action,
        "pool": pool_name,
        "pool_name": pool_info.get("name") if pool_info else None,
        "primary_model": target_model,
        "fallback_1": pool_info.get("fallback_1") if pool_info else None,
        "fallback_2": pool_info.get("fallback_2") if pool_info else None,
        "need_archive": branch in ("C", "C-auto"),
        "need_reset": branch == "C-auto",  # C-auto: 自动 /new 清空上下文
        "need_switch": need_switch or branch == "C-auto",  # C-auto 也需要切换
        "action_command": action_command,
        # legacy compat
        "session_action": action_command,
        "detection_method": detection,
        "context_score": ctx_score,
        "context_grade": ctx_grade,
        "fallback_chain": [target_model, pool_info.get("fallback_1"), pool_info.get("fallback_2")] if pool_info else [],
        "declaration": None,
        "context_cutoff_prompt": build_context_archive_prompt() if branch in ("C", "C-auto") else None,
        "auto_executed": False,
        "session_key": session_key,
    }
    
    result["declaration"] = generate_declaration(result, current_pool, current_model)
    
    # 记录日志
    log_file = os.path.expanduser("~/.openclaw/workspace/.lib/semantic_check.log")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            method_icon = {
                "context_embed": "📊",
                "embed": "📊",
                "context_jaccard_fallback": "⚙️",
                "jaccard_fallback": "⚙️",
                "context_token": "⚙️",
                "keyword_continue": "🔑",
                "indicator": "🔍",
                "keyword": "🔑",
                "no_context": "○",
                "system_passthrough": "🛡️"
            }.get(detection, "?")
            f.write(f"[{datetime.now().isoformat()}] {user_input[:40]:40} | {branch:5} {task_type:20} {method_icon} score={ctx_score:.3f} grade={ctx_grade}\n")
    except Exception as e:
        pass
    
    # 如果需要切换且启用了自动执行
    if need_switch and args.execute and target_model:
        print(f"🔄 Auto-switching model to: {target_model}", file=sys.stderr)
        success = execute_model_switch(target_model, session_key=session_key)
        result["auto_executed"] = success
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
