'use strict';

const path = require('path');
const fs = require('fs');

let passed = 0;
let failed = 0;
const failures = [];

function assert(condition, message) {
  if (!condition) throw new Error(`Assertion failed: ${message}`);
}

function assertEqual(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(`${message}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
  }
}

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`  PASS  ${name}`);
  } catch (err) {
    failed++;
    failures.push({ name, error: err.message });
    console.log(`  FAIL  ${name}`);
    console.log(`        ${err.message}`);
  }
}

// --- DockerfileParser Tests ---
console.log('\nDockerfileParser');
const { DockerfileParser } = require('../scripts/dockerfile-parser');

test('parses base image and tag', () => {
  const parser = new DockerfileParser();
  const config = parser.parse('FROM node:20-alpine\nEXPOSE 3000');
  assertEqual(config.baseImage, 'node', 'baseImage');
  assertEqual(config.baseTag, '20-alpine', 'baseTag');
});

test('parses exposed ports', () => {
  const parser = new DockerfileParser();
  const config = parser.parse('FROM nginx\nEXPOSE 80 443');
  assertEqual(config.exposedPorts.length, 2, 'port count');
  assertEqual(config.exposedPorts[0].port, 80, 'first port');
  assertEqual(config.exposedPorts[1].port, 443, 'second port');
});

test('parses ENV key=value format', () => {
  const parser = new DockerfileParser();
  const config = parser.parse('FROM node\nENV NODE_ENV=production PORT=3000');
  assertEqual(config.envVars.NODE_ENV, 'production', 'NODE_ENV');
  assertEqual(config.envVars.PORT, '3000', 'PORT');
});

test('parses ENV key value format', () => {
  const parser = new DockerfileParser();
  const config = parser.parse('FROM node\nENV MY_VAR hello world');
  assertEqual(config.envVars.MY_VAR, 'hello world', 'MY_VAR');
});

test('parses VOLUME', () => {
  const parser = new DockerfileParser();
  const config = parser.parse('FROM node\nVOLUME /data /logs');
  assertEqual(config.volumes.length, 2, 'volume count');
});

test('parses WORKDIR', () => {
  const parser = new DockerfileParser();
  const config = parser.parse('FROM node\nWORKDIR /opt/app');
  assertEqual(config.workdir, '/opt/app', 'workdir');
});

test('parses USER', () => {
  const parser = new DockerfileParser();
  const config = parser.parse('FROM node\nUSER appuser');
  assertEqual(config.user, 'appuser', 'user');
});

test('parses CMD exec form', () => {
  const parser = new DockerfileParser();
  const config = parser.parse('FROM node\nCMD ["node", "index.js"]');
  assert(Array.isArray(config.cmd), 'cmd should be array');
  assertEqual(config.cmd[0], 'node', 'cmd[0]');
});

test('parses HEALTHCHECK', () => {
  const parser = new DockerfileParser();
  const config = parser.parse('FROM node\nHEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost/');
  assert(config.healthcheck !== null, 'healthcheck should exist');
  assertEqual(config.healthcheck.interval, '30s', 'interval');
});

test('infers app type from base image', () => {
  const parser = new DockerfileParser();
  assertEqual(parser.parse('FROM node:20').appType, 'node', 'node');
  assertEqual(parser.parse('FROM python:3.12').appType, 'python', 'python');
  assertEqual(parser.parse('FROM golang:1.22').appType, 'golang', 'golang');
  assertEqual(parser.parse('FROM nginx:latest').appType, 'webserver', 'webserver');
  assertEqual(parser.parse('FROM eclipse-temurin:21').appType, 'java', 'java from temurin');
});

test('handles multi-stage builds', () => {
  const parser = new DockerfileParser();
  const config = parser.parse('FROM node:20 AS builder\nRUN npm build\nFROM node:20-alpine\nCOPY --from=builder /app /app');
  assertEqual(config.stages.length, 2, 'stage count');
});

test('handles continuation lines', () => {
  const parser = new DockerfileParser();
  const config = parser.parse('FROM node\nRUN apt-get update && \\\n    apt-get install -y curl');
  assertEqual(config.runInstructions.length, 1, 'should join into one RUN');
});

test('parses real-world Node.js Dockerfile', () => {
  const parser = new DockerfileParser();
  const examplePath = path.join(__dirname, '..', 'assets', 'docker-examples', 'Dockerfile.node');
  const config = parser.parseFile(examplePath);
  assertEqual(config.appType, 'node', 'app type');
  assertEqual(config.exposedPorts[0].port, 3000, 'port');
  assert(config.healthcheck !== null, 'healthcheck');
  assertEqual(config.user, 'node', 'user');
});

// --- ComposeParser Tests ---
console.log('\nComposeParser');
const { ComposeParser } = require('../scripts/compose-parser');

test('parses docker-compose services', () => {
  const parser = new ComposeParser();
  const config = parser.parse(`
version: '3'
services:
  web:
    image: nginx
    ports:
      - "80:80"
  api:
    image: node:20
    ports:
      - "3000:3000"
`);
  assertEqual(config.services.length, 2, 'service count');
  assertEqual(config.services[0].name, 'web', 'first service');
});

test('parses environment variables (list format)', () => {
  const parser = new ComposeParser();
  const config = parser.parse(`
version: '3'
services:
  app:
    image: node
    environment:
      - NODE_ENV=production
      - PORT=3000
`);
  assertEqual(config.services[0].envVars.NODE_ENV, 'production', 'NODE_ENV');
});

test('parses environment variables (map format)', () => {
  const parser = new ComposeParser();
  const config = parser.parse(`
version: '3'
services:
  app:
    image: node
    environment:
      NODE_ENV: production
      PORT: 3000
`);
  assertEqual(config.services[0].envVars.NODE_ENV, 'production', 'NODE_ENV');
});

test('parses volumes', () => {
  const parser = new ComposeParser();
  const config = parser.parse(`
version: '3'
services:
  db:
    image: postgres
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
volumes:
  pgdata:
`);
  assertEqual(config.services[0].volumes.length, 2, 'volume count');
  assertEqual(config.services[0].volumes[0].type, 'volume', 'named volume type');
  assertEqual(config.services[0].volumes[1].type, 'bind', 'bind mount type');
  assertEqual(config.services[0].volumes[1].readOnly, true, 'read only');
});

test('parses deploy resources', () => {
  const parser = new ComposeParser();
  const config = parser.parse(`
version: '3.8'
services:
  app:
    image: node
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
`);
  assertEqual(config.services[0].deploy.replicas, 3, 'replicas');
  assertEqual(config.services[0].deploy.resources.limits.memory, '512M', 'memory limit');
});

test('parses real-world docker-compose.yml', () => {
  const parser = new ComposeParser();
  const examplePath = path.join(__dirname, '..', 'assets', 'docker-examples', 'docker-compose.yml');
  const config = parser.parseFile(examplePath);
  assertEqual(config.services.length, 3, 'service count');
  assert(config.services[0].depends_on.length > 0, 'dependencies');
});

// --- ResourceEstimator Tests ---
console.log('\nResourceEstimator');
const { ResourceEstimator } = require('../scripts/resource-estimator');

test('estimates resources for node app', () => {
  const estimator = new ResourceEstimator();
  const resources = estimator.estimate({ appType: 'node', exposedPorts: [{ port: 3000 }], volumes: [] });
  assertEqual(resources.requests.cpu, '100m', 'cpu request');
  assertEqual(resources.requests.memory, '128Mi', 'memory request');
});

test('estimates resources for java app', () => {
  const estimator = new ResourceEstimator();
  const resources = estimator.estimate({ appType: 'java', exposedPorts: [], volumes: [] });
  assertEqual(resources.limits.cpu, '1000m', 'cpu limit');
  assertEqual(resources.limits.memory, '1024Mi', 'memory limit');
});

test('increases resources for many ports', () => {
  const estimator = new ResourceEstimator();
  const resources = estimator.estimate({
    appType: 'generic',
    exposedPorts: [{ port: 80 }, { port: 443 }, { port: 8080 }],
    volumes: [],
  });
  assertEqual(resources.limits.cpu, '750m', 'scaled cpu');
});

test('uses deploy resources from compose', () => {
  const estimator = new ResourceEstimator();
  const resources = estimator.estimate({
    appType: 'node',
    deploy: { resources: { limits: { cpus: '0.5', memory: '512M' } } },
  });
  assertEqual(resources.limits.cpu, '500m', 'cpu from deploy');
  assertEqual(resources.limits.memory, '512Mi', 'memory from deploy');
});

// --- HealthChecks Tests ---
console.log('\nHealthChecks');
const { HealthChecks } = require('../scripts/health-checks');

test('generates HTTP probes for web apps', () => {
  const hc = new HealthChecks();
  const probes = hc.generate({ appType: 'node', exposedPorts: [{ port: 3000 }] });
  assert(probes.livenessProbe.httpGet !== undefined, 'liveness httpGet');
  assertEqual(probes.livenessProbe.httpGet.port, 3000, 'probe port');
  assertEqual(probes.livenessProbe.httpGet.path, '/healthz', 'probe path');
});

test('generates TCP probes for databases', () => {
  const hc = new HealthChecks();
  const probes = hc.generate({ appType: 'redis', exposedPorts: [{ port: 6379 }] });
  assert(probes.livenessProbe.tcpSocket !== undefined, 'liveness tcpSocket');
});

test('generates exec probes when no ports', () => {
  const hc = new HealthChecks();
  const probes = hc.generate({ appType: 'generic', exposedPorts: [] });
  assert(probes.livenessProbe.exec !== undefined, 'liveness exec');
});

test('uses Docker HEALTHCHECK if present', () => {
  const hc = new HealthChecks();
  const probes = hc.generate({
    appType: 'node',
    exposedPorts: [{ port: 3000 }],
    healthcheck: { command: 'curl -f http://localhost:3000/', interval: '15s', timeout: '3s', retries: 5 },
  });
  assert(probes.livenessProbe.exec !== undefined, 'should use exec from healthcheck');
  assertEqual(probes.livenessProbe.failureThreshold, 5, 'retries');
});

test('always generates startup probe', () => {
  const hc = new HealthChecks();
  const probes = hc.generate({ appType: 'java', exposedPorts: [{ port: 8080 }] });
  assert(probes.startupProbe !== null, 'startup probe should exist');
  assert(probes.startupProbe.failureThreshold > 10, 'java should have high failureThreshold');
});

// --- K8sGenerator Tests ---
console.log('\nK8sGenerator');
const { K8sGenerator } = require('../scripts/k8s-generator');

test('generates deployment from Dockerfile config', () => {
  const gen = new K8sGenerator();
  const config = {
    baseImage: 'node',
    baseTag: '20-alpine',
    exposedPorts: [{ port: 3000, protocol: 'tcp' }],
    envVars: { NODE_ENV: 'production' },
    volumes: [],
    workdir: '/app',
    user: 'node',
    entrypoint: null,
    cmd: ['node', 'index.js'],
    healthcheck: null,
    appType: 'node',
    labels: {},
  };
  const manifests = gen.generate(config, { name: 'my-app' });
  const deployment = manifests.find(m => m.kind === 'Deployment');
  assert(deployment !== undefined, 'should have deployment');
  assertEqual(deployment.metadata.name, 'my-app', 'name');
  assertEqual(deployment.spec.template.spec.containers[0].image, 'node:20-alpine', 'image');
});

test('generates service for exposed ports', () => {
  const gen = new K8sGenerator();
  const config = {
    baseImage: 'node', baseTag: '20', exposedPorts: [{ port: 3000, protocol: 'tcp' }],
    envVars: {}, volumes: [], workdir: '/app', user: null, entrypoint: null, cmd: null,
    healthcheck: null, appType: 'node', labels: {},
  };
  const manifests = gen.generate(config, { name: 'api' });
  const service = manifests.find(m => m.kind === 'Service');
  assert(service !== undefined, 'should have service');
  assertEqual(service.spec.ports[0].port, 3000, 'port');
});

test('generates configmap for env vars', () => {
  const gen = new K8sGenerator();
  const config = {
    baseImage: 'node', baseTag: '20', exposedPorts: [],
    envVars: { FOO: 'bar', BAZ: 'qux' }, volumes: [], workdir: '/app',
    user: null, entrypoint: null, cmd: null, healthcheck: null, appType: 'node', labels: {},
  };
  const manifests = gen.generate(config, { name: 'app' });
  const cm = manifests.find(m => m.kind === 'ConfigMap');
  assert(cm !== undefined, 'should have configmap');
  assertEqual(cm.data.FOO, 'bar', 'env data');
});

test('generates PVC for volumes', () => {
  const gen = new K8sGenerator();
  const config = {
    baseImage: 'postgres', baseTag: '16', exposedPorts: [{ port: 5432, protocol: 'tcp' }],
    envVars: {}, volumes: ['/var/lib/postgresql/data'], workdir: '/app',
    user: null, entrypoint: null, cmd: null, healthcheck: null, appType: 'postgres', labels: {},
  };
  const manifests = gen.generate(config, { name: 'db' });
  const pvc = manifests.find(m => m.kind === 'PersistentVolumeClaim');
  assert(pvc !== undefined, 'should have PVC');
});

test('generates ingress for HTTP apps', () => {
  const gen = new K8sGenerator();
  const config = {
    baseImage: 'node', baseTag: '20', exposedPorts: [{ port: 3000, protocol: 'tcp' }],
    envVars: {}, volumes: [], workdir: '/app', user: null, entrypoint: null, cmd: null,
    healthcheck: null, appType: 'node', labels: {},
  };
  const manifests = gen.generate(config, { name: 'web' });
  const ingress = manifests.find(m => m.kind === 'Ingress');
  assert(ingress !== undefined, 'should have ingress');
});

test('does not generate ingress for database', () => {
  const gen = new K8sGenerator();
  const config = {
    baseImage: 'postgres', baseTag: '16', exposedPorts: [{ port: 5432, protocol: 'tcp' }],
    envVars: {}, volumes: [], workdir: '/app', user: null, entrypoint: null, cmd: null,
    healthcheck: null, appType: 'postgres', labels: {},
  };
  const manifests = gen.generate(config, { name: 'db' });
  const ingress = manifests.find(m => m.kind === 'Ingress');
  assertEqual(ingress, undefined, 'should not have ingress for db');
});

test('generates from docker-compose config', () => {
  const gen = new K8sGenerator();
  const composeConfig = {
    version: '3.8',
    services: [
      {
        name: 'web', image: 'node:20', exposedPorts: [{ port: 3000, protocol: 'tcp' }],
        envVars: { NODE_ENV: 'production' }, volumes: [], healthcheck: null,
        appType: 'node', labels: {}, deploy: null, user: null, workingDir: null,
        entrypoint: null, command: null,
      },
      {
        name: 'db', image: 'postgres:16', exposedPorts: [{ port: 5432, protocol: 'tcp' }],
        envVars: { POSTGRES_DB: 'myapp' }, volumes: [{ target: '/var/lib/postgresql/data' }],
        healthcheck: null, appType: 'postgres', labels: {}, deploy: null, user: null,
        workingDir: null, entrypoint: null, command: null,
      },
    ],
    globalVolumes: [],
    globalNetworks: [],
  };
  const manifests = gen.generateFromCompose(composeConfig);
  const deployments = manifests.filter(m => m.kind === 'Deployment');
  assertEqual(deployments.length, 2, 'should have 2 deployments');
});

test('produces valid YAML output', () => {
  const gen = new K8sGenerator();
  const config = {
    baseImage: 'node', baseTag: '20', exposedPorts: [{ port: 3000, protocol: 'tcp' }],
    envVars: { X: 'y' }, volumes: [], workdir: '/app', user: null, entrypoint: null,
    cmd: null, healthcheck: null, appType: 'node', labels: {},
  };
  const manifests = gen.generate(config, { name: 'app' });
  const yamlStr = gen.toYAML(manifests);
  assert(yamlStr.includes('apiVersion:'), 'should contain apiVersion');
  assert(yamlStr.includes('kind: Deployment'), 'should contain Deployment');
  assert(yamlStr.includes('---'), 'should have document separators');
});

// --- ManifestValidator Tests ---
console.log('\nManifestValidator');
const { ManifestValidator } = require('../scripts/manifest-validator');

test('validates correct deployment', () => {
  const validator = new ManifestValidator();
  const result = validator.validate({
    apiVersion: 'apps/v1',
    kind: 'Deployment',
    metadata: { name: 'test' },
    spec: {
      replicas: 2,
      selector: { matchLabels: { app: 'test' } },
      template: {
        metadata: { labels: { app: 'test' } },
        spec: {
          containers: [{
            name: 'test', image: 'node:20',
            resources: { requests: { cpu: '100m' }, limits: { cpu: '500m' } },
            livenessProbe: { httpGet: { path: '/', port: 3000 } },
            readinessProbe: { httpGet: { path: '/', port: 3000 } },
            securityContext: { runAsNonRoot: true },
          }],
        },
      },
    },
  });
  assertEqual(result.valid, true, 'should be valid');
});

test('detects missing apiVersion', () => {
  const validator = new ManifestValidator();
  const result = validator.validate({ kind: 'Service', metadata: { name: 'x' } });
  assert(result.errors.length > 0, 'should have errors');
  assert(result.errors.some(e => e.includes('apiVersion')), 'should mention apiVersion');
});

test('warns about missing resource limits', () => {
  const validator = new ManifestValidator();
  const result = validator.validate({
    apiVersion: 'apps/v1',
    kind: 'Deployment',
    metadata: { name: 'test' },
    spec: {
      replicas: 1,
      selector: { matchLabels: { app: 'test' } },
      template: {
        metadata: { labels: { app: 'test' } },
        spec: { containers: [{ name: 'test', image: 'node:20' }] },
      },
    },
  });
  assert(result.errors.some(e => e.includes('resource limits')), 'should warn about resources');
});

// --- Integration: End-to-end from example Dockerfile ---
console.log('\nIntegration');

test('end-to-end: Dockerfile.node to manifests', () => {
  const parser = new DockerfileParser();
  const gen = new K8sGenerator();
  const validator = new ManifestValidator();

  const config = parser.parseFile(path.join(__dirname, '..', 'assets', 'docker-examples', 'Dockerfile.node'));
  const manifests = gen.generate(config, { name: 'node-app' });
  const validation = validator.validateAll(manifests);

  assert(manifests.length >= 3, 'should generate multiple manifests');
  const deployment = manifests.find(m => m.kind === 'Deployment');
  const container = deployment.spec.template.spec.containers[0];
  assert(container.resources !== undefined, 'should have resources');
  assert(container.livenessProbe !== undefined, 'should have liveness probe');
  assert(container.readinessProbe !== undefined, 'should have readiness probe');
  assert(container.securityContext !== undefined, 'should have security context');
});

test('end-to-end: Dockerfile.java to manifests', () => {
  const parser = new DockerfileParser();
  const gen = new K8sGenerator();

  const config = parser.parseFile(path.join(__dirname, '..', 'assets', 'docker-examples', 'Dockerfile.java'));
  const manifests = gen.generate(config, { name: 'java-app' });

  const deployment = manifests.find(m => m.kind === 'Deployment');
  const container = deployment.spec.template.spec.containers[0];
  assert(container.resources.limits.memory === '1024Mi' || parseInt(container.resources.limits.memory) >= 1024,
    'java should have at least 1Gi memory');
});

test('end-to-end: docker-compose.yml to manifests', () => {
  const composeParser = new ComposeParser();
  const gen = new K8sGenerator();

  const config = composeParser.parseFile(path.join(__dirname, '..', 'assets', 'docker-examples', 'docker-compose.yml'));
  const manifests = gen.generateFromCompose(config);

  const deployments = manifests.filter(m => m.kind === 'Deployment');
  assertEqual(deployments.length, 3, 'should have 3 deployments (web, db, cache)');

  const services = manifests.filter(m => m.kind === 'Service');
  assert(services.length >= 3, 'should have services');
});

// --- Summary ---
console.log(`\n${'='.repeat(50)}`);
console.log(`Results: ${passed} passed, ${failed} failed, ${passed + failed} total`);

if (failures.length > 0) {
  console.log('\nFailures:');
  for (const f of failures) {
    console.log(`  ${f.name}: ${f.error}`);
  }
}

process.exit(failed > 0 ? 1 : 0);
