# Salesforce fields created/updated by OutboundSync

Source: OutboundSync Help Center — “Which Salesforce fields are updated” (Last updated Jul 8, 2025).

OutboundSync can create these custom fields on **Lead** and **Contact**.

> **Note:** The Salesforce field set covers email engagement signals only. HubSpot-only properties (social engagement via HeyReach, email sequence step, open/reply counts, and email-specific campaign IDs) are not available in Salesforce. See `hubspot_properties.md` for the full property list.

| Field Label | API Name | Data Type | Description |
|---|---|---|---|
| Last App URL | `OSLast AppUrl__c` | Text (255) | The URL of the outbound app or Smartlead sequence that last updated this record. |
| Last Bounce Time | `OSLast BounceTime__c` | Date/Time | The time when the last email to this record bounced. |
| Last Campaign ID | `OSLast CampaignId__c` | Text (255) | The unique ID of the last campaign this contact or lead was part of. |
| Last Campaign Name | `OSLast CampaignName__c` | Text (255) | The name of the last outbound campaign associated with this record. |
| Last Category ID | `OSLast LeadCategoryId__c` | Text (255) | The internal ID of the last lead category assigned (e.g., positive reply, interested). |
| Last Lead Category Name | `OSLast LeadCategoryName__c` | Text (255) | The name of the last lead category (e.g., Interested, Not a Fit, Unsubscribed). |
| Last Link Click Time | `OSLast LinkClickTime__c` | Date/Time | The timestamp of the most recent link click from an outbound email. |
| Last Link Click URL | `OSLast LinkClickURL__c` | Text (255) | The URL that was most recently clicked by the lead or contact. |
| Last Open Message | `OSLast OpenMessage__c` | Long Text Area (32,000) | The body of the most recently opened email. |
| Last Open Subject | `OSLast OpenSubject__c` | Text (255) | The subject line of the most recently opened email. |
| Last Open Time | `OSLast OpenTime__c` | Date/Time | The timestamp of the most recent email open. |
| Last Reply Address | `OSLast ReplyAddress__c` | Text (255) | The email address that sent the last reply. |
| Last Reply Message | `OSLast ReplyMessage__c` | Long Text Area (32,000) | The content of the most recent reply received. |
| Last Reply Name | `OSLast ReplyName__c` | Text (255) | The sender name of the last reply. |
| Last Reply Subject | `OSLast ReplySubject__c` | Text (255) | The subject of the email to which the last reply was made. |
| Last Reply Time | `OSLast ReplyTime__c` | Date/Time | The timestamp of the most recent reply received. |
| Last Sent Address | `OSLast SentAddress__c` | Text (255) | The email address used to send the last outbound message. |
| Last Sent Message | `OSLast SentMessage__c` | Long Text Area (32,000) | The body content of the last email sent to this record. |
| Last Sent Name | `OSLast SentName__c` | Text (255) | The name of the sender for the last sent email. |
| Last Sent Subject | `OSLast SentSubject__c` | Text (255) | The subject of the last email sent. |
| Last Sent Time | `OSLast SentTime__c` | Date/Time | The timestamp of the last email sent to this lead or contact. |
| Last Unsubscribe Time | `OSLast UnsubscribeTime__c` | Date/Time | The time this contact or lead unsubscribed from outbound messaging. |
| Last Update Occurred | `OSLast UpdateOccurred__c` | Date/Time | When OutboundSync last updated any of these custom fields. |
| Last Update Source | `OSLast UpdateSource__c` | Text (255) | The source system (e.g., Smartlead, Instantly) that triggered the last update. |
