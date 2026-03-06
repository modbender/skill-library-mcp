"""
Tax/VAT Article Generator for OpenClaw
Generate South African tax compliance articles
"""

import os
import json
import argparse
from datetime import datetime
from string import Template

# Article templates
ARTICLE_TEMPLATES = {
    "sars_compliance": """
# {{ARTICLE_TITLE}}

Stay ahead of SARS deadlines with automated compliance tools.

## Critical SARS Deadlines for {{YEAR}}

As the {{YEAR}} tax year progresses, South African businesses must navigate **SARS (South African Revenue Service)** deadlines. Missing these can result in significant penalties.

### Key Dates

**Provisional Tax Deadlines**
- **First Period ({{YEAR}}):** {{DEADLINE_1_DATE}}
- **Second Period ({{YEAR_P1}}):** {{DEADLINE_2_DATE}}
- **Third Period (Optional):** {{DEADLINE_3_DATE}}

Provisional taxpayers must submit **IRP6 forms** and make payments by these dates.

**Annual Income Tax Returns**
- **Individuals:** July - November {{YEAR}}
- **Companies (IT14):** Within 12 months of financial year-end
- **Trusts:** Filed via e@filing or approved software

**VAT Returns (VAT 201)**
- **Category A/B:** Every 2 months
- **Category C:** Monthly (turnover > R30 million)
- **Category D:** 6-monthly (micro-businesses)
- **Category E:** Annually

Late submissions incur penalties of **{{PENALTY_INFO}}** plus interest at **{{INTEREST_RATE}}**.

## How PayLessTax Helps

[{{CTA_TEXT}}]({{CTA_URL}})
""",
    "vat_guide": """
# VAT Compliance Guide {{YEAR}}

Understanding VAT obligations for South African businesses.

## VAT Categories Explained

1. **Category A:** Odd months (Jan, Mar, May, Jul, Sep, Nov)
2. **Category B:** Even months (Feb, Apr, Jun, Aug, Oct, Dec)
3. **Category C:** Monthly ( turnover > R30 million p.a.)
4. **Category D:** 6-monthly (turnover < R250k taxable supplies)
5. **Category E:** Annually

## Key Requirements

- Filing deadline: 25th working day after period end
- VAT 201 form via eFiling or approved software
- 15% standard rate (excludes zero-rated/exempt supplies)

*Note: {{SARS_NOTE}}*

[{{CTA_TEXT}}]({{CTA_URL}})
""",
    "paye_guide": """
# PAYE and EMP201 Compliance for {{YEAR}}

Monthly employer tax obligations explained.

## EMP201 Due Dates

- **Monthly:** 7th (or next business day) following month end
- **Payment methods:** eFiling, EFT, bank deposits
- **UIF/SDL:** Included in EMP201

## Penalties

- Late submission: {{LATE_PENALTY}}
- Late payment: {{PAYMENT_PENALTY}}
- Incorrect info: {{INCORRECT_PENALTY}}

## Best Practices

1. Monthly reconciliation
2. Employee data accuracy
3. Regular SARS profile checks
4. Early submission (avoid deadline rush)

[{{CTA_TEXT}}]({{CTA_URL}})
""",
    "provisional_tax": """
# Provisional Tax Guide {{YEAR}}

Step-by-step provisional tax compliance for taxpayers.

## Return Periods

| Period | Due Date | Purpose |
|--------|----------|---------|
| First | {{DEADLINE_1_DATE}} | First estimate of taxable income |
| Second | {{DEADLINE_2_DATE}} | Second/revised estimate |
| Third | {{DEADLINE_3_DATE}} | Top-up payment (optional) |

## IRP6 Filing

- Submit via SARS eFiling
- Estimate taxable income accurately
- Include all income sources
- Consider year-end adjustments

## Penalties

- Underestimation penalty: {{PENALTY_INFO}}
- Late submission: additional interest charges
- Non-payment: 10% immediate penalty

**Tip:** {{PRO_TIP}}
"""
}

class ArticleGenerator:
    def __init__(self, article_type):
        self.article_type = article_type
        self.template = ARTICLE_TEMPLATES.get(article_type, ARTICLE_TEMPLATES["sars_compliance"])

    def generate(self, variables):
        """Generate article from template with variables"""
        template = Template(self.template)
        content = template.safe_substitute(variables)

        return {
            "title": variables.get("ARTICLE_TITLE", "Tax Article"),
            "author": "PayLessTax Team",
            "date_generated": datetime.now().isoformat(),
            "year": variables.get("YEAR", datetime.now().year),
            "content": content.strip(),
            "article_type": self.article_type,
            "seo_metadata": {
                "keywords": [variables.get("MAIN_KEYWORD", "tax")],
                "canonical_url": variables.get("CANONICAL_URL", "")
            }
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', choices=list(ARTICLE_TEMPLATES.keys()), required=True)
    parser.add_argument('--year', default=str(datetime.now().year), help='Tax year')
    parser.add_argument('--output', default='./output')
    parser.add_argument('--title', required=True, help='Article title')
    parser.add_argument('--keyword', required=True, help='Main SEO keyword')
    parser.add_argument('--cta-text', default='Learn More')
    parser.add_argument('--cta-url', required=True, help='CTA destination URL')

    args = parser.parse_args()

    year = int(args.year)

    variables = {
        "ARTICLE_TITLE": args.title,
        "YEAR": str(year),
        "YEAR_P1": str(year + 1),
        "MAIN_KEYWORD": args.keyword,
        "DEADLINE_1_DATE": f"31 August {year}",
        "DEADLINE_2_DATE": f"28 February {year + 1}",
        "DEADLINE_3_DATE": f"30 September {year + 1}",
        "PENALTY_INFO": "10% of tax payable",
        "INTEREST_RATE": "repo rate + 4%",
        "LATE_PENALTY": "10% of tax due",
        "PAYMENT_PENALTY": "Interest at 10.25% p.a.",
        "INCORRECT_PENALTY": "Up to 200% of shortfall",
        "SARS_NOTE": "Penalties apply for late filing",
        "PRO_TIP": "Consider using automated tax software",
        "CTA_TEXT": args.cta_text,
        "CTA_URL": args.cta_url
    }

    os.makedirs(args.output, exist_ok=True)

    generator = ArticleGenerator(args.type)
    article = generator.generate(variables)

    filename = f"{args.type}_{year}_{datetime.now().strftime('%s')}.json"
    filepath = os.path.join(args.output, filename)

    with open(filepath, 'w') as f:
        json.dump(article, f, indent=2)

    print(f"Article generated: {filepath}")
