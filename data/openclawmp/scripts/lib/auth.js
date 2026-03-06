// ============================================================================
// auth.js — Authentication / token management
// ============================================================================

'use strict';

const config = require('./config.js');

/**
 * Check if the user is authenticated
 */
function isAuthenticated() {
  return config.getAuthToken() !== null;
}

/**
 * Get the current device ID
 */
function getDeviceId() {
  return config.getDeviceId();
}

/**
 * Get auth token
 */
function getToken() {
  return config.getAuthToken();
}

/**
 * Save auth token
 */
function saveToken(token, extra = {}) {
  config.saveAuthToken(token, extra);
}

module.exports = {
  isAuthenticated,
  getDeviceId,
  getToken,
  saveToken,
};
