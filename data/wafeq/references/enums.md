# Wafeq API Enum Types Reference

Complete reference for all enum types used across the Wafeq API.

---

## AccountSubClassificationEnum

Description: Account sub-classification categories for financial accounting.

| Value | Description |
|-------|-------------|
| `INCOME` | Income |
| `OTHER_INCOME` | Other Income |
| `COGS` | Cost of Sales |
| `OPERATING_EXPENSE` | Operating Expenses |
| `NON_OPERATING_EXPENSE` | Non-Operating Expenses |
| `CASH_EQUIVALENTS` | Cash and Cash Equivalents |
| `CURRENT_ASSET` | Current Assets |
| `NON_CURRENT_ASSET` | Non-Current Assets |
| `FIXED_ASSET` | Fixed Asset |
| `CURRENT_LIABILITY` | Current Liabilities |
| `NON_CURRENT_LIABILITY` | Non-Current Liabilities |
| `PAID_IN_CAPITAL` | Paid-in Capital |
| `RETAINED_EARNINGS` | Retained Earnings |
| `ACCUMULATED_OTHER_COMPREHENSIVE_INCOME` | Acc. Other Comprehensive Income |
| `TREASURY_STOCK` | Treasury Stock |
| `OWNERS_EQUITY` | Owner's Equity |
| `OPENING_BALANCE_EQUITY` | Opening Balance Equity |

---

## BankAccountSubClassificationEnum

Description: Sub-classification for bank-type accounts.

| Value | Description |
|-------|-------------|
| `BANK` | Bank |
| `PETTY_CASH` | Petty Cash |
| `CREDIT_CARD` | Credit Card |

---

## BillStatusEnum

Description: Status values for bills.

| Value | Description |
|-------|-------------|
| `DRAFT` | Draft |
| `AUTHORIZED` | Authorized |
| `PAID` | Paid |

---

## ChargeTypeEnum

Description: Who bears the charge/fee (banking context).

| Value | Description |
|-------|-------------|
| `OUR` | Ours (sender pays) |
| `BEN` | Beneficiary (recipient pays) |
| `SHA` | Shared |

---

## ClassificationEnum

Description: Top-level account classification categories.

| Value | Description |
|-------|-------------|
| `REVENUE` | Revenue |
| `EXPENSE` | Expense |
| `ASSET` | Asset |
| `BANK` | Bank |
| `LIABILITY` | Liability |
| `EQUITY` | Equity |

---

## CurrencyEnum

Description: ISO 4217 currency codes supported by Wafeq.

| Value | Description |
|-------|-------------|
| `AED` | UAE Dirham |
| `SAR` | Saudi Riyal |
| `USD` | US Dollar |
| `EUR` | Euro |
| `CAD` | Canadian Dollar |
| `AFN` | Afghan Afghani |
| `ALL` | Albanian Lek |
| `AMD` | Armenian Dram |
| `ARS` | Argentine Peso |
| `AUD` | Australian Dollar |
| `AZN` | Azerbaijani Manat |
| `BAM` | Bosnia-Herzegovina Convertible Mark |
| `BDT` | Bangladeshi Taka |
| `BGN` | Bulgarian Lev |
| `BHD` | Bahraini Dinar |
| `BIF` | Burundian Franc |
| `BND` | Brunei Dollar |
| `BOB` | Bolivian Boliviano |
| `BRL` | Brazilian Real |
| `BWP` | Botswanan Pula |
| `BYN` | Belarusian Ruble |
| `BZD` | Belize Dollar |
| `CDF` | Congolese Franc |
| `CHF` | Swiss Franc |
| `CLP` | Chilean Peso |
| `CNY` | Chinese Yuan |
| `COP` | Colombian Peso |
| `CRC` | Costa Rican Colon |
| `CVE` | Cape Verdean Escudo |
| `CZK` | Czech Koruna |
| `DJF` | Djiboutian Franc |
| `DKK` | Danish Krone |
| `DOP` | Dominican Peso |
| `DZD` | Algerian Dinar |
| `EGP` | Egyptian Pound |
| `ERN` | Eritrean Nakfa |
| `ETB` | Ethiopian Birr |
| `GBP` | British Pound |
| `GEL` | Georgian Lari |
| `GHS` | Ghanaian Cedi |
| `GNF` | Guinean Franc |
| `GTQ` | Guatemalan Quetzal |
| `HKD` | Hong Kong Dollar |
| `HNL` | Honduran Lempira |
| `HRK` | Croatian Kuna |
| `HUF` | Hungarian Forint |
| `IDR` | Indonesian Rupiah |
| `ILS` | Israeli New Shekel |
| `INR` | Indian Rupee |
| `IQD` | Iraqi Dinar |
| `IRR` | Iranian Rial |
| `ISK` | Icelandic Krona |
| `JMD` | Jamaican Dollar |
| `JOD` | Jordanian Dinar |
| `JPY` | Japanese Yen |
| `KES` | Kenyan Shilling |
| `KHR` | Cambodian Riel |
| `KMF` | Comorian Franc |
| `KRW` | South Korean Won |
| `KWD` | Kuwaiti Dinar |
| `KZT` | Kazakhstani Tenge |
| `LBP` | Lebanese Pound |
| `LKR` | Sri Lankan Rupee |
| `LYD` | Libyan Dinar |
| `MAD` | Moroccan Dirham |
| `MDL` | Moldovan Leu |
| `MGA` | Malagasy Ariary |
| `MKD` | Macedonian Denar |
| `MMK` | Myanmar Kyat |
| `MOP` | Macanese Pataca |
| `MUR` | Mauritian Rupee |
| `MXN` | Mexican Peso |
| `MYR` | Malaysian Ringgit |
| `MZN` | Mozambican Metical |
| `NAD` | Namibian Dollar |
| `NGN` | Nigerian Naira |
| `NIO` | Nicaraguan Cordoba |
| `NOK` | Norwegian Krone |
| `NPR` | Nepalese Rupee |
| `NZD` | New Zealand Dollar |
| `OMR` | Omani Rial |
| `PAB` | Panamanian Balboa |
| `PEN` | Peruvian Sol |
| `PHP` | Philippine Peso |
| `PKR` | Pakistani Rupee |
| `PLN` | Polish Zloty |
| `PYG` | Paraguayan Guarani |
| `QAR` | Qatari Riyal |
| `RON` | Romanian Leu |
| `RSD` | Serbian Dinar |
| `RUB` | Russian Ruble |
| `RWF` | Rwandan Franc |
| `SDG` | Sudanese Pound |
| `SEK` | Swedish Krona |
| `SGD` | Singapore Dollar |
| `SOS` | Somali Shilling |
| `SYP` | Syrian Pound |
| `THB` | Thai Baht |
| `TND` | Tunisian Dinar |
| `TOP` | Tongan Pa'anga |
| `TRY` | Turkish Lira |
| `TTD` | Trinidad and Tobago Dollar |
| `TWD` | New Taiwan Dollar |
| `TZS` | Tanzanian Shilling |
| `UAH` | Ukrainian Hryvnia |
| `UGX` | Ugandan Shilling |
| `UYU` | Uruguayan Peso |
| `UZS` | Uzbekistani Som |
| `VES` | Venezuelan Bolivar |
| `VND` | Vietnamese Dong |
| `XAF` | Central African CFA Franc |
| `XOF` | West African CFA Franc |
| `YER` | Yemeni Rial |
| `ZAR` | South African Rand |
| `ZMW` | Zambian Kwacha |

---

## DiscountTypeEnum

Description: Type of discount applied to line items.

| Value | Description |
|-------|-------------|
| `percent` | Percentage discount (%) |
| `amount` | Fixed amount discount |

---

## ExpenseTaxAmountTypeEnum

Description: Whether expense amounts include or exclude tax.

| Value | Description |
|-------|-------------|
| `TAX_EXCLUSIVE` | Excluding tax (exc. tax) |
| `TAX_INCLUSIVE` | Including tax (inc. tax) |

---

## Language41aEnum

Description: Language options (variant A).

| Value | Description |
|-------|-------------|
| `en` | English |
| `ar` | Arabic |

---

## LanguageAc1Enum

Description: Language options (variant B).

| Value | Description |
|-------|-------------|
| `ar` | Arabic |
| `en` | English |

---

## MediumEnum

Description: Communication medium for notifications.

| Value | Description |
|-------|-------------|
| `email` | Email |

---

## PaymentRequestStatusEnum

Description: Status values for payment requests.

| Value | Description |
|-------|-------------|
| `DELETED` | Deleted |
| `DRAFT` | Draft |
| `ERROR` | Error |
| `FETCHING_STATUS` | Fetching status |
| `NOT_FOUND` | Not found |
| `PENDING_APPROVAL` | Pending approval |
| `PENDING_RELEASE` | Pending release |
| `PROCESSED` | Processed |
| `PROCESSING` | Processing |
| `QUEUED` | Queued |
| `REJECTED` | Rejected |
| `RELEASED` | Released |
| `VALIDATED` | Validated |

---

## PayslipStatusEnum

Description: Status values for payslips.

| Value | Description |
|-------|-------------|
| `DRAFT` | Draft |
| `POSTED` | Posted |

---

## SimplifiedInvoiceStatusEnum

Description: Status values for simplified invoices.

| Value | Description |
|-------|-------------|
| `DRAFT` | Draft |
| `PAID` | Paid |

---

## Status9b4Enum

Description: Status values (used for quotes/other documents).

| Value | Description |
|-------|-------------|
| `DRAFT` | Draft |
| `SENT` | Sent |

---

## TaxAmountType8abEnum

Description: Whether amounts include or exclude tax (invoice context).

| Value | Description |
|-------|-------------|
| `TAX_INCLUSIVE` | Including tax (inc. tax) |
| `TAX_EXCLUSIVE` | Excluding tax (exc. tax) |

---

## TaxTypeEnum

Description: Type of tax applicable.

| Value | Description |
|-------|-------------|
| `SALES` | Sales tax |
| `PURCHASES` | Purchases tax |
| `REVERSE_CHARGE` | Reverse Charge |
| `OUT_OF_SCOPE` | Out of Scope |

---

## TypeEnum

Description: Type of discount/charge (same as DiscountTypeEnum).

| Value | Description |
|-------|-------------|
| `percent` | Percentage (%) |
| `amount` | Fixed amount |
