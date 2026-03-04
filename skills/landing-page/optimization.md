# Landing Page Optimization

## Pre-Launch Checklist

### Performance
- [ ] Page loads in <3 seconds (test: PageSpeed Insights)
- [ ] Images compressed and lazy-loaded
- [ ] No render-blocking resources
- [ ] Core Web Vitals passing

### Mobile
- [ ] Fully responsive (test at 375px width)
- [ ] Tap targets minimum 44px
- [ ] CTA visible without scrolling on mobile
- [ ] Text readable without zooming

### Accessibility
- [ ] Sufficient color contrast (4.5:1 for text)
- [ ] Alt text on all images
- [ ] Focusable interactive elements
- [ ] Keyboard navigation works

### Tracking
- [ ] Analytics installed (GA4, Plausible, or similar)
- [ ] CTA button click events tracked
- [ ] Form submission events tracked
- [ ] UTM parameters preserved

---

## Analytics Setup

### Essential Events

| Event | When to fire | What to track |
|-------|--------------|---------------|
| page_view | On load | Source, device, location |
| cta_click | CTA button click | Button text, position |
| form_start | First field interaction | Form ID |
| form_submit | Form completed | Form ID, time to complete |
| scroll_depth | 25%, 50%, 75%, 100% | Percentage |

### Key Metrics

| Metric | Good | Great |
|--------|------|-------|
| Bounce rate | <60% | <40% |
| Avg time on page | >30s | >60s |
| Scroll depth (50%+) | >40% | >60% |
| CTA click rate | >3% | >8% |
| Form conversion | >10% | >25% |

---

## A/B Testing

### What to Test (High Impact)

1. **Headline** — Different angles, specificity
2. **CTA copy** — Button text and surrounding copy
3. **Hero image** — Product vs outcome vs human
4. **Social proof** — Testimonials vs stats vs logos
5. **Form length** — Fields required vs optional

### Testing Rules

- One variable at a time
- Run until statistical significance (use calculator)
- Minimum 100 conversions per variant
- Test during consistent traffic periods
- Document everything

### Minimum Sample Size

| Baseline Rate | Detectable Lift | Sample per Variant |
|---------------|-----------------|-------------------|
| 2% | 20% | ~10,000 |
| 5% | 20% | ~4,000 |
| 10% | 20% | ~2,000 |
| 20% | 20% | ~1,000 |

---

## Common Problems & Fixes

### High Bounce Rate

| Cause | Fix |
|-------|-----|
| Slow load time | Compress images, defer scripts |
| Mismatch with ad/source | Align messaging |
| Confusing hero | Clearer headline, simpler layout |
| Wrong traffic | Review targeting, keyword match |

### Low CTA Clicks

| Cause | Fix |
|-------|-----|
| CTA not visible | Move above fold |
| Weak CTA copy | Action verb + benefit |
| Too many options | Single CTA per section |
| No urgency | Add scarcity or incentive |

### High Form Abandonment

| Cause | Fix |
|-------|-----|
| Too many fields | Remove non-essential |
| Privacy concerns | Add trust signals |
| Confusing labels | Test with real users |
| Mobile issues | Larger inputs, auto-complete |

---

## Iteration Cycle

1. **Baseline** — Run current page for 1-2 weeks, establish metrics
2. **Hypothesize** — "If we change X, metric Y will improve because Z"
3. **Test** — A/B test single change
4. **Analyze** — Wait for significance, review segments
5. **Implement** — Winner becomes new baseline
6. **Repeat** — Never stop testing

### Prioritization Matrix

| Impact | Effort | Priority |
|--------|--------|----------|
| High | Low | Do first |
| High | High | Plan carefully |
| Low | Low | Quick wins |
| Low | High | Skip |

---

## Tools

### Analytics
- Google Analytics 4 (free, comprehensive)
- Plausible (privacy-focused, simple)
- Mixpanel (event-based, funnels)

### A/B Testing
- Google Optimize (deprecated, but alternatives exist)
- Optimizely (enterprise)
- VWO (mid-market)
- PostHog (open source)

### Heatmaps & Session Recording
- Hotjar (freemium)
- FullStory (enterprise)
- Microsoft Clarity (free)

### Performance
- PageSpeed Insights (free)
- GTmetrix (free)
- WebPageTest (free, detailed)
