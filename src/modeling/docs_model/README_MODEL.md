# PlanMySky Weather Prediction Model

## Overview

LightGBM-based weather prediction system for daily rainfall forecasting and weather conditions.

**Models trained:**
1. **Rain Classifier** - Predicts probability of rain (rain/no-rain)
2. **Rainfall Regressor** - Predicts rainfall amount in mm
3. **Temperature Regressor** - Predicts daily mean temperature
4. **Wind Speed Regressor** - Predicts wind speed
5. **Cloud Cover Regressor** - Predicts cloud coverage percentage

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_modeling.txt
```

### 2. Train the Model

```bash
cd src/modeling
python rainfall_predictor.py
```

**This will:**
- Load processed ERA5 data from `data/processed/`
- Engineer 50+ features (temporal, lagged, rolling averages)
- Train 5 LightGBM models
- Save models to `models/` directory
- Display performance metrics

**Expected output:**
```
[1/5] Training rain classifier...
  Accuracy: 0.8542, Precision: 0.7891, Recall: 0.6234, AUC: 0.8912

[2/5] Training rainfall amount regressor...
  RMSE: 3.45 mm, MAE: 1.23 mm

[3/5] Training temperature regressor...
  RMSE: 1.82 °C, MAE: 1.34 °C

[4/5] Training wind speed regressor...
  RMSE: 0.68 m/s, MAE: 0.51 m/s

[5/5] Training cloud cover regressor...
  RMSE: 12.34 %, MAE: 9.87 %
```

### 3. Make Predictions

```bash
python predict_weather.py
```

**Options:**
1. **Single date prediction** - Get weather for a specific date
2. **7-day forecast** - Predict next 7 days
3. **Batch predictions** - Generate predictions for date range (save to JSON)

### 4. Example Output

```json
{
  "date": "2024-07-10",
  "location": "Kathmandu, Nepal",
  "rainfall_probability": 0.72,
  "predicted_rainfall_mm": 5.3,
  "predicted_temp_range": {
    "min": 22.5,
    "max": 30.1
  },
  "predicted_wind_speed": 2.8,
  "cloud_cover_pct": 65.2,
  "weather_category": "Rainy",
  "thresholds": {
    "temp_above_30C": true,
    "rainfall_above_10mm": false,
    "high_wind": false,
    "heavy_cloud": false
  }
}
```

## Features

### Input Features (Auto-generated)
- **Core weather variables**: Temperature, wind, pressure, humidity, cloud cover, solar radiation
- **Temporal features**: Month, day, day-of-year (sin/cos encoded for seasonality)
- **Derived features**: Relative humidity, temperature range, wind speed
- **Lagged features**: Previous 1, 3, 7 days values
- **Rolling averages**: 3-day and 7-day moving averages

**Total: 50+ features**

### Model Architecture

**LightGBM Configuration (Optimized for Laptop):**
```python
{
  "num_leaves": 31,
  "learning_rate": 0.05,
  "n_estimators": 500,
  "max_depth": 10,
  "subsample": 0.8,
  "colsample_bytree": 0.8
}
```

**Why LightGBM?**
- ✅ Fast training and prediction (10x faster than XGBoost)
- ✅ Low memory footprint (works on 8GB RAM)
- ✅ Handles missing values automatically
- ✅ Built-in categorical feature support
- ✅ Excellent performance on tabular data

### Performance

**System Requirements:**
- CPU: Intel i7 or equivalent
- RAM: 8 GB minimum
- GPU: Not required (but GTX 1050 can be used for inference acceleration)

**Training Time:**
- 2-3 years of data: ~2-5 minutes
- 10+ years of data: ~10-20 minutes

**Prediction Time:**
- Single prediction: <50ms
- Batch (365 days): <2 seconds

## Model Files

After training, these files are created in `models/`:

```
models/
├── planmysky_kathmandu_rain_classifier.pkl      # Rain/no-rain classifier
├── planmysky_kathmandu_rain_regressor.pkl       # Rainfall amount regressor
├── planmysky_kathmandu_temp_regressor.pkl       # Temperature predictor
├── planmysky_kathmandu_wind_regressor.pkl       # Wind speed predictor
├── planmysky_kathmandu_cloud_regressor.pkl      # Cloud cover predictor
├── planmysky_kathmandu_feature_scaler.pkl       # Feature scaler (StandardScaler)
└── planmysky_kathmandu_metadata.json            # Model metadata
```

**Total size:** ~5-10 MB (very lightweight!)

## Integration with Dashboard

### Option 1: Python Backend

```python
from rainfall_predictor import WeatherPredictor

# Load model once at startup
predictor = WeatherPredictor()
predictor.load_models("planmysky_kathmandu")

# Load historical data
df = pd.read_parquet("data/processed/era5_processed_*.parquet")

# Make prediction
prediction = predict_for_date(predictor, df, "2024-07-15", "Kathmandu")

# Return JSON to frontend
return json.dumps(prediction)
```

### Option 2: REST API (Flask)

```python
from flask import Flask, jsonify, request
from rainfall_predictor import WeatherPredictor
from predict_weather import predict_for_date, load_historical_data

app = Flask(__name__)

# Load at startup
predictor = WeatherPredictor()
predictor.load_models("planmysky_kathmandu")
df = load_historical_data()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    date = data.get('date')
    location = data.get('location', 'Kathmandu, Nepal')

    prediction = predict_for_date(predictor, df, date, location)
    return jsonify(prediction)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### Option 3: Batch Generation

For static dashboards, pre-generate predictions:

```bash
python predict_weather.py
# Select option 3: Batch predictions
# Start: 2024-01-01
# End: 2024-12-31
# Output: predictions_2024.json
```

Then load JSON in your dashboard directly.

## Customization

### Adjust Rainfall Threshold

Edit in `rainfall_predictor.py`:

```python
# Line ~470
if rain_proba > 0.3 and self.rain_regressor:  # Change 0.3 to your threshold
```

### Add New Features

Edit `engineer_features()` method:

```python
def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
    # Add your custom features here
    df['custom_feature'] = ...
    return df
```

### Tune Hyperparameters

Edit model configuration in `train_models()`:

```python
self.rain_classifier = lgb.LGBMClassifier(
    num_leaves=31,        # Increase for more complex patterns
    learning_rate=0.05,   # Lower = slower but more accurate
    n_estimators=500,     # More trees = better accuracy
    max_depth=10,         # Deeper trees = more complexity
    ...
)
```

## Troubleshooting

**Issue:** "No processed data files found"
- **Fix:** Run `era5_processing.py` first to process raw ERA5 data

**Issue:** "Not enough rainy days for rainfall regression"
- **Fix:** Download more data or use a location with more rainfall

**Issue:** Model performance is poor
- **Fix:**
  - Ensure you have at least 2-3 years of data
  - Check for missing values in processed data
  - Try tuning hyperparameters
  - Add more features

**Issue:** Predictions are all the same
- **Fix:** Check that lagged features are calculated correctly (need sequential data)

## Citation

```
@software{planmysky2024,
  title={PlanMySky: Weather Prediction System},
  author={PlanMySky Team},
  year={2024},
  event={NASA Space Apps Challenge},
  note={LightGBM-based rainfall prediction using ERA5 reanalysis data}
}
```

## License

MIT License - NASA Space Apps Challenge 2024
