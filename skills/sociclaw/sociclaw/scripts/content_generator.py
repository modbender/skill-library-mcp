"""
Module for generating optimized content for X (Twitter) posts.

This module provides functionality to:
- Generate text optimized for X (max 280 chars or threads)
- Adapt tone based on post category
- Include relevant hashtags
- Generate image prompts for the configured image backend
"""

import logging
import json
import random
import re
from dataclasses import dataclass, field
from collections import deque
from typing import List, Dict, Optional
from pathlib import Path

from .scheduler import PostPlan
from .brand_profile import BrandProfile, load_brand_profile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GeneratedPost:
    """
    Generated post with text, image prompt, and metadata.

    Attributes:
        text: Post text (280 chars or thread format)
        image_prompt: Prompt for image generation
        hashtags: List of hashtags to include
        category: Post category (e.g., "market_analysis")
        date: Publication date
        time: Publication time (hour in UTC)
    """
    text: str
    image_prompt: str
    title: str = ""
    body: str = ""
    details: str = ""
    hashtags: List[str] = field(default_factory=list)
    category: str = ""
    date: Optional[str] = None
    time: Optional[int] = None


class ContentGenerator:
    """
    Generate optimized content for X posts based on PostPlan.

    This class loads templates, generates text following X best practices,
    adapts tone by category, and creates image prompts for the image backend.
    """

    # Category-specific tone guidance
    TONES = {
        "market_analysis": "professional",
        "educational": "didactic",
        "news": "informative",
        "tips": "helpful",
        "opinion": "confident",
        "thread": "detailed",
        "meme": "casual"
    }

    # Maximum tweet length
    MAX_TWEET_LENGTH = 280
    RECENT_TEMPLATE_MEMORY = 20
    INSIGHT_SNIPPETS = {
        "market_analysis": [
            "Focus on momentum and confirmation before committing to a direction.",
            "Treat this as a scenario map, not a prediction.",
            "Watch volume and reaction speed around key levels.",
        ],
        "educational": [
            "Start simple, then add complexity only when the basics are stable.",
            "The fastest way to learn is to apply this in a small real example today.",
            "Consistency beats intensity when building skill in Web3.",
        ],
        "news": [
            "The practical impact is usually clearer after the first implementation wave.",
            "Track what changes for users, not just what changes in headlines.",
            "The second-order effects matter more than the announcement itself.",
        ],
        "tips": [
            "A small process upgrade here can prevent costly mistakes later.",
            "Use this as a repeatable habit, not a one-time fix.",
            "Do this once now and you save stress every week.",
        ],
        "opinion": [
            "Agree or disagree, but measure outcomes and adapt fast.",
            "The strongest edge is clear execution, not loud conviction.",
            "Debate is useful only when it improves your next action.",
        ],
        "thread": [
            "Below is a compact framework you can apply immediately.",
            "Use this thread as a checklist you can revisit.",
            "Save this and compare against your next execution cycle.",
        ],
        "meme": [
            "Funny because it is painfully true in every cycle.",
            "If this hit too close, you are probably doing it right.",
            "Laugh now, then fix the process.",
        ],
    }
    CTA_SNIPPETS = {
        "market_analysis": [
            "What is your invalidation level?",
            "What signal are you watching next?",
            "Would you wait for confirmation or front-run this move?",
        ],
        "educational": [
            "Want a step-by-step version?",
            "Should I break this into a checklist?",
            "Which part should I explain with examples?",
        ],
        "news": [
            "Do you see this as noise or structural change?",
            "What is the first consequence you expect?",
            "Who benefits the most if this trend continues?",
        ],
        "tips": [
            "Want more tactical tips like this?",
            "Should I turn this into a daily checklist?",
            "Which operational tip do you want next?",
        ],
        "opinion": [
            "Do you agree or disagree?",
            "What would change your mind here?",
            "What is the strongest counterpoint?",
        ],
        "thread": [
            "Reply if you want part 2.",
            "Should I publish a practical template for this?",
            "Want a one-page summary after this thread?",
        ],
        "meme": [
            "Too real or too far?",
            "Which part felt most accurate?",
            "Tag a friend who needed this today.",
        ],
    }
    INSIGHT_SNIPPETS_PT = {
        "market_analysis": [
            "Trate isso como mapa de cenarios, nao como previsao.",
            "Observe volume e reacao nos niveis-chave antes de agir.",
            "Gestao de risco primeiro, conviccao depois.",
        ],
        "educational": [
            "Comece simples e so adicione complexidade quando a base estiver clara.",
            "Aprendizado real vem de aplicacao pratica imediata.",
            "Consistencia vence intensidade no longo prazo.",
        ],
        "news": [
            "O impacto real aparece na execucao, nao no anuncio.",
            "Acompanhe mudanca de comportamento do usuario.",
            "Efeito de segunda ordem costuma ser o mais relevante.",
        ],
        "tips": [
            "Uma melhoria pequena no processo evita erros caros depois.",
            "Transforme isso em habito, nao em acao unica.",
            "Padrao simples e repetivel traz mais resultado.",
        ],
        "opinion": [
            "Opinioes so valem quando melhoram a execucao.",
            "A vantagem vem de clareza e disciplina operacional.",
            "Teste, meca e ajuste rapido.",
        ],
        "thread": [
            "Abaixo esta um framework direto para aplicar hoje.",
            "Use esta thread como checklist operacional.",
            "Salve para comparar com seu proximo ciclo de execucao.",
        ],
        "meme": [
            "Engracado porque e real em quase todo ciclo.",
            "Se doeu, provavelmente era necessario.",
            "Ria agora, ajuste o processo depois.",
        ],
    }
    CTA_SNIPPETS_PT = {
        "market_analysis": [
            "Qual seria seu nivel de invalidacao?",
            "Que sinal voce esta esperando para confirmar?",
            "Voce esperaria confirmacao ou anteciparia o movimento?",
        ],
        "educational": [
            "Quer que eu quebre isso em checklist?",
            "Quer exemplos praticos em sequencia?",
            "Qual parte voce quer aprofundar?",
        ],
        "news": [
            "Isso e ruido ou mudanca estrutural?",
            "Qual primeira consequencia voce espera?",
            "Quem mais se beneficia se essa tendencia continuar?",
        ],
        "tips": [
            "Quer mais taticas praticas como essa?",
            "Quer uma rotina diaria com esses pontos?",
            "Qual dica operacional devo cobrir em seguida?",
        ],
        "opinion": [
            "Voce concorda ou discorda?",
            "O que faria voce mudar de opiniao?",
            "Qual o melhor contraponto para isso?",
        ],
        "thread": [
            "Quer parte 2 com execucao pratica?",
            "Quer um template pronto para aplicar?",
            "Quer resumo em uma pagina no final?",
        ],
        "meme": [
            "Foi longe ou foi real demais?",
            "Qual parte te representou mais?",
            "Marca alguem que precisava ler isso hoje.",
        ],
    }

    def __init__(
        self,
        templates_path: Optional[Path] = None,
        brand_profile_path: Optional[Path] = None,
        brand_profile: Optional[BrandProfile] = None,
    ):
        """
        Initialize the ContentGenerator.

        Args:
            templates_path: Path to post_templates.json file.
                          If None, uses default location.
        """
        if templates_path is None:
            # Default to templates/ directory relative to this file
            templates_path = Path(__file__).parent.parent / "templates" / "post_templates.json"

        self.templates_path = templates_path
        self.templates: Dict[str, List[Dict]] = {}
        self._recent_template_keys: deque[str] = deque(maxlen=self.RECENT_TEMPLATE_MEMORY)
        self.brand_profile_path = brand_profile_path
        self.brand_profile = brand_profile or load_brand_profile(brand_profile_path)
        self._load_templates()

    def _load_templates(self) -> None:
        """Load post templates from JSON file."""
        try:
            if not self.templates_path.exists():
                logger.warning(f"Templates file not found at {self.templates_path}")
                self._create_default_templates()
                return

            with open(self.templates_path, 'r', encoding='utf-8') as f:
                self.templates = json.load(f)

            logger.info(f"Loaded {len(self.templates)} template categories")
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            self._create_default_templates()

    def _create_default_templates(self) -> None:
        """Create minimal default templates if file doesn't exist."""
        self.templates = {
            "market_analysis": [
                {
                    "structure": "{topic} analysis: {insight}",
                    "example": "Bitcoin analysis: Testing critical $40k support level"
                }
            ],
            "educational": [
                {
                    "structure": "How to {action}: {tip}",
                    "example": "How to start in DeFi: Begin with stablecoins"
                }
            ],
            "news": [
                {
                    "structure": "Breaking: {headline}",
                    "example": "Breaking: Major exchange announces Base integration"
                }
            ],
            "tips": [
                {
                    "structure": "Pro tip: {advice}",
                    "example": "Pro tip: Always verify contract addresses"
                }
            ],
            "opinion": [
                {
                    "structure": "{hot_take} {reasoning}",
                    "example": "L2s will flip L1s. Lower fees = better UX."
                }
            ],
            "thread": [
                {
                    "structure": "Thread: {topic}\n\n1/ {intro}",
                    "example": "Thread: Understanding gas fees\n\n1/ Let's break it down"
                }
            ],
            "meme": [
                {
                    "structure": "{setup}\n\n{punchline}",
                    "example": "Me: I'll just check the charts\n\nAlso me: *still staring 3h later*"
                }
            ]
        }

    def generate_post(self, plan: PostPlan) -> GeneratedPost:
        """
        Generate a complete post from a PostPlan.

        Args:
            plan: PostPlan with date, time, category, topic, and hashtags

        Returns:
            GeneratedPost with text, image_prompt, and metadata
        """
        try:
            # Get templates for this category
            category_templates = self.templates.get(plan.category, [])
            if not category_templates:
                logger.warning(f"No templates for category {plan.category}")
                category_templates = list(self.templates.values())[0]

            # Select template (avoiding recent repetition)
            template = self._choose_template(plan, category_templates)

            # Generate content blocks
            blocks = self._generate_content_blocks(plan, template)

            # Generate image prompt
            image_prompt = self._generate_image_prompt(plan, f"{blocks['title']} {blocks['body']}".strip())

            # Create GeneratedPost
            post = GeneratedPost(
                text=blocks["text"],
                image_prompt=image_prompt,
                title=blocks["title"],
                body=blocks["body"],
                details=blocks["details"],
                hashtags=plan.hashtags[:3],  # Limit to 3 hashtags
                category=plan.category,
                date=plan.date.strftime("%Y-%m-%d"),
                time=plan.time
            )

            logger.info(f"Generated post for {plan.category}: {blocks['text'][:50]}...")
            return post

        except Exception as e:
            logger.error(f"Error generating post: {e}")
            raise

    def _choose_template(self, plan: PostPlan, category_templates: List[Dict]) -> Dict:
        """
        Choose a template while reducing repeated template reuse.
        """
        if len(category_templates) == 1:
            chosen = category_templates[0]
            signature = f"{plan.category}:{chosen.get('structure', '')}"
            self._recent_template_keys.append(signature)
            return chosen

        candidates = []
        for tpl in category_templates:
            signature = f"{plan.category}:{tpl.get('structure', '')}"
            if signature not in self._recent_template_keys:
                candidates.append((tpl, signature))

        if not candidates:
            tpl = random.choice(category_templates)
            signature = f"{plan.category}:{tpl.get('structure', '')}"
        else:
            tpl, signature = random.choice(candidates)

        self._recent_template_keys.append(signature)
        return tpl

    def _generate_content_blocks(self, plan: PostPlan, template: Dict) -> Dict[str, str]:
        """
        Generate structured content blocks with more depth and less repetition.

        Args:
            plan: PostPlan with topic and category
            template: Template dict with structure and examples

        Returns:
            Dict with title/body/text/details
        """
        # Build base text based on template structure
        if "structure" in template:
            base_text = template["structure"]

            # Personality-aware replacement bank.
            persona = self._persona_profile()
            replacements = {
                "topic": plan.topic,
                "insight": random.choice(
                    [
                        f"a high-signal setup from a {persona['tone_modifier']} lens",
                        "a practical angle you can act on now",
                        "an overlooked lever with asymmetric upside",
                    ]
                ),
                "trend": random.choice(["momentum building", "trend consolidating", "expansion phase starting"]),
                "conclusion": random.choice(
                    [
                        "Manage risk first, then size conviction.",
                        "Wait for structure confirmation before scaling.",
                        "Track reaction quality, not just direction.",
                    ]
                ),
                "action": f"understand {plan.topic}",
                "tip": random.choice(["Start with one concrete example", "Define your risk limits first", "Use a repeatable process"]),
                "headline": plan.topic,
                "impact": random.choice(["Potentially meaningful for adoption", "Could reshape short-term positioning", "Likely to influence execution decisions"]),
                "detail": random.choice(["Implementation details will matter", "Watch how users actually adapt", "Monitor whether usage follows narrative"]),
                "context": random.choice(["Worth keeping on your radar", "Context is still evolving", "Early signal, not final verdict"]),
                "advice": plan.topic,
                "benefit": random.choice(["Security first", "Lower downside risk", "Higher consistency over time"]),
                "reasoning": random.choice(["Execution quality compounds.", "Discipline is the edge.", "Simple systems outperform reactive decisions."]),
                "hot_take": plan.topic,
                "statement": plan.topic,
                "intro": "Understanding the fundamentals",
                "point": "Key takeaway you can apply today",
                "opening": "Start with the core concept",
                "key_point": "Focus on risk management",
                "setup": plan.topic,
                "punchline": random.choice(persona["punchlines"]),
                "scenario": plan.topic,
                "explanation": "Keep it simple and consistent",
                "key_takeaway": "Safety and patience win",
            }

            for key, value in replacements.items():
                base_text = base_text.replace(f"{{{key}}}", value)

            # Replace any remaining placeholders
            base_text = re.sub(r"{[^}]+}", "details", base_text)
        else:
            # Fallback to example if no structure
            base_text = template.get("example", plan.topic)

        title = self._build_title(plan, base_text)
        body = self._build_body(plan, base_text)
        cta = random.choice(self._cta_pool(plan.category))

        text = f"{title}\n{body}\n{cta}".strip()

        # Enforce brand constraints before hashtags/length handling.
        text = self._apply_brand_constraints(text)

        # Add hashtags if they fit
        hashtags_text = " ".join(f"#{tag}" for tag in plan.hashtags[:3])

        # Check if we can fit hashtags within 280 chars
        if len(text) + len(hashtags_text) + 1 <= self.MAX_TWEET_LENGTH:
            text = f"{text} {hashtags_text}"
        elif len(text) > self.MAX_TWEET_LENGTH:
            # Truncate if too long
            available_space = self.MAX_TWEET_LENGTH - len(hashtags_text) - 4  # -4 for " ..."
            text = text[:available_space] + "..."
            if hashtags_text:
                text = f"{text} {hashtags_text}"

        if self._resolve_content_language() == "pt":
            details = (
                f"Titulo: {title}\n"
                f"Conteudo: {body}\n"
                f"CTA: {cta}\n"
                f"Topico: {plan.topic}\n"
                f"Categoria: {plan.category}"
            )
        else:
            details = (
                f"Title: {title}\n"
                f"Body: {body}\n"
                f"CTA: {cta}\n"
                f"Topic: {plan.topic}\n"
                f"Category: {plan.category}"
            )

        persona = self._persona_profile()
        if persona["signature_opener"]:
            details = f"{details}\nOpening Style: {persona['signature_opener']}"
        if persona["visual_style"]:
            details = f"{details}\nVisual Style: {persona['visual_style']}"
        if persona["traits"]:
            details = f"{details}\nPersonality Traits: {', '.join(persona['traits'])}"
        if persona["goals"]:
            details = f"{details}\nContent Goals: {', '.join(persona['goals'])}"

        if cta_style := persona["cta_style"]:
            text = self._enforce_cta_style(text, str(cta_style))

        return {
            "title": title.strip(),
            "body": body.strip(),
            "text": text.strip(),
            "details": details.strip(),
        }

    def _enforce_cta_style(self, text: str, style: str) -> str:
        if style not in {"question", "invitation", "challenge"}:
            return text
        if style == "question":
            if "?" not in text:
                return f"{text} What is your move?"
            return text
        if style == "invitation":
            if "dm" not in text.lower() and "comment" not in text.lower():
                return f"{text} Tell me what worked for you and I will DM a practical checklist."
            return text
        return f"{text} If you disagree, tell me where it breaks."

    def _persona_profile(self) -> Dict[str, object]:
        """Build a compact, normalized persona payload from brand profile data."""
        profile = self.brand_profile
        signature_openers = [s for s in profile.signature_openers if s.strip()]
        return {
            "traits": [t for t in profile.personality_traits if t.strip()],
            "goals": [g for g in profile.content_goals if g.strip()],
            "signature_opener": random.choice(signature_openers) if signature_openers else "",
            "visual_style": profile.visual_style or "",
            "cta_style": profile.cta_style or "question",
            "punchlines": [
                "Execution quality compounds, not hype.",
                "Consistency beats perfect timing every single week.",
                "Small process upgrades beat loud intentions.",
            ],
            "tone_modifier": profile.voice_tone.strip() if profile.voice_tone else "practical",
        }

    def _resolve_content_language(self) -> str:
        lang = (self.brand_profile.content_language or "").strip().lower()
        if not lang:
            return "en"
        if lang.startswith("pt"):
            return "pt"
        return "en"

    def _insight_pool(self, category: str) -> List[str]:
        if self._resolve_content_language() == "pt":
            return self.INSIGHT_SNIPPETS_PT.get(category, self.INSIGHT_SNIPPETS_PT["tips"])
        return self.INSIGHT_SNIPPETS.get(category, self.INSIGHT_SNIPPETS["tips"])

    def _cta_pool(self, category: str) -> List[str]:
        if self._resolve_content_language() == "pt":
            return self.CTA_SNIPPETS_PT.get(category, self.CTA_SNIPPETS_PT["tips"])
        return self.CTA_SNIPPETS.get(category, self.CTA_SNIPPETS["tips"])

    def _build_title(self, plan: PostPlan, base_text: str) -> str:
        primary = base_text.strip().splitlines()[0]
        if self._resolve_content_language() == "pt" and "Thread:" in primary:
            primary = primary.replace("Thread:", "Thread:")
        # Keep titles compact and scannable.
        if len(primary) > 90:
            primary = primary[:87] + "..."
        return primary

    def _build_body(self, plan: PostPlan, base_text: str) -> str:
        insight = random.choice(self._insight_pool(plan.category))
        connector = "sobre" if self._resolve_content_language() == "pt" else "about"
        body = f"{plan.topic} ({connector} {plan.category.replace('_', ' ')}): {insight}"
        # If base text already contains richer context, blend it in lightly.
        normalized = re.sub(r"\s+", " ", base_text).strip()
        if normalized and len(normalized) < 140:
            body = f"{normalized} {insight}"
        if len(body) > 170:
            body = body[:167] + "..."
        return body

    def _apply_brand_constraints(self, text: str) -> str:
        """
        Apply optional Brand Brain rules:
        - remove forbidden terms
        - inject one required keyword when missing
        """
        profile = self.brand_profile

        # Remove blocked terms (case-insensitive, whole-word).
        for blocked in profile.do_not_say:
            token = blocked.strip()
            if not token:
                continue
            text = re.sub(rf"\b{re.escape(token)}\b", "", text, flags=re.IGNORECASE)

        # Ensure at least one required keyword appears.
        if profile.keywords:
            has_any_keyword = any(k.lower() in text.lower() for k in profile.keywords if k.strip())
            if not has_any_keyword:
                primary = profile.keywords[0].strip()
                if primary:
                    text = f"{text} {primary}".strip()

        # Cleanup whitespace left by removals.
        text = re.sub(r"\s{2,}", " ", text).strip()
        return text

    def _generate_image_prompt(self, plan: PostPlan, text: str) -> str:
        """
        Generate an image prompt based on content.

        Args:
            plan: PostPlan with category and topic
            text: Generated post text

        Returns:
            Image generation prompt string
        """
        # Base style for crypto/web3 content, enriched with the brand profile.
        base_style = "modern, professional, crypto themed, vibrant colors"
        persona = self._persona_profile()
        style_hints = [base_style]
        if persona["tone_modifier"]:
            style_hints.append(f"tone: {persona['tone_modifier']}")
        if persona["visual_style"]:
            style_hints.append(persona["visual_style"])
        base_style_with_profile = ", ".join(style_hints)

        # Category-specific visual styles
        category_styles = {
            "market_analysis": f"financial chart, {base_style_with_profile}, data visualization",
            "educational": f"infographic style, {base_style_with_profile}, clean layout",
            "news": f"breaking news style, {base_style_with_profile}, bold typography",
            "tips": f"minimalist design, {base_style_with_profile}, icon-based",
            "opinion": f"bold statement, {base_style_with_profile}, striking visuals",
            "thread": f"thread visualization, {base_style_with_profile}, numbered layout",
            "meme": f"meme style, {base_style_with_profile}, humorous, relatable"
        }

        style = category_styles.get(plan.category, base_style)

        brand_context_parts = []
        if self.brand_profile.name:
            brand_context_parts.append(f"brand {self.brand_profile.name}")
        if self.brand_profile.voice_tone:
            brand_context_parts.append(f"tone {self.brand_profile.voice_tone}")
        if self.brand_profile.key_themes:
            brand_context_parts.append(f"themes {', '.join(self.brand_profile.key_themes[:3])}")

        brand_context = ", ".join(brand_context_parts)
        if brand_context:
            brand_context = f", {brand_context}"

        # Build prompt
        prompt = f"{plan.topic}, {style}{brand_context}, 1024x1024, high quality, digital art"

        return prompt

    def generate_batch(self, plans: List[PostPlan]) -> List[GeneratedPost]:
        """
        Generate multiple posts from a list of PostPlans.

        Args:
            plans: List of PostPlan objects

        Returns:
            List of GeneratedPost objects
        """
        posts = []
        for plan in plans:
            try:
                post = self.generate_post(plan)
                posts.append(post)
            except Exception as e:
                logger.error(f"Error generating post for plan {plan}: {e}")
                continue

        logger.info(f"Generated {len(posts)} posts from {len(plans)} plans")
        return posts
