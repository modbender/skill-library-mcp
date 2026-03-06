# Tax Compliance

## EU VAT Scenarios

| Seller | Buyer | Buyer VAT Valid | VAT Charged | Notes |
|--------|-------|-----------------|-------------|-------|
| Spain | Spain B2B | — | 21% Spain | Domestic |
| Spain | Spain B2C | — | 21% Spain | Domestic |
| Spain | Germany B2B | ✓ | 0% | Intracomunitario, reverse charge |
| Spain | Germany B2B | ✗ | 21% Spain | Treat as B2C |
| Spain | Germany B2C | — | 19% Germany | MOSS for digital services |
| Spain | USA B2B | — | 0% | Export |
| Spain | USA B2C | — | 0% | Export |

## VAT Number Validation

```typescript
import { checkVAT, countries } from 'jsvat';

async function validateVATNumber(vatNumber: string): Promise<ValidationResult> {
  // Format check
  const result = checkVAT(vatNumber, countries);
  if (!result.isValid) {
    return { valid: false, reason: 'Invalid format' };
  }
  
  // VIES API check (EU official database)
  const viesResult = await fetch(
    `https://ec.europa.eu/taxation_customs/vies/rest-api/check-vat-number`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        countryCode: result.country?.isoCode.short,
        vatNumber: result.value
      })
    }
  ).then(r => r.json());
  
  return {
    valid: viesResult.valid,
    name: viesResult.name,
    address: viesResult.address
  };
}
```

## Spanish Tax Obligations (Autónomos)

| Tax | Model | Frequency | Deadline |
|-----|-------|-----------|----------|
| IVA | 303 | Quarterly | 20th of Apr/Jul/Oct, 30th Jan |
| IRPF | 130 | Quarterly | Same as IVA |
| Resumen IVA | 390 | Annual | 30th Jan |
| Operaciones intracom. | 349 | Quarterly/Monthly | 20th following |

## Retention (Spain)

| Type | Rate | Applies To |
|------|------|------------|
| IRPF Professional | 15% | Invoices to companies as autónomo |
| IRPF Reduced | 7% | First 3 years of activity |
| IRPF Artists | 15% or 7% | Artistic work |
| None | 0% | Invoices to individuals, SL to SL |

**Important**: Retentions apply when autónomo invoices to a company, NOT when an SL invoices.

## US Sales Tax

- Varies by state (0% to 10%+)
- Physical presence OR economic nexus triggers obligation
- Digital services increasingly taxed
- Use Stripe Tax, TaxJar, or Avalara for automation

```typescript
// Stripe Tax automation
const session = await stripe.checkout.sessions.create({
  // ...
  automatic_tax: { enabled: true },
  customer_update: {
    address: 'auto', // Collect address for tax calculation
    shipping: 'auto'
  }
});
```

## Invoice Requirements by Region

### EU
- Sequential numbering (no gaps)
- VAT number of both parties (B2B)
- VAT breakdown by rate
- "Reverse charge" text for intracomunitario

### US
- No strict format requirements
- Sales tax shown separately
- Business address

### UK (Post-Brexit)
- Treated as non-EU for VAT
- UK VAT registration if selling B2C over £70k
- "Zero rated export" for B2B

## Record Keeping

| Document | Retention (Spain) | Retention (EU avg) |
|----------|-------------------|-------------------|
| Issued invoices | 6 years | 5-10 years |
| Received invoices | 6 years | 5-10 years |
| Tax declarations | 6 years | 5-10 years |
| Contracts | 6 years | 5-10 years |
