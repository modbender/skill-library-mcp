"""
Example script demonstrating batch import functionality
"""

import asyncio
import os
from lib.attio_enhanced import AttioEnhancedClient, batch_import_contacts


async def main():
    """
    Example of using the enhanced Attio client for batch imports
    """
    # Sample contact data for import
    contacts = [
        {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'company': 'Example Corp',
            'job_title': 'Software Engineer'
        },
        {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'company': 'Acme Inc',
            'job_title': 'Product Manager'
        },
        {
            'first_name': 'Bob',
            'last_name': 'Johnson',
            'email': 'bob.johnson@example.com',
            'company': 'Tech Solutions',
            'job_title': 'CTO'
        }
    ]
    
    # Perform batch import with all enhancements
    results = await batch_import_contacts(
        contacts=contacts,
        api_key=os.getenv('ATTIO_API_KEY'),
        workspace_id=os.getenv('ATTIO_WORKSPACE_ID')
    )
    
    print("Import Results:")
    print(f"Total Records: {results['import_results']['total_records']}")
    print(f"Successful: {results['import_results']['successful']}")
    print(f"Failed: {results['import_results']['failed']}")
    
    if results['import_results']['failed_details']:
        print("\nFailed Records:")
        for failure in results['import_results']['failed_details']:
            print(f"  Index {failure['index']}: {failure.get('errors', failure.get('error', 'Unknown error'))}")


if __name__ == "__main__":
    asyncio.run(main())