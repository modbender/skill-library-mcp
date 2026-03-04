'use strict';

class HealthChecks {
  /**
   * Generate Kubernetes probe configurations from a parsed Docker config.
   *
   * @param {object} config - Parsed Dockerfile or compose service config
   * @returns {object} { livenessProbe, readinessProbe, startupProbe }
   */
  generate(config) {
    const ports = config.exposedPorts || [];
    const healthcheck = config.healthcheck || null;
    const appType = config.appType || 'generic';

    const probes = {
      livenessProbe: null,
      readinessProbe: null,
      startupProbe: null,
    };

    // If the Dockerfile/compose has an explicit HEALTHCHECK, use it for liveness
    if (healthcheck && healthcheck.command) {
      probes.livenessProbe = this._fromDockerHealthcheck(healthcheck);
      // Create a readiness probe from the same command with shorter timing
      probes.readinessProbe = this._fromDockerHealthcheck(healthcheck);
      probes.readinessProbe.periodSeconds = 5;
      probes.readinessProbe.failureThreshold = 3;
    } else if (ports.length > 0) {
      // Infer probes from exposed ports and app type
      const primaryPort = ports[0].port;
      const httpProbe = this._isHttpApp(appType);

      if (httpProbe) {
        const healthPath = this._inferHealthPath(appType);
        probes.livenessProbe = {
          httpGet: { path: healthPath, port: primaryPort },
          initialDelaySeconds: this._getInitialDelay(appType),
          periodSeconds: 15,
          timeoutSeconds: 5,
          failureThreshold: 3,
          successThreshold: 1,
        };
        probes.readinessProbe = {
          httpGet: { path: healthPath, port: primaryPort },
          initialDelaySeconds: 5,
          periodSeconds: 5,
          timeoutSeconds: 3,
          failureThreshold: 3,
          successThreshold: 1,
        };
      } else {
        probes.livenessProbe = {
          tcpSocket: { port: primaryPort },
          initialDelaySeconds: this._getInitialDelay(appType),
          periodSeconds: 15,
          timeoutSeconds: 5,
          failureThreshold: 3,
          successThreshold: 1,
        };
        probes.readinessProbe = {
          tcpSocket: { port: primaryPort },
          initialDelaySeconds: 5,
          periodSeconds: 5,
          timeoutSeconds: 3,
          failureThreshold: 3,
          successThreshold: 1,
        };
      }
    } else {
      // No ports, use exec-based probes
      probes.livenessProbe = {
        exec: { command: ['cat', '/tmp/healthy'] },
        initialDelaySeconds: 15,
        periodSeconds: 20,
        timeoutSeconds: 5,
        failureThreshold: 3,
        successThreshold: 1,
      };
      probes.readinessProbe = {
        exec: { command: ['cat', '/tmp/healthy'] },
        initialDelaySeconds: 5,
        periodSeconds: 10,
        timeoutSeconds: 3,
        failureThreshold: 3,
        successThreshold: 1,
      };
    }

    // Always add a startup probe for slow-starting apps
    probes.startupProbe = this._generateStartupProbe(config, probes.livenessProbe);

    return probes;
  }

  _fromDockerHealthcheck(hc) {
    const command = Array.isArray(hc.command)
      ? (hc.command[0] === 'CMD-SHELL' ? ['/bin/sh', '-c', hc.command.slice(1).join(' ')] : hc.command)
      : ['/bin/sh', '-c', hc.command];

    return {
      exec: { command },
      initialDelaySeconds: this._parseDuration(hc.startPeriod || '0s'),
      periodSeconds: this._parseDuration(hc.interval || '30s'),
      timeoutSeconds: this._parseDuration(hc.timeout || '5s'),
      failureThreshold: hc.retries || 3,
      successThreshold: 1,
    };
  }

  _generateStartupProbe(config, livenessProbe) {
    if (!livenessProbe) return null;

    const appType = config.appType || 'generic';
    const maxStartupTime = this._getMaxStartupTime(appType);

    // Clone the liveness probe mechanism
    const startup = {};
    if (livenessProbe.httpGet) startup.httpGet = { ...livenessProbe.httpGet };
    else if (livenessProbe.tcpSocket) startup.tcpSocket = { ...livenessProbe.tcpSocket };
    else if (livenessProbe.exec) startup.exec = { ...livenessProbe.exec };

    startup.periodSeconds = 5;
    startup.timeoutSeconds = 5;
    startup.failureThreshold = Math.ceil(maxStartupTime / 5);
    startup.successThreshold = 1;

    return startup;
  }

  _isHttpApp(appType) {
    return ['node', 'python', 'java', 'ruby', 'php', 'golang', 'rust', 'dotnet', 'webserver'].includes(appType);
  }

  _inferHealthPath(appType) {
    const paths = {
      node: '/healthz',
      python: '/healthz',
      java: '/actuator/health',
      ruby: '/health',
      php: '/health',
      golang: '/healthz',
      rust: '/healthz',
      dotnet: '/health',
      webserver: '/',
    };
    return paths[appType] || '/healthz';
  }

  _getInitialDelay(appType) {
    const delays = {
      java: 30,
      dotnet: 20,
      node: 10,
      python: 10,
      golang: 5,
      rust: 5,
      ruby: 15,
      php: 10,
      webserver: 5,
      database: 15,
      redis: 5,
      postgres: 15,
      mysql: 20,
      mongo: 15,
      generic: 15,
    };
    return delays[appType] || 15;
  }

  _getMaxStartupTime(appType) {
    const times = {
      java: 120,
      dotnet: 90,
      node: 30,
      python: 30,
      golang: 15,
      rust: 15,
      ruby: 45,
      php: 30,
      webserver: 10,
      database: 60,
      redis: 10,
      postgres: 60,
      mysql: 90,
      mongo: 60,
      generic: 60,
    };
    return times[appType] || 60;
  }

  /**
   * Parse a Docker duration string (e.g. "30s", "1m30s") into seconds.
   */
  _parseDuration(str) {
    if (typeof str === 'number') return str;
    let seconds = 0;
    const minMatch = str.match(/(\d+)m/);
    const secMatch = str.match(/(\d+)s/);
    if (minMatch) seconds += parseInt(minMatch[1], 10) * 60;
    if (secMatch) seconds += parseInt(secMatch[1], 10);
    return seconds || 30;
  }
}

module.exports = { HealthChecks };
