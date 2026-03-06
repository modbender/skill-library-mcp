# Personal Genomics Dashboard

Interactive visualization for genetic analysis results. Runs entirely in your browser — no data is uploaded anywhere.

## Quick Start

### Option 1: Drag & Drop
1. Open `index.html` in your browser
2. Drag your `agent_summary.json` or `full_analysis.json` onto the drop zone
3. Explore your results!

### Option 2: Auto-Generated
When you run the analysis, the dashboard is automatically generated:
```bash
python comprehensive_analysis.py ~/dna-analysis/raw_data.txt
# Dashboard auto-opens at ~/dna-analysis/reports/dashboard.html
```

### Option 3: Generate Manually
```python
from dashboard_generator import generate_dashboard

generate_dashboard(
    json_path="~/dna-analysis/reports/agent_summary.json",
    output_path="~/dna-analysis/reports/dashboard.html",
    auto_open=True
)
```

## Features

### 📊 Overview
- Summary statistics (SNPs analyzed, format, alerts)
- Critical alerts prominently displayed
- High priority findings with recommendations

### 💊 Pharmacogenomics
- Drug-gene interactions table
- Search/filter functionality
- Risk variants highlighted

### 📈 Health Risks (PRS)
- Polygenic risk score visualizations
- Percentile bars with color coding
- Confidence indicators

### 🧬 Traits
- Visual trait cards with icons
- Searchable trait library
- Gene and genotype details

### 🌍 Ancestry
- Haplogroup display (mtDNA, Y-DNA)
- Ancestry composition if available
- Migration history context

### 🧪 Carrier Status
- Clear carrier variant display
- Condition descriptions
- Recommendations for genetic counseling

### 😴 Sleep Profile
- Chronotype visualization
- Caffeine metabolism indicator
- Personalized timing recommendations

### 🏃 Athletic Profile
- Power vs Endurance gauge
- Training recommendations
- Sport suitability

### ☀️ UV/Skin
- Skin type estimation
- SPF recommendations
- Melanoma risk indicators

### 🥗 Dietary
- Food interaction matrix
- Tolerance indicators
- Personalized nutrition notes

## Interface Features

- **Dark Mode**: Toggle with 🌙/☀️ button
- **Collapsible Sections**: Click headers to collapse/expand
- **Search**: Filter tables and traits
- **Print/PDF**: Use the Export PDF button (or Cmd/Ctrl+P)
- **Mobile Responsive**: Works on phones and tablets

## Privacy

🔒 **All processing happens locally in your browser.**

- No data is uploaded to any server
- No network requests are made
- Your genetic data never leaves your device

## Browser Support

- Chrome/Edge 80+
- Firefox 75+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Android)

## Customization

### Theming
Edit CSS variables in `<style>` section:
```css
:root {
    --accent-primary: #4f46e5;  /* Change main color */
    --radius: 12px;             /* Card border radius */
}
```

### Adding Sections
1. Add HTML section in `<main>`
2. Add render function in `<script>`
3. Call from `renderDashboard()`

## Troubleshooting

**Dashboard shows "No data available":**
- Ensure JSON file is valid
- Check browser console for errors
- Try both `agent_summary.json` and `full_analysis.json`

**Charts not rendering:**
- Ensure JavaScript is enabled
- Try a different browser
- Check for ad blockers interfering

**PDF export issues:**
- Use Chrome for best print results
- Disable "Headers and footers" in print dialog
- Set margins to "Minimum"

## Technical Notes

- Single HTML file with inline CSS/JS
- No external dependencies (except optional Chart.js CDN)
- ~70KB total size
- Vanilla JavaScript (no framework)
- SVG-based visualizations

## License

MIT License - part of the personal-genomics skill package.
