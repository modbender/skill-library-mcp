# Ad Symbiont - Plugin Specification

## Overview

WordPress plugin that automatically displays Amazon product ads when Amazon affiliate links are detected in post content.

## Plugin Metadata

- **Name**: Ad Symbiont
- **Version**: 1.0.0
- **Description**: Automatically displays Amazon product ads when Amazon affiliate links are detected in post content. Extracts ASIN, displays product info, and earns affiliate commissions.
- **Author**: Your Name
- **License**: GPL v2 or later
- **Text Domain**: ad-symbiont
- **Domain Path**: /languages
- **Requires at least**: 5.8
- **Tested up to**: 6.4

## Admin Settings

### Settings Page Location
- WordPress Settings menu → "Ad Symbiont"

### Settings Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| affiliate_tag | text | (empty) | Amazon Associate Affiliate Tag |
| display_mode | select | append | "replace" or "append" |
| enable_styling | checkbox | checked | Enable default CSS styling |
| paapi_access_key | text | (empty) | Amazon PA-API Access Key |
| paapi_secret_key | password | (empty) | Amazon PA-API Secret Key |
| paapi_tag | text | (empty) | PA-API Associate Tag |
| cache_duration | number | 12 | Hours to cache ads |

## Link Detection

### Supported Amazon Domains
- amazon.com
- amazon.ca
- amazon.co.uk
- amazon.de
- amazon.fr
- amazon.es
- amazon.it
- amazon.co.jp
- amzn.to (short URL)

### ASIN Extraction Patterns

```regex
/(?:amazon\.[a-z]{2,3}\/(?:dp|gp\/product|exec\/obidos\/ASIN|ASIN)|amzn\.to\/)([A-Z0-9]{10})/i
```

### ASIN Validation
- Must be exactly 10 alphanumeric characters
- Only letters A-Z and numbers 0-9

## Ad Display Modes

### 1. Replace Link
- Original Amazon link replaced with ad unit
- "Buy on Amazon" button links to original URL
- Falls back to original link if parsing fails

### 2. Append Below Link
- Ad unit inserted after the Amazon link
- Original link remains functional

## Ad Unit Structure

```html
<div class="ad-symbiont-ad">
  <div class="ad-symbiont-image">
    <a href="{affiliate_link}" target="_blank" rel="nofollow">
      <img src="{product_image}" alt="{product_title}">
    </a>
  </div>
  <div class="ad-symbiont-info">
    <h3 class="ad-symbiont-title">{product_title}</h3>
    <p class="ad-symbiont-price">{price}</p>
    <a href="{affiliate_link}" class="ad-symbiont-button" target="_blank" rel="nofollow">
      Buy on Amazon
    </a>
  </div>
</div>
```

## PA-API Integration

### Endpoint
- Official Product Advertising API 5.0
- Region-specific endpoints

### Request Format
- GetItems operation
- Include: Items/Request/ItemId, OfferSummary

### Fallback
If PA-API credentials not provided or API fails:
- Display simple ad with product image placeholder
- Include affiliate link directly

## Caching

### Method
- WordPress Transients API
- Transient key: `ad_symbiont_{asin}`

### Duration
- Default: 12 hours
- Configurable in settings (1-72 hours)

### Cache Invalidation
- On settings change
- Manual clear button in admin

## Gutenberg Block

### Block Name
- `ad-symbiont/amazon-ad`

### Attributes
- asin (string): Product ASIN
- display_mode (string): 'replace' or 'append'

### Block Features
- Manual ASIN input
- Preview of ad unit
- Insert button to add to post

## Security Requirements

### Input Sanitization
- `sanitize_text_field()` for text inputs
- `sanitize_url()` or `esc_url()` for URLs
- `sanitize_key()` for option names

### Output Escaping
- `esc_html()` for text content
- `esc_attr()` for HTML attributes
- `esc_url()` for URLs
- `esc_js()` for JavaScript strings

### Nonces
- Settings page form nonce
- Ajax action nonces

### Capabilities
- `manage_options` required for settings

## WordPress Integration

### Hooks Used
- `admin_menu` - Add settings page
- `admin_init` - Register settings
- `the_content` - Filter post content
- `wp_enqueue_scripts` - Frontend CSS/JS
- `admin_enqueue_scripts` - Admin CSS/JS
- `wp_ajax_ad_symbiont_clear_cache` - Clear cache action

### Shortcode
- `[ad_symbiont asin="B08N5WRWNW"]` - Manual ad display

## File Structure

```
ad-symbiont/
├── ad-symbiont.php          # Main plugin file
├── includes/
│   ├── class-settings.php   # Admin settings
│   ├── class-ads.php        # Ad generation
│   ├── class-link-detector.php # Link detection
│   └── class-paapi.php      # PA-API integration
├── assets/
│   ├── css/
│   │   └── admin.css        # Admin styles
│   ├── js/
│   │   └── admin.js         # Admin scripts
│   └── blocks/
│       ├── build/
│       │   └── index.js     # Block build
│       └── src/
│           └── index.js     # Block source
├── languages/
│   └── ad-symbiont.pot      # Translation template
└── readme.txt               # WordPress readme
```

## CSS Classes

```css
.ad-symbiont-ad { }
.ad-symbiont-ad.replace-mode { }
.ad-symbiont-ad.append-mode { }
.ad-symbiont-image { }
.ad-symbiont-image img { }
.ad-symbiont-info { }
.ad-symbiont-title { }
.ad-symbiont-price { }
.ad-symbiont-button { }
.ad-symbiont-button:hover { }
```

## Error Handling

- Invalid ASIN: Skip, leave original link
- PA-API failure: Show fallback ad
- Network error: Use cached data or fallback
- No affiliate tag: Show warning in admin

## Amazon Associates Compliance

- Affiliate tag appended to all links
- `rel="nofollow"` on affiliate links
- Disclosure notice option
- No cloaking or link masking
