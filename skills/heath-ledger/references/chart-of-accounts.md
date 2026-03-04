# Chart of Accounts

Aligned with professional bookkeeper's P&L structure (updated 2026-02-22).

## Categories

| Category | P&L Section | Cash Flow Section | Balance Sheet Only |
|----------|-------------|-------------------|-------------------|
| Sales/Service Revenue | Revenue | Operating | No |
| Interest Income | Revenue | Operating | No |
| Other Income | Revenue | Operating | No |
| Contractors | COGS | Operating | No |
| Servers & Hosting | COGS | Operating | No |
| Stripe Fees | COGS | Operating | No |
| Advertising | Operating Expenses | Operating | No |
| Amortization | Operating Expenses | Operating | No |
| Bank Service Charges | Operating Expenses | Operating | No |
| Business Licensing, Fees & Tax | Operating Expenses | Operating | No |
| Legal & Professional Fees | Operating Expenses | Operating | No |
| Performance fees (Seller) | Operating Expenses | Operating | No |
| Software expenses | Operating Expenses | Operating | No |
| Wages & Salaries | Operating Expenses | Operating | No |
| Insurance | Operating Expenses | Operating | No |
| Other Expenses | Operating Expenses | Operating | No |
| Owner Draws/Distributions | — | Financing | Yes |
| Transfers Between Accounts | — | — | Yes |
| Loans/Debt Payments | — | Financing | Yes |

## P&L Sections (order)

1. **Revenue**: Sales/Service Revenue, Interest Income, Other Income
2. **COGS**: Contractors, Servers & Hosting, Stripe Fees
3. **Operating Expenses**: Advertising, Amortization, Bank Service Charges, Business Licensing Fees & Tax, Legal & Professional Fees, Performance fees (Seller), Software expenses, Wages & Salaries, Insurance, Other Expenses

## Notes

- **Amortization**: $5,833.50/mo journal entry (goodwill on $1,050,030 acquisition, 15-year). Not a bank transaction — handled as manual/calculated entry.
- **Stripe**: Credits → Sales/Service Revenue; Debits/fees → Stripe Fees (COGS). Handled via special logic in categorize.mjs.
- **Deel**: Platform fees → Business Licensing, Fees & Tax; Payroll amounts → Wages & Salaries. (No Deel transactions in current data.)
- **Google**: Generic/Ads → Advertising; Cloud/Workspace → Software expenses. Longer pattern matches first.
- **Watson Goepel**: Asset acquisition on balance sheet, categorized as Transfers Between Accounts.
