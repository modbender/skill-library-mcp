# WordPress MCP — Feature Tools Reference

## WordPress Core (default: enabled)

64 tools for content management, media, taxonomies, users, and settings.

### Content
- `wp_get_posts(post_type, post_status, per_page, page, search, category, tag)` — List posts (no full content)
- `wp_get_post(post_id)` — Get full post with content
- `wp_get_post_snapshot(post_id)` — Complete post data in one call (post + meta + terms)
- `wp_create_post(post_title, post_content, post_status, post_type, ...)` — Create post (Markdown accepted)
- `wp_update_post(post_id, ...)` — Update any post field
- `wp_alter_post(post_id, search, replace)` — Search-replace in post content
- `wp_delete_post(post_id)`

### Media
- `wp_upload_media(url, title, alt_text)` — Upload from URL
- `wp_get_media(per_page, page, search)` — List media items
- `wp_get_media_item(media_id)` — Get media details
- `wp_update_media_item(media_id, title, alt_text, caption)`
- `wp_delete_media_item(media_id)`

### Taxonomies
- `wp_get_terms(taxonomy, per_page, search)` — List terms
- `wp_get_term(term_id, taxonomy)` — Get term details
- `wp_create_term(taxonomy, name, slug, parent, description)`
- `wp_add_post_terms(post_id, taxonomy, terms)` — Assign terms to post
- `wp_remove_post_terms(post_id, taxonomy, terms)`

### Comments
- `wp_get_comments(post_id, status, per_page)`
- `wp_create_comment(post_id, content, author, ...)`
- `wp_update_comment(comment_id, content, status)`
- `wp_delete_comment(comment_id)`

### Users
- `wp_get_users(role, per_page, search)`
- `wp_get_user(user_id)`
- `wp_get_current_user`

### Settings & Options
- `wp_get_options(keys)` — Read WP options
- `wp_update_option(key, value)`

## Plugins (opt-in)

- `wp_plugin_list` — List installed plugins
- `wp_plugin_activate(plugin)`
- `wp_plugin_deactivate(plugin)`
- `wp_plugin_get_file(plugin, file)` — Read plugin source file
- `wp_plugin_put_file(plugin, file, content)` — Write plugin file
- `wp_plugin_install(slug)` — Install from wordpress.org

## Themes (opt-in)

- `wp_theme_list` — List installed themes
- `wp_theme_activate(theme)`
- `wp_theme_get_file(theme, file)` — Read theme file
- `wp_theme_put_file(theme, file, content)` — Write theme file
- `wp_theme_install(slug)`

## Database (opt-in)

- `wp_db_query(query)` — Execute SQL (SELECT, INSERT, UPDATE, DELETE)

## SEO Engine (opt-in, requires SEO Engine plugin)

32 tools for SEO analysis and analytics.

### Analysis
- `mwseo_get_seo_score(post_id)` — SEO score for a post
- `mwseo_do_seo_scan(post_id)` — Run full SEO scan
- `mwseo_get_issues(post_id)` — Get SEO issues
- `mwseo_get_seo_statistics` — Site-wide SEO overview
- `mwseo_get_posts_needing_seo(per_page)` — Posts with problems
- `mwseo_get_posts_missing_seo(per_page)` — Posts without custom SEO
- `mwseo_set_seo_title(post_id, title)`
- `mwseo_set_seo_excerpt(post_id, excerpt)`

### Analytics
- `mwseo_get_analytics_data(start_date, end_date, metrics)` — Site traffic
- `mwseo_get_post_analytics(post_id, start_date, end_date)` — Per-post traffic
- `mwseo_get_analytics_top_countries(start_date, end_date)`
- `mwseo_get_analytics_top_pages(start_date, end_date)`

### AI Bot Traffic
- `mwseo_query_bot_traffic(start_date, end_date)` — AI crawler stats
- `mwseo_bot_profile(bot_name)` — Details about specific bot

## WooCommerce (opt-in, requires WooCommerce)

25 tools for store management.

- `wc_list_products(per_page, status, category, search)`
- `wc_get_product(product_id)`
- `wc_create_product(name, type, regular_price, description, ...)`
- `wc_update_product(product_id, ...)`
- `wc_list_orders(per_page, status, customer)`
- `wc_get_order(order_id)`
- `wc_update_order_status(order_id, status)`
- `wc_get_sales_report(period)` — Sales summary
- `wc_get_top_sellers(period)`
- `wc_get_low_stock_products(threshold)`

## Polylang (opt-in, requires Polylang)

11 tools for multilingual content.

- `pll_get_languages` — List configured languages
- `pll_translation_status` — Coverage overview
- `pll_get_posts_missing_translation(language, per_page)`
- `pll_create_translation(post_id, language, ...)` — Create linked translation
- `pll_get_post_language(post_id)`
- `pll_set_post_language(post_id, language)`

## Social Engine (opt-in, requires Social Engine)

8 tools for social media.

- `sclegn_list_accounts` — Connected social accounts
- `sclegn_post(account_id, content, media_url, scheduled_at)` — Schedule post
- `sclegn_publish_now(post_id)` — Publish immediately
- `sclegn_get_posts(account_id, status)`

## AI Features (always available with AI Engine)

- `mwai_vision(url, prompt)` — Analyze image via AI
- `mwai_image(prompt)` — Generate image, store in Media Library

## Dynamic REST (opt-in)

Raw access to WordPress REST API endpoints. More technical and limited compared to the optimized tools above.

- `wp_rest_get(endpoint, params)`
- `wp_rest_post(endpoint, body)`
- `wp_rest_put(endpoint, body)`
- `wp_rest_delete(endpoint)`
