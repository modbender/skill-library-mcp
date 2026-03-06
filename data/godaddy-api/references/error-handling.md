# Error Handling

## Common HTTP Status Codes

### 401 Unauthorized
**Cause**: Invalid or missing API credentials

**Solutions**:
- Check `GODADDY_API_KEY` is set correctly
- Check `GODADDY_API_SECRET` is set correctly
- Verify credentials at <https://developer.godaddy.com/keys>
- Ensure no extra whitespace in env vars

### 403 Forbidden / ACCESS_DENIED
**Cause**: Valid auth but account doesn't meet production API requirements

GoDaddy locks production endpoints based on account size:
- **Availability API**: Requires **50+ domains** in account
- **Management & DNS APIs**: Requires **10+ domains** OR **Discount Domain Club – Domain Pro Plan**

**Solutions**:
- **Quick fix**: Use OTE environment for testing (`export GODADDY_API_BASE_URL="https://api.ote-godaddy.com"`)
- **Unlock production**: Subscribe to Discount Domain Club – Domain Pro Plan (also gives lower domain pricing)
- **Accumulate domains**: Once you have 10+ domains, management/DNS APIs unlock automatically
- For purchases: verify Good as Gold funding is enabled

**Common scenario**: You create a production API key, call `/v1/domains`, get `ACCESS_DENIED` or empty results — your account just doesn't meet the domain count threshold.

### 404 Not Found
**Cause**: Resource doesn't exist

**Solutions**:
- Verify domain name spelling
- Check domain is in your account
- Confirm endpoint URL is correct

### 422 Unprocessable Entity
**Cause**: Request payload is malformed or invalid

**Solutions**:
- Validate JSON syntax with `jq`
- Check required fields are present
- Verify data types (strings, numbers, booleans)
- Review payload examples in [request-bodies.md](request-bodies.md)
- Use `/v1/domains/purchase/validate` before actual purchase

### 429 Too Many Requests
**Cause**: Rate limit exceeded (60 requests/min per endpoint)

**Solutions**:
- Wait 60 seconds before retrying
- Implement exponential backoff
- Batch operations when possible
- Consider caching responses

### 500 Internal Server Error
**Cause**: GoDaddy API issue

**Solutions**:
- Retry after a few seconds
- Check GoDaddy status page
- If persistent, contact GoDaddy support

## Error Response Format

Typical error response:
```json
{
  "code": "INVALID_BODY",
  "message": "Request body doesn't fulfill schema",
  "fields": [
    {
      "path": "contactAdmin.email",
      "message": "Invalid email format"
    }
  ]
}
```

## Debugging Tips

1. **Test in OTE first**: Use `https://api.ote-godaddy.com` to test without affecting production
2. **Validate JSON**: Run `cat payload.json | jq .` before sending
3. **Inspect curl output**: Add `-v` flag to curl for verbose debugging
4. **Check response**: Pipe output to `jq` for readable formatting
5. **Redact secrets**: Never log `GODADDY_API_KEY` or `GODADDY_API_SECRET`

## Example Debug Session

```bash
# Test auth
./scripts/gd-domains.sh list

# If 401, check env
echo "Key: ${GODADDY_API_KEY}"
echo "Secret: ${GODADDY_API_SECRET:0:5}..." # partial for security
echo "URL: ${GODADDY_API_BASE_URL}"

# Validate JSON payload
cat payload.json | jq .

# Test with verbose curl
curl -v -X GET "${GODADDY_API_BASE_URL}/v1/domains" \
  -H "Authorization: sso-key ${GODADDY_API_KEY}:${GODADDY_API_SECRET}" \
  -H "Accept: application/json"
```
