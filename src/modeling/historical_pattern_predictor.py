#!/usr/bin/env python3
"""
Historical Pattern-Based Weather Predictor
Analyzes 30+ years of historical data to predict weather for any date

When user selects a date (e.g., July 15):
- Find all July 15th occurrences in historical data (1990-2024)
- Calculate statistics and probabilities
- Show what typically happens on that date

Author: PlanMySky Team
NASA Space Apps Challenge
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HistoricalWeatherPredictor:
    """
    Predict weather based on historical patterns for the same date across years.
    """

    def __init__(self, data_dir: str = None, location_name: str = None):
        if data_dir:
            self.data_dir = Path(data_dir).resolve()
        else:
            # Resolve relative to project root (3 levels up from api file)
            self.data_dir = Path(__file__).resolve(
            ).parent.parent.parent / "data" / "processed"

        self.df = None
        self.location_name = location_name or "Unknown"
        self.location_folder = None

    def load_historical_data(self):
        """Load all available processed data."""
        try:
            # If location specified, look in location folder
            if self.location_name and self.location_name != "Unknown":
                clean_name = self.location_name.lower().replace(
                    ' ', '_').replace(',', '').replace('.', '_')
                self.location_folder = self.data_dir / clean_name

                if self.location_folder.exists():
                    # Try parquet first (faster)
                    parquet_files = list(self.location_folder.glob(
                        "era5_processed_*.parquet"))
                    if parquet_files:
                        logger.info(f"Loading {parquet_files[0].name}...")
                        # Only load necessary columns for faster loading
                        columns_needed = ['date', 'T2M_mean', 'T2M_min', 'T2M_max',
                                        'PRECTOT_mm', 'WindSpeed', 'CLDTOT_pct',
                                        'D2M', 'MSL', 'SSRD', 'location_name']
                        self.df = pd.read_parquet(parquet_files[0], columns=columns_needed)
                    else:
                        # Fall back to CSV
                        csv_files = list(self.location_folder.glob(
                            "era5_processed_*.csv"))
                        if csv_files:
                            logger.info(f"Loading {csv_files[0].name}...")
                            columns_needed = ['date', 'T2M_mean', 'T2M_min', 'T2M_max',
                                            'PRECTOT_mm', 'WindSpeed', 'CLDTOT_pct',
                                            'D2M', 'MSL', 'SSRD', 'location_name']
                            self.df = pd.read_csv(csv_files[0], usecols=columns_needed)
                        else:
                            raise FileNotFoundError(
                                f"No processed data files found in {self.location_folder}")
                else:
                    raise FileNotFoundError(
                        f"Location folder not found: {self.location_folder}")
            else:
                # Legacy: search in root directory
                parquet_files = list(self.data_dir.glob(
                    "era5_processed_*.parquet"))
                if parquet_files:
                    logger.info(f"Loading {parquet_files[0].name}...")
                    # Only load necessary columns for faster loading
                    columns_needed = ['date', 'T2M_mean', 'T2M_min', 'T2M_max',
                                    'PRECTOT_mm', 'WindSpeed', 'CLDTOT_pct',
                                    'D2M', 'MSL', 'SSRD', 'location_name']
                    self.df = pd.read_parquet(parquet_files[0], columns=columns_needed)
                else:
                    # Fall back to CSV
                    csv_files = list(self.data_dir.glob(
                        "era5_processed_*.csv"))
                    if csv_files:
                        logger.info(f"Loading {csv_files[0].name}...")
                        columns_needed = ['date', 'T2M_mean', 'T2M_min', 'T2M_max',
                                        'PRECTOT_mm', 'WindSpeed', 'CLDTOT_pct',
                                        'D2M', 'MSL', 'SSRD', 'location_name']
                        self.df = pd.read_csv(csv_files[0], usecols=columns_needed)
                    else:
                        raise FileNotFoundError(
                            "No processed data files found")

            # Convert date to datetime with fast path
            self.df['date'] = pd.to_datetime(self.df['date'], format='ISO8601', cache=True)

            # Extract temporal features using optimized vectorized operations
            dates = self.df['date'].dt
            self.df['month'] = dates.month.astype('int8')  # Smaller dtype
            self.df['day'] = dates.day.astype('int8')
            self.df['year'] = dates.year.astype('int16')
            self.df['day_of_year'] = dates.dayofyear.astype('int16')

            # Get location name
            if 'location_name' in self.df.columns:
                self.location_name = self.df['location_name'].iloc[0]

            logger.info(f"Loaded {len(self.df)} days of historical data")
            logger.info(
                f"Date range: {self.df['date'].min()} to {self.df['date'].max()}")
            logger.info(f"Location: {self.location_name}")

            return True

        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False

    def predict_for_date(self, target_month: int, target_day: int,
                         window_days: int = 7) -> Dict:
        """
        Predict weather for a specific date based on historical patterns.

        Args:
            target_month: Month (1-12)
            target_day: Day (1-31)
            window_days: Include dates within ±N days (default 7 for weekly context)

        Returns:
            Dictionary with predictions and historical statistics
        """
        try:
            # Calculate next future occurrence of this date
            from datetime import datetime
            today = datetime.now()
            current_year = today.year

            # Try this year first
            try:
                future_date = datetime(current_year, target_month, target_day)
                # If date already passed this year, use next year
                if future_date.date() < today.date():
                    future_date = datetime(
                        current_year + 1, target_month, target_day)
            except ValueError:
                # Invalid date (e.g., Feb 30), use next year
                future_date = datetime(
                    current_year + 1, target_month, target_day)

            future_date_str = future_date.strftime('%Y-%m-%d')

            # Find all historical occurrences of this date (±window)
            target_date = pd.Timestamp(
                year=2000, month=target_month, day=target_day)
            target_doy = target_date.dayofyear

            # Filter: same month and day (±window)
            matches = self.df[
                (self.df['month'] == target_month) &
                (abs(self.df['day'] - target_day) <= window_days)
            ].copy()

            if len(matches) == 0:
                return {"error": "No historical data found for this date"}

            n_years = matches['year'].nunique()
            logger.info(
                f"Found {len(matches)} historical records across {n_years} years")

            # ===== RAINFALL ANALYSIS =====
            # Rain occurrence (days with >0.1mm rain)
            rainy_days = (matches['PRECTOT_mm'] > 0.1).sum()
            total_days = len(matches)
            rain_probability = rainy_days / total_days

            # Rainfall amount statistics
            rainfall_mean = float(matches['PRECTOT_mm'].mean())
            rainfall_median = float(matches['PRECTOT_mm'].median())
            rainfall_max = float(matches['PRECTOT_mm'].max())
            rainfall_std = float(matches['PRECTOT_mm'].std())

            # Rain intensity categories
            light_rain = ((matches['PRECTOT_mm'] > 0.1) & (
                matches['PRECTOT_mm'] <= 2.5)).sum()
            moderate_rain = ((matches['PRECTOT_mm'] > 2.5) & (
                matches['PRECTOT_mm'] <= 10)).sum()
            heavy_rain = (matches['PRECTOT_mm'] > 10).sum()

            # ===== TEMPERATURE ANALYSIS =====
            temp_mean_avg = float(matches['T2M_mean'].mean())
            temp_mean_std = float(matches['T2M_mean'].std())
            temp_min_avg = float(matches['T2M_min'].mean())
            temp_max_avg = float(matches['T2M_max'].mean())

            temp_min_record = float(matches['T2M_min'].min())
            temp_max_record = float(matches['T2M_max'].max())

            # ===== WIND ANALYSIS =====
            wind_mean = float(matches['WindSpeed'].mean())
            wind_max = float(matches['WindSpeed'].max())
            wind_std = float(matches['WindSpeed'].std())

            # ===== CLOUD COVER ANALYSIS =====
            cloud_mean = float(matches['CLDTOT_pct'].mean())
            cloud_std = float(matches['CLDTOT_pct'].std())

            # Clear/cloudy day probability
            clear_days = (matches['CLDTOT_pct'] < 30).sum()
            cloudy_days = (matches['CLDTOT_pct'] > 70).sum()

            # ===== ADDITIONAL FEATURES =====
            humidity_mean = float(
                matches['D2M'].mean()) if 'D2M' in matches.columns else None
            pressure_mean = float(
                matches['MSL'].mean()) if 'MSL' in matches.columns else None
            solar_mean = float(matches['SSRD'].mean(
            )) if 'SSRD' in matches.columns else None

            # ===== WEATHER CATEGORY =====
            if rain_probability > 0.6:
                weather_category = "Rainy"
                category_confidence = rain_probability
            elif cloud_mean > 60:
                weather_category = "Cloudy"
                category_confidence = cloud_mean / 100
            else:
                weather_category = "Clear"
                category_confidence = (100 - cloud_mean) / 100

            # ===== EXTREME WEATHER PROBABILITIES =====
            prob_temp_above_30 = (matches['T2M_max'] > 30).sum() / total_days
            prob_temp_below_10 = (matches['T2M_min'] < 10).sum() / total_days
            prob_heavy_rain = heavy_rain / total_days
            prob_high_wind = (matches['WindSpeed'] > 5).sum() / total_days

            # ===== HISTORICAL YEARS DATA =====
            yearly_summary = matches.groupby('year').agg({
                'PRECTOT_mm': 'sum',
                'T2M_mean': 'mean',
                'WindSpeed': 'mean',
                'CLDTOT_pct': 'mean'
            }).round(2).to_dict('index')

            # ===== BUILD RESULT =====
            # Get data range for metadata
            data_start_year = int(self.df['year'].min())
            data_end_year = int(self.df['year'].max())

            result = {
                # Metadata
                # Next future occurrence (e.g., "2026-07-15")
                "date": future_date_str,
                # For reference
                "month_day": f"{target_month:02d}-{target_day:02d}",
                "location": self.location_name,
                "prediction_type": "historical_pattern",
                "based_on_data_range": f"{data_start_year}-{data_end_year}",
                "historical_years_analyzed": int(n_years),
                "total_observations": int(total_days),

                # Rainfall Prediction
                "rainfall": {
                    "probability": round(rain_probability, 3),
                    "probability_percent": round(rain_probability * 100, 1),
                    "expected_amount_mm": round(rainfall_mean, 2),
                    "median_amount_mm": round(rainfall_median, 2),
                    "max_recorded_mm": round(rainfall_max, 2),
                    "std_deviation_mm": round(rainfall_std, 2),
                    "intensity_distribution": {
                        "light_rain_days": int(light_rain),
                        "moderate_rain_days": int(moderate_rain),
                        "heavy_rain_days": int(heavy_rain),
                        "no_rain_days": int(total_days - rainy_days)
                    }
                },

                # Temperature Prediction
                "temperature": {
                    "mean_avg_celsius": round(temp_mean_avg, 1),
                    "mean_std_celsius": round(temp_mean_std, 1),
                    "expected_range": {
                        "min": round(temp_min_avg, 1),
                        "max": round(temp_max_avg, 1)
                    },
                    "record_low_celsius": round(temp_min_record, 1),
                    "record_high_celsius": round(temp_max_record, 1)
                },

                # Wind Prediction
                "wind": {
                    "mean_speed_ms": round(wind_mean, 1),
                    "max_recorded_ms": round(wind_max, 1),
                    "std_deviation_ms": round(wind_std, 1)
                },

                # Cloud Cover
                "cloud_cover": {
                    "mean_percent": round(cloud_mean, 1),
                    "std_percent": round(cloud_std, 1),
                    "clear_days_percent": round((clear_days / total_days) * 100, 1),
                    "cloudy_days_percent": round((cloudy_days / total_days) * 100, 1)
                },

                # Weather Category
                "weather_category": weather_category,
                "category_confidence": round(category_confidence, 2),

                # Extreme Weather Probabilities
                "extreme_probabilities": {
                    "temp_above_30C": round(prob_temp_above_30, 3),
                    "temp_below_10C": round(prob_temp_below_10, 3),
                    "heavy_rain_above_10mm": round(prob_heavy_rain, 3),
                    "high_wind_above_5ms": round(prob_high_wind, 3)
                },

                # Additional Info
                "additional": {
                    "humidity_celsius": round(humidity_mean, 1) if humidity_mean else None,
                    "pressure_hpa": round(pressure_mean, 1) if pressure_mean else None,
                    "solar_radiation_wm2": round(solar_mean, 1) if solar_mean else None
                },

                # Yearly breakdown (last 10 years)
                "recent_years": {
                    str(year): {
                        "rainfall_mm": float(data['PRECTOT_mm']),
                        "temp_celsius": float(data['T2M_mean']),
                        "wind_ms": float(data['WindSpeed']),
                        "cloud_pct": float(data['CLDTOT_pct'])
                    }
                    for year, data in list(yearly_summary.items())[-10:]
                }
            }

            return result

        except Exception as e:
            logger.error(
                f"Error predicting for date {target_month}-{target_day}: {e}")
            return {"error": str(e)}

    def get_monthly_statistics(self, month: int) -> Dict:
        """Get overall statistics for a specific month."""
        try:
            month_data = self.df[self.df['month'] == month]

            if len(month_data) == 0:
                return {"error": f"No data for month {month}"}

            result = {
                "month": int(month),
                "month_name": pd.Timestamp(year=2000, month=month, day=1).strftime('%B'),
                "location": self.location_name,
                "total_days": int(len(month_data)),
                "years_covered": int(month_data['year'].nunique()),

                "rainfall": {
                    "rainy_days_percent": float(round((month_data['PRECTOT_mm'] > 0.1).sum() / len(month_data) * 100, 1)),
                    "average_monthly_total_mm": float(round(month_data.groupby('year')['PRECTOT_mm'].sum().mean(), 1))
                },

                "temperature": {
                    "average_mean_celsius": float(round(month_data['T2M_mean'].mean(), 1)),
                    "average_min_celsius": float(round(month_data['T2M_min'].mean(), 1)),
                    "average_max_celsius": float(round(month_data['T2M_max'].mean(), 1))
                },

                "wind": {
                    "average_speed_ms": float(round(month_data['WindSpeed'].mean(), 1))
                },

                "cloud_cover": {
                    "average_percent": float(round(month_data['CLDTOT_pct'].mean(), 1))
                }
            }

            return result

        except Exception as e:
            logger.error(f"Error getting monthly stats: {e}")
            return {"error": str(e)}


def main():
    """Interactive prediction interface."""
    print("=" * 60)
    print("PlanMySky Historical Weather Predictor")
    print("Analyze 30+ years of data for any date")
    print("=" * 60)

    # Find available locations
    data_dir = Path("../../data/processed")
    locations = [d for d in data_dir.iterdir() if d.is_dir()]

    if not locations:
        print("No processed data found. Run era5_processing.py first.")
        return

    # Show available locations
    print("\nAVAILABLE LOCATIONS:")
    for i, loc in enumerate(locations, 1):
        print(f"  {i}. {loc.name}")

    # Select location
    if len(locations) == 1:
        selected_location = locations[0].name
        print(f"\nUsing location: {selected_location}")
    else:
        while True:
            try:
                choice = input(
                    f"\nSelect location [1-{len(locations)}]: ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(locations):
                    selected_location = locations[idx].name
                    break
                else:
                    print(
                        f"Please enter a number between 1 and {len(locations)}")
            except ValueError:
                print("Please enter a valid number")

    # Initialize and load data
    predictor = HistoricalWeatherPredictor(location_name=selected_location)

    print(f"\nLoading historical data for {selected_location}...")
    if not predictor.load_historical_data():
        print("Failed to load data. Run era5_processing.py first.")
        return

    print("\n" + "=" * 60)
    print("What would you like to do?")
    print("  1. Predict for a specific date (e.g., July 15)")
    print("  2. Get monthly statistics (e.g., all of July)")
    print("  3. Generate annual calendar predictions")
    print("=" * 60)

    choice = input("\nEnter choice [1-3]: ").strip()

    if choice == "1":
        # Single date prediction
        print("\nEnter date to analyze:")
        month = int(input("  Month (1-12): ").strip())
        day = int(input("  Day (1-31): ").strip())

        print(f"\nAnalyzing historical patterns for {month:02d}-{day:02d}...")
        print(
            "This includes all occurrences of this date across all years in the dataset.\n")

        prediction = predictor.predict_for_date(month, day)

        print("=" * 60)
        print(f"WEATHER PREDICTION FOR {month:02d}-{day:02d}")
        print("=" * 60)
        print(
            f"\nBased on {prediction['historical_years_analyzed']} years of data ({prediction['total_observations']} days)")
        print(f"\nRAINFALL:")
        print(
            f"  Probability: {prediction['rainfall']['probability_percent']}%")
        print(
            f"  Expected amount: {prediction['rainfall']['expected_amount_mm']} mm")
        print(
            f"  Max recorded: {prediction['rainfall']['max_recorded_mm']} mm")

        print(f"\nTEMPERATURE:")
        print(
            f"  Expected: {prediction['temperature']['expected_range']['min']}C - {prediction['temperature']['expected_range']['max']}C")
        print(
            f"  Average mean: {prediction['temperature']['mean_avg_celsius']}C")

        print(f"\nWIND:")
        print(f"  Average speed: {prediction['wind']['mean_speed_ms']} m/s")

        print(f"\nCLOUD COVER:")
        print(f"  Average: {prediction['cloud_cover']['mean_percent']}%")

        print(f"\nWEATHER CATEGORY: {prediction['weather_category']}")

        print(f"\nEXTREME WEATHER PROBABILITIES:")
        print(
            f"  Temperature > 30C: {prediction['extreme_probabilities']['temp_above_30C']*100:.1f}%")
        print(
            f"  Heavy rain > 10mm: {prediction['extreme_probabilities']['heavy_rain_above_10mm']*100:.1f}%")

        # Save to JSON in location-specific folder
        output_location_dir = Path("../../output") / selected_location
        output_location_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_location_dir / \
            f"prediction_{month:02d}_{day:02d}.json"

        with open(output_path, 'w') as f:
            json.dump(prediction, f, indent=2)

        print(f"\n💾 Full prediction saved to: {output_path}")

    elif choice == "2":
        # Monthly statistics
        month = int(input("\nEnter month (1-12): ").strip())

        print(f"\nAnalyzing month {month}...")
        stats = predictor.get_monthly_statistics(month)

        print("=" * 60)
        print(f"STATISTICS FOR {stats['month_name']}")
        print("=" * 60)
        print(f"Years covered: {stats['years_covered']}")
        print(f"Rainy days: {stats['rainfall']['rainy_days_percent']}%")
        print(
            f"Average monthly rainfall: {stats['rainfall']['average_monthly_total_mm']} mm")
        print(
            f"Average temperature: {stats['temperature']['average_mean_celsius']}°C")

    elif choice == "3":
        # Generate calendar for entire year
        print("\nGenerating predictions for entire year...")

        calendar_predictions = {}
        for month in range(1, 13):
            for day in [1, 15]:  # 1st and 15th of each month
                try:
                    pred = predictor.predict_for_date(month, day)
                    calendar_predictions[f"{month:02d}-{day:02d}"] = pred
                    print(f"  ✓ {month:02d}-{day:02d}")
                except:
                    pass

        output_location_dir = Path("../../output") / selected_location
        output_location_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_location_dir / "annual_calendar_predictions.json"

        with open(output_path, 'w') as f:
            json.dump(calendar_predictions, f, indent=2)

        print(f"\n💾 Annual calendar saved to: {output_path}")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
