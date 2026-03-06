'use strict';

const fs = require('fs');
const path = require('path');

class ResourceEstimator {
  constructor() {
    const heuristicsPath = path.join(__dirname, '..', 'references', 'resource-heuristics.json');
    this.heuristics = JSON.parse(fs.readFileSync(heuristicsPath, 'utf-8'));
  }

  /**
   * Estimate Kubernetes resource requests and limits for a parsed Docker config.
   *
   * @param {object} config - Parsed Dockerfile or Compose service config
   * @param {object} [overrides] - Optional manual overrides
   * @returns {object} { requests: {cpu, memory}, limits: {cpu, memory} }
   */
  estimate(config, overrides = {}) {
    const appType = config.appType || 'generic';
    const profile = this.heuristics[appType] || this.heuristics.generic;

    // Check if deploy resources are already specified (from compose)
    if (config.deploy && config.deploy.resources) {
      return this._fromDeployResources(config.deploy.resources, profile);
    }

    const resources = {
      requests: {
        cpu: profile.requests.cpu,
        memory: profile.requests.memory,
      },
      limits: {
        cpu: profile.limits.cpu,
        memory: profile.limits.memory,
      },
    };

    // Adjust based on signals
    this._adjustForPorts(config, resources);
    this._adjustForVolumes(config, resources);

    // Apply overrides
    if (overrides.requests) Object.assign(resources.requests, overrides.requests);
    if (overrides.limits) Object.assign(resources.limits, overrides.limits);

    return resources;
  }

  _fromDeployResources(deployRes, profile) {
    const resources = {
      requests: {
        cpu: profile.requests.cpu,
        memory: profile.requests.memory,
      },
      limits: {
        cpu: profile.limits.cpu,
        memory: profile.limits.memory,
      },
    };

    if (deployRes.limits) {
      if (deployRes.limits.cpus) resources.limits.cpu = this._cpuToK8s(deployRes.limits.cpus);
      if (deployRes.limits.memory) resources.limits.memory = this._memToK8s(deployRes.limits.memory);
    }
    if (deployRes.requests) {
      if (deployRes.requests.cpus) resources.requests.cpu = this._cpuToK8s(deployRes.requests.cpus);
      if (deployRes.requests.memory) resources.requests.memory = this._memToK8s(deployRes.requests.memory);
    }

    return resources;
  }

  /**
   * Convert Docker CPU format (e.g. "0.5") to Kubernetes format (e.g. "500m")
   */
  _cpuToK8s(cpuStr) {
    const num = parseFloat(cpuStr);
    if (isNaN(num)) return '100m';
    if (num < 1) return `${Math.round(num * 1000)}m`;
    return `${num}`;
  }

  /**
   * Convert Docker memory format (e.g. "512M") to Kubernetes format (e.g. "512Mi")
   */
  _memToK8s(memStr) {
    const str = String(memStr).trim();
    const match = str.match(/^(\d+(?:\.\d+)?)\s*([kmgtKMGT])?[bB]?$/);
    if (!match) return str.endsWith('i') ? str : str + 'i';

    const num = parseFloat(match[1]);
    const unit = (match[2] || '').toUpperCase();

    const unitMap = { K: 'Ki', M: 'Mi', G: 'Gi', T: 'Ti' };
    return `${Math.round(num)}${unitMap[unit] || 'Mi'}`;
  }

  /**
   * Increase resources if many ports are exposed (likely receives more traffic).
   */
  _adjustForPorts(config, resources) {
    const ports = config.exposedPorts || [];
    if (ports.length > 2) {
      resources.limits.cpu = this._scaleCpu(resources.limits.cpu, 1.5);
      resources.limits.memory = this._scaleMemory(resources.limits.memory, 1.3);
    }
  }

  /**
   * Increase memory if volumes are used (may do more I/O buffering).
   */
  _adjustForVolumes(config, resources) {
    const volumes = config.volumes || [];
    if (volumes.length > 0) {
      resources.limits.memory = this._scaleMemory(resources.limits.memory, 1.2);
    }
  }

  _scaleCpu(cpuStr, factor) {
    const match = cpuStr.match(/^(\d+)(m?)$/);
    if (!match) return cpuStr;
    const val = parseInt(match[1], 10);
    const suffix = match[2];
    return `${Math.round(val * factor)}${suffix}`;
  }

  _scaleMemory(memStr, factor) {
    const match = memStr.match(/^(\d+)(\w+)$/);
    if (!match) return memStr;
    const val = parseInt(match[1], 10);
    const suffix = match[2];
    return `${Math.round(val * factor)}${suffix}`;
  }
}

module.exports = { ResourceEstimator };
