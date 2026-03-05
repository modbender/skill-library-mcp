/**
 * Simple Logger
 */

const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  gray: '\x1b[90m'
};

function timestamp(): string {
  return new Date().toISOString().replace('T', ' ').slice(0, 19);
}

export const logger = {
  info: (message: string, ...args: any[]) => {
    console.log(`${colors.gray}[${timestamp()}]${colors.reset} ${colors.blue}INFO${colors.reset}  ${message}`, ...args);
  },
  
  warn: (message: string, ...args: any[]) => {
    console.log(`${colors.gray}[${timestamp()}]${colors.reset} ${colors.yellow}WARN${colors.reset}  ${message}`, ...args);
  },
  
  error: (message: string, ...args: any[]) => {
    console.log(`${colors.gray}[${timestamp()}]${colors.reset} ${colors.red}ERROR${colors.reset} ${message}`, ...args);
  },
  
  success: (message: string, ...args: any[]) => {
    console.log(`${colors.gray}[${timestamp()}]${colors.reset} ${colors.green}OK${colors.reset}    ${message}`, ...args);
  },
  
  debug: (message: string, ...args: any[]) => {
    if (process.env.DEBUG) {
      console.log(`${colors.gray}[${timestamp()}] DEBUG ${message}${colors.reset}`, ...args);
    }
  }
};
