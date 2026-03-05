"""
E-commerce Automator - Main Entry Point
Author: Tim (sales@dageno.ai)
Version: 3.0.0

This module provides the main interface for the E-commerce Automator,
integrating:
- Nano Banana 2: AI product image generation (Google Gemini)
- Product Synthesizer: Auto-generate product titles, descriptions, SKU, prices
- Shopify: Publish Shopify Admin API
 products via- WooCommerce: Publish products via WooCommerce REST API
"""

import os
import json
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path

from .analyzer import OpportunityAnalyzer
from .nano_banana_2 import NanoBanana2, generate_images_from_prompts
from .shopify import ShopifyIntegration
from .woocommerce import WooCommerceIntegration
from .product_synthesizer import ProductSynthesizer
from .config import AUTHOR_INFO, SKILL_CONFIG, validate_api_key


class EcommerceAutomator:
    """
    Main Engine for E-commerce Automation
    Workflow:
    1. Generate product images (Nano Banana 2)
    2. Synthesize product data (title, description, SKU, price)
     Shopify and3. Publish to/or WooCommerce
    """

    def __init__(
        self,
        google_api_key: Optional[str] = None,
        shopify_store_url: Optional[str] = None,
        shopify_access_token: Optional[str] = None,
        woo_store_url: Optional[str] = None,
        woo_consumer_key: Optional[str] = None,
        woo_consumer_secret: Optional[str] = None
    ):
        """
        Initialize the E-commerce Automator

        Args:
            google_api_key: Google API Key for Nano Banana 2
            shopify_store_url: Shopify store URL
            shopify_access_token: Shopify Admin API access token
            woo_store_url: WooCommerce store URL
            woo_consumer_key: WooCommerce API consumer key
            woo_consumer_secret: WooCommerce API consumer secret
        """
        # Initialize modules
        self.analyzer = OpportunityAnalyzer()
        self.image_generator = NanoBanana2(api_key=google_api_key)
        self.product_synthesizer = ProductSynthesizer()

        # Initialize integrations
        self.shopify = ShopifyIntegration(
            store_url=shopify_store_url,
            access_token=shopify_access_token
        )

        self.woocommerce = WooCommerceIntegration(
            store_url=woo_store_url,
            consumer_key=woo_consumer_key,
            consumer_secret=woo_consumer_secret
        )

        self.author_info = AUTHOR_INFO

        print(f"[INFO] E-commerce Automator v{SKILL_CONFIG['version']}")
        print(f"[AUTHOR] {self.author_info['name']} - {self.author_info['email']}")
        print(f"[WEBSITE] {self.author_info['website']}")

        # Check connections
        self._check_connections()

    def run_complete_workflow(
        self,
        product_input: str,
        country: str = "us",
        language: str = "en",
        generate_images: bool = True,
        publish_to_shopify: bool = False,
        publish_to_woocommerce: bool = False,
        output_dir: str = "output"
    ) -> Dict[str, Any]:
        """
        Unified workflow: One input completes the entire process.
        This is the main entry point for complete automation.

        Args:
            product_input: Single keyword or product name (e.g., "wireless headphones")
            country: Target country code (default: "us")
            language: Output language code (default: "en")
            generate_images: Whether to generate AI images (default: True)
            publish_to_shopify: Whether to publish to Shopify (default: False)
            publish_to_woocommerce: Whether to publish to WooCommerce (default: False)
            output_dir: Output directory for results (default: "output")

        Returns:
            Complete result dictionary with all outputs:
            - product_data: Synthesized product information
            - generated_images: List of generated image URLs
            - geo_analysis: GEO opportunity analysis results
            - publish_results: Publishing status for each platform

        Example:
            >>> from src.main import EcommerceAutomator
            >>> automator = EcommerceAutomator(google_api_key="your-api-key")
            >>> result = automator.run_complete_workflow("wireless bluetooth headphones")
            >>> print(result['product_data']['title'])
        """
        print("\n" + "=" * 60)
        print(f"[WORKFLOW] Starting Complete Workflow for: {product_input}")
        print(f"[VERSION] v{SKILL_CONFIG['version']}")
        print("=" * 60)

        # Validate input
        if not product_input or not product_input.strip():
            return {
                "status": "error",
                "message": "Invalid input: product_input cannot be empty",
                "error_code": "INVALID_INPUT"
            }

        product_input = product_input.strip()
        print(f"\n[INPUT] Product: {product_input}")
        print(f"[TARGET] Country: {country}, Language: {language}")

        result = {
            "input": product_input,
            "country": country,
            "language": language,
            "status": "in_progress",
            "steps_completed": []
        }

        try:
            # Step 1: Analyze GEO opportunities
            print(f"\n[STEP 1/4] Analyzing GEO opportunities...")
            analysis_result = self.analyzer.analyze(
                brand="AutoBrand",
                product=product_input,
                core_keyword=product_input,
                country=country,
                language=language,
                competitors=None,
                platform_focus=None
            )
            result["geo_analysis"] = analysis_result
            result["steps_completed"].append("geo_analysis")
            print(f"[SUCCESS] Found {len(analysis_result.get('opportunities', []))} opportunities")

            # Step 2: Synthesize product data
            print(f"\n[STEP 2/4] Synthesizing product data...")
            first_opportunity = analysis_result.get("opportunities", [{}])[0] if analysis_result.get("opportunities") else {}

            product_data = self.product_synthesizer.synthesize(
                product_name=product_input,
                category=first_opportunity.get("category", "General"),
                base_price=None,
                description=first_opportunity.get("content_body", ""),
                language=language,
                target_platforms=["shopify", "woocommerce"]
            )
            result["product_data"] = product_data
            result["steps_completed"].append("product_synthesis")
            print(f"[SUCCESS] Generated: {product_data['title']}")
            print(f"[PRICE] ${product_data['price']}, [SKU] {product_data['sku']}")

            # Step 3: Generate images
            generated_images = []
            if generate_images:
                print(f"\n[STEP 3/4] Generating product images...")

                if not validate_api_key():
                    print("[WARNING] No Google API Key found. Images will be simulated.")

                # Use the first opportunity's image prompts
                image_prompts = analysis_result.get("image_prompts", [])
                if image_prompts:
                    prompt_group = image_prompts[0]
                    prompts_to_generate = []
                    for style in ["white_info", "lifestyle", "hero"]:
                        if style in prompt_group:
                            prompts_to_generate.append({
                                "style": style,
                                "prompt": prompt_group[style]["prompt"]
                            })

                    image_results = self.image_generator.generate_batch(
                        prompts_to_generate,
                        f"product_{product_data['sku']}"
                    )
                    generated_images = image_results
                    result["generated_images"] = image_results
                    result["steps_completed"].append("image_generation")
                    print(f"[SUCCESS] Generated {len(generated_images)} images")
                else:
                    print("[WARNING] No image prompts available")
            else:
                print(f"\n[STEP 3/4] Skipping image generation (disabled)")

            # Step 4: Publish to platforms
            print(f"\n[STEP 4/4] Publishing to platforms...")
            publish_results = {
                "shopify": None,
                "woocommerce": None
            }

            # Get the main image URL
            main_image_url = generated_images[0].get("image_url") if generated_images else None

            # Publish to Shopify
            if publish_to_shopify and self.shopify.connected:
                shopify_result = self._publish_to_shopify(product_data, main_image_url)
                publish_results["shopify"] = shopify_result
                if shopify_result.get("success"):
                    print(f"[SUCCESS] Published to Shopify: ID {shopify_result.get('product_id')}")
                else:
                    print(f"[ERROR] Shopify: {shopify_result.get('error')}")
            elif publish_to_shopify and not self.shopify.connected:
                print(f"[WARNING] Shopify not connected. Skipping.")

            # Publish to WooCommerce
            if publish_to_woocommerce and self.woocommerce.connected:
                woo_result = self._publish_to_woocommerce(product_data, main_image_url)
                publish_results["woocommerce"] = woo_result
                if woo_result.get("success"):
                    print(f"[SUCCESS] Published to WooCommerce: ID {woo_result.get('product_id')}")
                else:
                    print(f"[ERROR] WooCommerce: {woo_result.get('error')}")
            elif publish_to_woocommerce and not self.woocommerce.connected:
                print(f"[WARNING] WooCommerce not connected. Skipping.")

            result["publish_results"] = publish_results
            result["steps_completed"].append("publishing")

            # Save result to file
            output_path = Path(output_dir) / f"workflow_result_{product_data['sku']}.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            result["status"] = "completed"
            result["output_file"] = str(output_path)

            print("\n" + "=" * 60)
            print(f"[WORKFLOW COMPLETED] All steps finished successfully!")
            print(f"[OUTPUT] {output_path}")
            print("=" * 60)

            return result

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            print(f"\n[ERROR] Workflow failed: {str(e)}")
            return result

    def _check_connections(self) -> None:
        """Check API connections status"""
        print("\n[CONNECTION CHECK]")

        # Check Shopify
        if self.shopify.connected:
            shopify_status = self.shopify.test_connection()
            if shopify_status.get("connected"):
                print(f"[SHOPIFY] Connected - {shopify_status.get('shop_name')}")
            else:
                print(f"[SHOPIFY] Configured but test failed: {shopify_status.get('error')}")
        else:
            print("[SHOPIFY] Not configured")

        # Check WooCommerce
        if self.woocommerce.connected:
            woo_status = self.woocommerce.test_connection()
            if woo_status.get("connected"):
                print(f"[WOOCOMMERCE] Connected - {woo_status.get('site_title')}")
            else:
                print(f"[WOOCOMMERCE] Configured but test failed: {woo_status.get('error')}")
        else:
            print("[WOOCOMMERCE] Not configured")

    def run_geo_analysis(
        self,
        brand: str,
        product: str,
        core_keyword: str,
        country: str,
        language: str = "en",
        competitors: Optional[List[str]] = None,
        platform_focus: Optional[List[str]] = None,
        generate_images: bool = True
    ) -> Dict[str, Any]:
        """
        Run GEO opportunity analysis with image generation

        Args:
            brand: Brand name
            product: Product name
            core_keyword: Core keyword/phrase
            country: Target country code
            language: Output language code
            competitors: List of competitor brands
            platform_focus: Target AI platforms
            generate_images: Whether to generate images

        Returns:
            Complete result with opportunities, prompts, images, and schedule
        """
        print(f"\n[STEP 1] Analyzing: {brand} - {product}")
        print(f"[KEYWORD] {core_keyword}")
        print(f"[TARGET] {country} / {language}")

        # Analyze opportunities
        print("\n[STEP 2] Generating opportunities and prompts...")
        analysis_result = self.analyzer.analyze(
            brand=brand,
            product=product,
            core_keyword=core_keyword,
            country=country,
            language=language,
            competitors=competitors,
            platform_focus=platform_focus
        )

        print(f"[FOUND] {len(analysis_result['opportunities'])} opportunities")

        # Generate images if requested
        generated_images = []

        if generate_images:
            print("\n[STEP 3] Invoking Nano Banana 2 (Model: gemini-3.1-flash-image)...")

            if not validate_api_key():
                print("[WARNING] No Google API Key found. Images will be simulated.")

            # Generate images for each opportunity
            for prompt_group in analysis_result["image_prompts"]:
                opportunity_id = prompt_group["opportunity_id"]

                prompts_to_generate = []
                for style in ["white_info", "lifestyle", "hero"]:
                    if style in prompt_group:
                        prompts_to_generate.append({
                            "style": style,
                            "prompt": prompt_group[style]["prompt"]
                        })

                results = self.image_generator.generate_batch(
                    prompts_to_generate,
                    opportunity_id
                )

                generated_images.extend(results)

            print(f"[SUCCESS] Generated {len(generated_images)} images")

        analysis_result["generated_images"] = generated_images
        return analysis_result

    def create_product(
        self,
        product_name: str,
        category: str = "",
        base_price: float = None,
        description: str = "",
        language: str = "en",
        target_platforms: Optional[List[str]] = None,
        generate_images: bool = True,
        image_style: str = "white_info",
        publish_to_shopify: bool = False,
        publish_to_woocommerce: bool = False
    ) -> Dict[str, Any]:
        """
        Complete e-commerce product creation workflow

        Args:
            product_name: Product name
            category: Product category
            base_price: Base price (optional)
            description: Product description (optional, auto-generated if not provided)
            language: Output language
            target_platforms: Target platforms (shopify, woocommerce)
            generate_images: Whether to generate product images
            image_style: Image style (white_info, lifestyle, hero)
            publish_to_shopify: Whether to publish to Shopify
            publish_to_woocommerce: Whether to publish to WooCommerce

        Returns:
            Complete result with synthesized data, images, and publish status
        """
        result = {
            "product_name": product_name,
            "category": category,
            "language": language,
            "generated_at": ""
        }

        # Step 1: Synthesize product data
        print(f"\n[STEP 1] Synthesizing product data for: {product_name}")
        product_data = self.product_synthesizer.synthesize(
            product_name=product_name,
            category=category,
            base_price=base_price,
            description=description,
            language=language,
            target_platforms=target_platforms or ["shopify", "woocommerce"]
        )

        result["product_data"] = product_data
        print(f"[SUCCESS] Generated title: {product_data['title']}")
        print(f"[PRICE] ${product_data['price']}")
        print(f"[SKU] {product_data['sku']}")

        # Step 2: Generate images
        generated_image_url = None

        if generate_images:
            print(f"\n[STEP 2] Generating product image ({image_style})...")

            if not validate_api_key():
                print("[WARNING] No Google API Key found. Image will be simulated.")

            # Build prompt based on style
            prompts = self._build_product_image_prompts(
                product_name,
                product_data,
                image_style
            )

            # Generate
            image_results = self.image_generator.generate_batch(
                [{"style": image_style, "prompt": prompts[image_style]}],
                f"product_{product_data['sku']}"
            )

            if image_results:
                generated_image_url = image_results[0].get("image_url")
                result["generated_image"] = image_results[0]
                print(f"[SUCCESS] Image generated: {generated_image_url}")
            else:
                print("[WARNING] Image generation failed")

        # Step 3: Publish to platforms
        publish_results = {
            "shopify": None,
            "woocommerce": None
        }

        target_platforms = target_platforms or []

        # Publish to Shopify
        if publish_to_shopify and self.shopify.connected:
            print(f"\n[STEP 3a] Publishing to Shopify...")
            shopify_result = self._publish_to_shopify(product_data, generated_image_url)
            publish_results["shopify"] = shopify_result
            if shopify_result.get("success"):
                print(f"[SUCCESS] Shopify product created: ID {shopify_result.get('product_id')}")
            else:
                print(f"[ERROR] Shopify: {shopify_result.get('error')}")
        elif publish_to_shopify and not self.shopify.connected:
            print(f"\n[WARNING] Shopify not connected. Skipping.")

        # Publish to WooCommerce
        if publish_to_woocommerce and self.woocommerce.connected:
            print(f"\n[STEP 3b] Publishing to WooCommerce...")
            woo_result = self._publish_to_woocommerce(product_data, generated_image_url)
            publish_results["woocommerce"] = woo_result
            if woo_result.get("success"):
                print(f"[SUCCESS] WooCommerce product created: ID {woo_result.get('product_id')}")
            else:
                print(f"[ERROR] WooCommerce: {woo_result.get('error')}")
        elif publish_to_woocommerce and not self.woocommerce.connected:
            print(f"\n[WARNING] WooCommerce not connected. Skipping.")

        result["publish_results"] = publish_results
        result["status"] = "completed"

        return result

    def _build_product_image_prompts(
        self,
        product_name: str,
        product_data: Dict,
        style: str
    ) -> Dict[str, str]:
        """Build image generation prompts for product"""

        prompts = {
            "white_info": f"White-background e-commerce product photo of {product_name}, clean minimalist design, soft directional lighting, 8k resolution, professional product photography. DO NOT EMBED TEXT; reserve overlay area at bottom 20%.",
            "lifestyle": f"Lifestyle photography: person using {product_name} in real场景, natural lighting, golden hour, candid moment, 8k resolution, photorealistic. DO NOT EMBED TEXT; reserve overlay area.",
            "hero": f"Premium hero banner: {product_name} on dark gradient background, dramatic lighting, commercial photography style, cinematic composition, 8k resolution. DO NOT EMBED TEXT; reserve overlay area."
        }

        return prompts

    def _publish_to_shopify(
        self,
        product_data: Dict,
        image_url: Optional[str]
    ) -> Dict[str, Any]:
        """Publish product to Shopify"""

        # Build tags list
        tags = [tag["name"] for tag in product_data.get("tags", [])]

        return self.shopify.create_product(
            title=product_data["title"],
            description=product_data["description"],
            price=product_data["price"],
            compare_at_price=product_data.get("compare_at_price"),
            inventory_quantity=product_data["inventory"],
            sku=product_data["sku"],
            product_type=product_data.get("product_type", ""),
            vendor=product_data.get("vendor", ""),
            tags=tags,
            image_url=image_url,
            status="active"
        )

    def _publish_to_woocommerce(
        self,
        product_data: Dict,
        image_url: Optional[str]
    ) -> Dict[str, Any]:
        """Publish product to WooCommerce"""

        # Build categories and tags
        categories = product_data.get("categories", [])
        tags = product_data.get("tags", [])

        # Build images
        images = []
        if image_url:
            images = [{"src": image_url, "alt": product_data["title"]}]

        return self.woocommerce.create_product(
            title=product_data["title"],
            description=product_data["description"],
            price=product_data["price"],
            regular_price=product_data.get("price"),
            sale_price=product_data.get("compare_at_price"),
            stock_quantity=product_data["inventory"],
            sku=product_data["sku"],
            product_type="simple",
            categories=categories,
            tags=tags,
            images=images,
            short_description=product_data.get("short_description", ""),
            status="publish",
            manage_stock=True
        )

    def save_result(self, result: Dict, output_path: str = "output/result.json") -> None:
        """Save result to JSON file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"[SAVED] Result saved to {output_path}")


def main():
    """
    Main function for command-line usage
    """
    # Example 1: Create product with auto-generated data and images
    print("=" * 50)
    print("Example 1: E-commerce Product Creation")
    print("=" * 50)

    automator = EcommerceAutomator()

    # Create product
    result = automator.create_product(
        product_name="Wireless Bluetooth Headphones Pro",
        category="Electronics",
        base_price=79.99,
        language="en",
        generate_images=True,
        image_style="white_info",
        publish_to_shopify=False,  # Set True when credentials configured
        publish_to_woocommerce=False  # Set True when credentials configured
    )

    # Save result
    automator.save_result(result, "output/ecommerce_result.json")

    print("\n[DONE] Product creation complete!")
    print(f"[PRODUCT] {result['product_data']['title']}")
    print(f"[PRICE] ${result['product_data']['price']}")

    # Example 2: GEO Analysis (existing functionality)
    print("\n" + "=" * 50)
    print("Example 2: GEO Opportunity Analysis")
    print("=" * 50)

    geo_result = automator.run_geo_analysis(
        brand="AcmeWatch",
        product="Acme DivePro 5",
        core_keyword="smartwatch water resistance",
        country="us",
        language="en",
        competitors=["BrandA", "BrandB"],
        generate_images=True
    )

    automator.save_result(geo_result, "output/geo_analysis_result.json")

    print("\n[DONE] GEO Analysis complete!")
    print(f"[OPPORTUNITIES] {len(geo_result['opportunities'])}")
    print(f"[IMAGES] {len(geo_result.get('generated_images', []))}")


if __name__ == "__main__":
    main()
