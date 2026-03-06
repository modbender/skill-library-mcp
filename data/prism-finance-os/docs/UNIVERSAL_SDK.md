# PRISM OS — Universal Finance SDK
## Complete Vertical & Tool Registry

---

## The 15 Finance Verticals

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PRISM OS UNIVERSAL SDK                             │
├──────────────┬──────────────┬──────────────┬──────────────┬────────────────┤
│   EQUITIES   │ FIXED INCOME │   FOREX/FX   │  COMMODITIES │  REAL ESTATE   │
├──────────────┼──────────────┼──────────────┼──────────────┼────────────────┤
│  DERIVATIVES │    MACRO     │ PRIVATE MKT  │ ALTERNATIVES │      ESG       │
├──────────────┼──────────────┼──────────────┼──────────────┼────────────────┤
│  CORP FIN    │   BANKING    │   INSURANCE  │  PERSONAL    │  CRYPTO/DEFI   │
└──────────────┴──────────────┴──────────────┴──────────────┴────────────────┘
                         ↑ All speak Canonical IDs ↑
```

---

## MODULE 11: EQUITIES
*Who uses it: Portfolio managers, retail investors, equity analysts, quant funds, algo traders*

```typescript
// ─── PRICE & QUOTES ───
prism.equities.getQuote(ticker)                  // Real-time L1 quote: bid/ask/last/size
prism.equities.getQuoteMulti(tickers[])          // Batch quotes
prism.equities.getExtendedHoursQuote(ticker)     // Pre/post market
prism.equities.getHistorical(ticker, from, to, interval)  // OHLCV
prism.equities.getIntradayData(ticker, interval) // 1m/5m/15m intraday

// ─── FUNDAMENTALS ───
prism.equities.getFundamentals(ticker)           // P/E, EPS, revenue, margins, ROE, ROIC
prism.equities.getIncomeStatement(ticker, period)   // Annual/quarterly
prism.equities.getBalanceSheet(ticker, period)
prism.equities.getCashFlowStatement(ticker, period)
prism.equities.getKeyMetrics(ticker)             // Quick ratio, current ratio, D/E, etc.
prism.equities.getSegmentRevenue(ticker)         // Business segment breakdown
prism.equities.getGeographicRevenue(ticker)      // Revenue by region
prism.equities.getEarningsHistory(ticker)        // Historical EPS + beats/misses
prism.equities.getGuidance(ticker)               // Management guidance
prism.equities.getDCFValuation(ticker)           // Discounted cash flow model
prism.equities.getComparableCompanies(ticker)    // Peer group comps

// ─── EARNINGS ───
prism.equities.getEarningsCalendar(from, to)     // Upcoming earnings dates
prism.equities.getEarningsEstimates(ticker)      // Consensus EPS/revenue estimates
prism.equities.getEarningsSurprise(ticker, limit)  // Historical beat/miss
prism.equities.getAnalystRevisions(ticker)       // Estimate revision momentum
prism.equities.getEarningsTranscript(ticker, quarter)  // Full call transcript
prism.equities.getEarningsSentiment(ticker, quarter)   // AI sentiment on transcript

// ─── ANALYST COVERAGE ───
prism.equities.getAnalystRatings(ticker)         // Buy/sell/hold consensus
prism.equities.getRatingHistory(ticker)          // Historical rating changes
prism.equities.getPriceTargets(ticker)           // Analyst price targets
prism.equities.getUpsideDownside(ticker)         // Implied upside from consensus PT
prism.equities.getAnalystEstimates(ticker, metric) // Revenue/EPS forward estimates

// ─── CORPORATE ACTIONS ───
prism.equities.getDividends(ticker)              // Dividend history + yield
prism.equities.getDividendCalendar(from, to)     // Upcoming ex-div dates
prism.equities.getStockSplits(ticker)            // Historical splits
prism.equities.getShareBuybacks(ticker)          // Buyback programs
prism.equities.getMergerActivity(ticker)         // M&A history and rumors
prism.equities.getIPOCalendar(from, to)          // Upcoming IPOs
prism.equities.getSPACActivity()                 // Active SPACs

// ─── OWNERSHIP & FLOW ───
prism.equities.getInstitutionalOwnership(ticker)    // 13F holders
prism.equities.getOwnershipChanges(ticker, quarter) // 13F changes QoQ
prism.equities.getInsiderTransactions(ticker)       // SEC Form 4 filings
prism.equities.getShortInterest(ticker)             // Short % float, borrow rate
prism.equities.getShortSqueezeScore(ticker)         // SI + momentum + borrow rate
prism.equities.getDarkPoolActivity(ticker)          // Dark pool prints
prism.equities.getOptionsFlow(ticker)               // Unusual options activity
prism.equities.getRetailFlow(ticker)                // Retail buy/sell pressure (Robinhood etc.)

// ─── SCREENING ───
prism.equities.screen(filters)                   // Multi-factor stock screener
prism.equities.getFactorExposure(ticker)         // Value, momentum, quality, size factors
prism.equities.getQuantScore(ticker)             // Composite quantitative score
prism.equities.getSectorPerformance(sector, window) // Sector rotations

// ─── TECHNICAL ───
prism.equities.getIndicator(ticker, indicator, params)  // RSI, MACD, Bollinger, EMA
prism.equities.getPatternRecognition(ticker)     // Head & shoulders, flags, etc.
prism.equities.getSupportResistance(ticker)      // Key price levels
prism.equities.getRelativeStrength(ticker, benchmark) // vs SPY, sector ETF
```

---

## MODULE 12: FIXED INCOME
*Who uses it: Bond traders, fixed income PMs, liability-driven investors, insurance asset managers, pensions*

```typescript
// ─── BOND PRICING ───
prism.fixedIncome.getPrice(cusip)               // Clean/dirty price
prism.fixedIncome.getYield(cusip)               // YTM, YTC, current yield
prism.fixedIncome.getSpread(cusip, benchmark?)  // OAS, z-spread, G-spread
prism.fixedIncome.getDV01(cusip)                // Dollar value of 1 basis point
prism.fixedIncome.getConvexity(cusip)
prism.fixedIncome.getModifiedDuration(cusip)
prism.fixedIncome.getMacaulayDuration(cusip)
prism.fixedIncome.getAccruedInterest(cusip)
prism.fixedIncome.getPriceByYield(cusip, yield) // Reverse: yield → price
prism.fixedIncome.getYieldByPrice(cusip, price) // Forward: price → yield

// ─── YIELD CURVE ───
prism.fixedIncome.getYieldCurve(country?, date?) // Full treasury yield curve
prism.fixedIncome.getForwardCurve(currency)      // Forward rate curve
prism.fixedIncome.getSwapCurve(currency)         // Interest rate swap curve
prism.fixedIncome.getCurveHistory(country, from, to, tenors[]) // Historical yields
prism.fixedIncome.getSpreadsHistory(spread_type, from, to)  // HY/IG spread history
prism.fixedIncome.get2s10s()                     // 2yr-10yr spread (recession signal)
prism.fixedIncome.getInversionAlert()            // Yield curve inversion status

// ─── CREDIT ───
prism.fixedIncome.getCreditRating(cusip)         // S&P, Moody's, Fitch
prism.fixedIncome.getRatingHistory(issuer)       // Rating change history
prism.fixedIncome.getCDSSpread(entity)           // Credit default swap spread
prism.fixedIncome.getDefaultProbability(entity)  // Implied default probability from CDS
prism.fixedIncome.getRecoveryRate(entity)        // Historical recovery rates by seniority
prism.fixedIncome.getCreditWatch(issuer)         // On watch for upgrade/downgrade?

// ─── ISSUANCE & SUPPLY ───
prism.fixedIncome.getIssuanceCalendar()          // Upcoming bond issuances
prism.fixedIncome.getTreasuryAuctions()          // Fed auction schedule + results
prism.fixedIncome.getIssuanceVolume(sector, window) // IG/HY new issuance flow
prism.fixedIncome.getCouponPayments(cusips[], from, to) // Cash flow modeling

// ─── SEARCH & SCREENING ───
prism.fixedIncome.search(query)                  // CUSIP, ISIN, issuer name
prism.fixedIncome.screen(filters)                // Rating, maturity, sector, yield, spread
prism.fixedIncome.getIssuerBonds(issuer)         // All bonds by issuer
prism.fixedIncome.getMaturingBonds(from, to)     // Bonds maturing in window

// ─── MBS / ABS / STRUCTURED ───
prism.fixedIncome.getMBSData(cusip)              // Prepayment speed, WAL, PSA
prism.fixedIncome.getCPRHistory(cusip)           // Conditional prepayment rate
prism.fixedIncome.getABSData(cusip)              // Asset-backed security detail
prism.fixedIncome.getCLOData(cusip)              // CLO tranche detail

// ─── PORTFOLIO ANALYTICS ───
prism.fixedIncome.getPortfolioDuration(holdings[])  // Aggregate duration
prism.fixedIncome.getDV01Portfolio(holdings[])
prism.fixedIncome.getYieldPortfolio(holdings[])
prism.fixedIncome.keyRateDuration(holdings[])    // KRD across tenors
prism.fixedIncome.stressTest(holdings[], scenarios[]) // Parallel/twist/butterfly
```

---

## MODULE 13: FOREX / FX
*Who uses it: FX traders, multinationals, international investors, import/export businesses, travel*

```typescript
// ─── SPOT RATES ───
prism.fx.getRate(base, quote)               // EUR/USD, BTC/USD etc.
prism.fx.getRateMulti(pairs[])              // Batch rates
prism.fx.getCrossRate(base, quote)          // Derived cross rate
prism.fx.getHistorical(pair, from, to, interval)
prism.fx.getIntraday(pair, interval)

// ─── FORWARD & SWAP RATES ───
prism.fx.getForwardRate(pair, tenor)        // 1W/1M/3M/6M/1Y forward
prism.fx.getForwardPoints(pair, tenor)      // Pips premium/discount
prism.fx.getSwapRate(pair, tenor)           // FX swap all-in rate
prism.fx.getImpliedRate(pair, tenor)        // Interest rate parity implied rate
prism.fx.getNDF(pair, tenor)               // Non-deliverable forward (EM)

// ─── VOLATILITY ───
prism.fx.getIV(pair, tenor)                // Implied volatility
prism.fx.getVolSmile(pair, tenor)          // Vol surface (25D RR, 25D Fly)
prism.fx.getRiskReversal(pair, tenor)      // Risk reversal
prism.fx.getRealizedVol(pair, window)      // Historical realized vol

// ─── CENTRAL BANK & POLICY ───
prism.fx.getCentralBankRates()             // All major CB policy rates
prism.fx.getRateDecisionCalendar()         // FOMC, ECB, BOJ, BOE dates
prism.fx.getInterventionHistory(pair)      // CB FX intervention history
prism.fx.getReserves(country)              // FX reserves by central bank

// ─── FLOWS & POSITIONING ───
prism.fx.getCOTReport(pair)               // CFTC Commitment of Traders
prism.fx.getBankPositioning(pair)         // BIS/bank survey positioning
prism.fx.getRetailSentiment(pair)         // Retail trader bias (FXSM)
prism.fx.getFlowData(pair, window)        // Real money vs spec flows

// ─── CONVERSION & UTILITY ───
prism.fx.convert(amount, from, to)         // Convert with live rate
prism.fx.convertHistorical(amount, from, to, date) // At historical rate
prism.fx.getCountryCurrency(country)       // Country → currency code
prism.fx.getPegStatus(currency)            // Is this currency pegged?
prism.fx.getSanctionedCurrencies()         // OFAC sanctioned currencies

// ─── EMERGING MARKETS ───
prism.fx.getEMRisk(currency)              // EM FX risk score
prism.fx.getCarryRank()                   // EM carry trade ranking
prism.fx.getCapitalControls(country)       // Restrictions on capital flows
```

---

## MODULE 14: COMMODITIES
*Who uses it: Commodities traders, energy companies, agricultural businesses, metals traders, mining cos.*

```typescript
// ─── SPOT PRICES ───
prism.commodities.getPrice(commodity)           // XAU, XAG, CL, NG, HG, ZC, ZW, etc.
prism.commodities.getPriceMulti(commodities[])
prism.commodities.getHistorical(commodity, from, to, interval)
prism.commodities.getBenchmarkPrices()          // WTI, Brent, Gold, Silver, etc.

// ─── FUTURES ───
prism.commodities.getFuturesChain(commodity)    // All listed futures contracts
prism.commodities.getFuturesPrice(contract)     // Specific contract price
prism.commodities.getRollYield(commodity)       // Contango/backwardation roll cost
prism.commodities.getBasis(commodity, location) // Spot vs futures basis
prism.commodities.getForwardCurve(commodity)    // Full forward curve
prism.commodities.getContangoBackwardation(commodity) // Curve structure

// ─── ENERGY ───
prism.commodities.getOilPrice(grade?)           // WTI, Brent, Dubai, Urals
prism.commodities.getNaturalGasPrice(hub?)      // Henry Hub, NBP, TTF, JKM
prism.commodities.getRefiningMargin(region)     // Crack spread / refinery margin
prism.commodities.getPowerPrice(region)         // Electricity price by hub
prism.commodities.getGasCrackerSpread()         // Gas-to-chemicals economics
prism.commodities.getLNGPrices()                // LNG spot by region
prism.commodities.getOilInventories()           // EIA/API weekly inventory report
prism.commodities.getRigCount()                 // Baker Hughes rig count
prism.commodities.getPipelineCapacity(route)    // Midstream capacity data

// ─── METALS ───
prism.commodities.getMetalPrice(metal)          // Gold, silver, copper, platinum, palladium
prism.commodities.getLMEData(metal)             // London Metal Exchange cash/3M
prism.commodities.getLeaserate(metal)           // Metal lending rates
prism.commodities.getGoldSilverRatio()
prism.commodities.getMineOutput(metal, country) // Production by country
prism.commodities.getRecyclingRate(metal)       // Scrap supply
prism.commodities.getRefineryData(metal)        // Refinery production/capacity

// ─── AGRICULTURAL ───
prism.commodities.getCropPrice(crop)            // Corn, wheat, soybeans, cotton, etc.
prism.commodities.getCropReport()               // USDA WASDE report data
prism.commodities.getCropYield(crop, country, year) // Historical/projected yield
prism.commodities.getPlantingProgress()         // USDA planting/harvest progress
prism.commodities.getWeatherImpact(crop, region) // Drought/flood risk to production
prism.commodities.getExportInspections(crop)    // Weekly export data
prism.commodities.getCarryOut(crop)             // Ending stocks forecast
prism.commodities.getSoftsPrice(soft)           // Coffee, cocoa, sugar, OJ

// ─── SUPPLY & DEMAND ───
prism.commodities.getInventoryData(commodity)   // Storage levels
prism.commodities.getProductionData(commodity)  // Global production
prism.commodities.getConsumptionData(commodity) // Global consumption
prism.commodities.getTradeFlows(commodity)      // Import/export flows
prism.commodities.getSeasonalPatterns(commodity) // Historical seasonality

// ─── SHIPPING ───
prism.commodities.getBalticDryIndex()           // BDI
prism.commodities.getShippingRates(route)       // Tanker/bulk rates by route
prism.commodities.getPortCongestion(port)       // Port delay data
prism.commodities.getVesselTracking(commodity)  // Commodity vessels in transit
```

---

## MODULE 15: REAL ESTATE
*Who uses it: RE investors, brokers, developers, REITs, mortgage lenders, property managers, appraisers*

```typescript
// ─── PROPERTY DATA ───
prism.realEstate.getPropertyData(address)       // Full property profile
prism.realEstate.getValuation(address)          // AVM (automated valuation model)
prism.realEstate.getAVMConfidence(address)      // Valuation confidence interval
prism.realEstate.getOwnershipHistory(address)   // Chain of title
prism.realEstate.getSaleHistory(address)        // Transaction history with prices
prism.realEstate.getPermitHistory(address)      // Building permits
prism.realEstate.getTaxAssessment(address)      // Assessed value + property tax
prism.realEstate.getPropertyCharacteristics(address) // Beds/baths/sqft/year built/lot

// ─── MARKET DATA ───
prism.realEstate.getMarketMetrics(zip?, msa?)   // Median price, DOM, inventory, absorption
prism.realEstate.getPriceHistory(zip, from, to) // Price index history
prism.realEstate.getAppreciationRate(zip, window) // Annualized appreciation
prism.realEstate.getInventoryLevels(zip)        // Months of supply
prism.realEstate.getDaysOnMarket(zip, type?)    // Average DOM by property type
prism.realEstate.getPriceReductions(zip)        // % listings with price cuts
prism.realEstate.getAbsorptionRate(zip)         // Rate at which homes sell
prism.realEstate.getListPriceToSaleRatio(zip)   // How close to ask do homes sell?

// ─── COMPS ───
prism.realEstate.getComps(address, radius, filters) // Comparable sales
prism.realEstate.getActiveListings(zip, filters)    // On-market comps
prism.realEstate.getPendingSales(zip)               // Under contract
prism.realEstate.getExpiredListings(zip)            // Failed to sell listings

// ─── RENTAL MARKET ───
prism.realEstate.getRentalRate(address, type?)  // Estimated rent
prism.realEstate.getRentalComps(address)        // Comparable rentals
prism.realEstate.getVacancyRate(zip, type?)     // By property type
prism.realEstate.getRentGrowth(zip, window)     // Rent change over time
prism.realEstate.getCapRate(address)            // Net operating income / value
prism.realEstate.getGrossYield(address)         // Gross rental yield
prism.realEstate.getCashOnCash(address, finParams) // CoC return with financing
prism.realEstate.getNOI(address)                // Net operating income estimate
prism.realEstate.getDSCR(address, loanAmount, rate) // Debt service coverage ratio

// ─── INVESTMENT ANALYSIS ───
prism.realEstate.getIRR(address, holdPeriod, assumptions) // Internal rate of return
prism.realEstate.getNPV(cashflows[], discountRate) // Net present value
prism.realEstate.getBreakEvenRent(address, finParams)
prism.realEstate.getFlipAnalysis(address)       // Buy-rehab-sell analysis
prism.realEstate.getBRRRRAnalysis(address)      // Buy-Rehab-Rent-Refinance-Repeat
prism.realEstate.getScenarioModel(address, scenarios[]) // Bull/base/bear returns

// ─── MORTGAGE & FINANCING ───
prism.realEstate.getMortgageRates(type?)        // 30yr, 15yr, ARM rates
prism.realEstate.getMortgageRateHistory(from, to) // Historical rate data
prism.realEstate.getMortgagePayment(principal, rate, term) // Monthly payment calc
prism.realEstate.getAffordability(income, rate) // Max purchase price
prism.realEstate.getLTVRatio(address, loanAmount) // Loan-to-value
prism.realEstate.getDSTRLoans()                 // DSCR loan rates/programs
prism.realEstate.getHardMoneyRates()            // Hard money lending rates
prism.realEstate.getBridgeLoanRates()

// ─── ZONING & DEVELOPMENT ───
prism.realEstate.getZoning(address)             // Zoning classification + uses
prism.realEstate.getZoningOverlays(address)     // Historic districts, flood zones
prism.realEstate.getDevelopmentPotential(address) // ADU potential, density bonus
prism.realEstate.getFARCalculation(address)     // Floor area ratio
prism.realEstate.getBuildingCosts(zip, type)    // $/sqft construction cost
prism.realEstate.getPermitVolume(zip, window)   // Development activity signal

// ─── DEMOGRAPHICS & NEIGHBORHOOD ───
prism.realEstate.getDemographics(zip)           // Population, income, age, growth
prism.realEstate.getSchoolRatings(address)      // School district scores
prism.realEstate.getCrimeData(zip)              // Crime rates by category
prism.realEstate.getWalkScore(address)          // Walk/bike/transit scores
prism.realEstate.getJobMarket(msa)              // Employment, job growth
prism.realEstate.getMigrationTrends(msa)        // Population in/out flows
prism.realEstate.getAffordabilityIndex(msa)     // Income vs home price ratio

// ─── REITs ───
prism.realEstate.getREITData(ticker)            // REIT fundamentals: FFO, AFFO, NAV
prism.realEstate.getFFO(ticker)                 // Funds from operations
prism.realEstate.getNAVPerShare(ticker)         // Net asset value
prism.realEstate.getSameStoreSales(ticker)      // SS revenue growth
prism.realEstate.getOccupancyRate(ticker)       // Portfolio occupancy
prism.realEstate.getREITScreen(filters)         // Screen REITs by sector/metrics
prism.realEstate.getREITSectorData(sector)      // Office/retail/industrial/MF/self-storage
```

---

## MODULE 16: MACRO & ECONOMICS
*Who uses it: Macro traders, hedge funds, global asset allocators, economists, central bank watchers*

```typescript
// ─── ECONOMIC INDICATORS ───
prism.macro.getGDP(country, frequency?)         // GDP + growth rate
prism.macro.getGDPForecast(country)             // Consensus GDP forecast
prism.macro.getInflation(country)               // CPI, PCE, PPI, core
prism.macro.getInflationExpectations(country, tenor) // Breakevens, surveys
prism.macro.getUnemployment(country)            // Unemployment + U6
prism.macro.getJobsReport(country)              // Latest employment report
prism.macro.getRetailSales(country)             // Consumer spending
prism.macro.getISM(country)                     // Manufacturing/services PMI
prism.macro.getPMI(country, sector)             // Markit/S&P PMIs
prism.macro.getConsumerConfidence(country)      // Conference Board, UMich
prism.macro.getHousingStarts(country)
prism.macro.getDurableGoods(country)
prism.macro.getTradeBalance(country)
prism.macro.getCurrentAccount(country)

// ─── MONETARY POLICY ───
prism.macro.getCentralBankRate(country)         // Policy rate
prism.macro.getRateDecision(country)            // Latest CB decision
prism.macro.getForwardGuidance(country)         // CB language analysis
prism.macro.getFedFundsImplied()                // Fed funds futures implied rate
prism.macro.getHikeProbability(numHikes, date)  // Market-implied hike probability
prism.macro.getQEBalance(country)               // Central bank balance sheet
prism.macro.getMoneySupply(country, measure)    // M1/M2/M3

// ─── GOVERNMENT & FISCAL ───
prism.macro.getGovernmentDebt(country)          // Debt/GDP
prism.macro.getFiscalDeficit(country)           // Budget deficit
prism.macro.getGovernmentSpending(country)      // G component of GDP
prism.macro.getTaxRevenue(country)

// ─── GLOBAL FLOWS ───
prism.macro.getForeignReserves(country)         // FX reserves
prism.macro.getTICData()                        // Treasury International Capital flows
prism.macro.getCapitalFlows(country, window)    // Portfolio + FDI flows

// ─── ECONOMIC CALENDAR ───
prism.macro.getCalendar(from, to, countries[]?) // All economic releases
prism.macro.getHighImpactEvents(window)         // Market-moving events only
prism.macro.getConsensusEstimate(eventId)       // Market consensus vs prior
prism.macro.getActualVsExpected(eventId)        // Surprise score

// ─── RECESSION & RISK INDICATORS ───
prism.macro.getRecessionProbability(country)    // Model-based recession probability
prism.macro.getLeadingIndicators(country)       // OECD CLI, CB LEI
prism.macro.getFinancialConditions(country)     // FCI (Goldman, Chicago Fed)
prism.macro.getCreditImpulse(country)           // Rate of change of credit growth
prism.macro.getSovereignRisk(country)           // CDS-implied default risk
prism.macro.getGeopoliticalRisk()               // GPR index

// ─── CROSS-ASSET ───
prism.macro.getCorrelationMatrix(assets[])      // Cross-asset correlation
prism.macro.getRiskOnRiskOff()                  // Market risk regime
prism.macro.getVolatilityRegime()               // VIX term structure, VVIX
prism.macro.getTailRiskIndicators()             // Skew, put/call ratio, etc.
```

---

## MODULE 17: DERIVATIVES
*Who uses it: Options traders, structured products desks, risk managers, volatility arb funds*

```typescript
// ─── OPTIONS ───
prism.derivatives.getOptionsChain(ticker, expiry?) // Full options chain
prism.derivatives.getOptionPrice(ticker, strike, expiry, type) // Single option
prism.derivatives.getGreeks(ticker, strike, expiry, type)  // Delta, gamma, theta, vega, rho
prism.derivatives.getImpliedVol(ticker, strike, expiry)    // IV for specific option
prism.derivatives.getIVSurface(ticker)          // Full IV surface
prism.derivatives.getTermStructure(ticker)      // IV by expiry (term structure)
prism.derivatives.getSkew(ticker, expiry)       // Skew by strike
prism.derivatives.getVIX()                      // VIX and term structure
prism.derivatives.getVIXFutures()               // VIX futures curve

// ─── PRICING MODELS ───
prism.derivatives.blackScholes(params)          // BS option price
prism.derivatives.binomialTree(params)          // American option pricing
prism.derivatives.monteCarloOption(params)      // Monte Carlo simulation
prism.derivatives.barrierOption(params)         // Barrier/knock-in/out
prism.derivatives.asianOption(params)           // Asian/average price option

// ─── FLOW & POSITIONING ───
prism.derivatives.getUnusualActivity(ticker)    // Unusual options flow
prism.derivatives.getDarkPoolPrints(ticker)     // Dark pool options
prism.derivatives.getGEX(ticker)               // Gamma exposure
prism.derivatives.getDEX(ticker)               // Delta exposure
prism.derivatives.getNetGamma(ticker)           // MM net gamma position
prism.derivatives.getPinRisk(ticker, expiry)    // Max pain / pin risk level
prism.derivatives.getPutCallRatio(ticker)       // P/C ratio + history

// ─── STRATEGIES ───
prism.derivatives.analyzeStrategy(legs[])       // P&L diagram for any strategy
prism.derivatives.getIronCondorParams(ticker)   // Suggested IC strikes/strikes
prism.derivatives.getButterflyParams(ticker)    // Butterfly spread params
prism.derivatives.findCoveredCallYield(ticker)  // Best covered call by yield
prism.derivatives.findCashSecuredPut(ticker)    // Best CSP by premium

// ─── FUTURES ───
prism.derivatives.getFuturesChain(product)      // All listed contracts
prism.derivatives.getFuturesPrice(contract)     // Specific contract
prism.derivatives.getBasis(product)             // Futures basis
prism.derivatives.getRollCost(product)          // Cost to roll position
prism.derivatives.getOpenInterestByStrike(ticker, expiry) // OI by strike
```

---

## MODULE 18: PRIVATE MARKETS
*Who uses it: VC investors, PE firms, startup operators, angel investors, LP allocators*

```typescript
// ─── COMPANY DATA ───
prism.private.getCompany(companyId)             // Private company profile
prism.private.searchCompanies(query, filters)   // Search private cos
prism.private.getFundamentals(companyId)        // Revenue, growth, margins (est.)
prism.private.getEmployeeCount(companyId)       // Headcount + growth
prism.private.getWebTraffic(domain)             // Similarweb-style traffic data
prism.private.getAppRankings(appId)             // App store rankings

// ─── FUNDRAISING ───
prism.private.getFundingHistory(companyId)      // All rounds with amounts
prism.private.getLatestRound(companyId)         // Most recent funding round
prism.private.getInvestors(companyId)           // Investor list with ownership est.
prism.private.getValuationHistory(companyId)    // Post-money valuations
prism.private.getCapTable(companyId)            // Estimated cap table

// ─── DEAL FLOW ───
prism.private.getRecentDeals(filters)           // Recent funding rounds
prism.private.getDealsByInvestor(investorId)    // Portfolio of a VC/PE firm
prism.private.getDealsBySector(sector)          // Sector deal flow
prism.private.getEmergingSectors()              // Hot sectors by deal count/volume

// ─── SECONDARIES ───
prism.private.getSecondaryBid(companyId)        // Secondary market bid/ask
prism.private.getLiquidityScore(companyId)      // How liquid is this private stock?
prism.private.getTenderOffers()                 // Active tender offers

// ─── VC / PE FUND DATA ───
prism.private.getFundData(fundId)               // Fund AUM, vintage, strategy
prism.private.getFundPerformance(fundId)        // IRR, TVPI, DPI, RVPI
prism.private.getInvestorProfile(investorId)    // Investment thesis + portfolio
prism.private.getPortfolioOverlap(fund1, fund2) // Shared portfolio companies

// ─── EXITS ───
prism.private.getIPOPipeline()                  // Companies preparing for IPO
prism.private.getAcquisitionTargets(sector)     // Likely M&A targets
prism.private.getExitHistory(companyId)         // Historical exits in sector
```

---

## MODULE 19: ALTERNATIVE ASSETS
*Who uses it: Family offices, collectors, alternative investment platforms, hedge funds*

```typescript
// ─── ART ───
prism.alternatives.getArtIndex(category?)       // Art price index (Artprice, Mei Moses)
prism.alternatives.getArtistMarket(artist)      // Artist-specific market data
prism.alternatives.getAuctionResults(filters)   // Recent auction hammer prices
prism.alternatives.getUpcomingAuctions()        // Upcoming major sales
prism.alternatives.getArtLending()              // Art-backed loan rates

// ─── COLLECTIBLES ───
prism.alternatives.getSportsCardsIndex()        // Trading card market index
prism.alternatives.getCardValue(cardId)         // Specific card valuation
prism.alternatives.getWineIndex(region?)        // Liv-ex fine wine indices
prism.alternatives.getWineValue(wine, vintage)  // Specific wine price
prism.alternatives.getWatchIndex(brand?)        // Watch market index
prism.alternatives.getWatchValue(reference)     // Specific reference price

// ─── INFRASTRUCTURE ───
prism.alternatives.getInfrastructureDeals()     // Infrastructure deal flow
prism.alternatives.getInfraYields(sector)       // Infrastructure yield by sector (toll, utility, airport)

// ─── TIMBERLAND / FARMLAND ───
prism.alternatives.getFarmlandIndex(region?)    // NCREIF Farmland Index
prism.alternatives.getFarmlandCap(crop, region) // Cap rates by crop type
prism.alternatives.getTimberIndex()             // NCREIF Timber Index

// ─── VOLATILITY AS AN ASSET ───
prism.alternatives.getVIXProducts()             // VIX ETPs, funds
prism.alternatives.getVolArb()                  // Realized vs implied vol spread
```

---

## MODULE 20: ESG & IMPACT
*Who uses it: ESG-focused funds, institutional allocators, corporate sustainability teams, impact investors*

```typescript
// ─── ESG SCORES ───
prism.esg.getScore(ticker)                      // Composite ESG score
prism.esg.getESGBreakdown(ticker)               // E, S, G sub-scores
prism.esg.getControversies(ticker)              // ESG controversy events
prism.esg.getESGRating(ticker, provider)        // MSCI, Sustainalytics, ISS
prism.esg.getPeerComparison(ticker)             // ESG vs sector peers

// ─── ENVIRONMENTAL ───
prism.esg.getCarbonEmissions(ticker)            // Scope 1/2/3 emissions
prism.esg.getCarbonIntensity(ticker)            // Emissions/revenue
prism.esg.getClimateRisk(ticker)                // Physical + transition risk
prism.esg.getSBTiStatus(ticker)                 // Science-based targets
prism.esg.getEnergyMix(ticker)                  // Renewable % of energy use
prism.esg.getWaterUsage(ticker)
prism.esg.getWasteData(ticker)

// ─── SOCIAL ───
prism.esg.getLaborPractices(ticker)             // Workforce data, safety
prism.esg.getDiversityMetrics(ticker)           // Board/exec diversity
prism.esg.getSupplyChainRisk(ticker)            // Supply chain ESG risk
prism.esg.getCommunityImpact(ticker)

// ─── GOVERNANCE ───
prism.esg.getBoardComposition(ticker)           // Independence, diversity
prism.esg.getExecutiveCompensation(ticker)      // CEO pay ratio
prism.esg.getShareholderRights(ticker)          // Dual class, poison pill
prism.esg.getAuditQuality(ticker)               // Auditor, restatements

// ─── SCREENING ───
prism.esg.screen(filters)                       // Screen by ESG criteria
prism.esg.getPAIscore(ticker)                   // Principal Adverse Impact (SFDR)
prism.esg.getExclusionLists()                   // Weapons, tobacco, fossil fuel lists
prism.esg.getTaxonomy(ticker, regulation)       // EU taxonomy alignment %

// ─── CARBON MARKETS ───
prism.esg.getCarbonPrice(market)                // EU ETS, California CCA, RGGI
prism.esg.getOffsetPrice(standard, type)        // VCS, Gold Standard credits
prism.esg.getCarbonOffset(volume, criteria)     // Find offset credits
prism.esg.getEmissionsData(country)             // Country-level emissions
```

---

## MODULE 21: CORPORATE FINANCE / FP&A
*Who uses it: CFOs, FP&A teams, investment bankers, M&A advisors, corporate development*

```typescript
// ─── VALUATION ───
prism.corpfin.getDCF(ticker, assumptions)       // Full DCF model
prism.corpfin.getCompsValuation(ticker)         // Trading comps (EV/EBITDA, P/E, etc.)
prism.corpfin.getPrecedentTransactions(sector)  // M&A transaction multiples
prism.corpfin.getLBOModel(ticker, finParams)    // LBO returns model
prism.corpfin.getSumOfParts(ticker)             // SOTP valuation
prism.corpfin.getWACCComponents(ticker)         // Beta, cost of equity, WACC

// ─── M&A ───
prism.corpfin.getMAActivity(sector, window)     // Recent M&A deals
prism.corpfin.getAcquisitionMultiples(sector)   // Transaction EV/EBITDA by sector
prism.corpfin.getSynergies(acquirer, target)    // Revenue + cost synergy estimate
prism.corpfin.getAccretionDilution(params)      // Accretion/dilution model
prism.corpfin.getDealPremium(sector)            // Takeover premium history

// ─── CAPITAL STRUCTURE ───
prism.corpfin.getCapStructure(ticker)           // Debt + equity + preferred
prism.corpfin.getCreditMetrics(ticker)          // Net debt/EBITDA, interest coverage
prism.corpfin.getDebtSchedule(ticker)           // Maturity schedule
prism.corpfin.getRefinancingRisk(ticker)        // Near-term maturities
prism.corpfin.getDebtCapacity(ticker, targetLeverage)

// ─── WORKING CAPITAL ───
prism.corpfin.getWorkingCapital(ticker)         // Current assets - current liabilities
prism.corpfin.getDSO(ticker)                    // Days sales outstanding
prism.corpfin.getDIO(ticker)                    // Days inventory outstanding
prism.corpfin.getDPO(ticker)                    // Days payable outstanding
prism.corpfin.getCCC(ticker)                    // Cash conversion cycle

// ─── BENCHMARKING ───
prism.corpfin.getSectorBenchmarks(sector, metrics[]) // Industry KPI benchmarks
prism.corpfin.getMarginBenchmarks(sector)       // EBITDA/net margin by sector
prism.corpfin.getGrowthBenchmarks(sector)       // Revenue growth percentiles
prism.corpfin.getCapexBenchmarks(sector)        // Capex/revenue ratios
```

---

## MODULE 22: BANKING & CREDIT
*Who uses it: Banks, credit analysts, lenders, credit funds, rating agencies, fintech lenders*

```typescript
// ─── CREDIT ANALYSIS ───
prism.banking.getCreditScore(entity, type)      // Individual or business credit
prism.banking.getCreditReport(entity)           // Full credit profile
prism.banking.getDefaultRisk(entity)            // PD (probability of default)
prism.banking.getLGD(entity, collateral)        // Loss given default
prism.banking.getEAD(entity)                    // Exposure at default
prism.banking.getExpectedLoss(entity)           // EL = PD × LGD × EAD

// ─── LENDING RATES ───
prism.banking.getPrimeRate()                    // WSJ Prime Rate
prism.banking.getLIBOR(tenor, currency)         // Legacy LIBOR (where still used)
prism.banking.getSOFR(tenor)                    // Secured Overnight Financing Rate
prism.banking.getEURIBOR(tenor)
prism.banking.getCorporateLoanRates(rating, tenor) // Corporate loan market rates
prism.banking.getCLOIssuance()                  // CLO market activity

// ─── CONSUMER LENDING ───
prism.banking.getMortgageRates()                // 30yr, 15yr, ARM
prism.banking.getAutoLoanRates()                // New/used auto loan rates
prism.banking.getStudentLoanRates()
prism.banking.getCreditCardRates()              // Average APR by type
prism.banking.getHELOCRates()

// ─── BANKING SECTOR ───
prism.banking.getBankFundamentals(ticker)       // NIM, efficiency ratio, ROA, ROE
prism.banking.getNIM(ticker)                    // Net interest margin
prism.banking.getLoanGrowth(ticker)             // Loan book growth
prism.banking.getNCO(ticker)                    // Net charge-off rate
prism.banking.getNPL(ticker)                    // Non-performing loan ratio
prism.banking.getCapitalRatios(ticker)          // CET1, Tier 1, Total capital
prism.banking.getStressTestResults(ticker)      // Fed DFAST/CCAR results

// ─── SYNDICATED LOANS ───
prism.banking.getLoanPricingData(issuer)        // Syndicated loan spreads
prism.banking.getLeveragedLoanIndex()           // LSTA Leveraged Loan Index
prism.banking.getCovLiteTerms()                 // Covenant-lite loan stats
```

---

## MODULE 23: INSURANCE
*Who uses it: Insurance companies, actuaries, risk managers, reinsurers, InsurTech*

```typescript
// ─── ACTUARIAL DATA ───
prism.insurance.getMortalityTables(country, year) // Life mortality tables
prism.insurance.getLongevityRisk(cohort)          // Longevity risk factors
prism.insurance.getMorbidityData(condition)       // Morbidity rates
prism.insurance.getClaimsHistory(sector, peril)   // Historical claims data

// ─── CAT RISK ───
prism.insurance.getCATModel(region, peril)        // Catastrophe risk model output
prism.insurance.getHurricaneRisk(location)        // Hurricane probability
prism.insurance.getEarthquakeRisk(location)       // Seismic risk
prism.insurance.getFloodRisk(location)            // FEMA flood zone + risk score
prism.insurance.getWildfireRisk(location)         // Wildfire risk score
prism.insurance.getCATBondPricing()               // CAT bond market pricing
prism.insurance.getReinsurancePricing(peril)      // Treaty pricing trends

// ─── PROPERTY INSURANCE ───
prism.insurance.getPropertyRisk(address)          // Property risk score
prism.insurance.getReplacementCost(address)       // RCV estimation
prism.insurance.getPropertyInsuranceRates(zip)    // Market rates by zip
prism.insurance.getInsurabilityScore(address)     // Can this property be insured?

// ─── INSURANCE MARKET ───
prism.insurance.getMarketRates(line)              // Rate trends by line of business
prism.insurance.getHardeningSoftening(line)       // Market cycle indicator
prism.insurance.getInsuranceSectorData(line)      // Combined ratio, loss ratio trends
prism.insurance.getReinsurancePricing(peril)

// ─── LIFE & ANNUITY ───
prism.insurance.getAnnuityRates(type)             // Annuity pricing
prism.insurance.getLifeSettlementValue(policy)    // Life settlement valuation
prism.insurance.getViaticalData()                 // Viatical settlement market
```

---

## MODULE 24: PERSONAL FINANCE
*Who uses it: Individual investors, financial advisors, robo-advisors, budgeting apps*

```typescript
// ─── BUDGETING & CASH FLOW ───
prism.personal.categorizeTransaction(txn)       // AI transaction categorization
prism.personal.getBudgetBenchmarks(income, location) // Typical spending by category
prism.personal.getInflationImpact(expenses, period) // How much have costs risen?
prism.personal.getSavingsRate(income, expenses) // Savings rate calculation

// ─── RETIREMENT PLANNING ───
prism.personal.getRetirementProjection(params)  // Monte Carlo retirement model
prism.personal.getSafeWithdrawalRate(portfolio, horizon) // SWR calculation
prism.personal.getSocialSecurityEstimate(earningsHistory) // SS benefit estimate
prism.personal.getRMDCalculation(accountBalance, age) // Required minimum distributions
prism.personal.getRetirementIncome(params)      // Retirement income waterfall

// ─── INVESTMENT PLANNING ───
prism.personal.getRiskProfile(answers)          // Risk tolerance assessment
prism.personal.getPortfolioAllocation(riskProfile) // Model portfolio
prism.personal.getRebalancingNeeds(holdings, targets) // When/how to rebalance
prism.personal.getTaxLossHarvesting(holdings)   // TLH opportunities
prism.personal.getAssetLocation(accounts, holdings) // Tax-efficient asset placement

// ─── TAX ───
prism.personal.getCapGainsTax(lots[], salePrice) // Capital gains tax calc
prism.personal.getWashSale(holdings, trades)    // Wash sale detection
prism.personal.getTaxLotOptimization(holdings, amount) // Best lots to sell
prism.personal.getQDIEligibility(dividends[])   // Qualified dividend income
prism.personal.getMunicipalBondTEY(yield, bracket) // Tax-equivalent yield
prism.personal.getRothConversionAnalysis(params) // Roth conversion optimizer

// ─── DEBT & CREDIT ───
prism.personal.getLoanPayoff(balance, rate, payment) // Payoff timeline
prism.personal.getDebtAvalanche(debts[])        // Optimal debt payoff order
prism.personal.getRefinanceAnalysis(params)     // Should I refinance?
prism.personal.getNetWorthTracking(assets[], liabilities[]) // Net worth calc

// ─── INSURANCE NEEDS ───
prism.personal.getLifeInsuranceNeed(params)     // DIME/human life value method
prism.personal.getDisabilityNeed(income)        // Income replacement need
prism.personal.getLTCNeed(age)                  // Long-term care cost estimate
```

---

## CROSS-CUTTING TOOLS (apply to ALL verticals)

```typescript
// ─── UNIVERSAL SIGNALS ───
prism.news.getForAsset(anyAssetId, limit)       // News for any asset type
prism.news.getBreaking()                        // Breaking across all markets
prism.news.getSentiment(anyAssetId)             // Sentiment for stocks, RE, commodities

// ─── UNIVERSAL RISK ───
prism.risk.getCorrelation(assets[])             // Cross-asset correlation
prism.risk.getPortfolioVaR(holdings[], confidence) // VaR for any portfolio
prism.risk.getStressTest(holdings[], scenarios[]) // Scenario analysis
prism.risk.getMonteCarlo(holdings[], params)    // Monte Carlo simulation

// ─── UNIVERSAL PORTFOLIO ───
prism.portfolio.getHoldings(accountId)          // Any account type
prism.portfolio.getPnL(accountId, window)       // Any asset class
prism.portfolio.getAttribution(accountId)       // Return attribution

// ─── UNIVERSAL EXECUTE ───
prism.execute.placeOrder(params)                // Unified order interface
prism.execute.conditional(condition, action)    // Event-driven for any market
prism.execute.alert(condition, config)          // Price/level alerts
```

---

## Agent × Vertical Mapping

| Agent Type | Primary Modules |
|-----------|----------------|
| Equity Analyst | equities, macro, derivatives, corpfin |
| Bond PM | fixedIncome, macro, banking, risk |
| FX Trader | fx, macro, derivatives |
| Commodity Trader | commodities, macro, derivatives |
| RE Investor | realEstate, banking, macro |
| VC/PE Analyst | private, equities, corpfin |
| Macro Hedge Fund | macro, fx, derivatives, fixedIncome, commodities |
| Options Trader | derivatives, equities, market |
| ESG Fund | esg, equities, corpfin |
| Family Office | all modules |
| RIA / Advisor | personal, equities, fixedIncome, alternatives |
| Quant Fund | equities, derivatives, market + signals + execute |
| Insurance Co | insurance, fixedIncome, macro |
| Corp Treasury | fx, banking, fixedIncome, corpfin |
| Crypto/DeFi Agent | assets, market, dex, cex, defi, predictions |

---

## Tool Count (Full Universal SDK)

| Module | Tools |
|--------|-------|
| Equities | ~52 |
| Fixed Income | ~38 |
| Forex / FX | ~32 |
| Commodities | ~42 |
| Real Estate | ~55 |
| Macro & Economics | ~38 |
| Derivatives | ~32 |
| Private Markets | ~24 |
| Alternative Assets | ~18 |
| ESG & Impact | ~32 |
| Corporate Finance | ~26 |
| Banking & Credit | ~28 |
| Insurance | ~24 |
| Personal Finance | ~28 |
| Crypto/DeFi (existing) | ~184 |
| **TOTAL** | **~653 tools** |
