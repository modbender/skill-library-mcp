# CRO Tools Reference

## Analytics Platforms

| Platform | Best For |
|----------|----------|
| Google Analytics 4 | Free, funnel analysis, traffic sources |
| Mixpanel | Event-based funnels, SaaS products |
| Amplitude | Behavioral cohorts, user paths |

**Key reports to check:**
- Funnel exploration (drop-off points)
- Path exploration (user journeys)
- Cohort analysis (retention)

## A/B Testing Tools

| Tool | Best For |
|------|----------|
| VWO | Visual editor, marketing teams |
| Optimizely | Enterprise, server-side testing |
| Google Optimize | Budget-conscious, GA integration |
| LaunchDarkly | Feature flags, product teams |

**Choosing a tool:**
- Low traffic (<5k/month): Use simpler tools or qualitative testing
- Medium traffic: VWO or AB Tasty
- High traffic: Optimizely or custom solution

## Heatmaps and Session Recording

| Tool | Best For |
|------|----------|
| Hotjar | All-in-one (heatmaps, recordings, feedback) |
| FullStory | Frustration detection, rage clicks |
| Microsoft Clarity | Free alternative, unlimited recordings |

**Use for:** Hypothesis generation, understanding WHY users drop off.

## Form Analytics

| Tool | Best For |
|------|----------|
| Zuko | Field-level analysis, enterprise |
| Hotjar Forms | Basic metrics, part of Hotjar suite |

**Key metrics:** Time per field, abandonment by field, error rates.

## Speed Testing

| Tool | Best For |
|------|----------|
| PageSpeed Insights | Quick Core Web Vitals check |
| WebPageTest | Detailed waterfall analysis |
| Lighthouse | CI integration, local testing |

**Remember:** Speed directly impacts conversion. A 1-second delay can reduce conversions by 7%.

## Recommended Stack by Stage

| Stage | Stack |
|-------|-------|
| Startup | GA4 + Clarity + PageSpeed |
| Growth | GA4 + Mixpanel + Hotjar + VWO |
| Scale | Amplitude + FullStory + Optimizely |

## Event Naming Convention

Use consistent naming across all tools:
```
[Object]_[Action]
form_started
form_submitted
checkout_initiated
purchase_completed
```

This enables cross-tool analysis and easier debugging.
