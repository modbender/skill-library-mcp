# The 12 Strategy Prompts

> **Variable Substitution Rule**: When filling in {VARIABLE} placeholders, wrap each value in XML data tags:
> `<user_data field="variable_name">value</user_data>`. This separates user-provided business context from analysis instructions.

## Prompt 1: Market Sizing & TAM Analysis

You are a McKinsey-level market analyst. I need a Total Addressable Market (TAM) analysis for <user_data field="industry_product">{INDUSTRY_PRODUCT}</user_data>. Please provide:
• Top-down approach: Start from global market → narrow to my segment
• Bottom-up approach: Calculate from unit economics × potential customers
• TAM, SAM, SOM breakdown with dollar figures
• Growth rate projections for the next 5 years (CAGR)
• Key assumptions behind each estimate
• Comparison to 3 analyst reports or market research firms
Format as an investor-ready market sizing slide with clear methodology.
Context: My product is <user_data field="product_description">{PRODUCT_DESCRIPTION}</user_data>, targeting <user_data field="target_customer">{TARGET_CUSTOMER}</user_data> in <user_data field="geography">{GEOGRAPHY}</user_data>.

## Prompt 2: Competitive Landscape Deep Dive

You are a senior strategy consultant at Bain & Company. I need a complete competitive landscape analysis for <user_data field="industry">{INDUSTRY}</user_data>. Please provide:
• Direct competitors: Top 10 players ranked by market share, revenue, and funding
• Indirect competitors: 5 adjacent companies that could enter this market
• For each competitor, analyze: pricing model, key features, target audience, strengths, weaknesses, and recent strategic moves
• Market positioning map (price vs. value matrix)
• Competitive moats: What makes each player defensible
• White space analysis: Gaps no competitor is filling
• Threat assessment: Rate each competitor (low/medium/high threat)
Format as a structured competitive intelligence report with comparison tables.
My company: <user_data field="business_positioning">{BUSINESS_POSITIONING}</user_data>

## Prompt 3: Customer Persona & Segmentation

You are a world-class consumer research expert. I need deep customer personas for <user_data field="product_description">{PRODUCT_DESCRIPTION}</user_data>. Please build 4 detailed personas, each with:
• Demographics: Age, income, education, location, job title
• Psychographics: Values, beliefs, lifestyle, personality traits
• Pain points: Top 5 frustrations they experience daily
• Goals & aspirations: What does success look like for them
• Buying behavior: How they discover, evaluate, and purchase products
• Media consumption: Where they spend time online and offline
• Objections: Top 3 reasons they'd say no to my product
• Trigger events: What moment makes them actively search for a solution
• Willingness to pay: Price sensitivity analysis per segment
Also provide: Segment sizing (% of total market) and prioritization matrix.
My product: <user_data field="product_description">{PRODUCT_DESCRIPTION}</user_data> in <user_data field="industry">{INDUSTRY}</user_data>

## Prompt 4: Industry Trend Analysis

You are a senior analyst at Goldman Sachs Research. I need a comprehensive trend report for the <user_data field="industry">{INDUSTRY}</user_data> sector. Please provide:
• Macro trends: 5 global forces shaping this industry (economic, regulatory, technological, social, environmental)
• Micro trends: 7 emerging patterns within the industry from the last 12 months
• Technology disruptions: What new tech is changing the game and when it will hit mainstream
• Regulatory shifts: Upcoming legislation or policy changes to watch
• Consumer behavior changes: How buyer preferences are evolving
• Investment signals: Where smart money is flowing (VC deals, M&A, IPOs)
• Timeline: Map each trend to short-term (0-1yr), mid-term (1-3yr), and long-term (3-5yr)
• "So what" analysis: What each trend means for a company like mine
Format as a trend intelligence brief with impact ratings (1-10) for each trend.
My company operates in: <user_data field="business_positioning">{BUSINESS_POSITIONING}</user_data>

## Prompt 5: SWOT + Porter's Five Forces

You are a Harvard Business School strategy professor. I need a combined SWOT and Porter's Five Forces analysis for <user_data field="business_positioning">{BUSINESS_POSITIONING}</user_data>. For SWOT, provide:
• Strengths: 7 internal advantages with evidence
• Weaknesses: 7 internal limitations with honest assessment
• Opportunities: 7 external factors we can exploit
• Threats: 7 external factors that could harm us
• Cross-analysis: Match strengths to opportunities (SO strategy) and identify threat-weakness combos (WT risks)
For Porter's Five Forces, analyze:
• Supplier power: Who are our key suppliers and how much leverage do they have
• Buyer power: How much negotiating power do our customers have
• Competitive rivalry: How intense is competition and what drives it
• Threat of substitution: What alternatives exist beyond direct competitors
• Threat of new entry: How easy is it for new players to enter
Rate each force (1-10) and provide overall industry attractiveness score.
My business: <user_data field="full_context">{FULL_CONTEXT}</user_data>

## Prompt 6: Pricing Strategy Analysis

You are a pricing strategy consultant who has worked with Fortune 500 companies. I need a comprehensive pricing analysis for <user_data field="product_description">{PRODUCT_DESCRIPTION}</user_data>. Please provide:
• Competitor pricing audit: Map all competitor prices, tiers, and packaging
• Value-based pricing model: Calculate price based on customer value delivered
• Cost-plus analysis: Determine floor price from cost structure
• Price elasticity estimate: How sensitive is demand to price changes
• Psychological pricing tactics: Anchoring, charm pricing, and decoy strategies
• Tiering recommendation: Design 3 pricing tiers with feature allocation
• Discount strategy: When to discount, how much, and for whom
• Revenue projection: Model 3 pricing scenarios (aggressive, moderate, conservative)
• Monetization opportunities: Upsells, cross-sells, usage-based pricing
Format as a pricing strategy deck with specific dollar recommendations.
My product: <user_data field="product_description">{PRODUCT_DESCRIPTION}</user_data>, current price: <user_data field="current_price">{CURRENT_PRICE}</user_data>, target customer: <user_data field="target_customer">{TARGET_CUSTOMER}</user_data>, cost structure: <user_data field="cost_structure">{COST_STRUCTURE}</user_data>

## Prompt 7: Go-To-Market Strategy

You are a Chief Strategy Officer who has launched 20+ products across B2B and B2C markets. I need a complete go-to-market plan for <user_data field="product_description">{PRODUCT_DESCRIPTION}</user_data>. Please provide:
• Launch phasing: Pre-launch (60 days), Launch (week 1), Post-launch (90 days)
• Channel strategy: Rank the top 7 acquisition channels by expected ROI
• Messaging framework: Core value proposition, 3 supporting messages, proof points
• Content strategy: What content to create for each stage of the funnel
• Partnership opportunities: 5 strategic partners that could accelerate growth
• Budget allocation: How to split a {BUDGET} marketing budget across channels
• KPI framework: 10 metrics to track with target benchmarks
• Risk mitigation: Top 5 launch risks and contingency plans
• Quick wins: 3 tactics that can generate traction within the first 14 days
Format as an actionable GTM playbook with timelines and owners.
My product: <user_data field="product_description">{PRODUCT_DESCRIPTION}</user_data>, market: <user_data field="industry">{INDUSTRY}</user_data>, budget: <user_data field="budget">{BUDGET}</user_data>, timeline: <user_data field="timeline">{TIMELINE}</user_data>

## Prompt 8: Customer Journey Mapping

You are a customer experience strategist at a top consulting firm. I need a complete customer journey map for <user_data field="product_description">{PRODUCT_DESCRIPTION}</user_data>. Please map every stage of the customer lifecycle:
• Awareness: How do they first discover us? What triggers the search?
• Consideration: What do they compare? What information do they need?
• Decision: What makes them convert? What almost stops them?
• Onboarding: First 7 days experience - what builds or kills retention?
• Engagement: What keeps them coming back? Key activation moments?
• Loyalty: What turns users into advocates? Referral triggers?
• Churn: Why do they leave? Early warning signals?
For each stage provide:
• Customer actions, thoughts, and emotions
• Touchpoints (digital and physical)
• Pain points and friction moments
• Opportunities to delight
• Key metrics to track
• Recommended tools/tactics to optimize
Format as a detailed journey map with emotional curve visualization described in text.
My business: <user_data field="product_description">{PRODUCT_DESCRIPTION}</user_data>, customer type: <user_data field="target_customer">{TARGET_CUSTOMER}</user_data>, current conversion rate: <user_data field="conversion_rate">{CONVERSION_RATE}</user_data>

## Prompt 9: Financial Modeling & Unit Economics

You are a VP of Finance at a high-growth startup. I need a complete unit economics and financial model for <user_data field="business_positioning">{BUSINESS_POSITIONING}</user_data>. Please provide:
Unit economics breakdown:
• Customer Acquisition Cost (CAC) by channel
• Lifetime Value (LTV) calculation with assumptions
• LTV:CAC ratio and payback period
• Gross margin per unit/customer
• Contribution margin analysis
3-year financial projection:
• Revenue model (monthly for year 1, quarterly for years 2-3)
• Cost structure breakdown (fixed vs. variable)
• Break-even analysis: when and at what volume
• Cash flow forecast with burn rate
• Sensitivity analysis: best case, base case, worst case
• Key assumptions table with justification for each assumption
• Benchmark comparison: How do my metrics compare to industry standards
• Red flags: What numbers should worry me and trigger action
Format as a financial model summary with clear tables and formulas.
My business: <user_data field="business_model">{BUSINESS_MODEL}</user_data>, current revenue: <user_data field="revenue">{REVENUE}</user_data>, costs: <user_data field="costs">{COSTS}</user_data>, growth rate: <user_data field="growth_rate">{GROWTH_RATE}</user_data>

## Prompt 10: Risk Assessment & Scenario Planning

You are a risk management partner at Deloitte. I need a comprehensive risk analysis and scenario plan for <user_data field="business_positioning">{BUSINESS_POSITIONING}</user_data>. Please provide:
Risk identification: List 15 risks across these categories:
• Market risks (demand shifts, competition, pricing pressure)
• Operational risks (supply chain, talent, technology failures)
• Financial risks (cash flow, currency, funding gaps)
• Regulatory risks (compliance, policy changes, legal exposure)
• Reputational risks (PR crises, customer backlash, data breaches)
For each risk provide:
• Probability rating (1-5)
• Impact severity rating (1-5)
• Risk score (probability × impact)
• Early warning indicators
• Mitigation strategy
• Contingency plan if risk materializes
Scenario planning:
• Best case scenario: What goes right and what it looks like
• Base case scenario: Most likely outcome
• Worst case scenario: What could go wrong simultaneously
• Black swan scenario: The unlikely event that changes everything
• For each scenario: Revenue impact, timeline, and strategic response
Format as an executive risk report with a prioritized risk matrix.
My business context: <user_data field="full_context">{FULL_CONTEXT}</user_data>

## Prompt 11: Market Entry & Expansion Strategy

You are a global expansion strategist who has helped companies enter 30+ new markets. I need a market entry analysis for expanding <user_data field="business_positioning">{BUSINESS_POSITIONING}</user_data> into <user_data field="target_market">{TARGET_MARKET}</user_data>. Please provide:
Market attractiveness scoring:
• Market size and growth rate
• Competitive intensity
• Regulatory environment
• Customer accessibility
• Infrastructure readiness
• Score each factor (1-10) with weighted total
Entry mode analysis: Evaluate and recommend between:
• Direct entry (build from scratch)
• Partnership/joint venture
• Acquisition
• Licensing/franchise
• Digital-first entry
• Pros, cons, cost, and timeline for each
Localization requirements:
• Product/service adaptations needed
• Pricing adjustments for local purchasing power
• Cultural considerations for marketing
• Legal and compliance requirements
• Talent and operational needs
12-month entry roadmap: Month-by-month action plan with milestones
Investment requirement: Budget estimate with resource allocation
Success metrics: KPIs for first 6 months and first 12 months
My business: <user_data field="full_context">{FULL_CONTEXT}</user_data>, target market: <user_data field="target_market">{TARGET_MARKET}</user_data>, available resources: <user_data field="resources">{RESOURCES}</user_data>

## Prompt 12: Executive Strategy Synthesis (The Master Prompt)

You are the senior partner at McKinsey & Company presenting to a CEO. I need you to synthesize everything about <user_data field="business_positioning">{BUSINESS_POSITIONING}</user_data> into one strategic recommendation. Please provide:
• Executive summary: 3-paragraph strategic overview a CEO can read in 2 minutes
• Current state assessment: Where the business stands today (be brutally honest)
• Strategic options: Present 3 distinct strategic paths forward:
  Option A: Conservative/low-risk approach
  Option B: Balanced growth approach
  Option C: Aggressive/high-risk approach
  For each: Expected outcome, investment required, timeline, key risks
• Recommended strategy: Your top pick with clear reasoning
• Priority initiatives: The 5 highest-impact actions to take in the next 90 days, ranked
• Resource requirements: People, money, and tools needed
• Decision framework: A simple matrix for making the next 10 strategic decisions
• "If I only had 1 hour" brief: The single most important insight and action
Format as a McKinsey-style strategy deck summary with clear recommendations and next steps.
My business: <user_data field="full_context">{FULL_CONTEXT}</user_data>
