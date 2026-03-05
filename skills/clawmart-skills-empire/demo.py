# ClawMart Skills Empire - Demo
# Shows what buyers get when they purchase

print("=" * 60)
print("CLAWMART SKILLS EMPIRE - DEMO")
print("=" * 60)

print("""
WHAT YOU GET:

1. TRADING SIGNAL GENERATOR
   - Real-time XAUUSD/EURUSD scanning
   - ICT concepts (Order Blocks, FVGs, OTE)
   - Entry/Exit/SL recommendations
   - Telegram/Discord alerts
   
2. CONTENT AUTOMATION ENGINE
   - Auto-generates tweets/posts
   - Blog article writer
   - Newsletter creator
   - SEO optimizer
   
3. LEAD GENERATION PRO
   - Business lead scraper
   - Email verifier
   - Outreach message generator
   - CRM connector
   
4. DATA ANALYSIS SUITE
   - CSV/Excel analyzer
   - Chart generator
   - Trend detection
   - Report exporter
   
5. CUSTOMER SUPPORT BOT
   - FAQ handler
   - Ticket classifier
   - Response suggestions
   - Satisfaction tracker
""")

print("=" * 60)
print("PRICING TIERS")
print("=" * 60)

tiers = [
    ("STARTER", "$9", ["Basic skill template", "Standard docs", "Email support"]),
    ("PRO", "$19", ["Full features", "Priority support", "6 months updates"]),
    ("EMPIRE", "$39", ["All 5 skills", "White-label rights", "Lifetime updates"])
]

for name, price, features in tiers:
    print(f"\n{name} - {price}")
    for f in features:
        print(f"  + {f}")

print("\n" + "=" * 60)
print("HOW TO USE")
print("=" * 60)
print("""
1. Choose template from /templates folder
2. Edit config.json with your API keys
3. Customize SKILL.md with your docs
4. Deploy to ClawMart
5. Start selling!
""")

print("=" * 60)
print("READY TO DEPLOY!")
print("=" * 60)
