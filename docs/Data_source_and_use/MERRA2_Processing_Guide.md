# MERRA-2 Data Processing Guide

## Overview
The `processing_merra2.py` script converts raw MERRA-2 NetCDF files into model-ready datasets with cleaning, unit conversions, and aggregations.

## Pipeline Workflow

### 🔍 **Data Discovery**
**Function**: `find_raw_files()`
- Scans `data/raw/` directory for MERRA-2 files (`merra2_raw_*.nc`)
- Sorts files chronologically for proper processing order
- Returns list of file paths to process

### 🎛️ **User Configuration**
**Function**: `get_user_processing_options()`
- **Missing Value Handling**: Linear interpolation, forward fill, or keep NaN
- **Output Format**: Parquet (recommended), CSV, or both
- **Aggregation Options**: Optional monthly and yearly summaries
- Interactive prompts with validation and confirmation

### 📁 **File Loading**
**Function**: `load_raw_file(file_path)`
- Opens NetCDF files using xarray
- Validates file structure and dimensions
- Returns xarray Dataset for processing

## Data Transformation Pipeline

### 🔄 **Unit Conversions**
**Function**: `convert_units(ds)`

| Variable | From | To | Conversion |
|----------|------|-----|------------|
| Temperature (T2M) | Kelvin | Celsius | -273.15 |
| Precipitation (PRECTOT, PRECSNO) | kg/m²/s | mm/day | ×86400 |
| Cloud Cover (CLDTOT) | fraction | percentage | ×100 |

### 📊 **Daily Aggregation**
**Function**: `aggregate_to_daily(ds)`

| Variable Type | Aggregation Method | Output Variables |
|---------------|-------------------|-----------------|
| **Temperature** | Mean, Min, Max | `T2M_mean`, `T2M_min`, `T2M_max` |
| **Precipitation** | Daily Sum | `PRECTOT_mm`, `PRECSNO_mm` |
| **Other Variables** | Daily Mean | Original variable names |

### ⚙️ **Variable Derivation**
**Function**: `derive_secondary_variables(df)`
- **Wind Speed**: Calculates from U/V components: `√(U10M² + V10M²)`
- **Variable Renaming**: Standardizes column names for clarity
- **Quality Enhancements**: Improves data interpretability

### 🧹 **Missing Value Treatment**
**Function**: `handle_missing_values(df, method)`

| Method | Description | Use Case |
|--------|-------------|----------|
| **Linear Interpolation** | Fills gaps ≤2 days | Best for short data gaps |
| **Forward Fill** | Uses last valid value | Simple gap filling |
| **No Interpolation** | Keeps NaN values | Preserve data quality flags |

- Adds `missing_flag` column to track affected records
- Processes only numeric weather variables (excludes coordinates)

### 📝 **Metadata Enhancement**
**Function**: `add_metadata(df, file_info)`
- **Data Source**: Marks records as 'MERRA-2'
- **Source File**: Tracks original filename
- **Location Name**: Extracts location from filename
- **Date Column**: Standardizes time column to 'date'

## Aggregation Features

### 📅 **Monthly Aggregates**
**Function**: `create_monthly_aggregates(df)`
- **Temperature**: Monthly averages and extremes
- **Precipitation**: Monthly totals
- **Other Variables**: Monthly means
- **Output**: Separate monthly dataset file

### 📆 **Yearly Aggregates**
**Function**: `create_yearly_aggregates(df)`
- **Temperature**: Annual averages and extremes
- **Precipitation**: Annual totals
- **Other Variables**: Annual means
- **Output**: Separate yearly dataset file

## Data Export

### 💾 **File Output**
**Function**: `save_data(df, filename_base, output_format)`

| Format | Engine | Use Case |
|--------|--------|----------|
| **Parquet** | PyArrow | Fast analytics, compression |
| **CSV** | Pandas | Excel compatibility, human-readable |

### 📂 **Output Structure**
```
data/processed/
├── merra2_processed_kathmandu_nepal_27.7_85.3_1990_2024.parquet
├── merra2_processed_kathmandu_nepal_27.7_85.3_1990_2024_monthly.parquet
└── merra2_processed_kathmandu_nepal_27.7_85.3_1990_2024_yearly.parquet
```

## Processing Functions

### 🔄 **Single File Processing**
**Function**: `process_file(file_path, config)`
1. Load raw NetCDF file
2. Convert units to standard formats
3. Aggregate to daily resolution
4. Derive secondary variables
5. Handle missing values
6. Add metadata
7. Return processed DataFrame

### 🚀 **Main Workflow**
**Function**: `run_processing()`
1. **Discovery**: Find all raw files
2. **Configuration**: Get user preferences
3. **Processing**: Process each file sequentially
4. **Combination**: Merge all processed data
5. **Deduplication**: Remove duplicate records
6. **Export**: Save in requested format(s)
7. **Aggregation**: Create monthly/yearly summaries if requested

## Output Dataset Structure

### 📋 **Column Schema**
| Column | Type | Description |
|--------|------|-------------|
| `date` | datetime | Daily timestamp |
| `lat`, `lon` | float | Coordinates |
| `T2M_mean/min/max` | float | Temperature (°C) |
| `PRECTOT_mm` | float | Total precipitation (mm/day) |
| `SNOW_mm` | float | Snow precipitation (mm/day) |
| `WindSpeed` | float | Wind speed (m/s) |
| `CLDTOT_pct` | float | Cloud cover (%) |
| `QV2M` | float | Specific humidity |
| `AOD` | float | Aerosol optical depth |
| `missing_flag` | int | Missing data indicator (0/1) |
| `data_source` | string | Always 'MERRA-2' |
| `location_name` | string | Location identifier |

## Quality Control

### ✅ **Data Validation**
- **Duplicate Removal**: Based on date uniqueness
- **Missing Data Tracking**: Flags and counts missing values
- **Memory Management**: Clears datasets after processing
- **Error Handling**: Continues processing despite individual file failures

### 📊 **Summary Statistics**
- Records processed vs. total available
- Missing data percentage
- Date range coverage
- File locations and formats

## Usage Example

```bash
cd src/preprocessing
python processing_merra2.py
```

**Interactive Flow**:
1. Select missing value handling method
2. Choose output format(s)
3. Decide on aggregation levels
4. Confirm configuration
5. Automated processing of all files
6. Summary report with file locations

## Next Steps
After processing, your data is ready for:
- **Machine Learning**: Feature engineering and model training
- **Analysis**: Statistical analysis and visualization
- **Visualization**: Time series plots and geographic analysis
- **Modeling**: Weather prediction and climate studies

The processed datasets provide clean, consistent, model-ready weather data for the PlanMySky project!