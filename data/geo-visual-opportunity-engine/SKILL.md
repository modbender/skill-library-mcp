---
name: geo-visual-opportunity-engine
description: GEO Visual Opportunity Engine workflow skill.
---

# GEO Visual Opportunity Engine

## Overview

GEO Visual Opportunity Engine is an AI-powered e-commerce automation tool that generates product images using Nano Banana 2 (Google Gemini) and automatically publishes products to Shopify and WooCommerce.

## Features

- **Product Data Synthesis**: Auto-generate product titles, descriptions, SKU, prices, inventory
- **AI Image Generation**: Automatically calls Nano Banana 2 to generate product images
- **Multi-Platform Support**: Publish to Shopify and WooCommerce simultaneously
- **Three Image Styles**: White info, lifestyle, and hero images for each product
- **GEO Opportunity Analysis**: Identifies high-priority visual content opportunities

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from src.main import EcommerceAutomator

# Initialize with API key
automator = EcommerceAutomator(google_api_key="your-google-api-key")

# Run complete workflow - one input to finish everything
result = automator.run_complete_workflow(
    product_input="wireless bluetooth headphones",
    country="us",
    language="en",
    generate_images=True,
    publish_to_shopify=False,
    publish_to_woocommerce=False
)

print(result['product_data']['title'])
print(result['status'])
```

### GEO Analysis Only

```python
from src.main import EcommerceAutomator

automator = EcommerceAutomator()

# Run GEO opportunity analysis
result = automator.run_geo_analysis(
    brand="AcmeWatch",
    product="Acme DivePro 5",
    core_keyword="smartwatch water resistance",
    country="us",
    language="en",
    generate_images=True
)

print(f"Found {len(result['opportunities'])} opportunities")
```

### Create Product with Publishing

```python
from src.main import EcommerceAutomator

automator = EcommerceAutomator(
    google_api_key="your-google-api-key",
    shopify_store_url="your-store.myshopify.com",
    shopify_access_token="your-access-token"
)

# Create and publish product
result = automator.create_product(
    product_name="Wireless Bluetooth Headphones Pro",
    category="Electronics",
    base_price=79.99,
    generate_images=True,
    image_style="white_info",
    publish_to_shopify=True,
    publish_to_woocommerce=False
)
```

## API Reference

### EcommerceAutomator

Main class for e-commerce automation.

#### `__init__(google_api_key, shopify_store_url, shopify_access_token, woo_store_url, woo_consumer_key, woo_consumer_secret)`

Initialize the automator with API credentials.

#### `run_complete_workflow(product_input, country='us', language='en', generate_images=True, publish_to_shopify=False, publish_to_woocommerce=False, output_dir='output')`

**Unified workflow** - One input completes the entire process:
1. Analyze GEO opportunities
2. Synthesize product data (title, description, SKU, price)
3. Generate AI images
4. Publish to e-commerce platforms

#### `run_geo_analysis(brand, product, core_keyword, country, language, competitors, platform_focus, generate_images)`

Run GEO opportunity analysis with image generation.

#### `create_product(product_name, category, base_price, description, language, target_platforms, generate_images, image_style, publish_to_shopify, publish_to_woocommerce)`

Complete e-commerce product creation workflow.

## Configuration

### Environment Variables

- `GOOGLE_API_KEY` - Google API Key for Nano Banana 2 image generation
- `SHOPIFY_STORE_URL` - Shopify store URL
- `SHOPIFY_ACCESS_TOKEN` - Shopify Admin API access token
- `WOOCOMMERCE_STORE_URL` - WooCommerce store URL
- `WOOCOMMERCE_CONSUMER_KEY` - WooCommerce API consumer key
- `WOOCOMMERCE_CONSUMER_SECRET` - WooCommerce API consumer secret

## Image Styles

- **white_info**: Clean white background, product-focused infographic
- **lifestyle**: Real-world场景 with human interaction, photorealistic
- **hero**: Dramatic hero shot with commercial photography quality

## Version

3.0.0

## Author

Tim (sales@dageno.ai)
