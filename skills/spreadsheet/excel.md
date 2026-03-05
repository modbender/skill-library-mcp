# Excel Operations — Spreadsheet Skill

## Libraries

| Library | Use Case |
|---------|----------|
| **openpyxl** | Read/write .xlsx (recommended) |
| **xlsxwriter** | Write-only, better formatting |
| **pandas** | Analysis + Excel I/O |

## Reading

```python
from openpyxl import load_workbook

wb = load_workbook('file.xlsx')
ws = wb.active

value = ws['A1'].value
data = [[cell.value for cell in row] for row in ws['A1:D10']]
```

## Writing

```python
from openpyxl import Workbook
from openpyxl.styles import Font

wb = Workbook()
ws = wb.active
ws['A1'] = 'Header'
ws['A1'].font = Font(bold=True)
ws.append([1, 2, 3])
wb.save('output.xlsx')
```

## Preserving Formulas

```python
# Read formula (not value)
wb = load_workbook('file.xlsx')  # data_only=False default
formula = ws['A1'].value  # Returns '=SUM(B:B)'

# TRAP: data_only=True loses formulas forever
```

## Traps

- **data_only=True** — Loads values, destroys formulas
- **Large files** — Use `read_only=True`, `write_only=True`
- **Dates** — Excel stores as floats; use datetime objects
- **Number format** — Set explicitly: `ws['B2'].number_format = '#,##0.00'`
