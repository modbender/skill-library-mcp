# Troubleshooting WordPress API Issues

Common problems and solutions when working with WordPress REST API and Gutenberg.

## Authentication Issues

### "rest_cookie_invalid_nonce" or 403 errors

**Problem**: Authentication failing despite correct credentials.

**Solutions**:
1. **Application Password format**: Ensure you're using the exact 24-character phrase with spaces. Don't modify it.
2. **HTTPS required**: WordPress may require HTTPS for authentication. Ensure your site uses SSL.
3. **User permissions**: The user must have `edit_posts` capability. Check user role.
4. **Basic Auth plugin**: If using Basic Auth, ensure the plugin is installed and activated.
   - Popular plugins: "Application Passwords" (built-in), "Basic Auth", "JWT Authentication"
5. **CORS issues**: If making requests from browser JavaScript, configure CORS headers.

### JWT Authentication fails

**Problem**: Token request returns 403 or "invalid_username".

**Solutions**:
1. Ensure JWT plugin is installed and configured.
2. Check secret key in WordPress configuration.
3. Verify token expiration (default 7 days).
4. Use `curl` to test:
   ```bash
   curl -X POST https://site.com/wp-json/jwt-auth/v1/token \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"password"}'
   ```

## Gutenberg Block Problems

### Blocks disappear or are stripped

**Problem**: Blocks are removed when saving via API.

**Causes and fixes**:
1. **Invalid block HTML**: Ensure block comments are properly formed.
   - Correct: `<!-- wp:paragraph --><p>Text</p><!-- /wp:paragraph -->`
   - Wrong: `<!-- wp:paragraph --><p>Text</p>` (missing closing comment)
2. **Unregistered block**: Custom blocks must be registered on the server.
   - Use only core blocks unless you've registered custom blocks.
   - Check block namespace: `wp:myplugin/my-block` requires plugin active.
3. **Block validation**: WordPress validates blocks. Test with simple paragraph first.
4. **Content sanitization**: WordPress may strip certain HTML tags.
   - Use `wp_kses_post` compatible tags only.
   - Avoid script tags unless user has `unfiltered_html` capability.

### Blocks render incorrectly

**Problem**: Blocks appear as raw HTML or misformatted.

**Solutions**:
1. **Check block alignment classes**: Ensure alignment classes match WordPress CSS.
2. **Missing CSS**: Some blocks require theme styles. Test with default theme.
3. **Image IDs**: When using `wp:image {"id":123}`, ensure media ID exists.
4. **Nested blocks**: Complex layouts (columns, groups) must have proper nesting.

## API Endpoint Issues

### 404 "No route was found"

**Problem**: API endpoint not accessible.

**Solutions**:
1. **Permalinks**: Ensure pretty permalinks are enabled (Settings → Permalinks).
2. **REST API disabled**: Some security plugins disable REST API. Check plugin settings.
3. **Custom endpoint**: Verify you're using correct namespace for custom post types.
4. **WordPress version**: Ensure WordPress 4.7+ (REST API v2).

### 400 "Invalid parameter"

**Problem**: Request fails with parameter validation error.

**Solutions**:
1. **Read error message**: WordPress provides specific parameter errors.
2. **Check data types**: Categories/tags should be arrays of IDs, not names.
3. **Status values**: Use only: `draft`, `publish`, `pending`, `private`, `future`.
4. **Date format**: Use ISO 8601: `2025-01-15T10:00:00`.

## Media Upload Issues

### "Sorry, this file type is not permitted"

**Problem**: File upload rejected.

**Solutions**:
1. **Check MIME types**: WordPress has allowed file types. Common images (jpg, png, gif) are allowed.
2. **File size limit**: Hosting may limit uploads. Check `upload_max_filesize` in PHP.
3. **File name**: Remove special characters, use lowercase extensions.
4. **Alternative**: Upload via WordPress admin first, then use existing media ID.

### "Missing attachment file"

**Problem**: Media created but file not attached.

**Solutions**:
1. **Use multipart/form-data**: Not `application/json`.
2. **Correct field name**: Use `file` as field name.
3. **Content-Type header**: Should match file type (`image/jpeg`, etc.).
4. **Test with curl**:
   ```bash
   curl -X POST https://site.com/wp-json/wp/v2/media \
     -u "user:pass" \
     -F "file=@image.jpg" \
     -F "title=My Image"
   ```

## Performance Problems

### Slow API responses

**Problem**: Requests take too long.

**Optimizations**:
1. **Reduce embed**: Add `?_embed=false` to requests.
2. **Limit fields**: Use `?_fields=id,title` to reduce payload.
3. **Cache responses**: Implement client-side caching.
4. **Pagination**: Request fewer items per page.
5. **Server-side**: Consider caching plugin (WP Rocket, W3 Total Cache).

### Timeouts during batch operations

**Problem**: Multiple requests cause timeouts.

**Solutions**:
1. **Add delays**: Sleep 1-2 seconds between requests.
2. **Batch operations**: Use WordPress's batch endpoint if available.
3. **Increase timeout**: Client-side timeout settings.
4. **Background processing**: Consider WordPress cron or queue.

## Cross-Origin (CORS) Issues

**Problem**: Browser blocks API requests.

**Solutions**:
1. **Install CORS plugin**: "WP REST API - CORS" or similar.
2. **Add headers manually**:
   ```php
   // In theme's functions.php
   add_action('rest_api_init', function() {
     remove_filter('rest_pre_serve_request', 'rest_send_cors_headers');
     add_filter('rest_pre_serve_request', function($value) {
       header('Access-Control-Allow-Origin: *');
       header('Access-Control-Allow-Methods: GET, POST, PUT, OPTIONS');
       header('Access-Control-Allow-Credentials: true');
       return $value;
     });
   }, 15);
   ```
3. **Proxy requests**: Route through same-origin server.

## SSL/TLS Issues

**Problem**: Certificate verification fails.

**Solutions**:
1. **Self-signed certs**: Disable verification (not recommended for production).
   ```python
   # Python requests
   requests.post(url, auth=auth, verify=False)
   ```
2. **Missing intermediate certificates**: Install full certificate chain.
3. **Use HTTP**: Only for local development.

## Debugging Techniques

### Enable WordPress debug

Add to `wp-config.php`:
```php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
define('WP_DEBUG_DISPLAY', false);
```

Check `wp-content/debug.log` for errors.

### Log API requests

```python
import logging
logging.basicConfig(level=logging.DEBUG)

import requests
requests.get(url, auth=auth)  # Will log full request/response
```

### Test with Postman or curl

1. **Verify endpoint availability**:
   ```bash
   curl -I https://site.com/wp-json/
   ```

2. **Test authentication**:
   ```bash
   curl -u "user:pass" https://site.com/wp-json/wp/v2/users/me
   ```

3. **Test post creation**:
   ```bash
   curl -X POST https://site.com/wp-json/wp/v2/posts \
     -u "user:pass" \
     -H "Content-Type: application/json" \
     -d '{"title":"Test","status":"draft"}'
   ```

### Check REST API index

Visit `https://site.com/wp-json/` to see all available routes.

## Common Error Messages

### "rest_forbidden" / "rest_cannot_edit"
User lacks capability. Ensure user role has `edit_posts` permission.

### "rest_invalid_json"
Invalid JSON in request body. Check for trailing commas, unquoted keys.

### "rest_post_invalid_id"
Post ID doesn't exist or user cannot access.

### "rest_invalid_param"
Parameter validation failed. Check error details in response.

### "rest_upload_invalid_file_type"
File type not allowed. Check WordPress allowed mime types.

## WordPress.com Specific Issues

### OAuth2 authentication required
Register application at [WordPress.com Developer](https://developer.wordpress.com/apps/).

### Rate limiting
WordPress.com enforces rate limits (typically 120 requests/minute). Implement retry with exponential backoff.

### Different endpoint structure
Use `https://public-api.wordpress.com/wp/v2/sites/{site_id}/` as base URL.

## Getting Help

1. **WordPress REST API Handbook**: https://developer.wordpress.org/rest-api/
2. **Gutenberg Handbook**: https://developer.wordpress.org/block-editor/
3. **Stack Overflow**: Tag with `wordpress-rest-api`
4. **WordPress Support Forums**: https://wordpress.org/support/