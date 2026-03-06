#!/usr/bin/env node
/**
 * Interactive demo: login, pick a project, create a task via freedcamp.mjs
 *
 * Usage:  node skill/scripts/demo.mjs
 *
 * Loads .env from project root automatically if env vars aren't set.
 */

import { execFileSync } from "node:child_process";
import { createInterface } from "node:readline/promises";
import { fileURLToPath } from "node:url";
import fs from "node:fs";
import path from "node:path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../..");
const FC_SCRIPT = path.join(__dirname, "freedcamp.mjs");

// Load .env if needed
function loadEnv() {
  if (process.env.FREEDCAMP_API_KEY && process.env.FREEDCAMP_API_SECRET) return;
  const envFile = path.join(ROOT, ".env");
  if (!fs.existsSync(envFile)) return;
  for (const line of fs.readFileSync(envFile, "utf-8").split("\n")) {
    const match = line.match(/^(?:export\s+)?(\w+)=(.+)$/);
    if (match) process.env[match[1]] = match[2].replace(/^["']|["']$/g, "");
  }
}

loadEnv();

const rl = createInterface({ input: process.stdin, output: process.stdout });
const ask = (q) => rl.question(q);

function fc(...args) {
  const out = execFileSync("node", [FC_SCRIPT, ...args], {
    encoding: "utf-8",
    env: process.env,
  });
  return JSON.parse(out.trim());
}

try {
  // 1. Login
  console.log("\nLogging in...");
  const me = fc("me");
  console.log(`  User ID: ${me.user_id}  |  ${me.projects_count} projects, ${me.groups_count} groups\n`);

  // 2. List projects, let user pick
  const groups = fc("groups-projects");
  const projects = groups.flatMap(g =>
    (g.projects || []).map(p => ({ ...p, group: g.name }))
  );

  if (projects.length === 0) {
    console.log("No projects found.");
    process.exit(1);
  }

  console.log("Projects:");
  projects.forEach((p, i) => {
    console.log(`  [${i + 1}] ${p.project_name}  (group: ${p.group})`);
  });

  const choice = await ask(`\nPick a project [1-${projects.length}]: `);
  const idx = Number(choice) - 1;
  if (idx < 0 || idx >= projects.length) {
    console.log("Invalid choice.");
    process.exit(1);
  }
  const project = projects[idx];
  console.log(`  -> ${project.project_name}\n`);

  // 3. Task details
  const title = await ask("Task title: ");
  if (!title.trim()) {
    console.log("Title is required.");
    process.exit(1);
  }
  const description = await ask("Description (enter to skip): ");

  // 4. Create
  console.log("\nCreating task...");
  const args = [
    "create-task",
    "--project", String(project.id),
    "--title", title.trim(),
  ];
  if (description.trim()) args.push("--description", description.trim());

  const result = fc(...args);
  const task = result?.tasks?.[0] || result;

  const taskId = task.id || task.task_id;
  const link = `https://freedcamp.com/view/${project.id}/tasks/${taskId}`;

  console.log("\nTask created:");
  console.log(`  ID:      ${taskId || "n/a"}`);
  console.log(`  Title:   ${task.title || title}`);
  console.log(`  Project: ${project.project_name}`);
  if (task.status !== undefined) console.log(`  Status:  ${task.status}`);
  console.log(`\n  Open:    ${link}`);
} finally {
  rl.close();
}
