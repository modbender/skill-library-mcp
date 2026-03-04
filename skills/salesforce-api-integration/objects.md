# Standard Objects - Salesforce API

## Account

Company or organization.

**Key Fields:**
| Field | Type | Description |
|-------|------|-------------|
| Id | ID | Unique identifier |
| Name | String | Account name (required) |
| Industry | Picklist | Industry type |
| Website | URL | Company website |
| Phone | Phone | Main phone |
| BillingCity | String | Billing address city |
| OwnerId | Reference | Record owner |
| ParentId | Reference | Parent account |

```bash
# Get account
curl "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Account/001xxx" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"

# Create account
curl -X POST "$SF_INSTANCE_URL/services/data/v59.0/sobjects/Account" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"Name": "Acme Corp", "Industry": "Technology"}'
```

## Contact

Individual person associated with an Account.

**Key Fields:**
| Field | Type | Description |
|-------|------|-------------|
| Id | ID | Unique identifier |
| FirstName | String | First name |
| LastName | String | Last name (required) |
| Email | Email | Email address |
| Phone | Phone | Phone number |
| AccountId | Reference | Parent account |
| Title | String | Job title |
| OwnerId | Reference | Record owner |

```bash
# Get contacts for account
curl "$SF_INSTANCE_URL/services/data/v59.0/query/?q=SELECT+Id,FirstName,LastName,Email+FROM+Contact+WHERE+AccountId='001xxx'" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Opportunity

Sales deal or potential revenue.

**Key Fields:**
| Field | Type | Description |
|-------|------|-------------|
| Id | ID | Unique identifier |
| Name | String | Opportunity name (required) |
| AccountId | Reference | Related account |
| Amount | Currency | Deal value |
| StageName | Picklist | Sales stage (required) |
| CloseDate | Date | Expected close (required) |
| Probability | Percent | Win probability |
| IsClosed | Boolean | Is closed (won or lost) |
| IsWon | Boolean | Is closed-won |

**Common Stages:**
- Prospecting
- Qualification
- Needs Analysis
- Proposal
- Negotiation
- Closed Won
- Closed Lost

```bash
# Open opportunities over $10k
curl "$SF_INSTANCE_URL/services/data/v59.0/query/?q=SELECT+Id,Name,Amount,StageName+FROM+Opportunity+WHERE+IsClosed=false+AND+Amount>10000" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Lead

Potential customer not yet converted.

**Key Fields:**
| Field | Type | Description |
|-------|------|-------------|
| Id | ID | Unique identifier |
| FirstName | String | First name |
| LastName | String | Last name (required) |
| Company | String | Company name (required) |
| Email | Email | Email address |
| Status | Picklist | Lead status |
| IsConverted | Boolean | Has been converted |
| ConvertedAccountId | Reference | Converted account |
| ConvertedContactId | Reference | Converted contact |

**Common Statuses:**
- Open - Not Contacted
- Working - Contacted
- Closed - Converted
- Closed - Not Converted

```bash
# Unconverted leads
curl "$SF_INSTANCE_URL/services/data/v59.0/query/?q=SELECT+Id,Name,Company,Email,Status+FROM+Lead+WHERE+IsConverted=false" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Case

Customer support issue.

**Key Fields:**
| Field | Type | Description |
|-------|------|-------------|
| Id | ID | Unique identifier |
| CaseNumber | String | Auto-generated number |
| Subject | String | Case subject |
| Description | TextArea | Case details |
| Status | Picklist | Case status |
| Priority | Picklist | Priority level |
| AccountId | Reference | Related account |
| ContactId | Reference | Related contact |
| IsClosed | Boolean | Is resolved |

**Common Statuses:**
- New
- Working
- Escalated
- Closed

```bash
# Open high-priority cases
curl "$SF_INSTANCE_URL/services/data/v59.0/query/?q=SELECT+Id,CaseNumber,Subject,Priority+FROM+Case+WHERE+IsClosed=false+AND+Priority='High'" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Task

Activity to be completed.

**Key Fields:**
| Field | Type | Description |
|-------|------|-------------|
| Id | ID | Unique identifier |
| Subject | String | Task subject |
| Status | Picklist | Task status |
| Priority | Picklist | Priority |
| ActivityDate | Date | Due date |
| WhoId | Reference | Contact/Lead |
| WhatId | Reference | Account/Opportunity |
| IsClosed | Boolean | Is completed |

## Event

Calendar event or meeting.

**Key Fields:**
| Field | Type | Description |
|-------|------|-------------|
| Id | ID | Unique identifier |
| Subject | String | Event subject |
| StartDateTime | DateTime | Start time |
| EndDateTime | DateTime | End time |
| WhoId | Reference | Contact/Lead |
| WhatId | Reference | Account/Opportunity |

## Custom Objects

Custom objects end in `__c`:

```bash
# List all objects (includes custom)
curl "$SF_INSTANCE_URL/services/data/v59.0/sobjects/" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"

# Describe custom object
curl "$SF_INSTANCE_URL/services/data/v59.0/sobjects/MyObject__c/describe" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```
