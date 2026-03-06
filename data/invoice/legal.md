# Invoice Legal Requirements

## Spain (RD 1619/2012)

### Required Fields

Every invoice must include:
1. **Número de factura** — Correlative within series
2. **Fecha de expedición**
3. **Datos del emisor:** Nombre/razón social, NIF, dirección
4. **Datos del destinatario:** Nombre/razón social, NIF, dirección
5. **Descripción de la operación**
6. **Base imponible**
7. **Tipo impositivo** (%)
8. **Cuota tributaria** (IVA amount)
9. **Importe total**

### Invoice Types

| Type | When to use |
|------|-------------|
| Factura completa | B2B, >400€, always for VAT deduction |
| Factura simplificada | B2C, <400€, no VAT deduction needed |
| Factura rectificativa | To correct or cancel previous invoice |

### Simplified Invoice (Ticket)

Allowed when:
- B2C transaction
- Amount ≤ 400€ (or ≤3,000€ for certain services)
- Recipient doesn't need VAT deduction

Can omit:
- Recipient tax ID
- Recipient address

### Credit Note (Rectificativa)

Required when:
- Error in original invoice
- Return of goods
- Discount after invoice issued
- Cancellation

Must include:
- Reference to original invoice (number, date)
- Reason for correction
- Original and corrected amounts

---

## VAT Rates (Spain)

| Rate | Name | Applies to |
|------|------|------------|
| 21% | General | Most goods and services |
| 10% | Reducido | Food, transport, hospitality |
| 4% | Superreducido | Bread, books, medicines |
| 0% | Exento | Insurance, finance, health |

### Intra-EU (B2B)

- No Spanish VAT
- Include: "Operación sujeta a inversión del sujeto pasivo"
- Client applies their local VAT

### Export (non-EU)

- No VAT (exempt)
- Include: "Exportación exenta de IVA"

---

## IRPF Retention (Freelancers)

When issuer is autonomous professional invoicing to company:

| Rate | When |
|------|------|
| 15% | Standard |
| 7% | First 3 years of activity |
| 0% | B2C, export, simplified regime |

**Calculation:**
```
Base: 1000€
IVA (21%): 210€
Total factura: 1210€
IRPF (15%): -150€
A cobrar: 1060€
```

Note: IRPF reduces what you receive, not the invoice total.

---

## Numbering Rules

- **Correlative** — No gaps: 001, 002, 003
- **By year** — Can reset each year (F-2026-001)
- **Multiple series** — Allowed for different activities
- **Never reuse** — Even cancelled invoices keep their number

---

## TicketBAI (País Vasco / Navarra)

If user is in Basque Country:
- All invoices must be registered with tax authority
- QR code required on invoice
- Digital signature required
- XML format submission

**Ask user:** "¿Necesitas facturación con TicketBAI?"

---

## Facturae (Public Administration)

If invoicing Spanish public entities (B2G):
- XML format required (Facturae 3.2.2)
- Submission via FACe portal
- Digital certificate required

**Ask user:** "¿Facturas a administración pública?"
