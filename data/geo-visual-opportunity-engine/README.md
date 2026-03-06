# GeoCommerce Automator

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/Version-3.0.0-blue.svg)](https://github.com/GEO-SEO/geo-visual-opportunity-engine)
[![Platform](https://img.shields.io/badge/Platform-Dify%20%7C%20Coze%20%7C%20Python-orange.svg)](#)
[![Shopify](https://img.shields.io/badge/Shopify-API%20Integration-purple.svg)](#)
[![WooCommerce](https://img.shields.io/badge/WooCommerce-API%20Integration-purple.svg)](#)

> E-commerce automation tool that integrates Nano Banana 2 AI image generation with Shopify and WooCommerce. Automatically generates product data, creates product images, and publishes to e-commerce platforms.

## Features

### Core Features
- **Product Data Synthesis**: Auto-generate product titles, descriptions, SKU, prices, inventory
- **AI Image Generation**: Automatically calls Nano Banana 2 (Google Gemini 3.1 Flash) to generate product images
- **Multi-Platform Support**: Publish to Shopify and WooCommerce simultaneously
- **Three Image Styles**: White info, lifestyle, and hero images for each product

### E-commerce Integrations
- **Shopify Admin API**: Create products, upload images, set price/inventory/SKU
- **WooCommerce REST API**: Auto-publish products with full metadata
- **Product Data Generator**: Auto-generate titles, descriptions, SEO keywords, categories, tags

### GEO Features (v1.0)
- **Smart Opportunity Analysis**: Identifies high-priority GEO opportunities
- **Three Image Prompts**: Generates white info, lifestyle, and hero image prompts
- **Localized Content**: Supports 10+ languages for content generation
- **4-Week Publishing Rhythm**: Provides complete content publishing plan

## Input Parameters

**One unified workflow**: Input once → Opportunity Analysis → Content Generation (text + images) → Auto-publish to e-commerce platforms.

```json
{
  "brand": "AcmeWatch",
  "product": "Acme DivePro 5",
  "core_keyword": "smartwatch water resistance",
  "category": "Electronics",
  "base_price": 199.99,
  "country": "us",
  "language": "en",
  "competitors": ["BrandA", "BrandB"],
  "platform_focus": ["ChatGPT", "Grok"],
  "publish_to_shopify": true,
  "publish_to_woocommerce": true,
  "image_style": "white_info"
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `brand` | string | ✅ | Brand name |
| `product` | string | ✅ | Product name |
| `core_keyword` | string | ✅ | Core keyword/phrase for SEO |
| `category` | string | ❌ | Product category (e.g., Electronics, Clothing) |
| `base_price` | number | ❌ | Product price in USD (auto-generates if not provided) |
| `country` | string | ✅ | Target country (e.g., us, uk, jp) |
| `language` | string | ✅ | Output language (e.g., en, zh) |
| `competitors` | array | ❌ | Competitor list (max 10) |
| `platform_focus` | array | ❌ | Target AI platforms |
| `publish_to_shopify` | boolean | ❌ | Auto-publish to Shopify (default: false) |
| `publish_to_woocommerce` | boolean | ❌ | Auto-publish to WooCommerce (default: false) |
| `image_style` | string | ❌ | Image style: white_info, lifestyle, hero |

### What happens after input:

1. **Opportunity Analysis** - Identify GEO opportunities based on brand/product/keywords
2. **Content Generation** - Generate text content (titles, descriptions, SEO keywords)
3. **Image Generation** - Auto-create product images using Nano Banana 2
4. **Auto-publish** - Upload to Shopify and/or WooCommerce (if enabled)

---

## Quick Start

### Prerequisites

- Python 3.9+
- Google AI Studio API Key (for Nano Banana 2 image generation)
- Shopify Admin API credentials (optional)
- WooCommerce API credentials (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/GEO-SEO/geo-visual-opportunity-engine.git
cd geo-visual-opportunity-engine

# Install dependencies
pip install -r requirements.txt

# Set your Google API Key
export GOOGLE_API_KEY="your-api-key-here"
```

### API Configuration

#### Google API (Nano Banana 2)
```bash
export GOOGLE_API_KEY="your-google-api-key"
```
Get your API key from: https://aistudio.google.com/app/apikey

#### Shopify
```bash
export SHOPIFY_STORE_URL="your-store.myshopify.com"
export SHOPIFY_ACCESS_TOKEN="your-admin-api-access-token"
```

#### WooCommerce
```bash
export WOOCOMMERCE_STORE_URL="https://your-store.com"
export WOOCOMMERCE_CONSUMER_KEY="your-consumer-key"
export WOOCOMMERCE_CONSUMER_SECRET="your-consumer-secret"
```

## Python Usage

### E-commerce Product Creation

```python
from src.main import EcommerceAutomator

# Initialize the automator
automator = EcommerceAutomator()

# Create and publish product
result = automator.create_product(
    product_name="Wireless Bluetooth Headphones Pro",
    category="Electronics",
    base_price=79.99,
    language="en",
    generate_images=True,
    image_style="white_info",
    publish_to_shopify=True,
    publish_to_woocommerce=True
)

# Result contains:
# - product_data: Synthesized title, description, SKU, price, inventory
# - generated_image: Nano Banana 2 generated image
# - publish_results: Shopify and WooCommerce publish status
```

### GEO Opportunity Analysis

```python
from src.main import EcommerceAutomator

# Initialize the engine
automator = EcommerceAutomator()

# Run GEO analysis
result = automator.run_geo_analysis(
    brand="AcmeWatch",
    product="Acme DivePro 5",
    core_keyword="smartwatch water resistance",
    country="us",
    language="en",
    competitors=["BrandA", "BrandB"]
)

# Result contains:
# - opportunities: List of GEO opportunities
# - image_prompts: Generated prompts for each opportunity
# - generated_images: Paths to Nano Banana 2 generated images
# - content_drafts: Localized content drafts
# - posting_schedule: 4-week publishing plan
```

## Workflow

```
Input: Product Info
    ↓
Nano Banana 2 → Generate product images
    ↓
Product Synthesizer → Generate title/description/SKU/price
    ↓
┌──────────────┬──────────────┐
│   Shopify   │  WooCommerce  │
│   API Upload │   API Upload  │
└──────────────┴──────────────┘
```

## Platform Integration

### Dify.ai

1. Open Dify dashboard
2. Create new app or import existing
3. Copy `prompts/system_prompt.md` content to "Prompt" section
4. Configure input variables (reference `schemas/input_schema.json`)
5. Set output format to JSON

### Coze / GPTs

1. Create new Bot
2. Paste `prompts/system_prompt.md` as system prompt
3. Configure input form (reference field definitions in `schemas/input_schema.json`)
4. Set output format to JSON

## Project Structure

```
geo-visual-opportunity-engine/
├── manifest.json                 # Skill metadata (v3.0.0)
├── README.md                    # This file
├── LICENSE                      # MIT License
├── requirements.txt             # Python dependencies
├── src/
│   ├── __init__.py
│   ├── main.py                  # Main entry point (EcommerceAutomator)
│   ├── analyzer.py              # GEO opportunity analysis
│   ├── nano_banana_2.py         # Nano Banana 2 image generation
│   ├── shopify.py               # Shopify API integration
│   ├── woocommerce.py           # WooCommerce API integration
│   ├── product_synthesizer.py   # Product data synthesis
│   └── config.py                # Configuration
├── schemas/
│   ├── input_schema.json        # Input JSON Schema
│   └── output_schema.json       # Output JSON Schema
├── prompts/
│   └── system_prompt.md         # Core system prompt
└── examples/
    ├── example_input.json        # Example input
    └── example_output.json       # Example output
```

## Output Format

### Product Creation Response

```json
{
  "product_name": "Wireless Bluetooth Headphones Pro",
  "category": "Electronics",
  "product_data": {
    "title": "Premium Wireless Bluetooth Headphones Pro",
    "description": "<h2>About This Product</h2>...",
    "price": 79.99,
    "sku": "SHOP-ABCD-1234",
    "inventory": 500,
    "seo_keywords": [...],
    "categories": [...],
    "tags": [...]
  },
  "generated_image": {
    "image_url": "output/images/product_123.png",
    "generation_status": "success"
  },
  "publish_results": {
    "shopify": {"success": true, "product_id": 123456},
    "woocommerce": {"success": true, "product_id": 789}
  },
  "status": "completed"
}
```

### Error Response

```json
{
  "error": "invalid_input",
  "details": "Required field cannot be empty"
}
```

## Supported Languages

- English
- Chinese
- Japanese
- Spanish
- French
- German
- Korean
- Portuguese
- Italian
- Russian

## Version History

### v3.0.0 (2026-02-28)

- Added Shopify Admin API integration
- Added WooCommerce REST API integration
- Added Product Synthesizer (auto-generate title, description, SKU, price)
- New workflow: Generate images → Synthesize data → Publish to e-commerce
- Main class renamed to EcommerceAutomator

### v3.0.0 (2026-02-28)

- Added Product Synthesizer (auto-generate title, description, SKU, price)
- New workflow: Generate images → Synthesize data → Publish to e-commerce
- Main class renamed to EcommerceAutomator
- Fixed version number to display correctly as v3.0.0

### v2.0.0 (2026-02-28)

- Added automatic Nano Banana 2 image generation
- Upgraded to Google Gemini 3.1 Flash Image model
- Added Python SDK for local execution

### v1.0.0 (2025-03-10)

- Initial release
- Structured JSON input/output
- Three-image prompt generation
- 4-week publishing rhythm planning

## Contributing

Issues and Pull Requests are welcome!

1. Fork this repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add some amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Author

- **Tim**
- Email: sales@dageno.ai
- Website: https://dageno.ai/

---

*This tool helps e-commerce teams automate product listing with AI-generated images and multi-platform publishing.*
