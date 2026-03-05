# Australian Tax Codes Reference

## Standard GST Tax Codes

### Input Tax (Purchases)
| Code | Description | Rate | GL Account | Usage |
|------|-------------|------|------------|-------|
| A1 | GST on Purchases | 10% | 224000 - GST Recoverable | Standard business purchases |
| E1 | GST-Free Purchases | 0% | N/A | Exports, basic food, education |
| N1 | Input Taxed Purchases | 0% | N/A | Financial services, residential rent |

### Output Tax (Sales)  
| Code | Description | Rate | GL Account | Usage |
|------|-------------|------|------------|-------|
| A2 | GST on Sales | 10% | 225000 - GST Collected | Standard sales to Australian customers |
| E2 | GST-Free Sales | 0% | N/A | Exports, basic food, education |
| N2 | Input Taxed Sales | 0% | N/A | Financial services, residential rent |

## Withholding Tax Codes

### PAYG Withholding
| WHT Type | Description | Rate | Condition |
|----------|-------------|------|-----------|
| 42 | Contractor - No ABN | 47% | No valid ABN provided |
| 43 | Contractor - ABN | 0% | Valid ABN provided |
| 47 | Foreign Resident | Variable | Based on tax treaty |

## GST Categories

### GST-Free Supplies
- Exports of goods and services
- Basic food (bread, milk, eggs, fruit, vegetables)
- Education courses and materials
- Medical and health services
- Charitable activities

### Input Taxed Supplies
- Financial supplies (loans, deposits)
- Residential rent and sales
- School fees and courses (some)
- Fund management
- Precious metals

### Taxable Supplies (10% GST)
- Most goods and services
- Commercial rent
- Restaurant meals
- Professional services
- Imports

## Special Cases

### RCTI (Reverse Charge Tax Invoice)
- Scrap metal industry
- Building and construction (some)
- Taxi/ride-share services
- System calculates GST on recipient's books

### Luxury Car Tax (LCT)
- Rate: 33% (above threshold ~$70,000)
- Separate tax code: L1
- Not GST - additional luxury tax

### Wine Equalisation Tax (WET)
- Rate: 29% of wholesale value
- Wine producers and importers
- Rebate available (up to $350,000/year)

## Configuration Notes

### Tax Procedure: TAXAU
- Condition Type MWST: Input/Output GST
- Condition Type MWAS: Additional taxes (LCT, WET)
- Account Key VST: Input tax
- Account Key MW1: Output tax

### GL Account Structure
```
224000 - GST Recoverable (Input Tax)
225000 - GST Collected (Output Tax)  
226000 - PAYG Withholding Payable
227000 - Luxury Car Tax Payable
228000 - Wine Equalisation Tax
```

### BAS Integration
- Monthly/Quarterly BAS preparation
- G1: Total Sales (GST inclusive)
- G2: Export Sales 
- G3: Other GST-free sales
- G10: Capital purchases
- G11: Non-capital purchases
- 1A: GST on sales
- 1B: GST on purchases