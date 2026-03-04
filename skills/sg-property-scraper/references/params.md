# PropertyGuru Parameter Reference

Complete list of valid parameter values for the PropertyGuru scraper.

## Listing Types
- `rent` — Property for rent
- `sale` — Property for sale

## Property Type Groups
- `N` — Condominium / Apartment
- `L` — Landed Property
- `H` — HDB (Housing Development Board)

## Sort Fields
- `date` — Sort by listing date
- `price` — Sort by price
- `psf` — Sort by price per square foot
- `size` — Sort by floor area

## Sort Orders
- `asc` — Ascending
- `desc` — Descending

## Entire Unit or Room
- `ent` — Entire unit only
- *(omit)* — Show both rooms and entire units

## Room Types (for room rentals with bedrooms=-1)
- `master` — Master bedroom
- `common` — Common room
- `shared` — Shared room

## Bedrooms
- `-1` — Room listing (use with roomType)
- `0` — Studio
- `1` to `5` — Number of bedrooms (use with entireUnitOrRoom=ent)

## MRT Station Codes

### North-South Line (NS)
NS1, NS2, NS3, NS3A, NS4, NS5, NS6, NS7, NS8, NS9, NS10, NS11, NS12, NS13, NS14, NS15, NS16, NS17, NS18, NS19, NS20, NS21, NS22, NS23, NS24, NS25, NS26, NS27, NS28

### East-West Line (EW)
EW1, EW2, EW3, EW4, EW5, EW6, EW7, EW8, EW9, EW10, EW11, EW12, EW13, EW14, EW15, EW16, EW17, EW18, EW19, EW20, EW21, EW22, EW23, EW24, EW25, EW26, EW27, EW28, EW29, EW30, EW31, EW32, EW33

### Changi Airport Branch (CG)
CG1, CG2

### North-East Line (NE)
NE1, NE3, NE4, NE5, NE6, NE7, NE8, NE9, NE10, NE11, NE12, NE13, NE14, NE15, NE16, NE17, NE18

*(Note: NE2 does not exist)*

### Circle Line (CC / CE)
CC1, CC2, CC3, CC4, CC5, CC6, CC7, CC8, CC9, CC10, CC11, CC12, CC13, CC14, CC15, CC16, CC17, CC19, CC20, CC21, CC22, CC23, CC24, CC25, CC26, CC27, CC28, CC29, CC30, CC31, CC32, CE1, CE2

*(Note: CC18 does not exist)*

### Downtown Line (DT)
DT1, DT2, DT3, DT5, DT6, DT7, DT8, DT9, DT10, DT11, DT12, DT13, DT14, DT15, DT16, DT17, DT18, DT19, DT20, DT21, DT22, DT23, DT24, DT25, DT26, DT27, DT28, DT29, DT30, DT31, DT32, DT33, DT34, DT35, DT36, DT37

*(Note: DT4 does not exist)*

### Thomson-East Coast Line (TE)
TE1, TE2, TE3, TE4, TE5, TE6, TE7, TE8, TE9, TE10, TE11, TE12, TE13, TE14, TE15, TE16, TE17, TE18, TE19, TE20, TE21, TE22, TE22A, TE23, TE24, TE25, TE26, TE27, TE28, TE29, TE30, TE31

### Jurong Region Line (JS / JE / JW)
JS1, JS2, JS3, JS4, JS5, JS6, JS7, JS8, JS9, JS10, JS11, JS12, JE1, JE2, JE3, JE4, JE5, JE6, JE7, JW1, JW2, JW3, JW4, JW5

### Cross Island Line (CR)
CR2, CR3, CR4, CR5, CR6, CR7, CR8, CR9, CR10, CR11, CR12, CR13

## Numeric Parameters (no fixed valid values)
- `minPrice` / `maxPrice` — Price in SGD
- `minSize` / `maxSize` — Floor area in sqft
- `minTopYear` / `maxTopYear` — Temporary Occupation Permit year
- `distanceToMRT` — Distance to nearest MRT in km (e.g. 0.5, 0.75, 1.0)
- `availability` — Availability status (integer)
