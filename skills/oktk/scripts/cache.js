/**
 * Cache - Hash-based deduplication for oktk
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

class Cache {
  constructor(options = {}) {
    this.enabled = options.cache !== false && process.env.OKTK_DISABLE !== 'true';
    this.ttl = options.ttl || parseInt(process.env.OKTK_CACHE_TTL) || 3600; // 1 hour default
    this.cacheDir = options.cacheDir || process.env.OKTK_CACHE_DIR || path.join(process.env.HOME, '.oktk', 'cache');
    this.debug = options.debug || process.env.OKTK_DEBUG === '1';

    // Ensure cache directory exists
    if (this.enabled) {
      this.ensureCacheDir();
    }
  }

  /**
   * Ensure cache directory exists
   */
  async ensureCacheDir() {
    try {
      await fs.promises.mkdir(this.cacheDir, { recursive: true });
    } catch (error) {
      console.error('Failed to create cache directory:', error.message);
      this.enabled = false;
    }
  }

  /**
   * Get cache file path for key
   */
  getCachePath(key) {
    return path.join(this.cacheDir, `${key}.json`);
  }

  /**
   * Get cached value
   */
  async get(key) {
    if (!this.enabled) return null;

    try {
      const cachePath = this.getCachePath(key);
      const data = await fs.promises.readFile(cachePath, 'utf8');
      const cached = JSON.parse(data);

      // Check if expired
      if (Date.now() - cached.timestamp > this.ttl * 1000) {
        if (this.debug) {
          console.log(`🗑️  Cache expired for ${key}`);
        }
        await this.delete(key);
        return null;
      }

      if (this.debug) {
        const age = Math.round((Date.now() - cached.timestamp) / 1000);
        console.log(`✅ Cache hit for ${key} (${age}s old)`);
      }

      return cached;

    } catch (error) {
      if (error.code === 'ENOENT') {
        // Cache miss
        if (this.debug) {
          console.log(`❌ Cache miss for ${key}`);
        }
        return null;
      }

      // Other error
      console.error('Cache read error:', error.message);
      return null;
    }
  }

  /**
   * Set cached value
   */
  async set(key, value) {
    if (!this.enabled) return false;

    try {
      const cachePath = this.getCachePath(key);
      const cacheData = {
        key,
        value,
        timestamp: Date.now(),
        ttl: this.ttl
      };

      await fs.promises.writeFile(
        cachePath,
        JSON.stringify(cacheData, null, 2),
        'utf8'
      );

      if (this.debug) {
        console.log(`💾 Cached ${key}`);
      }

      return true;

    } catch (error) {
      console.error('Cache write error:', error.message);
      return false;
    }
  }

  /**
   * Delete cached value
   */
  async delete(key) {
    if (!this.enabled) return false;

    try {
      const cachePath = this.getCachePath(key);
      await fs.promises.unlink(cachePath);
      return true;
    } catch (error) {
      if (error.code !== 'ENOENT') {
        console.error('Cache delete error:', error.message);
      }
      return false;
    }
  }

  /**
   * Clear all cache
   */
  async clear(filter = null) {
    if (!this.enabled) return 0;

    try {
      let files;

      if (filter) {
        // Clear only files matching filter pattern
        const allFiles = await fs.promises.readdir(this.cacheDir);
        files = allFiles.filter(f => f.includes(filter));
      } else {
        // Clear all files
        files = await fs.promises.readdir(this.cacheDir);
      }

      let deleted = 0;

      for (const file of files) {
        try {
          await fs.promises.unlink(path.join(this.cacheDir, file));
          deleted++;
        } catch (error) {
          console.error(`Failed to delete ${file}:`, error.message);
        }
      }

      if (this.debug) {
        console.log(`🗑️  Cleared ${deleted} cache file(s)`);
      }

      return deleted;

    } catch (error) {
      console.error('Cache clear error:', error.message);
      return 0;
    }
  }

  /**
   * Get cache statistics
   */
  async getStats() {
    if (!this.enabled) {
      return { enabled: false };
    }

    try {
      const files = await fs.promises.readdir(this.cacheDir);
      let totalSize = 0;
      let entries = 0;
      let expired = 0;
      const now = Date.now();

      for (const file of files) {
        try {
          const cachePath = path.join(this.cacheDir, file);
          const stats = await fs.promises.stat(cachePath);
          totalSize += stats.size;
          entries++;

          // Check if expired
          const data = await fs.promises.readFile(cachePath, 'utf8');
          const cached = JSON.parse(data);
          if (now - cached.timestamp > this.ttl * 1000) {
            expired++;
          }
        } catch (error) {
          // Skip invalid cache files
        }
      }

      return {
        enabled: true,
        entries,
        totalSize,
        expired,
        ttl: this.ttl,
        directory: this.cacheDir
      };

    } catch (error) {
      console.error('Cache stats error:', error.message);
      return { enabled: true, error: error.message };
    }
  }

  /**
   * Clean expired cache entries
   */
  async cleanExpired() {
    if (!this.enabled) return 0;

    try {
      const files = await fs.promises.readdir(this.cacheDir);
      const now = Date.now();
      let cleaned = 0;

      for (const file of files) {
        try {
          const cachePath = path.join(this.cacheDir, file);
          const data = await fs.promises.readFile(cachePath, 'utf8');
          const cached = JSON.parse(data);

          if (now - cached.timestamp > this.ttl * 1000) {
            await fs.promises.unlink(cachePath);
            cleaned++;
          }
        } catch (error) {
          // Skip or delete invalid cache files
          try {
            await fs.promises.unlink(path.join(this.cacheDir, file));
            cleaned++;
          } catch {
            // Ignore
          }
        }
      }

      if (this.debug && cleaned > 0) {
        console.log(`🧹 Cleaned ${cleaned} expired cache entries`);
      }

      return cleaned;

    } catch (error) {
      console.error('Cache cleanup error:', error.message);
      return 0;
    }
  }

  /**
   * Hash key (shorten long keys)
   */
  hashKey(key) {
    if (key.length <= 16) {
      return key;
    }

    return crypto
      .createHash('md5')
      .update(key)
      .digest('hex')
      .substring(0, 16);
  }
}

module.exports = Cache;
