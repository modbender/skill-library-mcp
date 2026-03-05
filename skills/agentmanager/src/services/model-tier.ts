import type { BudgetLevel, Plan, TaskSpec } from '../types.js';

export type ModelTier = 'cheap' | 'standard' | 'premium';
export type TierPriceTable = Record<ModelTier, number>;

const TierOrder: ModelTier[] = ['cheap', 'standard', 'premium'];

const baseAgentTier: Record<TaskSpec['agent'], ModelTier> = {
  triage: 'cheap',
  planner: 'standard',
  executor: 'cheap',
  verifier: 'premium'
};

const budgetCap: Record<BudgetLevel, ModelTier> = {
  cheap: 'standard',
  normal: 'premium',
  thorough: 'premium'
};

const modelNameByTier: Record<ModelTier, string> = {
  cheap: 'gpt-lite',
  standard: 'gpt-standard',
  premium: 'gpt-premium'
};

export const defaultTierPricePerToken: TierPriceTable = {
  cheap: 0.000001,
  standard: 0.000003,
  premium: 0.000008
};

export const capTier = (desired: ModelTier, cap: ModelTier): ModelTier => (TierOrder.indexOf(desired) <= TierOrder.indexOf(cap) ? desired : cap);

export const initialTierForTask = (task: TaskSpec, budgetLevel: BudgetLevel, ownerCap: ModelTier): ModelTier => {
  const desired = baseAgentTier[task.agent];
  return capTier(desired, capTier(budgetCap[budgetLevel], ownerCap));
};

export const upgradeTier = (tier: ModelTier, cap: ModelTier): ModelTier | null => {
  const i = TierOrder.indexOf(tier);
  if (i === TierOrder.length - 1) return null;
  const next = TierOrder[i + 1];
  return TierOrder.indexOf(next) <= TierOrder.indexOf(cap) ? next : null;
};

export const downgradeTier = (tier: ModelTier): ModelTier | null => {
  const i = TierOrder.indexOf(tier);
  if (i === 0) return null;
  return TierOrder[i - 1];
};

export const modelName = (tier: ModelTier): string => modelNameByTier[tier];

export const estimateCost = (tokens: number, tier: ModelTier, pricing: TierPriceTable): number => Number((tokens * pricing[tier]).toFixed(6));

export const inferTokens = (input: string, outputHint = 100): number => Math.max(32, Math.ceil(input.length / 4) + outputHint);

export const applyTierToPlan = (plan: Plan, budgetLevel: BudgetLevel, ownerCap: ModelTier): Plan => ({
  ...plan,
  tasks: plan.tasks.map((task) => {
    const tier = initialTierForTask(task, budgetLevel, ownerCap);
    return { ...task, model: modelName(tier) };
  })
});
