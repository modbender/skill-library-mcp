import os
import sys
from scripts.hienergy_skill import HiEnergySkill

def main():
    api_key = os.environ.get('HIENERGY_API_KEY')
    if not api_key:
        print("Error: HIENERGY_API_KEY env var not set.")
        sys.exit(1)

    skill = HiEnergySkill(api_key=api_key)
    
    print("Fetching last 50 approvals...")
    try:
        # 1. Get last 50 approvals
        approvals = skill.get_status_changes(to_status='approved', limit=50)
        
        if not approvals:
            print("No recent approvals found.")
            return

        print(f"Found {len(approvals)} recent approvals. Checking for contacts...")
        
        # Deduplicate by advertiser_id
        seen_advertisers = set()
        results = []

        for approval in approvals:
            adv_id = str(approval.get('advertiser_id'))
            adv_name = approval.get('advertiser_name', 'Unknown Advertiser')
            
            if not adv_id or adv_id in seen_advertisers:
                continue
            
            seen_advertisers.add(adv_id)
            
            # 2. Get contacts for this advertiser
            # Note: The /contacts endpoint filters by advertiser_id. 
            try:
                contacts = skill.get_contacts(advertiser_id=adv_id, limit=3)
                
                if contacts:
                    contact_strings = []
                    for c in contacts:
                        c_name = c.get('name') or c.get('full_name') or 'Unknown'
                        c_email = c.get('email') or 'No email'
                        contact_strings.append(f"{c_name} <{c_email}>")
                    
                    results.append(f"**{adv_name}**: {', '.join(contact_strings)}")
                # else:
                #    results.append(f"**{adv_name}**: No contacts found") # Optional: include empty ones?

            except Exception as e:
                # print(f"Failed to fetch contacts for {adv_name}: {e}")
                pass

        if not results:
            print("No contacts found for the recently approved advertisers.")
        else:
            print("\nContacts for recently approved advertisers:")
            for line in results:
                print(f"- {line}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
