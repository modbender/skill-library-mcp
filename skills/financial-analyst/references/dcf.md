# DCF Model Guide

## Purpose

Build a standard 5-year DCF with WACC via CAPM and terminal value via Gordon Growth.

## Required Inputs

- Historical income statement, cash flow, and balance sheet
- Shares outstanding and net debt (or cash and debt)
- Tax rate assumption (effective or statutory)
- Risk-free rate, equity risk premium, and beta (or enough data to estimate)

## Core Steps

1. Normalize historicals (one-time items, non-recurring revenue/expense).
2. Build revenue and margin drivers (volume, price, mix, unit economics).
3. Forecast operating expenses, D&A, capex, and working capital.
4. Compute unlevered free cash flow (UFCF).
5. Compute WACC and discount UFCF.
6. Compute terminal value and discount to present.
7. Derive equity value and per-share value.
8. Build a sensitivity table (WACC vs terminal growth).

## Standard Formulas

- UFCF = EBIT * (1 - tax rate) + D&A - Capex - Change in NWC
- WACC = (E / V) * Re + (D / V) * Rd * (1 - tax rate)
- Re (CAPM) = Risk-free + Beta * Equity Risk Premium (+ size or specific premium if required)
- Terminal Value (Gordon) = Final Year UFCF * (1 + g) / (WACC - g)
- Equity Value = Enterprise Value - Net Debt (+ other adjustments if needed)
- Per Share = Equity Value / Diluted Shares

## Checks and QA

- Keep units consistent (USD, millions, etc.) across all tabs.
- Reconcile cash flow line items to balance sheet movement where possible.
- Keep terminal growth below or near long-term GDP growth for the market.
- Ensure WACC is higher than terminal growth; flag if not.
- Provide an assumptions table for all key drivers.

## Output Expectations

- Valuation summary with EV and equity value
- Sensitivity table (WACC vs terminal growth)
- Assumptions table (revenue growth, margins, capex, NWC, tax rate)
