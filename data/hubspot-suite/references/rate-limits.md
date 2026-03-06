# HubSpot Rate Limits & Best Practices

Understanding and handling HubSpot API rate limits effectively.

## Rate Limit Overview

### Private Apps
- **100 requests per 10 seconds** per app
- **Burst limit**: 150 requests (brief spikes allowed)
- **Daily limit**: 1,000,000 requests per day
- Limits reset on a sliding window

### OAuth Apps
- **100 requests per 10 seconds** per app
- **Burst limit**: 150 requests
- **Daily limit**: 1,000,000 requests per day
- Enterprise accounts may have higher limits

### Legacy API Keys
- **10 requests per second** per portal
- **Burst limit**: 100 requests per 10 seconds
- Lower limits than Private Apps

### Search API Limits
- **4 requests per second** (separate from main limits)
- **6 requests per second** for Enterprise accounts
- Applies to all `/search` endpoints

### Batch Operations
- **100 records maximum** per batch request
- Batch requests count as single API call
- More efficient than individual requests

## Rate Limit Headers

Every API response includes rate limit information:

```bash
curl -I -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/objects/contacts?limit=1"

# Response headers:
X-HubSpot-RateLimit-Daily: 1000000
X-HubSpot-RateLimit-Daily-Remaining: 999950
X-HubSpot-RateLimit-Interval-Milliseconds: 10000
X-HubSpot-RateLimit-Max: 100
X-HubSpot-RateLimit-Remaining: 99
X-HubSpot-RateLimit-Secondly: 10
X-HubSpot-RateLimit-Secondly-Remaining: 9
```

### Header Meanings
- `X-HubSpot-RateLimit-Max`: Requests per interval (usually 100)
- `X-HubSpot-RateLimit-Remaining`: Requests left in current interval
- `X-HubSpot-RateLimit-Interval-Milliseconds`: Interval duration (usually 10000ms)
- `X-HubSpot-RateLimit-Daily`: Daily request limit
- `X-HubSpot-RateLimit-Daily-Remaining`: Daily requests remaining

## Handle Rate Limit Errors

### 429 Response
When rate limited, API returns HTTP 429:

```json
{
  "status": "error",
  "message": "Rate limit exceeded",
  "correlationId": "abc-123-def"
}
```

### Retry Strategy
```bash
#!/bin/bash
make_api_request() {
    local url="$1"
    local max_retries=5
    local retry_count=0
    local backoff=1
    
    while [ $retry_count -lt $max_retries ]; do
        response=$(curl -s -w "%{http_code}" -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" "$url")
        http_code="${response: -3}"
        body="${response%???}"
        
        if [ "$http_code" = "200" ]; then
            echo "$body"
            return 0
        elif [ "$http_code" = "429" ]; then
            echo "Rate limited. Waiting ${backoff}s before retry $((retry_count + 1))/$max_retries" >&2
            sleep $backoff
            backoff=$((backoff * 2))  # Exponential backoff
            retry_count=$((retry_count + 1))
        else
            echo "HTTP $http_code: $body" >&2
            return 1
        fi
    done
    
    echo "Max retries exceeded" >&2
    return 1
}

# Usage
make_api_request "https://api.hubapi.com/crm/v3/objects/contacts"
```

## Rate Limit Monitoring

### Check Current Usage
```bash
check_rate_limits() {
    curl -I -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
      "https://api.hubapi.com/crm/v3/objects/contacts?limit=1" 2>/dev/null | \
    grep -E "X-HubSpot-RateLimit" | \
    while read -r line; do
        echo "$line"
    done
}

check_rate_limits
```

### Monitor Script
```bash
#!/bin/bash
monitor_rate_limits() {
    while true; do
        echo "=== Rate Limit Check $(date) ==="
        
        response_headers=$(curl -I -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
            "https://api.hubapi.com/crm/v3/objects/contacts?limit=1" 2>/dev/null)
        
        remaining=$(echo "$response_headers" | grep "X-HubSpot-RateLimit-Remaining" | cut -d' ' -f2 | tr -d '\r')
        max_requests=$(echo "$response_headers" | grep "X-HubSpot-RateLimit-Max" | cut -d' ' -f2 | tr -d '\r')
        daily_remaining=$(echo "$response_headers" | grep "X-HubSpot-RateLimit-Daily-Remaining" | cut -d' ' -f2 | tr -d '\r')
        
        echo "Interval: $remaining/$max_requests remaining"
        echo "Daily: $daily_remaining remaining"
        
        if [ "$remaining" -lt 10 ]; then
            echo "WARNING: Only $remaining requests remaining in current interval!"
        fi
        
        sleep 60  # Check every minute
    done
}
```

## Optimization Strategies

### 1. Batch Operations
Instead of individual requests:
```bash
# Bad: 100 individual requests
for id in {1..100}; do
    curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        "https://api.hubapi.com/crm/v3/objects/contacts/$id"
done

# Good: 1 batch request
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/batch/read" \
    -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "inputs": [{"id": "1"}, {"id": "2"}, {"id": "3"}],
        "properties": ["firstname", "lastname", "email"]
    }'
```

### 2. Efficient Pagination
```bash
paginate_all_contacts() {
    local after=""
    local limit=100
    local total_fetched=0
    
    while true; do
        local url="https://api.hubapi.com/crm/v3/objects/contacts?limit=$limit"
        [ -n "$after" ] && url="${url}&after=${after}"
        
        echo "Fetching batch starting after: $after" >&2
        
        response=$(make_api_request "$url")
        
        # Extract data
        echo "$response" | jq -r '.results[]'
        
        # Check for next page
        after=$(echo "$response" | jq -r '.paging.next.after // empty')
        batch_size=$(echo "$response" | jq -r '.results | length')
        total_fetched=$((total_fetched + batch_size))
        
        echo "Fetched $batch_size records (total: $total_fetched)" >&2
        
        [ -z "$after" ] && break
        
        # Small delay to prevent rapid requests
        sleep 0.1
    done
}
```

### 3. Property Selection
Request only needed properties:
```bash
# Bad: Fetches all properties
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
    "https://api.hubapi.com/crm/v3/objects/contacts"

# Good: Specific properties only  
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
    "https://api.hubapi.com/crm/v3/objects/contacts?properties=firstname,lastname,email"
```

### 4. Use Search API Carefully
Search API has lower limits (4 req/sec):
```bash
# Throttle search requests
search_with_throttle() {
    local query="$1"
    
    # Check if we made a search recently
    local last_search_file="/tmp/hubspot_last_search"
    local current_time=$(date +%s)
    
    if [ -f "$last_search_file" ]; then
        local last_search=$(cat "$last_search_file")
        local time_diff=$((current_time - last_search))
        
        # Ensure at least 0.25 seconds between search requests (4 req/sec = 1 req/0.25s)
        if [ $time_diff -lt 1 ]; then
            sleep $((1 - time_diff))
        fi
    fi
    
    echo "$current_time" > "$last_search_file"
    
    curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
        -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$query"
}
```

## Parallel Processing

### Safe Concurrent Requests
```bash
#!/bin/bash
process_contacts_parallel() {
    local contact_ids=("$@")
    local max_parallel=10  # Stay well under rate limits
    local pids=()
    
    for id in "${contact_ids[@]}"; do
        # Wait if we have too many background jobs
        while [ ${#pids[@]} -ge $max_parallel ]; do
            for i in "${!pids[@]}"; do
                if ! kill -0 "${pids[i]}" 2>/dev/null; then
                    unset "pids[i]"
                fi
            done
            pids=("${pids[@]}")  # Reindex array
            sleep 0.1
        done
        
        # Start background job
        {
            echo "Processing contact $id"
            make_api_request "https://api.hubapi.com/crm/v3/objects/contacts/$id"
        } &
        
        pids+=($!)
        
        # Small delay between starting jobs
        sleep 0.05
    done
    
    # Wait for all jobs to complete
    for pid in "${pids[@]}"; do
        wait "$pid"
    done
}
```

## Error Recovery Patterns

### Exponential Backoff Implementation
```bash
exponential_backoff() {
    local max_attempts=5
    local base_delay=1
    local max_delay=60
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if "$@"; then
            return 0
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            echo "Max attempts reached. Giving up." >&2
            return 1
        fi
        
        local delay=$((base_delay * (2 ** (attempt - 1))))
        [ $delay -gt $max_delay ] && delay=$max_delay
        
        echo "Attempt $attempt failed. Retrying in ${delay}s..." >&2
        sleep $delay
        
        attempt=$((attempt + 1))
    done
}

# Usage
exponential_backoff curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
    "https://api.hubapi.com/crm/v3/objects/contacts/12345"
```

## Performance Monitoring

### Request Timing
```bash
time_api_request() {
    local start_time=$(date +%s.%N)
    local response
    
    response=$(curl -s -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" "$1")
    local exit_code=$?
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l)
    
    echo "Request took: ${duration}s" >&2
    echo "$response"
    
    return $exit_code
}
```

### Daily Usage Tracking
```bash
track_daily_usage() {
    local usage_file="/tmp/hubspot_daily_usage_$(date +%Y-%m-%d)"
    local current_requests
    
    current_requests=$(curl -I -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        "https://api.hubapi.com/crm/v3/objects/contacts?limit=1" 2>/dev/null | \
        grep "X-HubSpot-RateLimit-Daily-Remaining" | \
        cut -d' ' -f2 | tr -d '\r')
    
    echo "$(date '+%H:%M:%S'): $current_requests requests remaining" >> "$usage_file"
}
```

## Best Practices Summary

### Do's
✅ Use batch operations when possible (max 100 records)  
✅ Implement exponential backoff for retries  
✅ Monitor rate limit headers  
✅ Request only needed properties  
✅ Use pagination efficiently  
✅ Cache responses when appropriate  
✅ Spread requests over time  

### Don'ts
❌ Make burst requests without checking limits  
❌ Ignore 429 errors  
❌ Request all properties when you only need a few  
❌ Use search API for simple gets  
❌ Exceed batch limits (>100 records)  
❌ Make parallel requests without throttling  
❌ Retry immediately after 429 errors  

### Emergency Throttling
If you hit rate limits repeatedly:
```bash
# Emergency brake - wait for full reset
emergency_throttle() {
    echo "Emergency throttling activated. Waiting 10 seconds for rate limit reset..."
    sleep 10
}
```

### Rate Limit-Aware Wrapper
```bash
hubspot_api() {
    local remaining
    
    # Check remaining requests
    remaining=$(curl -I -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        "https://api.hubapi.com/crm/v3/objects/contacts?limit=1" 2>/dev/null | \
        grep "X-HubSpot-RateLimit-Remaining" | \
        cut -d' ' -f2 | tr -d '\r')
    
    # If low on requests, wait
    if [ "${remaining:-0}" -lt 5 ]; then
        echo "Rate limit low ($remaining remaining). Waiting 10s..." >&2
        sleep 10
    fi
    
    # Make actual request with retry logic
    make_api_request "$@"
}
```