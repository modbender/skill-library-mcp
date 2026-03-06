'use strict';

const fs = require('fs');
const path = require('path');

class DockerfileParser {
  /**
   * Parse a Dockerfile string into a structured configuration object.
   */
  parse(content) {
    const lines = this._preprocessLines(content);
    const config = {
      baseImage: null,
      baseTag: 'latest',
      stages: [],
      exposedPorts: [],
      envVars: {},
      volumes: [],
      labels: {},
      workdir: '/app',
      user: null,
      entrypoint: null,
      cmd: null,
      healthcheck: null,
      copyInstructions: [],
      runInstructions: [],
      args: {},
    };

    let currentStage = { name: null, baseImage: null, instructions: [] };

    for (const line of lines) {
      const instruction = this._parseInstruction(line);
      if (!instruction) continue;

      currentStage.instructions.push(instruction);

      switch (instruction.command) {
        case 'FROM':
          if (currentStage.baseImage) {
            config.stages.push({ ...currentStage });
            currentStage = { name: null, baseImage: null, instructions: [instruction] };
          }
          this._parseFrom(instruction.args, config, currentStage);
          break;
        case 'EXPOSE':
          this._parseExpose(instruction.args, config);
          break;
        case 'ENV':
          this._parseEnv(instruction.args, config);
          break;
        case 'VOLUME':
          this._parseVolume(instruction.args, config);
          break;
        case 'LABEL':
          this._parseLabel(instruction.args, config);
          break;
        case 'WORKDIR':
          config.workdir = instruction.args.trim();
          break;
        case 'USER':
          config.user = instruction.args.trim();
          break;
        case 'ENTRYPOINT':
          config.entrypoint = this._parseExecForm(instruction.args);
          break;
        case 'CMD':
          config.cmd = this._parseExecForm(instruction.args);
          break;
        case 'HEALTHCHECK':
          config.healthcheck = this._parseHealthcheck(instruction.args);
          break;
        case 'COPY':
        case 'ADD':
          config.copyInstructions.push(instruction.args);
          break;
        case 'RUN':
          config.runInstructions.push(instruction.args);
          break;
        case 'ARG':
          this._parseArg(instruction.args, config);
          break;
      }
    }

    if (currentStage.baseImage) {
      config.stages.push(currentStage);
    }

    this._inferAppType(config);

    return config;
  }

  /**
   * Parse a Dockerfile from a file path.
   */
  parseFile(filePath) {
    const resolvedPath = path.resolve(filePath);
    if (!fs.existsSync(resolvedPath)) {
      throw new Error(`Dockerfile not found: ${resolvedPath}`);
    }
    const content = fs.readFileSync(resolvedPath, 'utf-8');
    return this.parse(content);
  }

  /**
   * Join continuation lines (backslash at end) and strip comments.
   */
  _preprocessLines(content) {
    const rawLines = content.split('\n');
    const joined = [];
    let buffer = '';

    for (const raw of rawLines) {
      const trimmed = raw.trimEnd();
      if (trimmed.endsWith('\\')) {
        buffer += trimmed.slice(0, -1).trim() + ' ';
      } else {
        buffer += trimmed;
        joined.push(buffer.trim());
        buffer = '';
      }
    }
    if (buffer) joined.push(buffer.trim());

    return joined.filter(l => l && !l.startsWith('#'));
  }

  _parseInstruction(line) {
    const match = line.match(/^([A-Z]+)\s+(.*)/);
    if (!match) return null;
    return { command: match[1], args: match[2] };
  }

  _parseFrom(args, config, stage) {
    const asMatch = args.match(/^(\S+?)(?:\s+[Aa][Ss]\s+(\S+))?$/);
    if (!asMatch) return;

    const imageRef = asMatch[1];
    const alias = asMatch[2] || null;

    const [imageName, tag] = imageRef.includes(':')
      ? imageRef.split(':')
      : [imageRef, 'latest'];

    config.baseImage = imageName;
    config.baseTag = tag;
    stage.baseImage = imageName;
    stage.name = alias;
  }

  _parseExpose(args, config) {
    const parts = args.split(/\s+/);
    for (const part of parts) {
      const portMatch = part.match(/^(\d+)(\/(\w+))?$/);
      if (portMatch) {
        config.exposedPorts.push({
          port: parseInt(portMatch[1], 10),
          protocol: (portMatch[3] || 'tcp').toLowerCase(),
        });
      }
    }
  }

  _parseEnv(args, config) {
    // Handle both "ENV KEY=VALUE" and "ENV KEY VALUE" formats
    const kvMatch = args.match(/^(\w+)=("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\S+)(.*)$/);
    if (kvMatch) {
      // KEY=VALUE format, possibly multiple
      const pairs = args.match(/(\w+)=("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\S+)/g);
      if (pairs) {
        for (const pair of pairs) {
          const eqIdx = pair.indexOf('=');
          const key = pair.slice(0, eqIdx);
          let val = pair.slice(eqIdx + 1);
          val = val.replace(/^["']|["']$/g, '');
          config.envVars[key] = val;
        }
      }
    } else {
      const spaceMatch = args.match(/^(\w+)\s+(.+)$/);
      if (spaceMatch) {
        config.envVars[spaceMatch[1]] = spaceMatch[2];
      }
    }
  }

  _parseVolume(args, config) {
    const parsed = this._parseExecForm(args);
    if (Array.isArray(parsed)) {
      config.volumes.push(...parsed);
    } else {
      config.volumes.push(...args.split(/\s+/));
    }
  }

  _parseLabel(args, config) {
    const pairs = args.match(/(\S+)=("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\S+)/g);
    if (pairs) {
      for (const pair of pairs) {
        const eqIdx = pair.indexOf('=');
        const key = pair.slice(0, eqIdx);
        let val = pair.slice(eqIdx + 1);
        val = val.replace(/^["']|["']$/g, '');
        config.labels[key] = val;
      }
    }
  }

  _parseArg(args, config) {
    const match = args.match(/^(\w+)(?:=(.+))?$/);
    if (match) {
      config.args[match[1]] = match[2] || null;
    }
  }

  _parseExecForm(args) {
    const trimmed = args.trim();
    if (trimmed.startsWith('[')) {
      try {
        return JSON.parse(trimmed);
      } catch {
        return trimmed;
      }
    }
    return trimmed;
  }

  _parseHealthcheck(args) {
    const trimmed = args.trim();
    if (trimmed === 'NONE') return null;

    const hc = {
      command: null,
      interval: '30s',
      timeout: '5s',
      retries: 3,
      startPeriod: '0s',
    };

    const intervalMatch = trimmed.match(/--interval=(\S+)/);
    if (intervalMatch) hc.interval = intervalMatch[1];

    const timeoutMatch = trimmed.match(/--timeout=(\S+)/);
    if (timeoutMatch) hc.timeout = timeoutMatch[1];

    const retriesMatch = trimmed.match(/--retries=(\d+)/);
    if (retriesMatch) hc.retries = parseInt(retriesMatch[1], 10);

    const startMatch = trimmed.match(/--start-period=(\S+)/);
    if (startMatch) hc.startPeriod = startMatch[1];

    const cmdMatch = trimmed.match(/CMD\s+(.*)/);
    if (cmdMatch) {
      hc.command = this._parseExecForm(cmdMatch[1]);
    }

    return hc;
  }

  /**
   * Infer application type from base image and run instructions.
   */
  _inferAppType(config) {
    const image = (config.baseImage || '').toLowerCase();
    const runs = config.runInstructions.join(' ').toLowerCase();

    if (image.includes('node') || runs.includes('npm ') || runs.includes('yarn ')) {
      config.appType = 'node';
    } else if (image.includes('python') || runs.includes('pip ') || runs.includes('pipenv')) {
      config.appType = 'python';
    } else if (image.includes('golang') || image.includes('go') || runs.includes('go build')) {
      config.appType = 'golang';
    } else if (image.includes('java') || image.includes('maven') || image.includes('gradle') || image.includes('temurin') || image.includes('tomcat') || image.includes('spring') || runs.includes('mvn ') || runs.includes('gradle ')) {
      config.appType = 'java';
    } else if (image.includes('ruby') || runs.includes('gem ') || runs.includes('bundle ')) {
      config.appType = 'ruby';
    } else if (image.includes('php') || runs.includes('composer ')) {
      config.appType = 'php';
    } else if (image.includes('nginx') || image.includes('httpd') || image.includes('apache')) {
      config.appType = 'webserver';
    } else if (image.includes('redis') || image.includes('postgres') || image.includes('mysql') || image.includes('mongo')) {
      config.appType = 'database';
    } else if (image.includes('rust') || runs.includes('cargo ')) {
      config.appType = 'rust';
    } else if (image.includes('dotnet') || image.includes('aspnet') || runs.includes('dotnet ')) {
      config.appType = 'dotnet';
    } else {
      config.appType = 'generic';
    }
  }
}

module.exports = { DockerfileParser };
