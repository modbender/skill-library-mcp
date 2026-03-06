# Gas Price Alert - US City Coordinates

## Common US Cities

Use these coordinates for `--lat` and `--lon` parameters.

### Midwest

**Columbus, OH**
```
lat: 39.9612
lon: -82.9988
downtown: 39.9612, -82.9988
airport (CMH): 39.9980, -82.8919
```

**Chicago, IL**
```
lat: 41.8781
lon: -87.6298
downtown: 41.8781, -87.6298
airport (ORD): 41.9742, -87.9073
```

**Indianapolis, IN**
```
lat: 39.7684
lon: -86.1581
downtown: 39.7684, -86.1581
airport (IND): 39.7173, -86.2944
```

**Detroit, MI**
```
lat: 42.3314
lon: -83.0458
downtown: 42.3314, -83.0458
airport (DTW): 42.2162, -83.3554
```

### East Coast

**New York, NY**
```
lat: 40.7128
lon: -74.0060
downtown: 40.7128, -74.0060
airport (JFK): 40.6413, -73.7781
airport (LGA): 40.7769, -73.8740
```

**Boston, MA**
```
lat: 42.3601
lon: -71.0589
downtown: 42.3601, -71.0589
airport (BOS): 42.3656, -71.0096
```

**Philadelphia, PA**
```
lat: 39.9526
lon: -75.1652
downtown: 39.9526, -75.1652
airport (PHL): 39.8729, -75.2437
```

**Washington, DC**
```
lat: 38.9072
lon: -77.0369
downtown: 38.9072, -77.0369
airport (DCA): 38.8512, -77.0402
```

**Miami, FL**
```
lat: 25.7617
lon: -80.1918
downtown: 25.7617, -80.1918
airport (MIA): 25.7959, -80.2870
```

### West Coast

**Los Angeles, CA**
```
lat: 34.0522
lon: -118.2437
downtown: 34.0522, -118.2437
airport (LAX): 33.9425, -118.4081
```

**San Francisco, CA**
```
lat: 37.7749
lon: -122.4194
downtown: 37.7749, -122.4194
airport (SFO): 37.6213, -122.3790
```

**Seattle, WA**
```
lat: 47.6062
lon: -122.3321
downtown: 47.6062, -122.3321
airport (SEA): 47.4502, -122.3088
```

**Portland, OR**
```
lat: 45.5152
lon: -122.6784
downtown: 45.5152, -122.6784
airport (PDX): 45.5898, -122.5951
```

### South

**Atlanta, GA**
```
lat: 33.4484
lon: -84.3917
downtown: 33.4484, -84.3917
airport (ATL): 33.6407, -84.4277
```

**Dallas, TX**
```
lat: 32.7767
lon: -96.7970
downtown: 32.7767, -96.7970
airport (DFW): 32.8998, -97.0403
```

**Houston, TX**
```
lat: 29.7604
lon: -95.3698
downtown: 29.7604, -95.3698
airport (IAH): 29.9902, -95.3368
```

**Nashville, TN**
```
lat: 36.1627
lon: -86.7816
downtown: 36.1627, -86.7816
airport (BNA): 36.1263, -86.6774
```

### Mountain

**Denver, CO**
```
lat: 39.7392
lon: -104.9903
downtown: 39.7392, -104.9903
airport (DEN): 39.8561, -104.6737
```

**Phoenix, AZ**
```
lat: 33.4484
lon: -112.0740
downtown: 33.4484, -112.0740
airport (PHX): 33.4373, -112.0078
```

**Salt Lake City, UT**
```
lat: 40.7608
lon: -111.8910
downtown: 40.7608, -111.8910
airport (SLC): 40.7899, -111.9791
```

## Finding Coordinates

To find coordinates for any location:

1. **Google Maps:** Right-click on a location, coordinates appear
2. **OpenStreetMap:** Click on a location, coordinates shown in sidebar
3. **Geocoding services:** Nominatim (OpenStreetMap), Google Geocoding API

## Recommended Radius by Area Type

- **Urban downtown:** 5-10 miles (many stations)
- **Suburban:** 15-20 miles (good balance)
- **Rural:** 30-50 miles (fewer stations, need wider search)

## Costco Locations

The skill includes known Costco locations for major cities. For your area, you can:
1. Use the Costco Store Locator: https://www.costco.com/warehouse-locations
2. Add coordinates to the script's `search_costco_locations()` function
3. Or use the OpenStreetMap search which will find all stations including Costco
