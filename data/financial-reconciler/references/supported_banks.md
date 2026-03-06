# Supported Bank Formats

## Chase Bank
- **Format**: CSV with headers
- **Headers**: Transaction Date, Post Date, Description, Category, Type, Amount, Memo
- **Date format**: MM/DD/YYYY
- **Amount**: Signed (negative = debit, positive = credit)
- **Export path**: Chase.com → Statements & Documents → Download account activity → CSV

## Bank of America
- **Format**: CSV with headers
- **Headers**: Date, Description, Amount, Running Bal.
- **Date format**: MM/DD/YYYY
- **Amount**: Signed
- **Export path**: BofA.com → Statements & Documents → Download Transactions → CSV/Excel

## Wells Fargo
- **Format**: CSV without headers (5 columns)
- **Columns**: Date, Amount, *, *, Description
- **Date format**: MM/DD/YYYY
- **Amount**: Signed
- **Export path**: WellsFargo.com → Account Activity → Download → Comma Delimited

## OFX/QFX (Universal)
- **Format**: Open Financial Exchange (OFX/QFX)
- **Supported by**: Most US banks, Quicken, Microsoft Money
- **Contains**: Account info, transaction list, balances
- **Export**: Look for "Download to Quicken" or "Export OFX/QFX" in your bank's online portal

## Generic CSV
- **Auto-detection**: Matches column headers heuristically
- **Recognized date columns**: date, transaction date, trans date, posting date
- **Recognized description columns**: description, memo, payee, merchant, name
- **Recognized amount columns**: amount, debit/credit (separate columns supported)
- **Tip**: If auto-detect fails, rename your CSV headers to "Date", "Description", "Amount"

## Adding a New Bank Format
To add support for a new bank, edit `assets/csv_formats.json` and add a new entry under `formats` with the column mappings and detection headers.
