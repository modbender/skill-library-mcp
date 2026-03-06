'use strict';

const yaml = require('js-yaml');
const { ResourceEstimator } = require('./resource-estimator');
const { HealthChecks } = require('./health-checks');

class K8sGenerator {
  constructor() {
    this.resourceEstimator = new ResourceEstimator();
    this.healthChecks = new HealthChecks();
  }

  /**
   * Generate Kubernetes manifests from a parsed Docker config.
   *
   * @param {object} config - Parsed Dockerfile config (from DockerfileParser)
   * @param {object} options - { name, namespace, replicas, imageTag }
   * @returns {object[]} Array of K8s manifest objects
   */
  generate(config, options = {}) {
    const name = options.name || this._inferName(config);
    const namespace = options.namespace || 'default';
    const replicas = options.replicas || 2;
    const imageTag = options.imageTag || `${config.baseImage}:${config.baseTag || 'latest'}`;

    const manifests = [];

    // Deployment
    manifests.push(this._generateDeployment(config, { name, namespace, replicas, imageTag }));

    // Service (if ports are exposed)
    if (config.exposedPorts && config.exposedPorts.length > 0) {
      manifests.push(this._generateService(config, { name, namespace }));
    }

    // ConfigMap (if env vars exist)
    if (config.envVars && Object.keys(config.envVars).length > 0) {
      manifests.push(this._generateConfigMap(config, { name, namespace }));
    }

    // PVCs (if volumes exist)
    const pvcs = this._generatePVCs(config, { name, namespace });
    manifests.push(...pvcs);

    // Ingress (if HTTP app with ports)
    if (config.exposedPorts && config.exposedPorts.length > 0 && this._isHttpApp(config.appType)) {
      manifests.push(this._generateIngress(config, { name, namespace }));
    }

    return manifests;
  }

  /**
   * Generate manifests from a parsed docker-compose config (multiple services).
   *
   * @param {object} composeConfig - Parsed docker-compose config (from ComposeParser)
   * @param {object} options - { namespace }
   * @returns {object[]} Array of K8s manifest objects
   */
  generateFromCompose(composeConfig, options = {}) {
    const namespace = options.namespace || 'default';
    const allManifests = [];

    for (const service of composeConfig.services) {
      const serviceConfig = {
        baseImage: service.image || `${service.name}`,
        baseTag: 'latest',
        exposedPorts: service.exposedPorts || [],
        envVars: service.envVars || {},
        volumes: (service.volumes || []).map(v => v.target).filter(Boolean),
        workdir: service.workingDir || '/app',
        user: service.user,
        entrypoint: service.entrypoint,
        cmd: service.command,
        healthcheck: service.healthcheck,
        appType: service.appType || 'generic',
        labels: service.labels || {},
        deploy: service.deploy || null,
      };

      const imageTag = service.image || `${service.name}:latest`;
      const replicas = (service.deploy && service.deploy.replicas) || 2;

      const manifests = this.generate(serviceConfig, {
        name: service.name,
        namespace,
        replicas,
        imageTag,
      });

      allManifests.push(...manifests);
    }

    return allManifests;
  }

  /**
   * Render manifests as YAML string.
   */
  toYAML(manifests) {
    return manifests
      .map(m => yaml.dump(m, { lineWidth: -1, noRefs: true, quotingType: '"' }))
      .join('---\n');
  }

  _generateDeployment(config, { name, namespace, replicas, imageTag }) {
    const resources = this.resourceEstimator.estimate(config);
    const probes = this.healthChecks.generate(config);

    const container = {
      name,
      image: imageTag,
      resources,
      securityContext: {
        allowPrivilegeEscalation: false,
        readOnlyRootFilesystem: false,
        runAsNonRoot: config.user ? true : false,
        capabilities: { drop: ['ALL'] },
      },
    };

    // Ports
    if (config.exposedPorts && config.exposedPorts.length > 0) {
      container.ports = config.exposedPorts.map(p => ({
        containerPort: p.port,
        protocol: (p.protocol || 'tcp').toUpperCase(),
      }));
    }

    // Probes
    if (probes.livenessProbe) container.livenessProbe = probes.livenessProbe;
    if (probes.readinessProbe) container.readinessProbe = probes.readinessProbe;
    if (probes.startupProbe) container.startupProbe = probes.startupProbe;

    // Env from ConfigMap
    if (config.envVars && Object.keys(config.envVars).length > 0) {
      container.envFrom = [{ configMapRef: { name: `${name}-config` } }];
    }

    // Volume mounts
    const volumeMounts = [];
    const volumes = [];
    if (config.volumes && config.volumes.length > 0) {
      config.volumes.forEach((vol, i) => {
        const volPath = typeof vol === 'string' ? vol : vol.target || vol;
        const volName = `${name}-vol-${i}`;
        volumeMounts.push({ name: volName, mountPath: volPath });
        volumes.push({
          name: volName,
          persistentVolumeClaim: { claimName: `${name}-pvc-${i}` },
        });
      });
      container.volumeMounts = volumeMounts;
    }

    // Working directory
    if (config.workdir) {
      container.workingDir = config.workdir;
    }

    // Command / args
    if (config.entrypoint) {
      container.command = Array.isArray(config.entrypoint) ? config.entrypoint : [config.entrypoint];
    }
    if (config.cmd) {
      container.args = Array.isArray(config.cmd) ? config.cmd : config.cmd.split(/\s+/);
    }

    const deployment = {
      apiVersion: 'apps/v1',
      kind: 'Deployment',
      metadata: {
        name,
        namespace,
        labels: { app: name },
      },
      spec: {
        replicas,
        selector: { matchLabels: { app: name } },
        template: {
          metadata: { labels: { app: name } },
          spec: {
            containers: [container],
          },
        },
      },
    };

    if (volumes.length > 0) {
      deployment.spec.template.spec.volumes = volumes;
    }

    return deployment;
  }

  _generateService(config, { name, namespace }) {
    const ports = (config.exposedPorts || []).map((p, i) => ({
      name: `port-${i}`,
      port: p.port,
      targetPort: p.port,
      protocol: (p.protocol || 'tcp').toUpperCase(),
    }));

    return {
      apiVersion: 'v1',
      kind: 'Service',
      metadata: {
        name,
        namespace,
        labels: { app: name },
      },
      spec: {
        type: 'ClusterIP',
        selector: { app: name },
        ports,
      },
    };
  }

  _generateConfigMap(config, { name, namespace }) {
    const data = {};
    for (const [key, val] of Object.entries(config.envVars)) {
      data[key] = String(val);
    }

    return {
      apiVersion: 'v1',
      kind: 'ConfigMap',
      metadata: {
        name: `${name}-config`,
        namespace,
        labels: { app: name },
      },
      data,
    };
  }

  _generatePVCs(config, { name, namespace }) {
    const pvcs = [];
    const vols = config.volumes || [];

    vols.forEach((vol, i) => {
      pvcs.push({
        apiVersion: 'v1',
        kind: 'PersistentVolumeClaim',
        metadata: {
          name: `${name}-pvc-${i}`,
          namespace,
          labels: { app: name },
        },
        spec: {
          accessModes: ['ReadWriteOnce'],
          resources: {
            requests: { storage: '1Gi' },
          },
        },
      });
    });

    return pvcs;
  }

  _generateIngress(config, { name, namespace }) {
    const port = config.exposedPorts[0].port;

    return {
      apiVersion: 'networking.k8s.io/v1',
      kind: 'Ingress',
      metadata: {
        name: `${name}-ingress`,
        namespace,
        labels: { app: name },
        annotations: {
          'nginx.ingress.kubernetes.io/rewrite-target': '/',
        },
      },
      spec: {
        rules: [
          {
            host: `${name}.example.com`,
            http: {
              paths: [
                {
                  path: '/',
                  pathType: 'Prefix',
                  backend: {
                    service: {
                      name,
                      port: { number: port },
                    },
                  },
                },
              ],
            },
          },
        ],
      },
    };
  }

  _inferName(config) {
    if (config.labels && config.labels['com.docker.compose.service']) {
      return config.labels['com.docker.compose.service'];
    }
    const image = config.baseImage || 'app';
    return image.split('/').pop().replace(/[^a-z0-9-]/g, '-');
  }

  _isHttpApp(appType) {
    return ['node', 'python', 'java', 'ruby', 'php', 'golang', 'rust', 'dotnet', 'webserver'].includes(appType);
  }
}

module.exports = { K8sGenerator };
