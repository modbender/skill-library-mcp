#!/usr/bin/env node
"use strict";

const { Logger } = require("./logger");

class ProxyHandler {
  constructor(config = {}, logger) {
    this.logger = logger || new Logger({ silent: true });
    this.proxies = (config.proxies || []).map((p, idx) => ({
      ...this._normalize(p),
      index: idx,
      healthy: true,
      failCount: 0,
      lastUsed: null,
      lastChecked: null,
    }));
    this.currentIndex = 0;
    this.maxFailures = config.maxFailures || 3;
    this.rotationStrategy = config.rotationStrategy || "round-robin";
  }

  /**
   * Normalize a proxy entry to a standard format.
   */
  _normalize(proxy) {
    if (typeof proxy === "string") {
      const url = new URL(proxy);
      return {
        host: url.hostname,
        port: parseInt(url.port, 10) || 8080,
        protocol: url.protocol.replace(":", "") || "http",
        auth: url.username
          ? { username: url.username, password: url.password || "" }
          : null,
      };
    }
    return {
      host: proxy.host || "127.0.0.1",
      port: proxy.port || 8080,
      protocol: proxy.protocol || "http",
      auth: proxy.auth || null,
    };
  }

  /**
   * Get the current active proxy configuration.
   * @returns {object|null}
   */
  getActive() {
    const healthy = this.proxies.filter((p) => p.healthy);
    if (healthy.length === 0) {
      this.logger.warn("No healthy proxies available");
      return null;
    }

    let selected;
    switch (this.rotationStrategy) {
      case "least-used":
        selected = healthy.sort(
          (a, b) => (a.lastUsed || 0) - (b.lastUsed || 0)
        )[0];
        break;
      case "random":
        selected = healthy[Math.floor(Math.random() * healthy.length)];
        break;
      case "round-robin":
      default:
        // Find next healthy proxy starting from currentIndex
        selected = null;
        for (let i = 0; i < this.proxies.length; i++) {
          const idx = (this.currentIndex + i) % this.proxies.length;
          if (this.proxies[idx].healthy) {
            selected = this.proxies[idx];
            this.currentIndex = (idx + 1) % this.proxies.length;
            break;
          }
        }
        break;
    }

    if (selected) {
      selected.lastUsed = Date.now();
      this.logger.debug(`Active proxy: ${selected.host}:${selected.port}`);
    }

    return selected
      ? {
          host: selected.host,
          port: selected.port,
          protocol: selected.protocol,
          auth: selected.auth,
          url: this._toUrl(selected),
        }
      : null;
  }

  _toUrl(proxy) {
    const auth = proxy.auth
      ? `${proxy.auth.username}:${proxy.auth.password}@`
      : "";
    return `${proxy.protocol}://${auth}${proxy.host}:${proxy.port}`;
  }

  /**
   * Rotate to the next proxy in the list.
   * @returns {object|null}
   */
  rotate() {
    this.logger.info("Rotating proxy");
    return this.getActive();
  }

  /**
   * Mark a proxy as failed. After maxFailures, mark as unhealthy.
   * @param {string} host
   */
  markFailed(host) {
    const proxy = this.proxies.find((p) => p.host === host);
    if (!proxy) {
      this.logger.warn(`Proxy not found: ${host}`);
      return;
    }

    proxy.failCount++;
    this.logger.warn(`Proxy ${host} failure #${proxy.failCount}`);

    if (proxy.failCount >= this.maxFailures) {
      proxy.healthy = false;
      this.logger.error(`Proxy ${host} marked unhealthy after ${proxy.failCount} failures`);
    }
  }

  /**
   * Mark a proxy as healthy and reset its failure count.
   * @param {string} host
   */
  markHealthy(host) {
    const proxy = this.proxies.find((p) => p.host === host);
    if (proxy) {
      proxy.healthy = true;
      proxy.failCount = 0;
      proxy.lastChecked = Date.now();
      this.logger.debug(`Proxy ${host} marked healthy`);
    }
  }

  /**
   * Run health checks on all proxies.
   * In a real implementation this would make test connections.
   * Here we simulate by checking failure counts.
   * @returns {Array} list of proxy statuses
   */
  healthCheck() {
    const results = this.proxies.map((p) => ({
      host: p.host,
      port: p.port,
      healthy: p.healthy,
      failCount: p.failCount,
      lastChecked: new Date().toISOString(),
    }));

    // Reset proxies with fewer failures than threshold
    for (const proxy of this.proxies) {
      if (!proxy.healthy && proxy.failCount < this.maxFailures * 2) {
        proxy.healthy = true;
        proxy.failCount = Math.max(0, proxy.failCount - 1);
        this.logger.info(`Proxy ${proxy.host} recovered during health check`);
      }
      proxy.lastChecked = Date.now();
    }

    this.logger.info("Health check completed", {
      total: results.length,
      healthy: results.filter((r) => r.healthy).length,
    });

    return results;
  }

  /**
   * Add a new proxy to the pool.
   * @param {string|object} proxy
   */
  addProxy(proxy) {
    const normalized = this._normalize(proxy);
    const exists = this.proxies.some(
      (p) => p.host === normalized.host && p.port === normalized.port
    );
    if (exists) {
      this.logger.warn(`Proxy ${normalized.host}:${normalized.port} already exists`);
      return false;
    }

    this.proxies.push({
      ...normalized,
      index: this.proxies.length,
      healthy: true,
      failCount: 0,
      lastUsed: null,
      lastChecked: null,
    });
    this.logger.info(`Added proxy ${normalized.host}:${normalized.port}`);
    return true;
  }

  /**
   * Remove a proxy from the pool.
   * @param {string} host
   */
  removeProxy(host) {
    const idx = this.proxies.findIndex((p) => p.host === host);
    if (idx === -1) return false;
    this.proxies.splice(idx, 1);
    this.logger.info(`Removed proxy ${host}`);
    return true;
  }

  /**
   * Get status summary of all proxies.
   */
  getStatus() {
    return {
      total: this.proxies.length,
      healthy: this.proxies.filter((p) => p.healthy).length,
      unhealthy: this.proxies.filter((p) => !p.healthy).length,
      strategy: this.rotationStrategy,
      proxies: this.proxies.map((p) => ({
        host: p.host,
        port: p.port,
        protocol: p.protocol,
        healthy: p.healthy,
        failCount: p.failCount,
      })),
    };
  }
}

module.exports = { ProxyHandler };
