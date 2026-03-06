#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const CONFIG_DIR = path.join(process.cwd(), '.trae', 'config');
const DATA_DIR = path.join(process.cwd(), '.trae', 'data');
const SKILL_DIR = path.join(process.cwd(), '.trae', 'skills', 'teamwork');

const PROVIDERS_FILE = path.join(CONFIG_DIR, 'providers.json');
const ROLES_FILE = path.join(CONFIG_DIR, 'team-roles.json');
const SCORES_FILE = path.join(DATA_DIR, 'model_scores.json');

function ensureDirectories() {
  [CONFIG_DIR, DATA_DIR, SKILL_DIR].forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
}

function fileExists(filePath) {
  return fs.existsSync(filePath);
}

function readJSON(filePath) {
  if (!fileExists(filePath)) return null;
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (e) {
    return null;
  }
}

function writeJSON(filePath, data) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
}

function checkConfiguration() {
  const results = {
    providersExists: fileExists(PROVIDERS_FILE),
    rolesExists: fileExists(ROLES_FILE),
    scoresExists: fileExists(SCORES_FILE),
    hasProviders: false,
    hasModels: false,
    hasHostModel: false,
    isValid: false
  };

  if (results.providersExists) {
    const providers = readJSON(PROVIDERS_FILE);
    results.hasProviders = providers && providers.providers && providers.providers.length > 0;
    results.hasModels = results.hasProviders && providers.providers.some(p => p.models && p.models.length > 0);
    results.hasHostModel = providers && providers.host_model && providers.host_model.model;
  }

  results.isValid = results.providersExists && results.rolesExists && results.scoresExists && 
                    results.hasProviders && results.hasModels && results.hasHostModel;

  return results;
}

function initializeDefaultRoles() {
  const defaultRoles = {
    "$schema": "./schemas/team-roles.schema.json",
    "version": "1.0.0",
    "last_updated": new Date().toISOString(),
    "roles": {
      "project_manager": {
        "description": "Coordinates team activities and manages timeline",
        "required_capabilities": ["planning", "coordination", "communication"],
        "preferred_model_traits": {
          "reliability": "high",
          "thinking_depth": "medium",
          "response_speed": "medium"
        },
        "typical_workload": "medium"
      },
      "architect": {
        "description": "Designs system architecture and technical approach",
        "required_capabilities": ["system-design", "architecture", "patterns"],
        "preferred_model_traits": {
          "thinking_depth": "high",
          "creativity": "high",
          "context_understanding": "high"
        },
        "typical_workload": "high"
      },
      "developer": {
        "description": "Implements code following specifications",
        "required_capabilities": ["coding", "debugging", "refactoring"],
        "preferred_model_traits": {
          "code_quality": "high",
          "response_speed": "medium",
          "reliability": "high"
        },
        "typical_workload": "high"
      },
      "tester": {
        "description": "Creates and executes test suites",
        "required_capabilities": ["testing", "qa", "validation"],
        "preferred_model_traits": {
          "thinking_depth": "medium",
          "response_speed": "high",
          "reliability": "high"
        },
        "typical_workload": "medium"
      },
      "reviewer": {
        "description": "Performs code reviews and quality checks",
        "required_capabilities": ["code-review", "best-practices", "security"],
        "preferred_model_traits": {
          "thinking_depth": "high",
          "code_quality": "high",
          "reliability": "high"
        },
        "typical_workload": "medium"
      },
      "analyst": {
        "description": "Analyzes requirements and breaks down tasks",
        "required_capabilities": ["analysis", "communication", "documentation"],
        "preferred_model_traits": {
          "thinking_depth": "high",
          "context_understanding": "high",
          "creativity": "medium"
        },
        "typical_workload": "medium"
      },
      "herald": {
        "description": "Central communication hub for team coordination",
        "required_capabilities": ["communication", "coordination", "monitoring"],
        "preferred_model_traits": {
          "response_speed": "high",
          "reliability": "high",
          "response_frequency": "high"
        },
        "typical_workload": "medium"
      }
    }
  };

  writeJSON(ROLES_FILE, defaultRoles);
  return defaultRoles;
}

function initializeEmptyScores() {
  const scores = {
    "$schema": "./schemas/model-scores.schema.json",
    "version": "1.0.0",
    "last_updated": new Date().toISOString(),
    "evaluation_interval_seconds": 3600,
    "score_decay_factor": 0.95,
    "dimensions": [
      "response_speed",
      "response_frequency",
      "thinking_depth",
      "multi_threading",
      "code_quality",
      "creativity",
      "reliability",
      "context_understanding"
    ],
    "dimension_weights": {
      "response_speed": 0.125,
      "response_frequency": 0.125,
      "thinking_depth": 0.15,
      "multi_threading": 0.1,
      "code_quality": 0.15,
      "creativity": 0.1,
      "reliability": 0.15,
      "context_understanding": 0.1
    },
    "scores": {}
  };

  writeJSON(SCORES_FILE, scores);
  return scores;
}

function initializeEmptyProviders() {
  const providers = {
    "$schema": "./schemas/providers.schema.json",
    "version": "1.0.0",
    "last_updated": new Date().toISOString(),
    "providers": [],
    "host_model": {
      "provider": "",
      "model": ""
    },
    "budget": {
      "max_monthly_cost": 0,
      "currency": "USD",
      "alert_threshold": 0.8,
      "current_month_spent": 0
    }
  };

  writeJSON(PROVIDERS_FILE, providers);
  return providers;
}

function needsInitialization() {
  const check = checkConfiguration();
  return !check.isValid;
}

module.exports = {
  ensureDirectories,
  checkConfiguration,
  initializeDefaultRoles,
  initializeEmptyScores,
  initializeEmptyProviders,
  needsInitialization,
  fileExists,
  readJSON,
  writeJSON,
  PROVIDERS_FILE,
  ROLES_FILE,
  SCORES_FILE
};
