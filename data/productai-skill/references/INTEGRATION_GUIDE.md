# ProductAI Integration Guide

Complete guide for integrating ProductAI into your applications, workflows, and AI agents.

## Quick Start (5 minutes)

### 1. Install the Skill

```bash
# If skill is packaged as .skill file
openclaw skills install productai.skill

# Or clone directly
git clone https://github.com/your-org/productai-skill ~/.openclaw/workspace/productai
```

### 2. Configure API Credentials

```bash
cd ~/.openclaw/workspace/productai
python3 scripts/setup.py
```

Or manually create `config.json`:

```json
{
  "api_key": "your-api-key-here",
  "api_endpoint": "https://api.productai.photo/v1",
  "default_model": "nano-banana-2",
  "default_resolution": "1024x1024",
  "plan": "standard"
}
```

### 3. Test It

```bash
# Generate your first photo
scripts/generate_photo.py \
  --image product.jpg \
  --prompt "white studio background with soft shadows" \
  --output result.png
```

**Done!** You now have ProductAI integrated.

## Integration Patterns

### Pattern 1: Command-Line Scripts

Best for: Manual workflows, batch jobs, cron tasks

```bash
# Single photo generation
scripts/generate_photo.py --image product.jpg --prompt "modern living room" --output result.png

# Background replacement
scripts/generate_photo.py --image product.jpg --background-replace --output clean.png

# Batch processing
scripts/batch_generate.py \
  --input-dir ./products \
  --output-dir ./processed \
  --template "white background with subtle shadows"
```

### Pattern 2: Python Library

Best for: Python applications, Jupyter notebooks, automation scripts

```python
from productai_client import create_client

# Initialize client
client = create_client()

# Generate photo
result = client.generate(
    image='product.jpg',
    prompt='modern living room with natural lighting'
)

# Download result
client.download_result(result['image_url'], 'output.png')

print(f"Credits used: {result['credits_used']}")
print(f"Processing time: {result['processing_time_ms']}ms")
```

### Pattern 3: AI Agent Integration

Best for: OpenClaw agents, LangChain, AutoGPT, other AI systems

**OpenClaw Integration:**

The skill is auto-loaded when OpenClaw detects product photo tasks. Just ask:

> "Generate a professional product photo of this bottle in a modern kitchen setting"

**Custom Agent Integration:**

```python
import subprocess
import json

def generate_product_photo(image_path: str, prompt: str) -> dict:
    """Call ProductAI from any AI agent."""
    result = subprocess.run(
        [
            'python3',
            '/path/to/productai/scripts/generate_photo.py',
            '--image', image_path,
            '--prompt', prompt,
            '--output', 'result.png'
        ],
        capture_output=True,
        text=True
    )
    
    return json.loads(result.stdout)

# Use in your agent
result = generate_product_photo('product.jpg', 'white background')
print(f"Generated: {result['image_url']}")
```

### Pattern 4: REST API Wrapper

Best for: Microservices, web apps, team access

```python
from flask import Flask, request, jsonify
from productai_client import create_client

app = Flask(__name__)
client = create_client()

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    
    result = client.generate(
        image=data['image'],
        prompt=data['prompt'],
        model=data.get('model', 'nano-banana-2')
    )
    
    return jsonify(result)

@app.route('/api/background-replace', methods=['POST'])
def background_replace():
    data = request.json
    
    result = client.background_replace(
        image=data['image'],
        background_type=data.get('background_type', 'white')
    )
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)
```

## Real-World Use Cases

### E-Commerce Product Photos

**Challenge:** Need 1000 product photos with consistent white backgrounds for Shopify store.

**Solution:**

```bash
# 1. Organize products
mkdir -p products/raw products/processed

# 2. Batch process with white background
scripts/batch_generate.py \
  --input-dir products/raw \
  --output-dir products/processed \
  --template "clean white background with soft drop shadow" \
  --max-workers 5

# 3. Upload to Shopify (use Shopify API or bulk upload)
```

**Result:** Professional product photos at 10x lower cost than photographer.

### Marketing Campaign Visuals

**Challenge:** Create lifestyle product shots for Instagram campaign.

**Solution:**

```python
from productai_client import create_client

client = create_client()

scenes = [
    "product on rustic wooden table with morning coffee",
    "product held in hands outdoors with natural lighting",
    "product on modern desk with laptop and plant",
    "product on kitchen counter with fresh ingredients"
]

for i, scene in enumerate(scenes):
    result = client.generate(
        image='product.jpg',
        prompt=scene,
        model='flux-kontext',
        resolution='1024x1024'
    )
    
    client.download_result(
        result['image_url'],
        f'campaign/instagram_{i+1}.png'
    )
    
    print(f"✓ Generated scene {i+1}: {scene}")
```

**Result:** 4 unique lifestyle shots ready for social media in minutes.

### Product Catalog Updates

**Challenge:** Seasonal catalog needs all products re-shot with holiday theme.

**Solution:**

```bash
# Generate holiday-themed versions
scripts/batch_generate.py \
  --input-dir catalog/products \
  --output-dir catalog/holiday \
  --template "festive holiday setting with warm lighting and decorations" \
  --model nano-banana-2-pro

# Or summer theme
scripts/batch_generate.py \
  --input-dir catalog/products \
  --output-dir catalog/summer \
  --template "bright summer outdoor setting with natural sunlight"
```

**Result:** Entire catalog refreshed for new season without re-shooting products.

### Automated Listing Generator

**Challenge:** Automatically create marketplace listings with professional photos.

**Solution:**

```python
from productai_client import create_client
import csv

client = create_client()

# Read product inventory
with open('inventory.csv') as f:
    products = csv.DictReader(f)
    
    for product in products:
        # Generate professional photo
        result = client.generate(
            image=product['raw_photo_url'],
            prompt='clean white background for e-commerce',
            model='nano-banana-2'
        )
        
        # Download and save
        output_path = f"listings/{product['sku']}.png"
        client.download_result(result['image_url'], output_path)
        
        # Create listing (pseudo-code)
        create_marketplace_listing(
            title=product['name'],
            image=output_path,
            price=product['price']
        )
        
        print(f"✓ Listed {product['name']}")
```

**Result:** Fully automated listing creation with professional photos.

## Advanced Topics

### Custom Webhooks

Get notified when batch jobs complete:

```python
from flask import Flask, request
from productai_client import create_client

app = Flask(__name__)
client = create_client()

@app.route('/webhook/productai', methods=['POST'])
def productai_webhook():
    event = request.json
    
    if event['event'] == 'job.completed':
        job_id = event['job_id']
        result_url = event['result']['image_url']
        
        # Process completed job
        client.download_result(result_url, f'results/{job_id}.png')
        
        # Trigger next step in workflow
        process_completed_image(job_id)
    
    return '', 200

# Submit async batch
result = client.batch_generate(
    images=['product1.jpg', 'product2.jpg'],
    template='white background',
    webhook_url='https://your-server.com/webhook/productai'
)

batch_id = result['batch_id']
print(f"Batch submitted: {batch_id}")
```

### Credit Management

Monitor and optimize credit usage:

```python
from productai_client import create_client

client = create_client()

# Track credits
total_credits = 0
results = []

for image in product_images:
    result = client.generate(image=image, prompt='white background')
    
    credits_used = result['credits_used']
    total_credits += credits_used
    results.append(result)
    
    print(f"Processed {image}: {credits_used} credits")

print(f"Total credits used: {total_credits}")
print(f"Average per image: {total_credits / len(product_images):.2f}")
```

**Optimization tips:**
- Use lower resolution for thumbnails
- Batch similar products to save credits
- Cache generated images
- Use Basic plan for simple backgrounds, Pro for high-end

### Quality Control

Implement QA checks on generated images:

```python
from PIL import Image
import requests
from productai_client import create_client

client = create_client()

def check_image_quality(image_url: str) -> dict:
    """Basic quality checks on generated image."""
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    
    width, height = img.size
    aspect_ratio = width / height
    
    # Check resolution
    if width < 1000 or height < 1000:
        return {'status': 'low_resolution', 'width': width, 'height': height}
    
    # Check aspect ratio (for square products)
    if not (0.9 < aspect_ratio < 1.1):
        return {'status': 'wrong_aspect_ratio', 'ratio': aspect_ratio}
    
    return {'status': 'ok'}

# Generate with QA
result = client.generate(
    image='product.jpg',
    prompt='white background',
    resolution='1024x1024'
)

qa_result = check_image_quality(result['image_url'])
if qa_result['status'] == 'ok':
    client.download_result(result['image_url'], 'approved.png')
else:
    print(f"Quality issue: {qa_result}")
    # Retry or flag for manual review
```

### Template Management

Create reusable templates for consistent brand styling:

```python
# templates.py
TEMPLATES = {
    'ecommerce_white': 'clean white background with soft drop shadow',
    'ecommerce_grey': 'light grey gradient background',
    'lifestyle_home': 'modern home interior with natural lighting',
    'lifestyle_outdoor': 'outdoor setting with natural environment',
    'hands_holding': 'product held in hands with professional lighting',
    'table_flat_lay': 'flat lay on white marble table with props'
}

# Use templates
from productai_client import create_client

client = create_client()

result = client.generate(
    image='product.jpg',
    prompt=TEMPLATES['lifestyle_home'],
    model='flux-kontext'
)
```

### Error Handling & Retries

Robust error handling for production:

```python
import time
from productai_client import create_client, ProductAIClient
import requests

def generate_with_retry(
    client: ProductAIClient,
    image: str,
    prompt: str,
    max_retries: int = 3
) -> dict:
    """Generate with exponential backoff retry."""
    
    for attempt in range(max_retries):
        try:
            result = client.generate(image=image, prompt=prompt)
            return result
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limited
                wait = 2 ** attempt
                print(f"Rate limited. Waiting {wait}s...")
                time.sleep(wait)
                continue
            
            elif e.response.status_code == 402:
                # Insufficient credits
                raise Exception("Out of credits")
            
            elif attempt == max_retries - 1:
                # Last attempt, give up
                raise
            
            else:
                # Other error, retry
                wait = 2 ** attempt
                time.sleep(wait)
                continue
        
        except requests.exceptions.RequestException as e:
            # Network error
            if attempt == max_retries - 1:
                raise
            
            wait = 2 ** attempt
            print(f"Network error. Retrying in {wait}s...")
            time.sleep(wait)
            continue
    
    raise Exception("Max retries exceeded")

# Use it
client = create_client()
result = generate_with_retry(client, 'product.jpg', 'white background')
```

## Performance Optimization

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from productai_client import create_client

client = create_client()

def process_product(image_path: str, template: str) -> dict:
    result = client.generate(image=image_path, prompt=template)
    return {'input': image_path, 'result': result}

# Process 100 products in parallel (respect rate limits)
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {
        executor.submit(process_product, img, 'white background'): img
        for img in product_images
    }
    
    for future in as_completed(futures):
        result = future.result()
        print(f"✓ Processed {result['input']}")
```

### Caching Strategy

```python
import hashlib
import json
from pathlib import Path

CACHE_DIR = Path('cache/productai')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_cache_key(image: str, prompt: str, **kwargs) -> str:
    """Generate cache key from parameters."""
    params = {'image': image, 'prompt': prompt, **kwargs}
    key_string = json.dumps(params, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()

def cached_generate(client, image: str, prompt: str, **kwargs) -> dict:
    """Generate with caching."""
    cache_key = get_cache_key(image, prompt, **kwargs)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    # Check cache
    if cache_file.exists():
        print(f"Cache hit: {cache_key}")
        return json.loads(cache_file.read_text())
    
    # Generate
    result = client.generate(image=image, prompt=prompt, **kwargs)
    
    # Cache result
    cache_file.write_text(json.dumps(result, indent=2))
    
    return result
```

## Troubleshooting

### Common Issues

**Issue:** `Configuration file not found`

**Solution:**
```bash
cd ~/.openclaw/workspace/productai
python3 scripts/setup.py
```

---

**Issue:** `API Error 401: Unauthorized`

**Solution:** Check your API key in `config.json` is correct.

---

**Issue:** `API Error 402: Insufficient credits`

**Solution:** Your plan has run out of credits. Upgrade or wait for monthly reset.

---

**Issue:** `API Error 429: Rate limit exceeded`

**Solution:** Reduce `max_workers` in batch jobs or add delays between requests.

---

**Issue:** Generated images don't match prompt

**Solution:** 
- Make prompts more specific
- Try different models (flux-kontext for placement, nano-banana-2-pro for quality)
- Adjust scale parameter

---

**Issue:** Batch processing too slow

**Solution:**
- Increase `max_workers` (respect rate limits)
- Use async batch API with webhooks instead of polling
- Parallelize with multiple API keys if allowed

## Support & Resources

- **Documentation:** `references/API.md`
- **Website:** https://www.productai.photo
- **Email:** support@productai.photo
- **Discord:** (when available)

## Contributing

To contribute improvements to this integration:

1. Fork the skill repository
2. Make your changes
3. Test thoroughly
4. Submit pull request with description

**Areas for contribution:**
- Additional language bindings (JS, Ruby, Go)
- Enhanced error handling
- Performance optimizations
- New templates and presets
- Integration examples

## License

This integration skill is provided as-is for use with ProductAI service.
Check ProductAI's terms of service for API usage terms.
