# StripeMeter Pricing Simulator - Real-World Scenarios

This guide provides realistic pricing scenarios that demonstrate how to use the StripeMeter simulator for different business models and use cases.

## Scenario 1: SaaS API Company - CloudAPI

**Business Model:** REST API service with tiered pricing for different customer segments.

### Customer Segments
- **Startup**: Free tier with overage charges
- **Growth**: Pro plan with included usage + overages  
- **Enterprise**: High-volume with committed spend

### Pricing Configuration

```typescript
import { InvoiceSimulator } from '@stripemeter/pricing-lib';

const simulator = new InvoiceSimulator();

// Startup tier - Free with overage
const startupPricing = {
  model: 'tiered',
  currency: 'USD',
  tiers: [
    { upTo: 1000, unitPrice: 0.00 },    // Free tier: 1,000 calls
    { upTo: 10000, unitPrice: 0.02 },   // Overage: $0.02 per call
    { upTo: null, unitPrice: 0.015 }    // High volume discount
  ]
};

// Growth tier - Pro plan
const growthPricing = {
  model: 'tiered', 
  currency: 'USD',
  tiers: [
    { upTo: 10000, unitPrice: 0.00 },   // Included in $29 plan
    { upTo: 100000, unitPrice: 0.01 },  // Overage: $0.01 per call
    { upTo: null, unitPrice: 0.008 }    // High volume discount
  ]
};

// Enterprise tier - Volume pricing with commitment
const enterprisePricing = {
  model: 'volume',
  currency: 'USD', 
  tiers: [
    { upTo: 100000, unitPrice: 0.008 },
    { upTo: 500000, unitPrice: 0.006 },
    { upTo: null, unitPrice: 0.004 }
  ]
};
```

### Usage Scenarios

```typescript
const scenarios = [
  {
    name: 'Startup - Light Usage',
    segment: 'startup',
    usage: 500,
    pricing: startupPricing,
    expected: 0 // Free tier
  },
  {
    name: 'Startup - Overage',
    segment: 'startup', 
    usage: 5000,
    pricing: startupPricing,
    expected: 80 // 4,000 × $0.02
  },
  {
    name: 'Growth - Within Plan',
    segment: 'growth',
    usage: 8000,
    pricing: growthPricing,
    expected: 0 // Included in plan
  },
  {
    name: 'Growth - With Overage',
    segment: 'growth',
    usage: 25000,
    pricing: growthPricing,
    expected: 150 // 15,000 × $0.01
  },
  {
    name: 'Enterprise - High Volume',
    segment: 'enterprise',
    usage: 750000,
    pricing: enterprisePricing,
    expected: 3000 // 750,000 × $0.004
  }
];

// Run scenarios
scenarios.forEach(scenario => {
  const result = simulator.simulate({
    customerId: `${scenario.segment}_customer`,
    periodStart: '2024-01-01',
    periodEnd: '2024-02-01',
    usageItems: [{
      metric: 'api_calls',
      quantity: scenario.usage,
      priceConfig: scenario.pricing
    }]
  });
  
  console.log(`${scenario.name}:`);
  console.log(`  Usage: ${scenario.usage.toLocaleString()} API calls`);
  console.log(`  Bill: $${result.total}`);
  console.log(`  Expected: $${scenario.expected}`);
  console.log(`  Match: ${result.total === scenario.expected ? '✅' : '❌'}\n`);
});
```

## Scenario 2: Data Processing Platform - DataFlow

**Business Model:** ETL/data processing service with volume-based pricing and committed spend discounts.

### Pricing Structure

```typescript
const dataProcessingPricing = {
  model: 'volume',
  currency: 'USD',
  tiers: [
    { upTo: 100, unitPrice: 0.50 },     // $0.50 per GB (small jobs)
    { upTo: 1000, unitPrice: 0.35 },    // $0.35 per GB (medium jobs)  
    { upTo: 10000, unitPrice: 0.25 },   // $0.25 per GB (large jobs)
    { upTo: null, unitPrice: 0.15 }     // $0.15 per GB (enterprise)
  ]
};

const storageConfig = {
  model: 'flat',
  currency: 'USD',
  unitPrice: 0.025, // $0.025 per GB-hour
  minimumCharge: 1.00 // Minimum $1/month per customer
};

// Enterprise customer with commitment
const enterpriseCommitment = {
  amount: 5000, // $5,000 committed spend
  startDate: '2024-01-01',
  endDate: '2024-12-31', 
  applied: 2500 // $2,500 already used
};
```

### Multi-Metric Scenario

```typescript
const dataFlowScenario = {
  customerId: 'enterprise_dataflow',
  periodStart: '2024-01-01', 
  periodEnd: '2024-02-01',
  usageItems: [
    {
      metric: 'data_processed_gb',
      quantity: 15000, // 15 TB processed
      priceConfig: dataProcessingPricing
    },
    {
      metric: 'storage_gb_hours', 
      quantity: 744000, // 1 TB stored for full month (744 hours)
      priceConfig: storageConfig
    }
  ],
  commitments: [enterpriseCommitment],
  credits: [
    { amount: 500, reason: 'Migration assistance credit' }
  ]
};

const invoice = simulator.simulate(dataFlowScenario);

console.log('DataFlow Enterprise Customer - January 2024');
console.log('===========================================');
invoice.lineItems.forEach(item => {
  console.log(`${item.metric}: ${item.quantity.toLocaleString()} units × $${item.unitPrice} = $${item.subtotal}`);
});
console.log(`Subtotal: $${invoice.subtotal}`);
console.log(`Commitment Applied: -$${invoice.credits}`);  
console.log(`Final Total: $${invoice.total}`);
```

## Scenario 3: Storage Provider - CloudStore

**Business Model:** Cloud storage with graduated pricing (base fees + usage) and retention tiers.

### Pricing Configuration

```typescript
const storagePricing = {
  hot_storage: {
    model: 'graduated',
    currency: 'USD',
    tiers: [
      { upTo: 100, flatPrice: 5, unitPrice: 0.023 },    // $5 base + $0.023/GB
      { upTo: 1000, flatPrice: 15, unitPrice: 0.021 },  // $15 base + $0.021/GB  
      { upTo: null, flatPrice: 50, unitPrice: 0.018 }   // $50 base + $0.018/GB
    ]
  },
  cold_storage: {
    model: 'graduated',
    currency: 'USD', 
    tiers: [
      { upTo: 1000, flatPrice: 2, unitPrice: 0.008 },   // $2 base + $0.008/GB
      { upTo: 10000, flatPrice: 8, unitPrice: 0.006 },  // $8 base + $0.006/GB
      { upTo: null, flatPrice: 25, unitPrice: 0.004 }   // $25 base + $0.004/GB
    ]
  },
  archive_storage: {
    model: 'flat',
    currency: 'USD',
    unitPrice: 0.001 // $0.001/GB - cheap but slow retrieval
  },
  data_retrieval: {
    model: 'tiered',
    currency: 'USD',
    tiers: [
      { upTo: 10, unitPrice: 0.00 },      // 10 GB free retrieval
      { upTo: 100, unitPrice: 0.05 },     // $0.05/GB 
      { upTo: null, unitPrice: 0.03 }     // $0.03/GB bulk
    ]
  }
};
```

### Customer Usage Patterns

```typescript
const storageScenarios = [
  {
    name: 'Small Business',
    usage: {
      hot_storage: 50,      // 50 GB hot storage
      cold_storage: 200,    // 200 GB cold storage  
      archive_storage: 0,   // No archive
      data_retrieval: 5     // 5 GB retrieval (free)
    }
  },
  {
    name: 'Growing Startup',
    usage: {
      hot_storage: 500,     // 500 GB hot
      cold_storage: 2000,   // 2 TB cold
      archive_storage: 5000, // 5 TB archive
      data_retrieval: 50    // 50 GB retrieval
    }
  },
  {
    name: 'Enterprise',
    usage: {
      hot_storage: 5000,    // 5 TB hot
      cold_storage: 25000,  // 25 TB cold
      archive_storage: 100000, // 100 TB archive
      data_retrieval: 200   // 200 GB retrieval
    }
  }
];

// Calculate bills for each scenario
storageScenarios.forEach(scenario => {
  const usageItems = Object.entries(scenario.usage).map(([metric, quantity]) => ({
    metric,
    quantity,
    priceConfig: storagePricing[metric]
  }));
  
  const invoice = simulator.simulate({
    customerId: scenario.name.toLowerCase().replace(' ', '_'),
    periodStart: '2024-01-01',
    periodEnd: '2024-02-01', 
    usageItems
  });
  
  console.log(`${scenario.name} Storage Bill:`);
  console.log(`Total: $${invoice.total}`);
  
  // Show breakdown
  invoice.lineItems.forEach(item => {
    const usage = scenario.usage[item.metric];
    console.log(`  ${item.metric}: ${usage} GB = $${item.subtotal}`);
  });
  console.log('');
});
```

## Scenario 4: Enterprise Platform - WorkflowCloud  

**Business Model:** Complex enterprise platform with multiple pricing dimensions and custom contracts.

### Multi-Dimensional Pricing

```typescript
const workflowPricing = {
  compute_hours: {
    model: 'tiered',
    currency: 'USD',
    tiers: [
      { upTo: 100, unitPrice: 0.50 },    // Dev/test workloads
      { upTo: 1000, unitPrice: 0.35 },   // Production workloads
      { upTo: null, unitPrice: 0.25 }    // Enterprise scale
    ]
  },
  active_workflows: {
    model: 'graduated', 
    currency: 'USD',
    tiers: [
      { upTo: 10, flatPrice: 0, unitPrice: 0 },        // Free tier
      { upTo: 100, flatPrice: 50, unitPrice: 2.00 },   // Professional
      { upTo: null, flatPrice: 200, unitPrice: 1.50 }  // Enterprise
    ]
  },
  api_requests: {
    model: 'volume',
    currency: 'USD', 
    tiers: [
      { upTo: 100000, unitPrice: 0.0001 },   // $0.10 per 1K requests
      { upTo: 1000000, unitPrice: 0.00008 }, // Volume discount
      { upTo: null, unitPrice: 0.00005 }     // Enterprise rate
    ]
  },
  data_transfer_gb: {
    model: 'tiered',
    currency: 'USD',
    tiers: [
      { upTo: 100, unitPrice: 0.09 },     // First 100 GB
      { upTo: 1000, unitPrice: 0.085 },   // Next 900 GB  
      { upTo: null, unitPrice: 0.08 }     // Above 1 TB
    ]
  }
};
```

### Enterprise Contract Simulation

```typescript
const enterpriseContract = {
  customerId: 'acme_corp',
  periodStart: '2024-01-01',
  periodEnd: '2024-02-01',
  usageItems: [
    {
      metric: 'compute_hours',
      quantity: 5000,
      priceConfig: workflowPricing.compute_hours
    },
    {
      metric: 'active_workflows', 
      quantity: 250,
      priceConfig: workflowPricing.active_workflows
    },
    {
      metric: 'api_requests',
      quantity: 2500000,
      priceConfig: workflowPricing.api_requests
    },
    {
      metric: 'data_transfer_gb',
      quantity: 1500,
      priceConfig: workflowPricing.data_transfer_gb
    }
  ],
  commitments: [
    {
      amount: 10000, // $10K annual commitment
      startDate: '2024-01-01',
      endDate: '2024-12-31',
      applied: 0 // First month
    }
  ],
  credits: [
    { amount: 1000, reason: 'Migration support' },
    { amount: 500, reason: 'Q1 promotion' }
  ],
  taxRate: 0 // Enterprise - tax handled separately
};

const enterpriseInvoice = simulator.simulate(enterpriseContract);

console.log('ACME Corp - Enterprise Contract');
console.log('==============================');
console.log(`Period: ${enterpriseContract.periodStart} to ${enterpriseContract.periodEnd}`);
console.log('');

console.log('Usage Breakdown:');
enterpriseInvoice.lineItems.forEach(item => {
  console.log(`${item.metric.replace('_', ' ').toUpperCase()}:`);
  console.log(`  Quantity: ${item.quantity.toLocaleString()}`);
  console.log(`  Rate: $${item.unitPrice}`);
  console.log(`  Subtotal: $${item.subtotal}`);
  console.log('');
});

console.log('Billing Summary:');
console.log(`Subtotal: $${enterpriseInvoice.subtotal}`);
console.log(`Credits Applied: -$${enterpriseInvoice.credits}`);
console.log(`Commitment Applied: $${Math.min(enterpriseInvoice.total, 10000/12).toFixed(2)}`);
console.log(`Total Due: $${enterpriseInvoice.total}`);
```

## Scenario 5: Pricing Optimization Study

**Goal:** Compare different pricing strategies to maximize revenue while maintaining customer satisfaction.

### A/B Testing Different Models

```typescript
const usagePatterns = [
  { segment: 'small', avgUsage: 2500, customers: 1000 },
  { segment: 'medium', avgUsage: 15000, customers: 500 },
  { segment: 'large', avgUsage: 75000, customers: 100 },
  { segment: 'enterprise', avgUsage: 300000, customers: 20 }
];

const pricingOptions = {
  current: {
    model: 'tiered',
    tiers: [
      { upTo: 5000, unitPrice: 0.01 },
      { upTo: 50000, unitPrice: 0.008 },
      { upTo: null, unitPrice: 0.005 }
    ]
  },
  option_a: {
    model: 'volume', 
    tiers: [
      { upTo: 5000, unitPrice: 0.012 },
      { upTo: 50000, unitPrice: 0.009 },
      { upTo: null, unitPrice: 0.006 }
    ]
  },
  option_b: {
    model: 'graduated',
    tiers: [
      { upTo: 10000, flatPrice: 25, unitPrice: 0.005 },
      { upTo: 100000, flatPrice: 100, unitPrice: 0.003 },
      { upTo: null, flatPrice: 400, unitPrice: 0.002 }
    ]
  }
};

// Revenue analysis
console.log('Pricing Strategy Analysis');
console.log('========================');

Object.entries(pricingOptions).forEach(([strategyName, pricing]) => {
  let totalRevenue = 0;
  
  console.log(`\n${strategyName.toUpperCase()} Strategy:`);
  
  usagePatterns.forEach(pattern => {
    const invoice = simulator.simulate({
      customerId: pattern.segment,
      periodStart: '2024-01-01',
      periodEnd: '2024-02-01',
      usageItems: [{
        metric: 'api_calls',
        quantity: pattern.avgUsage,
        priceConfig: { model: pricing.model, currency: 'USD', tiers: pricing.tiers }
      }]
    });
    
    const segmentRevenue = invoice.total * pattern.customers;
    totalRevenue += segmentRevenue;
    
    console.log(`  ${pattern.segment}: $${invoice.total} × ${pattern.customers} = $${segmentRevenue.toLocaleString()}`);
  });
  
  console.log(`  TOTAL MONTHLY REVENUE: $${totalRevenue.toLocaleString()}`);
});
```

## Testing Best Practices

### 1. Edge Case Testing

```typescript
const edgeCases = [
  { name: 'Zero usage', quantity: 0 },
  { name: 'Exact tier boundary', quantity: 1000 },
  { name: 'Just over boundary', quantity: 1001 },
  { name: 'Fractional usage', quantity: 999.99 },
  { name: 'Very high usage', quantity: 10000000 }
];

edgeCases.forEach(testCase => {
  const result = simulator.simulate({
    customerId: 'test',
    periodStart: '2024-01-01',
    periodEnd: '2024-02-01',
    usageItems: [{
      metric: 'api_calls',
      quantity: testCase.quantity,
      priceConfig: tieredPricing
    }]
  });
  console.log(`${testCase.name}: $${result.total}`);
});
```

### 2. Consistency Validation

```typescript
// Ensure pricing is monotonic (more usage = higher or equal cost)
const quantities = [0, 100, 1000, 5000, 10000, 50000, 100000];

quantities.forEach((quantity, index) => {
  if (index === 0) return;
  
  const current = simulator.simulate({
    customerId: 'test',
    periodStart: '2024-01-01', 
    periodEnd: '2024-02-01',
    usageItems: [{ metric: 'test', quantity, priceConfig: tieredPricing }]
  });
  
  const previous = simulator.simulate({
    customerId: 'test',
    periodStart: '2024-01-01',
    periodEnd: '2024-02-01', 
    usageItems: [{ metric: 'test', quantity: quantities[index-1], priceConfig: tieredPricing }]
  });
  
  if (current.total < previous.total) {
    console.error(`❌ Pricing inconsistency: ${quantity} usage costs less than ${quantities[index-1]}`);
  }
});
```

## Integration with CI/CD

```typescript
// Example test for automated pricing validation
describe('Pricing Regression Tests', () => {
  test('Known customer scenarios should maintain expected costs', () => {
    const knownScenarios = [
      { usage: 1000, expectedCost: 10.00 },
      { usage: 5000, expectedCost: 42.00 },
      { usage: 20000, expectedCost: 146.00 }
    ];
    
    knownScenarios.forEach(scenario => {
      const result = simulator.simulate({
        customerId: 'regression_test',
        periodStart: '2024-01-01',
        periodEnd: '2024-02-01',
        usageItems: [{
          metric: 'api_calls',
          quantity: scenario.usage,
          priceConfig: productionPricing
        }]
      });
      
      expect(result.total).toBeCloseTo(scenario.expectedCost, 2);
    });
  });
});
```

These scenarios demonstrate how the StripeMeter pricing simulator can be used to test, validate, and optimize pricing strategies across different business models and customer segments.
