# Australian Banking Integration Reference

## Major Banks and BSB Ranges

### Commonwealth Bank of Australia (CBA)
- **BSB Range**: 06xxxx
- **File Format**: Direct Entry, CEMTEX
- **Payment Methods**: EFT, BPAY, Real-time Payments
- **Example BSB**: 062000, 063000, 064000

### National Australia Bank (NAB)
- **BSB Range**: 08xxxx  
- **File Format**: Direct Entry, NAB Connect
- **Payment Methods**: EFT, BPAY, PayID
- **Example BSB**: 082000, 083000, 084000

### Australia and New Zealand Banking (ANZ)
- **BSB Range**: 01xxxx
- **File Format**: Direct Entry, ANZ file format
- **Payment Methods**: EFT, BPAY, Falcon Payments
- **Example BSB**: 012000, 013000, 014000

### Westpac Banking Corporation
- **BSB Range**: 03xxxx
- **File Format**: Direct Entry, Westpac Banking
- **Payment Methods**: EFT, BPAY, Live Wire
- **Example BSB**: 032000, 033000, 034000

## Payment File Formats

### Direct Entry (DE)
- Standard Australian format
- Fixed-width record format
- Header, Detail, Trailer records
- Support for EFT payments

### CEMTEX (Cash and Electronic Money Transfer Exchange)
- Electronic payment standard
- Used for bulk payments
- Supports multiple payment types
- Real-time settlement

### BPAY Format
- Bill payment system
- Reference number based
- Automatic reconciliation
- Consumer payments focus

## Account Number Formats

### Standard Format
- 6-digit BSB + Account Number
- Account numbers: 4-9 digits typically
- Check digit validation available
- Format: BSB-Account (e.g., 062000-12345678)

### Validation Rules
- BSB must be valid and active
- Account number format varies by bank
- Some banks use check digit validation
- Real-time validation services available

## SAP Configuration

### House Bank Setup (FI12)
```
Bank Country: AU
Bank Key: 6-digit BSB (e.g., 062000)
Bank Account: Account number
Currency: AUD
GL Account: Bank GL account number
```

### Payment Method Configuration (FBZP)
```
Payment Method: E (EFT)
Outgoing: X
Single/Mass: M (Mass payments)
Currency: AUD
Min/Max Amount: As required
```

### File Output Format (DME)
- Program: RFFAU_T (Australia specific)
- Format: Direct Entry or bank-specific
- Output medium: File or direct transmission
- File name convention: Bank requirements

## Bank Statement Import

### Electronic Formats Supported
- **BAI2**: Bank Administration Institute format
- **MT940**: SWIFT message format  
- **CSV**: Comma-separated values
- **Bank-specific**: Custom formats per bank

### Transaction Codes Mapping
```
CHQ - Cheque payments
EFT - Electronic funds transfer
DEP - Deposit
WDL - Withdrawal  
FEE - Bank fees
INT - Interest
TFR - Transfer
```

### Automatic Matching
- Amount-based matching (±tolerance)
- Reference number matching
- Payment advice matching
- Date range matching

## Regulatory Compliance

### Anti-Money Laundering (AML)
- Transaction monitoring required
- Cash transactions >$10,000 reporting
- AUSTRAC compliance
- Customer identification requirements

### Banking Standards
- Australian Payments Network (AusPayNet) standards
- Reserve Bank of Australia (RBA) requirements
- Electronic Funds Transfer Code of Conduct
- Banking Code of Practice compliance

## Real-Time Payments

### PayID
- Email/mobile number addressing
- Real-time payment settlement
- 24/7 availability
- Enhanced payment information

### New Payments Platform (NPP)
- Real-time gross settlement
- Enhanced data capability
- Overlay services (PayID, Request to Pay)
- ISO 20022 messaging standard

### Osko
- Consumer overlay service
- Real-time notifications
- Payment requests
- Split bills and group payments

## Integration Points

### SAP Cash Management
- Real-time cash position
- Liquidity forecasting
- Bank communication management
- Multi-bank connectivity

### Treasury Module
- FX transaction processing
- Money market dealing
- Risk management
- Hedge accounting

### Financial Supply Chain Management
- E-invoicing integration
- Payment factory concept
- Bank connectivity hub
- Supplier financing