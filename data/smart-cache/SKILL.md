---
id: smart-cache
version: 1.0.0
name: Smart Cache
description: Intelligent caching with LRU/LFU strategies and TTL management
author: NeoClaw Team
category: utility
tags:
  - caching
  - performance
  - lru
  - lfu
dependencies: []
---

# Smart Cache

High-performance caching with multiple eviction strategies.

## Implementation

```javascript
class SmartCache {
  constructor(options = {}) {
    this.strategy = options.strategy || 'lru'; // 'lru' or 'lfu'
    this.maxSize = options.maxSize || 500;
    this.defaultTTL = options.defaultTTL || 3600000; // 1 hour
    
    this.cache = new Map();
    this.accessCount = new Map();
    this.accessOrder = [];
  }

  set(key, value, ttl = this.defaultTTL) {
    // Evict if at capacity
    if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
      this.evict();
    }

    const entry = {
      value,
      expiresAt: Date.now() + ttl,
      createdAt: Date.now()
    };

    this.cache.set(key, entry);
    this.accessCount.set(key, 0);
    this.updateAccessOrder(key);

    return true;
  }

  get(key) {
    const entry = this.cache.get(key);

    if (!entry) {
      return { hit: false, value: null };
    }

    // Check TTL
    if (Date.now() > entry.expiresAt) {
      this.delete(key);
      return { hit: false, value: null, reason: 'expired' };
    }

    // Update access tracking
    this.accessCount.set(key, (this.accessCount.get(key) || 0) + 1);
    this.updateAccessOrder(key);

    return { hit: true, value: entry.value };
  }

  delete(key) {
    this.cache.delete(key);
    this.accessCount.delete(key);
    this.accessOrder = this.accessOrder.filter(k => k !== key);
  }

  evict() {
    if (this.strategy === 'lru') {
      this.evictLRU();
    } else if (this.strategy === 'lfu') {
      this.evictLFU();
    }
  }

  evictLRU() {
    // Remove least recently used
    if (this.accessOrder.length > 0) {
      const keyToEvict = this.accessOrder[0];
      this.delete(keyToEvict);
    }
  }

  evictLFU() {
    // Remove least frequently used
    let minCount = Infinity;
    let keyToEvict = null;

    for (const [key, count] of this.accessCount.entries()) {
      if (count < minCount) {
        minCount = count;
        keyToEvict = key;
      }
    }

    if (keyToEvict) {
      this.delete(keyToEvict);
    }
  }

  updateAccessOrder(key) {
    // Remove from current position
    this.accessOrder = this.accessOrder.filter(k => k !== key);
    // Add to end (most recent)
    this.accessOrder.push(key);
  }

  clear() {
    this.cache.clear();
    this.accessCount.clear();
    this.accessOrder = [];
  }

  getStats() {
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      strategy: this.strategy,
      hitRate: this.calculateHitRate()
    };
  }

  calculateHitRate() {
    // Simplified - would track actual hits/misses in production
    return Math.round((this.cache.size / this.maxSize) * 100);
  }
}

// Export for OpenClaw
module.exports = { SmartCache };
```

## Usage

```javascript
const cache = new skills.smartCache.SmartCache({
  strategy: 'lru',
  maxSize: 500,
  defaultTTL: 3600000
});

// Set value
cache.set('key1', { data: 'value' }, 60000);

// Get value
const result = cache.get('key1');
if (result.hit) {
  console.log('Cache hit:', result.value);
}

// Stats
console.log(cache.getStats());
```

## Configuration

```json
{
  "strategy": "lru",
  "maxSize": 500,
  "defaultTTL": 3600000
}
```
