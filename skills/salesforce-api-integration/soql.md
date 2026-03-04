# SOQL Queries - Salesforce API

## Basic Query

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/query/?q=SELECT+Id,Name+FROM+Account+LIMIT+10" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Query with URL Encoding

For complex queries, URL-encode the SOQL:

```bash
QUERY="SELECT Id, Name, Email FROM Contact WHERE AccountId = '001xx000003DGbYAAW'"
curl "$SF_INSTANCE_URL/services/data/v59.0/query/?q=$(echo $QUERY | jq -sRr @uri)" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Common SOQL Patterns

### SELECT with WHERE

```sql
SELECT Id, Name, Industry FROM Account WHERE Industry = 'Technology'
SELECT Id, Name, Amount FROM Opportunity WHERE Amount > 10000
SELECT Id, Name FROM Lead WHERE Status = 'Open - Not Contacted'
```

### Date Filters

```sql
-- Date literals
SELECT Id, Name FROM Lead WHERE CreatedDate = TODAY
SELECT Id, Name FROM Lead WHERE CreatedDate = LAST_WEEK
SELECT Id, Name FROM Lead WHERE CreatedDate = LAST_N_DAYS:30
SELECT Id, Name FROM Lead WHERE CreatedDate = THIS_QUARTER

-- Date comparison
SELECT Id, Name FROM Opportunity WHERE CloseDate > 2024-01-01
SELECT Id, Name FROM Opportunity WHERE CloseDate = 2024-06-15
```

### Text Search (LIKE)

```sql
SELECT Id, Name FROM Account WHERE Name LIKE '%Acme%'
SELECT Id, Name FROM Contact WHERE Email LIKE '%@gmail.com'
SELECT Id, Name FROM Account WHERE Name LIKE 'A%'  -- starts with A
```

### Relationship Queries

```sql
-- Child-to-parent (dot notation)
SELECT Id, Name, Account.Name, Account.Industry FROM Contact

-- Parent-to-child (subquery)
SELECT Id, Name, (SELECT Id, LastName FROM Contacts) FROM Account

-- Multi-level
SELECT Id, Name, Account.Owner.Name FROM Contact
```

### Aggregate Functions

```sql
SELECT COUNT() FROM Account
SELECT COUNT(Id), Industry FROM Account GROUP BY Industry
SELECT StageName, SUM(Amount), AVG(Amount) FROM Opportunity GROUP BY StageName
SELECT AccountId, COUNT(Id) FROM Contact GROUP BY AccountId HAVING COUNT(Id) > 5
```

### ORDER BY and LIMIT

```sql
SELECT Id, Name, Amount FROM Opportunity ORDER BY Amount DESC LIMIT 20
SELECT Id, Name FROM Account ORDER BY CreatedDate DESC NULLS LAST
SELECT Id, Name FROM Contact ORDER BY LastName ASC, FirstName ASC
```

### NULL Handling

```sql
SELECT Id, Name FROM Account WHERE Website != null
SELECT Id, Name FROM Contact WHERE Email = null
```

### IN and NOT IN

```sql
SELECT Id, Name FROM Account WHERE Industry IN ('Technology', 'Finance', 'Healthcare')
SELECT Id, Name FROM Lead WHERE Status NOT IN ('Closed - Converted', 'Closed - Not Converted')
```

### Subqueries (Semi-Joins)

```sql
-- Accounts that have contacts
SELECT Id, Name FROM Account WHERE Id IN (SELECT AccountId FROM Contact)

-- Accounts that have opportunities
SELECT Id, Name FROM Account WHERE Id IN (SELECT AccountId FROM Opportunity WHERE Amount > 50000)
```

## SOSL Search

For text search across multiple objects:

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/search/?q=FIND+{John}+IN+ALL+FIELDS+RETURNING+Contact,Lead" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

### SOSL Patterns

```sql
FIND {John} IN ALL FIELDS RETURNING Contact(Id, Name), Lead(Id, Name)
FIND {Acme*} IN NAME FIELDS RETURNING Account(Id, Name, Industry)
FIND {"John Smith"} IN ALL FIELDS RETURNING Contact, Lead, Account
FIND {415*} IN PHONE FIELDS RETURNING Contact, Lead
```

## Pagination

For results over 2000 records:

```bash
# Initial query returns nextRecordsUrl
curl "$SF_INSTANCE_URL/services/data/v59.0/query/?q=SELECT+Id,Name+FROM+Account" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"

# Response includes:
# "nextRecordsUrl": "/services/data/v59.0/query/01gxx000000MYzz-2000"

# Fetch next batch
curl "$SF_INSTANCE_URL/services/data/v59.0/query/01gxx000000MYzz-2000" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Query All (Include Deleted)

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/queryAll/?q=SELECT+Id,Name+FROM+Account" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Describe Query

Get metadata about query results:

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/query/?q=SELECT+Id,Name+FROM+Account&explain=true" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```
