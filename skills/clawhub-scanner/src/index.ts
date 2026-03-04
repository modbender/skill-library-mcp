#!/usr/bin/env node
import { Command } from "commander";
import { runScan, scanSkill, getDefaultSkillPaths } from "./scanner.js";
import { printReport, formatJson } from "./reporter.js";

const program = new Command();

program
  .name("clawhub-scanner")
  .description("Scan ClawHub skills for malware, credential theft, and security risks")
  .version("0.1.0");

program
  .command("scan")
  .description("Scan installed skills for security issues")
  .option("-s, --skill <path>", "Scan a specific skill directory")
  .option("-j, --json", "Output results as JSON")
  .option("-v, --verbose", "Show all findings including low severity")
  .option("-q, --quiet", "Only output if issues found")
  .action((opts) => {
    let result;

    if (opts.skill) {
      const report = scanSkill(opts.skill);
      result = {
        timestamp: new Date().toISOString(),
        skillsScanned: 1,
        totalFindings: report.findings.length,
        critical: report.findings.filter((f) => f.severity === "critical").length,
        high: report.findings.filter((f) => f.severity === "high").length,
        medium: report.findings.filter((f) => f.severity === "medium").length,
        low: report.findings.filter((f) => f.severity === "low").length,
        skills: [report],
      };
    } else {
      result = runScan();
    }

    if (opts.quiet && result.totalFindings === 0) {
      process.exit(0);
    }

    if (!opts.verbose) {
      // Filter out low findings for default view
      for (const skill of result.skills) {
        skill.findings = skill.findings.filter((f) => f.severity !== "low");
      }
      result.low = 0;
      result.totalFindings = result.skills.reduce((sum, s) => sum + s.findings.length, 0);
    }

    if (opts.json) {
      console.log(formatJson(result));
    } else {
      printReport(result);
    }

    // Exit code: 2 for critical, 1 for high, 0 otherwise
    if (result.critical > 0) process.exit(2);
    if (result.high > 0) process.exit(1);
    process.exit(0);
  });

program
  .command("paths")
  .description("Show default skill directories being scanned")
  .action(() => {
    const paths = getDefaultSkillPaths();
    console.log(`Found ${paths.length} skill directories:\n`);
    for (const p of paths) {
      console.log(`  ${p}`);
    }
  });

program.parse();
