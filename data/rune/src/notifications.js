/**
 * notifications.js - Smart notification system with priority classification and intelligent routing
 * Phase 7: Smart Notifications (T-039 through T-043)
 */

import { openDb } from './db.js';
import { scoreFactsForRelevance } from './relevance.js';

const PRIORITY_LEVELS = {
  CRITICAL: 'critical',    // Immediate interrupt - service down, errors, blockers
  HIGH: 'high',           // Soon - urgent tasks, deadlines, important updates  
  MEDIUM: 'medium',       // Normal - progress updates, completions
  LOW: 'low',            // When convenient - minor updates, suggestions
  FYI: 'fyi'             // Digest only - logs, metrics, background info
};

const NOTIFICATION_CATEGORIES = {
  ERROR: 'error',               // System failures, exceptions
  SECURITY: 'security',         // Auth issues, suspicious activity
  DEPLOYMENT: 'deployment',     // Build/deploy status changes
  PROGRESS: 'progress',         // Task/project completions
  REMINDER: 'reminder',         // Scheduled reminders
  DISCOVERY: 'discovery',       // New insights, patterns found
  SOCIAL: 'social',            // Messages from others
  SYSTEM: 'system'             // Internal status, health checks
};

const CHANNELS = {
  DM: 'dm',                    // Direct message - highest priority
  DISCORD: 'discord',          // Discord server - project updates
  EMAIL: 'email',              // Email - daily summaries
  SYSTEM: 'system'             // System notification area
};

/**
 * Initialize notification tables
 */
function initNotificationTables(db) {
  db.exec(`
    CREATE TABLE IF NOT EXISTS notification_queue (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      message TEXT NOT NULL,
      priority TEXT NOT NULL,
      category TEXT NOT NULL,
      channel TEXT NOT NULL,
      context TEXT,
      created TEXT NOT NULL,
      hold_until TEXT,
      sent TEXT,
      attempts INTEGER DEFAULT 0
    );
    CREATE INDEX IF NOT EXISTS idx_notif_priority ON notification_queue(priority);
    CREATE INDEX IF NOT EXISTS idx_notif_sent ON notification_queue(sent);
    CREATE INDEX IF NOT EXISTS idx_notif_hold ON notification_queue(hold_until);
    
    CREATE TABLE IF NOT EXISTS notification_rules (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      pattern TEXT NOT NULL,
      priority_override TEXT,
      channel_override TEXT,
      timing_override TEXT,
      active INTEGER DEFAULT 1,
      created TEXT NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS user_preferences (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT NOT NULL DEFAULT 'default',
      quiet_hours_start TEXT DEFAULT '23:00',
      quiet_hours_end TEXT DEFAULT '07:00',
      work_hours_start TEXT DEFAULT '09:00', 
      work_hours_end TEXT DEFAULT '17:00',
      timezone TEXT DEFAULT 'America/New_York',
      batch_low_priority INTEGER DEFAULT 1,
      digest_frequency TEXT DEFAULT 'daily',
      updated TEXT NOT NULL
    );
  `);
}

/**
 * Classify notification priority and routing (T-039)
 */
async function classifyNotification(message, options = {}) {
  const { context, channel } = options;
  const db = openDb();
  
  try {
    initNotificationTables(db);
    
    const text = message.toLowerCase();
    let priority = PRIORITY_LEVELS.MEDIUM;
    let category = NOTIFICATION_CATEGORIES.SYSTEM;
    let reasoning = 'Default classification';
    
    // Critical indicators
    if (text.match(/\b(critical|emergency|down|failed|error|broken|urgent|asap)\b/)) {
      priority = PRIORITY_LEVELS.CRITICAL;
      category = text.includes('error') || text.includes('failed') ? 
        NOTIFICATION_CATEGORIES.ERROR : NOTIFICATION_CATEGORIES.SYSTEM;
      reasoning = 'Critical keywords detected';
    }
    
    // High priority indicators  
    else if (text.match(/\b(deadline|important|blocker|stuck|needs attention)\b/)) {
      priority = PRIORITY_LEVELS.HIGH;
      reasoning = 'High priority keywords';
    }
    
    // Deployment/build related
    else if (text.match(/\b(deploy|deployment|build|release|production)\b/)) {
      category = NOTIFICATION_CATEGORIES.DEPLOYMENT;
      priority = text.includes('failed') || text.includes('error') ? 
        PRIORITY_LEVELS.HIGH : PRIORITY_LEVELS.MEDIUM;
      reasoning = 'Deployment-related activity';
    }
    
    // Progress updates
    else if (text.match(/\b(completed|finished|done|ready|shipped)\b/)) {
      category = NOTIFICATION_CATEGORIES.PROGRESS;
      priority = PRIORITY_LEVELS.MEDIUM;
      reasoning = 'Progress update';
    }
    
    // Low priority/FYI
    else if (text.match(/\b(metrics|stats|summary|log|info)\b/)) {
      priority = PRIORITY_LEVELS.FYI;
      reasoning = 'Informational content';
    }
    
    // Context-based classification using facts
    try {
      const db = openDb();
      const allFacts = db.prepare('SELECT * FROM facts ORDER BY updated DESC LIMIT 50').all();
      db.close();
      
      if (allFacts.length > 0) {
        const relevantFacts = await scoreFactsForRelevance(message, allFacts, {
          engine: 'ollama',
          limit: 5,
          threshold: 0.6
        });
        
        // If message relates to high-priority projects, bump priority
        const highPriorityProjects = relevantFacts.filter(f => 
          f.category === 'project' && f.relevance_score > 0.8 &&
          (f.key.includes('critical') || f.value.toLowerCase().includes('urgent'))
        );
        
        if (highPriorityProjects.length > 0 && priority === PRIORITY_LEVELS.MEDIUM) {
          priority = PRIORITY_LEVELS.HIGH;
          reasoning += ' + high-priority project context';
        }
      }
    } catch (err) {
      // Context analysis failed, continue with basic classification
      console.warn('Context analysis failed:', err.message);
    }
    
    // Determine timing
    const timing = determineDeliveryTiming(priority, category);
    
    // Suggest channel based on priority and category
    const suggestedChannel = suggestChannel(priority, category);
    
    return {
      priority,
      category,
      urgency: priorityToUrgency(priority),
      sendNow: timing.sendNow,
      holdUntil: timing.holdUntil,
      suggestedChannel,
      reasoning,
      batchable: priority === PRIORITY_LEVELS.LOW || priority === PRIORITY_LEVELS.FYI
    };
    
  } finally {
    db.close();
  }
}

/**
 * Route notification based on classification (T-041)
 */
async function routeNotification(message, classification, options = {}) {
  const { forceSend = false, targetChannel } = options;
  const db = openDb();
  
  try {
    initNotificationTables(db);
    
    const now = new Date().toISOString();
    const channel = targetChannel || classification.suggestedChannel;
    
    // Check if we should send immediately
    const shouldSend = forceSend || classification.sendNow || 
      classification.priority === PRIORITY_LEVELS.CRITICAL;
    
    if (shouldSend) {
      // Actually send the notification (this would integrate with message tool)
      const result = await sendNotification(message, channel, classification);
      
      // Log successful send
      db.prepare(`
        INSERT INTO notification_queue (
          message, priority, category, channel, sent, attempts, created
        ) VALUES (?, ?, ?, ?, ?, 1, ?)
      `).run(message, classification.priority, classification.category, 
             channel, now, now);
      
      return { sent: true, channel, immediate: true };
    } else {
      // Queue for later delivery
      db.prepare(`
        INSERT INTO notification_queue (
          message, priority, category, channel, hold_until, created
        ) VALUES (?, ?, ?, ?, ?, ?)
      `).run(message, classification.priority, classification.category, 
             channel, classification.holdUntil, now);
      
      return { 
        sent: false, 
        queued: true, 
        reason: `Holding until ${classification.holdUntil || 'good timing'}` 
      };
    }
    
  } finally {
    db.close();
  }
}

/**
 * Determine optimal delivery timing (T-040)
 */
function determineDeliveryTiming(priority, category) {
  const now = new Date();
  const hour = now.getHours();
  
  // Critical always sends immediately
  if (priority === PRIORITY_LEVELS.CRITICAL) {
    return { sendNow: true };
  }
  
  // Quiet hours (11 PM - 7 AM) - hold non-critical
  if (hour >= 23 || hour < 7) {
    if (priority === PRIORITY_LEVELS.HIGH) {
      return { sendNow: true }; // High priority overrides quiet hours
    } else {
      return { 
        sendNow: false, 
        holdUntil: getNextGoodTiming() 
      };
    }
  }
  
  // Work hours (9 AM - 5 PM) - send medium+ immediately
  if (hour >= 9 && hour <= 17) {
    if (priority === PRIORITY_LEVELS.MEDIUM || priority === PRIORITY_LEVELS.HIGH) {
      return { sendNow: true };
    }
  }
  
  // Evening (6-10 PM) - batch low priority
  if (hour >= 18 && hour <= 22) {
    if (priority === PRIORITY_LEVELS.HIGH) {
      return { sendNow: true };
    } else if (priority === PRIORITY_LEVELS.MEDIUM) {
      return { sendNow: Math.random() > 0.5 }; // 50% chance - don't spam
    }
  }
  
  // Default: hold for batching
  return { 
    sendNow: false, 
    holdUntil: getNextBatchTime() 
  };
}

/**
 * Suggest best channel for notification type (T-041)
 */
function suggestChannel(priority, category) {
  // Critical/security always goes to DM
  if (priority === PRIORITY_LEVELS.CRITICAL || 
      category === NOTIFICATION_CATEGORIES.SECURITY ||
      category === NOTIFICATION_CATEGORIES.ERROR) {
    return CHANNELS.DM;
  }
  
  // High priority to DM
  if (priority === PRIORITY_LEVELS.HIGH) {
    return CHANNELS.DM;
  }
  
  // Project updates to Discord
  if (category === NOTIFICATION_CATEGORIES.DEPLOYMENT ||
      category === NOTIFICATION_CATEGORIES.PROGRESS) {
    return CHANNELS.DISCORD;
  }
  
  // Low priority to system/batch
  return CHANNELS.SYSTEM;
}

/**
 * Get pending notifications (T-043)
 */
function getPendingNotifications() {
  const db = openDb();
  
  try {
    initNotificationTables(db);
    
    return db.prepare(`
      SELECT * FROM notification_queue 
      WHERE sent IS NULL 
      ORDER BY 
        CASE priority 
          WHEN 'critical' THEN 4
          WHEN 'high' THEN 3
          WHEN 'medium' THEN 2
          WHEN 'low' THEN 1
          ELSE 0
        END DESC,
        created ASC
    `).all();
    
  } finally {
    db.close();
  }
}

/**
 * Send pending notifications that are ready (T-040)
 */
async function sendPendingNotifications(options = {}) {
  const { forceSend = false } = options;
  const db = openDb();
  
  try {
    initNotificationTables(db);
    
    const now = new Date().toISOString();
    const readyNotifications = db.prepare(`
      SELECT * FROM notification_queue 
      WHERE sent IS NULL 
        AND (hold_until IS NULL OR hold_until <= ? OR ?)
      ORDER BY 
        CASE priority 
          WHEN 'critical' THEN 4
          WHEN 'high' THEN 3  
          WHEN 'medium' THEN 2
          WHEN 'low' THEN 1
          ELSE 0
        END DESC
    `).all(now, forceSend);
    
    let sent = 0;
    let held = 0;
    
    for (const notif of readyNotifications) {
      try {
        // Group low-priority notifications into batches
        if (notif.priority === 'low' || notif.priority === 'fyi') {
          // Check if we should batch this
          const batchSize = await getBatchSize(notif.category);
          if (batchSize >= 3 && !forceSend) {
            held++;
            continue;
          }
        }
        
        // Send the notification
        await sendNotification(notif.message, notif.channel, {
          priority: notif.priority,
          category: notif.category
        });
        
        // Mark as sent
        db.prepare(`
          UPDATE notification_queue 
          SET sent = ?, attempts = attempts + 1 
          WHERE id = ?
        `).run(now, notif.id);
        
        sent++;
        
      } catch (err) {
        console.warn(`Failed to send notification ${notif.id}:`, err.message);
        
        // Increment attempts
        db.prepare(`
          UPDATE notification_queue 
          SET attempts = attempts + 1 
          WHERE id = ?
        `).run(notif.id);
      }
    }
    
    return { sent, held };
    
  } finally {
    db.close();
  }
}

/**
 * Actually send notification (placeholder - would integrate with message tool)
 */
async function sendNotification(message, channel, classification) {
  // This would use the message tool in practice
  console.log(`[SEND ${channel.toUpperCase()}] ${classification.priority}: ${message}`);
  
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 100));
  
  return { success: true, channel };
}

/**
 * Helper functions
 */
function priorityToUrgency(priority) {
  const mapping = {
    [PRIORITY_LEVELS.CRITICAL]: 'immediate',
    [PRIORITY_LEVELS.HIGH]: 'soon', 
    [PRIORITY_LEVELS.MEDIUM]: 'normal',
    [PRIORITY_LEVELS.LOW]: 'low',
    [PRIORITY_LEVELS.FYI]: 'none'
  };
  return mapping[priority] || 'normal';
}

function getNextGoodTiming() {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  tomorrow.setHours(9, 0, 0, 0); // 9 AM tomorrow
  return tomorrow.toISOString();
}

function getNextBatchTime() {
  const next = new Date();
  next.setHours(next.getHours() + 2); // 2 hours from now
  return next.toISOString();
}

async function getBatchSize(category) {
  // Count pending notifications in same category
  const db = openDb();
  try {
    const count = db.prepare(`
      SELECT COUNT(*) as count FROM notification_queue 
      WHERE category = ? AND sent IS NULL
    `).get(category);
    return count?.count || 0;
  } finally {
    db.close();
  }
}

/**
 * Generate daily digest of activity (T-042)
 */
async function generateDigest(days = 1, options = {}) {
  const { format = 'markdown', includeMetrics = true } = options;
  const db = openDb();
  
  try {
    initNotificationTables(db);
    
    const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
    const endDate = new Date().toISOString();
    
    // Gather data from multiple sources
    const data = {
      notifications: getDigestNotifications(db, cutoffDate),
      factUpdates: getDigestFacts(db, cutoffDate),
      projectActivity: getDigestProjects(db, cutoffDate),
      performanceEvents: getDigestPerformance(db, cutoffDate)
    };
    
    if (format === 'json') {
      return { content: JSON.stringify(data, null, 2), wordCount: 0 };
    }
    
    // Generate markdown digest
    const sections = [];
    
    sections.push(`# Daily Digest - ${new Date().toDateString()}`);
    sections.push('');
    
    // High-priority items first
    const criticalNotifs = data.notifications.filter(n => n.priority === 'critical' || n.priority === 'high');
    if (criticalNotifs.length > 0) {
      sections.push('## ⚠️ Attention Needed');
      criticalNotifs.forEach(n => {
        sections.push(`- **${n.category}**: ${n.message}`);
      });
      sections.push('');
    }
    
    // Project updates
    if (data.projectActivity.length > 0) {
      sections.push('## 📊 Project Activity');
      data.projectActivity.forEach(p => {
        sections.push(`- **${p.project_name}**: ${p.summary}`);
      });
      sections.push('');
    }
    
    // New facts/insights
    if (data.factUpdates.length > 0) {
      sections.push('## 🧠 Knowledge Updates');
      sections.push(`${data.factUpdates.length} new facts added:`);
      data.factUpdates.slice(0, 5).forEach(f => {
        sections.push(`- ${f.category}/${f.key}: ${f.value.substring(0, 80)}${f.value.length > 80 ? '...' : ''}`);
      });
      if (data.factUpdates.length > 5) {
        sections.push(`- ...and ${data.factUpdates.length - 5} more`);
      }
      sections.push('');
    }
    
    // Performance/mistakes
    const mistakes = data.performanceEvents.filter(e => e.event_type === 'mistake');
    const successes = data.performanceEvents.filter(e => e.event_type === 'success');
    
    if (mistakes.length > 0 || successes.length > 0) {
      sections.push('## 📈 Performance');
      if (successes.length > 0) {
        sections.push(`✅ ${successes.length} success(es)`);
      }
      if (mistakes.length > 0) {
        sections.push(`❌ ${mistakes.length} mistake(s):`);
        mistakes.slice(0, 3).forEach(m => {
          sections.push(`  - ${m.detail}`);
        });
      }
      sections.push('');
    }
    
    // All other notifications
    const otherNotifs = data.notifications.filter(n => n.priority !== 'critical' && n.priority !== 'high');
    if (otherNotifs.length > 0) {
      sections.push('## 📋 Other Updates');
      const grouped = {};
      otherNotifs.forEach(n => {
        if (!grouped[n.category]) grouped[n.category] = [];
        grouped[n.category].push(n.message);
      });
      
      Object.entries(grouped).forEach(([category, messages]) => {
        sections.push(`**${category}**: ${messages.length} update(s)`);
        if (messages.length <= 3) {
          messages.forEach(msg => sections.push(`  - ${msg}`));
        } else {
          messages.slice(0, 2).forEach(msg => sections.push(`  - ${msg}`));
          sections.push(`  - ...and ${messages.length - 2} more`);
        }
      });
      sections.push('');
    }
    
    // Summary stats
    if (includeMetrics) {
      sections.push('## 📊 Summary');
      sections.push(`- **Total Activity**: ${data.notifications.length} notifications, ${data.factUpdates.length} facts, ${data.projectActivity.length} projects`);
      sections.push(`- **Time Period**: Last ${days} day(s)`);
      sections.push(`- **Generated**: ${new Date().toLocaleString()}`);
    }
    
    const content = sections.join('\n');
    const wordCount = content.split(/\s+/).length;
    
    return { content, wordCount, data };
    
  } finally {
    db.close();
  }
}

/**
 * Batch send notifications with grouping (T-043)
 */
async function batchSendNotifications(options = {}) {
  const { category, force = false, maxCount = 10 } = options;
  const db = openDb();
  
  try {
    initNotificationTables(db);
    
    const now = new Date().toISOString();
    let query = `
      SELECT * FROM notification_queue 
      WHERE sent IS NULL 
        AND priority IN ('low', 'fyi')
    `;
    const params = [];
    
    if (category) {
      query += ' AND category = ?';
      params.push(category);
    }
    
    if (!force) {
      query += ' AND (hold_until IS NULL OR hold_until <= ?)';
      params.push(now);
    }
    
    query += ' ORDER BY created ASC LIMIT ?';
    params.push(maxCount);
    
    const notifications = db.prepare(query).all(...params);
    
    if (notifications.length === 0) {
      return { batched: 0, messages: 0, held: 0 };
    }
    
    // Group by category for batching
    const groups = {};
    notifications.forEach(notif => {
      if (!groups[notif.category]) groups[notif.category] = [];
      groups[notif.category].push(notif);
    });
    
    let batchedCount = 0;
    let messageCount = 0;
    
    for (const [cat, notifs] of Object.entries(groups)) {
      // Create batch message
      const batchMessage = createBatchMessage(cat, notifs);
      
      // Send the batch
      await sendNotification(batchMessage, CHANNELS.DISCORD, {
        priority: 'medium',
        category: 'batch'
      });
      
      // Mark notifications as sent
      for (const notif of notifs) {
        db.prepare(`
          UPDATE notification_queue 
          SET sent = ?, attempts = attempts + 1 
          WHERE id = ?
        `).run(now, notif.id);
        batchedCount++;
      }
      
      messageCount++;
    }
    
    // Count remaining notifications
    const remaining = db.prepare(`
      SELECT COUNT(*) as count FROM notification_queue 
      WHERE sent IS NULL
    `).get();
    
    return { 
      batched: batchedCount, 
      messages: messageCount, 
      held: remaining?.count || 0 
    };
    
  } finally {
    db.close();
  }
}

/**
 * Helper functions for digest generation
 */
function getDigestNotifications(db, cutoffDate) {
  return db.prepare(`
    SELECT * FROM notification_queue 
    WHERE created > ? 
    ORDER BY 
      CASE priority 
        WHEN 'critical' THEN 4
        WHEN 'high' THEN 3
        WHEN 'medium' THEN 2  
        WHEN 'low' THEN 1
        ELSE 0
      END DESC, created ASC
  `).all(cutoffDate);
}

function getDigestFacts(db, cutoffDate) {
  return db.prepare(`
    SELECT * FROM facts 
    WHERE updated > ? 
    ORDER BY updated DESC
  `).all(cutoffDate);
}

function getDigestProjects(db, cutoffDate) {
  // Check if project tables exist
  const hasProjects = db.prepare(`
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name='project_states'
  `).get();
  
  if (!hasProjects) return [];
  
  return db.prepare(`
    SELECT 
      name as project_name,
      'Phase ' || phase || ', Task: ' || COALESCE(active_task, 'none') as summary
    FROM project_states 
    WHERE updated > ?
    ORDER BY updated DESC
  `).all(cutoffDate);
}

function getDigestPerformance(db, cutoffDate) {
  return db.prepare(`
    SELECT * FROM performance_log 
    WHERE created > ? 
    ORDER BY created DESC
  `).all(cutoffDate);
}

function createBatchMessage(category, notifications) {
  const count = notifications.length;
  const messages = notifications.map(n => n.message);
  
  if (count === 1) {
    return messages[0];
  }
  
  const header = `📦 **${category} batch** (${count} updates):`;
  const items = messages.slice(0, 5).map(msg => `• ${msg}`);
  
  if (count > 5) {
    items.push(`• ...and ${count - 5} more`);
  }
  
  return [header, '', ...items].join('\n');
}

export {
  classifyNotification,
  routeNotification,
  getPendingNotifications,
  sendPendingNotifications,
  generateDigest,
  batchSendNotifications,
  PRIORITY_LEVELS,
  NOTIFICATION_CATEGORIES,
  CHANNELS
};