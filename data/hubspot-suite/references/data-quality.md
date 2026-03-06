# HubSpot Data Quality & Deduplication

Tools and strategies for maintaining clean, high-quality CRM data.

## Duplicate Detection

### Find Duplicate Contacts by Email
```bash
#!/bin/bash
find_duplicate_emails() {
    curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
        -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "properties": ["email", "firstname", "lastname", "createdate"],
            "limit": 1000
        }' | \
    jq -r '.results[] | [.properties.email, .id, .properties.firstname, .properties.lastname, .properties.createdate] | @csv' | \
    sort | uniq -d -w 20  # Find duplicates by first 20 chars (email)
}
```

### Find Duplicate Companies by Domain
```bash
find_duplicate_domains() {
    curl -X POST "https://api.hubapi.com/crm/v3/objects/companies/search" \
        -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "properties": ["name", "domain", "createdate"],
            "filters": [{"propertyName": "domain", "operator": "HAS_PROPERTY"}],
            "limit": 1000
        }' | \
    jq -r '.results[] | [.properties.domain, .id, .properties.name, .properties.createdate] | @csv' | \
    sort | uniq -d -w 30
}
```

### Advanced Duplicate Detection
```bash
#!/bin/bash
find_fuzzy_duplicates() {
    local object_type="$1"  # contacts, companies
    local match_field="$2"  # email, domain, name
    
    # Get all records
    local records_file="/tmp/hubspot_${object_type}_${match_field}.txt"
    
    curl -X POST "https://api.hubapi.com/crm/v3/objects/$object_type/search" \
        -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"properties\": [\"$match_field\", \"firstname\", \"lastname\", \"name\"],
            \"filters\": [{\"propertyName\": \"$match_field\", \"operator\": \"HAS_PROPERTY\"}],
            \"limit\": 1000
        }" | \
    jq -r --arg field "$match_field" '.results[] | 
        [.id, .properties[$field], (.properties.firstname // .properties.name), .properties.lastname] | 
        @csv' > "$records_file"
    
    # Find potential matches
    echo "Potential duplicate groups:"
    
    case "$match_field" in
        "email")
            # Email variations (gmail.com vs googlemail.com, etc.)
            cat "$records_file" | while IFS=',' read -r id email first last; do
                normalized=$(echo "$email" | sed 's/googlemail.com/gmail.com/g' | tr '[:upper:]' '[:lower:]')
                echo "$id,$normalized,$first,$last"
            done | sort -k2 | uniq -D -f1
            ;;
        "name"|"company")
            # Name variations (Inc vs Inc. vs Incorporated)
            cat "$records_file" | while IFS=',' read -r id name first last; do
                normalized=$(echo "$name" | sed -e 's/\bInc\.\?/Inc/g' -e 's/\bCorp\.\?/Corp/g' -e 's/\bLLC\b/LLC/g' | tr '[:upper:]' '[:lower:]')
                echo "$id,$normalized,$first,$last"
            done | sort -k2 | uniq -D -f1
            ;;
    esac
    
    rm "$records_file"
}
```

## Record Merging

### Merge Two Contacts
```bash
merge_contacts() {
    local primary_id="$1"
    local duplicate_id="$2"
    
    echo "Merging contact $duplicate_id into $primary_id"
    
    # Get data from both contacts
    primary=$(curl -s -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        "https://api.hubapi.com/crm/v3/objects/contacts/$primary_id")
    
    duplicate=$(curl -s -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        "https://api.hubapi.com/crm/v3/objects/contacts/$duplicate_id")
    
    # Log before merge
    echo "Primary: $(echo "$primary" | jq -r '.properties.email')"
    echo "Duplicate: $(echo "$duplicate" | jq -r '.properties.email')"
    
    # Perform merge
    curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/merge" \
        -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"primaryObjectId\": \"$primary_id\",
            \"objectIdToMerge\": \"$duplicate_id\"
        }"
    
    echo "Merge completed"
}
```

### Safe Merge with Validation
```bash
safe_merge_contacts() {
    local primary_id="$1"
    local duplicate_id="$2"
    
    # Validate both contacts exist
    if ! curl -s -f -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        "https://api.hubapi.com/crm/v3/objects/contacts/$primary_id" >/dev/null; then
        echo "ERROR: Primary contact $primary_id not found"
        return 1
    fi
    
    if ! curl -s -f -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        "https://api.hubapi.com/crm/v3/objects/contacts/$duplicate_id" >/dev/null; then
        echo "ERROR: Duplicate contact $duplicate_id not found" 
        return 1
    fi
    
    # Check if they have the same email
    primary_email=$(curl -s -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        "https://api.hubapi.com/crm/v3/objects/contacts/$primary_id?properties=email" | \
        jq -r '.properties.email')
    
    duplicate_email=$(curl -s -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        "https://api.hubapi.com/crm/v3/objects/contacts/$duplicate_id?properties=email" | \
        jq -r '.properties.email')
    
    if [ "$primary_email" != "$duplicate_email" ]; then
        echo "WARNING: Email mismatch - Primary: $primary_email, Duplicate: $duplicate_email"
        read -p "Continue with merge? (y/N): " confirm
        [[ $confirm != [yY] ]] && { echo "Merge cancelled"; return 1; }
    fi
    
    # Backup associations before merge
    backup_associations "$duplicate_id"
    
    # Perform merge
    merge_contacts "$primary_id" "$duplicate_id"
}
```

## Data Completeness Audits

### Find Missing Critical Data
```bash
audit_missing_data() {
    local object_type="$1"
    
    echo "=== Data Completeness Audit: $object_type ==="
    
    case "$object_type" in
        "contacts")
            # Missing phone numbers
            echo "Contacts missing phone numbers:"
            curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
                -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
                -H "Content-Type: application/json" \
                -d '{
                    "filters": [{"propertyName": "phone", "operator": "NOT_HAS_PROPERTY"}],
                    "properties": ["firstname", "lastname", "email"],
                    "limit": 100
                }' | jq -r '.results | length'
            
            # Missing company associations
            echo "Contacts not associated with companies:"
            curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
                -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
                -H "Content-Type: application/json" \
                -d '{
                    "filters": [{"propertyName": "associatedcompanyid", "operator": "NOT_HAS_PROPERTY"}],
                    "properties": ["firstname", "lastname", "email"],
                    "limit": 100
                }' | jq -r '.results | length'
            ;;
            
        "companies")
            # Missing industry
            echo "Companies missing industry:"
            curl -X POST "https://api.hubapi.com/crm/v3/objects/companies/search" \
                -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
                -H "Content-Type: application/json" \
                -d '{
                    "filters": [{"propertyName": "industry", "operator": "NOT_HAS_PROPERTY"}],
                    "properties": ["name", "domain"],
                    "limit": 100
                }' | jq -r '.results | length'
            
            # Missing employee count
            echo "Companies missing employee count:"
            curl -X POST "https://api.hubapi.com/crm/v3/objects/companies/search" \
                -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
                -H "Content-Type: application/json" \
                -d '{
                    "filters": [{"propertyName": "numberofemployees", "operator": "NOT_HAS_PROPERTY"}],
                    "properties": ["name", "domain"],
                    "limit": 100
                }' | jq -r '.results | length'
            ;;
            
        "deals")
            # Missing close dates
            echo "Open deals missing close dates:"
            curl -X POST "https://api.hubapi.com/crm/v3/objects/deals/search" \
                -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
                -H "Content-Type: application/json" \
                -d '{
                    "filters": [
                        {"propertyName": "closedate", "operator": "NOT_HAS_PROPERTY"},
                        {"propertyName": "dealstage", "operator": "NOT_IN", "values": ["closedwon", "closedlost"]}
                    ],
                    "properties": ["dealname", "amount", "dealstage"],
                    "limit": 100
                }' | jq -r '.results | length'
            ;;
    esac
}
```

### Data Quality Score
```bash
calculate_data_quality_score() {
    local object_type="$1"
    local object_id="$2"
    
    # Get object data
    local data=$(curl -s -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        "https://api.hubapi.com/crm/v3/objects/$object_type/$object_id")
    
    local score=0
    local max_score=0
    
    case "$object_type" in
        "contacts")
            # Required fields (20 points each)
            [[ $(echo "$data" | jq -r '.properties.email') != "null" ]] && score=$((score + 20))
            [[ $(echo "$data" | jq -r '.properties.firstname') != "null" ]] && score=$((score + 20))
            [[ $(echo "$data" | jq -r '.properties.lastname') != "null" ]] && score=$((score + 20))
            max_score=$((max_score + 60))
            
            # Important fields (10 points each)
            [[ $(echo "$data" | jq -r '.properties.phone') != "null" ]] && score=$((score + 10))
            [[ $(echo "$data" | jq -r '.properties.company') != "null" ]] && score=$((score + 10))
            [[ $(echo "$data" | jq -r '.properties.jobtitle') != "null" ]] && score=$((score + 10))
            max_score=$((max_score + 30))
            
            # Nice to have (5 points each)
            [[ $(echo "$data" | jq -r '.properties.city') != "null" ]] && score=$((score + 5))
            [[ $(echo "$data" | jq -r '.properties.industry') != "null" ]] && score=$((score + 5))
            max_score=$((max_score + 10))
            ;;
    esac
    
    local percentage=$((score * 100 / max_score))
    echo "Data Quality Score: $score/$max_score ($percentage%)"
    
    if [ $percentage -ge 80 ]; then
        echo "Status: ✅ High Quality"
    elif [ $percentage -ge 60 ]; then
        echo "Status: ⚠️  Medium Quality" 
    else
        echo "Status: ❌ Low Quality"
    fi
}
```

## Data Standardization

### Phone Number Normalization
```bash
normalize_phone_number() {
    local phone="$1"
    
    # Remove all non-digits
    local digits_only=$(echo "$phone" | sed 's/[^0-9]//g')
    
    # Add country code if missing
    if [[ ${#digits_only} -eq 10 ]]; then
        digits_only="1$digits_only"
    fi
    
    # Format as +1-555-123-4567
    if [[ ${#digits_only} -eq 11 && ${digits_only:0:1} == "1" ]]; then
        echo "+1-${digits_only:1:3}-${digits_only:4:3}-${digits_only:7:4}"
    else
        echo "$phone"  # Return original if can't normalize
    fi
}

# Batch normalize phone numbers
normalize_all_phones() {
    curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
        -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "filters": [{"propertyName": "phone", "operator": "HAS_PROPERTY"}],
            "properties": ["phone"],
            "limit": 100
        }' | \
    jq -r '.results[] | [.id, .properties.phone] | @csv' | \
    while IFS=',' read -r id phone; do
        normalized=$(normalize_phone_number "$phone")
        
        if [ "$phone" != "$normalized" ]; then
            echo "Updating $id: $phone -> $normalized"
            
            curl -X PATCH "https://api.hubapi.com/crm/v3/objects/contacts/$id" \
                -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
                -H "Content-Type: application/json" \
                -d "{\"properties\": {\"phone\": \"$normalized\"}}"
        fi
        
        sleep 0.1
    done
}
```

### Email Validation
```bash
validate_email_format() {
    local email="$1"
    
    # Basic regex for email validation
    if [[ "$email" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        echo "valid"
    else
        echo "invalid"
    fi
}

find_invalid_emails() {
    curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
        -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "properties": ["email", "firstname", "lastname"],
            "limit": 1000
        }' | \
    jq -r '.results[] | [.id, .properties.email, .properties.firstname, .properties.lastname] | @csv' | \
    while IFS=',' read -r id email first last; do
        if [ "$(validate_email_format "$email")" = "invalid" ]; then
            echo "Invalid email: $id,$email,$first,$last"
        fi
    done
}
```

## Automated Data Cleanup

### Remove Test Data
```bash
cleanup_test_data() {
    echo "Finding test contacts..."
    
    # Find contacts with test emails
    test_contacts=$(curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
        -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "filters": [{
                "propertyName": "email",
                "operator": "CONTAINS_TOKEN",
                "value": "test"
            }],
            "properties": ["email", "firstname", "lastname"],
            "limit": 100
        }')
    
    echo "$test_contacts" | jq -r '.results[] | [.id, .properties.email] | @csv' | \
    while IFS=',' read -r id email; do
        echo "Archiving test contact: $email ($id)"
        
        curl -X DELETE "https://api.hubapi.com/crm/v3/objects/contacts/$id" \
            -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
    done
}
```

### Fix Common Data Issues
```bash
fix_common_issues() {
    echo "Fixing common data quality issues..."
    
    # 1. Standardize job titles
    standardize_job_titles() {
        local patterns=(
            "s/\bCEO\b/Chief Executive Officer/g"
            "s/\bCTO\b/Chief Technology Officer/g" 
            "s/\bCMO\b/Chief Marketing Officer/g"
            "s/\bVP\b/Vice President/g"
            "s/\bSr\.\?/Senior/g"
            "s/\bJr\.\?/Junior/g"
        )
        
        # Apply patterns to job titles
        # Implementation would fetch contacts and update job titles
    }
    
    # 2. Capitalize names properly
    fix_name_capitalization() {
        curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts/search" \
            -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{
                "properties": ["firstname", "lastname"],
                "limit": 100
            }' | \
        jq -r '.results[] | [.id, .properties.firstname, .properties.lastname] | @csv' | \
        while IFS=',' read -r id first last; do
            # Proper case conversion
            proper_first=$(echo "$first" | sed 's/\b\w/\u&/g')
            proper_last=$(echo "$last" | sed 's/\b\w/\u&/g')
            
            if [ "$first" != "$proper_first" ] || [ "$last" != "$proper_last" ]; then
                echo "Updating name: $id"
                
                curl -X PATCH "https://api.hubapi.com/crm/v3/objects/contacts/$id" \
                    -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
                    -H "Content-Type: application/json" \
                    -d "{
                        \"properties\": {
                            \"firstname\": \"$proper_first\",
                            \"lastname\": \"$proper_last\"
                        }
                    }"
            fi
        done
    }
    
    standardize_job_titles
    fix_name_capitalization
}
```

## Data Quality Monitoring

### Daily Data Quality Report
```bash
daily_data_quality_report() {
    local report_date=$(date +%Y-%m-%d)
    local report_file="data_quality_report_$report_date.txt"
    
    {
        echo "=== HubSpot Data Quality Report - $report_date ==="
        echo ""
        
        echo "CONTACTS:"
        echo "- Total contacts: $(get_object_count contacts)"
        echo "- Missing phone: $(get_missing_property_count contacts phone)"
        echo "- Missing company: $(get_missing_property_count contacts company)"
        echo "- Invalid emails: $(count_invalid_emails)"
        echo ""
        
        echo "COMPANIES:"
        echo "- Total companies: $(get_object_count companies)"
        echo "- Missing industry: $(get_missing_property_count companies industry)"
        echo "- Missing employee count: $(get_missing_property_count companies numberofemployees)"
        echo ""
        
        echo "DEALS:"
        echo "- Total deals: $(get_object_count deals)"
        echo "- Missing close date: $(get_missing_close_dates)"
        echo "- Missing associations: $(get_deals_without_contacts)"
        
    } > "$report_file"
    
    echo "Data quality report saved: $report_file"
}

get_object_count() {
    curl -s -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
        "https://api.hubapi.com/crm/v3/objects/$1?limit=1" | \
    jq -r '.total'
}
```

## HubSpot UI Data Quality Tools

### Using HubSpot's Built-in Tools
1. **Data Quality Command Center**
   - Navigate to Data Management → Data Quality
   - View data quality score
   - See recommendations for improvement

2. **Duplicate Management**
   - Contacts → Manage duplicates
   - Auto-merge suggestions
   - Manual merge tools

3. **Property History**
   - View change history on records
   - Track data modifications
   - Identify data quality issues

4. **Import Health**
   - Monitor import success rates
   - Review validation errors
   - Track data source quality