'use strict';

const fs = require('fs');
const path = require('path');
const { Command } = require('commander');
const { Analyzer } = require('../lib/analyzer');
const { Visualizer } = require('../lib/visualizer');
const { Reporter } = require('../lib/reporter');
const { loadConfig, resolveOutputPath } = require('./config');

function loadMessages(filepath) {
  if (!fs.existsSync(filepath)) {
    throw new Error(`File not found: ${filepath}`);
  }
  const raw = fs.readFileSync(filepath, 'utf8');
  let data;
  try {
    data = JSON.parse(raw);
  } catch (e) {
    throw new Error(`Invalid JSON in ${filepath}: ${e.message}`);
  }
  if (!Array.isArray(data)) {
    throw new Error(`Expected an array of messages in ${filepath}, got ${typeof data}`);
  }
  return data;
}

function createProgram() {
  const program = new Command();

  program
    .name('agent-traffic-analyzer')
    .description(
      'Analyzes and visualizes communication patterns between OpenClaw agents'
    )
    .version('1.0.0');

  program
    .command('analyze')
    .description('Analyze agent communication patterns from a log file')
    .argument('<logfile>', 'Path to JSON communication log file')
    .option('-v, --verbose', 'Show detailed output')
    .action((logfile, opts) => {
      const config = loadConfig({ verbose: opts.verbose });
      const messages = loadMessages(logfile);
      const analyzer = new Analyzer(messages);
      const visualizer = new Visualizer(analyzer);
      const reporter = new Reporter(analyzer, visualizer);

      console.log(reporter.generateTextSummary());
    });

  program
    .command('summary')
    .description('Show summary statistics for agent communications')
    .argument('<logfile>', 'Path to JSON communication log file')
    .action((logfile) => {
      const messages = loadMessages(logfile);
      const analyzer = new Analyzer(messages);
      const summary = analyzer.getSummary();
      console.log(JSON.stringify(summary, null, 2));
    });

  program
    .command('bottlenecks')
    .description('Find bottlenecks in agent communication')
    .argument('<logfile>', 'Path to JSON communication log file')
    .option('--latency-threshold <ms>', 'Latency threshold in ms', parseInt, 100)
    .option('--traffic-threshold <ratio>', 'Traffic concentration threshold (0-1)', parseFloat, 0.3)
    .option('--failure-threshold <ratio>', 'Failure rate threshold (0-1)', parseFloat, 0.1)
    .action((logfile, opts) => {
      const messages = loadMessages(logfile);
      const analyzer = new Analyzer(messages);
      const bottlenecks = analyzer.findBottlenecks({
        latency_threshold: opts.latencyThreshold,
        traffic_threshold: opts.trafficThreshold,
        failure_threshold: opts.failureThreshold,
      });

      if (bottlenecks.length === 0) {
        console.log('No bottlenecks detected.');
        return;
      }

      console.log(`Found ${bottlenecks.length} bottleneck(s):\n`);
      for (const bn of bottlenecks) {
        const icon = bn.severity === 'critical' ? '[!]' : bn.severity === 'warning' ? '[~]' : '[i]';
        console.log(`  ${icon} [${bn.severity}] ${bn.detail}`);
      }

      const optimizations = analyzer.suggestOptimizations();
      if (optimizations.length > 0) {
        console.log('\nOptimization suggestions:');
        for (let i = 0; i < optimizations.length; i++) {
          console.log(`  ${i + 1}. [${optimizations[i].priority}] ${optimizations[i].description}`);
        }
      }
    });

  program
    .command('visualize')
    .description('Generate a visualization of the agent communication network')
    .argument('<logfile>', 'Path to JSON communication log file')
    .option('-f, --format <format>', 'Output format: dot, timeline, ascii', 'ascii')
    .option('-o, --output <file>', 'Write output to file instead of stdout')
    .option('--title <title>', 'Title for the visualization')
    .action((logfile, opts) => {
      const messages = loadMessages(logfile);
      const analyzer = new Analyzer(messages);
      const visualizer = new Visualizer(analyzer);

      let output;
      switch (opts.format.toLowerCase()) {
        case 'dot':
          output = visualizer.generateDot({ title: opts.title });
          break;
        case 'timeline':
          output = visualizer.generateTimeline();
          break;
        case 'ascii':
          output = visualizer.generateAsciiNetwork();
          break;
        default:
          console.error(`Unknown format: ${opts.format}. Use: dot, timeline, ascii`);
          process.exit(1);
      }

      if (opts.output) {
        const outPath = path.resolve(opts.output);
        fs.mkdirSync(path.dirname(outPath), { recursive: true });
        fs.writeFileSync(outPath, output, 'utf8');
        console.log(`Visualization written to ${outPath}`);
      } else {
        console.log(output);
      }
    });

  program
    .command('report')
    .description('Generate a full analysis report')
    .argument('<logfile>', 'Path to JSON communication log file')
    .option('-f, --format <format>', 'Output format: json, csv, dot', 'json')
    .option('-o, --output <file>', 'Write report to file')
    .action((logfile, opts) => {
      const messages = loadMessages(logfile);
      const analyzer = new Analyzer(messages);
      const visualizer = new Visualizer(analyzer);
      const reporter = new Reporter(analyzer, visualizer);

      const content = reporter.generateReport(opts.format);

      if (opts.output) {
        const outPath = path.resolve(opts.output);
        reporter.exportToFile(outPath, opts.format);
        console.log(`Report written to ${outPath}`);
      } else {
        console.log(content);
      }
    });

  return program;
}

module.exports = { createProgram, loadMessages };
