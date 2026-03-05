"""
QST Memory Multi-language Support

多語言支持。

支持：
- 中文 (zh)
- 英文 (en)
- 日文 (ja)
- 混合語言處理
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import re


# ===== 語言配置 =====
@dataclass
class LanguageConfig:
    """語言配置"""
    code: str          # 語言代碼
    name: str          # 語言名稱
    segmenter: str      # 分詞器
    coherence_factor: float  # Coherence 因子


# ===== 語言配置表 =====
LANGUAGES: Dict[str, LanguageConfig] = {
    'zh': LanguageConfig('zh', '中文', 'jieba', 1.0),
    'en': LanguageConfig('en', 'English', 'nltk', 0.95),
    'ja': LanguageConfig('ja', '日本語', 'sudachi', 0.9),
    'mixed': LanguageConfig('mixed', 'Mixed', 'auto', 1.1),
}


# ===== 分詞器介面 =====
class Segmenter:
    """分詞器基類"""
    
    def segment(self, text: str) -> List[str]:
        """分詞"""
        raise NotImplementedError
    
    def keywords(self, text: str, top_k: int = 10) -> List[str]:
        """提取關鍵詞"""
        raise NotImplementedError


# ===== 中文分詞器 =====
class ChineseSegmenter(Segmenter):
    """中文分詞器"""
    
    def __init__(self):
        try:
            import jieba
            self.jieba = jieba
        except ImportError:
            self.jieba = None
            print("Warning: jieba not installed, using simple tokenization")
    
    def segment(self, text: str) -> List[str]:
        """中文分詞"""
        if self.jieba:
            return list(self.jieba.cut(text))
        return self._simple_segment(text)
    
    def _simple_segment(self, text: str) -> List[str]:
        """簡單分詞"""
        # 中英文混合分詞
        tokens = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
        return tokens
    
    def keywords(self, text: str, top_k: int = 10) -> List[str]:
        """關鍵詞提取"""
        if self.jieba:
            return list(self.jieba.analyse.extract_tags(text, topK=top_k))
        return self._simple_keywords(text, top_k)
    
    def _simple_keywords(self, text: str, top_k: int) -> List[str]:
        """簡單關鍵詞"""
        words = self.segment(text)
        from collections import Counter
        freq = Counter(words)
        return [w for w, _ in freq.most_common(top_k)]


# ===== 英文分詞器 =====
class EnglishSegmenter(Segmenter):
    """英文分詞器"""
    
    def __init__(self):
        try:
            import nltk
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            self.nltk = nltk
        except ImportError:
            self.nltk = None
    
    def segment(self, text: str) -> List[str]:
        """英文分詞"""
        if self.nltk:
            from nltk.tokenize import word_tokenize
            return word_tokenize(text.lower())
        return self._simple_segment(text)
    
    def _simple_segment(self, text: str) -> List[str]:
        """簡單分詞"""
        return re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    def keywords(self, text: str, top_k: int = 10) -> List[str]:
        """關鍵詞提取"""
        words = self.segment(text)
        from collections import Counter
        freq = Counter(words)
        return [w for w, _ in freq.most_common(top_k)]


# ===== 日文分詞器 =====
class JapaneseSegmenter(Segmenter):
    """日文分詞器"""
    
    def __init__(self):
        try:
            import sudachipy
            self.sudachi = sudachipy
        except ImportError:
            self.sudachi = None
            print("Warning: sudachipy not installed, using simple tokenization")
    
    def segment(self, text: str) -> List[str]:
        """日文分詞"""
        if self.sudachi:
            tokenizer = self.sudachipy.Tokenizer()
            return [t.surface() for t in tokenizer.tokenize(text)]
        return self._simple_segment(text)
    
    def _simple_segment(self, text: str) -> List[str]:
        """簡單分詞"""
        return re.findall(r'[\w\u3040-\u309f\u30a0-\u30ff]+', text)
    
    def keywords(self, text: str, top_k: int = 10) -> List[str]:
        """關鍵詞提取"""
        words = self.segment(text)
        from collections import Counter
        freq = Counter(words)
        return [w for w, _ in freq.most_common(top_k)]


# ===== 自動分詞器 =====
class AutoSegmenter(Segmenter):
    """自動檢測語言並分詞"""
    
    def __init__(self):
        self.segmenters: Dict[str, Segmenter] = {}
        
        # 初始化各語言分詞器
        self.segmenters['zh'] = ChineseSegmenter()
        self.segmenters['en'] = EnglishSegmenter()
        self.segmenters['ja'] = JapaneseSegmenter()
        
        # 混合分詞器
        self.mixed_segmenter = self
    
    def detect_language(self, text: str) -> str:
        """檢測語言"""
        # 簡單檢測：統計字符
        zh_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        ja_chars = len(re.findall(r'[\u3040-\u30ff]', text))
        en_chars = len(re.findall(r'[a-zA-Z]', text))
        
        total = zh_chars + ja_chars + en_chars
        if total == 0:
            return 'en'
        
        if zh_chars / total > 0.3:
            return 'zh'
        if ja_chars / total > 0.3:
            return 'ja'
        if en_chars / total > 0.3:
            return 'en'
        
        return 'mixed'
    
    def segment(self, text: str) -> List[str]:
        """分詞（自動檢測）"""
        lang = self.detect_language(text)
        
        if lang == 'mixed':
            # 分段處理
            zh_parts = re.split(r'([\u4e00-\u9fff]+)', text)
            result = []
            for part in zh_parts:
                if re.search(r'[\u4e00-\u9fff]', part):
                    result.extend(self.segmenters['zh'].segment(part))
                else:
                    result.extend(self.segmenters['en'].segment(part))
            return result
        
        return self.segmenters.get(lang, self.segmenters['en']).segment(text)
    
    def keywords(self, text: str, top_k: int = 10) -> List[str]:
        """關鍵詞提取"""
        lang = self.detect_language(text)
        return self.segmenters.get(lang, self.segmenters['en']).keywords(text, top_k)


# ===== 語言感知編碼器 =====
class LanguageAwareEncoder:
    """
    語言感知編碼器
    
    根據語言調整：
    - Coherence 因子
    - Token 權重
    """
    
    def __init__(self, segmenter: Segmenter = None):
        """
        初始化
        
        Args:
            segmenter: 分詞器
        """
        self.segmenter = segmenter or AutoSegmenter()
        
    def encode(self, 
              text: str,
              base_coherence: float = 0.8) -> Dict:
        """
        編碼文本
        
        Args:
            text: 輸入文本
            base_coherence: 基礎 coherence
            
        Returns:
            {
                'coherence': 調整後 coherence,
                'tokens': 分詞結果,
                'keywords': 關鍵詞,
                'language': 檢測到的語言
            }
        """
        # 檢測語言
        lang = self._detect_language(text)
        
        # 獲取配置
        config = LANGUAGES.get(lang, LANGUAGES['mixed'])
        
        # 調整 coherence
        coherence = base_coherence * config.coherence_factor
        
        # 分詞
        tokens = self.segmenter.segment(text)
        
        # 關鍵詞
        keywords = self.segmenter.keywords(text)
        
        return {
            'coherence': min(2.0, coherence),
            'tokens': tokens,
            'keywords': keywords,
            'language': lang,
            'language_name': config.name
        }
    
    def _detect_language(self, text: str) -> str:
        """檢測語言"""
        zh_ratio = len(re.findall(r'[\u4e00-\u9fff]', text)) / len(text)
        ja_ratio = len(re.findall(r'[\u3040-\u30ff]', text)) / len(text)
        en_ratio = len(re.findall(r'[a-zA-Z]', text)) / len(text)
        
        if zh_ratio > 0.1:
            return 'zh'
        if ja_ratio > 0.1:
            return 'ja'
        if en_ratio > 0.1:
            return 'en'
        return 'mixed'
    
    def tokenize(self, text: str) -> List[str]:
        """分詞"""
        return self.segmenter.segment(text)
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """提取關鍵詞"""
        return self.segmenter.keywords(text, top_k)


# ===== 多語言記憶管理器 =====
class MultilingualMemoryManager:
    """
    多語言記憶管理器
    
    根據語言自動調整處理策略
    """
    
    def __init__(self, memory_core):
        """
        初始化
        
        Args:
            memory_core: QST 記憶核心
        """
        self.core = memory_core
        self.encoder = LanguageAwareEncoder()
    
    def store(self,
              content: str,
              base_coherence: float = None,
              dsi_level: int = 0) -> str:
        """
        存儲記憶（語言感知）
        
        Args:
            content: 內容
            base_coherence: 基礎 coherence
            dsi_level: DSI 層次
            
        Returns:
            記憶 ID
        """
        # 自動 coherence
        if base_coherence is None:
            base_coherence = 0.8
        
        # 語言感知編碼
        encoded = self.encoder.encode(content, base_coherence)
        
        # 存儲
        memory = self.core.encode(
            content=content,
            base_coherence=encoded['coherence'],
            dsi_level=dsi_level
        )
        
        # 附加語言信息
        memory.language = encoded['language']
        memory.keywords = encoded['keywords']
        
        return memory.id
    
    def retrieve(self,
                 query: str,
                 top_k: int = 5,
                 language_filter: str = None) -> List:
        """
        檢索（語言感知）
        
        Args:
            query: 查詢
            top_k: 返回數量
            language_filter: 語言過濾器
            
        Returns:
            檢索結果
        """
        # 語言感知查詢
        encoded = self.encoder.encode(query)
        
        # 檢索
        results = self.core.retrieve(query, top_k)
        
        # 語言過濾
        if language_filter:
            results = [
                r for r in results
                if hasattr(r.memory, 'language')
                and r.memory.language == language_filter
            ]
        
        return results
    
    def search_by_language(self,
                         language: str,
                         top_k: int = 10) -> List:
        """
        按語言搜索
        
        Args:
            language: 目標語言
            top_k: 返回數量
            
        Returns:
            記憶列表
        """
        results = []
        for memory in self.core.memories.values():
            if hasattr(memory, 'language') and memory.language == language:
                score = memory.coherence
                results.append((memory, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results[:top_k]]
    
    def get_language_stats(self) -> Dict:
        """獲取語言統計"""
        stats: Dict[str, int] = {}
        
        for memory in self.core.memories.values():
            lang = getattr(memory, 'language', 'unknown')
            stats[lang] = stats.get(lang, 0) + 1
        
        return stats


# ===== 便捷函數 =====
def create_segmenter(lang: str = 'auto') -> Segmenter:
    """
    創建分詞器
    
    Args:
        lang: 語言代碼 ('zh', 'en', 'ja', 'auto')
    """
    if lang == 'auto':
        return AutoSegmenter()
    elif lang == 'zh':
        return ChineseSegmenter()
    elif lang == 'en':
        return EnglishSegmenter()
    elif lang == 'ja':
        return JapaneseSegmenter()
    else:
        return AutoSegmenter()


def detect_language(text: str) -> str:
    """檢測語言"""
    segmenter = AutoSegmenter()
    return segmenter.detect_language(text)


# ===== 測試 =====
if __name__ == "__main__":
    print("=== Multi-language Support Test ===\n")
    
    # 初始化
    from memory_core import QSTMemoryCore
    from short_term import ShortTermMemory
    
    core = QSTMemoryCore()
    manager = MultilingualMemoryManager(core)
    
    # 測試文本
    texts = [
        ("你好，我是皇帝", "zh"),
        ("Hello, I am the King", "en"),
        ("こんにちは、王です", "ja"),
        ("混合語言測試 Hello 世界こんにちは", "mixed")
    ]
    
    print("1. Language Detection Test")
    for text, expected in texts:
        detected = detect_language(text)
        status = "✓" if detected == expected else "✗"
        print(f"   {status} [{expected}] {text[:20]}...")
    
    print("\n2. Tokenization Test")
    segmenter = AutoSegmenter()
    for text, _ in texts:
        tokens = segmenter.segment(text)
        print(f"   {text[:20]}... -> {tokens[:5]}")
    
    print("\n3. Encoding Test")
    for text, _ in texts:
        encoded = manager.encoder.encode(text)
        print(f"   [{encoded['language_name']}] σ={encoded['coherence']:.2f} kw={encoded['keywords'][:3]}")
    
    print("\n4. Store & Retrieve Test")
    for text, _ in texts:
        manager.store(text)
    
    print(f"   Stored {len(core.memories)} memories")
    
    results = manager.retrieve("皇帝")
    print(f"   '皇帝' search: {len(results)} results")
    
    print("\n5. Language Stats")
    print(manager.get_language_stats())
    
    print("\n=== Complete ===")
