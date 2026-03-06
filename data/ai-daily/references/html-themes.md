# HTML Theme Prompts

This document contains prompt templates for generating themed HTML webpages.

---

## Apple Style Theme

Generate a clean, minimalist HTML page inspired by Apple's design language.

### Design Principles

- **Minimalist philosophy**: Every pixel serves a purpose
- **Generous white space**: Content density ≤ 40%
- **Typography-first**: SF Pro Display for headings, SF Pro Text for body
- **Subtle visual effects**: Gentle glows, smooth transitions
- **Rim lighting**: Studio-quality soft lighting

### Color Palette

```css
--bg-color: #000000              /* Pure black background */
--glow-start: #0A1929           /* Deep blue */
--glow-end: #1A3A52             /* Midnight blue */
--title-color: #FFFFFF           /* Pure white */
--text-color: #E3F2FD            /* High brightness blue-white */
--accent-color: #42A5F5          /* Sky blue for highlights */
--secondary-color: #B0BEC5       /* Medium gray for secondary info */
```

### Structure

```html
<body>
  <div class="background-glow"></div>
  <div class="geometric-lines"></div>

  <div class="container">
    <header>
      <div class="logo-icon">🤖</div>
      <h1>AI Daily</h1>
      <div class="date-badge">2026年1月13日 星期一</div>
    </header>

    <main>
      <section class="summary-card">
        <h2>核心摘要</h2>
        <!-- Summary items -->
      </section>

      <section class="category-section">
        <h2>模型发布</h2>
        <!-- News cards -->
      </section>

      <!-- More categories -->

      <footer class="keywords-footer">
        #Anthropic #Google #MedGemma
      </footer>
    </main>
  </div>
</body>
```

### Key CSS Effects

```css
/* Background glow - bottom-right corner */
.background-glow {
  position: fixed;
  bottom: -20%;
  right: -20%;
  width: 70%;
  height: 70%;
  background: radial-gradient(
    circle at center,
    var(--glow-end) 0%,
    var(--glow-start) 40%,
    transparent 80%
  );
  opacity: 0.6;
  filter: blur(80px);
  z-index: -2;
}

/* Geometric lines - 15% opacity */
.geometric-lines {
  position: fixed;
  background-image:
    linear-gradient(90deg, transparent 49%, var(--accent-color) 50%, transparent 51%),
    linear-gradient(0deg, transparent 49%, var(--accent-color) 50%, transparent 51%);
  background-size: 200px 200px;
  opacity: 0.08;
  z-index: -1;
}

/* Glowing logo icon */
.logo-icon {
  animation: glow-pulse 3s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% {
    box-shadow: 0 0 40px var(--accent-color), 0 0 80px var(--accent-color);
  }
  50% {
    box-shadow: 0 0 50px var(--accent-color), 0 0 100px var(--accent-color);
  }
}
```

### Full Prompt

```
Generate an HTML webpage with Apple-style minimalist design for AI news summary.

## Content
{markdown_content}

## Design Requirements

**Colors** (Black background with blue glow):
- Background: #000000
- Title: #FFFFFF
- Body text: #E3F2FD
- Accent: #42A5F5 (for highlights and icons)
- Secondary: #B0BEC5

**Layout**:
- Centered container, max-width 900px
- Content density ≤ 40% (generous white space)
- Padding: 40px 20px

**Typography**:
- Headings: SF Pro Display, 24-48px, pure white
- Body: SF Pro Text, 16px, #E3F2FD
- Line height: 1.6

**Visual Effects**:
- Background glow from bottom-right corner (radial gradient, blur 80px)
- Subtle geometric lines pattern (15% opacity)
- Glowing logo icon with pulse animation
- Smooth hover transitions on cards

**Structure**:
```
<header>: Logo + Date badge
<main>:
  - Summary card (rounded, subtle border)
  - Category sections with cards
  - Keywords footer
<footer>: Copyright
```

**Card Style**:
- Background: rgba(255,255,255,0.05) with backdrop-filter blur
- Border: 1px solid rgba(255,255,255,0.1)
- Border radius: 12px
- Padding: 20px
- Hover: border color changes to accent color

**Output**: Complete single HTML file with inline CSS, no external dependencies.
```

---

## Ocean Calm Theme (深海蓝)

Business professional style for product announcements.

### Color Palette

```css
--bg-color: #000000
--glow-start: #0F1C3F           /* Deep indigo */
--glow-end: #1A2F5A             /* Royal blue */
--title-color: #FFFFFF
--text-color: #E3F2FD
--accent-color: #5C9FE5          /* Bright blue */
--secondary-color: #BBDEFB       /* Light blue */
```

### Prompt

```
Generate a professional business-style HTML webpage for AI news.

## Content
{markdown_content}

## Design: Ocean Calm Theme

Professional blue tones suitable for business updates and product launches.

**Colors**:
- Background: #000000
- Glow: Deep indigo (#0F1C3F) to royal blue (#1A2F5A)
- Title: #FFFFFF
- Body: #E3F2FD
- Accent: #5C9FE5 (bright blue)
- Secondary: #BBDEFB

**Style**: Corporate, trustworthy, data-driven.
```

---

## Autumn Warm Theme (秋日暖阳)

Warm vibrant style for community updates and lively discussions.

### Color Palette

```css
--bg-color: #000000
--glow-start: #1F1410           /* Deep brown */
--glow-end: #3D2415             /* Warm brown */
--title-color: #FFFFFF
--text-color: #FFF3E0            /* Warm white */
--accent-color: #FFA726          /* Bright orange */
--secondary-color: #FFCCBC       /* Light orange */
```

### Prompt

```
Generate a warm, vibrant HTML webpage for AI news.

## Content
{markdown_content}

## Design: Autumn Warm Theme

Warm orange tones for community-focused content.

**Colors**:
- Background: #000000
- Glow: Deep brown (#1F1410) to warm brown (#3D2415)
- Title: #FFFFFF
- Body: #FFF3E0 (warm white)
- Accent: #FFA726 (bright orange)
- Secondary: #FFCCBC

**Style**: Energetic, friendly, community-focused.
```

---

## Theme Comparison

| Theme | Style | Best For |
|--------|-------|----------|
| **Apple Style** | Minimalist, professional | Technical content, product reviews |
| **Ocean Calm** | Corporate, business | Business updates, announcements |
| **Autumn Warm** | Energetic, friendly | Community news, discussions |

---

## Usage in Skill

When user selects a theme, apply the corresponding prompt template and generate the HTML.

**Example workflow**:

1. User: "昨天AI资讯，生成网页"
2. Claude: "可选主题: 苹果风 / 深海蓝 / 秋日暖阳"
3. User: "苹果风"
4. Claude: Uses Apple Style Theme prompt to generate HTML
5. Save to `docs/{date}.html`
