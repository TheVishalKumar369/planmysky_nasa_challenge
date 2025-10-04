#!/usr/bin/env python3
"""
Weather Prediction Script
Load trained models and make predictions for specific dates

Author: PlanMySky Team
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

from rainfall_predictor import WeatherPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_historical_data(data_dir: str = "../../data/processed", location_name: str = None):
    """Load the processed historical data for a specific location."""
    data_path = Path(data_dir)

    # If location specified, look in location folder
    if location_name:
        clean_name = location_name.lower().replace(' ', '_').replace(',', '').replace('.', '_')
        location_path = data_path / clean_name
        if location_path.exists():
            parquet_files = list(location_path.glob("era5_processed_*.parquet"))
            if not parquet_files:
                csv_files = list(location_path.glob("era5_processed_*.csv"))
                if csv_files:
                    df = pd.read_csv(csv_files[0])
                else:
                    raise FileNotFoundError(f"No processed data files found for {location_name}")
            else:
                df = pd.read_parquet(parquet_files[0])
        else:
            raise FileNotFoundError(f"Location folder not found: {location_path}")
    else:
        # Legacy: search in root directory
        parquet_files = list(data_path.glob("era5_processed_*.parquet"))
        if not parquet_files:
            csv_files = list(data_path.glob("era5_processed_*.csv"))
            if csv_files:
                df = pd.read_csv(csv_files[0])
            else:
                raise FileNotFoundError("No processed data files found")
        else:
            df = pd.read_parquet(parquet_files[0])

    df['date'] = pd.to_datetime(df['date'])
    return df


def predict_for_date(predictor: WeatherPredictor, df: pd.DataFrame,
                     target_date: str, location: str = "Kathmandu, Nepal"):
    """Make prediction for a specific date."""
    try:
        # Parse target date
        target_dt = pd.to_datetime(target_date)

        # Find the closest date in historical data
        df = df.sort_values('date')
        df['date_diff'] = abs((df['date'] - target_dt).dt.days)
        closest_idx = df['date_diff'].idxmin()

        # Get data around that date for context (for lagged features)
        context_window = 10
        start_idx = max(0, closest_idx - context_window)
        end_idx = min(len(df), closest_idx + 1)

        df_context = df.iloc[start_idx:end_idx].copy()

        # Engineer features
        df_features = predictor.engineer_features(df_context)

        # Get features for the target date (last row after engineering)
        features = df_features.iloc[[-1]].copy()

        # Make prediction
        prediction = predictor.predict(features, location_name=location)

        return prediction

    except Exception as e:
        logger.error(f"Error predicting for date {target_date}: {e}")
        return {"error": str(e)}


def predict_next_n_days(predictor: WeatherPredictor, df: pd.DataFrame,
                        n_days: int = 7, location: str = "Kathmandu, Nepal"):
    """Predict for the next N days based on most recent data."""
    try:
        # Get most recent data
        df = df.sort_values('date')
        recent_data = df.tail(30).copy()  # Last 30 days for context

        predictions = []

        # Use the last known day as base
        last_date = recent_data['date'].max()

        for i in range(n_days):
            pred_date = last_date + timedelta(days=i+1)

            # For future predictions, we use the pattern from same day-of-year
            # from historical data as a baseline
            day_of_year = pred_date.dayofyear
            month = pred_date.month

            # Find similar days in history (same month, similar day-of-year)
            similar_days = df[
                (df['date'].dt.month == month) &
                (abs(df['date'].dt.dayofyear - day_of_year) <= 7)
            ].copy()

            if len(similar_days) > 0:
                # Use median of similar days as baseline
                baseline = similar_days.median()

                # Create feature row
                feature_row = recent_data.iloc[[-1]].copy()
                feature_row['date'] = pred_date

                # Update with baseline predictions
                for col in baseline.index:
                    if col in feature_row.columns and col not in ['date', 'lat', 'lon']:
                        feature_row[col] = baseline[col]

                # Engineer features
                df_temp = pd.concat([recent_data, feature_row], ignore_index=True)
                df_features = predictor.engineer_features(df_temp)

                # Get prediction
                features = df_features.iloc[[-1]].copy()
                prediction = predictor.predict(features, location_name=location)

                predictions.append(prediction)

                # Add this prediction to recent data for next iteration
                recent_data = df_temp.copy()

        return predictions

    except Exception as e:
        logger.error(f"Error predicting next {n_days} days: {e}")
        return [{"error": str(e)}]


def main():
    """Main prediction interface."""
    print("=" * 60)
    print("PlanMySky Weather Predictor")
    print("=" * 60)

    # Find available locations with models
    model_dir = Path("../../models")
    model_locations = [d for d in model_dir.iterdir() if d.is_dir()]

    if not model_locations:
        print("No trained models found. Please train models first by running: python rainfall_predictor.py")
        return

    # Show available locations
    print("\nAVAILABLE LOCATIONS:")
    for i, loc in enumerate(model_locations, 1):
        print(f"  {i}. {loc.name}")

    # Select location
    if len(model_locations) == 1:
        selected_location = model_locations[0].name
        print(f"\nUsing location: {selected_location}")
    else:
        while True:
            try:
                choice = input(f"\nSelect location [1-{len(model_locations)}]: ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(model_locations):
                    selected_location = model_locations[idx].name
                    break
                else:
                    print(f"Please enter a number between 1 and {len(model_locations)}")
            except ValueError:
                print("Please enter a valid number")

    # Load trained model
    print(f"\nLoading trained models for {selected_location}...")
    predictor = WeatherPredictor()

    try:
        predictor.load_models(prefix="planmysky", location_name=selected_location)
        print("✓ Models loaded successfully")
    except Exception as e:
        print(f"✗ Error loading models: {e}")
        print("\nPlease train the model first by running: python rainfall_predictor.py")
        return

    # Load historical data
    print("\nLoading historical data...")
    try:
        df = load_historical_data(location_name=selected_location)
        location_display_name = df['location_name'].iloc[0] if 'location_name' in df.columns else selected_location
        print(f"✓ Loaded {len(df)} days of data ({df['date'].min()} to {df['date'].max()})")
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return

    print("\n" + "=" * 60)
    print("Prediction Options:")
    print("  1. Predict for a specific date")
    print("  2. Predict for next 7 days")
    print("  3. Batch predictions (save to file)")
    print("=" * 60)

    choice = input("\nEnter choice [1-3]: ").strip()

    if choice == "1":
        # Single date prediction
        date_str = input("Enter date (YYYY-MM-DD): ").strip()

        print(f"\nMaking prediction for {date_str}...")
        prediction = predict_for_date(predictor, df, date_str, location_display_name)

        print("\n" + "=" * 60)
        print("PREDICTION RESULT")
        print("=" * 60)
        print(json.dumps(prediction, indent=2))

    elif choice == "2":
        # Next N days forecast
        n_days = input("Number of days to forecast [7]: ").strip()
        n_days = int(n_days) if n_days else 7

        print(f"\nForecasting next {n_days} days...")
        predictions = predict_next_n_days(predictor, df, n_days, location_display_name)

        print("\n" + "=" * 60)
        print(f"{n_days}-DAY FORECAST")
        print("=" * 60)

        for i, pred in enumerate(predictions, 1):
            print(f"\nDay {i}: {pred['date']}")
            print(f"  Weather: {pred['weather_category']}")
            print(f"  Rain Probability: {pred['rainfall_probability']*100:.1f}%")
            print(f"  Expected Rainfall: {pred['predicted_rainfall_mm']:.1f} mm")
            print(f"  Temperature: {pred['predicted_temp_range']['min']:.1f}°C - {pred['predicted_temp_range']['max']:.1f}°C")
            print(f"  Wind Speed: {pred['predicted_wind_speed']:.1f} m/s")
            print(f"  Cloud Cover: {pred['cloud_cover_pct']:.1f}%")

    elif choice == "3":
        # Batch predictions
        start_date = input("Start date (YYYY-MM-DD): ").strip()
        end_date = input("End date (YYYY-MM-DD): ").strip()
        output_file = input("Output file [predictions.json]: ").strip() or "predictions.json"

        print(f"\nGenerating predictions from {start_date} to {end_date}...")

        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        predictions = []

        for date in date_range:
            pred = predict_for_date(predictor, df, date.strftime('%Y-%m-%d'))
            predictions.append(pred)

        # Save to file in location-specific folder
        output_location_dir = Path("../../output") / selected_location
        output_location_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_location_dir / output_file

        with open(output_path, 'w') as f:
            json.dump(predictions, f, indent=2)

        print(f"\n✓ Saved {len(predictions)} predictions to {output_path}")

    else:
        print("Invalid choice")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
