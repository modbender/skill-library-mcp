"""
Product Data Synthesizer Module
Author: Tim (sales@dageno.ai)

This module generates e-commerce product data:
- Product title
- Product description
- SKU
- Price
- Inventory
- SEO keywords
- Product categories and tags
"""

import uuid
import hashlib
import random
from typing import Dict, List, Optional, Any


class ProductSynthesizer:
    """
    E-commerce Product Data Synthesizer
    Generates product metadata from basic input
    """

    def __init__(self):
        """Initialize the synthesizer"""
        self.default_currency = "USD"

    def _generate_sku(self, product_name: str, platform: str = "GEN") -> str:
        """
        Generate unique SKU

        Args:
            product_name: Product name
            platform: Platform prefix (e.g., SHOP, WOO)

        Returns:
            SKU string
        """
        # Generate hash from product name
        hash_obj = hashlib.md5(product_name.encode())
        short_hash = hash_obj.hexdigest()[:4].upper()

        # Generate random suffix
        random_suffix = str(uuid.uuid4())[:4].upper()

        return f"{platform}-{short_hash}-{random_suffix}"

    def _generate_price(
        self,
        base_price: float = None,
        min_price: float = 9.99,
        max_price: float = 299.99
    ) -> float:
        """
        Generate price

        Args:
            base_price: Base price (if provided)
            min_price: Minimum price
            max_price: Maximum price

        Returns:
            Price float
        """
        if base_price:
            return round(base_price, 2)

        # Generate random price in range
        return round(random.uniform(min_price, max_price), 2)

    def synthesize(
        self,
        product_name: str,
        category: str = "",
        base_price: float = None,
        description: str = "",
        language: str = "en",
        target_platforms: List[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesize complete product data

        Args:
            product_name: Product name
            category: Product category
            base_price: Base price
            description: Product description
            language: Output language
            target_platforms: Target platforms (shopify/woocommerce)

        Returns:
            Complete product data dictionary
        """
        target_platforms = target_platforms or ["shopify", "woocommerce"]

        # Generate title variations
        title_variations = self._generate_titles(product_name, language)

        # Generate description
        full_description = description or self._generate_description(
            product_name, category, language
        )

        # Generate short description
        short_description = self._generate_short_description(
            product_name, language
        )

        # Generate price
        price = self._generate_price(base_price)

        # Generate compare at price (for sales)
        compare_at_price = round(price * random.uniform(1.2, 1.5), 2) if random.random() > 0.5 else None

        # Generate inventory
        inventory = random.randint(50, 999)

        # Generate SKU for each platform
        skus = {}
        for platform in target_platforms:
            platform_prefix = platform.upper()[:4]
            skus[platform] = self._generate_sku(product_name, platform_prefix)

        # Generate SEO keywords
        seo_keywords = self._generate_seo_keywords(product_name, category)

        # Generate categories and tags
        categories = self._generate_categories(category, language)
        tags = self._generate_tags(product_name, category, language)

        return {
            "title": title_variations["primary"],
            "title_variations": title_variations,
            "description": full_description,
            "short_description": short_description,
            "price": price,
            "compare_at_price": compare_at_price,
            "inventory": inventory,
            "sku": skus.get("shopify", skus.get("woocommerce", "")),
            "skus": skus,
            "seo_keywords": seo_keywords,
            "categories": categories,
            "tags": tags,
            "vendor": self._extract_vendor(product_name),
            "product_type": category or "General",
            "language": language,
            "status": "active"
        }

    def _generate_titles(self, product_name: str, language: str) -> Dict[str, str]:
        """
        Generate title variations

        Args:
            product_name: Base product name
            language: Output language

        Returns:
            Dictionary of title variations
        """
        titles = {
            "primary": product_name,
            "enhanced": f"Premium {product_name} - High Quality",
            "seo": f"{product_name} | Best Price & Fast Shipping",
            "short": product_name[:50]
        }

        # Add language-specific variations
        if language == "zh":
            titles["primary"] = f"{product_name}（高品质）"
            titles["enhanced"] = f"精选 {product_name} - 品质保证"

        return titles

    def _generate_description(
        self,
        product_name: str,
        category: str,
        language: str
    ) -> str:
        """
        Generate product description

        Args:
            product_name: Product name
            category: Product category
            language: Output language

        Returns:
            HTML description
        """
        if language == "en":
            description = f"""
<h2>About This Product</h2>
<p>Introducing our premium <strong>{product_name}</strong>, designed to exceed your expectations. Crafted with precision and attention to detail, this product offers exceptional value and performance.</p>

<h2>Key Features</h2>
<ul>
<li>Premium quality materials</li>
<li>Durable and long-lasting</li>
<li>Modern design</li>
<li>Easy to use</li>
<li>Great value for money</li>
</ul>

<h2>Why Choose {product_name}?</h2>
<p>Our {product_name} stands out from the competition with its superior build quality and thoughtful design. Whether you're a beginner or professional, this product is perfect for your needs.</p>

<p><strong>Order now</strong> and experience the difference!</p>
"""
        elif language == "zh":
            description = f"""
<h2>关于本产品</h2>
<p>为您介绍我们的优质<strong>{product_name}</strong>，精心设计，超出您的期望。精选材料，精细做工，提供卓越的价值和性能。</p>

<h2>主要特点</h2>
<ul>
<li>优质材料</li>
<li>经久耐用</li>
<li>现代设计</li>
<li>易于使用</li>
<li>超高性价比</li>
</ul>

<h2>为什么选择 {product_name}？</h2>
<p>我们的{product_name}以其卓越的品质和贴心的设计在竞争中脱颖而出。无论是新手还是专业人士，这款产品都非常适合您。</p>

<p><strong>立即下单</strong>，体验与众不同！</p>
"""
        else:
            # Default English
            description = f"""
<h2>{product_name}</h2>
<p>Premium quality product with excellent features and great value.</p>

<h3>Features:</h3>
<ul>
<li>High quality materials</li>
<li>Durable construction</li>
<li>Modern design</li>
<li>Easy to use</li>
</ul>

<p>Order now!</p>
"""

        return description.strip()

    def _generate_short_description(
        self,
        product_name: str,
        language: str
    ) -> str:
        """
        Generate short description

        Args:
            product_name: Product name
            language: Output language

        Returns:
            Short description
        """
        if language == "en":
            return f"Premium {product_name} - High quality, great value, fast shipping."
        elif language == "zh":
            return f"优质{product_name}，品质保证，超值之选，快速发货。"
        else:
            return f"High quality {product_name} at great price."

    def _generate_seo_keywords(
        self,
        product_name: str,
        category: str
    ) -> List[str]:
        """
        Generate SEO keywords

        Args:
            product_name: Product name
            category: Product category

        Returns:
            List of SEO keywords
        """
        keywords = [
            product_name.lower(),
            product_name.lower().replace(" ", " - "),
            f"buy {product_name.lower()}",
            f"{product_name.lower()} online",
            f"best {product_name.lower()}",
            f"cheap {product_name.lower()}",
            f"{product_name.lower()} for sale"
        ]

        if category:
            keywords.append(f"{product_name.lower()} {category.lower()}")
            keywords.append(f"{category.lower()} {product_name.lower()}")

        return keywords

    def _generate_categories(
        self,
        category: str,
        language: str
    ) -> List[Dict]:
        """
        Generate product categories

        Args:
            category: Category name
            language: Output language

        Returns:
            List of category dictionaries
        """
        if not category:
            category = "General"

        return [{"id": 0, "name": category}]

    def _generate_tags(
        self,
        product_name: str,
        category: str,
        language: str
    ) -> List[Dict]:
        """
        Generate product tags

        Args:
            product_name: Product name
            category: Category name
            language: Output language

        Returns:
            List of tag dictionaries
        """
        tags = [
            {"name": product_name},
            {"name": "premium"},
            {"name": "quality"},
            {"name": "bestseller"}
        ]

        if category:
            tags.append({"name": category})

        return tags

    def _extract_vendor(self, product_name: str) -> str:
        """
        Extract vendor from product name (simplified)

        Args:
            product_name: Product name

        Returns:
            Vendor name
        """
        # For demo purposes, return a generic vendor
        words = product_name.split()
        if len(words) > 1:
            return f"Brand {words[0].capitalize()}"
        return "Premium Brand"


def synthesize_product(
    product_name: str,
    category: str = "",
    base_price: float = None,
    description: str = "",
    language: str = "en",
    target_platforms: List[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to synthesize product data

    Args:
        product_name: Product name
        category: Product category
        base_price: Base price
        description: Product description
        language: Output language
        target_platforms: Target platforms

    Returns:
        Product data dictionary
    """
    synthesizer = ProductSynthesizer()
    return synthesizer.synthesize(
        product_name=product_name,
        category=category,
        base_price=base_price,
        description=description,
        language=language,
        target_platforms=target_platforms
    )
