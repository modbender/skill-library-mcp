export const CHART_OF_ACCOUNTS = [
  // Revenue
  "Sales/Service Revenue", "Interest Income", "Other Income",
  // COGS
  "Contractors", "Servers & Hosting", "Stripe Fees",
  // Operating Expenses
  "Advertising", "Amortization", "Bank Service Charges",
  "Business Licensing, Fees & Tax", "Legal & Professional Fees",
  "Performance fees (Seller)", "Software expenses", "Wages & Salaries",
  "Insurance", "Other Expenses",
  // Balance Sheet
  "Owner Draws/Distributions", "Transfers Between Accounts", "Loans/Debt Payments",
];

export const ACCOUNT_CLASSIFICATIONS = [
  // Revenue
  { name: "Sales/Service Revenue", pnlSection: "Revenue", cashFlowSection: "Operating", isBalanceSheetOnly: false },
  { name: "Interest Income", pnlSection: "Revenue", cashFlowSection: "Operating", isBalanceSheetOnly: false },
  { name: "Other Income", pnlSection: "Revenue", cashFlowSection: "Operating", isBalanceSheetOnly: false },
  // COGS
  { name: "Contractors", pnlSection: "COGS", cashFlowSection: "Operating", isBalanceSheetOnly: false },
  { name: "Servers & Hosting", pnlSection: "COGS", cashFlowSection: "Operating", isBalanceSheetOnly: false },
  { name: "Stripe Fees", pnlSection: "COGS", cashFlowSection: "Operating", isBalanceSheetOnly: false },
  // Operating Expenses
  { name: "Advertising", pnlSection: "Operating Expenses", cashFlowSection: "Operating", isBalanceSheetOnly: false },
  { name: "Amortization", pnlSection: "Operating Expenses", cashFlowSection: "Operating", isBalanceSheetOnly: false },
  { name: "Bank Service Charges", pnlSection: "Operating Expenses", cashFlowSection: "Operating", isBalanceSheetOnly: false },
  { name: "Business Licensing, Fees & Tax", pnlSection: "Operating Expenses", cashFlowSection: "Operating", isBalanceSheetOnly: false },
  { name: "Legal & Professional Fees", pnlSection: "Operating Expenses", cashFlowSection: "Operating", isBalanceSheetOnly: false },
  { name: "Performance fees (Seller)", pnlSection: "Operating Expenses", cashFlowSection: "Operating", isBalanceSheetOnly: false },
  { name: "Software expenses", pnlSection: "Operating Expenses", cashFlowSection: "Operating", isBalanceSheetOnly: false },
  { name: "Wages & Salaries", pnlSection: "Operating Expenses", cashFlowSection: "Operating", isBalanceSheetOnly: false },
  { name: "Insurance", pnlSection: "Operating Expenses", cashFlowSection: "Operating", isBalanceSheetOnly: false },
  { name: "Other Expenses", pnlSection: "Operating Expenses", cashFlowSection: "Operating", isBalanceSheetOnly: false },
  // Balance Sheet
  { name: "Owner Draws/Distributions", pnlSection: null, cashFlowSection: "Financing", isBalanceSheetOnly: true },
  { name: "Transfers Between Accounts", pnlSection: null, cashFlowSection: null, isBalanceSheetOnly: true },
  { name: "Loans/Debt Payments", pnlSection: null, cashFlowSection: "Financing", isBalanceSheetOnly: true },
];

export const PNL_SECTIONS = [
  { name: "Revenue", categories: ["Sales/Service Revenue", "Interest Income", "Other Income"] },
  { name: "COGS", categories: ["Contractors", "Servers & Hosting", "Stripe Fees"] },
  { name: "Operating Expenses", categories: [
    "Advertising", "Amortization", "Bank Service Charges",
    "Business Licensing, Fees & Tax", "Legal & Professional Fees",
    "Performance fees (Seller)", "Software expenses", "Wages & Salaries",
    "Insurance", "Other Expenses",
  ]},
];
