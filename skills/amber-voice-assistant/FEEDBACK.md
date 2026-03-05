# Amber Voice Assistant - User Feedback & Feature Requests

## Feature Requests

### Asterisk Integration (Local PBX Alternative to Twilio)
**Date:** 2026-02-21  
**Source:** Potential user feedback  
**Priority:** Medium-High  

**Request:**  
Support for local Asterisk server instead of cloud-based Twilio to keep everything self-hosted.

**Context:**
- User wants to avoid cloud service fees and dependencies
- Existing Asterisk infrastructure at home/office
- Privacy/control preference for keeping phone calls on-premises

**Technical Requirements:**
- Interface with Asterisk Manager Interface (AMI) or Asterisk Gateway Interface (AGI)
- Replace Twilio SIP bridge with Asterisk channel drivers
- Maintain OpenAI Realtime API integration
- Support both inbound and outbound calls through local PBX

**Considerations:**
- Would make Amber accessible to users without Twilio accounts
- Requires different setup/configuration than cloud-based approach
- May need different audio handling for local vs SIP trunks
- Could be parallel support (both Twilio AND Asterisk) rather than replacement

**Next Steps:**
- Research Asterisk AMI/AGI integration patterns
- Investigate OpenAI Realtime + Asterisk compatibility
- Evaluate effort vs user demand
- Could be v5.0 feature or separate skill fork

---

## Enhancement Ideas

*(Add more user feedback here as it comes in)*

---

## Resolved Requests

*(Move completed requests here)*
