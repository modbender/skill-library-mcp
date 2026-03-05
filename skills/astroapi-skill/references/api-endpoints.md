# Astrology API v3 - Endpoint Reference

Base path: `/api/v3`

> This file is auto-generated from the OpenAPI spec. It covers all 241 endpoints organized by category, with request schemas for POST endpoints and query parameters for GET endpoints.

---

## Table of Contents

1. [Common Schemas](#common-schemas)
2. [Data - Raw Data & Positions](#data---raw-data--positions)
3. [Charts - Chart Data & Analysis](#charts---chart-data--analysis)
4. [Chart Rendering](#chart-rendering)
5. [SVG Chart Generation (Deprecated)](#svg-chart-generation-deprecated)
6. [Analysis - Reports & Interpretations](#analysis---reports--interpretations)
7. [Horoscopes & Predictions](#horoscopes--predictions)
8. [PDF Reports](#pdf-reports)
9. [Enhanced Traditional Analysis](#enhanced-traditional-analysis)
10. [Traditional & Hellenistic Astrology](#traditional--hellenistic-astrology)
11. [Horary Astrology](#horary-astrology)
12. [Tarot](#tarot)
13. [Numerology](#numerology)
14. [Vedic Astrology](#vedic-astrology)
15. [Chinese Astrology & BaZi](#chinese-astrology--bazi)
16. [Human Design](#human-design)
17. [Kabbalah](#kabbalah)
18. [Astrocartography & Relocation](#astrocartography--relocation)
19. [Eclipses](#eclipses)
20. [Lunar Features](#lunar-features)
21. [Fixed Stars](#fixed-stars)
22. [Palmistry](#palmistry)
23. [Insights - Relationship](#insights---relationship)
24. [Insights - Pet](#insights---pet)
25. [Insights - Wellness](#insights---wellness)
26. [Insights - Financial](#insights---financial)
27. [Insights - Business](#insights---business)
28. [Feng Shui & Flying Stars](#feng-shui--flying-stars)
29. [Zi Wei Dou Shu](#zi-wei-dou-shu)
30. [Glossary & Reference](#glossary--reference)
31. [Health & Monitoring](#health--monitoring)

---

## Common Schemas

### Subject (charts/analysis endpoints)

Used by most chart, analysis, render, and report endpoints.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | No | Default: "Subject" |
| `birth_data` | DateTimeLocation | **Yes** | See below |

### Subject (standard/insights endpoints)

Used by insights, numerology, human design, and standard endpoints.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | No | |
| `birth_data` | BirthData | **Yes** | See below |
| `email` | string | No | |
| `notes` | string | No | |

### DateTimeLocation

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `year` | integer | **Yes** | |
| `month` | integer | **Yes** | |
| `day` | integer | **Yes** | |
| `hour` | integer | **Yes** | |
| `minute` | integer | **Yes** | |
| `second` | integer | No | Default: 0 |
| `latitude` | number | No | Use lat/lng OR city/country |
| `longitude` | number | No | |
| `city` | string | No | Resolved to coordinates |
| `country_code` | string | No | ISO 2-letter code |
| `timezone` | string | No | IANA timezone |

### BirthData

Same as DateTimeLocation but all fields except `year` are optional (for partial birth data like numerology).

### DateRange

| Field | Type | Required |
|-------|------|----------|
| `start_date` | Date (`{year, month, day}`) | **Yes** |
| `end_date` | Date (`{year, month, day}`) | **Yes** |

### ChartOptions

| Field | Type | Default | Values |
|-------|------|---------|--------|
| `house_system` | string | `"P"` | P (Placidus), W (Whole Sign), K (Koch), A (Equal), R (Regiomontanus), C (Campanus), B (Alcabitius), M (Morinus), O (Porphyry), E (Equal MC), V (Vehlow), X (Axial), H (Horizontal), T (Polich/Page), G (Gauquelin) |
| `zodiac_type` | string | `"Tropic"` | Tropic, Sidereal |
| `active_points` | array[string] | - | Planet/point names to include |
| `precision` | integer | 2 | Decimal places |
| `fixed_stars` | FixedStarsConfig | null | |
| `use_cache` | boolean | true | |

### DataOptions

Extends ChartOptions with:

| Field | Type | Default | Values |
|-------|------|---------|--------|
| `house_system` | HouseSystem | - | P, W, K, A, R, C, O, M |
| `language` | Language | - | See Language enum |
| `tradition` | Tradition | - | universal, classical, psychological, event_oriented, vedic, chinese |
| `perspective` | PerspectiveType | - | geocentric, heliocentric, draconic, barycentric |
| `detail_level` | DetailLevel | - | basic, standard, full, professional |
| `include_interpretations` | boolean | true | |
| `include_raw_data` | boolean | false | |
| `precision_mode` | boolean | false | |

### StandardOptions

Same fields as DataOptions (without zodiac_type, active_points, precision).

### ReportOptions

| Field | Type | Default | Values |
|-------|------|---------|--------|
| `tradition` | string | `"universal"` | universal, psychological, event_oriented, classical |
| `language` | string | `"en"` | See Language enum |

### RenderOptions

| Field | Type | Default | Values |
|-------|------|---------|--------|
| `format` | string | `"svg"` | svg, png, jpg, webp, pdf |
| `width` | integer | null | |
| `scale` | number | 1.0 | |
| `quality` | integer | 90 | |
| `theme` | string | `"dark"` | light, dark, dark-high-contrast, classic |
| `language` | string | `"en"` | See Language enum |

### SVGOptions

| Field | Type | Default | Values |
|-------|------|---------|--------|
| `theme` | string | `"dark"` | light, dark, dark-high-contrast, classic |
| `language` | string | `"en"` | See Language enum |

### Language enum

`en, es, fr, de, it, pt, ru, zh, ja, hi, tr, uk, ar, en-US, en-GB, en-ARCHAIC, pt-BR, pt-PT, es-MX, es-ES, fr-FR, fr-CA, zh-CN, zh-TW`

Extended for some endpoints: `ko, nl, pl`

### FixedStarsConfig

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `presets` | array[string] | - | Star preset groups |
| `custom_orbs` | object | null | Custom orb overrides |
| `include_parans` | boolean | false | |
| `include_heliacal` | boolean | false | |
| `include_interpretations` | boolean | true | |

---

## Data - Raw Data & Positions

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| GET | `/data/now` | Current Time Data | - |
| POST | `/data/positions` | Planetary Positions | DataRequest |
| POST | `/data/house-cusps` | House Cusps | DataRequest |
| POST | `/data/aspects` | Aspects | DataRequest |
| POST | `/data/lunar-metrics` | Lunar Metrics | DataRequest |
| POST | `/data/global-positions` | Global Positions | GlobalDataRequest |
| POST | `/data/positions/enhanced` | Enhanced Positions | DataRequest |
| POST | `/data/aspects/enhanced` | Enhanced Aspects | DataRequest |
| POST | `/data/lunar-metrics/enhanced` | Enhanced Lunar Metrics | DataRequest |

### DataRequest

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `subject` | Subject | **Yes** | Standard Subject |
| `options` | DataOptions | No | |
| `filter_retrograde_only` | boolean | No | Default: false |

### GlobalDataRequest

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `year` | integer | **Yes** | |
| `month` | integer | **Yes** | |
| `day` | integer | **Yes** | |
| `hour` | integer | No | Default: 12 |
| `minute` | integer | No | Default: 0 |
| `second` | integer | No | Default: 0 |
| `options` | DataOptions | No | |

---

## Charts - Chart Data & Analysis

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/charts/natal` | Natal Chart | NatalChartRequest |
| POST | `/charts/synastry` | Synastry (two charts) | SynastryChartRequest |
| POST | `/charts/composite` | Composite (relationship entity) | CompositeChartRequest |
| POST | `/charts/transit` | Transit Snapshot | TransitChartRequest |
| POST | `/charts/solar-return` | Solar Return | SolarReturnRequest |
| POST | `/charts/lunar-return` | Lunar Return | LunarReturnRequest |
| POST | `/charts/solar-return-transits` | Solar Return Transits | SolarReturnTransitRequest |
| POST | `/charts/lunar-return-transits` | Lunar Return Transits | LunarReturnTransitRequest |
| POST | `/charts/progressions` | Progressions | ProgressionRequest |
| POST | `/charts/directions` | Directions | DirectionRequest |
| POST | `/charts/natal-transits` | Transit Period Analysis (date range) | NatalTransitRequest |

### NatalChartRequest

`subject` (Subject, required), `options` (ChartOptions)

### SynastryChartRequest

`subject1` (Subject, required), `subject2` (Subject, required), `options` (ChartOptions)

### CompositeChartRequest

`subject1` (Subject, required), `subject2` (Subject, required), `options` (ChartOptions)

### TransitChartRequest

`subject` (Subject), `transit_time` (TransitTime), `natal_subject` (Subject), `transit_datetime` (DateTimeLocation), `options` (ChartOptions)

### SolarReturnRequest

| Field | Type | Required |
|-------|------|----------|
| `subject` | Subject | **Yes** |
| `return_year` | integer | **Yes** |
| `return_location` | DateTimeLocation | No |
| `options` | ChartOptions | No |

### LunarReturnRequest

| Field | Type | Required |
|-------|------|----------|
| `subject` | Subject | **Yes** |
| `return_date` | string | **Yes** |
| `return_location` | DateTimeLocation | No |
| `options` | ChartOptions | No |

### ProgressionRequest

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `subject` | Subject | **Yes** | |
| `target_date` | string | **Yes** | |
| `progression_type` | string | No | Default: "secondary". Enum: secondary, primary, tertiary, minor |
| `location` | DateTimeLocation | No | |
| `options` | ChartOptions | No | |

### DirectionRequest

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `subject` | Subject | **Yes** | |
| `target_date` | string | **Yes** | |
| `direction_type` | string | No | Default: "solar_arc". Enum: solar_arc, symbolic, profection, naibod |
| `arc_rate` | number | No | |
| `options` | ChartOptions | No | |

### NatalTransitRequest

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `subject` | Subject | No | |
| `transit_time` | TransitTime | No | |
| `natal_subject` | Subject | No | |
| `date_range` | DateRange | No | |
| `orb` | number | No | Default: 1.0 |
| `report_options` | ReportOptions | No | |

### SolarReturnTransitRequest

| Field | Type | Required |
|-------|------|----------|
| `subject` | Subject | **Yes** |
| `return_year` | integer | **Yes** |
| `return_location` | DateTimeLocation | No |
| `options` | ChartOptions | No |
| `date_range` | DateRange | **Yes** |
| `orb` | number | No (default: 1.0) |
| `report_options` | ReportOptions | No |

### LunarReturnTransitRequest

| Field | Type | Required |
|-------|------|----------|
| `subject` | Subject | **Yes** |
| `return_date` | string | **Yes** |
| `return_location` | DateTimeLocation | No |
| `options` | ChartOptions | No |
| `date_range` | DateRange | **Yes** |
| `orb` | number | No (default: 1.0) |
| `report_options` | ReportOptions | No |

---

## Chart Rendering

Returns chart images in various formats (SVG, PNG, JPG, WebP, PDF).

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/render/natal` | Render Natal Chart | NatalChartRenderRequest |
| POST | `/render/synastry` | Render Synastry Chart | SynastryChartRenderRequest |
| POST | `/render/transit` | Render Transit Chart | TransitChartRenderRequest |
| POST | `/render/composite` | Render Composite Chart | CompositeChartRenderRequest |

All render requests include the same fields as their chart counterparts plus `render_options` (RenderOptions).

---

## SVG Chart Generation (Deprecated)

Use `/render/*` endpoints instead.

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/svg/natal` | Natal Chart SVG | NatalChartSVGRequest |
| POST | `/svg/synastry` | Synastry Chart SVG | SynastryChartSVGRequest |
| POST | `/svg/composite` | Composite Chart SVG | CompositeChartSVGRequest |
| POST | `/svg/transit` | Transit Chart SVG | TransitChartSVGRequest |

All SVG requests include the same fields as their chart counterparts plus `svg_options` (SVGOptions).

---

## Analysis - Reports & Interpretations

### Single-subject natal reports

These all use **NatalReportRequest**: `subject` (required), `tradition`, `language`, `report_options`, `fixed_stars`, `include_aspect_patterns` (default: false).

| Method | Path | Summary |
|--------|------|---------|
| POST | `/analysis/natal-report` | Natal Report |
| POST | `/analysis/career` | Career Analysis |
| POST | `/analysis/psychological` | Psychological Analysis |
| POST | `/analysis/karmic` | Karmic Analysis |
| POST | `/analysis/health` | Health Analysis |
| POST | `/analysis/spiritual` | Spiritual Analysis |
| POST | `/analysis/vocational` | Vocational Analysis |

### Two-subject reports

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/analysis/relationship-score` | Relationship Score | SynastryChartRequest |
| POST | `/analysis/synastry-report` | Synastry Report | SynastryReportRequest |
| POST | `/analysis/composite-report` | Composite Report | CompositeReportRequest |
| POST | `/analysis/compatibility-score` | Compatibility Score | SynastryChartRequest |
| POST | `/analysis/compatibility` | Compatibility | CompatibilityRequest |
| POST | `/analysis/relationship` | Relationship Analysis | (generic request body) |

**SynastryReportRequest**: `subject1`, `subject2` (required), `options`, `report_options`, `fixed_stars`, `include_house_overlays` (default: true).

**CompositeReportRequest**: `subject1`, `subject2` (required), `options`, `report_options`.

**CompatibilityRequest**: `subjects` (array[Subject]), `options`, `compatibility_options`.

### Return reports

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/analysis/solar-return-report` | Solar Return Report | SolarReturnReportRequest |
| POST | `/analysis/lunar-return-report` | Lunar Return Report | LunarReturnReportRequest |
| POST | `/analysis/solar-return-transit-report` | Solar Return Transit Report | SolarReturnTransitRequest |
| POST | `/analysis/lunar-return-transit-report` | Lunar Return Transit Report | LunarReturnTransitRequest |

**SolarReturnReportRequest**: `subject` (required), `return_year` (required), `return_location`, `options`, `report_options`, `include_life_areas` (default: true), `life_areas_filter`.

**LunarReturnReportRequest**: `subject` (required), `return_date` (required), `return_location`, `options`, `report_options`.

### Transit and progression reports

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/analysis/natal-transit-report` | Natal Transit Report | NatalTransitRequest |
| POST | `/analysis/transit-report` | Transit Report | NatalTransitRequest |
| POST | `/analysis/predictive` | Predictive Analysis | NatalTransitRequest |
| POST | `/analysis/progression-report` | Progression Report | ProgressionReportRequest |
| POST | `/analysis/direction-report` | Direction Report | DirectionReportRequest |

**ProgressionReportRequest**: `subject` (required), `target_date` (required), `progression_type` (default: "secondary"), `location`, `options`, `report_options`.

**DirectionReportRequest**: `subject` (required), `target_date` (required), `direction_type` (default: "solar_arc"), `arc_rate`, `options`, `report_options`.

### Other analysis

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/analysis/lunar-analysis` | Lunar Analysis | LunarAnalysisRequest |
| POST | `/analysis/relocation` | Relocation Analysis | RelocationChartRequest |

**LunarAnalysisRequest**: `datetime_location` (required), `tradition`, `language`, `report_options`.

---

## Horoscopes & Predictions

### Sun sign horoscopes (structured JSON)

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/horoscope/sign/daily` | Daily Sun Sign | SunSignDailyRequest |
| POST | `/horoscope/sign/weekly` | Weekly Sun Sign | generic object |
| POST | `/horoscope/sign/monthly` | Monthly Sun Sign | generic object |
| POST | `/horoscope/sign/yearly` | Yearly Sun Sign | generic object |

**SunSignDailyRequest**: `sign` (required), `language` (default: "en"), `tradition` (default: "universal"), `minimum_strength` (default: 0.0), `date`.

### Sun sign horoscopes (text format)

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/horoscope/sign/daily/text` | Daily Text | SunSignDailyTextRequest |
| POST | `/horoscope/sign/weekly/text` | Weekly Text | SunSignWeeklyTextRequest |
| POST | `/horoscope/sign/monthly/text` | Monthly Text | SunSignMonthlyTextRequest |
| POST | `/horoscope/sign/yearly/text` | Yearly Text | SunSignYearlyTextRequest |

Text requests add: `format` (short/paragraph/bullets/structured/long, default: "paragraph"), `emoji` (default: true).

Weekly text adds `date` field. Monthly text adds `year`, `month`. Yearly text adds `year`.

### Personalized horoscopes (structured JSON)

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/horoscope/personal/daily` | Daily Personalized | PersonalizedHoroscopeRequest |
| POST | `/horoscope/personal/weekly` | Weekly Personalized | PersonalizedHoroscopeRequest |
| POST | `/horoscope/personal/monthly` | Monthly Personalized | PersonalizedHoroscopeRequest |
| POST | `/horoscope/personal/yearly` | Yearly Personalized | PersonalizedHoroscopeRequest |

**PersonalizedHoroscopeRequest**:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `subject` | Subject | **Yes** | |
| `target_date` | string | No | |
| `horoscope_type` | string | No | Default: "daily". Enum: daily, weekly, monthly, yearly |
| `language` | string | No | Default: "en" |
| `tradition` | string | No | Default: "universal". Enum: universal, psychological, event_oriented, classical |
| `include_transits` | boolean | No | Default: true |
| `include_progressions` | boolean | No | Default: false |
| `include_major_transits` | boolean | No | Default: true |
| `include_retrograde_periods` | boolean | No | Default: true |
| `include_power_periods` | PowerPeriodsConfig | No | `{categories: [...], top_n: 5}` |

### Personalized horoscopes (text format)

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/horoscope/personal/daily/text` | Daily Text | PersonalizedDailyTextRequest |
| POST | `/horoscope/personal/weekly/text` | Weekly Text | PersonalizedWeeklyTextRequest |
| POST | `/horoscope/personal/monthly/text` | Monthly Text | PersonalizedMonthlyTextRequest |
| POST | `/horoscope/personal/yearly/text` | Yearly Text | PersonalizedYearlyTextRequest |

Extends PersonalizedHoroscopeRequest with: `format` (default: "paragraph"), `emoji` (default: true).

### Chinese BaZi Horoscope

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/horoscope/chinese/bazi` | Chinese BaZi Horoscope | ChineseBaZiHoroscopeRequest |

**ChineseBaZiHoroscopeRequest**: `subject` (required), `year` (integer), `language` (default: "en").

---

## PDF Reports

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/pdf/natal-report` | Generate Natal Report PDF | NatalReportPDFRequest |
| POST | `/pdf/horoscope/daily` | Generate Daily Horoscope PDF | DailyHoroscopePDFRequest |
| POST | `/pdf/horoscope/weekly` | Generate Weekly Horoscope PDF | WeeklyHoroscopePDFRequest |
| GET | `/pdf/horoscope/data/{sign}/{target_date}` | Get Daily Horoscope Data | path: sign, target_date; query: language, tradition |

### NatalReportPDFRequest

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `subject` | Subject | **Yes** | |
| `sections` | NatalReportPDFSections | No | |
| `tradition` | string | No | Default: "universal" |
| `chart_options` | NatalChartOptions | No | |
| `pdf_options` | PDFOptionsBase | No | |
| `include_chart_svg` | boolean | No | Default: true |
| `chart_theme` | string | No | Default: "light". Enum: light, dark |

### DailyHoroscopePDFRequest

`sign`, `target_date`, `subject`, `sections`, `pdf_options`, `include_chart_image` (default: false), `chart_theme` (default: "light").

### WeeklyHoroscopePDFRequest

`sign`, `week_start`, `subject`, `sections`, `pdf_options`, `include_chart_image` (default: false), `chart_theme` (default: "light").

### PDFOptionsBase

`page_settings`, `header_footer`, `style`, `branding`, `customization`, `language` (default: "en"), `include_cover_page` (default: true), `include_table_of_contents` (default: false), `watermark_text`.

---

## Enhanced Traditional Analysis

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/enhanced/personal-analysis` | Personal Analysis | PersonalAnalysisRequest |
| POST | `/enhanced/global-analysis` | Global Analysis | GlobalAnalysisRequest |
| POST | `/enhanced_charts/personal-analysis` | Personal Analysis (alt path) | PersonalAnalysisRequest |
| POST | `/enhanced_charts/global-analysis` | Global Analysis (alt path) | GlobalAnalysisRequest |

**PersonalAnalysisRequest**: `subject` (required), `calculation_time` (DateTimeLocation), `options` (ChartOptions), `orbs`.

**GlobalAnalysisRequest**: `calculation_time` (DateTimeLocation), `options` (ChartOptions), `orbs`.

---

## Traditional & Hellenistic Astrology

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/traditional/analysis` | Traditional Analysis | TraditionalAnalysisRequest |
| POST | `/traditional/analysis/annual-profection` | Annual Profection | AnnualProfectionRequest |
| POST | `/traditional/analysis/profection-timeline` | Profection Timeline | ProfectionTimelineRequest |
| POST | `/traditional/dignities` | Dignities Analysis | TraditionalAnalysisRequest |
| POST | `/traditional/lots` | Lots (Arabic Parts) | TraditionalAnalysisRequest |
| POST | `/traditional/profections` | Profections | TraditionalAnalysisRequest |
| GET | `/traditional/glossary/traditional-points` | Traditional Points Glossary | - |
| GET | `/traditional/glossary/dignities` | Dignities Glossary | - |
| GET | `/traditional/glossary/profection-houses` | Profection Houses Glossary | - |
| GET | `/traditional/capabilities` | Traditional Capabilities | - |

**TraditionalAnalysisRequest**: `subject` (required), `options` (ChartOptions), `orbs`.

**AnnualProfectionRequest**: `subject` (required), `current_date`, `current_age`.

**ProfectionTimelineRequest**: `subject` (required), `start_age` (default: 0), `end_age` (default: 84).

---

## Horary Astrology

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/horary/chart` | Generate Horary Chart | HoraryChartRequest |
| POST | `/horary/analyze` | Analyze Horary Question | HoraryAnalysisRequest |
| POST | `/horary/aspects` | Get Horary Aspects | HoraryAspectsRequest |
| POST | `/horary/fertility-analysis` | Fertility Question Analysis | FertilityAnalysisRequest |
| GET | `/horary/glossary/considerations` | Considerations Glossary | - |
| GET | `/horary/glossary/categories` | Categories Glossary | query: language |

### HoraryChartRequest

`question` (required), `question_time` (DateTimeLocation, required), `chart_options`, `options` (HoraryOptions).

### HoraryAnalysisRequest

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `question` | string | **Yes** | |
| `category` | string | **Yes** | Enum: pregnancy, fertility, love, marriage, career, job, money, health, missing_item, travel, general |
| `subcategory` | string | No | |
| `question_time` | DateTimeLocation | **Yes** | |
| `include_timing` | boolean | No | Default: true |
| `extended_lunar_sequence` | boolean | No | Default: true |
| `max_lookahead_degrees` | number | No | Default: 45.0 |
| `options` | HoraryOptions | No | |

### HoraryAspectsRequest

`question_time` (required), `max_lookahead_degrees` (default: 45.0), `include_separating` (default: false), `planets`, `chart_options`, `include_ingresses` (default: true), `include_stations` (default: true), `max_station_days` (default: 365.0).

### FertilityAnalysisRequest

Same as HoraryAnalysisRequest plus `include_all_planetary_aspects` (default: false).

---

## Tarot

### Glossary & Card Data

| Method | Path | Summary | Query Params |
|--------|------|---------|--------------|
| GET | `/tarot/glossary/cards` | All Tarot Cards | arcana, suit, element, planet, sign, house |
| GET | `/tarot/glossary/cards/{card_id}` | Card Detail | path: card_id |
| GET | `/tarot/glossary/spreads` | Spread Types | - |
| GET | `/tarot/cards/search` | Search Cards | keyword, life_area, element, planet, sign, arcana, page, page_size |
| GET | `/tarot/cards/daily` | Daily Card | user_id (required), life_area, birth_year/month/day/hour/minute, city, country_code |

### Card Drawing

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/tarot/cards/draw` | Draw Cards | DrawCardsRequest |

**DrawCardsRequest**: `count` (default: 1), `exclude_reversed` (default: false), `life_area`, `exclude_majors` (default: false), `exclude_minors` (default: false).

### Reports

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/tarot/reports/single` | Single Card Report | TarotReportRequest |
| POST | `/tarot/reports/three-card` | Three Card Report | TarotReportRequest |
| POST | `/tarot/reports/celtic-cross` | Celtic Cross Report | TarotReportRequest |
| POST | `/tarot/reports/synastry` | Synastry Report | TarotReportRequest |
| POST | `/tarot/reports/houses` | Houses Spread | TarotReportRequest |
| POST | `/tarot/reports/tree-of-life` | Tree of Life Spread | TreeOfLifeRequest |

**TarotReportRequest**:

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `spread_type` | string | "three_card" | single, three_card, celtic_cross, zodiac_wheel, synastry, houses, custom |
| `life_area` | string | null | |
| `birth_data` | DateTimeLocation | null | |
| `partner_birth_data` | DateTimeLocation | null | For synastry |
| `use_reversals` | boolean | true | |
| `tradition` | string | "universal" | universal, psychological, classical, hermetic |
| `include_dignities` | boolean | false | |
| `include_timing` | boolean | false | |
| `include_astro_context` | boolean | false | |
| `include_birth_cards` | boolean | false | |
| `interpretation_depth` | string | "basic" | keywords, basic, detailed, professional |
| `language` | string | "en" | |

**TreeOfLifeRequest**: `spread_type` (required), `life_area` (default: "general"), `birth_data`, `include_timing` (default: true), `include_dignities` (default: true), `include_astro_context` (default: false), `interpretation_depth` (default: "detailed"), `language`.

### Analysis

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/tarot/analysis/quintessence` | Quintessence | QuintessenceRequest |
| POST | `/tarot/analysis/birth-cards` | Birth Cards | BirthCardFlexibleRequest |
| POST | `/tarot/analysis/dignities` | Elemental Dignities | ElementalDignitiesRequest |
| POST | `/tarot/analysis/timing` | Timing Analysis | TimingAnalysisRequest |
| POST | `/tarot/analysis/optimal-times` | Find Optimal Times | OptimalTimesRequest |
| POST | `/tarot/analysis/transit-report` | Transit Report | TransitReportRequest (tarot) |
| POST | `/tarot/analysis/natal-report` | Natal Report | NatalReportRequest (tarot) |

**QuintessenceRequest**: `cards` (array[string]), `include_interpretation` (default: true).

**BirthCardFlexibleRequest**: `birth_date`, `include_interpretation`, `subject`, `options`.

**ElementalDignitiesRequest**: `cards` (array, required), `spread_type`.

**TimingAnalysisRequest**: `cards` (array, required), `birth_data`, `question_type`.

**OptimalTimesRequest**: `birth_data` (required), `question_type` (required), `date_range` (required).

**Tarot NatalReportRequest**: `birth_data` (required), `life_area` (default: "general"), `include_timing` (default: true), `interpretation_depth` (default: "detailed"), `language`.

**Tarot TransitReportRequest**: Same as tarot NatalReportRequest.

---

## Numerology

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/numerology/core-numbers` | Core Numbers | SingleSubjectRequest |
| POST | `/numerology/comprehensive` | Comprehensive Reading | SingleSubjectRequest |
| POST | `/numerology/compatibility` | Compatibility | MultipleSubjectsRequest |

**SingleSubjectRequest**: `subject` (StandardSubject, required), `options` (StandardOptions).

**MultipleSubjectsRequest**: `subjects` (array[StandardSubject]), `options` (StandardOptions).

---

## Vedic Astrology

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/vedic/birth-details` | Vedic Birth Details | VedicRequest |
| POST | `/vedic/kundli-matching` | Kundli Matching | VedicMatchingRequest |
| POST | `/vedic/manglik-dosha` | Manglik Dosha | VedicRequest |
| POST | `/vedic/divisional-chart` | Divisional Charts | VedicDivisionalRequest |
| POST | `/vedic/panchang` | Panchang | VedicDateLocationRequest |
| POST | `/vedic/remedies` | Remedies | VedicRemediesRequest |
| POST | `/vedic/vimshottari-dasha` | Vimshottari Dasha | VedicDashaRequest |
| POST | `/vedic/sade-sati` | Sade Sati | VedicSadeSatiRequest |
| POST | `/vedic/kaal-sarpa-dosha` | Kaal Sarpa Dosha | VedicKaalSarpaRequest |
| POST | `/vedic/transit` | Vedic Transit | VedicTransitRequest |
| POST | `/vedic/nakshatra-predictions` | Nakshatra Predictions | VedicNakshatraPredictionRequest |
| POST | `/vedic/yogini-dasha` | Yogini Dasha | VedicYoginiDashaRequest |
| POST | `/vedic/yoga-analysis` | Yoga Analysis | VedicYogaAnalysisRequest |
| POST | `/vedic/ashtakvarga` | Ashtakvarga | VedicAshtakvargaRequest |
| POST | `/vedic/shadbala` | Shadbala | VedicShadbalaRequest |
| POST | `/vedic/chara-dasha` | Chara Dasha | VedicCharaDashaRequest |
| POST | `/vedic/kp-system` | KP System | VedicKPSystemRequest |
| POST | `/vedic/varshaphal` | Varshaphal | VedicVarshaphalRequest |
| POST | `/vedic/festival-calendar` | Festival Calendar | VedicFestivalCalendarRequest |
| POST | `/vedic/regional-panchang` | Regional Panchang | VedicRegionalPanchangRequest |
| POST | `/vedic/chart` | Vedic Chart SVG | VedicChartSVGRequest |
| POST | `/vedic/chart/render/{format}` | Render Vedic Chart | VedicChartRenderRequest |

### VedicOptions

| Field | Type | Default | Values |
|-------|------|---------|--------|
| `ayanamsa` | string | "lahiri" | lahiri, krishnamurti, raman, yukteshwar, true_citra, jn_bhasin, ushashashi, true_revati, true_pushya, ss_citra, suryasiddhanta, fagan_bradley |
| `node_type` | string | "mean" | mean, true |
| `bhava_system` | string | "equal" | equal, whole_sign, placidus, koch, sripati |
| `language` | string | "en" | en, hi, ta, te, ru, kn, ml, bn, gu, mr, es, de, fr, it, pt, tr, uk, ar, zh, pt-BR, es-ES, fr-FR |
| `include_upagrahas` | boolean | false | |
| `include_arudha_padas` | boolean | false | |
| `precision` | integer | 6 | |

### Key Request Schemas

**VedicRequest**: `subject` (required), `options` (VedicOptions).

**VedicMatchingRequest**: `groom` (Subject, required), `bride` (Subject, required), `options`, `include_manglik` (default: true).

**VedicDivisionalRequest**: `subject` (required), `charts` (array[string]), `options`.

**VedicDashaRequest**: `subject` (required), `dasha_level` (default: "antardasha", enum: mahadasha/antardasha/pratyantardasha/sukshma/prana), `target_date`, `options`.

**VedicDateLocationRequest**: `datetime_location` (required), `options`.

**VedicRemediesRequest**: `subject` (required), `remedy_type` (default: "all", enum: all/gemstones/mantras/pujas/rudrakshas), `options`.

**VedicSadeSatiRequest**: `subject` (required), `check_date`, `include_remedies` (default: true), `options`.

**VedicKaalSarpaRequest**: `subject` (required), `include_remedies` (default: true), `options`.

**VedicTransitRequest**: `subject` (required), `transit_date`, `options`.

**VedicNakshatraPredictionRequest**: `subject` (required), `prediction_date`, `options`.

**VedicYoginiDashaRequest**: `subject` (required), `years_ahead` (default: 80), `options`.

**VedicYogaAnalysisRequest**: `subject` (required), `include_categories`, `options`.

**VedicAshtakvargaRequest**: `subject` (required), `include_sarva` (default: true), `options`.

**VedicShadbalaRequest**: `subject` (required), `options`.

**VedicCharaDashaRequest**: `subject` (required), `options`, `calculation_years` (default: 120), `include_antardashas` (default: true), `include_karakas` (default: true).

**VedicKPSystemRequest**: `subject` (required), `include_significators` (default: true), `include_ruling_planets` (default: true).

**VedicVarshaphalRequest**: `subject` (required), `target_year` (required), `options`.

**VedicFestivalCalendarRequest**: `year` (required), `region`, `festival_type`, `language`.

**VedicRegionalPanchangRequest**: `year` (required), `month` (required), `day` (required), `hour` (default: 12), `minute` (default: 0), `latitude` (required), `longitude` (required), `timezone` (required), `region`, `language`, `ayanamsa`.

**VedicChartSVGRequest**: `subject` (required), `style` (default: "north_indian", enum: north_indian/south_indian), `chart_options`, `svg_options`.

**VedicChartRenderRequest**: Same as SVG plus `width` (default: 800), `height` (default: 800).

---

## Chinese Astrology & BaZi

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/chinese/bazi` | Calculate BaZi | BaZiRequest |
| POST | `/chinese/compatibility` | Compatibility | MultipleSubjectsRequest |
| POST | `/chinese/luck-pillars` | Luck Pillars | LuckPillarsRequest |
| POST | `/chinese/ming-gua` | Ming Gua | SingleSubjectRequest |
| POST | `/chinese/yearly-forecast` | Yearly Forecast | ChineseYearlyRequest |
| GET | `/chinese/elements/balance/{year}` | Year Elements | path: year; query: include_predictions, language |
| GET | `/chinese/zodiac/{animal}` | Zodiac Animal Info | path: animal; query: year, language |
| GET | `/chinese/calendar/solar-terms/{year}` | Solar Terms | path: year; query: timezone, language |

### ChineseSubject

`name` (default: "Subject"), `birth_data` (ChineseBirthData, required), `gender`.

**ChineseBirthData**: Same fields as BirthData (year required, rest optional).

### BaZiRequest

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `subject` | ChineseSubject | required | |
| `include_luck_pillars` | boolean | null | |
| `include_annual_pillars` | boolean | false | |
| `current_year` | integer | null | |
| `language` | string | "en" | |
| `tradition` | string | "classical" | classical, modern, simplified |
| `analysis_depth` | string | "standard" | basic, standard, comprehensive, professional |

**LuckPillarsRequest**: `subject` (ChineseSubject, required), `include_annual_pillars` (default: true), `years_ahead` (default: 10), `current_year`, `language`.

**ChineseYearlyRequest**: `subject` (ChineseSubject, required), `forecast_year`, `include_monthly` (default: true), `include_advice` (default: true), `language`.

---

## Human Design

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/human-design/bodygraph` | Calculate Bodygraph | BodyGraphRequest |
| POST | `/human-design/type` | Get Type Only | BodyGraphRequest |
| POST | `/human-design/transits` | Transit Overlay | TransitOverlayRequest |
| POST | `/human-design/compatibility` | Compatibility | HDCompatibilityRequest |
| POST | `/human-design/design-date` | Calculate Design Date | BodyGraphRequest |
| GET | `/human-design/glossary/gates` | Gates Glossary | query: language, center |
| GET | `/human-design/glossary/channels` | Channels Glossary | query: language, circuit |
| GET | `/human-design/glossary/types` | Types Glossary | query: language |

**BodyGraphRequest**: `subject` (StandardSubject, required), `options` (StandardOptions), `hd_options` (HumanDesignOptions).

### HumanDesignOptions

| Field | Type | Default |
|-------|------|---------|
| `include_interpretations` | boolean | true |
| `include_design_chart` | boolean | true |
| `include_channels` | boolean | true |
| `include_definition_bridges` | boolean | false |
| `include_variables` | boolean | false |

**TransitOverlayRequest**: `subject` (required), `options`, `transit_datetime` (string), `transit_options`.

**HDCompatibilityRequest**: `subjects` (array[StandardSubject]), `options`, `hd_options`.

---

## Kabbalah

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/kabbalah/tree-of-life-chart` | Tree of Life Chart | TreeOfLifeChartRequest |
| POST | `/kabbalah/birth-angels` | Birth Angels | BirthAngelsRequest |
| POST | `/kabbalah/tikkun` | Tikkun | TikkunRequest |
| POST | `/kabbalah/gematria` | Gematria | GematriaRequest |
| GET | `/kabbalah/glossary/sephiroth` | Sephiroth Glossary | query: system (default: modern_halevi) |
| GET | `/kabbalah/glossary/hebrew-letters` | Hebrew Letters Glossary | - |
| GET | `/kabbalah/glossary/angels-72` | 72 Angels Glossary | - |

### TreeOfLifeChartRequest

`birth_data` (DateTimeLocation, required), `system` (KabbalahSystem: classical/modern_halevi/golden_dawn), `include_daat` (default: true), `include_paths` (default: true), `include_interpretations` (default: true), `language`, `tradition`.

### BirthAngelsRequest

`birth_data` (required), `include_secondary` (default: true), `include_tertiary` (default: false), `include_interpretations` (default: true), `language`.

### TikkunRequest

`birth_data` (required), `method` (TikkunMethod), `include_interpretations` (default: true), `language`.

### GematriaRequest

`text` (required), `methods` (array[GematriaMethod]), `find_equivalents` (default: false), `language`.

---

## Astrocartography & Relocation

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/astrocartography/map` | Generate Map | AstrocartographyMapRequest |
| POST | `/astrocartography/render` | Render Map | AstrocartographyRenderRequest |
| POST | `/astrocartography/lines` | Get Lines | AstrocartographyLinesRequest |
| POST | `/astrocartography/location-analysis` | Analyze Location | LocationAnalysisRequest |
| POST | `/astrocartography/search-locations` | Search Optimal Locations | SearchLocationsRequest |
| POST | `/astrocartography/compare-locations` | Compare Locations | CompareLocationsRequest |
| POST | `/astrocartography/relocation-chart` | Relocation Chart | RelocationChartRequest |
| POST | `/astrocartography/power-zones` | Find Power Zones | PowerZonesRequest |
| POST | `/astrocartography/paran-map` | Generate Paran Map | ParanMapRequest |
| POST | `/astrocartography/astrodynes` | Calculate Astrodynes | AstrodynesRequest |
| POST | `/astrocartography/astrodynes/compare` | Compare Astrodynes | AstrodynesCompareRequest |
| GET | `/astrocartography/line-meanings` | Line Meanings | query: language |
| GET | `/astrocartography/supported-features` | Supported Features | - |

### AstrocartographyMapRequest

`subject` (required), `map_options` (AstrocartographyOptions), `visual_options` (VisualOptions).

### AstrocartographyOptions

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `planets` | array[string] | - | |
| `line_types` | array[string] | - | |
| `include_parans` | boolean | false | |
| `include_local_space` | boolean | false | |
| `map_projection` | string | "mercator" | mercator, robinson, mollweide, equirectangular |
| `region` | MapRegion | null | `{latitude_range: [-60,80], longitude_range: [-180,180]}` |
| `line_orb_tolerance` | number | 2.0 | |
| `city_selection_algorithm` | string | "round_robin" | round_robin, population, distance |
| `max_cities_per_country` | integer | 4 | |
| `max_cities_per_line` | integer | 2 | |

### LocationInput

`city`, `country_code`, `latitude`, `longitude` (all optional, use coords or city/country).

### LocationAnalysisRequest

`subject` (required), `location` (LocationInput, required), `analysis_options`, `language`.

### SearchLocationsRequest

`subject` (required), `search_criteria` (SearchCriteria), `location_filters` (LocationFilters), `result_options`, `language`.

**SearchCriteria**: `life_area` (default: "overall", enum: identity/health/finance/career/love/relationships/creativity/spirituality/home/learning/communication/travel/overall), `preferred_planets`, `preferred_line_types`, `minimum_score` (default: 6.0), `avoid_debilitated` (default: true), `orb_tolerance` (default: 2.0).

**LocationFilters**: `countries`, `continents`, `min_population` (default: 750000), `max_population`, `climate_zones`, `languages`, `exclude_cities`.

### CompareLocationsRequest

`subject` (required), `locations` (array[LocationInput], required), `comparison_criteria`, `language`.

### RelocationChartRequest

`subject` (required), `options` (RelocationOptions: `target_location`, `show_changes`, `highlight_angular_changes`, `include_aspect_changes`, `orb_tolerance`), `language`.

### PowerZonesRequest

`subject` (required), `search_options`, `language`.

### AstrodynesRequest

`subject` (required), `relocation` (LocationInput), `options` (AstrodynesOptions: `include_dignities`, `aspects`, `house_system`).

### AstrodynesCompareRequest

`subject` (required), `locations` (array[LocationInput], required), `options` (AstrodynesOptions).

---

## Eclipses

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| GET | `/eclipses/upcoming` | Upcoming Eclipses | query: count (default: 5) |
| POST | `/eclipses/natal-check` | Eclipse Natal Impact | EclipseNatalCheckRequest |
| POST | `/eclipses/interpretation` | Eclipse Interpretation | EclipseInterpretationRequest |

**EclipseNatalCheckRequest**: `subject` (required), `date_range` (DateRange), `max_orb` (default: 5.0).

**EclipseInterpretationRequest**: `eclipse_id` (required), `birth_data` (Subject), `language`, `include_house_themes` (default: true).

---

## Lunar Features

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/lunar/phases` | Precise Lunar Phases | LunarPhasesRequest |
| POST | `/lunar/void-of-course` | Void of Course Status | VoidOfCourseRequest |
| POST | `/lunar/mansions` | Lunar Mansions | LunarMansionsRequest |
| POST | `/lunar/events` | Special Lunar Events | LunarEventsRequest |
| GET | `/lunar/calendar/{year}` | Annual Lunar Calendar | path: year; query: month |

**LunarPhasesRequest**: `datetime_location` (DateTimeLocation, required), `days_ahead`.

**VoidOfCourseRequest**: `datetime_location` (required), `days_ahead`, `use_modern_planets`.

**LunarMansionsRequest**: `datetime_location` (required), `system`, `days_ahead`.

**LunarEventsRequest**: `datetime_location` (required), `days_ahead`.

---

## Fixed Stars

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/fixed-stars/positions` | Fixed Stars Positions | FixedStarsPositionsRequest |
| POST | `/fixed-stars/conjunctions` | Fixed Stars Conjunctions | FixedStarsConjunctionsRequest |
| POST | `/fixed-stars/report` | Fixed Stars Report | FixedStarsReportRequest |
| GET | `/fixed-stars/presets` | Presets Info | - |

**FixedStarsPositionsRequest**: `subject` (required), `fixed_stars` (FixedStarsConfig).

**FixedStarsConjunctionsRequest**: `subject` (required), `fixed_stars` (FixedStarsConfig), `include_oppositions` (default: false).

**FixedStarsReportRequest**: `subject` (required), `fixed_stars` (FixedStarsConfig).

---

## Palmistry

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/palmistry/analysis` | Palm Analysis (raw data) | PalmAnalysisRequest |
| POST | `/palmistry/reading` | Palm Reading (interpretation) | PalmReadingRequest |
| POST | `/palmistry/astro` | Palm-Astrology Integration | PalmAstroRequest |
| POST | `/palmistry/compatibility` | Palm Compatibility | PalmCompatibilityRequest |

**PalmAnalysisRequest**: `image_url`, `image_base64`, `return_visualization` (default: false), `include_quality` (default: true).

**PalmReadingRequest**: `image_url`, `image_base64`, `return_visualization` (default: false), `language` (default: "en"), `include_raw_data` (default: false).

**PalmAstroRequest**: `image_url`, `image_base64`, `birth_data`, `return_visualization` (default: false), `language`.

**PalmCompatibilityRequest**: `palm_a_url`, `palm_a_base64`, `palm_b_url`, `palm_b_base64`, `return_visualization` (default: false), `language`.

---

## Insights - Relationship

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/insights/relationship/compatibility` | Compatibility | CompatibilityRequest |
| POST | `/insights/relationship/compatibility-score` | Quick Score | MultipleSubjectsRequest |
| POST | `/insights/relationship/love-languages` | Love Languages | SingleSubjectRequest |
| POST | `/insights/relationship/davison` | Davison Chart | MultipleSubjectsRequest |
| POST | `/insights/relationship/timing` | Relationship Timing | CompatibilityRequest |
| POST | `/insights/relationship/red-flags` | Red/Green Flags | SingleSubjectRequest |
| GET | `/insights/relationship/` | Discover Relationship Insights | - |

---

## Insights - Pet

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/insights/pet/personality` | Pet Personality | PetSingleSubjectRequest |
| POST | `/insights/pet/compatibility` | Pet-Human Compatibility | PetCompatibilityRequest |
| POST | `/insights/pet/training-windows` | Training Windows | PetSingleSubjectRequest |
| POST | `/insights/pet/health-sensitivities` | Health Sensitivities | PetSingleSubjectRequest |
| POST | `/insights/pet/multi-pet-dynamics` | Multi-Pet Dynamics | PetMultiSubjectRequest |

**PetSingleSubjectRequest**: `subject` (required), `options`, `pet_options` (PetOptions), `owner` (Subject).

**PetOptions**: `pet_type` (default: "dog"), `breed`, `training_type` (default: "obedience"), `language`.

**PetCompatibilityRequest**: `subjects` (array[Subject], required), `options` (PetOptions).

**PetMultiSubjectRequest**: `subjects` (array), `options`, `pet_options`.

---

## Insights - Wellness

All use **SingleSubjectRequest**: `subject` (StandardSubject, required), `options` (StandardOptions).

| Method | Path | Summary |
|--------|------|---------|
| POST | `/insights/wellness/body-mapping` | Body Mapping |
| POST | `/insights/wellness/biorhythms` | Biorhythms |
| POST | `/insights/wellness/wellness-timing` | Wellness Timing |
| POST | `/insights/wellness/energy-patterns` | Energy Patterns |
| POST | `/insights/wellness/wellness-score` | Wellness Score |
| POST | `/insights/wellness/moon-wellness` | Moon Wellness Calendar |

---

## Insights - Financial

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/insights/financial/market-timing` | Market Timing | MarketTimingRequest |
| POST | `/insights/financial/personal-trading` | Personal Trading Windows | generic |
| POST | `/insights/financial/gann-analysis` | Gann Cycles | GannRequest |
| POST | `/insights/financial/bradley-siderograph` | Bradley Turns | BradleySiderographRequest |
| POST | `/insights/financial/crypto-timing` | Crypto Timing | CryptoTimingRequest |
| POST | `/insights/financial/forex-timing` | Forex Timing | ForexRequest |

**MarketTimingRequest**: `start_date`, `end_date`, `markets` (array[string]), `language`.

**BradleySiderographRequest**: `language`, `birth_data`, `period` (default: "yearly"), `market` (default: "stocks"), `year`, `analysis_date`.

**CryptoTimingRequest**: `cryptocurrency` (default: "bitcoin"), `analysis_period_days` (default: 30), `include_volatility_forecast` (default: true), `language`.

**GannRequest**: `symbol` (default: "SPX"), `reference_date`, `forecast_days` (default: 90).

**ForexRequest**: `pair` (default: "EUR/USD"), `trading_session` (default: "london"), `forecast_days` (default: 7).

---

## Insights - Business

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/insights/business/team-dynamics` | Team Dynamics | BusinessMultipleRequest |
| POST | `/insights/business/hiring-compatibility` | Hiring Compatibility | BusinessMultipleRequest |
| POST | `/insights/business/leadership-style` | Leadership Style | BusinessSingleRequest |
| POST | `/insights/business/business-timing` | Business Timing | BusinessTimingRequest |
| POST | `/insights/business/department-compatibility` | Department Compatibility | generic object |
| POST | `/insights/business/succession-planning` | Succession Planning | BusinessMultipleRequest |

**BusinessSingleRequest**: `subject` (StandardSubject, required), `options` (BusinessOptions).

**BusinessMultipleRequest**: `subjects` (array[StandardSubject]), `options` (BusinessOptions).

**BusinessOptions** extends StandardOptions with: `team_name`, `department_focus`, `role`, `department`, `include_timing` (default: true), `include_development` (default: true), `current_leader_role`, `succession_department`, `departments`.

**BusinessTimingRequest**: `activities` (array, default: ["product_launch","meetings"]), `start_date`, `end_date`, `company_data` (DateTimeLocation), `language`.

---

## Insights Platform

| Method | Path | Summary |
|--------|------|---------|
| GET | `/insights/` | Discover All Insights |

---

## Feng Shui & Flying Stars

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/fengshui/flying-stars/chart` | Flying Stars Chart | FlyingStarsChartRequest |
| GET | `/fengshui/flying-stars/annual/{year}` | Annual Flying Stars | path: year; query: language |
| GET | `/fengshui/afflictions/{year}` | Annual Afflictions | path: year; query: language |
| GET | `/fengshui/glossary/stars` | Flying Stars Glossary | query: language |

### FlyingStarsChartRequest

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `facing_degrees` | number | **Yes** | Building facing direction |
| `period` | integer | **Yes** | Feng Shui period (1-9) |
| `include_annual` | boolean | No | Default: true |
| `include_monthly` | boolean | No | Default: false |
| `analysis_date` | string | No | |
| `language` | string | No | Default: "en" |

---

## Zi Wei Dou Shu

| Method | Path | Summary | Request Schema |
|--------|------|---------|----------------|
| POST | `/ziwei/chart` | Calculate Zi Wei Chart | ZiWeiChartRequest |

### ZiWeiChartRequest

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | No | Default: "Subject" |
| `birth_data` | ZiWeiBirthData | **Yes** | year, month, day, hour required; minute default 0 |
| `gender` | string | **Yes** | male, female |
| `language` | string | No | Default: "en" |

---

## Glossary & Reference

All are GET endpoints with no request body.

| Method | Path | Summary | Query Params |
|--------|------|---------|--------------|
| GET | `/glossary/cities` | Cities | search, country_code, sort_by (population/name), sort_order, limit (100), offset |
| GET | `/glossary/countries` | Countries | - |
| GET | `/glossary/house-systems` | House Systems | - |
| GET | `/glossary/zodiac-types` | Zodiac Types | - |
| GET | `/glossary/active-points` | Active Points | type |
| GET | `/glossary/active-points/primary` | Primary Active Points | type |
| GET | `/glossary/themes` | Themes | - |
| GET | `/glossary/languages` | Languages | - |
| GET | `/glossary/fixed-stars` | Fixed Stars | - |
| GET | `/glossary/life-areas` | Life Areas | language |
| GET | `/glossary/keywords` | Astrological Keywords | category (default: "planets") |
| GET | `/glossary/houses` | Houses | house_system (default: "P") |
| GET | `/glossary/elements` | Elements | - |
| GET | `/glossary/horary-categories` | Horary Categories | - |

---

## Health & Monitoring

| Method | Path | Summary |
|--------|------|---------|
| GET | `/health/` | Health Check |
| GET | `/health/debug/timezone` | Debug TimezoneFinder |

---

## Quick Reference: Request Pattern Cheat Sheet

| Pattern | Required Fields | Used By |
|---------|----------------|---------|
| Single Subject (chart) | `subject: {name, birth_data: {year,month,day,hour,minute,latitude,longitude}}` | Charts, Analysis, Vedic, Astrocartography |
| Two Subjects (chart) | `subject1: {...}, subject2: {...}` | Synastry, Composite |
| Single Subject (standard) | `subject: {name, birth_data: {year,month,day,...}}` | Insights, Numerology, Human Design |
| Multiple Subjects (standard) | `subjects: [{...}, {...}]` | Compatibility endpoints |
| DateTimeLocation only | `datetime_location: {year,month,day,hour,minute,lat,lng}` | Lunar, Panchang |
| Sign-based | `sign: "aries"` | Sun sign horoscopes |
| Image-based | `image_url` or `image_base64` | Palmistry |
| Text-based | `text: "..."` | Gematria |
| Question-based | `question: "...", question_time: {...}` | Horary |
