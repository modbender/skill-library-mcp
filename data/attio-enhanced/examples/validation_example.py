"""
Example script demonstrating data validation functionality
"""

from lib.attio_enhanced import validate_and_clean_crm_data


def main():
    """
    Example of using the enhanced validation functionality
    """
    # Sample records with some invalid data
    records = [
        {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'company': 'Example Corp'
        },
        {
            'first_name': '',  # Invalid: empty first name
            'last_name': 'Smith',
            'email': 'invalid-email',  # Invalid: bad email format
            'company': 'Acme Inc'
        },
        {
            'first_name': 'Bob',
            'last_name': 'Johnson',
            'email': 'bob.johnson@example.com',
            'company': ''  # This might be OK depending on business rules
        }
    ]
    
    # Validate and clean the data
    validation_results = validate_and_clean_crm_data(records, 'person')
    
    print("Validation Results:")
    print(f"Valid records: {validation_results['valid_count']}")
    print(f"Invalid records: {validation_results['invalid_count']}")
    
    print("\nValid Records:")
    for record in validation_results['valid_records']:
        print(f"  - {record['first_name']} {record['last_name']}")
    
    print("\nInvalid Records:")
    for invalid in validation_results['invalid_records']:
        idx = invalid['index']
        record = invalid['record']
        errors = invalid['errors']
        print(f"  Record {idx} ({record['first_name']} {record['last_name']}):")
        for field, field_errors in errors.items():
            print(f"    {field}: {', '.join(field_errors)}")


if __name__ == "__main__":
    main()