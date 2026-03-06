# StripeMeter Pricing Simulator - Getting Started

The StripeMeter Pricing Simulator is a powerful tool that helps you test different pricing strategies, validate billing logic, and optimize your revenue models before deploying to production. This guide will help you understand how to use the simulator effectively.

## What is the Pricing Simulator?

The simulator allows you to:
- **Test pricing models** (tiered, volume, graduated) with realistic usage data
- **Compare revenue outcomes** between different pricing strategies
- **Validate billing accuracy** before customers see their bills
- **Simulate complex scenarios** including credits, commitments, and adjustments
- **Optimize pricing** for different customer segments

## Quick Start

### 1. Basic Invoice Simulation

```typescript
import { InvoiceSimulator } from '@stripemeter/pricing-lib';

const simulator = new InvoiceSimulator();

// Define your usage and pricing
const simulationInput = {
  customerId: 'cust_123',
  periodStart: '2024-01-01',
  periodEnd: '2024-02-01',
  usageItems: [
    {
      metric: 'api_calls',
      quantity: 15000,
      priceConfig: {
        model: 'tiered',
        currency: 'USD',
        tiers: [
          { upTo: 1000, unitPrice: 0.10 },    // $0.10 for first 1,000
          { upTo: 10000, unitPrice: 0.08 },   // $0.08 for next 9,000
          { upTo: null, unitPrice: 0.05 }     // $0.05 for everything above
        ]
      }
    }
  ]
};

// Run the simulation
const invoice = simulator.simulate(simulationInput);
console.log(`Total bill: $${invoice.total}`);
```

### 2. Compare Pricing Models

```typescript
const usage = 15000; // API calls

const pricingModels = {
  tiered: {
    model: 'tiered',
    currency: 'USD',
    tiers: [
      { upTo: 1000, unitPrice: 0.10 },
      { upTo: 10000, unitPrice: 0.08 },
      { upTo: null, unitPrice: 0.05 }
    ]
  },
  volume: {
    model: 'volume',
    currency: 'USD',
    tiers: [
      { upTo: 1000, unitPrice: 0.10 },
      { upTo: 10000, unitPrice: 0.08 },
      { upTo: null, unitPrice: 0.05 }
    ]
  },
  graduated: {
    model: 'graduated',
    currency: 'USD',
    tiers: [
      { upTo: 1000, flatPrice: 50, unitPrice: 0.05 },
      { upTo: 10000, flatPrice: 100, unitPrice: 0.03 },
      { upTo: null, flatPrice: 200, unitPrice: 0.01 }
    ]
  }
};

// Compare results
Object.entries(pricingModels).forEach(([modelName, config]) => {
  const result = simulator.simulate({
    customerId: 'cust_123',
    periodStart: '2024-01-01',
    periodEnd: '2024-02-01',
    usageItems: [{ metric: 'api_calls', quantity: usage, priceConfig: config }]
  });
  console.log(`${modelName}: $${result.total}`);
});
```

## Pricing Model Types

### Tiered Pricing
Each unit is priced according to the tier it falls into.

```typescript
const tieredConfig = {
  model: 'tiered',
  currency: 'USD',
  tiers: [
    { upTo: 1000, unitPrice: 0.10 },    // First 1,000 units at $0.10
    { upTo: 10000, unitPrice: 0.08 },   // Next 9,000 units at $0.08
    { upTo: null, unitPrice: 0.05 }     // All remaining at $0.05
  ]
};

// 15,000 units = (1,000 × $0.10) + (9,000 × $0.08) + (5,000 × $0.05) = $1,070
```

### Volume Pricing
All units are priced at the rate of the tier they reach.

```typescript
const volumeConfig = {
  model: 'volume',
  currency: 'USD',
  tiers: [
    { upTo: 1000, unitPrice: 0.10 },
    { upTo: 10000, unitPrice: 0.08 },
    { upTo: null, unitPrice: 0.05 }
  ]
};

// 15,000 units = 15,000 × $0.05 = $750 (lowest applicable rate)
```

### Graduated Pricing
Each tier has a flat fee plus a per-unit rate.

```typescript
const graduatedConfig = {
  model: 'graduated',
  currency: 'USD',
  tiers: [
    { upTo: 1000, flatPrice: 50, unitPrice: 0.05 },
    { upTo: 10000, flatPrice: 100, unitPrice: 0.03 },
    { upTo: null, flatPrice: 200, unitPrice: 0.01 }
  ]
};

// 15,000 units = $200 + (15,000 × $0.01) = $350
```

## Advanced Features

### Credits and Commitments

```typescript
const simulationWithCredits = {
  customerId: 'cust_123',
  periodStart: '2024-01-01',
  periodEnd: '2024-02-01',
  usageItems: [
    {
      metric: 'api_calls',
      quantity: 15000,
      priceConfig: tieredConfig
    }
  ],
  credits: [
    { amount: 100, reason: 'Welcome credit' },
    { amount: 50, reason: 'Referral bonus', expiresAt: '2024-03-01' }
  ],
  commitments: [
    { amount: 500, startDate: '2024-01-01', endDate: '2024-12-31', applied: 0 }
  ],
  taxRate: 8.5 // 8.5% tax
};

const invoice = simulator.simulate(simulationWithCredits);
console.log(`Subtotal: $${invoice.subtotal}`);
console.log(`Credits: -$${invoice.credits}`);
console.log(`Tax: $${invoice.tax}`);
console.log(`Total: $${invoice.total}`);
```

### Multi-Metric Billing

```typescript
const multiMetricSimulation = {
  customerId: 'enterprise_customer',
  periodStart: '2024-01-01',
  periodEnd: '2024-02-01',
  usageItems: [
    {
      metric: 'api_calls',
      quantity: 50000,
      priceConfig: {
        model: 'tiered',
        currency: 'USD',
        tiers: [
          { upTo: 10000, unitPrice: 0.01 },
          { upTo: 100000, unitPrice: 0.008 },
          { upTo: null, unitPrice: 0.005 }
        ]
      }
    },
    {
      metric: 'data_processed_gb',
      quantity: 500,
      priceConfig: {
        model: 'volume',
        currency: 'USD',
        tiers: [
          { upTo: 100, unitPrice: 0.50 },
          { upTo: 1000, unitPrice: 0.40 },
          { upTo: null, unitPrice: 0.30 }
        ]
      }
    },
    {
      metric: 'storage_gb_hours',
      quantity: 8760, // 1 GB for full month
      priceConfig: {
        model: 'flat',
        currency: 'USD',
        unitPrice: 0.02
      }
    }
  ]
};

const invoice = simulator.simulate(multiMetricSimulation);
console.log('Invoice breakdown:');
invoice.lineItems.forEach(item => {
  console.log(`${item.metric}: ${item.quantity} units × $${item.unitPrice} = $${item.subtotal}`);
});
console.log(`Total: $${invoice.total}`);
```

## Real-World Scenarios

See [Pricing Scenarios](./simulator-scenarios.md) for detailed examples including:
- **SaaS API Company** - tiered pricing for different customer segments
- **Data Processing Service** - volume-based pricing with commitments
- **Storage Provider** - graduated pricing with minimum charges
- **Enterprise Platform** - complex multi-metric billing

## Integration with StripeMeter

The simulator uses the same pricing calculations as the live StripeMeter system, ensuring:
- **Billing accuracy** - what you simulate is what customers pay
- **Parity testing** - validate against Stripe invoices
- **Confidence** - deploy pricing changes with certainty

### Testing Against Live Data

```typescript
// Use real usage data from your system
const realUsageData = await getCustomerUsage('cust_123', '2024-01-01', '2024-02-01');

const simulatedInvoice = simulator.simulate({
  customerId: 'cust_123',
  periodStart: '2024-01-01',
  periodEnd: '2024-02-01',
  usageItems: realUsageData.map(usage => ({
    metric: usage.metric,
    quantity: usage.total,
    priceConfig: getPricingConfig(usage.metric)
  }))
});

// Compare with actual Stripe invoice
const stripeInvoice = await stripe.invoices.retrieve('in_...');
const difference = Math.abs(simulatedInvoice.total - stripeInvoice.total);
console.log(`Difference: $${difference} (${(difference/stripeInvoice.total*100).toFixed(2)}%)`);
```

## Best Practices

### 1. Start Simple
- Begin with single-metric, single-tier pricing
- Add complexity gradually as you understand the patterns

### 2. Test Edge Cases
```typescript
const edgeCases = [
  { name: 'Zero usage', quantity: 0 },
  { name: 'Minimum tier', quantity: 1 },
  { name: 'Tier boundary', quantity: 1000 },
  { name: 'High usage', quantity: 1000000 }
];

edgeCases.forEach(testCase => {
  const result = simulator.simulate({
    customerId: testCase.name,
    periodStart: '2024-01-01',
    periodEnd: '2024-02-01',
    usageItems: [{ 
      metric: 'api_calls', 
      quantity: testCase.quantity, 
      priceConfig: tieredConfig 
    }]
  });
  console.log(`${testCase.name}: $${result.total}`);
});
```

### 3. Validate Revenue Impact
```typescript
// Test pricing changes against historical data
const historicalUsage = getHistoricalUsage('last_3_months');
const currentRevenue = calculateRevenue(historicalUsage, currentPricing);
const newRevenue = calculateRevenue(historicalUsage, proposedPricing);

console.log(`Revenue impact: ${((newRevenue - currentRevenue) / currentRevenue * 100).toFixed(1)}%`);
```

### 4. Customer Segment Analysis
```typescript
const segments = ['startup', 'growth', 'enterprise'];

segments.forEach(segment => {
  const segmentUsage = getSegmentUsage(segment);
  const avgBill = calculateAverageBill(segmentUsage, pricingConfig);
  console.log(`${segment}: Average bill $${avgBill}`);
});
```

## Next Steps

1. **Explore Scenarios** - Check out [detailed pricing scenarios](./simulator-scenarios.md)
2. **Set up CI Testing** - Automate pricing validation in your deployment pipeline
3. **Monitor in Production** - Use reconciliation reports to ensure accuracy
4. **Optimize Continuously** - Regular simulation helps optimize pricing strategy

## Need Help?

- 📖 [Full Documentation](../README.md)
- 🐛 [Report Issues](https://github.com/geminimir/stripemeter/issues)
- 💬 [Community Discussions](https://github.com/geminimir/stripemeter/discussions)
- 📧 [Support](mailto:support@stripemeter.io)

## Simulator CLI (sim) quickstart

Use the local CLI to validate scenarios, run them offline using the pricing engine, and report diffs against expected artifacts.

```bash
# Build workspace (first time or after changes)
pnpm build

# Validate all scenarios under examples/
pnpm run sim validate --dir examples

# Run scenarios and write results to results/
pnpm run sim run --dir examples --out results --seed 42

# Record the current results as expected artifacts next to scenarios
pnpm run sim run --dir examples --out results --record

# Diff actual results vs expected and fail on differences
pnpm run sim report --dir examples --results results --fail-on-diff
```

- Scenarios live in `scenarios/` or any folder you specify (see `examples/`).
- Scenario files use `.sim.json` extension and minimally require `metadata`, `inputs.usageItems`, and an `expected.total` to assert.
- You can set per-scenario tolerances via `tolerances.absolute` and `tolerances.relative` for numeric diffs.

Example scenario skeleton:

```json
{
  "metadata": { "name": "tiered-basic", "version": "1" },
  "inputs": {
    "customerId": "cust_1",
    "periodStart": "2024-01-01",
    "periodEnd": "2024-01-31",
    "usageItems": [
      {
        "metric": "requests",
        "quantity": 350,
        "priceConfig": {
          "model": "tiered",
          "currency": "USD",
          "tiers": [
            { "upTo": 100, "unitPrice": 0.1 },
            { "upTo": 500, "unitPrice": 0.08 },
            { "upTo": null, "unitPrice": 0.05 }
          ]
        }
      }
    ]
  },
  "expected": { "total": 28.0 },
  "tolerances": { "absolute": 0.001, "relative": 0.0005 }
}
```

CI runs validate → run → report for `examples/`. Place your own scenarios in `scenarios/` and mirror the same commands locally.
