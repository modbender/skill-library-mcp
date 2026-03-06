---
name: freelance-invoice
description: Generate professional invoice PDFs for freelancers with
  multi-currency and tax support.
---


# Invoice Generator

Generate professional invoice PDFs from structured data.

**Use when** creating invoices, billing clients, or generating payment documents.

## Requirements

- Node.js 18+ with Puppeteer, OR `wkhtmltopdf`
- No API keys needed

## Instructions

1. **Collect invoice details**:
   - **From**: Name, address, email, bank details, logo URL (optional)
   - **To**: Client name, address, email
   - **Items**: Description, quantity, unit price
   - **Meta**: Invoice number, date, due date, currency (default: USD), tax rate (default: 0%)
   - **Notes**: Payment terms, thank you message

2. **Generate HTML invoice** with this structure:
   - Header: sender info + logo, invoice number/date
   - Client info block
   - Line items table with columns: Description | Qty | Unit Price | Amount
   - Subtotal, tax (if applicable), **total** in bold
   - Footer: payment instructions, bank details, notes

3. **Convert to PDF**:
   ```bash
   # Option A: Puppeteer (best quality)
   node -e "
   const p=require('puppeteer');
   (async()=>{
     const b=await p.launch({args:['--no-sandbox']});
     const pg=await b.newPage();
     await pg.setContent(fs.readFileSync('invoice.html','utf8'));
     await pg.pdf({path:'invoice.pdf',format:'A4',margin:{top:'20mm',bottom:'20mm',left:'15mm',right:'15mm'}});
     await b.close();
   })()
   "

   # Option B: wkhtmltopdf
   wkhtmltopdf --margin-top 20mm --margin-bottom 20mm invoice.html invoice.pdf
   ```

4. **Currency formatting**:
   | Currency | Symbol | Format |
   |----------|--------|--------|
   | USD | $ | $1,234.56 |
   | EUR | € | €1.234,56 |
   | JPY | ¥ | ¥123,456 |
   | GBP | £ | £1,234.56 |

5. **Deliver**: Save PDF, provide file path. Offer to adjust formatting.

## Invoice Number Convention

- Sequential: `INV-2025-001`, `INV-2025-002`
- Date-based: `INV-20250115-01`
- Client-prefixed: `ACME-2025-003`

Suggest incrementing from the last used number.

## Edge Cases

- **No tax**: Set tax to 0% and hide the tax row.
- **Multiple tax rates**: Support line-item-level tax or split tax display.
- **Discount**: Add a discount line with negative amount before subtotal.
- **Recurring invoices**: Suggest a naming scheme and increment invoice numbers.
- **Missing Puppeteer**: Fall back to `wkhtmltopdf`. If neither available, output HTML only.

## Security Considerations

- Never embed real bank account details in example outputs.
- Invoice HTML should not load external resources (tracking pixels, scripts).
- Sanitize all user input before embedding in HTML to prevent XSS.
