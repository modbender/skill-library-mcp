# UI Flows (Salesforce Lightning)

## Create Lead
- App Launcher → Sales → Leads → New
- Required: Last Name, Company
- Common: First Name, Title, Email, Phone, Lead Source
- Save and capture record URL

## Convert Lead
- Lead record → Convert
- Confirm Account/Contact/Opportunity creation

## Create Opportunity
- Opportunities → New
- Required: Opportunity Name, Close Date, Stage
- Common: Amount, Lead Source, Primary Campaign

## Create Case
- Service App → Cases → New
- Required: Contact or Account, Subject, Status
- Common: Origin, Priority

## Create Quote (CPQ)
- Opportunity → Quotes → New
- Select Price Book
- Add Products → Quote Lines → Save

## Update Record
- Open record → Edit
- Modify fields → Save
- Confirm success toast

## Delete Record
- Record dropdown → Delete
- Confirm delete dialog
- Capture confirmation

## Setup Navigation
- Setup (gear icon) → Setup
- Use Quick Find for objects (Apex Classes, Users, Profiles, Permission Sets)
