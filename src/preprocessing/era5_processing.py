#!/usr/bin/env python3
"""
ERA5 Data Processing
Cleans, processes, and converts raw ERA5 data to model-ready Parquet format.

Author: PlanMySky Team
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import xarray as xr
import pyarrow as pa
import pyarrow.parquet as pq
import zipfile
import tempfile
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ERA5DataProcessor:
    """
    Complete ERA5 data processing with cleaning, aggregation, and export.
    """

    # ERA5 to standard variable name mapping - Updated for all new variables
    VARIABLE_MAPPING = {
        # Temperature & Humidity
        't2m': 'T2M',
        'd2m': 'D2M',

        # Precipitation
        'tp': 'PRECTOT',
        'sf': 'PRECSNO',

        # Wind
        'u10': 'U10M',
        'v10': 'V10M',

        # Pressure
        'sp': 'PS',
        'msl': 'MSL',

        # Clouds & Radiation
        'tcc': 'CLDTOT',
        'ssrd': 'SSRD',
        'strd': 'STRD',

        # Additional
        'e': 'EVAP',
        'tcwv': 'TCWV',
        'tco3': 'TCO3'
    }

    def __init__(self, raw_data_dir: str = "../../data/raw", output_dir: str = "../../data/processed"):
        """Initialize data processor."""
        self.raw_data_dir = Path(raw_data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.location_name = None  # Will be determined from raw data

    def get_available_locations(self) -> List[Path]:
        """Get all location folders in raw data directory."""
        try:
            # Find all subdirectories in raw data dir
            locations = [d for d in self.raw_data_dir.iterdir() if d.is_dir()]
            return locations
        except Exception as e:
            logger.error(f"Error finding locations: {e}")
            return []

    def find_raw_files(self, location_folder: Path = None) -> List[str]:
        """Find all raw ERA5 NetCDF files for a specific location."""
        try:
            if location_folder is None:
                # Legacy: search in root directory
                pattern = "era5_raw_*.nc"
                raw_files = list(self.raw_data_dir.glob(pattern))
            else:
                # New: search in location-specific folder
                pattern = "era5_raw_*.nc"
                raw_files = list(location_folder.glob(pattern))

            raw_files.sort()

            logger.info(f"Found {len(raw_files)} raw data files")
            for i, file in enumerate(raw_files, 1):
                logger.info(f"  {i}. {file.name}")

            return [str(f) for f in raw_files]

        except Exception as e:
            logger.error(f"Error finding raw files: {e}")
            return []

    def get_user_processing_options(self) -> Dict:
        """Get processing options from user."""
        print("="*60)
        print("ERA5 DATA PROCESSING SETUP")
        print("="*60)

        try:
            # Processing options
            print("\n1. PROCESSING OPTIONS")
            print("-" * 30)

            print("Missing value handling:")
            print("  1. Linear interpolation (≤2 days gaps)")
            print("  2. Forward fill (simple)")
            print("  3. No interpolation (keep NaN)")

            while True:
                try:
                    choice = input("Select missing value method [1-3, default: 1]: ").strip()
                    if not choice:
                        missing_method = 1
                    else:
                        missing_method = int(choice)
                        if missing_method not in [1, 2, 3]:
                            print("Please select 1, 2, or 3")
                            continue
                    break
                except ValueError:
                    print("Please enter a valid number")

            # Output format
            print("\n2. OUTPUT FORMAT")
            print("-" * 30)
            print("Choose output format:")
            print("  1. Parquet (recommended for analysis)")
            print("  2. CSV (for Excel/spreadsheet)")
            print("  3. Both formats")

            while True:
                try:
                    choice = input("Select output format [1-3, default: 1]: ").strip()
                    if not choice:
                        output_format = 1
                    else:
                        output_format = int(choice)
                        if output_format not in [1, 2, 3]:
                            print("Please select 1, 2, or 3")
                            continue
                    break
                except ValueError:
                    print("Please enter a valid number")

            # Aggregation options
            print("\n3. AGGREGATION OPTIONS")
            print("-" * 30)
            print("Additional aggregations (optional):")

            monthly = input("Create monthly aggregates? (y/N): ").strip().lower() in ['y', 'yes']
            yearly = input("Create yearly aggregates? (y/N): ").strip().lower() in ['y', 'yes']

            # Confirmation
            print("\n" + "="*60)
            print("PROCESSING CONFIGURATION")
            print("="*60)

            missing_methods = {
                1: "Linear interpolation (≤2 days)",
                2: "Forward fill",
                3: "No interpolation"
            }
            output_formats = {
                1: "Parquet only",
                2: "CSV only",
                3: "Both Parquet and CSV"
            }

            print(f"Missing value method: {missing_methods[missing_method]}")
            print(f"Output format: {output_formats[output_format]}")
            print(f"Monthly aggregates: {'Yes' if monthly else 'No'}")
            print(f"Yearly aggregates: {'Yes' if yearly else 'No'}")

            confirm = input("\nProceed with this configuration? (y/N): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("Processing cancelled.")
                return None

            return {
                'missing_method': missing_method,
                'output_format': output_format,
                'monthly_aggregates': monthly,
                'yearly_aggregates': yearly
            }

        except KeyboardInterrupt:
            print("\nProcessing setup cancelled by user.")
            return None
        except Exception as e:
            logger.error(f"Error getting processing options: {e}")
            return None

    def load_raw_file(self, file_path: str) -> Optional[xr.Dataset]:
        """Load a raw NetCDF file (handles ZIP archives)."""
        tmpdir = None
        try:
            logger.info(f"Loading: {Path(file_path).name}")

            # Check if file is a ZIP archive
            if zipfile.is_zipfile(file_path):
                logger.info("File is a ZIP archive, extracting...")
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    nc_files = [f for f in zip_ref.namelist() if f.endswith('.nc')]

                    if not nc_files:
                        logger.error("No .nc files found in ZIP archive")
                        return None

                    logger.info(f"Found {len(nc_files)} NetCDF file(s) in archive")

                    # Extract to temp location
                    tmpdir = tempfile.mkdtemp()
                    for nc_file in nc_files:
                        zip_ref.extract(nc_file, tmpdir)

                    # Load all NetCDF files and merge
                    datasets = []
                    for nc_file in nc_files:
                        extracted_file = Path(tmpdir) / nc_file
                        ds_temp = xr.open_dataset(extracted_file, engine='netcdf4')
                        datasets.append(ds_temp)

                    # Merge datasets if multiple
                    if len(datasets) > 1:
                        logger.info(f"Merging {len(datasets)} datasets...")
                        ds = xr.merge(datasets, compat='override')
                    else:
                        ds = datasets[0]
            else:
                # Load directly as NetCDF
                ds = xr.open_dataset(file_path, engine='netcdf4')

            # Standardize time coordinate name
            if 'valid_time' in ds.coords:
                ds = ds.rename({'valid_time': 'time'})

            logger.info(f"Loaded dataset - dimensions: {dict(ds.dims)}")
            logger.info(f"Variables: {list(ds.data_vars)}")

            # Store tmpdir reference for cleanup
            if tmpdir:
                ds.attrs['_tmpdir'] = tmpdir

            return ds

        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            if tmpdir:
                shutil.rmtree(tmpdir, ignore_errors=True)
            return None

    def convert_units(self, ds: xr.Dataset) -> xr.Dataset:
        """Convert ERA5 units to standard formats."""
        try:
            ds_converted = ds.copy()

            # Temperature: Kelvin to Celsius
            for temp_var in ['t2m', 'd2m']:
                if temp_var in ds_converted:
                    ds_converted[temp_var] = ds_converted[temp_var] - 273.15
                    ds_converted[temp_var].attrs['units'] = 'degrees_C'

            # Precipitation & Evaporation: m to mm (multiply by 1000)
            for var in ['tp', 'sf', 'e']:
                if var in ds_converted:
                    ds_converted[var] = ds_converted[var] * 1000  # m to mm
                    ds_converted[var].attrs['units'] = 'mm'

            # Pressure: Pa to hPa
            for pres_var in ['sp', 'msl']:
                if pres_var in ds_converted:
                    ds_converted[pres_var] = ds_converted[pres_var] / 100  # Pa to hPa
                    ds_converted[pres_var].attrs['units'] = 'hPa'

            # Cloud cover: fraction to percentage
            if 'tcc' in ds_converted:
                ds_converted['tcc'] = ds_converted['tcc'] * 100
                ds_converted['tcc'].attrs['units'] = 'percent'

            # Radiation: J/m² to W/m² (divide by time step in seconds)
            # Assuming 3-hour time steps = 10800 seconds
            for rad_var in ['ssrd', 'strd']:
                if rad_var in ds_converted:
                    ds_converted[rad_var] = ds_converted[rad_var] / 10800  # J/m² to W/m²
                    ds_converted[rad_var].attrs['units'] = 'W/m²'

            # Ozone: kg/m² to Dobson units
            if 'tco3' in ds_converted:
                ds_converted['tco3'] = ds_converted['tco3'] * 2.144e-5 * 1000  # to Dobson units
                ds_converted['tco3'].attrs['units'] = 'DU'

            logger.info("Unit conversions complete")
            return ds_converted

        except Exception as e:
            logger.error(f"Error in unit conversion: {e}")
            return ds

    def aggregate_to_daily(self, ds: xr.Dataset) -> pd.DataFrame:
        """Aggregate 3-hourly ERA5 data to daily resolution."""
        try:
            logger.info("Starting daily aggregation...")

            # Resample to daily
            daily_data = {}

            for var in ds.data_vars:
                var_data = ds[var]

                if var == 't2m':
                    # Temperature: daily mean, min, max
                    daily_data['T2M_mean'] = var_data.resample(time='D').mean()
                    daily_data['T2M_min'] = var_data.resample(time='D').min()
                    daily_data['T2M_max'] = var_data.resample(time='D').max()
                elif var in ['tp', 'sf']:
                    # Precipitation: daily sum
                    if var == 'tp':
                        daily_data['PRECTOT_mm'] = var_data.resample(time='D').sum()
                    else:
                        daily_data['SNOW_mm'] = var_data.resample(time='D').sum()
                elif var == 'tcc':
                    daily_data['CLDTOT_pct'] = var_data.resample(time='D').mean()
                else:
                    # Other variables: daily mean
                    standard_name = self.VARIABLE_MAPPING.get(var, var.upper())
                    daily_data[standard_name] = var_data.resample(time='D').mean()

            # Convert to DataFrame
            df_list = []
            for var_name, data_array in daily_data.items():
                df_var = data_array.to_dataframe().reset_index()
                df_var = df_var.rename(columns={data_array.name: var_name})

                # Handle coordinates
                if 'latitude' in df_var.columns:
                    df_var = df_var.rename(columns={'latitude': 'lat'})
                if 'longitude' in df_var.columns:
                    df_var = df_var.rename(columns={'longitude': 'lon'})

                coord_cols = ['time']
                if 'lat' in df_var.columns:
                    coord_cols.append('lat')
                if 'lon' in df_var.columns:
                    coord_cols.append('lon')

                df_var = df_var[coord_cols + [var_name]]
                df_list.append(df_var)

            # Merge all variables
            if not df_list:
                logger.error("No data arrays to merge")
                return pd.DataFrame()

            df_daily = df_list[0]
            for df_var in df_list[1:]:
                merge_cols = ['time']
                if 'lat' in df_var.columns and 'lat' in df_daily.columns:
                    merge_cols.append('lat')
                if 'lon' in df_var.columns and 'lon' in df_daily.columns:
                    merge_cols.append('lon')

                df_daily = df_daily.merge(df_var, on=merge_cols, how='outer')

            logger.info(f"Daily aggregation complete - {df_daily.shape[0]} days")
            return df_daily

        except Exception as e:
            logger.error(f"Error in daily aggregation: {e}")
            return pd.DataFrame()

    def derive_secondary_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """Derive secondary variables like wind speed."""
        try:
            df_derived = df.copy()

            # Wind speed from U and V components
            if 'U10M' in df_derived.columns and 'V10M' in df_derived.columns:
                df_derived['WindSpeed'] = np.sqrt(df_derived['U10M']**2 + df_derived['V10M']**2)
                logger.info("Derived wind speed from U/V components")

            logger.info("Variable derivation complete")
            return df_derived

        except Exception as e:
            logger.error(f"Error in variable derivation: {e}")
            return df

    def handle_missing_values(self, df: pd.DataFrame, method: int = 1) -> pd.DataFrame:
        """Handle missing values based on user choice."""
        try:
            df_filled = df.copy()

            # Sort by time
            df_filled = df_filled.sort_values('time').reset_index(drop=True)

            # Get numeric columns (exclude coordinates)
            numeric_cols = df_filled.select_dtypes(include=[np.number]).columns
            excluded_cols = ['lat', 'lon']
            process_cols = [col for col in numeric_cols if col not in excluded_cols]

            if method == 1:  # Linear interpolation
                logger.info("Applying linear interpolation for gaps ≤2 days")
                for col in process_cols:
                    df_filled[col] = df_filled[col].interpolate(method='linear', limit=2)

            elif method == 2:  # Forward fill
                logger.info("Applying forward fill for missing values")
                for col in process_cols:
                    df_filled[col] = df_filled[col].fillna(method='ffill')

            elif method == 3:  # No interpolation
                logger.info("Keeping missing values as NaN")
                pass

            # Add missing data flag
            missing_mask = df_filled[process_cols].isnull().any(axis=1)
            df_filled['missing_flag'] = missing_mask.astype(int)

            total_missing = df_filled['missing_flag'].sum()
            logger.info(f"Missing value handling complete - {total_missing} rows flagged")

            return df_filled

        except Exception as e:
            logger.error(f"Error in missing value handling: {e}")
            return df

    def add_metadata(self, df: pd.DataFrame, file_info: str = None) -> pd.DataFrame:
        """Add metadata columns."""
        try:
            df_meta = df.copy()

            # Add metadata
            df_meta['data_source'] = 'ERA5'
            df_meta['source_file'] = file_info or 'processed_era5_data'

            # Extract location name if available
            if file_info and 'era5_raw_' in file_info:
                try:
                    parts = Path(file_info).stem.split('_')
                    if len(parts) >= 4:
                        location_part = '_'.join(parts[2:-4])
                        df_meta['location_name'] = location_part.replace('_', ' ').title()
                except:
                    pass

            # Rename time column to date
            df_meta = df_meta.rename(columns={'time': 'date'})

            logger.info("Metadata addition complete")
            return df_meta

        except Exception as e:
            logger.error(f"Error adding metadata: {e}")
            return df

    def create_monthly_aggregates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create monthly aggregates."""
        try:
            logger.info("Creating monthly aggregates...")

            df_monthly = df.copy()
            df_monthly['date'] = pd.to_datetime(df_monthly['date'])
            df_monthly = df_monthly.set_index('date')

            # Group by month and aggregate
            monthly_agg = {}

            # Temperature - average the daily means, keep extremes
            if 'T2M_mean' in df_monthly.columns:
                monthly_agg['T2M_mean'] = df_monthly['T2M_mean'].resample('M').mean()
            if 'T2M_min' in df_monthly.columns:
                monthly_agg['T2M_min'] = df_monthly['T2M_min'].resample('M').min()
            if 'T2M_max' in df_monthly.columns:
                monthly_agg['T2M_max'] = df_monthly['T2M_max'].resample('M').max()

            # Precipitation - sum
            for col in ['PRECTOT_mm', 'SNOW_mm']:
                if col in df_monthly.columns:
                    monthly_agg[col] = df_monthly[col].resample('M').sum()

            # Other variables - mean
            other_vars = ['U10M', 'V10M', 'WindSpeed', 'CLDTOT_pct', 'QV2M', 'TCO3']
            for col in other_vars:
                if col in df_monthly.columns:
                    monthly_agg[col] = df_monthly[col].resample('M').mean()

            # Combine results
            df_monthly_result = pd.DataFrame(monthly_agg).reset_index()

            # Add coordinates and metadata
            if 'lat' in df.columns:
                df_monthly_result['lat'] = df['lat'].iloc[0]
            if 'lon' in df.columns:
                df_monthly_result['lon'] = df['lon'].iloc[0]

            # Copy metadata
            for col in ['data_source', 'source_file', 'location_name']:
                if col in df.columns:
                    df_monthly_result[col] = df[col].iloc[0]

            df_monthly_result['aggregation_level'] = 'monthly'

            logger.info(f"Monthly aggregates created - {df_monthly_result.shape[0]} months")
            return df_monthly_result

        except Exception as e:
            logger.error(f"Error creating monthly aggregates: {e}")
            return pd.DataFrame()

    def create_yearly_aggregates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create yearly aggregates."""
        try:
            logger.info("Creating yearly aggregates...")

            df_yearly = df.copy()
            df_yearly['date'] = pd.to_datetime(df_yearly['date'])
            df_yearly = df_yearly.set_index('date')

            # Group by year and aggregate
            yearly_agg = {}

            # Temperature - average the daily means, keep extremes
            if 'T2M_mean' in df_yearly.columns:
                yearly_agg['T2M_mean'] = df_yearly['T2M_mean'].resample('Y').mean()
            if 'T2M_min' in df_yearly.columns:
                yearly_agg['T2M_min'] = df_yearly['T2M_min'].resample('Y').min()
            if 'T2M_max' in df_yearly.columns:
                yearly_agg['T2M_max'] = df_yearly['T2M_max'].resample('Y').max()

            # Precipitation - sum
            for col in ['PRECTOT_mm', 'SNOW_mm']:
                if col in df_yearly.columns:
                    yearly_agg[col] = df_yearly[col].resample('Y').sum()

            # Other variables - mean
            other_vars = ['U10M', 'V10M', 'WindSpeed', 'CLDTOT_pct', 'QV2M', 'TCO3']
            for col in other_vars:
                if col in df_yearly.columns:
                    yearly_agg[col] = df_yearly[col].resample('Y').mean()

            # Combine results
            df_yearly_result = pd.DataFrame(yearly_agg).reset_index()

            # Add coordinates and metadata
            if 'lat' in df.columns:
                df_yearly_result['lat'] = df['lat'].iloc[0]
            if 'lon' in df.columns:
                df_yearly_result['lon'] = df['lon'].iloc[0]

            # Copy metadata
            for col in ['data_source', 'source_file', 'location_name']:
                if col in df.columns:
                    df_yearly_result[col] = df[col].iloc[0]

            df_yearly_result['aggregation_level'] = 'yearly'

            logger.info(f"Yearly aggregates created - {df_yearly_result.shape[0]} years")
            return df_yearly_result

        except Exception as e:
            logger.error(f"Error creating yearly aggregates: {e}")
            return pd.DataFrame()

    def save_data(self, df: pd.DataFrame, filename_base: str, output_format: int = 1, location_folder: Path = None):
        """Save data in requested format(s)."""
        try:
            # Determine output directory
            if location_folder:
                output_location_dir = self.output_dir / location_folder.name
                output_location_dir.mkdir(parents=True, exist_ok=True)
            else:
                output_location_dir = self.output_dir

            if output_format in [1, 3]:  # Parquet
                parquet_file = output_location_dir / f"{filename_base}.parquet"
                df.to_parquet(parquet_file, engine='pyarrow', index=False)
                logger.info(f"Saved Parquet: {parquet_file}")

            if output_format in [2, 3]:  # CSV
                csv_file = output_location_dir / f"{filename_base}.csv"
                df.to_csv(csv_file, index=False)
                logger.info(f"Saved CSV: {csv_file}")

        except Exception as e:
            logger.error(f"Error saving data: {e}")

    def process_file(self, file_path: str, config: Dict) -> Optional[pd.DataFrame]:
        """Process a single raw file."""
        tmpdir = None
        try:
            # Load raw data
            ds = self.load_raw_file(file_path)
            if ds is None:
                return None

            # Get tmpdir for cleanup
            tmpdir = ds.attrs.get('_tmpdir')

            # Convert units
            ds = self.convert_units(ds)

            # Daily aggregation
            df_daily = self.aggregate_to_daily(ds)
            if df_daily.empty:
                logger.error("Daily aggregation resulted in empty dataframe")
                return None

            # Close dataset to release file handles
            ds.close()

            # Derive secondary variables
            df_derived = self.derive_secondary_variables(df_daily)

            # Handle missing values
            df_clean = self.handle_missing_values(df_derived, config['missing_method'])

            # Add metadata
            df_final = self.add_metadata(df_clean, file_path)

            logger.info(f"File processing complete - {df_final.shape[0]} records")

            # Cleanup temp directory
            if tmpdir:
                shutil.rmtree(tmpdir, ignore_errors=True)

            return df_final

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            if tmpdir:
                shutil.rmtree(tmpdir, ignore_errors=True)
            return None

    def run_processing(self) -> bool:
        """Main processing workflow."""
        try:
            print("ERA5 Data Processing Pipeline")
            print("NASA Space Apps Challenge - PlanMySky Project")

            # Find available locations
            locations = self.get_available_locations()

            if not locations:
                # Check for legacy files in root directory
                logger.info("Checking for legacy files in root directory...")
                raw_files = self.find_raw_files(None)
                if not raw_files:
                    logger.error("No raw data files found. Run era5_acquisition.py first.")
                    return False
                location_folder = None
            else:
                # Show available locations
                print("\n" + "="*60)
                print("AVAILABLE LOCATIONS")
                print("="*60)
                for i, loc in enumerate(locations, 1):
                    # Try to load metadata
                    metadata_path = loc / 'metadata.json'
                    if metadata_path.exists():
                        import json
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                        loc_name = metadata.get('location_name', loc.name)
                        print(f"  {i}. {loc_name} ({loc.name})")
                    else:
                        print(f"  {i}. {loc.name}")

                # Select location
                if len(locations) == 1:
                    location_folder = locations[0]
                    print(f"\nProcessing location: {location_folder.name}")
                else:
                    while True:
                        try:
                            choice = input(f"\nSelect location to process [1-{len(locations)}]: ").strip()
                            idx = int(choice) - 1
                            if 0 <= idx < len(locations):
                                location_folder = locations[idx]
                                break
                            else:
                                print(f"Please enter a number between 1 and {len(locations)}")
                        except ValueError:
                            print("Please enter a valid number")

                # Find raw files in selected location
                raw_files = self.find_raw_files(location_folder)
                if not raw_files:
                    logger.error(f"No raw data files found in {location_folder}")
                    return False

            # Get processing configuration
            config = self.get_user_processing_options()
            if not config:
                return False

            # Process each file
            all_dataframes = []
            successful_files = 0

            for i, file_path in enumerate(raw_files, 1):
                logger.info(f"\nProcessing file {i}/{len(raw_files)}: {Path(file_path).name}")

                df = self.process_file(file_path, config)
                if df is not None:
                    all_dataframes.append(df)
                    successful_files += 1

            if not all_dataframes:
                logger.error("No files were successfully processed")
                return False

            # Combine all data
            logger.info("Combining all processed data...")
            df_combined = pd.concat(all_dataframes, ignore_index=True)
            df_combined = df_combined.sort_values('date').reset_index(drop=True)

            # Remove duplicates
            initial_records = len(df_combined)
            df_combined = df_combined.drop_duplicates(subset=['date'], keep='first')
            final_records = len(df_combined)

            if initial_records != final_records:
                logger.info(f"Removed {initial_records - final_records} duplicate records")

            # Generate output filename
            location_name = df_combined.get('location_name', pd.Series(['unknown'])).iloc[0]
            if isinstance(location_name, str):
                clean_name = location_name.lower().replace(' ', '_').replace(',', '')
            else:
                clean_name = "unknown_location"

            lat = df_combined['lat'].iloc[0] if 'lat' in df_combined.columns else 0
            lon = df_combined['lon'].iloc[0] if 'lon' in df_combined.columns else 0

            start_date = df_combined['date'].min()
            end_date = df_combined['date'].max()
            start_year = pd.to_datetime(start_date).year
            end_year = pd.to_datetime(end_date).year

            # Simplified filename (location info is in folder)
            filename_base = f"era5_processed_{start_year}_{end_year}"

            # Save main dataset
            self.save_data(df_combined, filename_base, config['output_format'], location_folder)

            # Create aggregates if requested
            if config['monthly_aggregates']:
                df_monthly = self.create_monthly_aggregates(df_combined)
                if not df_monthly.empty:
                    monthly_filename = f"era5_processed_{start_year}_{end_year}_monthly"
                    self.save_data(df_monthly, monthly_filename, config['output_format'], location_folder)

            if config['yearly_aggregates']:
                df_yearly = self.create_yearly_aggregates(df_combined)
                if not df_yearly.empty:
                    yearly_filename = f"era5_processed_{start_year}_{end_year}_yearly"
                    self.save_data(df_yearly, yearly_filename, config['output_format'], location_folder)

            # Determine output location
            if location_folder:
                output_location_dir = self.output_dir / location_folder.name
            else:
                output_location_dir = self.output_dir

            # Summary
            print("\n" + "="*60)
            print("DATA PROCESSING COMPLETED")
            print("="*60)
            print(f"Location: {clean_name}")
            print(f"Processed files: {successful_files}/{len(raw_files)}")
            print(f"Total records: {final_records:,}")
            print(f"Date range: {start_date} to {end_date}")
            print(f"Missing data: {df_combined['missing_flag'].sum()} days")
            print(f"Output location: {output_location_dir}")
            print("\nDataset ready for analysis and modeling!")

            return True

        except Exception as e:
            logger.error(f"Error in processing workflow: {e}")
            return False


def main():
    """Main execution function."""
    processor = ERA5DataProcessor()
    success = processor.run_processing()

    if success:
        print("\nData processing completed successfully!")
        print("Your ERA5 dataset is ready for analysis.")
    else:
        print("\nData processing failed. Check logs for details.")


if __name__ == "__main__":
    main()