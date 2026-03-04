# Default Chart of Accounts

Convention: 1xxx = assets, 2xxx = liabilities, 3xxx = equity, 4xxx = revenue, 5xxx = expenses

## Assets (1xxx)
| Code | Name |
|------|------|
| 1000-cash | Cash and cash equivalents |
| 1010-bank-checking | Checking account |
| 1020-bank-savings | Savings account |
| 1100-accounts-rec | Accounts receivable |
| 1200-prepaid | Prepaid expenses |
| 1500-equipment | Equipment |
| 1510-equipment-dep | Accumulated depreciation — equipment |

## Liabilities (2xxx)
| Code | Name |
|------|------|
| 2000-accounts-pay | Accounts payable |
| 2100-accrued-liab | Accrued liabilities |
| 2200-deferred-rev | Deferred revenue |
| 2500-loans-pay | Loans payable |
| 2900-tax-payable | Taxes payable |

## Equity (3xxx)
| Code | Name |
|------|------|
| 3000-owner-equity | Owner's equity |
| 3100-retained | Retained earnings |
| 3900-distributions | Owner distributions |

## Revenue (4xxx)
| Code | Name |
|------|------|
| 4000-revenue | Revenue |
| 4100-services | Services revenue |
| 4200-subscriptions | Subscription revenue |
| 4900-other-income | Other income |

## Expenses (5xxx)
| Code | Name |
|------|------|
| 5000-payroll | Payroll and wages |
| 5100-contractors | Contractor payments |
| 5200-rent | Rent and facilities |
| 5300-software | Software and tools |
| 5400-marketing | Marketing and advertising |
| 5500-travel | Travel and entertainment |
| 5600-legal | Legal and professional fees |

## Customizing

Fork `accounts.yaml` and replace codes/names to match your entity. Account codes are arbitrary strings — keep them consistent across all journal entries. Vertical forks (pm-in-a-box, dental-in-a-box, etc.) define their own extended charts.
