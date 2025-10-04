#!/usr/bin/env python3
"""
ERA5 Data Acquisition
Downloads ERA5 reanalysis data from Copernicus Climate Data Store for specific locations.

Author: PlanMySky Team
"""

import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import cdsapi
import xarray as xr

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ERA5DataAcquisition:
    """
    ERA5 data acquisition with efficient point extraction and user interaction.
    """

    # ERA5 Variables mapping - Optimized for rainfall prediction model
    # Split into core (must-have) and optional (accuracy boost) variables
    ERA5_VARIABLES_CORE = [
        'total_precipitation',           # tp - Target variable
        '2m_temperature',                # t2m - Daily mean/min/max
        '10m_u_component_of_wind',       # u10 - Wind speed calculation
        '10m_v_component_of_wind',       # v10 - Wind speed calculation
        'total_cloud_cover',             # tcc - Cloud coverage
    ]

    ERA5_VARIABLES_OPTIONAL = [
        '2m_dewpoint_temperature',       # d2m - Relative humidity
        'mean_sea_level_pressure',       # msl - Fronts/storms
        'total_column_water_vapour',     # tcwv - Moisture availability
        'surface_solar_radiation_downwards',  # ssrd - Solar energy
    ]

    # Variable name mapping for output
    VARIABLE_MAPPING = {
        'total_precipitation': 'PRECTOT',
        '2m_temperature': 'T2M',
        '2m_dewpoint_temperature': 'D2M',
        '10m_u_component_of_wind': 'U10M',
        '10m_v_component_of_wind': 'V10M',
        'total_cloud_cover': 'CLDTOT',
        'mean_sea_level_pressure': 'MSL',
        'total_column_water_vapour': 'TCWV',
        'surface_solar_radiation_downwards': 'SSRD'
    }

    def __init__(self, output_dir: str = "../../data/raw", batch_size_years: int = 3):
        """Initialize ERA5 data acquisition handler."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.batch_size_years = batch_size_years
        self.client = None
        self.include_optional = True  # Can be configured by user
        self.location_folder = None  # Will be set based on location name

    def setup_cds_api(self) -> bool:
        """Setup CDS API client with user credentials."""
        try:
            # Check for existing .cdsapirc file
            cdsapi_file = Path.home() / '.cdsapirc'

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

                # Create .cdsapirc file
                with open(cdsapi_file, 'w') as f:
                    f.write(f"url: https://cds.climate.copernicus.eu/api\n")
                    f.write(f"key: {api_key}\n")

                print(f"\nCredentials saved to {cdsapi_file}")
                print("="*60)

            # Initialize CDS API client
            self.client = cdsapi.Client()
            logger.info("CDS API client initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Error setting up CDS API: {e}")
            return False

    def _parse_coordinate(self, coord_str: str, coord_type: str) -> float:
        """Parse coordinate string in various formats."""
        import re

        coord_str = coord_str.strip().upper()
        coord_str = coord_str.replace('°', ' ').replace(',', '').strip()

        # Pattern for decimal with optional direction
        decimal_pattern = r'^([+-]?\d+\.?\d*)\s*([NSEW]?)$'
        match = re.match(decimal_pattern, coord_str)

        if match:
            value = float(match.group(1))
            direction = match.group(2)

            if direction:
                if coord_type == 'latitude':
                    if direction == 'S':
                        value = -abs(value)
                    elif direction == 'N':
                        value = abs(value)
                    elif direction in ['E', 'W']:
                        raise ValueError(f"Invalid direction '{direction}' for latitude (use N or S)")
                elif coord_type == 'longitude':
                    if direction == 'W':
                        value = -abs(value)
                    elif direction == 'E':
                        value = abs(value)
                    elif direction in ['N', 'S']:
                        raise ValueError(f"Invalid direction '{direction}' for longitude (use E or W)")

            return value

        try:
            return float(coord_str.split()[0])
        except:
            raise ValueError("Please use format like '27.7103' or '27.7103° N'")

    def get_user_input(self) -> Optional[Dict]:
        """Get user configuration for ERA5 data acquisition."""
        print("="*60)
        print("ERA5 DATA ACQUISITION SETUP")
        print("="*60)

        try:
            # Location input
            print("\n1. LOCATION INFORMATION")
            print("-" * 30)

            location_name = input("Enter location name (e.g., 'Kathmandu, Nepal'): ").strip()
            if not location_name:
                location_name = "Unknown Location"

            print("\nCoordinate Input Options:")
            print("  Format 1: Decimal degrees (e.g., 27.7103 for latitude, 85.3222 for longitude)")
            print("  Format 2: With direction (e.g., 27.7103° N, 85.3222° E)")
            print("  Examples:")
            print("    - Kathmandu: 27.7103° N, 85.3222° E")
            print("    - New York: 40.7128° N, 74.0060° W")
            print("    - Sydney: 33.8688° S, 151.2093° E")

            while True:
                try:
                    lat_input = input("\nEnter latitude (examples: 27.7103 or 27.7103° N): ").strip()
                    lat = self._parse_coordinate(lat_input, 'latitude')
                    if -90 <= lat <= 90:
                        break
                    else:
                        print("Latitude must be between -90 and 90 degrees")
                except ValueError as e:
                    print(f"Invalid latitude format: {e}")
                    print("Please use decimal format (27.7103) or with direction (27.7103° N)")

            while True:
                try:
                    lon_input = input("Enter longitude (examples: 85.3222 or 85.3222° E): ").strip()
                    lon = self._parse_coordinate(lon_input, 'longitude')
                    if -180 <= lon <= 180:
                        break
                    else:
                        print("Longitude must be between -180 and 180 degrees")
                except ValueError as e:
                    print(f"Invalid longitude format: {e}")
                    print("Please use decimal format (85.3222) or with direction (85.3222° E)")

            # Coverage area selection
            print("\n2. COVERAGE AREA")
            print("-" * 30)
            print("Select area size to download around your location:")
            print("  1. Small city (55 km × 55 km)")
            print("     Examples: Kathmandu, Pokhara, small towns")
            print("  2. Medium city (111 km × 111 km)")
            print("     Examples: Delhi NCR, Boston, mid-size metros")
            print("  3. Large metro (222 km × 222 km)")
            print("     Examples: NYC, Tokyo, Mumbai, Los Angeles")
            print("  4. Custom (specify coverage in km)")

            while True:
                coverage_choice = input("\nSelect coverage [1-4, default: 1]: ").strip()
                if not coverage_choice or coverage_choice == '1':
                    coverage_km = 55
                    print(f"✓ Selected: Small city (55 km × 55 km)")
                    break
                elif coverage_choice == '2':
                    coverage_km = 111
                    print(f"✓ Selected: Medium city (111 km × 111 km)")
                    break
                elif coverage_choice == '3':
                    coverage_km = 222
                    print(f"✓ Selected: Large metro (222 km × 222 km)")
                    break
                elif coverage_choice == '4':
                    while True:
                        try:
                            coverage_km = int(input("Enter coverage area in km (25-500): ").strip())
                            if 25 <= coverage_km <= 500:
                                print(f"✓ Selected: Custom ({coverage_km} km × {coverage_km} km)")
                                break
                            else:
                                print("Please enter a value between 25 and 500 km")
                        except ValueError:
                            print("Please enter a valid number")
                    break
                else:
                    print("Please select 1, 2, 3, or 4")

            # Time range input
            print("\n3. TIME RANGE")
            print("-" * 30)
            print("Available data: 1940-01-01 to present")

            while True:
                try:
                    start_date = input("Enter start date (YYYY-MM-DD) [default: 1990-01-01]: ").strip()
                    if not start_date:
                        start_date = "1990-01-01"
                    datetime.strptime(start_date, '%Y-%m-%d')
                    break
                except ValueError:
                    print("Please enter date in YYYY-MM-DD format")

            while True:
                try:
                    end_date = input("Enter end date (YYYY-MM-DD) [default: 2024-12-31]: ").strip()
                    if not end_date:
                        end_date = "2024-12-31"
                    datetime.strptime(end_date, '%Y-%m-%d')
                    break
                except ValueError:
                    print("Please enter date in YYYY-MM-DD format")

            # Batch size input
            print("\n3. PROCESSING OPTIONS")
            print("-" * 30)
            print("Batch size controls download chunks:")
            print("  - 1 year: Smallest batches, safest for quota limits")
            print("  - 3 years: Small batches, good for quota limits")
            print("  - 5 years: Medium batches (recommended)")
            print("  - 10+ years: May exceed quota limits")
            print("\nNote: CDS has strict quota limits. Start with smaller batches!")

            while True:
                try:
                    batch_input = input("Enter batch size in years [default: 3]: ").strip()
                    if not batch_input:
                        batch_years = 3
                    else:
                        batch_years = int(batch_input)
                        if batch_years < 1 or batch_years > 30:
                            print("Batch size must be between 1 and 30 years")
                            continue
                    break
                except ValueError:
                    print("Please enter a valid number")

            # Variable selection
            print("\n4. VARIABLE SELECTION")
            print("-" * 30)
            print("Core variables (always included):")
            for var in self.ERA5_VARIABLES_CORE:
                print(f"  - {var}")

            print("\nOptional variables (improve model accuracy):")
            for var in self.ERA5_VARIABLES_OPTIONAL:
                print(f"  - {var}")

            include_optional = input("\nInclude optional variables? (Y/n): ").strip().lower()
            self.include_optional = include_optional not in ['n', 'no']

            # Confirmation
            print("\n" + "="*60)
            print("CONFIGURATION SUMMARY")
            print("="*60)
            print(f"Location: {location_name}")
            print(f"Coordinates: {lat:.3f}°N, {lon:.3f}°E")
            print(f"Time range: {start_date} to {end_date}")
            print(f"Batch size: {batch_years} years")

            # Variable selection
            num_vars = len(self.ERA5_VARIABLES_CORE)
            if self.include_optional:
                num_vars += len(self.ERA5_VARIABLES_OPTIONAL)
            print(f"Variables: {num_vars} ({'core + optional' if self.include_optional else 'core only'})")

            # Calculate time span
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            years = (end_dt - start_dt).days / 365.25
            estimated_batches = int(np.ceil(years / batch_years))

            print(f"Time span: {years:.1f} years")
            print(f"Number of batches: {estimated_batches}")

            # More accurate size estimation
            size_per_batch = 5 if not self.include_optional else 10
            print(f"Estimated file size: {estimated_batches * size_per_batch:.1f} - {estimated_batches * size_per_batch * 2:.1f} MB total")
            print(f"\nNote: Batching helps avoid CDS quota limits")

            confirm = input("\nProceed with this configuration? (y/N): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("Configuration cancelled.")
                return None

            return {
                'location_name': location_name,
                'lat': lat,
                'lon': lon,
                'coverage_km': coverage_km,
                'start_date': start_date,
                'end_date': end_date,
                'batch_size_years': batch_years,
                'include_optional': self.include_optional
            }

        except KeyboardInterrupt:
            print("\nSetup cancelled by user.")
            return None
        except Exception as e:
            logger.error(f"Error getting user input: {e}")
            return None

    def create_time_batches(self, start_date: str, end_date: str, batch_size_years: int) -> List[Tuple[str, str]]:
        """Create time batches for processing."""
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')

            batches = []
            current_dt = start_dt

            while current_dt < end_dt:
                batch_end = min(
                    current_dt + timedelta(days=batch_size_years * 365),
                    end_dt
                )

                batches.append((
                    current_dt.strftime('%Y-%m-%d'),
                    batch_end.strftime('%Y-%m-%d')
                ))

                current_dt = batch_end

            logger.info(f"Created {len(batches)} time batches")
            return batches

        except Exception as e:
            logger.error(f"Error creating time batches: {e}")
            return []

    def download_era5_data(self, lat: float, lon: float, start_date: str, end_date: str,
                          location_name: str = None, coverage_km: int = 55) -> Optional[str]:
        """Download ERA5 data for specific point and time range."""
        try:
            # Generate filename (Windows-compatible: replace dots in coordinates)
            start_year = start_date.split('-')[0]
            end_year = end_date.split('-')[0]

            # Convert coordinates to Windows-safe format (replace . with _)
            lat_str = str(lat).replace('.', '_').replace('-', 'neg')
            lon_str = str(lon).replace('.', '_').replace('-', 'neg')

            # Create location-specific folder
            if location_name:
                clean_name = location_name.lower().replace(' ', '_').replace(',', '').replace('.', '_')
                self.location_folder = self.output_dir / clean_name
            else:
                self.location_folder = self.output_dir / f"lat{lat_str}_lon{lon_str}"

            self.location_folder.mkdir(parents=True, exist_ok=True)

            # Simplified filename (location info is in folder name)
            filename = f"era5_raw_{start_year}_{end_year}.nc"
            output_path = self.location_folder / filename

            # Check if file already exists
            if output_path.exists():
                logger.info(f"File already exists: {filename}")
                return str(output_path)

            logger.info(f"Downloading ERA5 data: {start_date} to {end_date}")
            logger.info(f"Location: {lat:.3f}°N, {lon:.3f}°E")

            # Calculate bounding box based on coverage area
            # Convert km to degrees (approximate: 1° ≈ 111 km)
            margin = (coverage_km / 111.0) / 2  # Divide by 2 because margin is radius
            area = [lat + margin, lon - margin, lat - margin, lon + margin]  # North, West, South, East

            logger.info(f"Coverage area: ~{coverage_km} km × {coverage_km} km (±{margin:.3f}° margin)")

            # Select variables based on user choice
            variables = self.ERA5_VARIABLES_CORE.copy()
            if self.include_optional:
                variables.extend(self.ERA5_VARIABLES_OPTIONAL)

            # ERA5 request - minimized for quota limits
            # Use only 2 times per day to reduce request size
            request = {
                'product_type': 'reanalysis',
                'variable': variables,
                'date': f'{start_date}/{end_date}',
                'time': [
                    '00:00', '12:00'  # 2 times/day minimum for daily aggregation
                ],
                'area': area,
                'format': 'netcdf',
            }

            logger.info(f"Requesting {len(variables)} variables, 2 times per day")
            logger.info(f"Request size: ~{len(variables) * 2} data points per day")

            # Download using CDS API
            self.client.retrieve('reanalysis-era5-single-levels', request, str(output_path))

            if output_path.exists():
                file_size_mb = output_path.stat().st_size / (1024 * 1024)
                logger.info(f"ERA5 data downloaded: {filename} ({file_size_mb:.1f} MB)")

                # Save metadata about this download
                metadata = {
                    'location_name': location_name,
                    'latitude': lat,
                    'longitude': lon,
                    'coverage_km': coverage_km,
                    'coverage_area': {
                        'north': lat + margin,
                        'south': lat - margin,
                        'west': lon - margin,
                        'east': lon + margin,
                        'margin_degrees': margin
                    },
                    'start_date': start_date,
                    'end_date': end_date,
                    'download_date': datetime.now().isoformat(),
                    'file_size_mb': file_size_mb,
                    'variables': self.ERA5_VARIABLES_CORE + (self.ERA5_VARIABLES_OPTIONAL if self.include_optional else [])
                }

                import json
                metadata_path = self.location_folder / 'metadata.json'
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)

                return str(output_path)
            else:
                logger.error("Download completed but file not found")
                return None

        except Exception as e:
            logger.error(f"Error downloading ERA5 data: {e}")
            return None

    def check_existing_files(self, config: Dict) -> List[Dict]:
        """Check for existing files and return list of missing batches."""
        try:
            start_dt = datetime.strptime(config['start_date'], '%Y-%m-%d')
            end_dt = datetime.strptime(config['end_date'], '%Y-%m-%d')

            # Determine location folder
            location_name = config.get('location_name', '')
            if location_name:
                clean_name = location_name.lower().replace(' ', '_').replace(',', '').replace('.', '_')
                location_folder = self.output_dir / clean_name
            else:
                lat_str = str(config['lat']).replace('.', '_').replace('-', 'neg')
                lon_str = str(config['lon']).replace('.', '_').replace('-', 'neg')
                location_folder = self.output_dir / f"lat{lat_str}_lon{lon_str}"

            missing_batches = []
            current_dt = start_dt

            while current_dt < end_dt:
                batch_end = min(
                    current_dt + timedelta(days=config['batch_size_years'] * 365),
                    end_dt
                )

                # Simplified filename
                filename = f"era5_raw_{current_dt.year}_{batch_end.year}.nc"
                file_path = location_folder / filename

                if not file_path.exists():
                    missing_batches.append({
                        'start_date': current_dt.strftime('%Y-%m-%d'),
                        'end_date': batch_end.strftime('%Y-%m-%d'),
                        'filename': filename
                    })
                else:
                    logger.info(f"Found existing file: {filename}")

                current_dt = batch_end

            return missing_batches

        except Exception as e:
            logger.error(f"Error checking existing files: {e}")
            return []

    def run_acquisition(self) -> bool:
        """Main acquisition workflow with resume capability."""
        try:
            print("ERA5 Data Acquisition Pipeline")
            print("NASA Space Apps Challenge - PlanMySky Project")

            # Setup CDS API
            if not self.setup_cds_api():
                logger.error("Failed to setup CDS API")
                return False

            # Get user configuration
            config = self.get_user_input()
            if not config:
                return False

            # Update batch size from user input
            self.batch_size_years = config['batch_size_years']

            # Check for existing files and resume capability
            missing_batches = self.check_existing_files(config)

            if not missing_batches:
                print("\n" + "="*60)
                print("ALL DATA ALREADY DOWNLOADED")
                print("="*60)
                print("All required files are already present in the data directory.")
                print("If you want to re-download, delete the existing files first.")
                return True

            # Determine location folder
            location_name = config.get('location_name', '')
            if location_name:
                clean_name = location_name.lower().replace(' ', '_').replace(',', '').replace('.', '_')
                location_folder = self.output_dir / clean_name
            else:
                lat_str = str(config['lat']).replace('.', '_').replace('-', 'neg')
                lon_str = str(config['lon']).replace('.', '_').replace('-', 'neg')
                location_folder = self.output_dir / f"lat{lat_str}_lon{lon_str}"

            existing_files = list(location_folder.glob('*.nc')) if location_folder.exists() else []
            print(f"\nFound {len(existing_files)} existing files in {location_folder.name}/")
            print(f"Need to download {len(missing_batches)} missing batches")

            # Ask user about resuming
            if len(existing_files) > 0:
                resume = input("\nResume from where download stopped? (Y/n): ").strip().lower()
                if resume == 'n':
                    print("Starting fresh download...")
                else:
                    print("Resuming download...")

            # Process missing batches only
            all_files = []
            successful_batches = 0

            for batch_num, batch_info in enumerate(missing_batches, 1):
                batch_start = batch_info['start_date']
                batch_end = batch_info['end_date']

                logger.info(f"\nProcessing Batch {batch_num}/{len(missing_batches)}: {batch_start} to {batch_end}")
                print(f"Downloading batch {batch_num}/{len(missing_batches)}: {batch_start} to {batch_end}")

                try:
                    # Download batch data
                    file_path = self.download_era5_data(
                        lat=config['lat'],
                        lon=config['lon'],
                        start_date=batch_start,
                        end_date=batch_end,
                        location_name=config['location_name'],
                        coverage_km=config.get('coverage_km', 55)  # Default to 55 km if not specified
                    )

                    if file_path:
                        all_files.append(file_path)
                        successful_batches += 1
                        print(f"Batch {batch_num} completed successfully")
                    else:
                        print(f"Failed to download batch {batch_num}")

                except KeyboardInterrupt:
                    print(f"\nDownload interrupted by user during batch {batch_num}")
                    print(f"Progress: {successful_batches}/{len(missing_batches)} batches completed")
                    print("You can resume later by running the script again - it will continue from where it stopped!")
                    return successful_batches > 0

                except Exception as e:
                    logger.error(f"Error processing batch {batch_num}: {e}")
                    print(f"Error in batch {batch_num}: {e}")
                    print("Continuing with next batch...")
                    continue

            # Summary
            print("\n" + "="*60)
            print("DATA ACQUISITION COMPLETED")
            print("="*60)
            print(f"Successfully completed: {successful_batches}/{len(missing_batches)} batches")
            print(f"Files saved in: {location_folder}")

            # List all files
            all_nc_files = list(location_folder.glob('*.nc')) if location_folder.exists() else []
            print(f"Total data files for this location: {len(all_nc_files)}")

            if successful_batches == len(missing_batches):
                print("All data downloaded successfully!")
                print("Next step: Run era5_processing.py to convert to model-ready format")
            else:
                print("WARNING: Some batches failed. You can re-run this script to retry missing data.")

            logger.info(f"Data acquisition complete! {successful_batches}/{len(missing_batches)} batches successful")

            return successful_batches > 0

        except Exception as e:
            logger.error(f"Error in acquisition workflow: {e}")
            return False


def main():
    """Main execution function."""
    processor = ERA5DataAcquisition()
    success = processor.run_acquisition()

    if success:
        print("\nData acquisition completed successfully!")
        print("Your ERA5 dataset is ready for processing.")
    else:
        print("\nData acquisition failed. Check logs for details.")


if __name__ == "__main__":
    main()