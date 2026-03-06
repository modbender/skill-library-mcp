'use strict';

const path = require('path');

const DEFAULT_CONFIG = {
  latency_threshold: 100,
  traffic_threshold: 0.3,
  failure_threshold: 0.1,
  output_format: 'json',
  output_dir: process.cwd(),
  verbose: false,
  timeline_width: 80,
  dot_title: 'Agent Communication Network',
};

function loadConfig(overrides = {}) {
  const config = { ...DEFAULT_CONFIG };

  // Apply overrides
  for (const [key, value] of Object.entries(overrides)) {
    if (value !== undefined && value !== null) {
      config[key] = value;
    }
  }

  return config;
}

function resolveOutputPath(filepath, config) {
  if (path.isAbsolute(filepath)) return filepath;
  return path.join(config.output_dir, filepath);
}

module.exports = { DEFAULT_CONFIG, loadConfig, resolveOutputPath };
