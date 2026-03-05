# 🔍 Flight Search Results

**Route:** {{ORIGIN}} → {{DESTINATION}}
**Dates:** {{DEPARTURE_DATE}}{{#RETURN_DATE}} / {{RETURN_DATE}}{{/RETURN_DATE}}
**Passengers:** {{ADULTS}} adult(s)
**Currency:** {{CURRENCY}}

---

## ✈️ Best Options

{{#FLIGHTS}}
### {{INDEX}}. {{AIRLINE}} - {{PRICE}} {{CURRENCY}}

**Outbound:** {{DEPARTURE_DATE}}
- {{#SEGMENTS_OUTBOUND}}
  - {{FROM}} → {{TO}} | {{DEPARTURE_TIME}} - {{ARRIVAL_TIME}} | {{CARRIER}} {{FLIGHT_NUMBER}}
  - Duration: {{DURATION}}
{{/SEGMENTS_OUTBOUND}}

{{#HAS_RETURN}}
**Return:** {{RETURN_DATE}}
- {{#SEGMENTS_RETURN}}
  - {{FROM}} → {{TO}} | {{DEPARTURE_TIME}} - {{ARRIVAL_TIME}} | {{CARRIER}} {{FLIGHT_NUMBER}}
  - Duration: {{DURATION}}
{{/SEGMENTS_RETURN}}
{{/HAS_RETURN}}

**Total Duration:** {{TOTAL_DURATION}}
**Class:** {{TRAVEL_CLASS}}

---
{{/FLIGHTS}}

## 📊 Summary

- **Lowest Price:** {{MIN_PRICE}} {{CURRENCY}} ({{MIN_AIRLINE}})
- **Shortest Duration:** {{MIN_DURATION}} ({{MIN_DURATION_AIRLINE}})
- **Best Value:** {{BEST_VALUE_AIRLINE}}

---

🔔 **Want to monitor prices?** Say "monitor this route"
