'use strict';

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

class ComposeParser {
  /**
   * Parse a docker-compose.yml string into structured service configurations.
   */
  parse(content) {
    const doc = yaml.load(content);
    if (!doc) throw new Error('Empty or invalid docker-compose file');

    const composeVersion = doc.version || '3';
    const services = doc.services || {};
    const volumes = doc.volumes || {};
    const networks = doc.networks || {};

    const result = {
      version: composeVersion,
      services: [],
      globalVolumes: Object.keys(volumes),
      globalNetworks: Object.keys(networks),
    };

    for (const [serviceName, serviceDef] of Object.entries(services)) {
      result.services.push(this._parseService(serviceName, serviceDef));
    }

    return result;
  }

  /**
   * Parse a docker-compose.yml from a file path.
   */
  parseFile(filePath) {
    const resolvedPath = path.resolve(filePath);
    if (!fs.existsSync(resolvedPath)) {
      throw new Error(`docker-compose file not found: ${resolvedPath}`);
    }
    const content = fs.readFileSync(resolvedPath, 'utf-8');
    return this.parse(content);
  }

  _parseService(name, def) {
    const service = {
      name,
      image: def.image || null,
      build: null,
      ports: [],
      envVars: {},
      volumes: [],
      depends_on: [],
      command: def.command || null,
      entrypoint: def.entrypoint || null,
      healthcheck: null,
      restart: def.restart || 'no',
      networks: [],
      labels: {},
      deploy: null,
      user: def.user || null,
      workingDir: def.working_dir || null,
      exposedPorts: [],
    };

    // Build context
    if (def.build) {
      if (typeof def.build === 'string') {
        service.build = { context: def.build, dockerfile: 'Dockerfile' };
      } else {
        service.build = {
          context: def.build.context || '.',
          dockerfile: def.build.dockerfile || 'Dockerfile',
          args: def.build.args || {},
        };
      }
    }

    // Ports
    if (def.ports) {
      service.ports = def.ports.map(p => this._parsePort(p));
      service.exposedPorts = service.ports.map(p => ({
        port: p.containerPort,
        protocol: p.protocol || 'tcp',
      }));
    }

    // Expose (internal ports)
    if (def.expose) {
      for (const exp of def.expose) {
        const port = parseInt(String(exp), 10);
        if (!isNaN(port)) {
          service.exposedPorts.push({ port, protocol: 'tcp' });
        }
      }
    }

    // Environment
    if (def.environment) {
      if (Array.isArray(def.environment)) {
        for (const entry of def.environment) {
          const eqIdx = String(entry).indexOf('=');
          if (eqIdx > 0) {
            service.envVars[entry.slice(0, eqIdx)] = entry.slice(eqIdx + 1);
          } else {
            service.envVars[entry] = '';
          }
        }
      } else {
        Object.assign(service.envVars, def.environment);
      }
    }

    // Volumes
    if (def.volumes) {
      service.volumes = def.volumes.map(v => this._parseVolume(v));
    }

    // Dependencies
    if (def.depends_on) {
      if (Array.isArray(def.depends_on)) {
        service.depends_on = def.depends_on;
      } else {
        service.depends_on = Object.keys(def.depends_on);
      }
    }

    // Healthcheck
    if (def.healthcheck) {
      service.healthcheck = this._parseHealthcheck(def.healthcheck);
    }

    // Networks
    if (def.networks) {
      if (Array.isArray(def.networks)) {
        service.networks = def.networks;
      } else {
        service.networks = Object.keys(def.networks);
      }
    }

    // Labels
    if (def.labels) {
      if (Array.isArray(def.labels)) {
        for (const label of def.labels) {
          const eqIdx = label.indexOf('=');
          if (eqIdx > 0) {
            service.labels[label.slice(0, eqIdx)] = label.slice(eqIdx + 1);
          }
        }
      } else {
        Object.assign(service.labels, def.labels);
      }
    }

    // Deploy (resource limits for swarm/k8s)
    if (def.deploy) {
      service.deploy = this._parseDeploy(def.deploy);
    }

    // Infer app type from image
    service.appType = this._inferAppType(service);

    return service;
  }

  _parsePort(portDef) {
    if (typeof portDef === 'object' && portDef !== null) {
      return {
        hostPort: portDef.published || null,
        containerPort: portDef.target,
        protocol: portDef.protocol || 'tcp',
      };
    }

    const str = String(portDef);
    const protoMatch = str.match(/^(.+)\/(\w+)$/);
    const portStr = protoMatch ? protoMatch[1] : str;
    const protocol = protoMatch ? protoMatch[2] : 'tcp';

    const parts = portStr.split(':');
    if (parts.length >= 2) {
      return {
        hostPort: parseInt(parts[parts.length - 2], 10),
        containerPort: parseInt(parts[parts.length - 1], 10),
        protocol,
      };
    }
    return {
      hostPort: null,
      containerPort: parseInt(parts[0], 10),
      protocol,
    };
  }

  _parseVolume(volumeDef) {
    if (typeof volumeDef === 'object' && volumeDef !== null) {
      return {
        source: volumeDef.source || null,
        target: volumeDef.target,
        type: volumeDef.type || 'volume',
        readOnly: volumeDef.read_only || false,
      };
    }

    const str = String(volumeDef);
    const parts = str.split(':');

    if (parts.length >= 2) {
      const readOnly = parts.length >= 3 && parts[2] === 'ro';
      const source = parts[0];
      const target = parts[1];
      const isNamedVolume = !source.startsWith('/') && !source.startsWith('.');
      return {
        source,
        target,
        type: isNamedVolume ? 'volume' : 'bind',
        readOnly,
      };
    }
    return { source: null, target: parts[0], type: 'volume', readOnly: false };
  }

  _parseHealthcheck(hc) {
    if (hc.disable) return null;
    return {
      command: hc.test || null,
      interval: hc.interval || '30s',
      timeout: hc.timeout || '5s',
      retries: hc.retries || 3,
      startPeriod: hc.start_period || '0s',
    };
  }

  _parseDeploy(deploy) {
    const result = { replicas: deploy.replicas || 1 };

    if (deploy.resources) {
      result.resources = {};
      if (deploy.resources.limits) {
        result.resources.limits = {
          cpus: deploy.resources.limits.cpus || null,
          memory: deploy.resources.limits.memory || null,
        };
      }
      if (deploy.resources.reservations) {
        result.resources.requests = {
          cpus: deploy.resources.reservations.cpus || null,
          memory: deploy.resources.reservations.memory || null,
        };
      }
    }

    return result;
  }

  _inferAppType(service) {
    const image = (service.image || '').toLowerCase();
    if (image.includes('node')) return 'node';
    if (image.includes('python') || image.includes('django') || image.includes('flask')) return 'python';
    if (image.includes('golang') || image.includes('go:')) return 'golang';
    if (image.includes('java') || image.includes('maven') || image.includes('gradle') || image.includes('tomcat') || image.includes('spring')) return 'java';
    if (image.includes('ruby') || image.includes('rails')) return 'ruby';
    if (image.includes('php') || image.includes('laravel')) return 'php';
    if (image.includes('nginx') || image.includes('httpd') || image.includes('apache') || image.includes('caddy')) return 'webserver';
    if (image.includes('redis')) return 'redis';
    if (image.includes('postgres')) return 'postgres';
    if (image.includes('mysql') || image.includes('mariadb')) return 'mysql';
    if (image.includes('mongo')) return 'mongo';
    if (image.includes('rust')) return 'rust';
    if (image.includes('dotnet') || image.includes('aspnet')) return 'dotnet';
    return 'generic';
  }
}

module.exports = { ComposeParser };
