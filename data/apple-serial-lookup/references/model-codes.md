# Apple Model Code Mappings

These are the last 3-4 characters of old-format Apple serial numbers, which encode specific models, configurations, colors, and storage capacities.

**Note:** Apple doesn't publish complete model code tables. These mappings are compiled from repair databases, forums, and observed patterns.

## MacBook Pro Model Codes

### 2012 MacBook Pro Models

| Code | Model Identifier | Device | Processor | RAM | Storage | Notes |
|------|------------------|--------|-----------|-----|---------|-------|
| DKQ* | MacBookPro10,1 | MacBook Pro 15" Retina Mid-2012 | i7 2.3-2.7GHz | 8-16GB | 256-768GB | First Retina MacBook Pro |
| DL4* | MacBookPro9,1 | MacBook Pro 15" Mid-2012 | i7 2.3-2.7GHz | 4-8GB | 500GB-1TB | Non-Retina |

### 2013 MacBook Pro Models

| Code | Model Identifier | Device | Processor | RAM | Storage | Notes |
|------|------------------|--------|-----------|-----|---------|-------|
| F* | MacBookPro10,1 | MacBook Pro 15" Retina Early 2013 | i7 2.4-2.8GHz | 8-16GB | 256-768GB SSD | |
| G* | MacBookPro10,2 | MacBook Pro 13" Retina Late 2012/Early 2013 | i5/i7 | 8-16GB | 128-768GB SSD | |

## iPhone Model Codes

### iPhone 7 (2016)

| Code | Model Identifier | Device | Storage | Color | Carrier | Notes |
|------|------------------|--------|---------|-------|---------|-------|
| HG7H | iPhone9,1 | iPhone 7 4.7" | 32/128/256GB | Various | GSM | A10 Fusion, 2GB RAM |
| MN* | iPhone9,3 | iPhone 7 4.7" | 32/128/256GB | Various | CDMA | A10 Fusion, 2GB RAM |

### iPhone 7 Plus (2016)

| Code | Model Identifier | Device | Storage | RAM | Notes |
|------|------------------|--------|---------|-----|-------|
| NG* | iPhone9,2 | iPhone 7 Plus 5.5" | 32/128/256GB | 3GB | Dual camera |
| NF* | iPhone9,4 | iPhone 7 Plus 5.5" | 32/128/256GB | 3GB | CDMA variant |

## iPad Model Codes

### iPad (2021+) - New Randomized Format

New 10-character serials (like K4PMWCGJT4) cannot be decoded. Use Apple Check Coverage or browser automation for identification.

## Common Patterns

### Last Character (Storage/Config)
- **1, 2, 3**: Often indicate storage tiers (32/128/256GB) or configuration variants
- **H, K, L**: Common in iPhone storage encoding
- **Q, R, S**: Common in Mac configuration encoding

### Color Encoding (iPhones)
Model codes often embed color information, but mappings vary by generation:
- Space Gray, Silver, Gold, Rose Gold variants use different letter combinations
- (PRODUCT)RED and Jet Black introduced additional codes

## Model Identifier Patterns

### Mac Format
- **MacBookPro{X},{Y}**: X = generation, Y = size/variant
  - MacBookPro10,1 = 15" Retina Mid 2012-Early 2013
  - MacBookPro10,2 = 13" Retina Late 2012-Early 2013

### iPhone Format  
- **iPhone{X},{Y}**: X = chip generation, Y = variant
  - iPhone9,1 = iPhone 7 (GSM)
  - iPhone9,3 = iPhone 7 (CDMA)

## Data Sources

1. **EveryMac.com** - Most comprehensive Mac database
2. **The Apple Wiki** - Community-maintained device specifications
3. **Apple Support Pages** - Official model identifier listings
4. **Repair Databases** - Real-world mappings from service providers

## Limitations

- **Incomplete**: Many model codes are undocumented
- **Regional Variants**: Same model may have different codes by region/carrier
- **New Format**: Post-2021 serials are randomized and cannot be decoded
- **Updates**: Apple occasionally reuses or changes code patterns

For unknown codes, web lookup via EveryMac or Apple Support is required.