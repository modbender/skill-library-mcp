# Discover Hottest Debatable Topic for Prediction Market

Scans recent X posts for the most debated/hot topic right now in a given category (e.g., crypto, tech, sports, politics, gaming, pop culture, entertainment, music). 

Picks the top one based on engagement/controversy in last 24-48 hours, then turns it into a clean yes/no prediction market question with:
- Clear question (e.g., "Will [event] happen by [date]?")
- Short duration (1-14 days)
- Unambiguous resolution criteria (e.g., "Resolved yes if confirmed by official sources like [list]")
- Hotness score (8-10/10)
- Short reasoning why it's debatable/hot
- 2-4 source links (from X or web)

Uses X search tools to find trends, LLM to analyze/format.

Inputs:
- category (string): The category to scan, e.g., "crypto" or "politics". Default: "crypto"

Outputs:
- market_proposal (JSON): Object with keys: question (str), duration_days (int), resolution_criteria (str), score (float), reasoning (str), sources (list of str)
