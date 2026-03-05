# Use Cases → API Endpoints

Quick reference mapping user intents to the correct API endpoint.

## Birth Charts & Positions

| User asks about... | Endpoint | Method |
|---|---|---|
| "What's my birth chart?" / "My natal chart" | `/api/v3/charts/natal` | POST |
| "Where are my planets?" / planetary positions | `/api/v3/data/positions` | POST |
| "What are my houses?" / house cusps | `/api/v3/data/house-cusps` | POST |
| "What aspects do I have?" | `/api/v3/data/aspects` | POST |
| "Enhanced positions with dignities" | `/api/v3/data/positions/enhanced` | POST |
| "Enhanced aspects with reception" | `/api/v3/data/aspects/enhanced` | POST |
| "Show me the current sky" / now | `/api/v3/data/now` | GET |
| "Global planetary positions (no location)" | `/api/v3/data/global-positions` | POST |

## Relationships & Compatibility

| User asks about... | Endpoint | Method |
|---|---|---|
| "Are we compatible?" / synastry | `/api/v3/charts/synastry` | POST |
| "Our composite chart" / relationship entity | `/api/v3/charts/composite` | POST |
| "Compatibility score" (quick) | `/api/v3/analysis/compatibility-score` | POST |
| "Full compatibility analysis" | `/api/v3/analysis/compatibility` | POST |
| "Synastry report" (detailed) | `/api/v3/analysis/synastry-report` | POST |
| "Relationship score" | `/api/v3/analysis/relationship-score` | POST |
| "Love languages" | `/api/v3/insights/relationship/love-languages` | POST |
| "Relationship red/green flags" | `/api/v3/insights/relationship/red-flags` | POST |
| "Davison chart" | `/api/v3/insights/relationship/davison` | POST |
| "Relationship timing" | `/api/v3/insights/relationship/timing` | POST |

## Transits & Forecasting

| User asks about... | Endpoint | Method |
|---|---|---|
| "What transits are happening now?" | `/api/v3/charts/transit` | POST |
| "Transit period analysis (date range)" | `/api/v3/charts/natal-transits` | POST |
| "My solar return" / birthday chart | `/api/v3/charts/solar-return` | POST |
| "My lunar return" | `/api/v3/charts/lunar-return` | POST |
| "Solar return transits" | `/api/v3/charts/solar-return-transits` | POST |
| "Lunar return transits" | `/api/v3/charts/lunar-return-transits` | POST |
| "Progressions" / secondary progressions | `/api/v3/charts/progressions` | POST |
| "Directions" / primary directions | `/api/v3/charts/directions` | POST |
| "Transit report" | `/api/v3/analysis/transit-report` | POST |
| "Predictive analysis" | `/api/v3/analysis/predictive` | POST |

## Moon & Lunar

| User asks about... | Endpoint | Method |
|---|---|---|
| "What moon phase is it?" / lunar metrics | `/api/v3/data/lunar-metrics` | POST |
| "Enhanced lunar metrics" (traditional) | `/api/v3/data/lunar-metrics/enhanced` | POST |
| "Is the moon void of course?" | `/api/v3/lunar/void-of-course` | POST |
| "Lunar phases for a period" | `/api/v3/lunar/phases` | POST |
| "Lunar mansions" | `/api/v3/lunar/mansions` | POST |
| "Special lunar events" | `/api/v3/lunar/events` | POST |
| "Annual lunar calendar" | `/api/v3/lunar/calendar/{year}` | GET |
| "Lunar analysis report" | `/api/v3/analysis/lunar-analysis` | POST |

## Horoscopes

| User asks about... | Endpoint | Method |
|---|---|---|
| "Today's horoscope for Aries" | `/api/v3/horoscope/sign/daily` | POST |
| "My personal daily horoscope" | `/api/v3/horoscope/personal/daily` | POST |
| "Weekly horoscope for Leo" | `/api/v3/horoscope/sign/weekly` | POST |
| "Monthly horoscope" | `/api/v3/horoscope/sign/monthly` | POST |
| "Yearly horoscope" | `/api/v3/horoscope/sign/yearly` | POST |
| "Personal weekly/monthly/yearly" | `/api/v3/horoscope/personal/{period}` | POST |
| Text versions (plain text) | Add `/text` to any horoscope endpoint | POST |

## Analysis Reports (AI-interpreted)

| User asks about... | Endpoint | Method |
|---|---|---|
| "Full natal report" | `/api/v3/analysis/natal-report` | POST |
| "Career analysis" | `/api/v3/analysis/career` | POST |
| "Relationship analysis" | `/api/v3/analysis/relationship` | POST |
| "Psychological profile" | `/api/v3/analysis/psychological` | POST |
| "Karmic analysis" | `/api/v3/analysis/karmic` | POST |
| "Health tendencies" | `/api/v3/analysis/health` | POST |
| "Spiritual path" | `/api/v3/analysis/spiritual` | POST |
| "Vocational guidance" | `/api/v3/analysis/vocational` | POST |
| "Relocation analysis" | `/api/v3/analysis/relocation` | POST |
| "Progression report" | `/api/v3/analysis/progression-report` | POST |
| "Direction report" | `/api/v3/analysis/direction-report` | POST |
| "Composite report" | `/api/v3/analysis/composite-report` | POST |

## Chart Rendering

| User asks about... | Endpoint | Method |
|---|---|---|
| "Draw my natal chart" (SVG) | `/api/v3/svg/natal` | POST |
| "Draw synastry chart" (SVG) | `/api/v3/svg/synastry` | POST |
| "Draw transit chart" (SVG) | `/api/v3/svg/transit` | POST |
| "Draw composite chart" (SVG) | `/api/v3/svg/composite` | POST |
| "Render natal chart" (PNG) | `/api/v3/render/natal` | POST |
| "Render synastry" (PNG) | `/api/v3/render/synastry` | POST |
| "Render transit" (PNG) | `/api/v3/render/transit` | POST |
| "Render composite" (PNG) | `/api/v3/render/composite` | POST |

## Tarot

| User asks about... | Endpoint | Method |
|---|---|---|
| "Draw tarot cards" | `/api/v3/tarot/cards/draw` | POST |
| "Daily tarot card" | `/api/v3/tarot/cards/daily` | GET |
| "Single card reading" | `/api/v3/tarot/reports/single` | POST |
| "Three card spread" | `/api/v3/tarot/reports/three-card` | POST |
| "Celtic cross spread" | `/api/v3/tarot/reports/celtic-cross` | POST |
| "Tarot birth cards" | `/api/v3/tarot/analysis/birth-cards` | POST |
| "Search tarot cards" | `/api/v3/tarot/cards/search` | GET |
| "All tarot cards" (glossary) | `/api/v3/tarot/glossary/cards` | GET |

## Numerology

| User asks about... | Endpoint | Method |
|---|---|---|
| "My life path number" / core numbers | `/api/v3/numerology/core-numbers` | POST |
| "Full numerology reading" | `/api/v3/numerology/comprehensive` | POST |
| "Numerology compatibility" | `/api/v3/numerology/compatibility` | POST |

## Vedic Astrology

| User asks about... | Endpoint | Method |
|---|---|---|
| "Vedic birth chart" / birth details | `/api/v3/vedic/birth-details` | POST |
| "Kundli matching" / marriage compatibility | `/api/v3/vedic/kundli-matching` | POST |
| "Manglik dosha" | `/api/v3/vedic/manglik-dosha` | POST |
| "Divisional charts (D9, etc.)" | `/api/v3/vedic/divisional-chart` | POST |
| "Panchang" / almanac | `/api/v3/vedic/panchang` | POST |
| "Remedies" | `/api/v3/vedic/remedies` | POST |
| "Vimshottari dasha" | `/api/v3/vedic/vimshottari-dasha` | POST |
| "Sade sati" | `/api/v3/vedic/sade-sati` | POST |
| "Yoga analysis" | `/api/v3/vedic/yoga-analysis` | POST |
| "Ashtakvarga" | `/api/v3/vedic/ashtakvarga` | POST |
| "Nakshatra predictions" | `/api/v3/vedic/nakshatra-predictions` | POST |

## Chinese Astrology & Feng Shui

| User asks about... | Endpoint | Method |
|---|---|---|
| "BaZi / Four Pillars" | `/api/v3/chinese/bazi` | POST |
| "Chinese compatibility" | `/api/v3/chinese/compatibility` | POST |
| "Luck pillars" | `/api/v3/chinese/luck-pillars` | POST |
| "Ming Gua number" | `/api/v3/chinese/ming-gua` | POST |
| "Flying stars chart" | `/api/v3/fengshui/flying-stars/chart` | POST |
| "Annual flying stars" | `/api/v3/fengshui/flying-stars/annual/{year}` | GET |
| "Chinese horoscope" | `/api/v3/horoscope/chinese/bazi` | POST |

## Human Design

| User asks about... | Endpoint | Method |
|---|---|---|
| "My bodygraph" | `/api/v3/human-design/bodygraph` | POST |
| "My human design type" | `/api/v3/human-design/type` | POST |
| "Human design compatibility" | `/api/v3/human-design/compatibility` | POST |
| "Human design transits" | `/api/v3/human-design/transits` | POST |

## Kabbalah

| User asks about... | Endpoint | Method |
|---|---|---|
| "Tree of life chart" | `/api/v3/kabbalah/tree-of-life-chart` | POST |
| "Birth angels" | `/api/v3/kabbalah/birth-angels` | POST |
| "Tikkun" (soul correction) | `/api/v3/kabbalah/tikkun` | POST |
| "Gematria" | `/api/v3/kabbalah/gematria` | POST |

## Astrocartography

| User asks about... | Endpoint | Method |
|---|---|---|
| "Astrocartography map" | `/api/v3/astrocartography/map` | POST |
| "Best places to live" | `/api/v3/astrocartography/search-locations` | POST |
| "Compare locations" | `/api/v3/astrocartography/compare-locations` | POST |
| "Power zones" | `/api/v3/astrocartography/power-zones` | POST |
| "Location analysis" | `/api/v3/astrocartography/location-analysis` | POST |
| "Relocation chart" | `/api/v3/astrocartography/relocation-chart` | POST |

## Eclipses

| User asks about... | Endpoint | Method |
|---|---|---|
| "Upcoming eclipses" | `/api/v3/eclipses/upcoming` | GET |
| "Eclipse impact on my chart" | `/api/v3/eclipses/natal-check` | POST |
| "Eclipse interpretation" | `/api/v3/eclipses/interpretation` | POST |

## Fixed Stars

| User asks about... | Endpoint | Method |
|---|---|---|
| "Fixed star positions" | `/api/v3/fixed-stars/positions` | POST |
| "Fixed star conjunctions" | `/api/v3/fixed-stars/conjunctions` | POST |
| "Fixed stars report" | `/api/v3/fixed-stars/report` | POST |

## Palmistry

| User asks about... | Endpoint | Method |
|---|---|---|
| "Palm analysis" (raw data) | `/api/v3/palmistry/analysis` | POST |
| "Palm reading" (interpretation) | `/api/v3/palmistry/reading` | POST |
| "Palm + astrology integration" | `/api/v3/palmistry/astro` | POST |
| "Palm compatibility" | `/api/v3/palmistry/compatibility` | POST |

## Business & Financial Insights

| User asks about... | Endpoint | Method |
|---|---|---|
| "Team dynamics" | `/api/v3/insights/business/team-dynamics` | POST |
| "Hiring compatibility" | `/api/v3/insights/business/hiring-compatibility` | POST |
| "Leadership style" | `/api/v3/insights/business/leadership-style` | POST |
| "Business timing" | `/api/v3/insights/business/business-timing` | POST |
| "Market timing" | `/api/v3/insights/financial/market-timing` | POST |
| "Crypto timing" | `/api/v3/insights/financial/crypto-timing` | POST |

## Wellness Insights

| User asks about... | Endpoint | Method |
|---|---|---|
| "Body mapping" | `/api/v3/insights/wellness/body-mapping` | POST |
| "Biorhythms" | `/api/v3/insights/wellness/biorhythms` | POST |
| "Energy patterns" | `/api/v3/insights/wellness/energy-patterns` | POST |
| "Wellness score" | `/api/v3/insights/wellness/wellness-score` | POST |
| "Moon wellness calendar" | `/api/v3/insights/wellness/moon-wellness` | POST |

## Traditional Astrology

| User asks about... | Endpoint | Method |
|---|---|---|
| "Annual profections" | `/api/v3/traditional/analysis/annual-profection` | POST |
| "Traditional analysis" | `/api/v3/traditional/analysis` | POST |
| "Dignities analysis" | `/api/v3/traditional/dignities` | POST |
| "Lots (Arabic parts)" | `/api/v3/traditional/lots` | POST |
| "Profections" | `/api/v3/traditional/profections` | POST |

## Horary Astrology

| User asks about... | Endpoint | Method |
|---|---|---|
| "Horary chart" | `/api/v3/horary/chart` | POST |
| "Analyze horary question" | `/api/v3/horary/analyze` | POST |
| "Fertility question" | `/api/v3/horary/fertility-analysis` | POST |

## Glossary (reference data)

| Data needed | Endpoint | Method |
|---|---|---|
| Available house systems | `/api/v3/glossary/house-systems` | GET |
| Zodiac types | `/api/v3/glossary/zodiac-types` | GET |
| Active points (planets, etc.) | `/api/v3/glossary/active-points` | GET |
| Supported languages | `/api/v3/glossary/languages` | GET |
| Cities search | `/api/v3/glossary/cities?search=...` | GET |
| Countries | `/api/v3/glossary/countries` | GET |
| Themes | `/api/v3/glossary/themes` | GET |
| Fixed stars list | `/api/v3/glossary/fixed-stars` | GET |
