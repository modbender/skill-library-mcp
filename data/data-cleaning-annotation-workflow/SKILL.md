---
name: data-cleaning-annotation-workflow
description: "Complete workflow for time series datasets (Energy, Manufacturing, Climate) on Kaggle to Data Annotation platform (data.smlcrm.com). Includes downloading, cleaning with pandas, uploading RAW with metadata, configuring columns (Time/Target/Covariate/Group), setting units (kWh, kVarh, tCO2, ratio, seconds), and assigning groups by selecting all variables and applying all group tags. Use when finding Kaggle datasets, cleaning for ML, uploading with metadata, configuring types/units, assigning groups to all variables, or complete pipeline to CLEAN status."
---

# Simulacrum Data Annotation Workflow

Complete end-to-end workflow for time series dataset preparation and annotation on the Data Annotation platform (data.smlcrm.com).

## What This Skill Does

This skill captures the precise workflow for processing time series datasets (Energy, Manufacturing, Climate) from discovery to CLEAN status:

1. **Find Dataset**: Search Kaggle for Energy/Manufacturing/Climate time series data
2. **Download**: Get CSV files via browser or Kaggle CLI
3. **Clean**: Run Python/pandas script to handle missing values, duplicates, formatting
4. **Upload RAW**: Upload original CSV with metadata (name, domain, source URL, description)
5. **Configure Headers**: Set column types (Time, Target, Covariate, Group) and units
6. **Assign Groups**: Select ALL variables (target + covariates), apply ALL group tags
7. **Upload Cleaned**: Final upload → **CLEAN** status

## Supported Domains

- **Energy**: Power consumption, utilities, renewable energy, grid data
- **Manufacturing**: Industrial processes, steel production, emissions, equipment data
- **Climate**: CO2 emissions, environmental monitoring, weather correlation data

## Quick Start

For the full pipeline from Kaggle to annotated dataset:

```
1. Find dataset on Kaggle
2. Download (browser or kaggle CLI)
3. Clean with scripts/clean_dataset.py
4. Upload RAW dataset to data.smlcrm.com (with metadata)
5. Click "Clean" and upload cleaned file
6. Configure column metadata (types, units)
7. Assign groups to variables
8. Upload cleaned dataset → CLEAN status
```

## Workflow Steps

### Step 1: Find and Download Dataset

**From Kaggle (Browser Method):**
1. Navigate to kaggle.com/datasets
2. Search for relevant dataset (e.g., "steel industry energy consumption", "manufacturing emissions", "climate CO2")
3. Review data description, file list, and preview
4. Click "Download" button
5. Extract CSV file from downloaded zip

**Alternative: Kaggle CLI**
```bash
# Install if needed: pip install kaggle
# Configure: kaggle competitions list

scripts/download_kaggle.sh <dataset-name> [output-dir]
# Example: scripts/download_kaggle.sh csafrit2/steel-industry-energy-consumption
```

### Step 2: Clean the Dataset

**Always run the cleaning script before upload:**

```bash
python3 scripts/clean_dataset.py <input.csv> [-o <output.csv>]
```

**What the script does:**
- Strips whitespace from column names
- Removes duplicate rows
- Fills missing numeric values with median
- Fills missing categorical values with mode or 'Unknown'
- Converts timestamp columns to datetime format
- Outputs column summary for metadata configuration

**Output:**
- Cleaned CSV file ready for upload
- Column summary printed to console (save this for metadata config)

### Step 3: Upload Raw Dataset to Platform

1. Navigate to data.smlcrm.com/dashboard
2. Click **"Upload Dataset"** button
3. Fill in metadata for the RAW dataset:
   - **Name**: Descriptive dataset name
   - **Domain**: Category (Energy, Manufacturing, Climate, etc.)
   - **Source URL**: Kaggle or original source URL
   - **Description**: Brief summary of the dataset
4. Upload the **original/raw** CSV file (not cleaned yet)
5. Click **Upload**

**Result:** Dataset appears in list with **RAW** status

### Step 4: Upload Cleaned File & Configure Metadata

1. Find the RAW dataset in the list
2. Click **"Clean"** button
3. Upload the **cleaned** CSV file (from Step 2)
4. Configure headers for each column:

| Setting | Description |
|---------|-------------|
| **Name** | Column name (editable) |
| **Units** | Measurement units (kWh, °C, %, ratio, tCO2, etc.) |
| **Type** | Time / Target / Covariate / Group |

**Column Type Guide:**
- **Time**: Timestamp/datetime columns (usually required)
- **Target**: Variable to predict (at least one required)
- **Covariate**: Input features/independent variables
- **Group**: Categorical segment variables (WeekStatus, Day_of_week, Load_Type, etc.)

**Bulk Configuration:**
- Select multiple rows via checkboxes
- Use "Apply" dropdown to set type for selected columns
- Set units individually or in bulk

**Common Unit Patterns:**
- Energy: kWh, MWh, MW
- Power: kVarh, kW
- Emissions: tCO2, kgCO2
- Ratios: ratio, %
- Time: seconds, minutes, hours

### Step 5: Assign Groups to Variables

**Purpose:** Group variables define how data is segmented for analysis.

**Exact Workflow:**
1. **Select ALL variables** by checking their checkboxes:
   - Target variable(s)
   - ALL covariate variables
   
2. **Apply ALL group tags** to selected variables:
   - Click first group tag (e.g., WeekStatus) → all selected get this group
   - Click second group tag (e.g., Day_of_week) → all selected get this group
   - Click third group tag (e.g., Load_Type) → all selected get this group
   - Continue for all available group tags

3. **Result:** All variables have all groups assigned (e.g., "WeekStatus × Day_of_week × Load_Type")

**Important:** Assign groups to BOTH target variables AND all covariates.

### Step 6: Final Upload

1. Click **"Upload Cleaned Dataset"** button
2. Wait for processing
3. Dataset status changes from **RAW** → **CLEAN**
4. Verify data points count is correct

## Example: Steel Industry Energy Dataset

**Source:** https://www.kaggle.com/datasets/csafrit2/steel-industry-energy-consumption

**Metadata:**
- **Name:** Steel Industry Energy Consumption (South Korea)
- **Domain:** Energy
- **Data Points:** 350,400

**Column Configuration:**
| Column | Type | Units |
|--------|------|-------|
| Timestamps | Time | - |
| Usage_kWh | Target | kWh |
| Lagging_Current_Reactive.Power_kVarh | Covariate | kVarh |
| Leading_Current_Reactive_Power_kVarh | Covariate | kVarh |
| CO2(tCO2) | Covariate | tCO2 |
| Lagging_Current_Power_Factor | Covariate | ratio |
| Leading_Current_Power_Factor | Covariate | ratio |
| NSM | Covariate | seconds |
| WeekStatus | Group | - |
| Day_of_week | Group | - |
| Load_Type | Group | - |

**Group Assignment:**
1. Select: Usage_kWh, Lagging_Current_Reactive.Power_kVarh, Leading_Current_Reactive_Power_kVarh, CO2(tCO2), Lagging_Current_Power_Factor, Leading_Current_Power_Factor, NSM
2. Click: WeekStatus → all selected get WeekStatus
3. Click: Day_of_week → all selected get Day_of_week
4. Click: Load_Type → all selected get Load_Type
5. Final: All variables show "WeekStatus × Day_of_week × Load_Type"

## Reference Materials

For detailed platform configuration guidance, see [references/platform_guide.md](references/platform_guide.md).

## Troubleshooting

**"Next" button disabled:**
- Check at least one Time column is set
- Check at least one Target column is set
- Verify all columns have types assigned

**Groups not appearing:**
- Columns must be marked as "Group" type first
- Proceed to next step after setting Group types

**Upload fails:**
- Re-run cleaning script
- Check CSV format (comma-delimited)
- Verify no empty column names

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/clean_dataset.py` | Clean and prepare CSV for upload |
| `scripts/download_kaggle.sh` | Download datasets via Kaggle CLI |

## Platform URL

Data Annotation Platform: https://data.smlcrm.com
