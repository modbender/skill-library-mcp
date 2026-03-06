'use strict';

const Ajv = require('ajv');
const fs = require('fs');
const path = require('path');

class ManifestValidator {
  constructor() {
    this.ajv = new Ajv({ allErrors: true, strict: false });
    this._loadSchemas();
  }

  _loadSchemas() {
    const schemasDir = path.join(__dirname, '..', 'assets', 'schemas');
    this.schemas = {};

    const schemaFiles = fs.readdirSync(schemasDir).filter(f => f.endsWith('.json'));
    for (const file of schemaFiles) {
      const name = path.basename(file, '.json');
      const schema = JSON.parse(fs.readFileSync(path.join(schemasDir, file), 'utf-8'));
      this.schemas[name] = this.ajv.compile(schema);
    }
  }

  /**
   * Validate a Kubernetes manifest object.
   *
   * @param {object} manifest - The K8s manifest object
   * @returns {object} { valid: boolean, errors: string[] }
   */
  validate(manifest) {
    const errors = [];

    // Basic structural checks
    if (!manifest.apiVersion) errors.push('Missing apiVersion');
    if (!manifest.kind) errors.push('Missing kind');
    if (!manifest.metadata) errors.push('Missing metadata');
    if (manifest.metadata && !manifest.metadata.name) errors.push('Missing metadata.name');

    // Kind-specific validation
    const kind = (manifest.kind || '').toLowerCase();
    const schemaKey = `${kind}-schema`;

    if (this.schemas[schemaKey]) {
      const validate = this.schemas[schemaKey];
      const valid = validate(manifest);
      if (!valid && validate.errors) {
        for (const err of validate.errors) {
          errors.push(`${err.instancePath || '/'}: ${err.message}`);
        }
      }
    }

    // Best-practice checks
    errors.push(...this._checkBestPractices(manifest));

    return { valid: errors.length === 0, errors };
  }

  /**
   * Validate an array of manifests.
   */
  validateAll(manifests) {
    const results = [];
    for (const manifest of manifests) {
      results.push({
        kind: manifest.kind,
        name: manifest.metadata?.name,
        ...this.validate(manifest),
      });
    }

    const allValid = results.every(r => r.valid);
    return { valid: allValid, results };
  }

  _checkBestPractices(manifest) {
    const warnings = [];
    const kind = manifest.kind;

    if (kind === 'Deployment') {
      const spec = manifest.spec || {};
      const template = spec.template || {};
      const podSpec = template.spec || {};
      const containers = podSpec.containers || [];

      for (const container of containers) {
        if (!container.resources) {
          warnings.push(`Container "${container.name}": missing resource limits (best practice)`);
        }
        if (!container.livenessProbe) {
          warnings.push(`Container "${container.name}": missing livenessProbe (best practice)`);
        }
        if (!container.readinessProbe) {
          warnings.push(`Container "${container.name}": missing readinessProbe (best practice)`);
        }
        if (container.image && container.image.endsWith(':latest')) {
          warnings.push(`Container "${container.name}": using :latest tag (not recommended for production)`);
        }
        if (!container.securityContext) {
          warnings.push(`Container "${container.name}": missing securityContext (best practice)`);
        }
      }

      if (!spec.replicas || spec.replicas < 2) {
        warnings.push('Deployment has fewer than 2 replicas (consider HA)');
      }
    }

    return warnings;
  }
}

module.exports = { ManifestValidator };
