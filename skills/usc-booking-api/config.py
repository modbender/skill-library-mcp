#!/usr/bin/env python3
"""
Urban Sports Scanner - Venue Configuration

Trage hier deine Venues ein. Die Venue-ID findest du in der URL
der Venue-Seite auf urbansportsclub.com:
  https://urbansportsclub.com/de/venues/20818
                                         ^^^^^
Keywords helfen bei der Erkennung der Kursnamen im Seitentext.

plan_type: Mitgliedschafts-Stufe (bestimmt welche Kurse buchbar sind).
business_type: "b2c" (Privatmitglieder) oder "b2b" (Firmenmitglieder).
"""

# Privat (b2c): 1=Essential, 2=Classic, 3=Premium, 6=Max
# Firma  (b2b): 1=S, 2=M, 3=L, 6=XL
PLAN_TYPE = 3       # Premium
BUSINESS_TYPE = "b2c"  # b2c = Privat, b2b = Firma

VENUES = {
    # Beispiel:
    # "storm": {
    #     "name": "STORM Cycling Berlin - Mitte",
    #     "url": "https://urbansportsclub.com/de/venues/20818",
    #     "type": "cycling",
    #     "keywords": ["Performance", "Groove", "Cycling"],
    # },
}
