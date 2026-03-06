# Legal Requirements for Invoice Storage

## Retention Periods

| Country | Period | Notes |
|---------|--------|-------|
| Spain | 4 years | From end of tax year |
| Germany | 10 years | For VAT invoices |
| France | 6 years | General commercial |
| UK | 6 years | VAT records |
| USA | 3-7 years | Varies by state/type |

**Default:** Keep everything for 10 years. Storage is cheap, audits are expensive.

---

## Spain Specifics

### Required Invoice Fields (RD 1619/2012)

For invoice to be valid for VAT deduction:
- Número de factura (correlativo)
- Fecha de expedición
- Nombre/razón social emisor
- NIF/CIF emisor
- Domicilio emisor
- Descripción operación
- Base imponible
- Tipo impositivo (% IVA)
- Cuota tributaria (IVA en €)
- Total factura

### IVA Types
| Rate | Applies to |
|------|------------|
| 21% | General (most services/products) |
| 10% | Reduced (food, transport, hotels) |
| 4% | Super-reduced (bread, books, medicine) |
| 0% | Exempt (insurance, finance, health) |

### Deductibility Rules
- Must have valid invoice (not just receipt)
- Must be necessary for business activity
- Must be registered in accounting
- Proportional deduction for mixed use (e.g., home office)

---

## Quarterly Obligations (Spain)

| Model | Deadline | What |
|-------|----------|------|
| 303 | 1-20 Apr/Jul/Oct, 1-30 Jan | Quarterly VAT |
| 347 | February | Annual ops >3,005.06€ per provider |
| 390 | January | Annual VAT summary |

### Modelo 303 Preparation

Agent should track and provide:
- Sum of bases by IVA type (21%, 10%, 4%)
- Sum of IVA soportado (paid, deductible)
- Comparison with previous quarters

---

## GDPR Considerations

- Invoices may contain personal data
- Don't share invoices externally without consent
- Redact personal data if exporting for analysis
- Provider data is typically business data (not personal)

---

## Backup Requirements

- Invoices must be readable for entire retention period
- PDF/A format recommended for long-term archival
- Regular backups (cloud + local)
- Test restore periodically
