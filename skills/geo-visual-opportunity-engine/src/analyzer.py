"""
Opportunity Analyzer Module
Author: Tim (sales@dageno.ai)

This module handles GEO opportunity analysis and generates prompts
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class OpportunityAnalyzer:
    """
    GEO Opportunity Analyzer
    Analyzes brand/product/keywords to identify visual opportunities
    """

    def __init__(self):
        """Initialize the analyzer"""
        self.skill_version = "geo_v2.0"

    def analyze(
        self,
        brand: str,
        product: str,
        core_keyword: str,
        country: str,
        language: str = "en",
        competitors: Optional[List[str]] = None,
        platform_focus: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze and generate GEO opportunities

        Args:
            brand: Brand name
            product: Product name
            core_keyword: Core keyword
            country: Target country
            language: Output language
            competitors: List of competitors
            platform_focus: Target AI platforms

        Returns:
            Complete analysis result with opportunities, prompts, and drafts
        """
        # Default values
        competitors = competitors or []
        platform_focus = platform_focus or ["ChatGPT", "Perplexity", "Grok", "Gemini"]

        # Generate opportunities
        opportunities = self._generate_opportunities(
            brand, product, core_keyword, country, platform_focus, competitors
        )

        # Generate image prompts
        image_prompts = self._generate_image_prompts(opportunities, language)

        # Generate content drafts
        content_drafts = self._generate_content_drafts(opportunities, language)

        # Generate posting schedule
        posting_schedule = self._generate_posting_schedule(country)

        # Build result
        result = {
            "opportunities": opportunities,
            "image_prompts": image_prompts,
            "content_drafts": content_drafts,
            "posting_schedule": posting_schedule,
            "meta": {
                "skill_version": self.skill_version,
                "generated_at": datetime.now().isoformat() + "Z",
                "input_echo": {
                    "brand": brand,
                    "product": product,
                    "core_keyword": core_keyword,
                    "country": country,
                    "language": language,
                    "competitors": competitors
                }
            }
        }

        return result

    def _generate_opportunities(
        self,
        brand: str,
        product: str,
        core_keyword: str,
        country: str,
        platform_focus: List[str],
        competitors: List[str]
    ) -> List[Dict]:
        """Generate opportunity list"""
        opportunities = []

        # Opportunity 1: Explain/ Educational
        opportunities.append({
            "id": "op1",
            "title": f"What is {core_keyword}? Complete guide for {country.upper()}",
            "intent_type": "explain",
            "search_volume_estimate": 12000,
            "platforms": platform_focus[:2],
            "priority_score": 95,
            "brand_gap_summary": f"{brand} lacks comprehensive educational content about {core_keyword}.",
            "source_gap_summary": f"AI search results mainly cite competitors; {brand} is not mentioned.",
            "recommended_action": f"Publish comprehensive guide about {core_keyword} with visual assets."
        })

        # Opportunity 2: Comparison
        opportunities.append({
            "id": "op2",
            "title": f"{brand} vs Competitors: Which is better for {core_keyword}?",
            "intent_type": "compare",
            "search_volume_estimate": 8500,
            "platforms": platform_focus[1:3] if len(platform_focus) > 2 else platform_focus,
            "priority_score": 88,
            "brand_gap_summary": f"{brand} has no direct comparison content against {competitors[0] if competitors else 'competitors'}.",
            "source_gap_summary": "Users searching comparisons get competitor-dominated results.",
            "recommended_action": "Create comparison landing page with data."
        })

        # Opportunity 3: Use Case
        opportunities.append({
            "id": "op3",
            "title": f"Real-world use cases: How to use {product} for {core_keyword}",
            "intent_type": "use_case",
            "search_volume_estimate": 15000,
            "platforms": platform_focus,
            "priority_score": 92,
            "brand_gap_summary": f"{brand} has product specs but lacks real-world usage content.",
            "source_gap_summary": "AI recommends competitors for practical use cases.",
            "recommended_action": "Publish user stories and scenario guides."
        })

        return opportunities

    def _generate_image_prompts(
        self,
        opportunities: List[Dict],
        language: str
    ) -> List[Dict]:
        """Generate image prompts for each opportunity"""
        prompts = []

        for opp in opportunities:
            opp_id = opp["id"]
            product_context = opp["title"]

            prompts.append({
                "opportunity_id": opp_id,
                "white_info": {
                    "prompt": f"White-background e-commerce infographic showing {product_context}, clean minimalist design, soft directional lighting, 8k resolution, professional product photography. DO NOT EMBED TEXT; reserve overlay area at bottom 20%.",
                    "suggested_overlay_text": {
                        "title": f"{product_context[:50]}",
                        "bullets": ["Key benefit 1", "Key benefit 2", "Key benefit 3"]
                    },
                    "size_recommendation": "1200x1800"
                },
                "lifestyle": {
                    "prompt": f"Lifestyle photography: person using product in real场景, natural lighting, golden hour, candid moment, 8k resolution, photorealistic. DO NOT EMBED TEXT; reserve overlay area.",
                    "suggested_overlay_text": {
                        "main": "Real-world application",
                        "sub": "See how it works"
                    },
                    "size_recommendation": "1200x628"
                },
                "hero": {
                    "prompt": f"Premium hero banner: {product_context}, dramatic lighting, dark gradient background, commercial photography style, cinematic composition, 8k resolution. DO NOT EMBED TEXT; reserve overlay area.",
                    "suggested_overlay_text": {
                        "headline": product_context[:40],
                        "cta": "Learn More"
                    },
                    "size_recommendation": "1600x900"
                }
            })

        return prompts

    def _generate_content_drafts(
        self,
        opportunities: List[Dict],
        language: str
    ) -> List[Dict]:
        """Generate content drafts for each opportunity"""
        drafts = []

        for opp in opportunities:
            opp_id = opp["id"]
            title = opp["title"]
            intent_type = opp["intent_type"]

            # Generate body based on intent type
            if intent_type == "explain":
                body = f"{title} - A comprehensive guide. This content explains everything you need to know about the topic. Our product offers the best solution with advanced features and reliable performance. Learn more about how we can help you achieve your goals."
            elif intent_type == "compare":
                body = f"Comparing our product with competitors. Our solution provides superior features, better value, and outstanding performance. See why choose us over others in the market. Detailed analysis and real test results show the difference."
            else:  # use_case
                body = f"Real-world applications and use cases. See how our product solves real problems in various scenarios. From daily use to professional applications, our product delivers exceptional results. Discover the possibilities today."

            drafts.append({
                "opportunity_id": opp_id,
                "title": title,
                "short_description": f"Learn about {title[:50]}...",
                "body": body,
                "seo_keywords": [title.lower().split()[0], "product", "review"],
                "suggested_cta": "Learn More"
            })

        return drafts

    def _generate_posting_schedule(self, country: str) -> Dict:
        """Generate 4-week posting schedule"""
        return {
            "country": country,
            "week_by_week": [
                {
                    "week": 1,
                    "channels": [
                        {"name": "X", "posts": 2},
                        {"name": "LinkedIn", "posts": 1},
                        {"name": "Instagram", "posts": 1}
                    ],
                    "focus": "Launch explainer content and white info graphics",
                    "kpis": ["impressions", "engagement_rate"]
                },
                {
                    "week": 2,
                    "channels": [
                        {"name": "X", "posts": 2},
                        {"name": "YouTube", "posts": 1},
                        {"name": "Facebook", "posts": 1}
                    ],
                    "focus": "Release comparison content with lifestyle images",
                    "kpis": ["clicks", "time_on_page"]
                },
                {
                    "week": 3,
                    "channels": [
                        {"name": "TikTok", "posts": 2},
                        {"name": "Instagram", "posts": 2},
                        {"name": "X", "posts": 1}
                    ],
                    "focus": "Share user stories and use case scenarios",
                    "kpis": ["views", "shares"]
                },
                {
                    "week": 4,
                    "channels": [
                        {"name": "LinkedIn", "posts": 1},
                        {"name": "X", "posts": 2},
                        {"name": "Email", "posts": 1}
                    ],
                    "focus": "Recap campaign and optimize based on performance",
                    "kpis": ["conversions", "roi"]
                }
            ],
            "first_publish_guidelines": "Publish content on product domain with proper SEO markup; schedule social posts between Tue-Thu for optimal engagement.",
            "recap_and_iterations": "Review performance metrics at day 14 and 28; iterate based on engagement data."
        }
