# Azure Document Intelligence Prebuilt Models

Reference guide for Azure Document Intelligence prebuilt models (API v4.0, 2024-11-30).

## Model Overview

| Model ID | Purpose | Best For |
|----------|---------|----------|
| `prebuilt-read` | General OCR | Pure text extraction from any document |
| `prebuilt-layout` | Document structure | Tables, forms, paragraphs, figures |
| `prebuilt-invoice` | Invoice processing | Vendor info, line items, totals |
| `prebuilt-receipt` | Receipt scanning | Merchant, items, dates, totals |
| `prebuilt-idDocument` | ID recognition | IDs, passports, driver's licenses |
| `prebuilt-businessCard` | Business cards | Contact information extraction |
| `prebuilt-tax.us.w2` | W-2 tax forms | US employee wage statements |
| `prebuilt-healthInsuranceCard.us` | Insurance cards | Health insurance information |

---

## prebuilt-read

**Description**: General-purpose OCR model optimized for extracting printed and handwritten text from documents. Supports 300+ languages including CJK (Chinese, Japanese, Korean).

**When to Use**:
- Extracting plain text from any document type
- Processing scanned documents and images
- Handwriting recognition
- Multi-language documents
- When you only need text content, not structure

**Key Extracted Fields**:
- `content`: Full extracted text
- `pages`: Per-page text and metadata
- `paragraphs`: Text blocks with bounding regions
- `words`: Individual words with confidence scores
- `lines`: Text lines with spans

**Supported Formats**: PDF, JPEG, PNG, BMP, TIFF, HEIF

**Example**:
```bash
python scripts/ocr_extract.py document.pdf --model prebuilt-read
```

---

## prebuilt-layout

**Description**: Extracts text along with document structure including tables, selection marks, paragraphs, and figures. Ideal for structured documents where layout matters.

**When to Use**:
- Documents with tables or forms
- Structured reports and papers
- Documents with checkboxes or selection marks
- When you need to preserve document structure
- Forms with labeled fields

**Key Extracted Fields**:
- `content`: Full extracted text
- `tables`: Table structure with cells, rows, columns
- `paragraphs`: Structured paragraph blocks
- `selectionMarks`: Checkboxes, radio buttons
- `figures`: Detected figures with captions
- `sections`: Document sections with hierarchy

**Supported Formats**: PDF, JPEG, PNG, BMP, TIFF, HEIF

**Example**:
```bash
python scripts/ocr_extract.py report.pdf --model prebuilt-layout --format markdown
```

---

## prebuilt-invoice

**Description**: Specialized model for extracting key information from invoices. Automatically identifies vendor details, line items, totals, and payment information.

**When to Use**:
- Processing vendor invoices
- Accounts payable automation
- Invoice data entry automation
- Financial document processing

**Key Extracted Fields**:
- `VendorName`: Vendor/supplier name
- `VendorAddress`: Vendor address
- `CustomerName`: Customer/bill-to name
- `CustomerAddress`: Customer address
- `InvoiceId`: Invoice number
- `InvoiceDate`: Invoice date
- `DueDate`: Payment due date
- `PurchaseOrder`: PO number
- `Items`: Line items (description, quantity, unit price, amount)
- `SubTotal`: Subtotal before tax
- `TotalTax`: Tax amount
- `InvoiceTotal`: Total amount due
- `AmountDue`: Amount due
- `PaymentTerm`: Payment terms
- `BillingAddress`: Billing address
- `ShippingAddress`: Shipping address

**Supported Formats**: PDF, JPEG, PNG, BMP, TIFF

**Example**:
```bash
python scripts/ocr_extract.py invoice.pdf --model prebuilt-invoice --format json
```

---

## prebuilt-receipt

**Description**: Extracts key information from sales receipts. Optimized for point-of-sale receipts from retail stores, restaurants, and services.

**When to Use**:
- Expense report automation
- Receipt digitization
- Retail transaction processing
- Restaurant receipt processing

**Key Extracted Fields**:
- `MerchantName`: Store/merchant name
- `MerchantAddress`: Store address
- `MerchantPhoneNumber`: Store phone
- `TransactionDate`: Purchase date
- `TransactionTime`: Purchase time
- `Items`: Purchased items (name, quantity, price)
- `Subtotal`: Subtotal before tax
- `Tax`: Tax amount
- `Tip`: Tip amount (if applicable)
- `Total`: Total amount
- `PaymentMethod`: Payment method used

**Supported Formats**: PDF, JPEG, PNG, BMP, TIFF

**Example**:
```bash
python scripts/ocr_extract.py receipt.jpg --model prebuilt-receipt --format json
```

---

## prebuilt-idDocument

**Description**: Extracts information from identity documents including passports, driver's licenses, and national ID cards from various countries.

**When to Use**:
- Identity verification workflows
- KYC (Know Your Customer) processes
- Customer onboarding
- Document verification

**Key Extracted Fields**:
- `FirstName`: Given name
- `LastName`: Surname
- `DocumentNumber`: ID/passport number
- `DateOfBirth`: Birth date
- `DateOfExpiration`: Expiration date
- `Sex`: Gender
- `Address`: Address (driver's license)
- `CountryRegion`: Issuing country
- `Region`: State/province
- `DocumentType`: Type of ID document
- `Nationality`: Nationality (passports)
- `PlaceOfBirth`: Birth place (passports)
- `MachineReadableZone`: MRZ data (passports)

**Supported Document Types**:
- US Driver's License
- International Passports
- US State IDs
- Social Security Cards
- Residence Permits
- National IDs (various countries)

**Supported Formats**: PDF, JPEG, PNG, BMP, TIFF

**Example**:
```bash
python scripts/ocr_extract.py passport.jpg --model prebuilt-idDocument --format json
```

---

## prebuilt-businessCard

**Description**: Extracts contact information from business cards. Supports cards in various layouts and languages.

**When to Use**:
- CRM data entry
- Contact management
- Networking event follow-up
- Lead capture digitization

**Key Extracted Fields**:
- `ContactNames`: Names on card (first, last)
- `CompanyNames`: Company/organization
- `JobTitles`: Job title/position
- `Departments`: Department name
- `Emails`: Email addresses
- `Phones`: Phone numbers (work, mobile, fax)
- `Addresses`: Physical addresses
- `Websites`: Website URLs

**Supported Formats**: JPEG, PNG, BMP, TIFF

**Example**:
```bash
python scripts/ocr_extract.py card.jpg --model prebuilt-businessCard --format json
```

---

## prebuilt-tax.us.w2

**Description**: Specialized model for extracting information from US W-2 tax forms (Wage and Tax Statement).

**When to Use**:
- Tax preparation software
- Payroll verification
- Financial services automation
- Tax document processing

**Key Extracted Fields**:
- `Employee`: Employee SSN, name, address
- `Employer`: EIN, name, address
- `WagesTipsOtherCompensation`: Box 1 - wages
- `FederalIncomeTaxWithheld`: Box 2 - federal tax
- `SocialSecurityWages`: Box 3
- `SocialSecurityTaxWithheld`: Box 4
- `MedicareWagesAndTips`: Box 5
- `MedicareTaxWithheld`: Box 6
- `SocialSecurityTips`: Box 7
- `AllocatedTips`: Box 8
- `DependentCareBenefits`: Box 10
- `NonQualifiedPlans`: Box 11
- `StateTaxInfo`: State wages and tax
- `LocalTaxInfo`: Local wages and tax
- `TaxYear`: Tax year

**Supported Formats**: PDF, JPEG, PNG, BMP, TIFF

**Example**:
```bash
python scripts/ocr_extract.py w2_form.pdf --model prebuilt-tax.us.w2 --format json
```

---

## prebuilt-healthInsuranceCard.us

**Description**: Extracts information from US health insurance cards including member details and coverage information.

**When to Use**:
- Healthcare patient intake
- Insurance verification
- Medical billing automation
- Eligibility checks

**Key Extracted Fields**:
- `Insurer`: Insurance company name
- `MemberId`: Member ID number
- `MemberName`: Member name
- `GroupNumber`: Group number
- `PlanName`: Plan name
- `PlanType`: Type of plan (HMO, PPO, etc.)
- `DateOfBirth`: Member's date of birth
- `EffectiveDate`: Coverage start date
- `Copays`: Copay information
- `Prescriptions`: Prescription coverage
- `ServiceNumbers`: Customer service phone numbers

**Supported Formats**: JPEG, PNG, BMP, TIFF

**Example**:
```bash
python scripts/ocr_extract.py insurance_card.jpg --model prebuilt-healthInsuranceCard.us --format json
```

---

## Model Selection Decision Tree

```
Need to extract text from a document?
│
├─ Just need plain text? → prebuilt-read
│
├─ Need tables or structure? → prebuilt-layout
│
├─ Is it a specific document type?
│   │
│   ├─ Invoice → prebuilt-invoice
│   ├─ Receipt → prebuilt-receipt
│   ├─ ID/Passport → prebuilt-idDocument
│   ├─ Business card → prebuilt-businessCard
│   ├─ W-2 tax form → prebuilt-tax.us.w2
│   └─ Insurance card → prebuilt-healthInsuranceCard.us
│
└─ Unknown/general document
    ├─ Has tables/forms → prebuilt-layout
    └─ Text only → prebuilt-read
```

## Performance Notes

- **prebuilt-read**: Fastest, best for high-volume text extraction
- **prebuilt-layout**: Slightly slower due to structure analysis
- **Specialized models**: Optimized for their document types, may be slower on large batches

## Supported Languages

- **prebuilt-read/layout**: 300+ languages including all CJK languages
- **Specialized models**: Primarily English, with varying support for other languages

## API Limits

- Max file size: 500 MB (PDF), 50 MB (images)
- Max pages: 2000 pages per document
- Max images in PDF: 2000 images
- Minimum resolution: 50x50 pixels
- Maximum resolution: 10000x10000 pixels
