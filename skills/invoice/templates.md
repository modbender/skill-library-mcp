# Invoice Templates

## HTML Template (Default)

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body { font-family: -apple-system, sans-serif; margin: 40px; }
    .header { display: flex; justify-content: space-between; margin-bottom: 40px; }
    .logo { max-height: 60px; }
    .invoice-info { text-align: right; }
    .invoice-number { font-size: 24px; font-weight: bold; color: #2563eb; }
    .parties { display: flex; gap: 40px; margin-bottom: 40px; }
    .party { flex: 1; }
    .party-title { font-weight: bold; color: #666; margin-bottom: 8px; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th { background: #f3f4f6; text-align: left; padding: 12px; }
    td { padding: 12px; border-bottom: 1px solid #e5e7eb; }
    .amount { text-align: right; }
    .totals { margin-top: 20px; }
    .totals-row { display: flex; justify-content: flex-end; gap: 40px; padding: 8px 0; }
    .totals-label { color: #666; }
    .grand-total { font-size: 20px; font-weight: bold; border-top: 2px solid #333; padding-top: 12px; }
    .payment { margin-top: 40px; padding: 20px; background: #f9fafb; border-radius: 8px; }
    .footer { margin-top: 40px; font-size: 12px; color: #666; text-align: center; }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <!-- {{logo}} -->
      <h2>{{issuer.name}}</h2>
      <div>{{issuer.tax_id}}</div>
      <div>{{issuer.address}}</div>
    </div>
    <div class="invoice-info">
      <div class="invoice-number">{{invoice_number}}</div>
      <div>Fecha: {{date}}</div>
      <div>Vencimiento: {{due_date}}</div>
    </div>
  </div>

  <div class="parties">
    <div class="party">
      <div class="party-title">CLIENTE</div>
      <div><strong>{{client.name}}</strong></div>
      <div>{{client.tax_id}}</div>
      <div>{{client.address}}</div>
    </div>
  </div>

  <table>
    <thead>
      <tr>
        <th>Descripción</th>
        <th class="amount">Cantidad</th>
        <th class="amount">Precio</th>
        <th class="amount">Total</th>
      </tr>
    </thead>
    <tbody>
      {{#each line_items}}
      <tr>
        <td>{{description}}</td>
        <td class="amount">{{quantity}}</td>
        <td class="amount">{{unit_price}}€</td>
        <td class="amount">{{total}}€</td>
      </tr>
      {{/each}}
    </tbody>
  </table>

  <div class="totals">
    <div class="totals-row">
      <span class="totals-label">Base imponible:</span>
      <span>{{subtotal}}€</span>
    </div>
    <div class="totals-row">
      <span class="totals-label">IVA ({{tax_rate}}%):</span>
      <span>{{tax_amount}}€</span>
    </div>
    {{#if retention}}
    <div class="totals-row">
      <span class="totals-label">IRPF (-{{retention_rate}}%):</span>
      <span>-{{retention_amount}}€</span>
    </div>
    {{/if}}
    <div class="totals-row grand-total">
      <span>TOTAL:</span>
      <span>{{total}}€</span>
    </div>
  </div>

  <div class="payment">
    <strong>Forma de pago:</strong> Transferencia bancaria<br>
    <strong>IBAN:</strong> {{issuer.iban}}<br>
    <strong>Concepto:</strong> {{invoice_number}}
  </div>

  <div class="footer">
    {{issuer.name}} · {{issuer.tax_id}} · {{issuer.email}}
  </div>
</body>
</html>
```

## PDF Generation

**Option 1: Browser print**
```bash
# Open HTML in browser, print to PDF
```

**Option 2: WeasyPrint**
```bash
weasyprint invoice.html invoice.pdf
```

**Option 3: Puppeteer/Playwright**
```javascript
await page.pdf({ path: 'invoice.pdf', format: 'A4' });
```

## Customization

Store user customizations in `config.json`:
```json
{
  "logo": "~/billing/logo.png",
  "primary_color": "#2563eb",
  "footer_text": "Gracias por su confianza",
  "payment_note": "Transferencia bancaria a 30 días"
}
```
