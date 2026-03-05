import fs from "node:fs";
import YAML from "yaml";
import { z } from "zod";

const SkillConfigSchema = z.object({
  skill_name: z.string(),
  chain: z.string(),
  sources: z.any(),
  bags: z.any(),
  smart_wallets: z.any(),
  risk_budget_split: z.any(),
  risk_gates: z.any(),
  copy_trade_rules: z.any(),
  ai_signal: z.any(),
  portfolio: z.any(),
  exits: z.any(),
  rug_alarms: z.any(),
  execution: z.any(),
});

export type SkillConfig = z.infer<typeof SkillConfigSchema>;

export function loadConfig(path = "config/skill.yaml"): SkillConfig {
  const raw = fs.readFileSync(path, "utf-8");
  const parsed = YAML.parse(raw);
  return SkillConfigSchema.parse(parsed);
}

export function loadSmartWallets(path = "config/smart_wallets.json"): { wallets: { address: string; label?: string }[] } {
  const raw = fs.readFileSync(path, "utf-8");
  return JSON.parse(raw);
}
