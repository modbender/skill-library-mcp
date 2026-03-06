=== Ad Symbiont ===
Contributors: yourname
Donate link: https://example.com/donate
Tags: amazon, affiliate, ads, ecommerce, widget
Requires at least: 5.8
Tested up to: 6.4
Stable tag: 1.0.0
License: GPL v2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Automatically displays Amazon product ads when Amazon affiliate links are detected in post content.

== Description ==

Ad Symbiont automatically detects Amazon affiliate links in your WordPress posts and pages, and displays attractive product ad units. The plugin extracts the ASIN from Amazon URLs and generates ads with product images, titles, and prices.

### Features

*   **Automatic Detection**: Detects Amazon links from amazon.com, amazon.co.uk, amazon.de, and more
*   **Flexible Display**: Choose to replace links with ads or append ads below links
*   **PA-API Integration**: Optional Product Advertising API for real product data
*   **Caching**: Built-in caching improves performance and reduces API calls
*   **Gutenberg Block**: Easily insert Amazon ads with the block editor
*   **Shortcode**: Manual ad placement with `[ad_symbiont asin="B08N5WRWNW"]`
*   **Styling Options**: Enable/disable default styling or use your own CSS
*   **Secure**: Proper sanitization and escaping throughout

### Supported Amazon Domains

*   amazon.com, amazon.ca, amazon.co.uk
*   amazon.de, amazon.fr, amazon.es, amazon.it
*   amazon.co.jp, amazon.com.au
*   amzn.to (short URLs)

== Installation ==

1. Upload the `ad-symbiont` folder to the `/wp-content/plugins/` directory
2. Activate the plugin through the 'Plugins' menu in WordPress
3. Go to Settings > Ad Symbiont to configure
4. Enter your Amazon Affiliate Tag
5. Optionally configure PA-API credentials for enhanced ads

== Frequently Asked Questions ==

= Do I need an Amazon Affiliate account? =

Yes, you need an Amazon Associates account to earn commissions.

= Does this work with Amazon short URLs (amzn.to)? =

Yes, the plugin detects both full Amazon URLs and short amzn.to links.

= What if PA-API credentials are not provided? =

The plugin will display a fallback ad with your affiliate link. Users will still see a "Buy on Amazon" button.

= Can I manually insert ads? =

Yes, use the Gutenberg block or shortcode: `[ad_symbiont asin="B08N5WRWNW"]`

= How do I find a product ASIN? =

ASIN is the 10-character ID in Amazon product URLs. For example, in `amazon.com/dp/B08N5WRWNW`, the ASIN is `B08N5WRWNW`.

= Does this support multiple Amazon domains? =

Yes, supports amazon.com, .co.uk, .de, .fr, .es, .it, .co.jp, .ca, .com.au, and amzn.to short URLs.

== Screenshots ==

1. Admin settings page
2. Amazon ad display example
3. Gutenberg block

== Changelog ==

= 1.0.0 =
* Initial release
* Automatic Amazon link detection
* Admin settings page
* PA-API integration
* Gutenberg block support
* Shortcode support
* Caching system

== Upgrade Notice ==

= 1.0.0 =
Initial release of Ad Symbiont.
