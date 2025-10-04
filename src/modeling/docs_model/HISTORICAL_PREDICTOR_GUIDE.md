# Historical Pattern-Based Weather Predictor

## Concept

**Instead of ML forecasting**, this system analyzes **30+ years of historical data** to show what weather **typically occurs** on any given date.

### How It Works:

When a user selects **July 15**:
1. Find all "July 15th" occurrences in the dataset (1990-2024 = 35 years)
2. Calculate statistics across all those days:
   - Rain probability: How many July 15ths had rain?
   - Average rainfall: What's the typical amount?
   - Temperature range: What's normal for July 15?
   - Extreme events: Has it ever been >30°C? >10mm rain?
3. Return comprehensive statistics + probabilities

## Perfect For:

✅ **Long-term planning** - "Should I plan an outdoor wedding on August 20?"
✅ **Historical context** - "Is this year's July unusually rainy?"
✅ **Climate patterns** - "What's monsoon season look like?"
✅ **Risk assessment** - "What's the chance of heavy rain in September?"

## Usage

### Quick Start:

```bash
cd P:\PlanMySky\src\modeling
python historical_pattern_predictor.py
```

### Example Interaction:

```
Select option: 1 (Predict for specific date)
Month: 7
Day: 15

Output:
============================================================
WEATHER PREDICTION FOR 07-15
============================================================

Based on 35 years of data (450 days with ±7 day window)

RAINFALL:
  Probability: 85.3%  ← 85% of July 15ths had rain
  Expected amount: 12.4 mm
  Max recorded: 45.2 mm  ← Worst July 15th ever

TEMPERATURE:
  Expected: 22.5C - 28.3C
  Average mean: 25.1C
  Record high: 32.1C  ← Hottest July 15th

WEATHER CATEGORY: Rainy
```

## Output Format (JSON)

```json
{
  "date": "07-15",
  "location": "Kathmandu, Nepal",
  "historical_years_analyzed": 35,
  "total_observations": 450,

  "rainfall": {
    "probability": 0.853,
    "probability_percent": 85.3,
    "expected_amount_mm": 12.4,
    "median_amount_mm": 8.2,
    "max_recorded_mm": 45.2,
    "std_deviation_mm": 9.1,
    "intensity_distribution": {
      "light_rain_days": 180,
      "moderate_rain_days": 210,
      "heavy_rain_days": 60,
      "no_rain_days": 66
    }
  },

  "temperature": {
    "mean_avg_celsius": 25.1,
    "mean_std_celsius": 2.3,
    "expected_range": {
      "min": 22.5,
      "max": 28.3
    },
    "record_low_celsius": 18.2,
    "record_high_celsius": 32.1
  },

  "wind": {
    "mean_speed_ms": 2.8,
    "max_recorded_ms": 8.5,
    "std_deviation_ms": 1.2
  },

  "cloud_cover": {
    "mean_percent": 78.5,
    "std_percent": 15.2,
    "clear_days_percent": 8.9,
    "cloudy_days_percent": 72.4
  },

  "weather_category": "Rainy",
  "category_confidence": 0.85,

  "extreme_probabilities": {
    "temp_above_30C": 0.124,  ← 12.4% chance
    "temp_below_10C": 0.0,
    "heavy_rain_above_10mm": 0.356,  ← 35.6% chance
    "high_wind_above_5ms": 0.089
  },

  "recent_years": {
    "2023": {"rainfall_mm": 15.2, "temp_celsius": 26.1},
    "2022": {"rainfall_mm": 8.4, "temp_celsius": 24.3},
    ...
  }
}
```

## Dashboard Integration

### Example 1: Date Selector Widget

```python
from historical_pattern_predictor import HistoricalWeatherPredictor

# Initialize once
predictor = HistoricalWeatherPredictor()
predictor.load_historical_data()

# User selects date
month = 7  # July
day = 15

# Get prediction
prediction = predictor.predict_for_date(month, day)

# Display
print(f"Rain chance: {prediction['rainfall']['probability_percent']}%")
print(f"Expected: {prediction['rainfall']['expected_amount_mm']} mm")
print(f"Temperature: {prediction['temperature']['expected_range']['min']}-{prediction['temperature']['expected_range']['max']}°C")
```

### Example 2: Annual Calendar View

```python
# Generate predictions for entire year
predictions = {}
for month in range(1, 13):
    for day in [1, 15]:  # 1st and 15th of each month
        pred = predictor.predict_for_date(month, day)
        predictions[f"{month:02d}-{day:02d}"] = pred

# Save for dashboard
import json
with open('annual_predictions.json', 'w') as f:
    json.dump(predictions, f)
```

### Example 3: Monthly Overview

```python
# Get July statistics
july_stats = predictor.get_monthly_statistics(7)

print(f"July typically has:")
print(f"  - {july_stats['rainfall']['rainy_days_percent']}% rainy days")
print(f"  - {july_stats['rainfall']['average_monthly_total_mm']} mm total rainfall")
print(f"  - {july_stats['temperature']['average_mean_celsius']}°C average temp")
```

## Features

### Window Parameter

By default, includes dates within ±7 days for more data:
- July 15 → Includes July 8-22
- Gives ~30 observations per year instead of just 1
- More robust statistics

Can be adjusted:
```python
# Strict: exact date only
prediction = predictor.predict_for_date(7, 15, window_days=0)

# Loose: ±2 weeks
prediction = predictor.predict_for_date(7, 15, window_days=14)
```

### Supported Statistics

**Rainfall:**
- Probability (% of days with rain)
- Expected amount (mean)
- Median, max, standard deviation
- Intensity distribution (light/moderate/heavy)

**Temperature:**
- Expected range (min-max)
- Average mean
- Record extremes
- Standard deviation

**Wind:**
- Average speed
- Maximum recorded
- Variability

**Cloud Cover:**
- Average percentage
- Clear vs cloudy day frequency

**Extreme Events:**
- Probability of temp >30°C
- Probability of heavy rain >10mm
- Probability of high wind >5m/s

### Yearly Breakdown

Shows recent 10 years individually:
```json
"recent_years": {
  "2023": {"rainfall_mm": 15.2, "temp_celsius": 26.1},
  "2022": {"rainfall_mm": 8.4, "temp_celsius": 24.3},
  ...
}
```

Useful for trend analysis or showing variability.

## Advantages Over ML Forecasting

### For Hackathon Context:

✅ **No training needed** - Works immediately with historical data
✅ **Interpretable** - Users understand "based on 35 years"
✅ **Reliable** - Not predicting future, just showing historical patterns
✅ **Fast** - <50ms queries
✅ **Accurate for planning** - Perfect for "typical weather on this date"

### Use Cases:

1. **Event Planning**: "Should I book outdoor venue for Sept 10 wedding?"
2. **Agriculture**: "When should I plant crops based on rainfall patterns?"
3. **Tourism**: "Best month to visit Kathmandu for clear skies?"
4. **Infrastructure**: "Historical flood risk assessment"
5. **Education**: "Teaching climate patterns and seasonal cycles"

## Combining Both Approaches

You can use **both systems**:

1. **Historical Predictor** → Long-term planning, typical patterns
2. **LightGBM Model** → Short-term forecasts (next 1-7 days)

Example dashboard:
```
User selects: August 15, 2025

Historical Tab:
  "Based on 35 years, August 15 typically has:
   - 72% rain probability
   - 18mm average rainfall
   - 24-29°C temperature"

Forecast Tab (if within 7 days):
  "This year's August 15 forecast:
   - 85% rain probability
   - 22mm expected rainfall
   - 25-30°C temperature"
```

## Performance

**Query Time:** <50ms per date
**Memory:** ~100MB (loaded historical data)
**Data Requirements:** Minimum 2-3 years, ideal 30+ years
**Accuracy:** N/A (not forecasting, showing historical statistics)

## Files Created

```
src/modeling/
└── historical_pattern_predictor.py    # Main script

output/
├── prediction_07_15.json              # Single date prediction
├── annual_calendar_predictions.json   # Entire year (24 dates)
└── monthly_stats.json                 # Month-level statistics
```

## Example Outputs

### Good for dashboard cards:

```
╔════════════════════════════════╗
║      JULY 15 - KATHMANDU       ║
║   Based on 35 years of data    ║
╠════════════════════════════════╣
║  ☔ Rain: 85% chance (12mm)    ║
║  🌡️  Temp: 22-28°C            ║
║  💨 Wind: 2.8 m/s              ║
║  ☁️  Cloud: 79%                ║
╚════════════════════════════════╝
```

### Good for risk assessment:

```
Extreme Weather Probabilities:
  🌡️  Temperature >30°C: 12.4%
  ☔ Heavy rain >10mm: 35.6%
  💨 High wind >5m/s: 8.9%
```

## Tips for Presentation

1. **Show the data range** - "Based on 1990-2024 (35 years)"
2. **Highlight extremes** - "Wettest July 15: 45mm in 2018"
3. **Compare to current** - "This year vs historical average"
4. **Show confidence** - More years = more reliable
5. **Visualize distribution** - Histogram of all July 15ths

## Summary

**This approach is perfect for your hackathon because:**
- ✅ No ML complexity - Easy to explain
- ✅ Works with limited data - Even 5-10 years useful
- ✅ Immediate results - No training required
- ✅ Highly interpretable - "85% of July 15ths had rain"
- ✅ Perfect for planning - "What to expect on this date"
- ✅ Complements forecasting - Show both historical + prediction

You can build the entire dashboard around this concept! 🎉
