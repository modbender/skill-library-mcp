"""
Soul Memory v3.1 - Cantonese (廣東話) Grammar Branch Module
廣東話語法分支 - 語氣詞與語境映射系統

Version: 3.1.0
Author: Li Si (李斯)
"""

import re
from enum import Enum
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


class ToneIntensity(Enum):
    """語氣強度等級"""
    LIGHT = "輕微"      # 程度 1
    MEDIUM = "中等"    # 程度 2
    STRONG = "強烈"    # 程度 3


class ContextType(Enum):
    """語境類型"""
    CASUAL = "閒聊"      # 輕鬆對話
    FORMAL = "正式"      # 技術/正式討論
    HUMOR = "幽默"       # 輕鬆幽默
    CONCESSION = "讓步"  # 讓步語氣
    EMPHASIS = "強調"    # 強調語氣


@dataclass
class CantoneseExpression:
    """廣東話表達單元"""
    phrase: str
    tone_intensity: ToneIntensity
    context_types: List[ContextType]
    examples: List[str]
    tags: List[str]
    frequency: int = 0  # 使用頻率統計


@dataclass
class CantoneseAnalysisResult:
    """粵語分析結果"""
    is_cantonese: bool
    confidence: float
    detected_particles: List[str]
    suggested_context: ContextType
    suggested_intensity: ToneIntensity
    tone_analysis: Dict[str, any] = field(default_factory=dict)


class CantoneseSyntaxBranch:
    """
    廣東話語法分支核心類別
    
    功能：
    1. 管理語氣詞及其程度分級
    2. 語境映射與自動選擇
    3. 粵語檢測與分析
    4. 動態表達建議
    """
    
    VERSION = "3.1.0"
    
    def __init__(self):
        # 語氣詞分類
        self.tone_particles: Dict[ToneIntensity, List[CantoneseExpression]] = {
            ToneIntensity.LIGHT: [],
            ToneIntensity.MEDIUM: [],
            ToneIntensity.STRONG: []
        }
        
        # 語境映射
        self.context_mappings: Dict[ContextType, List[str]] = {}
        
        # 用戶偏好記憶
        self.user_preferences: Dict[str, List[str]] = {}
        
        # 學習到的表達模式
        self.learned_patterns: List[Dict] = []
        
        # 初始化預設數據
        self._init_default_data()
    
    def _init_default_data(self):
        """初始化預設廣東話數據"""
        # 程度 1：輕微
        self.tone_particles[ToneIntensity.LIGHT] = [
            CantoneseExpression("架", ToneIntensity.LIGHT, [ContextType.CASUAL, ContextType.EMPHASIS], 
                              ["係架", "好架", "明架"], ["語氣詞", "輕微", "肯定"]),
            CantoneseExpression("啦", ToneIntensity.LIGHT, [ContextType.CASUAL, ContextType.CONCESSION],
                              ["好啦", "算啦", "夠啦"], ["語氣詞", "輕微", "讓步"]),
            CantoneseExpression("囉", ToneIntensity.LIGHT, [ContextType.CASUAL, ContextType.EMPHASIS],
                              ["係囉", "好囉", "得囉"], ["語氣詞", "輕微", "認同"]),
            CantoneseExpression("喎", ToneIntensity.LIGHT, [ContextType.CASUAL],
                              ["係喎", "哦喎"], ["語氣詞", "輕微", "醒悟"]),
            CantoneseExpression("嘅", ToneIntensity.LIGHT, [ContextType.CASUAL],
                              ["係嘅", "好嘅", "得嘅"], ["語氣詞", "輕微", "肯定"]),
        ]
        
        # 程度 2：中等
        self.tone_particles[ToneIntensity.MEDIUM] = [
            CantoneseExpression("真係...啦", ToneIntensity.MEDIUM, [ContextType.EMPHASIS, ContextType.CASUAL],
                              ["真係勁架啦", "真係犀利啦"], ["語氣詞", "中等", "強調"]),
            CantoneseExpression("都...架", ToneIntensity.MEDIUM, [ContextType.CASUAL, ContextType.EMPHASIS],
                              ["我都係架", "你都識架"], ["語氣詞", "中等", "包含"]),
            CantoneseExpression("好啦", ToneIntensity.MEDIUM, [ContextType.CONCESSION, ContextType.CASUAL],
                              ["好啦好啦", "好啦啦"], ["語氣詞", "中等", "讓步"]),
            CantoneseExpression("算啦", ToneIntensity.MEDIUM, [ContextType.CONCESSION],
                              ["算啦算啦", "唔緊要算啦"], ["語氣詞", "中等", "放棄"]),
            CantoneseExpression("咁啦", ToneIntensity.MEDIUM, [ContextType.CONCESSION, ContextType.CASUAL],
                              ["咁啦咁啦", "係咁啦"], ["語氣詞", "中等", "讓步"]),
        ]
        
        # 程度 3：強烈
        self.tone_particles[ToneIntensity.STRONG] = [
            CantoneseExpression("好犀利架！", ToneIntensity.STRONG, [ContextType.HUMOR, ContextType.EMPHASIS],
                              ["悟飯好犀利架！", "呢招好犀利架！"], ["語氣詞", "強烈", "讚嘆"]),
            CantoneseExpression("係晒架！", ToneIntensity.STRONG, [ContextType.EMPHASIS, ContextType.HUMOR],
                              ["係晒架！", "真係係晒架！"], ["語氣詞", "強烈", "完全肯定"]),
            CantoneseExpression("搞掂晒啦！", ToneIntensity.STRONG, [ContextType.HUMOR, ContextType.CONCESSION],
                              ["搞掂晒啦！", "完成晒啦！"], ["語氣詞", "強烈", "完成"]),
            CantoneseExpression("犀利到爆！", ToneIntensity.STRONG, [ContextType.HUMOR, ContextType.EMPHASIS],
                              ["犀利到爆！", "勁到爆！"], ["語氣詞", "強烈", "極致"]),
            CantoneseExpression("勁到癲！", ToneIntensity.STRONG, [ContextType.HUMOR],
                              ["勁到癲！", "犀利到癲！"], ["語氣詞", "強烈", "誇張"]),
        ]
        
        # 語境映射
        self.context_mappings = {
            ContextType.CASUAL: ["架", "啦", "囉", "犀利", "好", "得", "嘅", "喎"],
            ContextType.FORMAL: ["係咁", "所以", "咁樣", "即係", "其實", "基本上"],
            ContextType.HUMOR: ["衰鬼", "扮晒嘢", "犀利到爆", "搞掂晒", "真係離譜", "勁到癲"],
            ContextType.CONCESSION: ["好啦", "算啦", "咁啦", "無謂啦", "罷就"],
            ContextType.EMPHASIS: ["真係", "確實", "老實講", "老實說", "講真"]
        }
    
    def detect_cantonese(self, text: str) -> Tuple[bool, float]:
        """
        檢測文本是否包含廣東話元素
        
        Returns:
            (是否為粵語, 置信度 0-1)
        """
        # 粵語特有字符
        cantonese_chars = {'架', '啦', '囉', '嘅', '咁', '咗', '吓', '喎', 
                          '嘢', '係', '喺', '睇', '瞓', '飲', '緊', '過', '哋', '冇', '唔'}
        
        # 粵語特有詞彙
        cantonese_words = ['唔', '冇', '哋', '咁', '咗', '喺', '喎', '嘢', '係咪',
                          '點解', '點樣', '幾多', '幾好', '真係', '老實講', '犀利', '勁']
        
        score = 0
        
        # 檢測特有字符
        for char in cantonese_chars:
            if char in text:
                score += 0.05
        
        # 檢測特有詞彙
        for word in cantonese_words:
            if word in text:
                score += 0.1
        
        # 語氣詞加分
        for particle in ['架', '啦', '囉', '喎', '嘅']:
            if particle in text:
                score += 0.15
        
        # 特殊表達模式
        patterns = [
            r'[\u4e00-\u9fff]+架[!！.）\s]',
            r'[\u4e00-\u9fff]+啦[!！.）\s]',
            r'[\u4e00-\u9fff]+囉[!！.）\s]',
            r'真係[\u4e00-\u9fff]+',
            r'好[\u4e00-\u9fff]+架',
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                score += 0.2
        
        is_cantonese = score >= 0.3
        confidence = min(score, 1.0)
        
        return is_cantonese, confidence
    
    def analyze(self, text: str) -> CantoneseAnalysisResult:
        """
        深度分析粵語文本
        
        Returns:
            CantoneseAnalysisResult 完整分析結果
        """
        is_canto, confidence = self.detect_cantonese(text)
        
        # 檢測到的語氣詞
        detected_particles = []
        for intensity, expressions in self.tone_particles.items():
            for expr in expressions:
                if expr.phrase in text:
                    detected_particles.append(expr.phrase)
                for ex in expr.examples:
                    if ex in text:
                        detected_particles.append(ex)
        
        detected_particles = list(set(detected_particles))
        
        # 推斷語境
        suggested_context = self._infer_context(text)
        
        # 推斷語氣強度
        suggested_intensity = self._infer_intensity(text, detected_particles)
        
        # 語氣分析詳情
        tone_analysis = {
            "particle_count": len(detected_particles),
            "has_strong_tone": any(p in text for p in ["！", "犀利到爆", "勁到"]),
            "has_concession": any(p in text for p in ["好啦", "算啦", "咁啦"]),
            "formality_level": "正式" if suggested_context == ContextType.FORMAL else "非正式"
        }
        
        return CantoneseAnalysisResult(
            is_cantonese=is_canto,
            confidence=confidence,
            detected_particles=detected_particles,
            suggested_context=suggested_context,
            suggested_intensity=suggested_intensity,
            tone_analysis=tone_analysis
        )
    
    def _infer_context(self, text: str) -> ContextType:
        """推斷語境類型"""
        scores = {ctx: 0 for ctx in ContextType}
        
        for ctx, keywords in self.context_mappings.items():
            for kw in keywords:
                if kw in text:
                    scores[ctx] += 1
        
        # 特殊規則
        if any(w in text for w in ["技術", "分析", "開發", "系統"]):
            scores[ContextType.FORMAL] += 2
        if any(w in text for w in ["哈哈", "笑話", "衰鬼", "離譜"]):
            scores[ContextType.HUMOR] += 2
        if any(w in text for w in ["好啦", "算啦", "咁啦", "無謂"]):
            scores[ContextType.CONCESSION] += 2
        
        max_score = max(scores.values())
        if max_score == 0:
            return ContextType.CASUAL
        
        for ctx, score in scores.items():
            if score == max_score:
                return ctx
        
        return ContextType.CASUAL
    
    def _infer_intensity(self, text: str, particles: List[str]) -> ToneIntensity:
        """推斷語氣強度"""
        # 強烈標記
        strong_markers = ["！", "犀利到爆", "勁到", "係晒", "搞掂晒"]
        if any(m in text for m in strong_markers):
            return ToneIntensity.STRONG
        
        # 中等標記
        medium_markers = ["真係", "都...架", "好啦", "算啦"]
        if any(m in text for m in medium_markers):
            return ToneIntensity.MEDIUM
        
        # 檢查語氣詞
        for p in particles:
            for expr in self.tone_particles.get(ToneIntensity.STRONG, []):
                if p == expr.phrase or p in expr.examples:
                    return ToneIntensity.STRONG
            for expr in self.tone_particles.get(ToneIntensity.MEDIUM, []):
                if p == expr.phrase or p in expr.examples:
                    return ToneIntensity.MEDIUM
        
        return ToneIntensity.LIGHT
    
    def suggest_expression(self, concept: str, context: ContextType = None, 
                          intensity: ToneIntensity = None) -> List[str]:
        """
        建議最佳廣東話表達
        
        Args:
            concept: 要表達的概念
            context: 語境類型（可選）
            intensity: 語氣強度（可選）
        
        Returns:
            建議表達列表
        """
        suggestions = []
        
        # 根據語氣強度獲取語氣詞
        if intensity:
            for expr in self.tone_particles.get(intensity, []):
                if context in expr.context_types or context is None:
                    suggestions.extend(expr.examples)
        else:
            # 嘗試所有強度
            for intensity_level in [ToneIntensity.LIGHT, ToneIntensity.MEDIUM, ToneIntensity.STRONG]:
                for expr in self.tone_particles.get(intensity_level, []):
                    if context in expr.context_types or context is None:
                        suggestions.extend(expr.examples)
        
        # 如果有概念，嘗試組合
        if concept and suggestions:
            combined = []
            for s in suggestions[:3]:
                combined.append(f"{concept}{s}")
            return combined
        
        return suggestions[:5] if suggestions else ["架", "啦", "囉"]
    
    def learn_pattern(self, text: str, context: ContextType, feedback: str = None):
        """
        學習新的表達模式
        
        Args:
            text: 表達文本
            context: 語境類型
            feedback: 用戶反饋（可選）
        """
        pattern = {
            "text": text,
            "context": context.value,
            "feedback": feedback,
            "timestamp": self._get_timestamp()
        }
        self.learned_patterns.append(pattern)
        
        # 更新語境映射
        key_phrases = self._extract_key_phrases(text)
        for phrase in key_phrases:
            if phrase not in self.context_mappings.get(context, []):
                self.context_mappings[context].append(phrase)
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """提取關鍵短語"""
        phrases = []
        # 簡單提取：連續中文字符
        matches = re.findall(r'[\u4e00-\u9fff]+', text)
        return [m for m in matches if len(m) >= 2]
    
    def _get_timestamp(self) -> str:
        """獲取時間戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_stats(self) -> Dict:
        """獲取統計信息"""
        return {
            "version": self.VERSION,
            "total_particles": sum(len(v) for v in self.tone_particles.values()),
            "light_particles": len(self.tone_particles[ToneIntensity.LIGHT]),
            "medium_particles": len(self.tone_particles[ToneIntensity.MEDIUM]),
            "strong_particles": len(self.tone_particles[ToneIntensity.STRONG]),
            "context_types": len(self.context_mappings),
            "learned_patterns": len(self.learned_patterns)
        }


# 測試入口
if __name__ == "__main__":
    branch = CantoneseSyntaxBranch()
    
    # 測試檢測
    test_cases = [
        "悟飯好犀利架！",
        "係咁樣既，所以技術上係可行既",
        "好啦好啦，算啦",
        "This is English text"
    ]
    
    print("🧪 廣東話語法分支測試")
    print("=" * 50)
    
    for text in test_cases:
        result = branch.analyze(text)
        print(f"\n📝 輸入: {text}")
        print(f"   粵語: {'✅' if result.is_cantonese else '❌'} (置信度: {result.confidence:.2f})")
        print(f"   語境: {result.suggested_context.value}")
        print(f"   強度: {result.suggested_intensity.value}")
        print(f"   語氣詞: {result.detected_particles}")
