"""金融情感分析模块 - 基于 FinBERT.

该模块提供基于 FinBERT 的金融文本情感分析功能。
支持单条和批量分析，包含延迟加载和 LLM fallback 机制。
"""

import os
import json
from typing import List, Dict, Union, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SentimentLabel(str, Enum):
    """情感标签枚举"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    ERROR = "error"
    EMPTY = "empty"


@dataclass
class SentimentResult:
    """情感分析结果.

    Attributes:
        score: 情感分数，范围 -1.0（极度负面）到 1.0（极度正面）
        label: 情感标签（positive/negative/neutral/error/empty）
        confidence: 模型置信度，范围 0.0 到 1.0
        raw_label: 原始模型输出标签
        method: 分析方法（finbert/llm_fallback/rule_based/empty）
    """
    score: float = 0.0
    label: str = "neutral"
    confidence: float = 0.0
    raw_label: str = ""
    method: str = "unknown"

    def to_dict(self) -> Dict:
        """转换为字典."""
        return asdict(self)

    def is_bullish(self, threshold: float = 0.1) -> bool:
        """判断是否看涨.

        Args:
            threshold: 看涨阈值，默认 0.1

        Returns:
            如果情感分数大于阈值返回 True
        """
        return self.score > threshold

    def is_bearish(self, threshold: float = -0.1) -> bool:
        """判断是否看跌.

        Args:
            threshold: 看跌阈值，默认 -0.1

        Returns:
            如果情感分数小于阈值返回 True
        """
        return self.score < threshold


class FinBERTSentimentAnalyzer:
    """FinBERT 情感分析器.

    使用中文金融新闻 FinBERT 模型进行情感分析。
    支持延迟加载、批量处理和多种 fallback 策略。

    Example:
        >>> analyzer = FinBERTSentimentAnalyzer()
        >>> result = analyzer.analyze("央行降息，股市上涨")
        >>> print(result.score, result.label)
    """

    # 中文金融新闻 FinBERT 模型
    DEFAULT_MODEL = "uer/roberta-base-finetuned-chinanews-chinese"

    # 备用模型（按优先级排序）
    FALLBACK_MODELS = [
        "uer/roberta-base-finetuned-jd-binary-chinese",
        "uer/roberta-base-finetuned-dianping-chinese",
        "uer/roberta-base-finetuned-weibo-chinese",
    ]

    # 情感关键词映射（rule-based fallback）
    BULLISH_KEYWORDS = [
        "上涨", "涨停", "利好", "增长", "盈利", "突破", "买入", "增持",
        "反弹", "创新高", "超预期", "降息", "降准", "刺激", "支持",
        "利好", "景气", "扩张", "回升", "改善", "复苏", "牛市",
        "rise", "surge", "rally", "bull", "gain", "profit", "growth",
        "upgrade", "buy", "outperform", "beat", "positive"
    ]

    BEARISH_KEYWORDS = [
        "下跌", "跌停", "利空", "亏损", "跌破", "卖出", "减持",
        "回调", "创新低", "不及预期", "加息", "收紧", "风险", "危机",
        "衰退", "萎缩", "下滑", "恶化", "熊市", "panic", "crash",
        "fall", "drop", "decline", "bear", "loss", "sell", "downgrade",
        "underperform", "miss", "negative", "warning"
    ]

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: str = "cpu",
        use_mps: bool = False,
        cache_dir: Optional[str] = None
    ):
        """初始化情感分析器.

        Args:
            model_name: 模型名称，默认使用中文 FinBERT
            device: 运行设备，"cpu"、"cuda" 或 "mps"
            use_mps: 是否尝试使用 Apple Silicon MPS
            cache_dir: HuggingFace 缓存目录
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self.device = self._select_device(device, use_mps)
        self.cache_dir = cache_dir or os.path.expanduser("~/.cache/huggingface")

        self._pipeline = None
        self._model_loaded = False
        self._model_info = {
            "model_name": self.model_name,
            "loaded": False,
            "device": self.device,
            "cache_dir": self.cache_dir,
            "fallback_used": False
        }

    def _select_device(self, device: str, use_mps: bool) -> str:
        """选择最佳可用设备.

        Args:
            device: 用户指定的设备
            use_mps: 是否允许使用 MPS

        Returns:
            实际使用的设备名称
        """
        if device != "auto":
            return device

        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            if use_mps and torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass

        return "cpu"

    def _load_model(self) -> bool:
        """延迟加载模型.

        Returns:
            是否成功加载模型
        """
        if self._model_loaded:
            return True

        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

            logger.info(f"Loading FinBERT model: {self.model_name}")

            # 尝试加载主模型
            loaded = self._try_load_model(
                self.model_name,
                AutoTokenizer,
                AutoModelForSequenceClassification,
                pipeline
            )

            # 主模型失败，尝试备用模型
            if not loaded:
                for fallback_model in self.FALLBACK_MODELS:
                    logger.warning(f"Trying fallback model: {fallback_model}")
                    loaded = self._try_load_model(
                        fallback_model,
                        AutoTokenizer,
                        AutoModelForSequenceClassification,
                        pipeline
                    )
                    if loaded:
                        self._model_info["model_name"] = fallback_model
                        self._model_info["fallback_used"] = True
                        break

            if loaded:
                self._model_loaded = True
                self._model_info["loaded"] = True
                logger.info(f"Model loaded successfully on {self.device}")
                return True
            else:
                logger.error("All models failed to load")
                return False

        except ImportError as e:
            logger.warning(f"transformers not installed: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def _try_load_model(
        self,
        model_name: str,
        AutoTokenizer,
        AutoModelForSequenceClassification,
        pipeline
    ) -> bool:
        """尝试加载单个模型.

        Args:
            model_name: 模型名称
            AutoTokenizer: Tokenizer 类
            AutoModelForSequenceClassification: 模型类

        Returns:
            是否成功加载
        """
        try:
            # 尝试从本地缓存加载
            try:
                tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    local_files_only=True,
                    cache_dir=self.cache_dir
                )
                model = AutoModelForSequenceClassification.from_pretrained(
                    model_name,
                    local_files_only=True,
                    cache_dir=self.cache_dir
                )
                logger.info(f"Model loaded from local cache: {model_name}")
            except (OSError, ValueError):
                # 从 HuggingFace 下载
                logger.info(f"Downloading model: {model_name}")
                tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    cache_dir=self.cache_dir
                )
                model = AutoModelForSequenceClassification.from_pretrained(
                    model_name,
                    cache_dir=self.cache_dir
                )

            # 确定设备映射
            device_id = -1  # CPU default
            if self.device == "mps":
                import torch
                device_id = 0 if torch.backends.mps.is_available() else -1
            elif self.device == "cuda":
                import torch
                device_id = 0 if torch.cuda.is_available() else -1

            self._pipeline = pipeline(
                "sentiment-analysis",
                model=model,
                tokenizer=tokenizer,
                device=device_id,
                truncation=True,
                max_length=512
            )

            return True

        except Exception as e:
            logger.warning(f"Failed to load {model_name}: {e}")
            return False

    def analyze(self, text: str) -> SentimentResult:
        """分析单条文本情感.

        Args:
            text: 待分析文本（新闻标题、摘要等）

        Returns:
            SentimentResult 包含标准化后的情感分数
        """
        if not text or not text.strip():
            return SentimentResult(
                score=0.0,
                label=SentimentLabel.EMPTY,
                confidence=0.0,
                raw_label="",
                method="empty"
            )

        if not self._load_model():
            # 模型加载失败，使用 rule-based fallback
            return self._rule_based_fallback(text)

        try:
            result = self._pipeline(text[:512])
            raw = result[0]

            label = raw['label'].lower()
            confidence = raw['score']

            # 映射到 -1.0 ~ 1.0
            if 'positive' in label or label == 'positive':
                score = confidence
                normalized_label = SentimentLabel.POSITIVE
            elif 'negative' in label or label == 'negative':
                score = -confidence
                normalized_label = SentimentLabel.NEGATIVE
            else:
                score = 0.0
                normalized_label = SentimentLabel.NEUTRAL

            return SentimentResult(
                score=round(score, 3),
                label=normalized_label,
                confidence=round(confidence, 3),
                raw_label=label,
                method="finbert"
            )

        except Exception as e:
            logger.error(f"FinBERT analysis failed: {e}")
            return self._rule_based_fallback(text)

    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """批量分析文本情感（效率更高）.

        Args:
            texts: 待分析文本列表

        Returns:
            SentimentResult 列表，与输入顺序一致
        """
        if not texts:
            return []

        if not self._load_model():
            return [self._rule_based_fallback(t) for t in texts]

        try:
            # 记录原始索引，过滤空文本
            valid_indices = []
            valid_texts = []
            for i, t in enumerate(texts):
                if t and t.strip():
                    valid_indices.append(i)
                    valid_texts.append(t[:512])

            if not valid_texts:
                return [
                    SentimentResult(0.0, SentimentLabel.EMPTY, 0.0, "", "empty")
                    for _ in texts
                ]

            results = self._pipeline(valid_texts)

            # 构建完整结果列表
            processed = [
                SentimentResult(0.0, SentimentLabel.EMPTY, 0.0, "", "empty")
                for _ in texts
            ]

            for idx, raw in zip(valid_indices, results):
                label = raw['label'].lower()
                confidence = raw['score']

                if 'positive' in label:
                    score = confidence
                    norm_label = SentimentLabel.POSITIVE
                elif 'negative' in label:
                    score = -confidence
                    norm_label = SentimentLabel.NEGATIVE
                else:
                    score = 0.0
                    norm_label = SentimentLabel.NEUTRAL

                processed[idx] = SentimentResult(
                    score=round(score, 3),
                    label=norm_label,
                    confidence=round(confidence, 3),
                    raw_label=label,
                    method="finbert"
                )

            return processed

        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            return [self._rule_based_fallback(t) for t in texts]

    def _rule_based_fallback(self, text: str) -> SentimentResult:
        """基于规则的情感分析 fallback.

        当 FinBERT 不可用时，使用关键词匹配进行简单情感判断。

        Args:
            text: 待分析文本

        Returns:
            SentimentResult
        """
        if not text:
            return SentimentResult(0.0, SentimentLabel.EMPTY, 0.0, "", "empty")

        text_lower = text.lower()

        bullish_count = sum(1 for kw in self.BULLISH_KEYWORDS if kw in text_lower)
        bearish_count = sum(1 for kw in self.BEARISH_KEYWORDS if kw in text_lower)

        total = bullish_count + bearish_count
        if total == 0:
            return SentimentResult(0.0, SentimentLabel.NEUTRAL, 0.5, "neutral", "rule_based")

        # 计算情感分数
        score = (bullish_count - bearish_count) / max(total, 3)
        score = max(-1.0, min(1.0, score))  # 限制在 -1 到 1

        if score > 0.1:
            label = SentimentLabel.POSITIVE
        elif score < -0.1:
            label = SentimentLabel.NEGATIVE
        else:
            label = SentimentLabel.NEUTRAL

        confidence = min(0.7, total / 10)  # 关键词越多置信度越高，最高 0.7

        return SentimentResult(
            score=round(score, 3),
            label=label,
            confidence=round(confidence, 3),
            raw_label="keyword_match",
            method="rule_based"
        )

    def get_model_info(self) -> Dict:
        """获取模型信息.

        Returns:
            包含模型状态信息的字典
        """
        return self._model_info.copy()

    def warmup(self) -> bool:
        """预热模型（预加载并执行一次推理）.

        Returns:
            是否成功预热
        """
        success = self._load_model()
        if success:
            # 执行一次虚拟推理确保模型完全加载
            _ = self.analyze("测试")
        return success


# 单例模式 - 全局复用
_sentiment_analyzer: Optional[FinBERTSentimentAnalyzer] = None


def get_sentiment_analyzer(
    model_name: Optional[str] = None,
    device: str = "auto"
) -> FinBERTSentimentAnalyzer:
    """获取全局情感分析器实例（单例模式）.

    Args:
        model_name: 模型名称，None 使用默认
        device: 运行设备

    Returns:
        FinBERTSentimentAnalyzer 实例
    """
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = FinBERTSentimentAnalyzer(
            model_name=model_name,
            device=device
        )
    return _sentiment_analyzer


def reset_sentiment_analyzer():
    """重置全局分析器（用于测试）."""
    global _sentiment_analyzer
    _sentiment_analyzer = None


async def analyze_news_sentiment(
    title: str,
    summary: str = "",
    title_weight: float = 0.7
) -> SentimentResult:
    """分析新闻情感（供数据源调用）.

    优先使用标题，如果有摘要则加权合并分析。

    Args:
        title: 新闻标题
        summary: 新闻摘要
        title_weight: 标题权重（0-1），默认 0.7

    Returns:
        SentimentResult
    """
    analyzer = get_sentiment_analyzer()

    # 只有标题
    if not summary or len(summary) < 10:
        return analyzer.analyze(title)

    # 标题 + 摘要
    title_result = analyzer.analyze(title)
    summary_result = analyzer.analyze(summary[:300])

    # 加权合并
    combined_score = (
        title_result.score * title_weight +
        summary_result.score * (1 - title_weight)
    )

    # 确定最终标签
    if combined_score > 0.1:
        label = SentimentLabel.POSITIVE
    elif combined_score < -0.1:
        label = SentimentLabel.NEGATIVE
    else:
        label = SentimentLabel.NEUTRAL

    # 置信度取平均
    confidence = (title_result.confidence + summary_result.confidence) / 2

    return SentimentResult(
        score=round(combined_score, 3),
        label=label,
        confidence=round(confidence, 3),
        raw_label=f"title:{title_result.raw_label},summary:{summary_result.raw_label}",
        method="finbert_weighted"
    )


def analyze_news_batch(
    news_items: List[Dict],
    text_key: str = "title",
    summary_key: str = "summary"
) -> List[Dict]:
    """批量分析新闻列表.

    Args:
        news_items: 新闻列表，每项是包含 title 和可选 summary 的字典
        text_key: 标题字段名
        summary_key: 摘要字段名

    Returns:
        添加 sentiment 相关字段的 news_items
    """
    analyzer = get_sentiment_analyzer()

    # 构建待分析文本
    texts = []
    for item in news_items:
        title = item.get(text_key, "")
        summary = item.get(summary_key, "")
        if summary and len(summary) > 10:
            text = f"{title}。{summary[:200]}"
        else:
            text = title
        texts.append(text)

    results = analyzer.analyze_batch(texts)

    # 添加结果到原数据
    for item, result in zip(news_items, results):
        item["sentiment"] = result.score
        item["sentiment_label"] = result.label
        item["sentiment_confidence"] = result.confidence
        item["sentiment_method"] = result.method

    return news_items


def calculate_aggregate_sentiment(
    results: List[SentimentResult],
    method: str = "mean"
) -> Dict:
    """计算聚合情感.

    Args:
        results: 情感结果列表
        method: 聚合方法，"mean" 或 "weighted"

    Returns:
        聚合结果字典
    """
    if not results:
        return {
            "score": 0.0,
            "label": "neutral",
            "confidence": 0.0,
            "count": 0
        }

    if method == "weighted":
        # 按置信度加权
        total_weight = sum(r.confidence for r in results)
        if total_weight == 0:
            score = sum(r.score for r in results) / len(results)
        else:
            score = sum(r.score * r.confidence for r in results) / total_weight
    else:
        score = sum(r.score for r in results) / len(results)

    # 确定聚合标签
    if score > 0.1:
        label = "bullish"
    elif score < -0.1:
        label = "bearish"
    else:
        label = "neutral"

    return {
        "score": round(score, 3),
        "label": label,
        "confidence": round(sum(r.confidence for r in results) / len(results), 3),
        "count": len(results),
        "positive_count": sum(1 for r in results if r.label == SentimentLabel.POSITIVE),
        "negative_count": sum(1 for r in results if r.label == SentimentLabel.NEGATIVE),
        "neutral_count": sum(1 for r in results if r.label == SentimentLabel.NEUTRAL),
    }
