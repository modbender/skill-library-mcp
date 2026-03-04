# Data Annotation Platform - Configuration Reference

## Overview
The Data Annotation platform (data.smlcrm.com) is used for uploading, cleaning, and configuring time series datasets for ML/AI training in Energy, Manufacturing, and Climate domains.

## Supported Domains

- **Energy**: Power consumption, utilities, renewable energy, grid data
- **Manufacturing**: Industrial processes, steel production, emissions, equipment data  
- **Climate**: CO2 emissions, environmental monitoring, weather correlation data

## Workflow Steps

### 1. Dataset Upload (Raw)
- Navigate to data.smlcrm.com/dashboard
- Click "Upload Dataset" button
- Fill in metadata:
  - **Name**: Dataset name (e.g., "Steel Industry Energy Consumption")
  - **Domain**: Category (Energy, Manufacturing, Climate)
  - **Source URL**: Original data source (e.g., Kaggle URL)
  - **Description**: Brief description of the dataset
- Upload the **original/raw** CSV file
- Dataset appears with **RAW** status

### 2. Dataset Cleaning
- Find the RAW dataset in the list
- Click "Clean" button
- Upload **cleaned** CSV file (use `clean_dataset.py` script first)

### 3. Configure Dataset Headers (Metadata)
After uploading cleaned file, configure each column:

#### Column Types
| Type | Description | When to Use |
|------|-------------|-------------|
| **Time** | Timestamp/datetime column | For date/time fields |
| **Target** | Variable to predict | The main output variable for ML models |
| **Covariate** | Input features | Independent variables/features |
| **Group** | Categorical groupings | Variables that define segments/categories |

#### Required Setup
- **At least one Time column** (usually the timestamp)
- **At least one Target column** (what you're predicting)
- **Units**: Specify units for each column (e.g., kWh, °C, %, ratio, tCO2)

#### Common Unit Examples by Domain

**Energy Domain:**
- kWh, MWh, MW - Energy/power consumption
- kVarh - Reactive power
- ratio - Power factor
- seconds, minutes - Time encodings

**Manufacturing Domain:**
- tCO2, kgCO2 - Emissions
- ratio - Efficiency metrics
- % - Percentage values
- °C - Temperature

**Climate Domain:**
- tCO2 - Carbon emissions
- ppm - Concentrations
- mm - Precipitation
- °C - Temperature

### 4. Assign Groups to Variables
- Select ALL variables (target + all covariates) via checkboxes
- Click ALL group tags one by one
- Each click applies that group to all selected variables
- Result: All variables have all groups assigned

**Example Pattern:**
1. Select: Target + Covariate1 + Covariate2 + Covariate3...
2. Click: GroupTag1 → all get GroupTag1
3. Click: GroupTag2 → all get GroupTag2
4. Click: GroupTag3 → all get GroupTag3
5. Final: "GroupTag1 × GroupTag2 × GroupTag3" on all variables

### 5. Upload Cleaned Dataset
- Click "Upload Cleaned Dataset" to finalize
- Dataset status changes from RAW to CLEAN

## Column Naming Conventions

### Good Practices
- Use descriptive names: `energy_consumption_kwh` not `col1`
- Include units in name when helpful: `temperature_celsius`
- Avoid spaces (use underscores): `power_factor` not `power factor`
- Avoid special characters except underscore

### Typical Time Series Structure
```
- date/timestamp/Timestamps → Time
- target_variable → Target (with units)
- feature_1, feature_2, ... → Covariates (with units)
- category_1, category_2, ... → Groups (no units)
```

## Troubleshooting

### "Next" button is disabled
- Ensure at least one column is set to "Time" type
- Ensure at least one column is set to "Target" type
- All columns must have appropriate types assigned

### Groups not appearing
- Columns must be explicitly marked as "Group" type in header configuration
- After setting Group type, proceed to next step to see group tags

### Can't assign groups properly
- Must select variables via checkboxes BEFORE clicking group tags
- Group tags only appear after at least one column is set to Group type
- Remember to select BOTH target and covariates

### Upload fails
- Check CSV format (comma-delimited)
- Ensure no empty column names
- Verify file is not corrupted
- Try re-cleaning with the clean_dataset.py script

## Kaggle Dataset Integration

### Finding Datasets
1. Search Kaggle for relevant datasets
2. Check data description and schema
3. Download CSV files

### Common Dataset Sources by Domain

**Energy:**
- Steel Industry Energy Consumption (South Korea)
- Household power consumption
- Renewable energy production data

**Manufacturing:**
- Industrial emissions datasets
- Equipment sensor data
- Production line metrics

**Climate:**
- Climate TRACE emissions data
- CO2 monitoring datasets
- Weather correlation data

### Download Process
1. Navigate to dataset page on Kaggle
2. Click "Download" button
3. Extract CSV from zip file
4. Run cleaning script
5. Upload to Data Annotation platform
