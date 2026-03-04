"""
ConvoYield Premium Playbooks — Industry-specific strategy packs.

Each playbook contains battle-tested plays optimized for a specific industry.
These are the monetizable add-ons that generate recurring revenue.

Available playbooks:
    - saas_sales: 25 plays for B2B SaaS sales conversations
    - ecommerce: 22 plays for online retail optimization
    - real_estate: 20 plays for real estate lead conversion
    - healthcare: 18 plays for healthcare patient engagement
"""

from convoyield.playbooks.saas_sales import SAAS_SALES_PLAYBOOK
from convoyield.playbooks.ecommerce import ECOMMERCE_PLAYBOOK
from convoyield.playbooks.real_estate import REAL_ESTATE_PLAYBOOK
from convoyield.playbooks.healthcare import HEALTHCARE_PLAYBOOK

ALL_PLAYBOOKS = {
    "saas_sales": SAAS_SALES_PLAYBOOK,
    "ecommerce": ECOMMERCE_PLAYBOOK,
    "real_estate": REAL_ESTATE_PLAYBOOK,
    "healthcare": HEALTHCARE_PLAYBOOK,
}
