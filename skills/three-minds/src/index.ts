#!/usr/bin/env node
/**
 * Three Minds v2 - CLI 入口
 * 
 * 三个能干活的 AI 分身协作系统
 */

import { Command } from 'commander';
import { Council, loadConfig, getDefaultConfig } from './council';
import { CouncilConfig } from './types';
import * as path from 'path';
import * as fs from 'fs';

const program = new Command();

program
  .name('three-minds')
  .description('三个臭皮匠顶个诸葛亮 - AI 分身协作系统')
  .version('2.0.0')
  .argument('<task>', '任务描述')
  .option('-c, --config <path>', '配置文件路径')
  .option('-d, --dir <path>', '工作目录（默认当前目录）', process.cwd())
  .option('-m, --max-rounds <n>', '最大轮数', '15')
  .option('-q, --quiet', '静默模式')
  .option('-o, --output <path>', '保存结果到文件')
  .action(async (task: string, options: any) => {
    try {
      let config: CouncilConfig;

      if (options.config) {
        config = await loadConfig(options.config);
        // 覆盖工作目录
        config.projectDir = path.resolve(options.dir);
      } else {
        config = getDefaultConfig(path.resolve(options.dir));
      }

      // 覆盖 maxRounds
      if (options.maxRounds) {
        config.maxRounds = parseInt(options.maxRounds, 10);
      }

      // 确保工作目录存在
      if (!fs.existsSync(config.projectDir)) {
        console.error(`错误: 工作目录不存在: ${config.projectDir}`);
        process.exit(1);
      }

      const council = new Council(config, options.quiet);
      const session = await council.run(task);

      // 保存结果
      if (options.output) {
        const outputPath = path.resolve(options.output);
        const outputContent = JSON.stringify(session, null, 2);
        fs.writeFileSync(outputPath, outputContent);
        console.log(`\n💾 结果已保存: ${outputPath}`);
      }

      // 根据状态设置退出码
      process.exit(session.status === 'consensus' ? 0 : 1);
    } catch (error: any) {
      console.error(`错误: ${error.message}`);
      process.exit(1);
    }
  });

program.parse();
