# ERA5 Data Acquisition: Migration Experience & Problem-Solving Guide

**Project**: PlanMySky - NASA Space Apps Challenge
**Date**: September 30, 2025
**Task**: Migration from MERRA-2 to ERA5 dataset

---

## Overview

This document chronicles our experience migrating from NASA's MERRA-2 dataset to ECMWF's ERA5 reanalysis dataset, including all challenges encountered and solutions implemented.

---

## Key Differences: MERRA-2 vs ERA5

| Aspect | MERRA-2 | ERA5 |
|--------|---------|------|
| **Provider** | NASA EarthData | Copernicus Climate Data Store (CDS) |
| **Authentication** | Token-based (Bearer) | API key-based (.cdsapirc file) |
| **API Endpoint** | Direct HTTP requests | Python `cdsapi` library |
| **Data Format** | NetCDF4 (direct) | ZIP archive containing NetCDF files |
| **Spatial Resolution** | ~0.5° × 0.625° | ~0.25° × 0.25° (higher resolution) |
| **Temporal Resolution** | Hourly | Hourly (configurable) |
| **License** | Open access | Requires accepting Terms of Use |

---

## Problems Encountered & Solutions

### 1. **Authentication Configuration Issues**

#### Problem
```
Error: Climate Data Store API endpoint not found
```

**Root Cause**: Using outdated CDS API v2 endpoint and wrong API key format.

**Old Configuration** (Incorrect):
```
url: https://cds.climate.copernicus.eu/api/v2
key: de3047e3-e018-4905-af92-bf8d143e6b68:e99084e9-ddd5-4db9-bcda-5329c770261e
```

**Solution**: Updated to new CDS API endpoint and key format.

**New Configuration** (Correct):
```
url: https://cds.climate.copernicus.eu/api
key: e99084e9-ddd5-4db9-bcda-5329c770261e
```

**Code Changes** (`era5_acquisition.py:68-73`):
```python
# Create .cdsapirc file
with open(cdsapi_file, 'w') as f:
    f.write(f"url: https://cds.climate.copernicus.eu/api\n")  # Removed /v2
    f.write(f"key: {api_key}\n")  # Removed {uid}: prefix
```

---

### 2. **License/Terms of Use Not Accepted**

#### Problem
```
403 Client Error: Forbidden
required licences not accepted
```

**Root Cause**: ERA5 dataset requires explicit acceptance of Terms of Use before API access.

**Solution**:
1. Visit: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download
2. Navigate to "Download" tab
3. Scroll down and accept "Terms of Use" checkbox
4. No code changes needed - one-time manual step

---

### 3. **Windows-Incompatible Filenames**

#### Problem
From MERRA-2 experience: Filenames with dots (`.`) in coordinates caused issues on Windows filesystems.

**Example**: `era5_raw_kathmandu_nepal_27.7103_85.3222_2024_2024.nc`

**Solution**: Proactively replaced dots with underscores in coordinate strings.

**Code Changes** (`era5_acquisition.py:296-304`):
```python
# Convert coordinates to Windows-safe format (replace . with _)
lat_str = str(lat).replace('.', '_').replace('-', 'neg')
lon_str = str(lon).replace('.', '_').replace('-', 'neg')

if location_name:
    clean_name = location_name.lower().replace(' ', '_').replace(',', '').replace('.', '_')
    filename = f"era5_raw_{clean_name}_lat{lat_str}_lon{lon_str}_{start_year}_{end_year}.nc"
else:
    filename = f"era5_raw_lat{lat_str}_lon{lon_str}_{start_year}_{end_year}.nc"
```

**Result**: `era5_raw_kathmandu_nepal_lat27_7103_lon85_3222_2024_2024.nc`

---

### 4. **Credential Prompt Not Appearing**

#### Problem
Script didn't prompt for credentials when `.cdsapirc` file already existed (even with wrong format).

**Solution**: Enhanced credential setup with clearer instructions and removed UID prompt.

**Code Changes** (`era5_acquisition.py:58-76`):
```python
if not cdsapi_file.exists():
    print("\n" + "="*60)
    print("CDS API CREDENTIALS SETUP")
    print("="*60)
    print("CDS API credentials not found. Setting up...")
    print("\nPlease provide your Copernicus Climate Data Store credentials:")
    print("Get them from: https://cds.climate.copernicus.eu/user")
    print("\nNote: You need ONLY the API key (without UID prefix)")
    print("Example: e99084e9-ddd5-4db9-bcda-5329c770261e")

    api_key = input("\nEnter your API key: ").strip()
```

**User Action Required**: Delete old `.cdsapirc` to trigger re-setup:
```bash
rm ~/.cdsapirc
```

---

### 5. **Downloaded File Format Confusion**

#### Problem
```
OSError: [Errno -51] NetCDF: Unknown file format
```

**Root Cause**: CDS API downloads data as ZIP archives with `.nc` extension, not direct NetCDF files.

**Investigation**:
```bash
$ file era5_raw_kathmandu_nepal_lat27_7103_lon85_3222_2024_2024.nc
Zip archive data, at least v2.0 to extract
```

**Solution**: Created verification script that handles both ZIP and NetCDF formats.

**Code Changes** (`check_era5_data.py:28-48`):
```python
# Check if file is a zip archive
if zipfile.is_zipfile(latest_file):
    print("\nNote: File is a ZIP archive. Extracting...")
    with zipfile.ZipFile(latest_file, 'r') as zip_ref:
        nc_files = [f for f in zip_ref.namelist() if f.endswith('.nc')]
        print(f"Found {len(nc_files)} NetCDF file(s) in archive")

        # Extract to temp location
        tmpdir = tempfile.mkdtemp()
        for nc_file in nc_files:
            zip_ref.extract(nc_file, tmpdir)

        extracted_file = Path(tmpdir) / nc_files[0]

    # Open after zip is closed (prevents file lock issues)
    ds = xr.open_dataset(extracted_file, engine='netcdf4')
else:
    ds = xr.open_dataset(latest_file, engine='netcdf4')
```

---

### 6. **Variable Name Differences**

#### Problem
Time coordinate named `valid_time` instead of expected `time`, causing AttributeError.

**Error**:
```python
AttributeError: 'Dataset' object has no attribute 'time'
```

**Solution**: Dynamic detection of coordinate names.

**Code Changes** (`check_era5_data.py:72-74`):
```python
# Handle different time coordinate names
time_coord = 'valid_time' if 'valid_time' in ds.coords else 'time'
print(f"Time range: {pd.to_datetime(ds[time_coord].min().values)} to {pd.to_datetime(ds[time_coord].max().values)}")
```

---

### 7. **Missing Variables in Download**

#### Observation
Requested 8 variables but only received 5 in downloaded data.

**Requested**:
- `2m_temperature` → ✅ `t2m` (received)
- `total_precipitation` → ❌ (missing)
- `snowfall` → ❌ (missing)
- `10m_u_component_of_wind` → ✅ `u10` (received)
- `10m_v_component_of_wind` → ✅ `v10` (received)
- `specific_humidity` → ❌ (missing)
- `total_cloud_cover` → ✅ `tcc` (received)
- `total_column_ozone` → ✅ `tco3` (received)

**Explanation**: ERA5 data is split across two "streams":
- **Instant variables**: Temperature, wind, cloud cover (received)
- **Accumulated variables**: Precipitation, snowfall (in separate file or require different processing)

**Status**: Identified but not yet resolved. May need separate API calls for accumulated variables.

---

## Final Working Configuration

### File Structure
```
P:\PlanMySky\
├── data/
│   └── raw/
│       └── era5_raw_kathmandu_nepal_lat27_7103_lon85_3222_2024_2024.nc
├── src/
│   └── acquisition/
│       ├── era5_acquisition.py
│       └── check_era5_data.py
└── ~/.cdsapirc (credentials file)
```

### Verified Data Properties
- **File size**: 127 KB (compressed ZIP)
- **Timesteps**: 256 (8 times/day × 32 days)
- **Location**: 27.61°N, 85.22°E (Kathmandu, Nepal)
- **Time range**: 2024-01-01 00:00 to 2024-02-01 21:00
- **Variables**: 5 (t2m, u10, v10, tcc, tco3)
- **Missing values**: 0 (all data complete)

### Sample Data
```
valid_time           latitude  longitude  t2m       u10       v10       tcc       tco3
2024-01-01 00:00:00  27.61     85.223     282.62    -0.63     -0.47     0.898     0.0061
2024-01-01 03:00:00  27.61     85.223     282.92    -0.48     -0.35     0.597     0.0062
2024-01-01 06:00:00  27.61     85.223     288.01     0.95      1.19     0.004     0.0062
```

---

## Lessons Learned

1. **Always check API documentation for latest endpoints** - API v2 → API v1 transition caught us off guard
2. **Windows filename compatibility** - Proactive handling saved debugging time
3. **CDS downloads are ZIP files** - Despite `.nc` extension, they're compressed archives
4. **License acceptance is mandatory** - Can't be bypassed via API
5. **Variable naming varies by dataset** - `time` vs `valid_time`, `T2M` vs `t2m`
6. **File handle management matters** - Must close ZIP before accessing extracted files on Windows
7. **ERA5 data comes in multiple streams** - Instant vs accumulated variables need different handling

---

## Next Steps

1. ✅ Data acquisition working
2. ✅ Data verification script complete
3. ⏳ Handle missing precipitation/snowfall variables
4. ⏳ Create `era5_processing.py` to convert to model-ready format
5. ⏳ Update preprocessing pipeline to match ERA5 variable names

---

## Useful Resources

- **ERA5 Documentation**: https://confluence.ecmwf.int/display/CKB/ERA5
- **CDS API Python Library**: https://pypi.org/project/cdsapi/
- **ERA5 Variables List**: https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels
- **Get API Key**: https://cds.climate.copernicus.eu/user
- **Accept License**: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download#manage-licences

---

*Document created by PlanMySky Team - September 2025*