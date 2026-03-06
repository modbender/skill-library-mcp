---
name: csv-to-excel
description: "Convert CSV files to professionally formatted Excel workbooks with Chinese character support, automatic formatting, and multi-sheet capabilities. Use when users need to: (1) Convert single CSV to Excel, (2) Combine multiple CSV files into one Excel with separate sheets, (3) Format CSV data with headers, borders, and auto-adjusted columns, (4) Handle Chinese or other non-ASCII characters in CSV files, or (5) Create professional Excel reports from CSV data."
---

# CSV To Excel Converter

## Overview

This skill enables conversion of CSV files to Excel format with professional formatting, proper encoding handling for Chinese characters, and support for combining multiple CSV files into a single Excel workbook with separate sheets.

## Quick Start

Use the `csv_to_excel.py` script for all conversions:

```bash
# Single CSV to Excel
python scripts/csv_to_excel.py input.csv output.xlsx

# Multiple CSVs to one Excel (each becomes a sheet)
python scripts/csv_to_excel.py file1.csv file2.csv file3.csv --output combined.xlsx

# With custom sheet names
python scripts/csv_to_excel.py sales.csv inventory.csv --output report.xlsx --sheet-names "销售数据" "库存数据"
```

## Features

### Automatic Encoding Detection
- Detects CSV encoding automatically (UTF-8, GBK, GB2312, UTF-8-SIG)
- Ensures Chinese characters display correctly in Excel
- No manual encoding specification needed

### Professional Formatting
- **Header row**: Bold white text on blue background
- **Borders**: Thin borders around all cells
- **Column widths**: Auto-adjusted based on content (handles Chinese characters properly)
- **Frozen panes**: Header row frozen for easy scrolling
- **Alignment**: Headers centered

### Multi-Sheet Support
- Combine multiple CSV files into one Excel workbook
- Each CSV becomes a separate sheet
- Custom sheet names supported
- Sheet names default to CSV filenames (max 31 characters)

## Common Usage Patterns

### Pattern 1: Single File Conversion
User says: "Convert this data.csv to Excel"

```bash
python scripts/csv_to_excel.py data.csv data.xlsx
```

### Pattern 2: Multiple Files to Multi-Sheet Excel
User says: "Combine these CSV files into one Excel, each file as a separate sheet"

```bash
python scripts/csv_to_excel.py sales_2024.csv sales_2025.csv inventory.csv --output report.xlsx
```

Result: `report.xlsx` with 3 sheets named "sales_2024", "sales_2025", "inventory"

### Pattern 3: Custom Sheet Names
User says: "Create an Excel with these CSVs and name the sheets in Chinese"

```bash
python scripts/csv_to_excel.py q1.csv q2.csv q3.csv q4.csv --output 年度报告.xlsx --sheet-names "第一季度" "第二季度" "第三季度" "第四季度"
```

### Pattern 4: Handling Chinese Content
User says: "This CSV has Chinese text and it shows as garbled characters in Excel"

The script automatically detects encoding and handles Chinese characters:
```bash
python scripts/csv_to_excel.py 中文数据.csv 输出.xlsx
```

## Technical Details

### Encoding Support
The script tries these encodings in order:
1. UTF-8
2. GBK (common for Chinese Windows)
3. GB2312 (simplified Chinese)
4. UTF-8-SIG (UTF-8 with BOM)
5. Latin1 (fallback)

### CSV Dialect Detection
- Automatically detects delimiter (comma, semicolon, tab, etc.)
- Handles quoted fields
- Works with various CSV formats

### Column Width Calculation
- Chinese characters counted as 2 width units
- ASCII characters counted as 1 width unit
- Maximum width capped at 50 for readability
- Adds 2 units padding for visual comfort

## Dependencies

The script requires `openpyxl`:

```bash
pip install openpyxl
```

## Troubleshooting

**Issue**: Chinese characters still appear garbled
- **Solution**: The CSV file may have a rare encoding. Try converting the CSV to UTF-8 first using a text editor.

**Issue**: Sheet name error
- **Solution**: Excel sheet names must be ≤31 characters. The script auto-truncates, but you can specify shorter custom names.

**Issue**: Empty sheets created
- **Solution**: Check that CSV files are not empty and are properly formatted.

**Issue**: Script not found
- **Solution**: Run the script from the skill directory or use the full path: `python .kiro/skills/csv-to-excel/scripts/csv_to_excel.py`
