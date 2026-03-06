# Invoice Generation

## Required Invoice Fields (EU)

| Field | Description | Example |
|-------|-------------|---------|
| Invoice number | Sequential, no gaps | INV-2024-0042 |
| Issue date | Date invoice created | 2024-03-15 |
| Due date | Payment deadline | 2024-04-15 |
| Seller details | Name, address, VAT ID | Acme Ltd, VAT: IE1234567A |
| Buyer details | Name, address, VAT ID (B2B) | Client Co, VAT: DE123456789 |
| Line items | Description, qty, unit price | "Pro Plan - Mar 2024", 1, €99.00 |
| VAT breakdown | Rate, base, amount per rate | 21%: Base €99.00, VAT €20.79 |
| Total | Net + VAT | €119.79 |

## Sequential Numbering

```typescript
async function getNextInvoiceNumber(): Promise<string> {
  const year = new Date().getFullYear();
  
  const result = await db.$transaction(async (tx) => {
    const counter = await tx.invoiceCounter.upsert({
      where: { year },
      update: { lastNumber: { increment: 1 } },
      create: { year, lastNumber: 1 }
    });
    return counter.lastNumber;
  });
  
  return `INV-${year}-${String(result).padStart(5, '0')}`;
}
```

## B2B vs B2C Tax Handling

```typescript
function calculateTax(amount: number, buyer: Buyer, seller: Seller): TaxResult {
  // Same country
  if (buyer.countryCode === seller.countryCode) {
    return { rate: seller.defaultVatRate, type: 'domestic' };
  }
  
  // EU B2B with valid VAT
  if (isEU(buyer.countryCode) && isEU(seller.countryCode) && buyer.vatNumber) {
    const valid = await validateVATNumber(buyer.vatNumber);
    if (valid) {
      return { rate: 0, type: 'intracomunitario', reverseCharge: true };
    }
  }
  
  // EU B2C - charge buyer's country VAT (for digital services)
  if (isEU(buyer.countryCode) && seller.sellsDigitalServices) {
    return { rate: getVATRate(buyer.countryCode), type: 'moss' };
  }
  
  // Non-EU - typically no VAT
  return { rate: 0, type: 'export' };
}
```

## Payment Reminder Schedule

| Days overdue | Action |
|--------------|--------|
| 0 | Invoice sent |
| 7 | Friendly reminder |
| 15 | Second reminder, mention late fees |
| 30 | Final notice, service suspension warning |
| 45 | Service suspended, collection process |

**Important**: Check contract terms. "Net 30" means no reminders before day 30.

## Dunning Email Templates

```typescript
const dunningTemplates = {
  reminder_7: {
    subject: 'Invoice #{number} - Friendly Reminder',
    tone: 'friendly',
    includePayLink: true
  },
  reminder_15: {
    subject: 'Invoice #{number} - Second Notice',
    tone: 'firm',
    mentionLateFees: true,
    includePayLink: true
  },
  final_30: {
    subject: 'Invoice #{number} - Final Notice Before Service Suspension',
    tone: 'urgent',
    mentionSuspension: true,
    includePayLink: true
  }
};
```

## PDF Generation Checklist

- [ ] Invoice number prominently displayed
- [ ] Both parties' full legal details
- [ ] Clear line item breakdown
- [ ] Tax calculation visible and correct
- [ ] Payment instructions (bank details, payment link)
- [ ] Terms and conditions reference
- [ ] For intracomunitario: "Reverse charge" statement
