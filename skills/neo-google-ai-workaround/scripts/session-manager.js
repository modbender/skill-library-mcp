#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { Logger } = require("./logger");

class SessionManager {
  constructor(config = {}, logger) {
    this.logger = logger || new Logger({ silent: true });
    this.sessionDir =
      config.sessionDir ||
      path.join(__dirname, "..", "assets", ".sessions");
    this.maxSessions = config.maxSessions || 5;
    this.sessionTTL = config.sessionTTL || 3600000; // 1 hour default
    this.sessions = new Map();
    this.activeSessionId = null;
  }

  /**
   * Create a new session with optional authentication tokens.
   * @param {object} options - { token, refreshToken, proxy, metadata }
   * @returns {object} The created session
   */
  create(options = {}) {
    const sessionId = crypto.randomUUID();
    const now = Date.now();

    const session = {
      id: sessionId,
      token: options.token || null,
      refreshToken: options.refreshToken || null,
      proxy: options.proxy || null,
      metadata: options.metadata || {},
      createdAt: now,
      expiresAt: now + this.sessionTTL,
      lastActivity: now,
      requestCount: 0,
      active: true,
    };

    // Evict oldest session if at capacity
    if (this.sessions.size >= this.maxSessions) {
      this._evictOldest();
    }

    this.sessions.set(sessionId, session);
    this.activeSessionId = sessionId;

    this.logger.info(`Session created: ${sessionId.slice(0, 8)}...`);
    this._persist(session);

    return { ...session };
  }

  /**
   * Get the currently active session.
   * @returns {object|null}
   */
  getActive() {
    if (!this.activeSessionId) return null;

    const session = this.sessions.get(this.activeSessionId);
    if (!session) return null;

    // Check expiration
    if (Date.now() > session.expiresAt) {
      this.logger.warn(`Active session ${session.id.slice(0, 8)}... expired`);
      session.active = false;
      this.activeSessionId = null;
      return null;
    }

    return { ...session };
  }

  /**
   * Rotate to a new session, deactivating the current one.
   * @param {object} options - Options for the new session
   * @returns {object} The new active session
   */
  rotate(options = {}) {
    const current = this.getActive();
    if (current) {
      const session = this.sessions.get(current.id);
      if (session) {
        session.active = false;
        this.logger.info(`Session ${current.id.slice(0, 8)}... deactivated for rotation`);
      }
    }

    return this.create(options);
  }

  /**
   * Refresh the authentication token for the active session.
   * Simulates token refresh by generating a new token.
   * @returns {object|null} Updated session or null
   */
  refreshToken() {
    const session = this.activeSessionId
      ? this.sessions.get(this.activeSessionId)
      : null;

    if (!session) {
      this.logger.warn("No active session to refresh token for");
      return null;
    }

    // Simulate token refresh
    const newToken = `tok_${crypto.randomBytes(16).toString("hex")}`;
    session.token = newToken;
    session.expiresAt = Date.now() + this.sessionTTL;
    session.lastActivity = Date.now();

    this.logger.info(`Token refreshed for session ${session.id.slice(0, 8)}...`);
    this._persist(session);

    return { ...session };
  }

  /**
   * Record activity on the active session.
   */
  recordActivity() {
    const session = this.activeSessionId
      ? this.sessions.get(this.activeSessionId)
      : null;

    if (session) {
      session.lastActivity = Date.now();
      session.requestCount++;
    }
  }

  /**
   * Destroy a session by ID.
   * @param {string} sessionId
   * @returns {boolean}
   */
  destroy(sessionId) {
    const session = this.sessions.get(sessionId);
    if (!session) return false;

    session.active = false;
    this.sessions.delete(sessionId);

    if (this.activeSessionId === sessionId) {
      this.activeSessionId = null;
    }

    this._removePersisted(sessionId);
    this.logger.info(`Session ${sessionId.slice(0, 8)}... destroyed`);
    return true;
  }

  /**
   * Destroy all sessions.
   */
  destroyAll() {
    const count = this.sessions.size;
    for (const [id] of this.sessions) {
      this._removePersisted(id);
    }
    this.sessions.clear();
    this.activeSessionId = null;
    this.logger.info(`Destroyed ${count} sessions`);
  }

  /**
   * Get a list of all sessions.
   */
  list() {
    const now = Date.now();
    return Array.from(this.sessions.values()).map((s) => ({
      id: s.id,
      active: s.active && s.id === this.activeSessionId,
      expired: now > s.expiresAt,
      requestCount: s.requestCount,
      createdAt: new Date(s.createdAt).toISOString(),
      expiresAt: new Date(s.expiresAt).toISOString(),
      hasProxy: !!s.proxy,
    }));
  }

  /**
   * Get session statistics.
   */
  getStats() {
    const sessions = Array.from(this.sessions.values());
    const now = Date.now();
    return {
      total: sessions.length,
      active: sessions.filter((s) => s.active && now <= s.expiresAt).length,
      expired: sessions.filter((s) => now > s.expiresAt).length,
      totalRequests: sessions.reduce((sum, s) => sum + s.requestCount, 0),
      maxSessions: this.maxSessions,
    };
  }

  /**
   * Persist session to file system.
   */
  _persist(session) {
    try {
      if (!fs.existsSync(this.sessionDir)) {
        fs.mkdirSync(this.sessionDir, { recursive: true });
      }
      const filePath = path.join(this.sessionDir, `${session.id}.json`);
      const data = { ...session };
      // Don't persist actual tokens to disk in plaintext for security
      data.token = data.token ? "[REDACTED]" : null;
      data.refreshToken = data.refreshToken ? "[REDACTED]" : null;
      fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
    } catch (err) {
      this.logger.error(`Failed to persist session: ${err.message}`);
    }
  }

  /**
   * Remove persisted session file.
   */
  _removePersisted(sessionId) {
    try {
      const filePath = path.join(this.sessionDir, `${sessionId}.json`);
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
      }
    } catch (err) {
      this.logger.error(`Failed to remove persisted session: ${err.message}`);
    }
  }

  /**
   * Evict the oldest session when at capacity.
   */
  _evictOldest() {
    let oldest = null;
    for (const [, session] of this.sessions) {
      if (!oldest || session.createdAt < oldest.createdAt) {
        oldest = session;
      }
    }
    if (oldest) {
      this.destroy(oldest.id);
      this.logger.info(`Evicted oldest session ${oldest.id.slice(0, 8)}...`);
    }
  }
}

module.exports = { SessionManager };
