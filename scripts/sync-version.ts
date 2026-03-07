#!/usr/bin/env tsx
/**
 * Syncs version from package.json into .claude-plugin/plugin.json and marketplace.json.
 * Run automatically as part of the build step.
 */

import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const root = join(import.meta.dirname, "..");
const pkg = JSON.parse(readFileSync(join(root, "package.json"), "utf-8"));
const version = pkg.version;

const files = [
  join(root, ".claude-plugin", "plugin.json"),
  join(root, ".claude-plugin", "marketplace.json"),
];

for (const file of files) {
  const content = JSON.parse(readFileSync(file, "utf-8"));
  if (content.version !== version) {
    content.version = version;
    writeFileSync(file, JSON.stringify(content, null, 2) + "\n");
    console.log(`Updated ${file} → ${version}`);
  }

  // Also update version in plugins array entries (marketplace.json)
  if (content.plugins) {
    for (const plugin of content.plugins) {
      if (plugin.version && plugin.version !== version) {
        plugin.version = version;
        writeFileSync(file, JSON.stringify(content, null, 2) + "\n");
        console.log(`Updated plugin entry in ${file} → ${version}`);
      }
    }
  }
}
