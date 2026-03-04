"""
Memori + Zhipu API - OpenClaw Skill

Memory augmentation and LLM call interception using the Memori Python library.
"""
import os
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import re
import pathlib

# Import the real Memori library
from memori import Memori, Memory, AugmentedContext

# Zhipu API config (optional - the skill works without these)
# NOTE: ZHIPUAI_API_KEY is OPTIONAL. If not set, the skill operates
# entirely locally with no external API calls. Only set this if you
# explicitly consent to sending conversation data to Zhipu AI servers.
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "")
ZHIPUAI_MODEL = os.getenv("ZHIPUAI_MODEL", "glm-4.7")

# Feature flags
AUGMENTATION_ENABLED = True
RETRIEVAL_ENABLED = True
INTERCEPTION_ENABLED = True

# Try to import Zhipu SDK (optional)
# The zhipuai package is not required for core functionality.
# It's only needed if you want to enable Zhipu AI augmentation.
try:
    from zhipuai import ZhipuAI
    ZHIPUAI_AVAILABLE = True
except ImportError:
    ZHIPUAI_AVAILABLE = False


# ============================================
# Configurable tech terms (not hard-coded)
# ============================================

# Default fallback terms.
# Intentionally left empty so deployers provide their own terms via
# the MEMORI_TECH_TERMS env var or MEMORI_TECH_TERMS_FILE.
# You can set a small non-sensitive fallback here if desired.
DEFAULT_TECH_TERMS: List[str] = []

# Cached loaded terms
_TECH_TERMS_CACHE: Optional[List[str]] = None


def load_tech_terms() -> List[str]:
    """Load tech terms from environment, file, or fall back to defaults.

    Order of sources:
      1. MEMORI_TECH_TERMS environment variable (comma-separated)
      2. MEMORI_TECH_TERMS_FILE (one term per line)
      3. DEFAULT_TECH_TERMS fallback
    Results are cached for the process lifetime.
    """
    global _TECH_TERMS_CACHE
    if _TECH_TERMS_CACHE is not None:
        return _TECH_TERMS_CACHE

    terms: List[str] = []

    # 1) Env var
    env = os.getenv("MEMORI_TECH_TERMS", "")
    if env:
        terms.extend([t.strip() for t in env.split(",") if t.strip()])

    # 2) File
    file_path = os.getenv("MEMORI_TECH_TERMS_FILE", "./config/tech_terms.txt")
    p = pathlib.Path(file_path)
    if p.exists():
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
            terms.extend([ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")])
        except Exception:
            # ignore file read errors and fall back
            pass

    # 3) fallback: only use DEFAULT_TECH_TERMS if it's non-empty.
    # If DEFAULT_TECH_TERMS is empty, we return an empty term list to avoid
    # embedding hard-coded organization-specific keywords in the source.
    if not terms:
        if DEFAULT_TECH_TERMS:
            terms = DEFAULT_TECH_TERMS.copy()
        else:
            terms = []

    # dedupe while preserving order
    seen: Set[str] = set()
    normalized: List[str] = []
    for t in terms:
        if t not in seen:
            seen.add(t)
            normalized.append(t)

    _TECH_TERMS_CACHE = normalized
    return _TECH_TERMS_CACHE


def add_tech_term(term: str, persist: bool = False) -> None:
    """Add a tech term at runtime. If persist=True and a file path is configured,
    append it to the file path to make it persistent across restarts."""
    global _TECH_TERMS_CACHE
    terms = load_tech_terms()
    if term not in terms:
        terms.append(term)
        _TECH_TERMS_CACHE = terms
        if persist:
            file_path = os.getenv("MEMORI_TECH_TERMS_FILE", "./config/tech_terms.txt")
            try:
                p = pathlib.Path(file_path)
                p.parent.mkdir(parents=True, exist_ok=True)
                with p.open("a", encoding="utf-8") as f:
                    f.write(term + "\n")
            except Exception:
                pass


# ============================================
# Data Models
# ============================================

@dataclass
class Message:
    """Message object."""
    role: str
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


# ============================================
# Memori Wrapper
# ============================================

class MemoriWrapper:
    """
    Wrapper for Memori library with convenience features.
    """

    def __init__(
        self,
        db_path: str = "./memori.db",
        entity_id: str = "default"
    ):
        """
        Initialize Memori wrapper.

        Args:
            db_path: Database path
            entity_id: Entity ID
        """
        self.memori = Memori(db_path=db_path, entity_id=entity_id)
        self.entity_id = entity_id

    # Delegate to Memori library
    def search(self, query: str, limit: int = 5) -> List[Memory]:
        """Search memories."""
        if not RETRIEVAL_ENABLED:
            return []
        return self.memori.search(query, limit=limit)

    def augment(self, query: str, limit: int = 3) -> AugmentedContext:
        """Augment query."""
        return self.memori.augment(query, limit=limit)

    def store(self, content: str) -> int:
        """Store memory."""
        return self.memori.store(content)

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics."""
        return self.memori.get_stats()

    def close(self):
        """Close connection."""
        self.memori.close()

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support."""
        self.close()


# ============================================
# Zhipu AI Client (Optional)
# ============================================

class ZhipuClient:
    """
    Zhipu AI client for optional conversation augmentation.

    NOTE: This is an OPTIONAL feature. The skill works perfectly without it.
    Only use this if you:
    1. Have installed the zhipuai package (pip install zhipuai)
    2. Have set ZHIPUAI_API_KEY environment variable
    3. Explicitly consent to sending conversation data to external API servers

    If ZHIPUAI_API_KEY is not set, this client gracefully disables itself
    and the skill operates in local-only mode.
    """

    def __init__(self):
        self.client = None

        # Only initialize if Zhipu SDK is available AND API key is provided
        if ZHIPUAI_AVAILABLE and ZHIPUAI_API_KEY:
            try:
                self.client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
            except Exception as e:
                # Fail gracefully - the skill will continue to work in local mode
                print(f"Warning: Zhipu client initialization failed: {e}")
                print("The skill will continue to operate in local-only mode.")

    def is_available(self) -> bool:
        """Check if Zhipu API is available and configured."""
        return self.client is not None

    def augment_conversation(
        self,
        messages: List[Message]
    ) -> Optional[Dict[str, Any]]:
        """
        Augment conversation using Zhipu API.

        Args:
            messages: Conversation messages

        Returns:
            Augmentation result if API is available, None otherwise

        NOTE: This sends conversation text to Zhipu AI's external servers.
        Only use if you have explicitly consented to this data transmission.
        """
        if not self.is_available():
            return None

        prompt = """Analyze the following conversation and extract:
1. Entities: Technical terms, concepts
2. Relations: Causal relationships, dependencies
3. Summary: Brief summary (100 words max)

Conversation:
""" + "\n".join([f"{m.role}: {m.content}" for m in messages])

        try:
            response = self.client.chat.completions.create(
                model=ZHIPUAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a technical analysis assistant."},
                    {"role": "user", "content": prompt}
                ]
            )

            return {
                "entities": self._extract_entities(response.choices[0].message.content),
                "summary": response.choices[0].message.content[:500],
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }

        except Exception as e:
            # Fail gracefully - don't break the skill if API call fails
            print(f"Warning: Zhipu augmentation failed: {e}")
            return None

    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text using configurable tech terms.

        Sources for tech terms (in order):
        1. Environment variable MEMORI_TECH_TERMS (comma-separated)
        2. File specified by MEMORI_TECH_TERMS_FILE (one term per line)
        3. Default fallback list
        """
        found: List[str] = []
        terms = load_tech_terms()
        for term in terms:
            # match as whole word where possible, case-insensitive
            pattern = r"\b" + re.escape(term) + r"\b"
            if re.search(pattern, text, flags=re.IGNORECASE):
                found.append(term)
        return found


# ============================================
# LLM Call Interceptor
# ============================================

class LLMInterceptor:
    """
    Intercepts LLM calls and injects memory context.
    """
    # keywords are loaded at runtime from configuration; keep field on instance
    def __init__(self, memori_wrapper: MemoriWrapper):
        self.memori = memori_wrapper
        self.intercept_count = 0
        # load configured keywords (cached)
        self.tech_keywords = load_tech_terms()

    def should_intercept(self, messages: List[Dict[str, str]]) -> bool:
        """Check if should intercept."""
        if not INTERCEPTION_ENABLED:
            return False

        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                # perform case-insensitive whole-word-ish matching against configured terms
                for kw in self.tech_keywords:
                    # simple contains check is fast and covers many cases; for word boundaries use regex
                    if re.search(r"\b" + re.escape(kw) + r"\b", content, flags=re.IGNORECASE):
                        return True
                return False

        return False

    def intercept(
        self,
        messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Intercept and augment messages.

        Args:
            messages: Original messages

        Returns:
            Augmented messages
        """
        # Extract user query
        user_query = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_query = msg.get("content", "")
                break

        if not user_query:
            return messages

        # Augment with Memori
        context = self.memori.augment(user_query, limit=3)

        if not context.has_memories:
            return messages

        # Build augmented messages
        enhanced_messages = [
            {
                "role": "system",
                "content": f"""You are a professional technical assistant. Please answer the user's question based on the following professional knowledge:

{context.enhanced_prompt}
"""
            }
        ]

        # Add original messages (except system)
        for msg in messages:
            if msg.get("role") != "system":
                enhanced_messages.append(msg)

        self.intercept_count += 1
        return enhanced_messages


# ============================================
# Global Instances
# ============================================

_memori_wrapper_instance = None
_interceptor_instance = None
_zhipu_client = None


def get_memori() -> MemoriWrapper:
    """Get global Memori instance."""
    global _memori_wrapper_instance
    if _memori_wrapper_instance is None:
        _memori_wrapper_instance = MemoriWrapper()
    return _memori_wrapper_instance


def get_interceptor() -> LLMInterceptor:
    """Get global interceptor instance."""
    global _interceptor_instance
    if _interceptor_instance is None:
        _interceptor_instance = LLMInterceptor(get_memori())
    return _interceptor_instance


def get_zhipu_client() -> ZhipuClient:
    """Get Zhipu client instance."""
    global _zhipu_client
    if _zhipu_client is None:
        _zhipu_client = ZhipuClient()
    return _zhipu_client


# ============================================
# Convenience API
# ============================================

def search(query: str, limit: int = 5) -> List[Memory]:
    """Search memories."""
    return get_memori().search(query, limit=limit)


def augment(query: str, limit: int = 3) -> str:
    """
    Augment query.

    Returns:
        Augmented prompt text if memories found
        None if no memories found
    """
    context = get_memori().augment(query, limit=limit)

    if context.has_memories:
        return context.enhanced_prompt
    else:
        return None


def intercept_llm(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Intercept LLM call."""
    interceptor = get_interceptor()

    if interceptor.should_intercept(messages):
        return interceptor.intercept(messages)
    else:
        return messages


# ============================================
# Compatibility API
# ============================================

def enhance_with_memori(query: str) -> str:
    """Augment query (compatibility function)."""
    return augment(query)


def intercept_llm_call(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Intercept LLM call (compatibility function)."""
    return intercept_llm(messages)
