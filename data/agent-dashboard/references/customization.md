# Customization Guide

This guide covers how to customize Mission Control's appearance and functionality.

## Changing the Theme

### Color Variables

The dashboard uses CSS custom properties for colors. Edit the `:root` section:

```css
:root {
    /* Background colors */
    --bg-primary: #0a0a0b;     /* Main background */
    --bg-secondary: #111113;    /* Secondary background */
    --bg-tertiary: #18181b;     /* Card backgrounds */
    --bg-card: #1a1a1d;         /* Elevated cards */
    --bg-hover: #222225;        /* Hover states */

    /* Border colors */
    --border: #27272a;          /* Default borders */
    --border-light: #3f3f46;    /* Light borders */

    /* Text colors */
    --text-primary: #fafafa;    /* Primary text */
    --text-secondary: #a1a1aa;  /* Secondary text */
    --text-muted: #71717a;      /* Muted text */

    /* Accent colors */
    --accent-blue: #3b82f6;     /* Primary accent */
    --accent-green: #22c55e;    /* Success/live */
    --accent-yellow: #eab308;   /* Warning/testing */
    --accent-red: #ef4444;      /* Error/down */
    --accent-purple: #a855f7;   /* Branding */
    --accent-orange: #f97316;   /* Urgent/attention */
}
```

### Light Theme

For a light theme, swap the color scheme:

```css
:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f9fafb;
    --bg-tertiary: #f3f4f6;
    --bg-card: #ffffff;
    --bg-hover: #e5e7eb;
    --border: #e5e7eb;
    --border-light: #d1d5db;
    --text-primary: #111827;
    --text-secondary: #4b5563;
    --text-muted: #9ca3af;
}
```

## Changing the Logo

Replace the logo icon emoji:

```html
<div class="logo-icon">🚀</div>
```

Options:
- Different emoji: `🎯`, `⚡`, `🔮`, `💫`, `🌟`
- SVG icon: Replace the emoji with an `<svg>` element
- Image: Use an `<img>` tag

For an image logo:

```html
<div class="logo-icon">
    <img src="your-logo.png" alt="Logo" style="width: 24px; height: 24px;">
</div>
```

## Adding Custom Sections

### New Card Section

Add a new card to the grid:

```html
<div class="card">
    <div class="card-header">
        <span class="icon">🎯</span>
        <h2>Custom Section</h2>
    </div>
    <div id="custom-section">
        <!-- Your content here -->
    </div>
</div>
```

### Render Function

Add rendering logic:

```javascript
function renderDashboard(data) {
    // ... existing code ...

    // Custom section
    const customSection = document.getElementById('custom-section');
    if (data.customData) {
        customSection.innerHTML = data.customData.map(item => `
            <div class="custom-item">${item.name}</div>
        `).join('');
    }
}
```

### Update Data Schema

Add to your `dashboard-data.json`:

```json
{
    "customData": [
        {"name": "Item 1", "value": 100},
        {"name": "Item 2", "value": 200}
    ]
}
```

## Hiding Sections

### Remove a Section

Delete or comment out the card HTML. For example, to remove Products:

```html
<!-- Remove this entire card -->
<div class="card">
    <div class="card-header">
        <span class="icon">📊</span>
        <h2>Products</h2>
    </div>
    <div class="product-grid" id="products-grid"></div>
</div>
```

### Conditional Display

Show sections based on data:

```javascript
// Only show products section if there are products
const productsCard = document.getElementById('products-card');
if (data.products && data.products.length > 0) {
    productsCard.style.display = 'block';
} else {
    productsCard.style.display = 'none';
}
```

## Modifying the Grid Layout

### Two-Column Fixed

```css
.grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
}
```

### Three-Column

```css
.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
}
```

### Full-Width Card

```css
.full-width {
    grid-column: 1 / -1;
}
```

```html
<div class="card full-width">
    <!-- Spans all columns -->
</div>
```

## Changing Refresh Interval (Tier 2)

In `tier2-github.html`:

```javascript
const CONFIG = {
    // ...
    REFRESH_INTERVAL: 30000  // Change to desired ms (e.g., 60000 for 1 minute)
};
```

## Custom Fonts

Replace Inter with your preferred font:

```html
<link href="https://fonts.googleapis.com/css2?family=YOUR_FONT:wght@400;500;600;700&display=swap" rel="stylesheet">
```

```css
body {
    font-family: 'YOUR_FONT', -apple-system, BlinkMacSystemFont, sans-serif;
}
```

## Adding Charts

### Using Chart.js

Add to `<head>`:

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

Add a canvas:

```html
<div class="card">
    <div class="card-header">
        <span class="icon">📈</span>
        <h2>Traffic</h2>
    </div>
    <canvas id="traffic-chart"></canvas>
</div>
```

Initialize in JavaScript:

```javascript
function renderDashboard(data) {
    // ... existing code ...

    // Traffic chart
    if (data.traffic) {
        const ctx = document.getElementById('traffic-chart');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.traffic.map(d => d.date),
                datasets: [{
                    label: 'Visitors',
                    data: data.traffic.map(d => d.visitors),
                    borderColor: 'var(--accent-blue)',
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } }
            }
        });
    }
}
```

## Mobile Optimization

### Larger Touch Targets

```css
@media (max-width: 768px) {
    .cron-row, .activity-item, .product-card {
        padding: 16px;
        min-height: 48px;
    }
}
```

### Stack Everything

```css
@media (max-width: 480px) {
    .grid {
        grid-template-columns: 1fr;
    }
    
    .stats-row {
        flex-direction: column;
    }
    
    .stat-pill {
        width: 100%;
        justify-content: space-between;
    }
}
```

## Accessibility Improvements

### Skip Link

Add at the start of `<body>`:

```html
<a href="#main-content" class="skip-link">Skip to content</a>

<style>
.skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: var(--accent-blue);
    color: white;
    padding: 8px 16px;
    z-index: 100;
}
.skip-link:focus {
    top: 0;
}
</style>
```

### Better Focus States

```css
*:focus {
    outline: 2px solid var(--accent-blue);
    outline-offset: 2px;
}

*:focus:not(:focus-visible) {
    outline: none;
}
```

### ARIA Labels

```html
<button onclick="checkPassword()" aria-label="Submit PIN">
    Access Dashboard
</button>

<div role="status" aria-live="polite" id="connection-status">
    <!-- Connection status -->
</div>
```

## Sound Notifications

Add audio alerts for new action items:

```javascript
function renderDashboard(data) {
    // Check for new action items
    const prevCount = window.lastActionCount || 0;
    const newCount = data.actionRequired?.length || 0;
    
    if (newCount > prevCount) {
        playNotificationSound();
    }
    window.lastActionCount = newCount;

    // ... rest of render code
}

function playNotificationSound() {
    const audio = new Audio('data:audio/wav;base64,UklGRl9vT19...'); // Base64 sound
    audio.volume = 0.3;
    audio.play().catch(() => {}); // Ignore autoplay restrictions
}
```

## Internationalization

### Date/Time Formatting

```javascript
function formatTime(isoString) {
    if (!isoString) return 'never';
    const date = new Date(isoString);
    
    // Use user's locale
    return new Intl.RelativeTimeFormat('auto', {
        numeric: 'auto'
    }).format(
        Math.floor((date - new Date()) / 60000),
        'minute'
    );
}
```

### Translations

```javascript
const i18n = {
    en: {
        activeNow: 'Active Now',
        actionRequired: 'Action Required',
        cronJobs: 'Cron Jobs'
    },
    es: {
        activeNow: 'Activo Ahora',
        actionRequired: 'Acción Requerida',
        cronJobs: 'Trabajos Programados'
    }
};

const lang = navigator.language.split('-')[0];
const t = i18n[lang] || i18n.en;
```

---

For more help, check the main [SKILL.md](../SKILL.md) or open an issue on GitHub.
