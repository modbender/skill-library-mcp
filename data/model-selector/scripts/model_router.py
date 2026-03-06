import re
import json
import os
try:
    from sentence_transformers import SentenceTransformer, util
    _HAS_SEMANTIC = True
except ImportError:
    _HAS_SEMANTIC = False

class ModelRouter:
    """
    Standalone Model Router for OpenClaw Skills.
    Categorizes inputs into Elite, Balanced, or Basic tiers.
    Supports dynamic keyword refinement (Rolling Adjustment).
    """
    def __init__(self, 
                 elite_model="anthropic/claude-3-5-sonnet-latest", 
                 balanced_model="openai/gpt-4o-mini", 
                 basic_model="deepseek/deepseek-chat",
                 history_file="query_history.json"):
        self.mapping = {
            "ELITE": elite_model,
            "BALANCED": balanced_model,
            "BASIC": basic_model
        }
        self.history_file = history_file
        self.encoder = None
        self.intent_embeddings = {}
        
        # Default Intent Matrix - Enhanced for practical use cases (ClawHub Ready)
        self.intent_matrix = {
            "ELITE": [
                "architecture design", "complex algorithm", "system optimization", 
                "precision reasoning", "heavy coding", "security audit",
                "high-frequency trading", "latency optimization", "financial modeling",
                "distributed systems", "database internals", "kernel programming",
                "精密推理", "架構設計", "演算法開發", "安全審查", "複雜邏輯開發", "深度性能優化", "分散式架構"
            ],
            "BALANCED": [
                "data extraction", "summarization", "translation", 
                "creative writing", "email drafting", "bug fixing",
                "Python script", "code explanation", "test case generation",
                "web scraping", "text classification", "format conversion",
                "摘要", "內容整理", "翻譯", "創意寫作", "日常郵件", "程式錯修復", "程式碼解釋", "格式轉換"
            ],
            "BASIC": [
                "greeting", "small talk", "weather", "simple math",
                "help command", "status check", "simple question",
                "token count", "current time", "joke",
                "日常對話", "閒聊", "天氣查詢", "簡單運算", "狀態檢查", "問候", "講笑話"
            ]
        }

        if _HAS_SEMANTIC:
            try:
                # Using a slightly faster/smaller model for efficiency
                self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
                self._prepare_embeddings()
            except Exception as e:
                print(f"Error loading encoder: {e}")

    def _prepare_embeddings(self):
        self.intent_embeddings = {}
        for tier, examples in self.intent_matrix.items():
            embeddings = self.encoder.encode(examples, convert_to_tensor=True)
            self.intent_embeddings[tier] = embeddings

    def route(self, query: str):
        """
        Input: User query string
        Output: Dict containing predicted tier and the corresponding model name
        """
        best_tier = "BASIC"
        max_similarity = 0.0
        similarities = {}

        # 1. Semantic Check
        if self.encoder:
            query_emb = self.encoder.encode(query, convert_to_tensor=True)
            for tier, cluster in self.intent_embeddings.items():
                # Max similarity against any keyword in the tier
                sims = util.cos_sim(query_emb, cluster)[0]
                best_sim = torch.max(sims).item()
                similarities[tier] = best_sim
                if best_sim > max_similarity:
                    max_similarity = best_sim
                    best_tier = tier
            
            # Confidence threshold - adjusted for max-based comparison
            if max_similarity < 0.4: best_tier = "BASIC"
        else:
            # 2. Simple Keyword Fallback
            for tier in ["ELITE", "BALANCED"]:
                if any(re.search(re.escape(kw), query, re.IGNORECASE) for kw in self.intent_matrix[tier]):
                    best_tier = tier
                    break

        result = {
            "tier": best_tier,
            "model": self.mapping.get(best_tier),
            "confidence": float(max_similarity) if self.encoder else 1.0,
            "all_scores": similarities
        }
        
        # Log for rolling adjustment
        self._log_query(query, best_tier)
        
        return result

    def _log_query(self, query, tier):
        """Logs the query for future keyword refinement."""
        try:
            history = []
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    try:
                        history = json.load(f)
                    except:
                        history = []
            
            history.append({"query": query, "tier": tier, "timestamp": os.path.getmtime(self.history_file) if os.path.exists(self.history_file) else 0})
            
            # Keep only last 1000 queries
            if len(history) > 1000:
                history = history[-1000:]
                
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass

    def refine_keywords(self):
        """
        Rollout refinement: Analyze history and update intent mapping.
        This provides a hook for an external process or LLM call to suggest new terms.
        """
        if not os.path.exists(self.history_file):
            return "No history found."
            
        with open(self.history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
            
        # Example: Simple keyword frequency analysis (placeholder for LLM refinement)
        # In practice, an AI agent would read this 'history' and call an ELITE model
        # to generate a list of new keywords for each tier.
        return f"History contains {len(history)} queries ready for refinement."

    def add_keywords(self, tier: str, keywords: list):
        """Add new keywords to a specific tier and refresh embeddings."""
        if tier in self.intent_matrix:
            added = []
            for kw in keywords:
                if kw not in self.intent_matrix[tier]:
                    self.intent_matrix[tier].append(kw)
                    added.append(kw)
            if added and self.encoder:
                self._prepare_embeddings()
            return added
        return []

# Usage Example for the Skill
if __name__ == "__main__":
    import torch
    router = ModelRouter()
    
    # Simulate queries
    test_queries = [
        "How's the weather today?",
        "Write a complex Python script for high-frequency trading latency optimization.",
        "Summarize this long meeting transcript into bullet points.",
        "這是一個關於分散式系統架構的深度設計問題。"
    ]
    
    print(f"{'Query':<50} | {'Tier':<10} | {'Score':<6}")
    print("-" * 75)
    for q in test_queries:
        decision = router.route(q)
        print(f"{q[:48]:<50} | {decision['tier']:<10} | {decision['confidence']:.3f}")
