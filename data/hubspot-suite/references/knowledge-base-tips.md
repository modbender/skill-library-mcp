# HubSpot Knowledge Base Tips

Common admin tasks, UI navigation, and troubleshooting guidance.

## Account & Portal Setup

### Initial Portal Configuration
1. **Settings → Account Defaults**
   - Set company currency and timezone
   - Configure date formats
   - Set default user permissions

2. **User Management**
   - Settings → Users & Teams
   - Create teams for sales, marketing, service
   - Set up user roles and permissions
   - Configure two-factor authentication

3. **Domain Setup**
   - Settings → Domains & URLs
   - Connect your website domain
   - Set up tracking domain for emails
   - Configure meeting links domain

## CRM Setup & Configuration

### Contact & Company Properties
1. **Creating Custom Properties**
   - Settings → Properties → Contacts
   - Choose appropriate field type (text, dropdown, number, etc.)
   - Group related properties together
   - Set display order and permissions

2. **Property Dependencies**
   - Use dependent fields for conditional logic
   - Example: Show "Budget Range" only if "Qualified" = Yes
   - Settings → Properties → [Object] → Create dependent property

3. **Required Fields**
   - Make critical fields required during record creation
   - Configure validation rules for data quality
   - Set up default values where applicable

### Deal Pipelines & Stages
1. **Pipeline Configuration**
   - Settings → Objects → Deals → Pipelines
   - Customize stages to match your sales process
   - Set probability percentages for each stage
   - Configure automation between stages

2. **Deal Stage Requirements**
   - Set required properties for stage advancement
   - Example: Require "Budget" before moving to "Proposal"
   - Use workflows to enforce business rules

3. **Multiple Pipelines**
   - Create separate pipelines for different product lines
   - Example: Enterprise Sales vs SMB Sales
   - Different stages and requirements per pipeline

## Lead Management & Scoring

### Lead Scoring Setup
1. **Positive Scoring Rules**
   - Settings → Lead Scoring
   - +10 points for email open
   - +20 points for form submission
   - +50 points for demo request
   - Company size and industry scoring

2. **Negative Scoring Rules**
   - -10 points for unsubscribe
   - -5 points for email bounce
   - Job title exclusions (student, personal email)

3. **Lead Qualification Process**
   - Set MQL threshold (e.g., 50 points)
   - Create workflows to assign qualified leads
   - Notify sales team of hot leads

### Lead Source Tracking
1. **UTM Parameter Setup**
   - Use consistent UTM naming conventions
   - Track campaigns across all channels
   - Set up HubSpot tracking URLs

2. **Form Source Attribution**
   - Enable automatic lead source capture
   - Set up hidden fields for campaign tracking
   - Use smart content for source-specific messaging

## Email Marketing & Automation

### Email Template Best Practices
1. **Template Design**
   - Use mobile-responsive templates
   - Include your logo and branding
   - Keep subject lines under 50 characters
   - Add clear call-to-action buttons

2. **Personalization**
   - Use contact property tokens: `Hi {{ contact.firstname }}`
   - Segment lists for targeted messaging
   - A/B test subject lines and content

3. **Compliance Setup**
   - Add unsubscribe links to all emails
   - Include company address in footer
   - Set up subscription preferences page
   - Configure GDPR compliance settings

### Workflow Automation
1. **Welcome Series**
   - Trigger: Contact subscribes to newsletter
   - Action: Send welcome email immediately
   - Delay: 3 days, send educational content
   - Delay: 1 week, send product overview

2. **Lead Nurturing**
   - Trigger: Contact downloads whitepaper
   - Action: Add to nurture list
   - Action: Assign lead score +20
   - Delay: 2 days, send follow-up email

3. **Sales Notifications**
   - Trigger: Deal moves to "Decision Maker Bought In"
   - Action: Create task for sales rep
   - Action: Send internal notification
   - Action: Update deal properties

## Sales Process Optimization

### Activity Logging
1. **Call Logging**
   - Use HubSpot mobile app for call logging
   - Set up call dispositions (Connected, No Answer, etc.)
   - Track call duration and outcomes
   - Associate calls with deals and contacts

2. **Email Integration**
   - Connect Gmail/Outlook for email tracking
   - Use HubSpot Sales Chrome extension
   - Track email opens and clicks
   - Set up email templates for common responses

3. **Meeting Scheduling**
   - Set up meeting links for easy scheduling
   - Configure buffer times between meetings
   - Add meeting types (demo, discovery, close)
   - Enable automatic meeting reminders

### Sales Reporting
1. **Activity Dashboard**
   - Track calls, emails, meetings per rep
   - Monitor response times
   - Measure activity-to-opportunity conversion
   - Set up weekly activity goals

2. **Pipeline Reports**
   - Deal velocity by stage
   - Conversion rates between stages
   - Average deal size trends
   - Win/loss analysis by rep

## Customer Service Setup

### Ticket Management
1. **Ticket Pipelines**
   - Settings → Objects → Tickets → Pipelines
   - Stages: New → In Progress → Waiting on Customer → Closed
   - Set up SLA requirements per priority level
   - Configure auto-assignment rules

2. **Knowledge Base**
   - Service → Knowledge Base
   - Create article categories by topic
   - Use SEO-friendly URLs
   - Set up internal vs external articles
   - Enable customer portal access

3. **Customer Feedback**
   - Set up CSAT surveys after ticket closure
   - Create NPS campaigns for customers
   - Use feedback to improve service processes
   - Track customer satisfaction trends

### Live Chat & Chatbots
1. **Chat Widget Setup**
   - Conversations → Chatflows
   - Customize appearance and behavior
   - Set availability hours and routing
   - Create canned responses for common questions

2. **Chatbot Configuration**
   - Build qualification chatbots
   - Route visitors to appropriate teams
   - Capture lead information
   - Integrate with meeting scheduler

## Data Management & Hygiene

### Import Best Practices
1. **Data Preparation**
   - Clean data before importing
   - Use HubSpot's CSV template
   - Map external fields to HubSpot properties
   - Test with small batch first

2. **Duplicate Prevention**
   - Use email as unique identifier for contacts
   - Use domain for company deduplication
   - Review duplicate suggestions before import
   - Set up automated duplicate alerts

3. **Data Validation**
   - Set up property validation rules
   - Use dropdown fields where possible
   - Require key fields for data completeness
   - Regular data audits and cleanup

### List Management
1. **Smart Lists vs Static Lists**
   - Use smart lists for dynamic segmentation
   - Static lists for one-time campaigns
   - Combine lists with AND/OR logic
   - Regular list hygiene and updates

2. **Segmentation Strategy**
   - Segment by lifecycle stage
   - Industry and company size segments
   - Behavioral segments (engagement level)
   - Geographic segmentation

## Integration & API Management

### Common Integrations
1. **Salesforce Sync**
   - App Marketplace → Salesforce Integration
   - Choose sync direction and objects
   - Map fields between systems
   - Set up conflict resolution rules

2. **Gmail/Outlook Integration**
   - Connect email for tracking and logging
   - Use HubSpot Sales browser extension
   - Sync calendar for meeting scheduling
   - Enable automatic contact creation

3. **Social Media Integration**
   - Connect LinkedIn for social selling
   - Facebook/Instagram for lead ads
   - Twitter for social monitoring
   - Set up social media reporting

### API & Developer Tools
1. **Private App Setup**
   - Settings → Integrations → Private Apps
   - Select required scopes
   - Generate access token
   - Test API connection

2. **Webhook Configuration**
   - Settings → Integrations → Webhooks
   - Choose events to track
   - Set up endpoint URL
   - Test webhook delivery

## Mobile App Usage

### HubSpot Mobile Features
1. **Contact Management**
   - View and edit contact records
   - Log calls and meetings on the go
   - Take photos and add to records
   - Use voice-to-text for notes

2. **Deal Management**
   - Update deal stages from mobile
   - View pipeline on the go
   - Get notifications for deal changes
   - Quick deal creation

3. **Task Management**
   - View daily task list
   - Create and complete tasks
   - Set reminders and due dates
   - Voice memos for follow-ups

## Troubleshooting Common Issues

### Email Deliverability
1. **Low Open Rates**
   - Check sender reputation
   - Review subject line length
   - Verify email authentication (SPF, DKIM)
   - Clean list of inactive contacts

2. **High Bounce Rates**
   - Remove hard bounces immediately
   - Validate email addresses before sending
   - Use double opt-in for subscriptions
   - Monitor bounce rate trends

3. **Spam Complaints**
   - Review email content for spam triggers
   - Ensure clear unsubscribe process
   - Segment lists for relevant content
   - Check complaint rates by source

### Data Sync Issues
1. **Integration Sync Failures**
   - Check API rate limits
   - Verify authentication tokens
   - Review field mapping conflicts
   - Check for required field errors

2. **Duplicate Records**
   - Use HubSpot's duplicate detection
   - Set up automatic merge rules
   - Regular data audits
   - Train team on data entry standards

3. **Missing Data**
   - Check import logs for errors
   - Verify field mapping
   - Review user permissions
   - Check for hidden/deleted records

### Performance Issues
1. **Slow Loading**
   - Clear browser cache
   - Check internet connection
   - Review browser extensions
   - Try incognito mode

2. **Feature Not Working**
   - Check user permissions
   - Verify feature is enabled
   - Review browser compatibility
   - Contact HubSpot support

## Getting Help & Support

### HubSpot Resources
1. **Knowledge Base**
   - knowledge.hubspot.com
   - Video tutorials and guides
   - Step-by-step instructions
   - Best practice articles

2. **Community**
   - community.hubspot.com
   - Ask questions to other users
   - Share experiences and tips
   - Get advice from experts

3. **Academy**
   - academy.hubspot.com
   - Free certification courses
   - Product training videos
   - Sales and marketing education

4. **Support Channels**
   - In-app chat support
   - Email support tickets
   - Phone support (paid plans)
   - Premium support options

### Training & Onboarding
1. **New User Training**
   - Complete HubSpot Academy courses
   - Set up practice portal
   - Join user onboarding sessions
   - Review documentation

2. **Team Training**
   - Schedule group training sessions
   - Create internal documentation
   - Set up test environments
   - Regular skill updates

3. **Advanced Features**
   - Custom object training
   - Workflow automation
   - API integration basics
   - Reporting and analytics