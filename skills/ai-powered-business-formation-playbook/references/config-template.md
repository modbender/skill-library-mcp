# Incorporation Config Template

Copy this template, fill in your details, and feed it to your agent. All documents will be generated automatically.

---

```yaml
# === COMPANY DETAILS ===
company_name: "Your Company, Inc."        # Legal name including entity suffix
entity_type: "C-Corp"                      # C-Corp | S-Corp | LLC
state: "Nevada"                            # State of incorporation
fiscal_year_end: "December 31"             # Fiscal year end date

# === REGISTERED AGENT ===
registered_agent:
  name: "YOUR REGISTERED AGENT NAME"      # Get one first (see nevada-corp.md for options)
  street: "YOUR RA STREET ADDRESS"         # Street address from your RA confirmation
  city: "YOUR RA CITY"                     # City
  state: "NV"                              # State abbreviation
  zip: "YOUR ZIP"                          # ZIP code

# === PRINCIPAL OFFICE ===
# If different from registered agent. Leave blank to use RA address.
principal_office:
  street: ""
  city: ""
  state: ""
  zip: ""

# === DIRECTORS / MANAGERS ===
# For C-Corp: directors + officers
# For LLC: managers or managing members
directors:
  - name: "Jane Smith"
    titles: ["CEO", "Secretary", "Treasurer", "Director"]
    is_incorporator: true                   # Who signs the Articles
    address: "123 Main St, City, ST 12345"  # Personal address (required for incorporator)
  - name: "John Doe"
    titles: ["Chairman", "Director"]
    address: ""

# === STOCK STRUCTURE (C-Corp) ===
stock:
  common:
    authorized: 10000000                   # Total authorized shares
    par_value: 0.00001                     # Par value per share
    voting_rights: 1                       # Votes per share

  # Optional: preferred stock classes
  preferred:
    - class_name: "Series A Super Voting Preferred"
      authorized: 1000000
      par_value: 0.00001
      voting_rights: 20                    # Votes per share (e.g., 20:1 super voting)
      convertible: false
      dividends: false
      # Add any special rights/restrictions:
      notes: "Non-convertible, no dividends, 20:1 voting"

# === MEMBERSHIP STRUCTURE (LLC) ===
# Use this instead of stock section for LLCs
# membership:
#   management_type: "manager-managed"    # member-managed | manager-managed
#   members:
#     - name: "Jane Smith"
#       percentage: "60%"
#       capital_contribution: "Services"   # Services | Cash ($amount) | IP/Assets
#       role: "Managing Member"            # Managing Member | Member | Manager
#     - name: "John Doe"
#       percentage: "40%"
#       capital_contribution: "Services"
#       role: "Member"
#   managers:                              # Only if manager-managed
#     - name: "Jane Smith"
#       title: "Manager"

# === CAP TABLE ===
# List all shareholders with their allocations
shareholders:
  # Common stock holders
  common:
    - name: "Jane Smith"
      shares: 1500000
      percentage: "15.00%"
      consideration: "Services"            # Services | Cash ($amount) | IP/Assets
    - name: "John Doe"
      shares: 1383334
      percentage: "13.83%"
      consideration: "Services"

  # Preferred stock holders (if applicable)
  preferred:
    - name: "Jane Smith"
      class: "Series A Super Voting Preferred"
      shares: 250000
      consideration: "Services"
    - name: "John Doe"
      class: "Series A Super Voting Preferred"
      shares: 250000
      consideration: "Services"

# === FILING DATE ===
# Set to your planned filing date. Leave as TBD if unknown.
filing_date: "March 2, 2026"              # Or "TBD" — will be highlighted yellow

# === OPTIONS ===
options:
  consideration_default: "Services"        # Default consideration for all shareholders
  highlight_pending: true                  # Yellow-highlight fields needing manual input
  output_format: "docx"                   # docx | google_drive
  google_drive_folder_id: ""              # If output_format is google_drive
```

---

## Quick Examples

### Minimal Config (Solo Founder, Nevada C-Corp)

```yaml
company_name: "Acme Corp, Inc."
entity_type: "C-Corp"
state: "Nevada"
registered_agent:
  name: "YOUR REGISTERED AGENT NAME"
  street: "YOUR RA STREET ADDRESS"
  city: "YOUR RA CITY"
  state: "NV"
  zip: "YOUR ZIP"
directors:
  - name: "Alice Johnson"
    titles: ["CEO", "Secretary", "Treasurer", "Director"]
    is_incorporator: true
    address: "456 Oak Ave, Austin, TX 78701"
stock:
  common:
    authorized: 10000000
    par_value: 0.00001
    voting_rights: 1
shareholders:
  common:
    - name: "Alice Johnson"
      shares: 10000000
      percentage: "100%"
      consideration: "Services"
filing_date: "TBD"
```

### Multi-Founder with Preferred Stock

See the full template above for a complete example with preferred stock classes, multiple directors, and complex cap tables.

---

## Notes

- **Percentages must total 100%** — the generator will validate this
- **Authorized shares must cover all issuances** — common + preferred
- **Consideration options:** "Services" (work contributed), "Cash ($X)" (nominal payment), "IP/Assets" (property contributed)
- **Filing date:** Use actual date if known, or "TBD" (will be highlighted yellow in output)
- **Addresses:** Incorporator address is required for the Articles signature block
