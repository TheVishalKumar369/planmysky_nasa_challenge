#!/usr/bin/env python3
"""
PlanMySky - Weather Prediction Model
Uses LightGBM for rainfall prediction and weather forecasting

Author: PlanMySky Team
NASA Space Apps Challenge
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
import joblib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WeatherPredictor:
    """
    Weather prediction system using LightGBM for:
    - Rainfall probability (classification)
    - Rainfall amount (regression)
    - Temperature, wind speed, cloud cover prediction
    """

    def __init__(self, model_dir: str = "../../models", location_name: str = None):
        """Initialize the weather predictor."""
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.location_name = location_name
        self.location_model_dir = None  # Will be set when loading/saving models

        # Models
        self.rain_classifier = None  # Rain/No-rain classification
        self.rain_regressor = None   # Rainfall amount prediction
        self.temp_regressor = None   # Temperature prediction
        self.wind_regressor = None   # Wind speed prediction
        self.cloud_regressor = None  # Cloud cover prediction

        # Scalers
        self.feature_scaler = None
        self.target_scalers = {}

        # Feature information
        self.feature_names = []
        self.metadata = {}

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived features for better predictions."""
        try:
            df_feat = df.copy()

            # Convert date to datetime
            df_feat['date'] = pd.to_datetime(df_feat['date'])

            # Temporal features
            df_feat['year'] = df_feat['date'].dt.year
            df_feat['month'] = df_feat['date'].dt.month
            df_feat['day'] = df_feat['date'].dt.day
            df_feat['day_of_year'] = df_feat['date'].dt.dayofyear
            df_feat['day_of_week'] = df_feat['date'].dt.dayofweek

            # Seasonal encoding (sine/cosine for cyclical nature)
            df_feat['month_sin'] = np.sin(2 * np.pi * df_feat['month'] / 12)
            df_feat['month_cos'] = np.cos(2 * np.pi * df_feat['month'] / 12)
            df_feat['day_of_year_sin'] = np.sin(2 * np.pi * df_feat['day_of_year'] / 365)
            df_feat['day_of_year_cos'] = np.cos(2 * np.pi * df_feat['day_of_year'] / 365)

            # Derived meteorological features
            if 'T2M_mean' in df_feat.columns and 'D2M' in df_feat.columns:
                # Relative humidity approximation
                df_feat['rel_humidity_approx'] = 100 - 5 * (df_feat['T2M_mean'] - df_feat['D2M'])
                df_feat['rel_humidity_approx'] = df_feat['rel_humidity_approx'].clip(0, 100)

            # Temperature range
            if 'T2M_max' in df_feat.columns and 'T2M_min' in df_feat.columns:
                df_feat['temp_range'] = df_feat['T2M_max'] - df_feat['T2M_min']

            # Lagged features (previous day weather)
            lag_features = ['PRECTOT_mm', 'T2M_mean', 'MSL', 'TCWV', 'CLDTOT_pct']
            for feat in lag_features:
                if feat in df_feat.columns:
                    df_feat[f'{feat}_lag1'] = df_feat[feat].shift(1)
                    df_feat[f'{feat}_lag3'] = df_feat[feat].shift(3)
                    df_feat[f'{feat}_lag7'] = df_feat[feat].shift(7)

            # Rolling averages (3-day, 7-day)
            rolling_features = ['T2M_mean', 'MSL', 'TCWV', 'WindSpeed', 'CLDTOT_pct']
            for feat in rolling_features:
                if feat in df_feat.columns:
                    df_feat[f'{feat}_roll3'] = df_feat[feat].rolling(window=3, min_periods=1).mean()
                    df_feat[f'{feat}_roll7'] = df_feat[feat].rolling(window=7, min_periods=1).mean()

            # Binary rain indicator for classification
            df_feat['has_rain'] = (df_feat['PRECTOT_mm'] > 0.1).astype(int)

            logger.info(f"Feature engineering complete: {df_feat.shape[1]} features created")
            return df_feat

        except Exception as e:
            logger.error(f"Error in feature engineering: {e}")
            return df

    def prepare_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Prepare features and targets for training."""
        try:
            # Core features (always available)
            feature_cols = [
                # Current conditions
                'T2M_mean', 'T2M_min', 'T2M_max',
                'U10M', 'V10M', 'WindSpeed',
                'D2M', 'MSL', 'TCWV', 'CLDTOT_pct', 'SSRD',

                # Temporal
                'month', 'day', 'day_of_year', 'day_of_week',
                'month_sin', 'month_cos', 'day_of_year_sin', 'day_of_year_cos',

                # Derived
                'rel_humidity_approx', 'temp_range',
            ]

            # Add lagged features
            lag_features = ['PRECTOT_mm', 'T2M_mean', 'MSL', 'TCWV', 'CLDTOT_pct']
            for feat in lag_features:
                for lag in [1, 3, 7]:
                    feature_cols.append(f'{feat}_lag{lag}')

            # Add rolling averages
            rolling_features = ['T2M_mean', 'MSL', 'TCWV', 'WindSpeed', 'CLDTOT_pct']
            for feat in rolling_features:
                for window in [3, 7]:
                    feature_cols.append(f'{feat}_roll{window}')

            # Select only existing columns
            feature_cols = [col for col in feature_cols if col in df.columns]

            # Target variables
            target_cols = ['has_rain', 'PRECTOT_mm', 'T2M_mean', 'WindSpeed', 'CLDTOT_pct']

            X = df[feature_cols].copy()
            y = df[target_cols].copy()

            # Drop rows with NaN (from lagging)
            valid_idx = ~(X.isnull().any(axis=1) | y.isnull().any(axis=1))
            X = X[valid_idx]
            y = y[valid_idx]

            self.feature_names = feature_cols

            logger.info(f"Data prepared: {X.shape[0]} samples, {X.shape[1]} features")
            return X, y

        except Exception as e:
            logger.error(f"Error preparing data: {e}")
            raise

    def train_models(self, X: pd.DataFrame, y: pd.DataFrame, test_size: float = 0.2, val_size: float = 0.1):
        """Train all prediction models."""
        try:
            logger.info("Starting model training...")

            # Split data: train / validation / test
            X_temp, X_test, y_temp, y_test = train_test_split(
                X, y, test_size=test_size, shuffle=False  # Time series - no shuffle
            )

            val_ratio = val_size / (1 - test_size)
            X_train, X_val, y_train, y_val = train_test_split(
                X_temp, y_temp, test_size=val_ratio, shuffle=False
            )

            logger.info(f"Train: {X_train.shape[0]}, Val: {X_val.shape[0]}, Test: {X_test.shape[0]}")

            # Scale features
            self.feature_scaler = StandardScaler()
            X_train_scaled = self.feature_scaler.fit_transform(X_train)
            X_val_scaled = self.feature_scaler.transform(X_val)
            X_test_scaled = self.feature_scaler.transform(X_test)

            # ===== 1. Rain Classification (Rain/No-rain) =====
            logger.info("\n[1/5] Training rain classifier...")
            self.rain_classifier = lgb.LGBMClassifier(
                objective='binary',
                num_leaves=31,
                learning_rate=0.05,
                n_estimators=500,
                max_depth=10,
                min_child_samples=20,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                verbose=-1
            )

            self.rain_classifier.fit(
                X_train_scaled, y_train['has_rain'],
                eval_set=[(X_val_scaled, y_val['has_rain'])],
                callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)]
            )

            # Evaluate
            y_pred_class = self.rain_classifier.predict(X_test_scaled)
            y_pred_proba = self.rain_classifier.predict_proba(X_test_scaled)[:, 1]

            acc = accuracy_score(y_test['has_rain'], y_pred_class)
            prec = precision_score(y_test['has_rain'], y_pred_class, zero_division=0)
            rec = recall_score(y_test['has_rain'], y_pred_class, zero_division=0)
            auc = roc_auc_score(y_test['has_rain'], y_pred_proba)

            logger.info(f"  Accuracy: {acc:.4f}, Precision: {prec:.4f}, Recall: {rec:.4f}, AUC: {auc:.4f}")

            # ===== 2. Rainfall Amount Regression =====
            logger.info("\n[2/5] Training rainfall amount regressor...")

            # Train only on rainy days
            rain_mask_train = y_train['has_rain'] == 1
            rain_mask_val = y_val['has_rain'] == 1
            rain_mask_test = y_test['has_rain'] == 1

            if rain_mask_train.sum() > 50:  # Need enough rainy samples
                self.rain_regressor = lgb.LGBMRegressor(
                    objective='regression',
                    num_leaves=31,
                    learning_rate=0.05,
                    n_estimators=500,
                    max_depth=10,
                    min_child_samples=10,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                    verbose=-1
                )

                self.rain_regressor.fit(
                    X_train_scaled[rain_mask_train], y_train.loc[rain_mask_train, 'PRECTOT_mm'],
                    eval_set=[(X_val_scaled[rain_mask_val], y_val.loc[rain_mask_val, 'PRECTOT_mm'])],
                    callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)]
                )

                # Evaluate on rainy test days
                if rain_mask_test.sum() > 0:
                    y_pred_rain = self.rain_regressor.predict(X_test_scaled[rain_mask_test])
                    rmse = np.sqrt(mean_squared_error(y_test.loc[rain_mask_test, 'PRECTOT_mm'], y_pred_rain))
                    mae = mean_absolute_error(y_test.loc[rain_mask_test, 'PRECTOT_mm'], y_pred_rain)
                    logger.info(f"  RMSE: {rmse:.4f} mm, MAE: {mae:.4f} mm")
            else:
                logger.warning("  Not enough rainy days for rainfall regression")

            # ===== 3. Temperature Regression =====
            logger.info("\n[3/5] Training temperature regressor...")
            self.temp_regressor = lgb.LGBMRegressor(
                objective='regression',
                num_leaves=31,
                learning_rate=0.05,
                n_estimators=300,
                max_depth=8,
                random_state=42,
                verbose=-1
            )

            self.temp_regressor.fit(
                X_train_scaled, y_train['T2M_mean'],
                eval_set=[(X_val_scaled, y_val['T2M_mean'])],
                callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)]
            )

            y_pred_temp = self.temp_regressor.predict(X_test_scaled)
            rmse = np.sqrt(mean_squared_error(y_test['T2M_mean'], y_pred_temp))
            mae = mean_absolute_error(y_test['T2M_mean'], y_pred_temp)
            logger.info(f"  RMSE: {rmse:.4f} °C, MAE: {mae:.4f} °C")

            # ===== 4. Wind Speed Regression =====
            logger.info("\n[4/5] Training wind speed regressor...")
            self.wind_regressor = lgb.LGBMRegressor(
                objective='regression',
                num_leaves=31,
                learning_rate=0.05,
                n_estimators=300,
                max_depth=8,
                random_state=42,
                verbose=-1
            )

            self.wind_regressor.fit(
                X_train_scaled, y_train['WindSpeed'],
                eval_set=[(X_val_scaled, y_val['WindSpeed'])],
                callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)]
            )

            y_pred_wind = self.wind_regressor.predict(X_test_scaled)
            rmse = np.sqrt(mean_squared_error(y_test['WindSpeed'], y_pred_wind))
            mae = mean_absolute_error(y_test['WindSpeed'], y_pred_wind)
            logger.info(f"  RMSE: {rmse:.4f} m/s, MAE: {mae:.4f} m/s")

            # ===== 5. Cloud Cover Regression =====
            logger.info("\n[5/5] Training cloud cover regressor...")
            self.cloud_regressor = lgb.LGBMRegressor(
                objective='regression',
                num_leaves=31,
                learning_rate=0.05,
                n_estimators=300,
                max_depth=8,
                random_state=42,
                verbose=-1
            )

            self.cloud_regressor.fit(
                X_train_scaled, y_train['CLDTOT_pct'],
                eval_set=[(X_val_scaled, y_val['CLDTOT_pct'])],
                callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)]
            )

            y_pred_cloud = self.cloud_regressor.predict(X_test_scaled)
            rmse = np.sqrt(mean_squared_error(y_test['CLDTOT_pct'], y_pred_cloud))
            mae = mean_absolute_error(y_test['CLDTOT_pct'], y_pred_cloud)
            logger.info(f"  RMSE: {rmse:.4f} %, MAE: {mae:.4f} %")

            logger.info("\nAll models trained successfully!")
            return True

        except Exception as e:
            logger.error(f"Error training models: {e}")
            return False

    def save_models(self, prefix: str = "planmysky", location_name: str = None):
        """Save all trained models and scalers."""
        try:
            # Determine location-specific model directory
            if location_name:
                clean_name = location_name.lower().replace(' ', '_').replace(',', '').replace('.', '_')
                self.location_model_dir = self.model_dir / clean_name
            elif self.location_name:
                clean_name = self.location_name.lower().replace(' ', '_').replace(',', '').replace('.', '_')
                self.location_model_dir = self.model_dir / clean_name
            else:
                self.location_model_dir = self.model_dir

            self.location_model_dir.mkdir(parents=True, exist_ok=True)

            # Save models
            if self.rain_classifier:
                joblib.dump(self.rain_classifier, self.location_model_dir / f"{prefix}_rain_classifier.pkl")
            if self.rain_regressor:
                joblib.dump(self.rain_regressor, self.location_model_dir / f"{prefix}_rain_regressor.pkl")
            if self.temp_regressor:
                joblib.dump(self.temp_regressor, self.location_model_dir / f"{prefix}_temp_regressor.pkl")
            if self.wind_regressor:
                joblib.dump(self.wind_regressor, self.location_model_dir / f"{prefix}_wind_regressor.pkl")
            if self.cloud_regressor:
                joblib.dump(self.cloud_regressor, self.location_model_dir / f"{prefix}_cloud_regressor.pkl")

            # Save scaler
            if self.feature_scaler:
                joblib.dump(self.feature_scaler, self.location_model_dir / f"{prefix}_feature_scaler.pkl")

            # Save feature names and metadata
            metadata = {
                'feature_names': self.feature_names,
                'n_features': len(self.feature_names),
                'location_name': location_name or self.location_name,
                'model_version': '1.0',
                'trained_date': pd.Timestamp.now().isoformat()
            }

            with open(self.location_model_dir / f"{prefix}_metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Models saved to {self.location_model_dir}")
            return True

        except Exception as e:
            logger.error(f"Error saving models: {e}")
            return False

    def load_models(self, prefix: str = "planmysky", location_name: str = None):
        """Load trained models and scalers."""
        try:
            # Determine location-specific model directory
            if location_name:
                clean_name = location_name.lower().replace(' ', '_').replace(',', '').replace('.', '_')
                self.location_model_dir = self.model_dir / clean_name
            elif self.location_name:
                clean_name = self.location_name.lower().replace(' ', '_').replace(',', '').replace('.', '_')
                self.location_model_dir = self.model_dir / clean_name
            else:
                self.location_model_dir = self.model_dir

            if not self.location_model_dir.exists():
                raise FileNotFoundError(f"Model directory not found: {self.location_model_dir}")

            # Load models
            self.rain_classifier = joblib.load(self.location_model_dir / f"{prefix}_rain_classifier.pkl")

            rain_reg_path = self.location_model_dir / f"{prefix}_rain_regressor.pkl"
            if rain_reg_path.exists():
                self.rain_regressor = joblib.load(rain_reg_path)

            self.temp_regressor = joblib.load(self.location_model_dir / f"{prefix}_temp_regressor.pkl")
            self.wind_regressor = joblib.load(self.location_model_dir / f"{prefix}_wind_regressor.pkl")
            self.cloud_regressor = joblib.load(self.location_model_dir / f"{prefix}_cloud_regressor.pkl")

            # Load scaler
            self.feature_scaler = joblib.load(self.location_model_dir / f"{prefix}_feature_scaler.pkl")

            # Load metadata
            with open(self.location_model_dir / f"{prefix}_metadata.json", 'r') as f:
                self.metadata = json.load(f)
                self.feature_names = self.metadata['feature_names']
                if 'location_name' in self.metadata:
                    self.location_name = self.metadata['location_name']

            logger.info(f"Models loaded from {self.location_model_dir}")
            return True

        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False

    def predict(self, features: pd.DataFrame, location_name: str = "Unknown") -> Dict:
        """Make weather predictions for given features."""
        try:
            # Ensure all required features are present
            for feat in self.feature_names:
                if feat not in features.columns:
                    features[feat] = 0  # Fill missing with default

            # Select and order features
            X = features[self.feature_names].copy()

            # Scale features
            X_scaled = self.feature_scaler.transform(X)

            # Get the first (or only) prediction
            idx = 0

            # Predict rainfall probability
            rain_proba = float(self.rain_classifier.predict_proba(X_scaled)[idx, 1])

            # Predict rainfall amount (only if likely to rain)
            if rain_proba > 0.3 and self.rain_regressor:
                rain_amount = float(self.rain_regressor.predict(X_scaled)[idx])
                rain_amount = max(0, rain_amount)  # Non-negative
            else:
                rain_amount = 0.0

            # Predict other variables
            temp_pred = float(self.temp_regressor.predict(X_scaled)[idx])
            wind_pred = float(self.wind_regressor.predict(X_scaled)[idx])
            cloud_pred = float(self.cloud_regressor.predict(X_scaled)[idx])
            cloud_pred = np.clip(cloud_pred, 0, 100)

            # Get original temp range if available
            temp_min = features['T2M_min'].iloc[idx] if 'T2M_min' in features.columns else temp_pred - 3
            temp_max = features['T2M_max'].iloc[idx] if 'T2M_max' in features.columns else temp_pred + 3

            # Categorize weather
            if rain_proba > 0.6:
                weather_category = "Rainy"
            elif cloud_pred > 60:
                weather_category = "Cloudy"
            else:
                weather_category = "Clear"

            # Thresholds
            thresholds = {
                "temp_above_30C": bool(temp_max > 30),
                "rainfall_above_10mm": bool(rain_amount > 10),
                "high_wind": bool(wind_pred > 5),
                "heavy_cloud": bool(cloud_pred > 75)
            }

            # Build result
            date_str = features['date'].iloc[idx] if 'date' in features.columns else pd.Timestamp.now().strftime('%Y-%m-%d')

            result = {
                "date": str(date_str),
                "location": location_name,
                "rainfall_probability": round(rain_proba, 3),
                "predicted_rainfall_mm": round(rain_amount, 2),
                "predicted_temp_range": {
                    "min": round(temp_min, 1),
                    "max": round(temp_max, 1)
                },
                "predicted_wind_speed": round(wind_pred, 1),
                "cloud_cover_pct": round(cloud_pred, 1),
                "weather_category": weather_category,
                "thresholds": thresholds
            }

            return result

        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return {"error": str(e)}


def main():
    """Main training workflow."""
    logger.info("PlanMySky Weather Prediction Model Training")
    logger.info("=" * 60)

    # Load processed data
    data_dir = Path("../../data/processed")

    # Find available locations
    locations = [d for d in data_dir.iterdir() if d.is_dir()]

    if not locations:
        # Legacy: check for files in root
        processed_files = list(data_dir.glob("era5_processed_*.parquet"))
        if not processed_files:
            logger.error("No processed data files found. Run era5_processing.py first.")
            return
        location_folder = None
        location_name = "Unknown"
    else:
        # Show available locations
        print("\n" + "="*60)
        print("AVAILABLE LOCATIONS FOR MODEL TRAINING")
        print("="*60)
        for i, loc in enumerate(locations, 1):
            print(f"  {i}. {loc.name}")

        # Select location
        if len(locations) == 1:
            location_folder = locations[0]
            location_name = location_folder.name
            print(f"\nTraining models for: {location_name}")
        else:
            while True:
                try:
                    choice = input(f"\nSelect location to train [1-{len(locations)}]: ").strip()
                    idx = int(choice) - 1
                    if 0 <= idx < len(locations):
                        location_folder = locations[idx]
                        location_name = location_folder.name
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(locations)}")
                except ValueError:
                    print("Please enter a valid number")

        # Find processed files in location folder
        processed_files = list(location_folder.glob("era5_processed_*.parquet"))
        if not processed_files:
            logger.error(f"No processed data files found in {location_folder}")
            return

    logger.info(f"Found {len(processed_files)} processed file(s)")

    # Load data (use parquet for speed)
    df = pd.read_parquet(processed_files[0])
    logger.info(f"Loaded data: {df.shape[0]} records")

    # Get location name from data if available
    if 'location_name' in df.columns:
        location_name = df['location_name'].iloc[0]

    # Initialize predictor
    predictor = WeatherPredictor(location_name=location_name)

    # Feature engineering
    logger.info("\nPerforming feature engineering...")
    df_features = predictor.engineer_features(df)

    # Prepare data
    logger.info("\nPreparing training data...")
    X, y = predictor.prepare_data(df_features)

    # Train models
    logger.info("\nTraining models...")
    success = predictor.train_models(X, y, test_size=0.1, val_size=0.1)

    if success:
        # Save models
        logger.info("\nSaving models...")
        predictor.save_models(prefix="planmysky", location_name=location_name)

        logger.info("\n" + "=" * 60)
        logger.info("Training complete!")
        logger.info(f"Location: {location_name}")
        logger.info(f"Models saved to: {predictor.location_model_dir}")
        logger.info("\nYou can now use these models for predictions!")
    else:
        logger.error("Training failed!")


if __name__ == "__main__":
    main()
