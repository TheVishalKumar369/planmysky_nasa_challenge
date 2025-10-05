# PlanMySky – NASA Earthdata Authentication & MERRA-2 Data Acquisition Lesson

## Project Context
During initial data acquisition for Kathmandu, Nepal (1990–2024), we encountered repeated **401 Unauthorized errors** due to improper NASA Earthdata authentication.

---

## Mistake
- Attempting downloads **without correctly setting up authentication credentials**.
- NetCDF files returned **HTML error pages** instead of actual data.

---

## Solution Implemented
1. **.netrc file:** Created a proper `.netrc` (Windows: `_netrc`) with credentials for `urs.earthdata.nasa.gov`.
2. **Environment variables fallback:** `EARTHDATA_USERNAME` and `EARTHDATA_PASSWORD` used if `.netrc` failed.
3. **Interactive login:** Final fallback to authenticate directly via `earthaccess`.
4. **Validation:** Each downloaded file checked for proper NetCDF format to ensure **no HTML error pages** were processed.

---

## Result
- Successful acquisition of MERRA-2 NetCDF files.
- Files are now ready for preprocessing (subsetting, unit conversion, aggregation, metadata addition) into **Parquet format**.
- High-quality datasets prepared for modeling.

---

## Key Takeaways
- Always **verify authentication** before large-scale downloads.
- **Validate downloaded files** to prevent propagating errors downstream.
- Modular authentication logic ensures **reproducibility and scalability** for multiple locations and long time spans.
