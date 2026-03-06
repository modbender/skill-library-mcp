export class CLIError extends Error {
  constructor(message: string, public code?: string) {
    super(message);
    this.name = 'CLIError';
  }
}

export class ValidationError extends CLIError {
  constructor(message: string) {
    super(message, 'VALIDATION_ERROR');
    this.name = 'ValidationError';
  }
}

export class CanvasError extends CLIError {
  constructor(message: string) {
    super(message, 'CANVAS_ERROR');
    this.name = 'CanvasError';
  }
}

export class AIError extends CLIError {
  constructor(message: string) {
    super(message, 'AI_ERROR');
    this.name = 'AIError';
  }
}

export function formatError(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
}

export function getNodeCanvasInstallHelp(): string {
  const platform = process.platform;
  let installCmd = '';

  switch (platform) {
    case 'darwin':
      installCmd = 'brew install pkg-config cairo pango jpeg giflib librsvg pixman';
      break;
    case 'linux':
      installCmd = 'sudo apt-get install libcairo2-dev libjpeg-dev libpango1.0-dev libgif-dev librsvg2-dev';
      break;
    case 'win32':
      installCmd = 'npm install --global --production windows-build-tools';
      break;
    default:
      installCmd = 'See https://github.com/Automattic/node-canvas#installation';
  }

  return `
Please install the required dependencies:

${installCmd}

Then reinstall the dependencies:
  npm install

For more information, visit:
  https://github.com/Automattic/node-canvas#installation
`;
}
