/**
 * SonarQube Analyzer - Main Entry Point
 * OpenClaw skill for automated code quality analysis
 */

const api = require('./api');
const rules = require('./rules');
const analyzer = require('./analyzer');
const reporter = require('./reporter');

// Export all modules
module.exports = {
  // API client
  ...api,
  
  // Rule definitions
  ...rules,
  
  // Analysis engine
  ...analyzer,
  
  // Report generators
  ...reporter
};