# HubSpot Import & Export Operations

Bulk data migration, CSV imports, and large-scale data operations.

## CSV Import via UI

### Basic Import Process
1. **Contacts → Import**
2. Upload CSV file
3. Map columns to HubSpot properties
4. Review and start import
5. Monitor import status

### Import Best Practices
- **Email column required** for contacts
- **Domain column recommended** for companies  
- Use internal property names in headers
- Format dates as `YYYY-MM-DD` or `MM/DD/YYYY`
- Keep files under 100MB
- Limit to 1,000,000 records per import

## API-Based Bulk Import

### Batch Create (Recommended)
```bash
# Import up to 100 contacts at once
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/batch/create" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "properties": {
          "email": "john@company.com",
          "firstname": "John",
          "lastname": "Doe",
          "company": "Example Corp",
          "jobtitle": "VP Sales"
        }
      },
      {
        "properties": {
          "email": "jane@company.com",
          "firstname": "Jane", 
          "lastname": "Smith",
          "company": "Example Corp",
          "jobtitle": "Marketing Director"
        }
      }
    ]
  }'
```

### Batch Create with Error Handling
```bash
#!/bin/bash
batch_create_contacts() {
    local input_file="$1"
    local batch_size=100
    local batch_num=0
    local success_count=0
    local error_count=0
    
    # Read CSV and process in batches
    tail -n +2 "$input_file" | while IFS=',' read -r email firstname lastname company jobtitle; do
        batch_data+=("{
            \"properties\": {
                \"email\": \"$email\",
                \"firstname\": \"$firstname\", 
                \"lastname\": \"$lastname\",
                \"company\": \"$company\",
                \"jobtitle\": \"$jobtitle\"
            }
        }")
        
        # Process batch when full
        if [ ${#batch_data[@]} -eq $batch_size ]; then
            process_batch
            batch_data=()
            batch_num=$((batch_num + 1))
            
            # Rate limiting pause
            sleep 1
        fi
    done
    
    # Process remaining records
    [ ${#batch_data[@]} -gt 0 ] && process_batch
    
    echo "Import complete: $success_count successful, $error_count errors"
}

process_batch() {
    local json_array=$(printf "%s," "${batch_data[@]}")
    json_array="[${json_array%,}]"
    
    response=$(curl -s -X POST "https://api.hubapi.com/crm/v3/objects/contacts/batch/create" \
        -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"inputs\": $json_array}")
    
    # Check for errors
    if echo "$response" | jq -e '.status == "error"' >/dev/null; then
        echo "Batch $batch_num failed: $(echo "$response" | jq -r '.message')"
        error_count=$((error_count + batch_size))
    else
        local created=$(echo "$response" | jq -r '.results | length')
        success_count=$((success_count + created))
        echo "Batch $batch_num: Created $created records"
    fi
}
```

## Advanced Import Patterns

### CSV to JSON Converter
```bash
#!/bin/bash
csv_to_hubspot_json() {
    local csv_file="$1"
    local object_type="$2"  # contacts, companies, deals
    
    # Read header
    local header=$(head -n 1 "$csv_file")
    IFS=',' read -ra HEADERS <<< "$header"
    
    echo "["
    
    local first=true
    tail -n +2 "$csv_file" | while IFS=',' read -ra VALUES; do
        [ "$first" = true ] && first=false || echo ","
        
        echo "  {"
        echo "    \"properties\": {"
        
        local prop_first=true
        for i in "${!HEADERS[@]}"; do
            [ "$prop_first" = true ] && prop_first=false || echo ","
            echo -n "      \"${HEADERS[i]}\": \"${VALUES[i]}\""
        done
        
        echo ""
        echo "    }"
        echo -n "  }"
    done
    
    echo ""
    echo "]"
}

# Usage
csv_to_hubspot_json contacts.csv contacts > contacts.json
```

### Import with Associations
```bash
# Import deals with company associations
curl -X POST "https://api.hubapi.com/crm/v3/objects/deals/batch/create" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "properties": {
          "dealname": "Q4 Enterprise Deal",
          "amount": "100000",
          "dealstage": "qualifiedtobuy"
        },
        "associations": [
          {
            "to": {"id": "COMPANY_ID"},
            "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 5}]
          }
        ]
      }
    ]
  }'
```

### Upsert Logic (Update or Create)
```bash
#!/bin/bash
upsert_contact() {
    local email="$1"
    local firstname="$2"
    local lastname="$3"
    
    # Try to find existing contact
    existing=$(curl -s -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
        -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"filters\": [{
                \"propertyName\": \"email\",
                \"operator\": \"EQ\", 
                \"value\": \"$email\"
            }],
            \"limit\": 1
        }")
    
    local contact_id=$(echo "$existing" | jq -r '.results[0].id // empty')
    
    if [ -n "$contact_id" ]; then
        # Update existing
        echo "Updating existing contact: $contact_id"
        curl -X PATCH "https://api.hubapi.com/crm/v3/objects/contacts/$contact_id" \
            -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{
                \"properties\": {
                    \"firstname\": \"$firstname\",
                    \"lastname\": \"$lastname\"
                }
            }"
    else
        # Create new
        echo "Creating new contact"
        curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts" \
            -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{
                \"properties\": {
                    \"email\": \"$email\",
                    \"firstname\": \"$firstname\",
                    \"lastname\": \"$lastname\"
                }
            }"
    fi
}
```

## Data Export

### Export All Contacts
```bash
#!/bin/bash
export_all_contacts() {
    local output_file="contacts_export.csv"
    local after=""
    local limit=100
    
    # CSV header
    echo "id,email,firstname,lastname,phone,company,createdate" > "$output_file"
    
    while true; do
        local url="https://api.hubapi.com/crm/v3/objects/contacts"
        url="$url?properties=email,firstname,lastname,phone,company,createdate&limit=$limit"
        [ -n "$after" ] && url="$url&after=$after"
        
        echo "Fetching batch (after: $after)" >&2
        
        response=$(curl -s -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" "$url")
        
        # Convert to CSV
        echo "$response" | jq -r '.results[] | 
            [.id, .properties.email, .properties.firstname, .properties.lastname, 
             .properties.phone, .properties.company, .properties.createdate] | 
            @csv' >> "$output_file"
        
        # Get next page
        after=$(echo "$response" | jq -r '.paging.next.after // empty')
        [ -z "$after" ] && break
        
        sleep 0.1  # Rate limiting
    done
    
    echo "Export complete: $(wc -l < "$output_file") records in $output_file"
}
```

### Export with Search Filters
```bash
#!/bin/bash
export_filtered_contacts() {
    local filter_json="$1"
    local output_file="$2"
    local after=""
    local limit=100
    
    echo "id,email,firstname,lastname,createdate" > "$output_file"
    
    while true; do
        local search_query="{
            \"filters\": $filter_json,
            \"properties\": [\"email\", \"firstname\", \"lastname\", \"createdate\"],
            \"limit\": $limit"
        
        [ -n "$after" ] && search_query="$search_query, \"after\": \"$after\""
        search_query="$search_query }"
        
        response=$(curl -s -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
            -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
            -H "Content-Type: application/json" \
            -d "$search_query")
        
        echo "$response" | jq -r '.results[] | 
            [.id, .properties.email, .properties.firstname, .properties.lastname, .properties.createdate] | 
            @csv' >> "$output_file"
        
        after=$(echo "$response" | jq -r '.paging.next.after // empty')
        [ -z "$after" ] && break
        
        sleep 0.25  # Search API rate limit
    done
}

# Usage: Export recent leads
export_filtered_contacts '[{
    "propertyName": "lifecyclestage",
    "operator": "EQ",
    "value": "lead"
}, {
    "propertyName": "createdate",
    "operator": "GTE", 
    "value": "2024-01-01"
}]' "recent_leads.csv"
```

## Data Validation

### Pre-Import Validation
```bash
#!/bin/bash
validate_csv() {
    local csv_file="$1"
    local required_columns=("email" "firstname" "lastname")
    local errors=0
    
    echo "Validating CSV file: $csv_file"
    
    # Check file exists
    [ ! -f "$csv_file" ] && { echo "File not found"; return 1; }
    
    # Check headers
    local header=$(head -n 1 "$csv_file")
    for col in "${required_columns[@]}"; do
        if ! echo "$header" | grep -q "$col"; then
            echo "ERROR: Missing required column: $col"
            errors=$((errors + 1))
        fi
    done
    
    # Check for empty emails
    local empty_emails=$(tail -n +2 "$csv_file" | cut -d',' -f1 | grep -c "^$")
    [ "$empty_emails" -gt 0 ] && {
        echo "ERROR: $empty_emails rows have empty email addresses"
        errors=$((errors + 1))
    }
    
    # Check email format
    local invalid_emails=$(tail -n +2 "$csv_file" | cut -d',' -f1 | grep -v "@" | wc -l)
    [ "$invalid_emails" -gt 0 ] && {
        echo "ERROR: $invalid_emails rows have invalid email format"
        errors=$((errors + 1))
    }
    
    if [ $errors -eq 0 ]; then
        echo "✅ CSV validation passed"
        return 0
    else
        echo "❌ CSV validation failed with $errors errors"
        return 1
    fi
}
```

### Duplicate Detection Before Import
```bash
#!/bin/bash
check_duplicates_before_import() {
    local csv_file="$1"
    
    echo "Checking for existing records..."
    
    tail -n +2 "$csv_file" | while IFS=',' read -r email firstname lastname; do
        existing=$(curl -s -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
            -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{
                \"filters\": [{
                    \"propertyName\": \"email\",
                    \"operator\": \"EQ\",
                    \"value\": \"$email\"
                }],
                \"limit\": 1
            }")
        
        local contact_id=$(echo "$existing" | jq -r '.results[0].id // empty')
        
        if [ -n "$contact_id" ]; then
            echo "DUPLICATE: $email already exists (ID: $contact_id)"
        fi
        
        sleep 0.25  # Search API rate limit
    done
}
```

## Migration Workflows

### Full CRM Migration
```bash
#!/bin/bash
migrate_crm_data() {
    local source_dir="$1"
    
    echo "Starting CRM migration from $source_dir"
    
    # 1. Import companies first (for associations)
    if [ -f "$source_dir/companies.csv" ]; then
        echo "Importing companies..."
        ./scripts/bulk-import.sh companies "$source_dir/companies.csv"
    fi
    
    # 2. Import contacts (with company associations)
    if [ -f "$source_dir/contacts.csv" ]; then
        echo "Importing contacts..."
        ./scripts/bulk-import.sh contacts "$source_dir/contacts.csv"
    fi
    
    # 3. Import deals (with contact/company associations)
    if [ -f "$source_dir/deals.csv" ]; then
        echo "Importing deals..."
        ./scripts/bulk-import.sh deals "$source_dir/deals.csv"
    fi
    
    # 4. Import tickets
    if [ -f "$source_dir/tickets.csv" ]; then
        echo "Importing tickets..."
        ./scripts/bulk-import.sh tickets "$source_dir/tickets.csv"
    fi
    
    echo "Migration complete"
}
```

### Data Backup Export
```bash
#!/bin/bash
backup_hubspot_data() {
    local backup_dir="hubspot_backup_$(date +%Y%m%d)"
    mkdir -p "$backup_dir"
    
    echo "Creating HubSpot data backup in $backup_dir"
    
    # Export all object types
    for object_type in contacts companies deals tickets; do
        echo "Exporting $object_type..."
        ./scripts/bulk-export.sh "$object_type" "$backup_dir/${object_type}.csv"
    done
    
    # Export custom objects
    # TODO: Add custom object export logic
    
    echo "Backup complete in $backup_dir"
}
```

## Common Import Issues

### Email Duplicate Handling
HubSpot prevents duplicate emails. Handle with:
```bash
# Option 1: Skip duplicates
if curl returns 409; then continue; fi

# Option 2: Update existing  
if duplicate_found; then 
    update_existing_contact
else
    create_new_contact
fi
```

### Date Format Issues
```bash
# Convert various date formats to ISO 8601
normalize_date() {
    local input_date="$1"
    
    # Try different formats
    if date -d "$input_date" "+%Y-%m-%d" 2>/dev/null; then
        return 0
    elif date -d "$(echo "$input_date" | sed 's|/|-|g')" "+%Y-%m-%d" 2>/dev/null; then
        return 0
    else
        echo "Invalid date: $input_date" >&2
        return 1
    fi
}
```

### Property Mapping
```bash
# Map external field names to HubSpot properties
map_property() {
    local external_field="$1"
    
    case "$external_field" in
        "First Name") echo "firstname" ;;
        "Last Name") echo "lastname" ;;
        "Email Address") echo "email" ;;
        "Phone Number") echo "phone" ;;
        "Company Name") echo "company" ;;
        *) echo "$external_field" | tr '[:upper:]' '[:lower:]' | sed 's/ /_/g' ;;
    esac
}
```

## HubSpot UI Tips

### Import Monitor
1. **Data Management → Import**
2. View import history and status
3. Download error reports
4. Re-import failed records

### Export Options
1. **Contacts/Companies/Deals → Actions → Export**
2. Choose All records or Current view
3. Select properties to include
4. Monitor export progress in notifications

### Import Templates
1. Use HubSpot's CSV templates
2. Download sample files from import wizard
3. Keep property names consistent
4. Test with small batches first