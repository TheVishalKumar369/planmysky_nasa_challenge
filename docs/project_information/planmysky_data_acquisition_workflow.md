# PlanMySky – MERRA-2 Data Acquisition & Processing  
**NASA Space Apps Challenge**

## Project Overview
We acquire **MERRA-2 reanalysis data** for Kathmandu, Nepal (27.7°N, 85.3°E), spanning **1990–2024**, generating **model-ready datasets** for weather prediction.

---

## Tools
- **Python 3.10+**
- `earthaccess`
- `xarray`
- `pandas`
- `pyarrow`
- `numpy`
- Optional: `dask` for large-scale data handling

---

## Workflow

### Acquisition
- Authenticate via **.netrc** or environment variables
- Search granules by **collection, variable, date, and location**
- **Download in time-based batches** to manage RAM effectively

### Processing
- Convert **NetCDF → daily Parquet files**
- **Spatial subsetting**, **unit conversion**, aggregation
- Derive secondary variables (e.g., wind speed)
- Handle missing data via **linear interpolation**
- Add **metadata**
- Save **incremental Parquet files per batch**, then merge for final dataset

### Memory Management
- Lazy loading of NetCDF datasets
- Batch processing of granules
- Process **one location at a time**
- Capable of handling **30+ years of data** on a standard laptop

---

## Outcome
- **Clean, high-quality, daily-aggregated datasets**
- Ready for **statistical modeling**, **machine learning**, or **API integration**

---

## Notes
- Acquisition and processing are **modular**, ensuring:
  - Reproducibility
  - Scalability
  - Efficient RAM usage
