import chalk from 'chalk';

const timestamp = () => new Date().toISOString();

export const logger = {
  info: (msg, ...args) => {
    console.log(chalk.blue(`[${timestamp()}] INFO:`), msg, ...args);
  },

  success: (msg, ...args) => {
    console.log(chalk.green(`[${timestamp()}] SUCCESS:`), msg, ...args);
  },

  warning: (msg, ...args) => {
    console.log(chalk.yellow(`[${timestamp()}] WARNING:`), msg, ...args);
  },

  error: (msg, ...args) => {
    console.error(chalk.red(`[${timestamp()}] ERROR:`), msg, ...args);
  },

  section: title => {
    console.log('\n' + chalk.cyan('='.repeat(60)));
    console.log(chalk.cyan.bold(title));
    console.log(chalk.cyan('='.repeat(60)) + '\n');
  },

  data: (label, value) => {
    console.log(chalk.gray(`  ${label}:`), chalk.white(value));
  },

  txHash: (hash, explorerUrl = 'https://pgp.elastos.io') => {
    console.log(chalk.gray(`  Transaction:`), chalk.white(hash));
    console.log(chalk.gray(`  Explorer:`), chalk.blue(`${explorerUrl}/tx/${hash}`));
  },

  btcTxHash: hash => {
    console.log(chalk.gray(`  BTC Transaction:`), chalk.white(hash));
    console.log(chalk.gray(`  Explorer:`), chalk.blue(`https://mempool.space/tx/${hash}`));
  }
};
