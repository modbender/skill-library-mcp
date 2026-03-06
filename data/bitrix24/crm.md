# CRM

## Deals

```bash
# List deals (with pagination)
curl -s "${BITRIX24_WEBHOOK_URL}crm.deal.list.json" \
  -d 'select[]=ID&select[]=TITLE&select[]=STAGE_ID&select[]=OPPORTUNITY&select[]=CURRENCY_ID&select[]=CONTACT_ID&select[]=COMPANY_ID' | jq .result

# Get deal by ID
curl -s "${BITRIX24_WEBHOOK_URL}crm.deal.get.json" -d 'id=123' | jq .result

# Create deal
curl -s "${BITRIX24_WEBHOOK_URL}crm.deal.add.json" \
  -d 'fields[TITLE]=New Deal&fields[STAGE_ID]=NEW&fields[OPPORTUNITY]=50000&fields[CURRENCY_ID]=RUB&fields[CONTACT_ID]=1&fields[COMPANY_ID]=1' | jq .result

# Update deal
curl -s "${BITRIX24_WEBHOOK_URL}crm.deal.update.json" \
  -d 'id=123&fields[STAGE_ID]=WON&fields[OPPORTUNITY]=75000' | jq .result

# Delete deal
curl -s "${BITRIX24_WEBHOOK_URL}crm.deal.delete.json" -d 'id=123' | jq .result

# Filter: deals in specific stage
curl -s "${BITRIX24_WEBHOOK_URL}crm.deal.list.json" \
  -d 'filter[STAGE_ID]=NEW&filter[>OPPORTUNITY]=10000&select[]=ID&select[]=TITLE&select[]=OPPORTUNITY' | jq .result

# Filter: deals created after date
curl -s "${BITRIX24_WEBHOOK_URL}crm.deal.list.json" \
  -d 'filter[>DATE_CREATE]=2026-01-01T00:00:00&select[]=ID&select[]=TITLE&select[]=DATE_CREATE' | jq .result
```

**Stage IDs (default pipeline):**
| Stage | ID |
|---|---|
| New | `NEW` |
| Preparation | `PREPARATION` |
| Invoice sent | `PREPAYMENT_INVOICE` |
| In progress | `EXECUTING` |
| Final invoice | `FINAL_INVOICE` |
| Won | `WON` |
| Lost | `LOSE` |

Custom pipelines use numeric category IDs. Get all stages:
```bash
curl -s "${BITRIX24_WEBHOOK_URL}crm.status.list.json" \
  -d 'filter[ENTITY_ID]=DEAL_STAGE' | jq .result
```

**Key fields:** TITLE, STAGE_ID, OPPORTUNITY, CURRENCY_ID, CONTACT_ID, COMPANY_ID, ASSIGNED_BY_ID, BEGINDATE, CLOSEDATE, COMMENTS, SOURCE_ID, SOURCE_DESCRIPTION, UTM_SOURCE.

## Contacts

```bash
# List contacts
curl -s "${BITRIX24_WEBHOOK_URL}crm.contact.list.json" \
  -d 'select[]=ID&select[]=NAME&select[]=LAST_NAME&select[]=PHONE&select[]=EMAIL' | jq .result

# Get contact by ID
curl -s "${BITRIX24_WEBHOOK_URL}crm.contact.get.json" -d 'id=123' | jq .result

# Create contact
curl -s "${BITRIX24_WEBHOOK_URL}crm.contact.add.json" \
  -d 'fields[NAME]=Ivan&fields[LAST_NAME]=Petrov&fields[PHONE][0][VALUE]=+79001234567&fields[PHONE][0][VALUE_TYPE]=WORK&fields[EMAIL][0][VALUE]=ivan@example.com&fields[EMAIL][0][VALUE_TYPE]=WORK' | jq .result

# Update contact
curl -s "${BITRIX24_WEBHOOK_URL}crm.contact.update.json" \
  -d 'id=123&fields[NAME]=Ivan&fields[LAST_NAME]=Sidorov' | jq .result

# Search by phone
curl -s "${BITRIX24_WEBHOOK_URL}crm.contact.list.json" \
  -d 'filter[PHONE]=+79001234567&select[]=ID&select[]=NAME&select[]=LAST_NAME' | jq .result
```

**Key fields:** NAME, LAST_NAME, SECOND_NAME, PHONE, EMAIL, WEB, COMPANY_ID, POST, ADDRESS, BIRTHDATE, ASSIGNED_BY_ID, SOURCE_ID, COMMENTS.

## Leads

```bash
# List leads
curl -s "${BITRIX24_WEBHOOK_URL}crm.lead.list.json" \
  -d 'select[]=ID&select[]=TITLE&select[]=STATUS_ID&select[]=NAME&select[]=PHONE' | jq .result

# Create lead
curl -s "${BITRIX24_WEBHOOK_URL}crm.lead.add.json" \
  -d 'fields[TITLE]=New Lead&fields[NAME]=Maria&fields[LAST_NAME]=Ivanova&fields[PHONE][0][VALUE]=+79009876543&fields[SOURCE_ID]=WEB' | jq .result

# Convert lead to deal+contact
curl -s "${BITRIX24_WEBHOOK_URL}crm.lead.update.json" \
  -d 'id=123&fields[STATUS_ID]=CONVERTED' | jq .result
```

**Lead statuses:** `NEW`, `IN_PROCESS`, `PROCESSED`, `CONVERTED`, `JUNK`.

## Companies

```bash
# List companies
curl -s "${BITRIX24_WEBHOOK_URL}crm.company.list.json" \
  -d 'select[]=ID&select[]=TITLE&select[]=COMPANY_TYPE&select[]=PHONE' | jq .result

# Create company
curl -s "${BITRIX24_WEBHOOK_URL}crm.company.add.json" \
  -d 'fields[TITLE]=Acme Corp&fields[COMPANY_TYPE]=CUSTOMER&fields[INDUSTRY]=IT&fields[PHONE][0][VALUE]=+74951234567&fields[PHONE][0][VALUE_TYPE]=WORK' | jq .result
```

**Company types:** `CUSTOMER`, `SUPPLIER`, `PARTNER`, `OTHER`.

## Activities (calls, meetings, emails)

```bash
# List activities for a deal
curl -s "${BITRIX24_WEBHOOK_URL}crm.activity.list.json" \
  -d 'filter[OWNER_TYPE_ID]=2&filter[OWNER_ID]=123&select[]=ID&select[]=SUBJECT&select[]=TYPE_ID&select[]=COMPLETED' | jq .result

# Create activity (meeting)
curl -s "${BITRIX24_WEBHOOK_URL}crm.activity.add.json" \
  -d 'fields[OWNER_TYPE_ID]=2&fields[OWNER_ID]=123&fields[TYPE_ID]=2&fields[SUBJECT]=Meeting&fields[START_TIME]=2026-03-01T10:00:00&fields[END_TIME]=2026-03-01T11:00:00&fields[RESPONSIBLE_ID]=1' | jq .result

# Complete activity
curl -s "${BITRIX24_WEBHOOK_URL}crm.activity.update.json" \
  -d 'id=456&fields[COMPLETED]=Y' | jq .result
```

**OWNER_TYPE_ID:** `1` = Lead, `2` = Deal, `3` = Contact, `4` = Company.
**TYPE_ID:** `1` = Email, `2` = Meeting, `3` = Call, `6` = Task.

## More Methods (MCP)

This file covers common CRM methods. For additional methods or updated parameters, use MCP:
- `bitrix-search "crm deal"` — find all deal-related methods
- `bitrix-search "crm contact"` — find contact methods
- `bitrix-method-details crm.deal.add` — get full spec for any method
