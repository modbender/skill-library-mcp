# Users & Structure

## Users

```bash
# Current authenticated user
curl -s "${BITRIX24_WEBHOOK_URL}user.current.json" | jq .result

# Get user by ID
curl -s "${BITRIX24_WEBHOOK_URL}user.get.json" -d 'ID=1' | jq '.result[0]'

# Search users by name
curl -s "${BITRIX24_WEBHOOK_URL}user.search.json" \
  -d 'FILTER[NAME]=Ivan' | jq .result

# Search by email
curl -s "${BITRIX24_WEBHOOK_URL}user.search.json" \
  -d 'FILTER[EMAIL]=ivan@example.com' | jq .result

# List all active users
curl -s "${BITRIX24_WEBHOOK_URL}user.get.json" \
  -d 'filter[ACTIVE]=true&SORT=LAST_NAME&ORDER=ASC' | jq .result

# Filter by department
curl -s "${BITRIX24_WEBHOOK_URL}user.get.json" \
  -d 'filter[UF_DEPARTMENT]=5' | jq .result
```

## Departments

```bash
# List all departments
curl -s "${BITRIX24_WEBHOOK_URL}department.get.json" | jq .result

# Get department by ID
curl -s "${BITRIX24_WEBHOOK_URL}department.get.json" -d 'ID=5' | jq .result

# Create department
curl -s "${BITRIX24_WEBHOOK_URL}department.add.json" \
  -d 'NAME=Engineering&PARENT=1&HEAD=1' | jq .result

# Update department
curl -s "${BITRIX24_WEBHOOK_URL}department.update.json" \
  -d 'ID=5&NAME=Updated Name' | jq .result

# Delete department
curl -s "${BITRIX24_WEBHOOK_URL}department.delete.json" -d 'ID=5' | jq .result
```

## Reference

**User fields:** ID, NAME, LAST_NAME, SECOND_NAME, EMAIL, PERSONAL_PHONE, WORK_PHONE, PERSONAL_PHOTO, WORK_POSITION, UF_DEPARTMENT (array of department IDs), ACTIVE, DATE_REGISTER, LAST_LOGIN.

**Department fields:** ID, NAME, SORT, PARENT (parent department ID), HEAD (head user ID), UF_HEAD.

## More Methods (MCP)

This file covers common user methods. For additional methods or updated parameters, use MCP:
- `bitrix-search "user"` — find all user-related methods
- `bitrix-search "department"` — find department methods
- `bitrix-method-details user.get` — get full spec for any method
