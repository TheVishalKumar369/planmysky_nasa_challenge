# MERRA-2 Data Acquisition Guide

## Overview
The `data_acquisition_merra2.py` script downloads MERRA-2 reanalysis data from NASA Earthdata for any location and time period with memory-efficient batch processing and smart resume capabilities.

## Pipeline Workflow

### 🔐 **Authentication Setup**
**Function**: `authenticate()`
- Connects to NASA Earthdata using `.netrc` file (Windows: `_netrc`)
- Uses official `earthaccess` library for secure authentication
- Validates credentials before starting downloads
- **Required**: Free NASA Earthdata account at https://urs.earthdata.nasa.gov/

### 🎛️ **User Configuration**
**Function**: `get_user_input()`

#### **Location Setup**
- **Location Name**: Descriptive name (e.g., "Kathmandu, Nepal")
- **Coordinates**: Flexible input formats
  - Decimal: `27.7103`, `85.3222`
  - With Direction: `27.7103° N`, `85.3222° E`
  - Examples provided for major cities

#### **Time Range Selection**
- **Available Data**: 1980-01-01 to 2024-12-31 (full MERRA-2 coverage)
- **Default Range**: 1990-01-01 to 2024-12-31
- **Custom Periods**: Any valid date range within available data

#### **Processing Options**
| Batch Size | Memory Usage | Speed | Recommended For |
|------------|--------------|-------|-----------------|
| **3 years** | 4GB RAM | Slower | Older computers |
| **5 years** | 6GB RAM | Balanced | **Most users** |
| **10 years** | 12GB RAM | Faster | High-end systems |

### 🧭 **Coordinate Parsing**
**Function**: `_parse_coordinate(coord_str, coord_type)`

**Supported Formats**:
```
# Decimal degrees
27.7103
85.3222

# With direction indicators
27.7103° N
85.3222° E
27.7103°N (no space)
85.3222°E (no space)
```

**Smart Validation**:
- Latitude: -90° to +90° (N/S validation)
- Longitude: -180° to +180° (E/W validation)
- Direction enforcement (N/S for latitude, E/W for longitude)

## MERRA-2 Data Collections

### 📊 **Data Types Downloaded**
**Constant**: `MERRA2_COLLECTIONS`

| Collection | Variables | Description |
|------------|-----------|-------------|
| **M2T1NXSLV** | T2M, U10M, V10M, QV2M | Single-level diagnostics (temperature, wind, humidity) |
| **M2T1NXFLX** | PRECTOT, PRECSNO | Surface flux diagnostics (precipitation) |
| **M2T1NXRAD** | CLDTOT | Radiation diagnostics (cloud cover) |
| **M2T1NXAER** | TOTEXTTAU | Aerosol diagnostics (atmospheric particles) |

### 🌍 **Spatial Coverage**
- **Bounding Box**: 0.2° × 0.2° around target point
- **Global Availability**: Any location worldwide
- **Resolution**: 0.5° × 0.625° native MERRA-2 grid

## Data Search and Download

### 🔍 **Granule Search**
**Function**: `search_granules_for_collection(collection, start_date, end_date, lat, lon)`
- Creates bounding box around target coordinates
- Searches NASA's CMR (Common Metadata Repository)
- Returns list of available data granules
- Handles temporal and spatial filtering

### 📥 **Collection Acquisition**
**Function**: `acquire_collection_batch(collection, variables, start_date, end_date, lat, lon)`

**Process Flow**:
1. **Search**: Find all granules for the collection and time period
2. **Download**: Stream data directly from NASA servers
3. **Validation**: Verify NetCDF format (not HTML error pages)
4. **Variable Selection**: Extract only required variables
5. **Concatenation**: Combine all granules into single dataset
6. **Memory Management**: Clean up temporary data

### ✅ **Data Validation**
**Function**: `validate_netcdf_file(file_obj)`
- Checks file headers for NetCDF format
- Detects HTML error pages from server issues
- Ensures proper data structure before processing
- Returns boolean validation result

## Batch Processing System

### 📅 **Time Batch Creation**
**Function**: `create_time_batches(start_date, end_date, batch_size_years)`
- Splits large time ranges into manageable chunks
- Ensures memory-efficient processing
- Handles partial years at the end
- Returns list of (start_date, end_date) tuples

### 🔄 **Batch Data Acquisition**
**Function**: `acquire_batch_data(lat, lon, start_date, end_date, location_name, bbox_size)`

**For each batch**:
1. **Collection Loop**: Process all 4 MERRA-2 collections
2. **Error Handling**: Continue if individual collections fail
3. **Memory Management**: Clear datasets after processing
4. **Progress Reporting**: Log status for each collection

### 💾 **Data Storage**
**Function**: `save_raw_data(datasets, lat, lon, start_date, end_date, location_name)`

**File Naming Convention**:
```
merra2_raw_{location}_{lat}_{lon}_{start_year}_{end_year}.nc

Examples:
merra2_raw_kathmandu_nepal_27.7_85.3_1990_1994.nc
merra2_raw_kathmandu_nepal_27.7_85.3_1995_1999.nc
```

## Smart Resume Capabilities

### 🔍 **Existing File Detection**
**Function**: `check_existing_files(config)`
- Scans output directory for existing data files
- Compares expected vs. actual files
- Identifies missing batches that need downloading
- Returns list of missing batch information

### ♻️ **Resume Logic**
**Benefits**:
- **No Re-downloads**: Skips existing files automatically
- **User Choice**: Option to resume or start fresh
- **Progress Preservation**: Maintains completed work
- **Time Saving**: Only downloads missing data

**User Experience**:
```
📁 Found 3 existing files
📥 Need to download 2 missing batches

Resume from where download stopped? (Y/n): Y
Resuming download...
```

## Error Handling and Recovery

### 🛡️ **Interruption Scenarios**

| Scenario | Detection | Recovery Action |
|----------|-----------|-----------------|
| **User Interruption** (Ctrl+C) | KeyboardInterrupt | Graceful exit with progress report |
| **Network Failure** | Connection errors | Skip current batch, continue with next |
| **NASA Server Error** | HTTP errors | Log error, continue processing |
| **Disk Full** | Write errors | Stop with clear error message |
| **Memory Issues** | Memory errors | Reduce batch size recommendation |

### 🔄 **Automatic Recovery**
- **Partial Downloads**: Detected and re-attempted on next run
- **Corrupted Files**: Validation catches issues early
- **Network Timeouts**: Automatic retry with logging
- **Server Maintenance**: Graceful handling of temporary outages

## Main Workflow

### 🚀 **Complete Processing Flow**
**Function**: `run_acquisition()`

**Execution Steps**:
1. **Welcome**: Display project information
2. **Input**: Collect user configuration with validation
3. **Authentication**: Connect to NASA Earthdata
4. **Resume Check**: Detect existing files and missing batches
5. **Download**: Process missing batches with error handling
6. **Summary**: Report results and next steps

### 📊 **Progress Tracking**
```
📦 Downloading batch 1/5: 1990-01-01 to 1994-12-31
✅ Batch 1 completed successfully

📦 Downloading batch 2/5: 1995-01-01 to 1999-12-31
✅ Batch 2 completed successfully
```

### 🎯 **Completion Summary**
```
=============================================================
DATA ACQUISITION COMPLETED
=============================================================
✅ Successfully completed: 5/5 batches
📁 Files saved in: P:\PlanMySky\data\raw
📊 Total data files: 5
🎉 All data downloaded successfully!
💡 Next step: Run processing_merra2.py to convert to model-ready format
```

## Output Structure

### 📂 **File Organization**
```
data/raw/
├── merra2_raw_kathmandu_nepal_27.7_85.3_1990_1994.nc
├── merra2_raw_kathmandu_nepal_27.7_85.3_1995_1999.nc
├── merra2_raw_kathmandu_nepal_27.7_85.3_2000_2004.nc
├── merra2_raw_kathmandu_nepal_27.7_85.3_2005_2009.nc
└── merra2_raw_kathmandu_nepal_27.7_85.3_2010_2014.nc
```

### 📋 **Data Content**
Each NetCDF file contains:
- **Time Dimension**: Hourly/3-hourly timestamps
- **Spatial Dimensions**: lat, lon coordinates
- **Weather Variables**: All 8 MERRA-2 variables
- **Metadata**: Units, descriptions, source information
- **Quality Flags**: Data quality indicators

## System Requirements

### 💻 **Hardware Requirements**
| Batch Size | RAM Needed | Storage (per decade) | Network |
|------------|------------|---------------------|---------|
| 3 years | 4GB+ | ~2GB | Stable broadband |
| 5 years | 6GB+ | ~3GB | Stable broadband |
| 10 years | 12GB+ | ~5GB | Fast broadband |

### 🔧 **Software Dependencies**
```python
# Core scientific stack
import numpy as np
import xarray as xr
import earthaccess

# System utilities
from pathlib import Path
from datetime import datetime, timedelta
import logging
```

### 🌐 **NASA Account Setup**
1. **Registration**: Create free account at https://urs.earthdata.nasa.gov/
2. **Application Approval**: Approve applications for MERRA-2 data access
3. **Credentials File**: Create `.netrc` (Linux/Mac) or `_netrc` (Windows)

## Usage Example

### 📋 **Basic Usage**
```bash
cd src/acquisition
python data_acquisition_merra2.py
```

### 🎛️ **Interactive Session**
```
=============================================================
MERRA-2 DATA ACQUISITION SETUP
=============================================================

1. LOCATION INFORMATION
------------------------------
Enter location name (e.g., 'Kathmandu, Nepal'): Kathmandu, Nepal

Coordinate Input Options:
  Format 1: Decimal degrees (e.g., 27.7103 for latitude, 85.3222 for longitude)
  Format 2: With direction (e.g., 27.7103° N, 85.3222° E)
  Examples:
    - Kathmandu: 27.7103° N, 85.3222° E
    - New York: 40.7128° N, 74.0060° W
    - Sydney: 33.8688° S, 151.2093° E

Enter latitude (examples: 27.7103 or 27.7103° N): 27.7103° N
Enter longitude (examples: 85.3222 or 85.3222° E): 85.3222° E

2. TIME RANGE
------------------------------
Available data: 1980-01-01 to 2024-12-31
Enter start date (YYYY-MM-DD) [default: 1990-01-01]: 1990-01-01
Enter end date (YYYY-MM-DD) [default: 2024-12-31]: 2024-12-31

3. PROCESSING OPTIONS
------------------------------
Batch size controls memory usage:
  - 3 years: Low memory (4GB), slower
  - 5 years: Balanced (6GB), recommended
  - 10 years: High memory (12GB), faster
Enter batch size in years [default: 5]: 5
```

## Troubleshooting

### ❗ **Common Issues**

| Issue | Cause | Solution |
|-------|--------|----------|
| **Authentication Failed** | Missing/invalid `.netrc` | Create proper credentials file |
| **No Data Found** | Invalid coordinates | Check coordinate format and range |
| **Memory Error** | Batch size too large | Reduce batch size to 3 years |
| **Network Timeout** | Slow/unstable connection | Retry with stable internet |
| **Permission Error** | Write access denied | Check directory permissions |

### 🔧 **Performance Tips**
- **Optimal Batch Size**: Start with 5 years, adjust based on performance
- **Network Stability**: Use wired connection for large downloads
- **Disk Space**: Ensure adequate free space before starting
- **Background Apps**: Close memory-intensive applications during download

## Next Steps
After successful acquisition:
1. **Verify Files**: Check that all expected `.nc` files exist in `data/raw/`
2. **Run Processing**: Execute `processing_merra2.py` to convert to model-ready format
3. **Quality Check**: Review processing logs for any issues
4. **Analysis**: Begin using processed data for modeling and analysis

The acquisition system provides robust, resumable downloads of global MERRA-2 weather data for the PlanMySky project! 🌍🛰️