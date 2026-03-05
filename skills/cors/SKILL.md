---
name: CORS
description: Configure Cross-Origin Resource Sharing correctly to avoid security issues and debugging pain.
metadata: {"clawdbot":{"emoji":"🔀","os":["linux","darwin","win32"]}}
---

## Preflight Triggers

- Any header except: Accept, Accept-Language, Content-Language, Content-Type (with restrictions)
- Content-Type other than: application/x-www-form-urlencoded, multipart/form-data, text/plain
- Methods: PUT, DELETE, PATCH, or any custom method
- ReadableStream in request body
- Event listeners on XMLHttpRequest.upload
- One trigger = preflight; simple requests skip OPTIONS entirely

## Credentials Mode

- `Access-Control-Allow-Origin: *` incompatible with credentials—must specify exact origin
- `Access-Control-Allow-Credentials: true` required for cookies/auth headers
- Fetch: `credentials: 'include'`; XHR: `withCredentials = true`
- Without credentials mode, cookies not sent even to same origin for cross-origin requests

## Wildcard Limitations

- `*` doesn't match subdomains—`*.example.com` is invalid, not a pattern
- Can't use `*` with credentials—specify origin dynamically from request
- `Access-Control-Allow-Headers: *` works in most browsers but not all—list explicitly for compatibility
- `Access-Control-Expose-Headers: *` same issue—list headers you need to expose

## Origin Validation

- Check Origin header against allowlist—don't reflect blindly (security risk)
- Regex matching pitfall: `example.com` matches `evilexample.com`—anchor the pattern
- `null` origin: sandboxed iframes, file:// URLs—usually reject, never allow as trusted
- Missing Origin header: same-origin or non-browser client—handle explicitly

## Vary Header (Critical)

- Always include `Vary: Origin` when response depends on origin—even if you allow only one
- Without Vary: CDN/proxy caches response for one origin, serves to others—breaks CORS
- Add `Vary: Access-Control-Request-Headers, Access-Control-Request-Method` for preflight caching correctness

## Exposed Headers

- By default, JS can only read: Cache-Control, Content-Language, Content-Type, Expires, Last-Modified, Pragma
- Custom headers invisible to JS unless listed in `Access-Control-Expose-Headers`
- `X-Request-ID`, `X-RateLimit-*`, etc. need explicit exposure—common oversight

## Preflight Caching

- `Access-Control-Max-Age: 86400` caches preflight for 24h—reduces OPTIONS traffic significantly
- Chrome caps at 2 hours; Firefox at 24 hours—values above are silently reduced
- Cached per origin + URL + request characteristics—not globally
- Set to 0 or omit during development—caching hides config changes

## Debugging

- CORS error in browser = request reached server and came back—check server logs
- Preflight failure: server must return 2xx with CORS headers on OPTIONS—404/500 = failure
- Opaque response in fetch: `mode: 'no-cors'` succeeds but response is empty—usually not what you want
- Network tab shows CORS errors; Console shows which header is missing

## Common Server Mistakes

- Only setting CORS headers on main handler, not OPTIONS—preflight fails
- Setting headers after error response—CORS headers missing on 4xx/5xx breaks error handling
- Proxy stripping headers—verify headers reach client, not just that server sets them
- `Access-Control-Allow-Origin: "*", "https://example.com"`—must be single value, not list

## Security

- Don't reflect Origin header blindly—validate against allowlist first
- Private Network Access: Chrome requires `Access-Control-Allow-Private-Network: true` for localhost access from public web
- CORS doesn't prevent request from being sent—just blocks response reading; server still processes it
- Sensitive endpoints: don't rely on CORS alone; use authentication + CSRF tokens
