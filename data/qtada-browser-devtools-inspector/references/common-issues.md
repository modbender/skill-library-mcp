# Common Frontend Issues & Solutions

Quick reference for diagnosing common issues found via DevTools.

## Console Errors

### 1. "Failed to load resource: net::ERR_FAILED"

**Cause:** Network request failed (404, 500, CORS, timeout)

**Diagnosis:**
```bash
node scripts/capture_network.js <url> --filter=failed
```

**Common Fixes:**
- Check API endpoint exists
- Verify correct baseURL in frontend config
- Check CORS headers
- Verify backend is running

---

### 2. "Access to XMLHttpRequest blocked by CORS policy"

**Cause:** Missing or incorrect CORS headers

**Diagnosis:**
```bash
node scripts/check_cors.js <url>
```

**Fixes:**
- Add `Access-Control-Allow-Origin` header in backend
- Set correct origin (not `*` if using credentials)
- Handle preflight OPTIONS requests
- Check Laravel CORS config (`config/cors.php`)

---

### 3. "Uncaught TypeError: Cannot read property 'X' of undefined"

**Cause:** Accessing property on undefined/null object

**Diagnosis:**
```bash
node scripts/capture_console.js <url> --filter=error
```

**Fixes:**
- Add null/undefined checks (`object?.property`)
- Ensure API data loaded before rendering
- Check network tab for failed API calls

---

### 4. "404 Not Found" on API endpoints

**Cause:** API route doesn't exist or wrong URL

**Diagnosis:**
```bash
node scripts/capture_network.js <url> --filter=failed --type=xhr
```

**Common Mistakes:**
- `/api/vendors` instead of `/api/superadmin/vendors`
- `/api/marketplace/products` instead of `/api/products`
- Wrong baseURL (localhost vs localhost:8000)

---

## Network Issues

### 1. Slow API Responses (>1s)

**Diagnosis:**
```bash
node scripts/analyze_performance.js <url>
node scripts/capture_network.js <url> --filter=slow --type=xhr
```

**Common Causes:**
- N+1 query problem (Laravel)
- Missing database indexes
- Large response payload
- No caching

**Fixes:**
- Use eager loading in Laravel
- Add database indexes
- Implement API pagination
- Enable Redis caching

---

### 2. Large Bundle Sizes

**Diagnosis:**
```bash
node scripts/analyze_performance.js <url>
# Look for largeResources
```

**Fixes:**
- Code splitting (React.lazy, dynamic imports)
- Tree shaking (Vite/Webpack)
- Minification (production build)
- Remove unused dependencies

---

### 3. Blocked Requests

**Diagnosis:**
```bash
node scripts/capture_network.js <url> --filter=failed
```

**Common Causes:**
- CORS (cross-origin)
- Content Security Policy
- Mixed content (HTTPS → HTTP)
- Ad blockers

---

## Performance Issues

### 1. High Time to First Byte (TTFB > 1s)

**Indicates:** Backend performance issue

**Fixes:**
- Optimize database queries
- Add caching (Redis)
- Enable OPCache (PHP)
- Use CDN for static assets

---

### 2. Long DOM Content Loaded (>3s)

**Indicates:** JavaScript blocking rendering

**Fixes:**
- Move scripts to bottom of body
- Use async/defer attributes
- Code splitting
- Reduce initial bundle size

---

### 3. Multiple Requests to Same Endpoint

**Indicates:** Missing caching or state management

**Fixes:**
- Implement React Query / SWR
- Use Redux/Zustand for global state
- Add HTTP caching headers
- Implement request deduplication

---

## ThreeU-Specific Issues

### Issue: Products Not Loading

**Symptoms:**
- Empty product list
- Console: "Failed to load /api/products"

**Diagnosis:**
```bash
node scripts/capture_console.js http://localhost:5177 --filter=error
node scripts/capture_network.js http://localhost:5177 --filter=failed --type=xhr
```

**Possible Causes:**
1. Backend not running
2. Wrong API baseURL in .env
3. BOM encoding in PHP files
4. Redis connection failed
5. Database down

---

### Issue: SuperAdmin 404 Errors

**Symptoms:**
- Vendor list empty
- Console: "404 /api/vendors"

**Diagnosis:**
```bash
node scripts/capture_network.js http://localhost:5179 --filter=failed
```

**Fix:**
Update API service to use `/api/superadmin/vendors`

---

### Issue: CORS Errors on localhost

**Symptoms:**
- "blocked by CORS policy" in console
- Network shows (failed) requests

**Diagnosis:**
```bash
node scripts/check_cors.js http://localhost:5177
```

**Fixes:**
1. Update Laravel `config/cors.php`:
   ```php
   'allowed_origins' => [
       'http://localhost:5177',
       'http://localhost:5179',
   ]
   ```
2. Clear config cache:
   ```bash
   docker exec threeu-api php artisan config:clear
   ```

---

## Workflow Examples

### Debug New Feature Not Working

```bash
# 1. Check console for errors
node scripts/capture_console.js http://localhost:5177 --filter=error

# 2. Check network for failed requests
node scripts/capture_network.js http://localhost:5177 --filter=failed

# 3. Check CORS if cross-origin requests
node scripts/check_cors.js http://localhost:5177

# 4. Review output and fix identified issues
```

### Optimize Slow Page

```bash
# 1. Measure current performance
node scripts/analyze_performance.js http://localhost:5177

# 2. Find slow resources
node scripts/capture_network.js http://localhost:5177 --filter=slow

# 3. Fix identified bottlenecks
# 4. Measure again to verify improvement
```
