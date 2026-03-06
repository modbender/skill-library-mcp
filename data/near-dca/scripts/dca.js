#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const CONFIG_DIR = path.join(os.homedir(), '.near-dca');
const PLANS_FILE = path.join(CONFIG_DIR, 'plans.json');

/**
 * Load DCA plans
 */
async function loadPlans() {
  try {
    const data = await fs.readFile(PLANS_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    return [];
  }
}

/**
 * Save DCA plans
 */
async function savePlans(plans) {
  await fs.mkdir(CONFIG_DIR, { recursive: true });
  await fs.writeFile(PLANS_FILE, JSON.stringify(plans, null, 2));
}

/**
 * Create a new DCA plan
 */
async function createPlan(token, amount, schedule, account) {
  const plans = await loadPlans();
  const plan = {
    id: Date.now().toString(),
    token,
    amount,
    schedule,
    account,
    status: 'active',
    created: new Date().toISOString(),
    purchases: []
  };
  plans.push(plan);
  await savePlans(plans);
  return plan;
}

/**
 * List DCA plans
 */
async function listPlans(account) {
  const plans = await loadPlans();
  let filtered = account ? plans.filter(p => p.account === account) : plans;
  return filtered;
}

/**
 * Cancel a DCA plan
 */
async function cancelPlan(planId) {
  const plans = await loadPlans();
  const index = plans.findIndex(p => p.id === planId);
  if (index === -1) {
    throw new Error('Plan not found');
  }
  plans[index].status = 'cancelled';
  plans[index].cancelled = new Date().toISOString();
  await savePlans(plans);
  return plans[index];
}

/**
 * Calculate performance
 */
function calculatePerformance(plan) {
  if (plan.purchases.length === 0) {
    return { avgPrice: 0, totalInvested: 0, totalTokens: 0 };
  }

  const totalInvested = plan.purchases.reduce((sum, p) => sum + p.invested, 0);
  const totalTokens = plan.purchases.reduce((sum, p) => sum + p.tokens, 0);
  const avgPrice = totalTokens > 0 ? totalInvested / totalTokens : 0;

  return { avgPrice, totalInvested, totalTokens };
}

// CLI interface
const command = process.argv[2];
const arg1 = process.argv[3];
const arg2 = process.argv[4];
const arg3 = process.argv[5];
const arg4 = process.argv[6] || process.env.NEAR_ACCOUNT;

async function main() {
  try {
    switch (command) {
      case 'create': {
        if (!arg1 || !arg2 || !arg3) {
          console.error('Error: Token, amount, and schedule required');
          console.error('Usage: near-dca create <token> <amount> <schedule> [account]');
          process.exit(1);
        }
        const account = arg4;
        if (!account) {
          console.error('Error: Account ID required (set NEAR_ACCOUNT or pass as argument)');
          process.exit(1);
        }
        const plan = await createPlan(arg1, arg2, arg3, account);
        console.log(`✅ DCA plan created:`);
        console.log(`   ID: ${plan.id}`);
        console.log(`   Token: ${plan.token}`);
        console.log(`   Amount: ${plan.amount} per purchase`);
        console.log(`   Schedule: ${plan.schedule}`);
        console.log(`   Account: ${plan.account}`);
        console.log(`   Note: Set up cron to execute purchases`);
        break;
      }

      case 'list': {
        const account = arg1 || process.env.NEAR_ACCOUNT;
        const plans = await listPlans(account);
        if (plans.length === 0) {
          console.log('No DCA plans found');
        } else {
          console.log('DCA Plans:');
          console.log('');
          plans.forEach(plan => {
            const perf = calculatePerformance(plan);
            console.log(`  ID: ${plan.id}`);
            console.log(`  Token: ${plan.token} | Amount: ${plan.amount} | Schedule: ${plan.schedule}`);
            console.log(`  Status: ${plan.status} | Purchases: ${plan.purchases.length}`);
            console.log(`  Invested: ${perf.totalInvested} | Tokens: ${perf.totalTokens.toFixed(4)} | Avg Price: ${perf.avgPrice.toFixed(4)}`);
            console.log('');
          });
        }
        break;
      }

      case 'cancel': {
        if (!arg1) {
          console.error('Error: Plan ID required');
          console.error('Usage: near-dca cancel <plan_id>');
          process.exit(1);
        }
        const plan = await cancelPlan(arg1);
        console.log(`✅ Cancelled DCA plan ${arg1}`);
        break;
      }

      case 'performance': {
        if (!arg1) {
          console.error('Error: Plan ID required');
          console.error('Usage: near-dca performance <plan_id>');
          process.exit(1);
        }
        const plans = await loadPlans();
        const plan = plans.find(p => p.id === arg1);
        if (!plan) {
          console.error('Plan not found');
          process.exit(1);
        }
        const perf = calculatePerformance(plan);
        console.log(`DCA Performance for plan ${arg1}:`);
        console.log(`  Total Invested: ${perf.totalInvested} ${plan.token}`);
        console.log(`  Total Tokens: ${perf.totalTokens.toFixed(4)} NEAR`);
        console.log(`  Average Price: ${perf.avgPrice.toFixed(4)} ${plan.token}/NEAR`);
        console.log(`  Number of Purchases: ${plan.purchases.length}`);
        break;
      }

      case 'history': {
        if (!arg1) {
          console.error('Error: Plan ID required');
          console.error('Usage: near-dca history <plan_id>');
          process.exit(1);
        }
        const plans = await loadPlans();
        const plan = plans.find(p => p.id === arg1);
        if (!plan) {
          console.error('Plan not found');
          process.exit(1);
        }
        console.log(`Purchase History for plan ${arg1}:`);
        plan.purchases.forEach(p => {
          console.log(`  ${p.date}: ${p.tokens} NEAR for ${p.invested} ${plan.token} (${p.price})`);
        });
        break;
      }

      default:
        console.log('NEAR DCA (Dollar-Cost Averaging)');
        console.log('');
        console.log('Commands:');
        console.log('  create <token> <amt> <sched> [acc]  Create DCA plan');
        console.log('  list [account]                    List DCA plans');
        console.log('  cancel <plan_id>                  Cancel plan');
        console.log('  performance <plan_id>             Show performance');
        console.log('  history <plan_id>                 Show purchase history');
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
