import { execSync } from 'child_process';
import chalk from 'chalk';

export interface SystemDeps {
  name: string;
  command: string;
  required: boolean;
}

export const requiredDeps: SystemDeps[] = [
  { name: 'pkg-config', command: 'pkg-config --version', required: true },
  { name: 'cairo', command: 'pkg-config --exists cairo', required: true },
  { name: 'pango', command: 'pkg-config --exists pango-1.0', required: true },
  { name: 'jpeg', command: 'pkg-config --exists libjpeg', required: false },
  { name: 'giflib', command: 'pkg-config --exists giflib', required: false },
  { name: 'librsvg', command: 'pkg-config --exists librsvg-2.0', required: false },
  { name: 'pixman', command: 'pkg-config --exists pixman-1', required: false },
];

export function checkSystemDeps(): { missing: string[]; optional: string[] } {
  const missing: string[] = [];
  const optional: string[] = [];

  for (const dep of requiredDeps) {
    try {
      execSync(dep.command, { stdio: 'ignore' });
    } catch {
      if (dep.required) {
        missing.push(dep.name);
      } else {
        optional.push(dep.name);
      }
    }
  }

  return { missing, optional };
}

export function getInstallInstructions(): string {
  const platform = process.platform;

  switch (platform) {
    case 'darwin':
      return `
For macOS, install the required dependencies using Homebrew:

  brew install pkg-config cairo pango jpeg giflib librsvg pixman

Then rebuild node-canvas:

  npm rebuild canvas

Or reinstall your dependencies:

  npm install
`;
    case 'linux':
      return `
For Ubuntu/Debian, install the required dependencies:

  sudo apt-get update
  sudo apt-get install libcairo2-dev libjpeg-dev libpango1.0-dev libgif-dev librsvg2-dev libpixman1-dev

Then rebuild node-canvas:

  npm rebuild canvas

Or reinstall your dependencies:

  npm install
`;
    case 'win32':
      return `
For Windows, install the required tools:

  npm install --global --production windows-build-tools

Then rebuild node-canvas:

  npm rebuild canvas

Or reinstall your dependencies:

  npm install
`;
    default:
      return `
For your platform, please visit the node-canvas installation guide:

  https://github.com/Automattic/node-canvas#installation
`;
  }
}

export function displayInstallHelp(missing: string[], optional: string[]): void {
  console.error(chalk.red('\n✗ Missing required system dependencies:'));
  console.error(chalk.gray('  ' + missing.join(', ')));

  if (optional.length > 0) {
    console.error(chalk.yellow('\n⚠ Missing optional dependencies:'));
    console.error(chalk.gray('  ' + optional.join(', ')));
  }

  console.error(chalk.blue('\n' + getInstallInstructions()));

  console.error(chalk.gray('For more information, visit:'));
  console.error(chalk.gray('  https://github.com/Automattic/node-canvas#installation'));
}

export async function tryLoadCanvas(): Promise<boolean> {
  try {
    await import('canvas');
    return true;
  } catch {
    return false;
  }
}
