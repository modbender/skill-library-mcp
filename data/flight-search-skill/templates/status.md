# ✈️ Flight Status

**Flight:** {{FLIGHT_NUMBER}}
**Airline:** {{AIRLINE_NAME}}
**Route:** {{DEPARTURE_AIRPORT}} ({{DEPARTURE_IATA}}) → {{ARRIVAL_AIRPORT}} ({{ARRIVAL_IATA}})
**Date:** {{FLIGHT_DATE}}

---

## {{STATUS_EMOJI}} Status: {{STATUS_TEXT}}

---

### 📍 Departure

- **Airport:** {{DEPARTURE_AIRPORT}}
- **Terminal:** {{DEPARTURE_TERMINAL}}
- **Gate:** {{DEPARTURE_GATE}}
- **Scheduled:** {{DEPARTURE_SCHEDULED}}
- **Estimated:** {{DEPARTURE_ESTIMATED}}
{{#DEPARTURE_DELAY}}
- ⚠️ **Delay:** {{DEPARTURE_DELAY}} minutes
{{/DEPARTURE_DELAY}}

---

### 🛬 Arrival

- **Airport:** {{ARRIVAL_AIRPORT}}
- **Terminal:** {{ARRIVAL_TERMINAL}}
- **Gate:** {{ARRIVAL_GATE}}
- **Baggage:** {{ARRIVAL_BAGGAGE}}
- **Scheduled:** {{ARRIVAL_SCHEDULED}}
- **Estimated:** {{ARRIVAL_ESTIMATED}}
{{#ARRIVAL_DELAY}}
- ⚠️ **Delay:** {{ARRIVAL_DELAY}} minutes
{{/ARRIVAL_DELAY}}

---

### 🛩️ Aircraft

- **Type:** {{AIRCRAFT_TYPE}}
- **Registration:** {{AIRCRAFT_REGISTRATION}}

---

{{#LIVE_TRACKING}}
### 📡 Live Tracking

- **Altitude:** {{ALTITUDE}} m
- **Speed:** {{SPEED}} km/h
- **Direction:** {{DIRECTION}}°
- **Location:** {{LATITUDE}}, {{LONGITUDE}}
- **Last Updated:** {{LIVE_UPDATED}}
{{/LIVE_TRACKING}}

---

🔔 **Want to track this flight?** Say "track {{FLIGHT_NUMBER}}"

_Data from AviationStack. Updates every 30-60 seconds._
