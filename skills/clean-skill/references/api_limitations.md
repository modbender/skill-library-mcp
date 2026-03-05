# API and Data Source Limitations

## Overview

Both Dianping and Xiaohongshu do not provide public APIs for restaurant data access. This skill relies on web scraping, which has significant limitations and legal considerations.

## Dianping (大众点评)

### Access Method
- **No public API**: Dianping API requires business partnership
- **Web scraping**: Primary method for data collection

### Limitations

1. **Anti-Scraping Measures**
   - IP blocking after 50-100 requests
   - CAPTCHA challenges
   - Request rate monitoring
   - User-Agent detection

2. **Rate Limiting**
   - Recommended: 1 request per 2 seconds minimum
   - With rotating proxies: 1 request per 1 second
   - Residential proxies required for sustained access

3. **Dynamic Content**
   - JavaScript rendering required for full data
   - Selenium or Playwright needed
   - Slower than static HTML scraping

4. **Data Completeness**
   - Some restaurants hide review counts
   - Price ranges may be missing
   - Tags are user-generated and inconsistent

### Legal Considerations
- Terms of Service prohibit scraping
- Commercial use requires explicit permission
- Data is protected under Chinese copyright law

**Recommendation**: Use for personal research only. Consider official API for commercial use.

## Xiaohongshu (小红书)

### Access Method
- **No public API**: No API available at all
- **Web scraping**: Only method, highly restricted

### Limitations

1. **Authentication Required**
   - Most searches require logged-in cookies
   - Cookies expire after 24-48 hours
   - Need to periodically re-authenticate

2. **Strict Anti-Scraping**
   - Aggressive IP blocking (10-20 requests)
   - Device fingerprinting
   - Behavior analysis (mouse movement, timing)

3. **Rate Limiting**
   - Recommended: 1 request per 3 seconds minimum
   - With rotating proxies: 1 request per 2 seconds
   - Residential proxies mandatory

4. **Data Structure**
   - Unstructured user-generated content
   - Restaurant names extracted from text (NLP required)
   - No standardized address format
   - Sentiment analysis required for quality assessment

5. **Platform-Specific Issues**
   - Influencer bias (paid promotions)
   - Fake reviews and bot activity
   - Trend-based spikes in engagement

### Legal Considerations
- Strict Terms of Service prohibiting all scraping
- Data protection concerns (user-generated content)
- Commercial use explicitly prohibited

**Recommendation**: Use only for personal research. Be transparent about data sources.

## Implementation Challenges

### 1. Restaurant Name Matching

**Problem**: Same restaurant has different names on platforms
- Dianping: "银座寿司"
- Xiaohongshu: "银座寿司静安店" or "静安银座日料"

**Solution**: Fuzzy matching with similarity threshold
- Uses `thefuzz` library for Levenshtein distance
- Configurable threshold (default: 0.7)
- May need manual verification for low-confidence matches

### 2. Location Variations

**Problem**: Same location expressed differently
- Dianping: "静安区南京西路"
- Xiaohongshu: "静安" or "上海静安"

**Solution**: Normalize location strings
- Use administrative district codes
- Map common aliases to standard names

### 3. Data Freshness

**Problem**: Scraped data becomes stale
- Ratings change daily
- New reviews constantly added
- Restaurants close or move

**Solution**:
- Cache data for 24 hours maximum
- Implement delta updates for changed restaurants
- Schedule periodic re-scraping

## Mitigation Strategies

### Technical Mitigations

1. **Proxy Rotation**
   - Use residential proxy pools (e.g., Bright Data, Smartproxy)
   - Rotate every 5-10 requests
   - Geographic targeting (match location search)

2. **Request Delays**
   - Randomize delays (1.5x - 3x recommended rate)
   - Mimic human browsing patterns
   - Avoid burst requests

3. **Session Management**
   - Rotate user agents randomly
   - Maintain cookie jars for authenticated sessions
   - Implement exponential backoff on errors

4. **Caching**
   - Cache restaurant data locally
   - Invalidate after 24 hours
   - Use Redis or SQLite for persistence

### Legal Mitigations

1. **Use for Personal Research Only**
   - No commercial applications
   - No resale of data
   - Attribution to platforms

2. **Rate Limiting**
   - Respect platforms' server load
   - Don't abuse public endpoints
   - Implement aggressive delays

3. **Data Privacy**
   - Anonymize user information
   - Don't store personal identifiers
   - Aggregate statistics only

## Alternative Approaches

### 1. Official APIs (Recommended for Commercial Use)

**Dianping Open Platform**
- Requires business registration
- API key application process
- Rate limits apply but documented
- Legal and reliable
- Contact: https://open.dianping.com/

**Cost**: Free tier available, paid tiers for higher volume

### 2. Third-Party Data Providers

- Meituan API (Dianping's parent company)
- Qichacha (company data)
- Local Chinese data providers

**Pros**: Legal, reliable, updated
**Cons**: Expensive, may lack granular data

### 3. Manual Research

For small-scale queries:
- Manual search on both platforms
- Spreadsheet comparison
- Human judgment for matching

**Pros**: No technical or legal issues
**Cons**: Not scalable, time-consuming

## Compliance Checklist

For any deployment:

- [ ] Reviewed Terms of Service for both platforms
- [ ] Implemented rate limiting (≥2 seconds per request)
- [ ] Using residential proxies (not datacenter)
- [ ] Data usage is for personal research only
- [ ] No resale or commercial exploitation
- [ ] Respecting robots.txt
- [ ] Implemented caching to minimize requests
- [ ] Anonymizing user-generated content
- [ ] Providing attribution when displaying data

## Disclaimer

This skill is provided for educational purposes only. Users are responsible for ensuring their use complies with applicable laws and platform terms of service. The authors assume no liability for misuse.

**Last Updated**: 2026-02-09
