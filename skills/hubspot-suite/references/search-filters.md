# HubSpot Search Operators & Filter Syntax

Complete guide to advanced searching and filtering across all CRM objects.

## Basic Search Structure

```bash
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {
        "propertyName": "email",
        "operator": "CONTAINS_TOKEN", 
        "value": "gmail"
      }
    ],
    "sorts": [{"propertyName": "createdate", "direction": "DESCENDING"}],
    "properties": ["firstname", "lastname", "email"],
    "limit": 100,
    "after": "12345"
  }'
```

## Search Operators

### Equality Operators

#### EQ (Equals)
```bash
# Exact match
{
  "propertyName": "lifecyclestage",
  "operator": "EQ",
  "value": "customer"
}

# Example: Find all customers
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "lifecyclestage",
      "operator": "EQ",
      "value": "customer"
    }]
  }'
```

#### NEQ (Not Equals)
```bash
# Exclude specific values
{
  "propertyName": "hs_lead_status", 
  "operator": "NEQ",
  "value": "unqualified"
}

# Example: All qualified leads
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "hs_lead_status",
      "operator": "NEQ", 
      "value": "unqualified"
    }]
  }'
```

### Comparison Operators

#### LT, LTE, GT, GTE (Numeric/Date Comparisons)
```bash
# Companies with > 100 employees
{
  "propertyName": "numberofemployees",
  "operator": "GT",
  "value": "100"
}

# Deals created in last 30 days
{
  "propertyName": "createdate",
  "operator": "GTE", 
  "value": "2024-01-15T00:00:00.000Z"
}

# High value deals (>$50K)
{
  "propertyName": "amount",
  "operator": "GTE",
  "value": "50000"
}
```

#### BETWEEN (Range)
```bash
# Revenue range
{
  "propertyName": "annualrevenue",
  "operator": "BETWEEN",
  "value": "1000000",
  "highValue": "10000000"  
}

# Date range
{
  "propertyName": "closedate",
  "operator": "BETWEEN",
  "value": "2024-01-01",
  "highValue": "2024-03-31"
}

# Example: Q1 closed deals
curl -X POST "https://api.hubapi.com/crm/v3/objects/deals/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "closedate",
      "operator": "BETWEEN", 
      "value": "2024-01-01",
      "highValue": "2024-03-31"
    }]
  }'
```

### Text Operators

#### CONTAINS_TOKEN (Word Search)
```bash
# Contains specific word (whole word match)
{
  "propertyName": "jobtitle",
  "operator": "CONTAINS_TOKEN",
  "value": "manager"
}

# Example: All managers
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "jobtitle",
      "operator": "CONTAINS_TOKEN",
      "value": "manager"  
    }]
  }'
```

#### NOT_CONTAINS_TOKEN
```bash
# Exclude specific words
{
  "propertyName": "company",
  "operator": "NOT_CONTAINS_TOKEN", 
  "value": "competitor"
}
```

### Existence Operators

#### HAS_PROPERTY (Field Has Value)
```bash
# Contacts with phone numbers
{
  "propertyName": "phone",
  "operator": "HAS_PROPERTY"
}

# Companies with revenue data
{
  "propertyName": "annualrevenue", 
  "operator": "HAS_PROPERTY"
}

# Example: Contacts with complete profiles
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {"propertyName": "phone", "operator": "HAS_PROPERTY"},
      {"propertyName": "jobtitle", "operator": "HAS_PROPERTY"},
      {"propertyName": "company", "operator": "HAS_PROPERTY"}
    ]
  }'
```

#### NOT_HAS_PROPERTY (Missing Data)
```bash
# Contacts missing email (rare, since email is usually required)
{
  "propertyName": "phone", 
  "operator": "NOT_HAS_PROPERTY"
}

# Example: Companies missing key data
curl -X POST "https://api.hubapi.com/crm/v3/objects/companies/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "industry",
      "operator": "NOT_HAS_PROPERTY"
    }],
    "properties": ["name", "domain"]
  }'
```

### List Operators

#### IN (Match Any Value)
```bash
# Multiple lifecycle stages
{
  "propertyName": "lifecyclestage",
  "operator": "IN",
  "values": ["lead", "marketingqualifiedlead", "salesqualifiedlead"]
}

# Multiple industries
{
  "propertyName": "industry",
  "operator": "IN",
  "values": ["Technology", "Software", "SaaS"]
}

# Example: Tech companies
curl -X POST "https://api.hubapi.com/crm/v3/objects/companies/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "industry",
      "operator": "IN",
      "values": ["Technology", "Software", "Computer Software", "Information Technology"]
    }]
  }'
```

#### NOT_IN (Exclude Values)
```bash
# Exclude lost/closed deals
{
  "propertyName": "dealstage",
  "operator": "NOT_IN",
  "values": ["closedwon", "closedlost"]
}

# Example: Open pipeline deals
curl -X POST "https://api.hubapi.com/crm/v3/objects/deals/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [{
      "propertyName": "dealstage", 
      "operator": "NOT_IN",
      "values": ["closedwon", "closedlost"]
    }],
    "properties": ["dealname", "amount", "dealstage", "closedate"]
  }'
```

## Advanced Filter Combinations

### AND Logic (Default)
Multiple filters are automatically AND'd together:
```bash
# Hot leads with phone numbers
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {
        "propertyName": "hs_lead_status",
        "operator": "EQ",
        "value": "open"
      },
      {
        "propertyName": "phone", 
        "operator": "HAS_PROPERTY"
      },
      {
        "propertyName": "createdate",
        "operator": "GTE",
        "value": "'$(date -u -d '7 days ago' '+%Y-%m-%d')'"
      }
    ]
  }'
```

### OR Logic with Filter Groups
```bash
# Contacts that are either customers OR have high lead score
{
  "filterGroups": [
    {
      "filters": [
        {
          "propertyName": "lifecyclestage",
          "operator": "EQ", 
          "value": "customer"
        }
      ]
    },
    {
      "filters": [
        {
          "propertyName": "hubspotscore",
          "operator": "GTE",
          "value": "80"
        }
      ]
    }
  ]
}
```

### Complex Mixed Logic
```bash
# (High value deals OR enterprise accounts) AND (created this month)
curl -X POST "https://api.hubapi.com/crm/v3/objects/deals/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filterGroups": [
      {
        "filters": [
          {
            "propertyName": "amount",
            "operator": "GTE",
            "value": "100000"
          },
          {
            "propertyName": "createdate",
            "operator": "GTE", 
            "value": "'$(date -u -d '30 days ago' '+%Y-%m-%d')'"
          }
        ]
      },
      {
        "filters": [
          {
            "propertyName": "dealtype",
            "operator": "EQ",
            "value": "enterprise"  
          },
          {
            "propertyName": "createdate",
            "operator": "GTE",
            "value": "'$(date -u -d '30 days ago' '+%Y-%m-%d')'"
          }
        ]
      }
    ]
  }'
```

## Sorting Options

### Single Sort
```bash
{
  "sorts": [
    {
      "propertyName": "createdate",
      "direction": "DESCENDING"
    }
  ]
}
```

### Multiple Sorts (Priority Order)
```bash
{
  "sorts": [
    {
      "propertyName": "hs_lead_status", 
      "direction": "ASCENDING"
    },
    {
      "propertyName": "hubspotscore",
      "direction": "DESCENDING" 
    },
    {
      "propertyName": "createdate",
      "direction": "DESCENDING"
    }
  ]
}
```

## Pagination Best Practices

### Efficient Pagination
```bash
#!/bin/bash
search_all_contacts() {
    local after=""
    local limit=100
    local filters="$1"
    
    while true; do
        local query="{
            \"filters\": $filters,
            \"properties\": [\"firstname\", \"lastname\", \"email\"],
            \"limit\": $limit"
        
        [ -n "$after" ] && query="$query, \"after\": \"$after\""
        query="$query }"
        
        response=$(curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
            -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
            -H "Content-Type: application/json" \
            -d "$query")
        
        # Process results
        echo "$response" | jq -r '.results[]'
        
        # Get next page token
        after=$(echo "$response" | jq -r '.paging.next.after // empty')
        
        [ -z "$after" ] && break
        
        # Rate limit pause
        sleep 0.1
    done
}

# Usage
search_all_contacts '[{"propertyName": "lifecyclestage", "operator": "EQ", "value": "lead"}]'
```

## Common Search Patterns

### Sales Qualified Leads
```bash
{
  "filters": [
    {
      "propertyName": "lifecyclestage",
      "operator": "EQ",
      "value": "salesqualifiedlead"
    },
    {
      "propertyName": "createdate", 
      "operator": "GTE",
      "value": "2024-01-01"
    }
  ],
  "sorts": [
    {
      "propertyName": "hubspotscore",
      "direction": "DESCENDING"
    }
  ]
}
```

### Stale Opportunities
```bash
{
  "filters": [
    {
      "propertyName": "dealstage",
      "operator": "NOT_IN",
      "values": ["closedwon", "closedlost"]
    },
    {
      "propertyName": "hs_lastmodifieddate",
      "operator": "LTE", 
      "value": "2024-01-01T00:00:00.000Z"
    }
  ]
}
```

### High-Value Prospects
```bash
{
  "filters": [
    {
      "propertyName": "lifecyclestage",
      "operator": "IN",
      "values": ["lead", "marketingqualifiedlead"]
    },
    {
      "propertyName": "annualrevenue",
      "operator": "GTE", 
      "value": "10000000"
    },
    {
      "propertyName": "numberofemployees",
      "operator": "GTE",
      "value": "1000"
    }
  ]
}
```

### Recently Engaged Contacts
```bash
{
  "filters": [
    {
      "propertyName": "notes_last_contacted",
      "operator": "GTE",
      "value": "2024-02-01T00:00:00.000Z"
    },
    {
      "propertyName": "hs_email_last_open_date", 
      "operator": "GTE",
      "value": "2024-02-01T00:00:00.000Z"
    }
  ]
}
```

## Property-Specific Tips

### Date Properties
- Use ISO 8601 format: `2024-01-15T00:00:00.000Z`
- For date-only: `2024-01-15` 
- HubSpot times are in UTC
- Use `GTE` for "on or after" date ranges

### Numeric Properties
- Values must be strings: `"50000"` not `50000`
- Use comparison operators for ranges
- Be aware of currency formatting

### Dropdown/Enum Properties
- Use exact internal values, not display labels
- Case-sensitive matching
- Use IN operator for multiple options

### Boolean Properties
- Values: `"true"` or `"false"` (strings)
- Use `HAS_PROPERTY` to check if set

## Performance Optimization

### Indexed Properties
These properties are optimized for searching:
- `createdate`, `lastmodifieddate`
- `email`, `domain`
- Standard HubSpot properties
- Custom properties with high cardinality

### Search Efficiency Tips
✅ Use specific filters rather than broad text searches  
✅ Filter by indexed properties when possible  
✅ Use BETWEEN for date ranges instead of multiple GT/LT  
✅ Limit results to what you need  
✅ Use batch operations after search  

❌ Avoid complex text searches on large datasets  
❌ Don't search without any filters  
❌ Avoid OR logic with many filter groups  

## Error Handling

### Common Search Errors
- **400**: Invalid property name or operator
- **429**: Rate limit exceeded (search API: 4 req/sec)
- **413**: Query too complex

### Validation
```bash
validate_search() {
    local property="$1"
    local operator="$2"
    local value="$3"
    
    # Check if property exists
    curl -s -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        "https://api.hubapi.com/crm/v3/properties/contacts/$property" | \
    jq -e '.name' >/dev/null || {
        echo "Property '$property' does not exist"
        return 1
    }
    
    echo "Property '$property' is valid"
}
```