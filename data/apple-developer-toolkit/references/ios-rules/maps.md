---
description: "Implementation rules for maps"
---
# Maps

MAPS & LOCATION:
- import MapKit; use Map(position:) { } for SwiftUI maps
- Annotation("Label", coordinate:) { } for custom map pins
- MapCircle, MapPolyline for overlays
- CLLocationManager for user location — requires NSLocationWhenInUseUsageDescription (add CONFIG_CHANGES)
- @State private var position: MapCameraPosition = .automatic
- MKLocalSearch for place search; MKDirections for routing
- .mapControls { MapUserLocationButton(); MapCompass() }

OVERLAY PATTERNS ON MAP VIEWS:
- Map() with .ignoresSafeArea() fills screen edge-to-edge (behind status bar and home indicator)
- For overlays on a map (search bar, header, floating buttons), use .safeAreaInset(edge:) on the Map:
  Map(position: $position) { ... }
      .ignoresSafeArea()
      .safeAreaInset(edge: .top) {
          HeaderView()
              .padding(.horizontal)
              .background(.ultraThinMaterial)
      }
      .safeAreaInset(edge: .bottom) {
          ActionBar()
              .padding()
              .background(.ultraThinMaterial)
      }
- NEVER use ZStack { Map(); VStack { overlay }.padding(.top, 60) } — magic numbers break on different devices
- .mapControls positions built-in controls (compass, user location) inside safe area automatically
- For floating action buttons, use .overlay(alignment: .bottomTrailing) with .padding() — overlay respects safe area by default
