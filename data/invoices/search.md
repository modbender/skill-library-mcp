# Search and Reporting

## Natural Language Queries

Support these patterns:

### By Provider
- "facturas de Hetzner"
- "todo lo de AWS"
- "invoices from Google"

### By Date
- "facturas de enero"
- "invoices from last quarter"
- "this year's invoices"
- "facturas de 2025"

### By Amount
- "facturas de más de 500€"
- "invoices over 1000"
- "facturas entre 100 y 200"

### By Status
- "facturas pendientes de pago"
- "paid invoices"
- "overdue invoices"

### By Category
- "gastos de hosting"
- "software expenses"
- "todas las facturas de seguros"

### Combined
- "facturas de Hetzner de más de 50€ en 2025"
- "unpaid invoices from last month"

---

## Reports

### Monthly Summary
```
📊 February 2026 Summary

Total invoices: 23
Total amount: €2,847.50

By category:
• Hosting: €890.00 (5 invoices)
• Software: €450.00 (8 invoices)
• Professional: €1,200.00 (2 invoices)
• Other: €307.50 (8 invoices)

Payment status:
• Paid: 18 (€2,100.00)
• Pending: 5 (€747.50)
```

### Quarterly Tax Report
```
📋 Q1 2026 Tax Summary (Spain - Modelo 303)

Base imponible: €12,450.00
IVA soportado:
• 21%: €2,180.00
• 10%: €120.00
• 4%: €15.00
Total IVA: €2,315.00

⚠️ Missing invoices for deduction:
• February telecom (usually €45)
```

### Provider Analysis
```
📈 Hetzner - 12 months

Total spend: €1,068.00
Monthly average: €89.00
Trend: +5% vs last year

Invoices:
• INV-12340 (Jan): €89.00
• INV-12345 (Feb): €89.00
...
```

### Annual Summary (for accountant)
```
📁 2025 Annual Export

Generating:
• invoices_2025.csv (147 records)
• invoices_2025.zip (all PDFs)
• providers_2025.json (summary by provider)

Ready to send to accountant.
```

---

## Export Formats

### CSV (Standard)
```csv
date,provider,invoice_number,subtotal,tax_rate,tax_amount,total,currency,category,status
2026-02-13,Hetzner,INV-12345,75.21,19,14.29,89.50,EUR,hosting,paid
```

### Modelo 303 (Spain)
Grouped by tax rate, ready for quarterly VAT declaration.

### Full Archive
ZIP with folder structure + CSV index.
