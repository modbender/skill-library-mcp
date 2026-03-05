import ExcelJS from 'exceljs';

const CURRENCY_FORMAT = '#,##0.00;(#,##0.00);"-"';
const MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

function fmt(amount) { return Number((amount || 0).toFixed(2)); }
function monthLabel(monthKey) { const [,m] = monthKey.split("-"); return MONTH_NAMES[parseInt(m,10)-1] || monthKey; }

function applyHeaderStyle(row) { row.font = { bold: true, size: 11 }; row.alignment = { horizontal: "left" }; }
function applySectionTotalStyle(row, colCount) {
  row.font = { bold: true, size: 11 };
  for (let i = 2; i <= colCount; i++) row.getCell(i).border = { top: { style: "thin" } };
}
function applyGrandTotalStyle(row, colCount) {
  row.font = { bold: true, size: 12 };
  for (let i = 2; i <= colCount; i++) row.getCell(i).border = { top: { style: "thin" }, bottom: { style: "double" } };
}
function setCurrencyFormat(row, startCol, endCol) {
  for (let i = startCol; i <= endCol; i++) row.getCell(i).numFmt = CURRENCY_FORMAT;
}

function buildPnlSheet(workbook, pnl) {
  const ws = workbook.addWorksheet("Profit & Loss");
  const hasMulti = pnl.months.length > 1;
  const dataCols = hasMulti ? pnl.months.length + 1 : 1;
  const totalCols = 1 + dataCols;

  ws.getColumn(1).width = 30;
  for (let i = 2; i <= totalCols; i++) ws.getColumn(i).width = 15;

  const titleRow = ws.addRow([pnl.entityName]); titleRow.font = { bold: true, size: 14 };
  const subRow = ws.addRow(["Profit & Loss Statement"]); subRow.font = { size: 12 };
  const dateRow = ws.addRow([`${pnl.dateStart} to ${pnl.dateEnd}`]); dateRow.font = { size: 10, color: { argb: "FF666666" } };
  ws.addRow([]);

  if (hasMulti) {
    const headerRow = ws.addRow(["", ...pnl.months.map(monthLabel), "Total"]);
    applyHeaderStyle(headerRow);
    for (let i = 2; i <= totalCols; i++) headerRow.getCell(i).alignment = { horizontal: "right" };
  } else {
    const headerRow = ws.addRow(["", "Amount"]);
    applyHeaderStyle(headerRow);
    headerRow.getCell(2).alignment = { horizontal: "right" };
  }

  function addCategoryRows(section) {
    const hdr = ws.addRow([section.name]); hdr.font = { bold: true, size: 11 };
    ws.addRow([]);
    for (const cat of section.categories) {
      if (hasMulti) {
        const vals = pnl.months.map(m => fmt(cat.monthly[m]));
        const row = ws.addRow([`  ${cat.name}`, ...vals, fmt(cat.total)]);
        setCurrencyFormat(row, 2, totalCols);
      } else {
        const row = ws.addRow([`  ${cat.name}`, fmt(cat.total)]);
        setCurrencyFormat(row, 2, 2);
      }
    }
    const totalLabel = `Total ${section.name}`;
    if (hasMulti) {
      const monthTotals = pnl.months.map(m => fmt(section.categories.reduce((s,c) => s + (c.monthly[m]||0), 0)));
      const row = ws.addRow([totalLabel, ...monthTotals, fmt(section.sectionTotal)]);
      setCurrencyFormat(row, 2, totalCols); applySectionTotalStyle(row, totalCols);
    } else {
      const row = ws.addRow([totalLabel, fmt(section.sectionTotal)]);
      setCurrencyFormat(row, 2, 2); applySectionTotalStyle(row, 2);
    }
    ws.addRow([]);
  }

  const rev = pnl.sections.find(s => s.name === "Revenue");
  const cogs = pnl.sections.find(s => s.name === "Cost of Goods Sold");
  const opex = pnl.sections.find(s => s.name === "Operating Expenses");
  if (rev) addCategoryRows(rev);
  if (cogs) addCategoryRows(cogs);

  // Gross Profit
  if (hasMulti) {
    const gp = pnl.months.map(m => {
      const r = rev?.categories.reduce((s,c) => s + (c.monthly[m]||0), 0) || 0;
      const c = cogs?.categories.reduce((s,c2) => s + (c2.monthly[m]||0), 0) || 0;
      return fmt(r - c);
    });
    const gpRow = ws.addRow(["Gross Profit", ...gp, fmt(pnl.summary.grossProfit)]);
    setCurrencyFormat(gpRow, 2, totalCols); applySectionTotalStyle(gpRow, totalCols);
  } else {
    const gpRow = ws.addRow(["Gross Profit", fmt(pnl.summary.grossProfit)]);
    setCurrencyFormat(gpRow, 2, 2); applySectionTotalStyle(gpRow, 2);
  }
  ws.addRow([]);
  if (opex) addCategoryRows(opex);

  // Net Income
  if (hasMulti) {
    const ni = pnl.months.map(m => {
      const r = rev?.categories.reduce((s,c) => s + (c.monthly[m]||0), 0) || 0;
      const c = cogs?.categories.reduce((s,c2) => s + (c2.monthly[m]||0), 0) || 0;
      const o = opex?.categories.reduce((s,c3) => s + (c3.monthly[m]||0), 0) || 0;
      return fmt(r - c - o);
    });
    const niRow = ws.addRow(["Net Income", ...ni, fmt(pnl.summary.netIncome)]);
    setCurrencyFormat(niRow, 2, totalCols); applyGrandTotalStyle(niRow, totalCols);
  } else {
    const niRow = ws.addRow(["Net Income", fmt(pnl.summary.netIncome)]);
    setCurrencyFormat(niRow, 2, 2); applyGrandTotalStyle(niRow, 2);
  }
}

function buildBalanceSheetSheet(workbook, bs) {
  const ws = workbook.addWorksheet("Balance Sheet");
  ws.getColumn(1).width = 30; ws.getColumn(2).width = 18;
  ws.addRow(["Cash-Basis Balance Sheet"]).font = { bold: true, size: 14 };
  ws.addRow([`As of ${bs.asOfDate}`]).font = { size: 10, color: { argb: "FF666666" } };
  ws.addRow([]);
  ws.addRow(["ASSETS"]).font = { bold: true, size: 12 };
  ws.addRow([]);
  ws.addRow(["Cash & Cash Equivalents"]).font = { bold: true, size: 11 };
  for (const acct of bs.assets.cash.accounts) {
    const row = ws.addRow([`  ${acct.name}`, fmt(acct.balance)]); setCurrencyFormat(row, 2, 2);
  }
  const ta = ws.addRow(["Total Assets", fmt(bs.assets.cash.total)]); setCurrencyFormat(ta, 2, 2); applySectionTotalStyle(ta, 2);
  ws.addRow([]); ws.addRow([]);
  ws.addRow(["EQUITY"]).font = { bold: true, size: 12 }; ws.addRow([]);
  let r = ws.addRow(["Beginning Balance", fmt(bs.equity.beginningBalance)]); setCurrencyFormat(r, 2, 2);
  r = ws.addRow(["Net Income", fmt(bs.equity.netIncome)]); setCurrencyFormat(r, 2, 2);
  if (bs.equity.ownerDraws !== 0) { r = ws.addRow(["Owner Draws/Distributions", fmt(bs.equity.ownerDraws)]); setCurrencyFormat(r, 2, 2); }
  const te = ws.addRow(["Total Equity", fmt(bs.equity.endingBalance)]); setCurrencyFormat(te, 2, 2); applyGrandTotalStyle(te, 2);
}

function buildCashFlowSheet(workbook, cf) {
  const ws = workbook.addWorksheet("Cash Flow");
  ws.getColumn(1).width = 30; ws.getColumn(2).width = 18;
  ws.addRow(["Statement of Cash Flows"]).font = { bold: true, size: 14 };
  ws.addRow([`${cf.dateStart} to ${cf.dateEnd}`]).font = { size: 10, color: { argb: "FF666666" } };
  ws.addRow([]);
  ws.addRow(["OPERATING ACTIVITIES"]).font = { bold: true, size: 12 }; ws.addRow([]);
  for (const item of cf.operating.items) { const r = ws.addRow([`  ${item.name}`, fmt(item.amount)]); setCurrencyFormat(r, 2, 2); }
  const ot = ws.addRow(["Net Cash from Operations", fmt(cf.operating.total)]); setCurrencyFormat(ot, 2, 2); applySectionTotalStyle(ot, 2);
  ws.addRow([]);
  if (cf.financing.items.length > 0) {
    ws.addRow(["FINANCING ACTIVITIES"]).font = { bold: true, size: 12 }; ws.addRow([]);
    for (const item of cf.financing.items) { const r = ws.addRow([`  ${item.name}`, fmt(item.amount)]); setCurrencyFormat(r, 2, 2); }
    const ft = ws.addRow(["Net Cash from Financing", fmt(cf.financing.total)]); setCurrencyFormat(ft, 2, 2); applySectionTotalStyle(ft, 2);
    ws.addRow([]);
  }
  const nc = ws.addRow(["Net Change in Cash", fmt(cf.netChange)]); setCurrencyFormat(nc, 2, 2); applySectionTotalStyle(nc, 2);
  ws.addRow([]);
  let r = ws.addRow(["Beginning Cash Balance", fmt(cf.beginningCash)]); setCurrencyFormat(r, 2, 2);
  r = ws.addRow(["Ending Cash Balance", fmt(cf.endingCash)]); setCurrencyFormat(r, 2, 2); applyGrandTotalStyle(r, 2);
}

function buildTransactionDetailSheet(workbook, transactions) {
  const ws = workbook.addWorksheet("Transaction Detail");
  ws.columns = [
    { header: "Date", key: "date", width: 12 },
    { header: "Counterparty", key: "counterparty", width: 25 },
    { header: "Description", key: "description", width: 30 },
    { header: "Amount", key: "amount", width: 14 },
    { header: "Category", key: "category", width: 22 },
    { header: "Confidence", key: "confidence", width: 12 },
  ];
  ws.getRow(1).font = { bold: true };
  for (const tx of transactions) {
    const row = ws.addRow({
      date: tx.date || tx.posted_at || "",
      counterparty: tx.counterparty || tx.counterparty_name || "",
      description: tx.description || tx.bank_description || "",
      amount: fmt(tx.amount),
      category: tx.category || "Uncategorized",
      confidence: tx.confidence != null ? Number((tx.confidence * 100).toFixed(0)) + "%" : "",
    });
    row.getCell("amount").numFmt = CURRENCY_FORMAT;
  }
  ws.autoFilter = { from: { row: 1, column: 1 }, to: { row: 1, column: 6 } };
  ws.views = [{ state: "frozen", ySplit: 1 }];
}

export async function generateBooksExcel(pnl, balanceSheet, cashFlow, transactions) {
  const workbook = new ExcelJS.Workbook();
  workbook.creator = "Heath Ledger";
  workbook.created = new Date();
  buildPnlSheet(workbook, pnl);
  buildBalanceSheetSheet(workbook, balanceSheet);
  buildCashFlowSheet(workbook, cashFlow);
  buildTransactionDetailSheet(workbook, transactions);
  return workbook.xlsx.writeBuffer();
}
