export function renderKPIs(data: any) {
  return `
## 📊 FutureFulfillment KPIs

| Metric | Value |
|--------|-------|
| Open Picklists | ${data.open_count} |
| Closed Today | ${data.closed_today} |
| Pickers Active | ${data.active_pickers} |
| Stock Movements | ${data.stock_moves} |
`;
}

export function renderPickerStats(pickers: any[]) {
  return `
## 👤 Picker Performance (Today)

| Picker | Open | Closed | Total | Efficiency |
|--------|------|--------|-------|------------|
${pickers.map(p => `| ${p.name} | ${p.open} | ${p.closed} | ${p.total} | ${p.efficiency}% |`).join('\n')}
`;
}

export function renderStockTable(movements: any[]) {
  return `
## 📦 Stock Movements by Client (Sortable)

| Client | Stock In | Stock Out | Net | Value |
|--------|----------|-----------|-----|-------|
${movements.map(m => `| ${m.client} | +${m.in} | -${m.out} | ${m.net > 0 ? `+${m.net}` : m.net} | €${m.value} |`).join('\n')}
`;
}
