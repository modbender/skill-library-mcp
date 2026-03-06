# Verticals

Verticals are forks of biz-in-a-box tailored to specific industries. They extend the base protocol with domain-specific labels, account codes, and entity fields — without breaking base validation.

## pm-in-a-box (Property Management)

The first official vertical. One repo = one property management company or rental unit.

### Extended entity.yaml fields
```yaml
meta:
  units: 42              # number of units under management
  property_type: residential|commercial|mixed
  jurisdiction: TX
  software: appfolio|yardi|buildium|other
```

### Additional labels
| Label | Use |
|-------|-----|
| `rent-payment` | tenant rent receipt |
| `maintenance` | maintenance/repair expense |
| `vacancy` | vacancy period event |
| `lease-start` | new lease begins |
| `lease-end` | lease terminates |
| `security-deposit` | deposit received or returned |
| `owner-distribution` | distribution to property owner |
| `management-fee` | PM company fee |

### Additional accounts
```yaml
revenue:
  4300-mgmt-fees: "Property management fees"
  4400-late-fees: "Late fees"
  4500-pet-fees: "Pet fees"

liabilities:
  2300-security-deposits: "Tenant security deposits held"

expenses:
  5700-maintenance: "Maintenance and repairs"
  5800-vacancy-costs: "Vacancy and turnover costs"
  5900-insurance: "Property insurance"
```

### Example entries

**Rent received:**
```json
{"id":"01HXYZ...","time":"2026-03-01T00:00:00Z","labels":["financial","rent-payment"],"description":"Unit 101 — March rent","tenant":"T-101","unit":"101","debits":[{"account":"1010-bank-checking","amount":1500}],"credits":[{"account":"4000-revenue","amount":1500}]}
```

**Maintenance expense:**
```json
{"id":"01HABC...","time":"2026-03-05T14:00:00Z","labels":["financial","maintenance"],"description":"HVAC repair Unit 203","vendor":"CoolAir LLC","unit":"203","debits":[{"account":"5700-maintenance","amount":350}],"credits":[{"account":"1010-bank-checking","amount":350}]}
```

## Creating a New Vertical

1. Fork biz-in-a-box: `git clone https://github.com/taylorhou/biz-in-a-box my-vertical-in-a-box`
2. Create `verticals/<name>/SPEC.md` defining extended labels, accounts, entity fields
3. Extend `accounts.yaml` with vertical-specific codes
4. Add vertical labels to `labels.yaml`
5. Update `FORK.md` to describe the vertical
6. Submit a PR or publish as a separate repo

See `FORK.md` in the base repo for forking guidelines.
