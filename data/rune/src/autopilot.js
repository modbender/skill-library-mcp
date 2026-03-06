/**
 * autopilot.js - Project Autopilot for autonomous work management
 * Phase 6: Project state tracking, task management, blocker detection
 */

import { openDb } from './db.js';

const PROJECT_PHASES = [
  'planning',     // Initial design, requirements  
  'building',     // Active development
  'testing',      // QA, debugging, refinement
  'deploying',    // Production deployment
  'complete',     // Finished, maintenance only
  'paused',       // On hold
  'cancelled'     // Abandoned
];

const TASK_PRIORITIES = {
  CRITICAL: 'critical',    // Blocking other work
  HIGH: 'high',           // Important, time-sensitive  
  MEDIUM: 'medium',       // Normal priority
  LOW: 'low',            // Nice to have
  BACKLOG: 'backlog'     // Future consideration
};

/**
 * Initialize project state tables
 */
function initProjectTables(db) {
  db.exec(`
    CREATE TABLE IF NOT EXISTS project_states (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE,
      phase TEXT NOT NULL DEFAULT 'planning',
      active_task TEXT,
      next_steps TEXT,
      priority TEXT DEFAULT 'medium',
      health_score REAL DEFAULT 0.5,
      last_activity TEXT,
      created TEXT NOT NULL,
      updated TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_project_name ON project_states(name);
    CREATE INDEX IF NOT EXISTS idx_project_phase ON project_states(phase);
    CREATE INDEX IF NOT EXISTS idx_project_updated ON project_states(updated);
    
    CREATE TABLE IF NOT EXISTS project_blockers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      project_name TEXT NOT NULL,
      description TEXT NOT NULL,
      severity TEXT DEFAULT 'medium',
      created TEXT NOT NULL,
      resolved TEXT,
      FOREIGN KEY (project_name) REFERENCES project_states(name) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_blocker_project ON project_blockers(project_name);
    CREATE INDEX IF NOT EXISTS idx_blocker_resolved ON project_blockers(resolved);
    
    CREATE TABLE IF NOT EXISTS project_tasks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      project_name TEXT NOT NULL,
      description TEXT NOT NULL,
      status TEXT DEFAULT 'todo',
      priority TEXT DEFAULT 'medium',
      assigned_to TEXT,
      estimated_hours REAL,
      actual_hours REAL,
      created TEXT NOT NULL,
      completed TEXT,
      FOREIGN KEY (project_name) REFERENCES project_states(name) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_task_project ON project_tasks(project_name);
    CREATE INDEX IF NOT EXISTS idx_task_status ON project_tasks(status);
  `);
}

/**
 * Get current state of a project (T-034)
 */
function getProjectState(projectName) {
  const db = openDb();
  
  try {
    initProjectTables(db);
    
    // Get or create project state
    let project = db.prepare('SELECT * FROM project_states WHERE name = ?').get(projectName);
    
    if (!project) {
      // Auto-create project from existing facts
      const now = new Date().toISOString();
      db.prepare(`
        INSERT INTO project_states (name, phase, created, updated) 
        VALUES (?, 'planning', ?, ?)
      `).run(projectName, now, now);
      
      project = db.prepare('SELECT * FROM project_states WHERE name = ?').get(projectName);
    }
    
    // Get active blockers
    const blockers = db.prepare(`
      SELECT * FROM project_blockers 
      WHERE project_name = ? AND resolved IS NULL
      ORDER BY created DESC
    `).all(projectName);
    
    // Get active tasks
    const tasks = db.prepare(`
      SELECT * FROM project_tasks 
      WHERE project_name = ? AND status != 'complete'
      ORDER BY priority DESC, created ASC
    `).all(projectName);
    
    return {
      ...project,
      blockers,
      tasks,
      health_score: calculateProjectHealth(project, blockers, tasks)
    };
    
  } finally {
    db.close();
  }
}

/**
 * Update project state (T-035)
 */
function updateProjectState(projectName, updates) {
  const db = openDb();
  
  try {
    initProjectTables(db);
    
    const now = new Date().toISOString();
    
    // Ensure project exists
    const existing = db.prepare('SELECT id FROM project_states WHERE name = ?').get(projectName);
    if (!existing) {
      db.prepare(`
        INSERT INTO project_states (name, phase, created, updated)
        VALUES (?, 'planning', ?, ?)
      `).run(projectName, now, now);
    }
    
    // Handle special operations
    if (updates.add_blocker) {
      db.prepare(`
        INSERT INTO project_blockers (project_name, description, created)
        VALUES (?, ?, ?)
      `).run(projectName, updates.add_blocker, now);
    }
    
    if (updates.resolve_blocker) {
      db.prepare(`
        UPDATE project_blockers 
        SET resolved = ? 
        WHERE id = ? AND project_name = ?
      `).run(now, updates.resolve_blocker, projectName);
    }
    
    if (updates.add_task) {
      db.prepare(`
        INSERT INTO project_tasks (project_name, description, priority, created)
        VALUES (?, ?, ?, ?)
      `).run(projectName, updates.add_task, updates.task_priority || 'medium', now);
    }
    
    // Update standard fields
    const fields = [];
    const values = [];
    
    if (updates.phase && PROJECT_PHASES.includes(updates.phase)) {
      fields.push('phase = ?');
      values.push(updates.phase);
    }
    
    if (updates.active_task !== undefined) {
      fields.push('active_task = ?');
      values.push(updates.active_task);
    }
    
    if (updates.next_steps !== undefined) {
      fields.push('next_steps = ?');
      values.push(updates.next_steps);
    }
    
    if (updates.priority && Object.values(TASK_PRIORITIES).includes(updates.priority)) {
      fields.push('priority = ?');
      values.push(updates.priority);
    }
    
    if (fields.length > 0) {
      fields.push('updated = ?', 'last_activity = ?');
      values.push(now, now);
      values.push(projectName);
      
      const sql = `UPDATE project_states SET ${fields.join(', ')} WHERE name = ?`;
      db.prepare(sql).run(...values);
    }
    
    // Log the update
    db.prepare(`
      INSERT INTO performance_log (event_type, category, detail, created)
      VALUES ('project-update', 'autopilot', ?, ?)
    `).run(`Updated ${projectName}: ${Object.keys(updates).join(', ')}`, now);
    
  } finally {
    db.close();
  }
}

/**
 * List all projects with summary (T-034)
 */
function listAllProjects() {
  const db = openDb();
  
  try {
    initProjectTables(db);
    
    const projects = db.prepare(`
      SELECT 
        p.*,
        COUNT(b.id) as blockers,
        COUNT(t.id) as active_tasks
      FROM project_states p
      LEFT JOIN project_blockers b ON p.name = b.project_name AND b.resolved IS NULL
      LEFT JOIN project_tasks t ON p.name = t.project_name AND t.status != 'complete'
      GROUP BY p.id
      ORDER BY p.updated DESC
    `).all();
    
    return projects.map(project => ({
      ...project,
      health_score: calculateProjectHealth(project, [], [])
    }));
    
  } finally {
    db.close();
  }
}

/**
 * Calculate project health score (0.0 - 1.0)
 */
function calculateProjectHealth(project, blockers, tasks) {
  let score = 0.5; // Baseline
  
  // Phase scoring
  const phaseScores = {
    'planning': 0.3,
    'building': 0.7,
    'testing': 0.8,
    'deploying': 0.9,
    'complete': 1.0,
    'paused': 0.2,
    'cancelled': 0.0
  };
  score = phaseScores[project.phase] || 0.5;
  
  // Blocker penalty
  const blockerCount = blockers?.length || 0;
  score -= Math.min(0.4, blockerCount * 0.1);
  
  // Activity bonus/penalty
  if (project.last_activity) {
    const daysSinceActivity = (Date.now() - new Date(project.last_activity).getTime()) / (1000 * 60 * 60 * 24);
    if (daysSinceActivity > 7) {
      score -= Math.min(0.3, (daysSinceActivity - 7) * 0.02); // Stale project penalty
    } else if (daysSinceActivity < 1) {
      score += 0.1; // Active project bonus
    }
  }
  
  // Task completion ratio
  const activeTasks = tasks?.filter(t => t.status !== 'complete') || [];
  const completedTasks = tasks?.filter(t => t.status === 'complete') || [];
  if (completedTasks.length + activeTasks.length > 0) {
    const completionRate = completedTasks.length / (completedTasks.length + activeTasks.length);
    score += (completionRate - 0.5) * 0.2; // Boost for >50% completion
  }
  
  return Math.max(0, Math.min(1, score));
}

/**
 * Smart task picker for autopilot (T-036)
 */
function getNextTask(options = {}) {
  const db = openDb();
  
  try {
    initProjectTables(db);
    
    // Find projects that need attention (unblocked projects only)
    const candidates = db.prepare(`
      SELECT p.*
      FROM project_states p
      WHERE p.phase NOT IN ('complete', 'paused', 'cancelled')
        AND (p.active_task IS NOT NULL OR p.next_steps IS NOT NULL)
        AND NOT EXISTS (
          SELECT 1 FROM project_blockers b 
          WHERE b.project_name = p.name AND b.resolved IS NULL
        )
      ORDER BY 
        CASE p.priority 
          WHEN 'critical' THEN 4
          WHEN 'high' THEN 3  
          WHEN 'medium' THEN 2
          WHEN 'low' THEN 1
          ELSE 2
        END DESC,
        p.last_activity ASC
      LIMIT 5
    `).all();
    
    if (candidates.length === 0) {
      return null;
    }
    
    // Score candidates
    const scored = candidates.map(project => ({
      ...project,
      score: scoreTaskUrgency(project)
    }));
    
    // Return highest scoring unblocked project
    return scored.sort((a, b) => b.score - a.score)[0];
    
  } finally {
    db.close();
  }
}

/**
 * Score task urgency for autopilot selection
 */
function scoreTaskUrgency(project) {
  let score = 0;
  
  // Priority weight
  const priorityWeights = { critical: 10, high: 7, medium: 5, low: 3, backlog: 1 };
  score += priorityWeights[project.priority] || 5;
  
  // Staleness penalty (encourages working on neglected projects)
  if (project.last_activity) {
    const daysSinceActivity = (Date.now() - new Date(project.last_activity).getTime()) / (1000 * 60 * 60 * 24);
    score += Math.min(5, daysSinceActivity * 0.5);
  }
  
  // Phase urgency
  const phaseUrgency = { building: 3, testing: 4, deploying: 5 };
  score += phaseUrgency[project.phase] || 0;
  
  return score;
}

/**
 * Detect if project is blocked too long (T-037)
 */
function detectStuckProjects(hours = 48) {
  const db = openDb();
  
  try {
    initProjectTables(db);
    
    const cutoffTime = new Date(Date.now() - hours * 60 * 60 * 1000).toISOString();
    
    const stuckProjects = db.prepare(`
      SELECT 
        p.*,
        COUNT(b.id) as blocker_count,
        MIN(b.created) as oldest_blocker
      FROM project_states p
      JOIN project_blockers b ON p.name = b.project_name AND b.resolved IS NULL
      WHERE b.created < ?
        AND p.phase NOT IN ('complete', 'paused', 'cancelled')
      GROUP BY p.id
      HAVING blocker_count > 0
      ORDER BY oldest_blocker ASC
    `).all(cutoffTime);
    
    return stuckProjects;
    
  } finally {
    db.close();
  }
}

export {
  getProjectState,
  updateProjectState,
  listAllProjects,
  getNextTask,
  detectStuckProjects,
  calculateProjectHealth,
  PROJECT_PHASES,
  TASK_PRIORITIES
};