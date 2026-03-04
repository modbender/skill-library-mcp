/**
 * Janitor Configuration Examples
 *
 * Copy and modify this file to customize session management behavior
 */

// ============================================================
// EXAMPLE 1: Default Configuration (Balanced)
// ============================================================
const defaultConfig = {
  enabled: true,
  unusedFileAgeDays: 7,

  sessionManagement: {
    enabled: true,

    monitoring: {
      intervalMinutes: 5,       // Check every 5 minutes
      alertThreshold: 80,        // Alert at 80% of 200k tokens
      emergencyThreshold: 95     // Emergency cleanup at 95%
    },

    pruning: {
      maxSessionAge: 7,          // Delete sessions older than 7 days
      maxContextTokens: 160000,  // Maximum tokens before cleanup
      keepRecentHours: 24,       // Always keep last 24 hours
      keepMinimumSessions: 5     // Never go below 5 sessions
    },

    archiving: {
      enabled: true,
      retentionDays: 30,         // Keep archives for 30 days
      compression: true          // Use gzip compression
    },

    preservation: {
      pinned: true,              // Preserve pinned sessions
      highEngagement: true,      // Keep sessions with many messages
      minMessagesForImportant: 10 // Min messages to be "important"
    }
  }
};

// ============================================================
// EXAMPLE 2: Raspberry Pi / Low Resource (Aggressive)
// ============================================================
const raspberryPiConfig = {
  enabled: true,
  unusedFileAgeDays: 3,

  sessionManagement: {
    enabled: true,

    monitoring: {
      intervalMinutes: 5,
      alertThreshold: 70,        // More aggressive - alert earlier
      emergencyThreshold: 85     // Emergency at 85% instead of 95%
    },

    pruning: {
      maxSessionAge: 3,          // Delete after 3 days instead of 7
      maxContextTokens: 140000,  // Lower threshold
      keepRecentHours: 12,       // Only keep 12 hours instead of 24
      keepMinimumSessions: 3
    },

    archiving: {
      enabled: true,
      retentionDays: 14,         // Shorter retention
      compression: true
    },

    preservation: {
      pinned: false,             // Don't preserve pinned (save space)
      highEngagement: true,
      minMessagesForImportant: 15 // Higher bar for "important"
    }
  }
};

// ============================================================
// EXAMPLE 3: Desktop / High Resource (Conservative)
// ============================================================
const desktopConfig = {
  enabled: true,
  unusedFileAgeDays: 14,

  sessionManagement: {
    enabled: true,

    monitoring: {
      intervalMinutes: 15,       // Less frequent checks
      alertThreshold: 85,        // More lenient
      emergencyThreshold: 95
    },

    pruning: {
      maxSessionAge: 14,         // Keep sessions longer
      maxContextTokens: 180000,  // Higher threshold
      keepRecentHours: 48,       // Keep 2 days
      keepMinimumSessions: 10
    },

    archiving: {
      enabled: true,
      retentionDays: 90,         // Long retention
      compression: true
    },

    preservation: {
      pinned: true,
      highEngagement: true,
      minMessagesForImportant: 5  // Lower bar - preserve more
    }
  }
};

// ============================================================
// EXAMPLE 4: Manual Control Only (No Auto-Cleanup)
// ============================================================
const manualConfig = {
  enabled: true,
  unusedFileAgeDays: 7,

  sessionManagement: {
    enabled: true,

    monitoring: {
      intervalMinutes: 10,
      alertThreshold: 90,        // Only alert when very high
      emergencyThreshold: 98     // Almost never auto-cleanup
    },

    pruning: {
      maxSessionAge: 30,         // Very long retention
      maxContextTokens: 190000,  // Almost never hit
      keepRecentHours: 72,       // Keep 3 days
      keepMinimumSessions: 20
    },

    archiving: {
      enabled: true,
      retentionDays: 365,        // Keep archives 1 year
      compression: true
    },

    preservation: {
      pinned: true,
      highEngagement: true,
      minMessagesForImportant: 3  // Preserve almost everything
    }
  }
};

// ============================================================
// EXAMPLE 5: Session Management Disabled
// ============================================================
const disabledSessionManagementConfig = {
  enabled: true,
  unusedFileAgeDays: 7,

  sessionManagement: {
    enabled: false  // Disable all session management features
  }
};

// ============================================================
// EXAMPLE 6: Custom Configuration for Testing
// ============================================================
const testingConfig = {
  enabled: true,
  unusedFileAgeDays: 1,

  sessionManagement: {
    enabled: true,

    monitoring: {
      intervalMinutes: 1,        // Check every minute (testing only!)
      alertThreshold: 50,        // Low threshold for testing
      emergencyThreshold: 60
    },

    pruning: {
      maxSessionAge: 1,          // Delete after 1 day
      maxContextTokens: 100000,
      keepRecentHours: 1,
      keepMinimumSessions: 2
    },

    archiving: {
      enabled: true,
      retentionDays: 7,
      compression: false         // No compression for faster testing
    },

    preservation: {
      pinned: true,
      highEngagement: true,
      minMessagesForImportant: 20
    }
  }
};

// ============================================================
// USAGE
// ============================================================

// In your code:
const Janitor = require('./janitor');

// Use one of the configs above:
const janitor = new Janitor(raspberryPiConfig);

// Or create your own custom config:
const customConfig = {
  sessionManagement: {
    monitoring: {
      alertThreshold: 75  // Your custom threshold
    }
  }
};

const customJanitor = new Janitor(customConfig);

// Export for use in other files
module.exports = {
  defaultConfig,
  raspberryPiConfig,
  desktopConfig,
  manualConfig,
  disabledSessionManagementConfig,
  testingConfig
};
