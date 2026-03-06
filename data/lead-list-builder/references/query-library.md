# Search Query Library

## How to Build Queries

Formula: `"[keyword] [city]" -yelp -facebook -tripadvisor -houzz -thumbtack -homeadvisor`

Always exclude aggregators to get direct business websites only.

## Niche Query Templates

### Landscaping / Lawn Care
```
"landscaping company {city}"
"lawn care service {city}"
"landscape design {city}"
"lawn maintenance {city}"
"{city} landscaping contractor"
```

### Plumbing
```
"plumber in {city}"
"plumbing company {city}"
"emergency plumber {city}"
"drain cleaning {city}"
"{city} plumbing services"
```

### HVAC / Heating & Cooling
```
"HVAC company {city}"
"air conditioning repair {city}"
"heating and cooling {city}"
"furnace repair {city}"
```

### Restaurant / Cafe / Food
```
"restaurant {city}" -yelp -tripadvisor -opentable
"cafe {city}" -yelp
"diner {city}"
"pizza restaurant {city}"
"family restaurant {city}"
```

### Hair Salon / Beauty
```
"hair salon {city}"
"beauty salon {city}"
"barbershop {city}"
"nail salon {city}"
"spa {city}"
```

### General Contractor / Home Services
```
"general contractor {city}"
"home remodeling {city}"
"roofing company {city}"
"painting company {city}"
"flooring company {city}"
"electrical contractor {city}"
```

### Auto Services
```
"auto repair shop {city}"
"car mechanic {city}"
"auto body shop {city}"
"tire shop {city}"
```

### Medical / Dental / Chiro
```
"dentist {city}"
"chiropractor {city}"
"physical therapy {city}"
"optometrist {city}"
```

### Gym / Fitness
```
"gym {city}"
"personal trainer {city}"
"yoga studio {city}"
"crossfit {city}"
"fitness studio {city}"
```

### Real Estate / Property
```
"property management company {city}"
"real estate agent {city}"
"mortgage broker {city}"
```

### Pet Services
```
"dog groomer {city}"
"veterinarian {city}"
"pet boarding {city}"
"dog trainer {city}"
```

## Aggregators to Always Exclude
```
-yelp -facebook -tripadvisor -houzz -thumbtack -homeadvisor -angi -angieslist
-bbb.org -yellowpages -manta -bark.com -porch.com -chamberofcommerce
-google.com/maps -maps.google -nextdoor -foursquare -citysearch
```

## Finding Ultra-Neglected Sites (High Score Leads)

Add these to find the most outdated sites:
```
"landscaping {city}" inurl:index.html          # Old static sites
"plumber {city}" "© 2018" OR "© 2017" OR "© 2016"   # Copyright year in title
"contractor {city}" site:.com -site:wordpress.com  # Own domain, possibly old
"restaurant {city}" filetype:html              # Static HTML pages
```

## City Format Tips
- Use full state: "Portland OR" not just "Portland"
- For large metros: also try suburbs ("Beaverton OR", "Lake Oswego OR")
- For small markets: drop city, use region ("central Oregon landscaping")
