# PlanMySky Weather API - Complete Guide

**Version:** 1.0.0
**Base URL:** `http://localhost:8000`
**API Documentation (Interactive):** `http://localhost:8000/docs`

---

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Authentication](#authentication)
4. [Available Endpoints](#available-endpoints)
5. [Location Management](#location-management)
6. [Weather Predictions](#weather-predictions)
7. [Statistics & Analytics](#statistics--analytics)
8. [Data Download](#data-download)
9. [Response Format](#response-format)
10. [Error Handling](#error-handling)
11. [Code Examples](#code-examples)

---

## Overview

PlanMySky Weather API provides **historical weather pattern predictions** for any date based on 30+ years of ERA5 data. The API analyzes historical patterns to predict future weather conditions.

### Key Features
- ✅ Multi-location support (Kathmandu, New York, etc.)
- ✅ Historical pattern analysis (1990-2024)
- ✅ Future date predictions based on past patterns
- ✅ Monthly statistics and trends
- ✅ JSON data export/download
- ✅ RESTful API design

### How It Works
When you ask for weather on **July 15, 2026**, the API:
1. Finds all **July 15th dates** from 1990-2024 (35 years)
2. Calculates statistics (rainfall probability, average temp, etc.)
3. Returns prediction for **July 15, 2026** based on historical patterns

---

## Getting Started

### 1. Start the API Server

```bash
cd backend/api
python weather_api.py
```

Server will start at: `http://localhost:8000`

### 2. Test the API

Open your browser and go to:
- **Interactive Docs:** `http://localhost:8000/docs`
- **Status Check:** `http://localhost:8000/api/status`

### 3. Check Available Locations

```bash
curl http://localhost:8000/api/locations
```

**Response:**
```json
{
  "locations": ["kathmandu_nepal", "newyork_usa"],
  "total": 2
}
```

---

## Authentication

**Current Version:** No authentication required
**Future:** API keys may be added for production deployment

---

## Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | API status and available locations |
| GET | `/api/locations` | List all available locations |
| GET | `/api/predict/{month}/{day}` | Get weather prediction for a date |
| POST | `/api/predict` | Get prediction (POST version) |
| GET | `/api/monthly/{month}` | Get monthly statistics |
| POST | `/api/monthly` | Get monthly stats (POST version) |
| GET | `/api/calendar` | Get annual calendar predictions |
| GET | `/api/download/predictions` | Download predictions as JSON file |
| GET | `/api/health` | Health check endpoint |

---

## Location Management

### Get Available Locations

**Endpoint:** `GET /api/locations`

**Request:**
```bash
curl http://localhost:8000/api/locations
```

**Response:**
```json
{
  "locations": [
    "kathmandu_nepal",
    "newyork_usa",
    "sydney_australia"
  ],
  "total": 3
}
```

**Notes:**
- Locations are automatically discovered from `data/processed/` folder
- Each location must have processed weather data available
- Location names are folder names (lowercase, underscores)

---

## Weather Predictions

### 1. Get Prediction for Specific Date

**Endpoint:** `GET /api/predict/{month}/{day}`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `month` | integer | Yes | Month (1-12) |
| `day` | integer | Yes | Day (1-31) |
| `location` | string | Yes | Location identifier |
| `window_days` | integer | No | Date window ±N days (default: 7) |

**Example Request:**
```bash
curl "http://localhost:8000/api/predict/7/15?location=kathmandu_nepal&window_days=7"
```

**Example Response:**
```json
{
  "date": "2026-07-15",
  "month_day": "07-15",
  "location": "Kathmandu Nepal",
  "prediction_type": "historical_pattern",
  "based_on_data_range": "1990-2024",
  "historical_years_analyzed": 35,
  "total_observations": 280,

  "rainfall": {
    "probability": 0.857,
    "probability_percent": 85.7,
    "expected_amount_mm": 45.2,
    "median_amount_mm": 38.5,
    "max_recorded_mm": 125.3,
    "std_deviation_mm": 22.1,
    "intensity_distribution": {
      "light_rain_days": 120,
      "moderate_rain_days": 100,
      "heavy_rain_days": 20,
      "no_rain_days": 40
    }
  },

  "temperature": {
    "mean_avg_celsius": 24.5,
    "mean_std_celsius": 2.1,
    "expected_range": {
      "min": 20.3,
      "max": 28.7
    },
    "record_low_celsius": 15.2,
    "record_high_celsius": 32.4
  },

  "wind": {
    "mean_speed_ms": 2.3,
    "max_recorded_ms": 8.5,
    "std_deviation_ms": 1.2
  },

  "cloud_cover": {
    "mean_percent": 75.4,
    "std_percent": 15.2,
    "clear_days_percent": 10.5,
    "cloudy_days_percent": 65.3
  },

  "weather_category": "Rainy",
  "category_confidence": 0.85,

  "extreme_probabilities": {
    "temp_above_30C": 0.15,
    "temp_below_10C": 0.0,
    "heavy_rain_above_10mm": 0.65,
    "high_wind_above_5ms": 0.12
  },

  "additional": {
    "humidity_celsius": 22.1,
    "pressure_hpa": 1012.5,
    "solar_radiation_wm2": 185.3
  },

  "recent_years": {
    "2024": {
      "rainfall_mm": 52.3,
      "temp_celsius": 25.1,
      "wind_ms": 2.8,
      "cloud_pct": 80.5
    },
    "2023": {
      "rainfall_mm": 41.2,
      "temp_celsius": 24.2,
      "wind_ms": 2.1,
      "cloud_pct": 72.3
    }
  }
}
```

**Date Logic:**
- If you request **July 15** on **October 2, 2025**:
  - July 15, 2025 already passed → Returns **July 15, 2026**
- If you request **December 25** on **October 2, 2025**:
  - December 25, 2025 hasn't happened → Returns **December 25, 2025**

### 2. POST Version (JSON Request Body)

**Endpoint:** `POST /api/predict`

**Request Body:**
```json
{
  "month": 7,
  "day": 15,
  "location": "kathmandu_nepal",
  "window_days": 7
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "month": 7,
    "day": 15,
    "location": "kathmandu_nepal",
    "window_days": 7
  }'
```

**Response:** Same as GET version

---

## Statistics & Analytics

### 1. Monthly Statistics

**Endpoint:** `GET /api/monthly/{month}`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `month` | integer | Yes | Month (1-12) |
| `location` | string | Yes | Location identifier |

**Example Request:**
```bash
curl "http://localhost:8000/api/monthly/7?location=kathmandu_nepal"
```

**Example Response:**
```json
{
  "month": 7,
  "month_name": "July",
  "location": "Kathmandu Nepal",
  "years_covered": 35,

  "rainfall": {
    "rainy_days_percent": 85.2,
    "average_monthly_total_mm": 445.3,
    "wettest_year": {
      "year": 2019,
      "total_mm": 687.2
    },
    "driest_year": {
      "year": 2006,
      "total_mm": 245.1
    }
  },

  "temperature": {
    "average_mean_celsius": 24.2,
    "average_min_celsius": 20.1,
    "average_max_celsius": 28.5
  },

  "wind": {
    "average_speed_ms": 2.4
  },

  "cloud_cover": {
    "average_percent": 72.3
  }
}
```

### 2. Annual Calendar

**Endpoint:** `GET /api/calendar`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `location` | string | Yes | Location identifier |
| `dates_per_month` | integer | No | Predictions per month (1-4, default: 2) |

**Example Request:**
```bash
curl "http://localhost:8000/api/calendar?location=kathmandu_nepal&dates_per_month=2"
```

**IMPORTANT:** The `location` parameter is REQUIRED for this endpoint.

**Example Response:**
```json
{
  "calendar": {
    "01-01": { /* Full prediction object */ },
    "01-15": { /* Full prediction object */ },
    "02-01": { /* Full prediction object */ },
    "02-15": { /* Full prediction object */ },
    ...
  },
  "total_predictions": 24,
  "dates_per_month": 2
}
```

**dates_per_month Options:**
- `1` → 15th of each month (12 predictions)
- `2` → 1st and 15th (24 predictions)
- `3` → 1st, 15th, 28th (36 predictions)
- `4` → 1st, 10th, 20th, 28th (48 predictions)

---

## Data Download

### Download Predictions as JSON File

**Endpoint:** `GET /api/download/predictions`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `location` | string | Yes | Location identifier |
| `start_date` | string | Yes | Start date (YYYY-MM-DD) |
| `end_date` | string | Yes | End date (YYYY-MM-DD) |
| `save_to_file` | boolean | No | Save to output folder (default: true) |

**Example Request:**
```bash
curl "http://localhost:8000/api/download/predictions?location=kathmandu_nepal&start_date=2025-01-01&end_date=2025-12-31" \
  --output weather_predictions_2025.json
```

**Response:** Downloads JSON file

**File Structure:**
```json
{
  "location": "kathmandu_nepal",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "total_predictions": 365,
  "generated_at": "2025-10-02T14:30:00",

  "predictions": {
    "2025-01-01": { /* Full prediction */ },
    "2025-01-02": { /* Full prediction */ },
    ...
  }
}
```

**Additional Features:**
- ✅ File is automatically saved to `output/{location}/predictions_{start}_to_{end}.json`
- ✅ Browser download via `Content-Disposition: attachment` header
- ✅ Generates predictions on-the-fly (always up-to-date)

---

## Response Format

### Success Response

All successful responses return JSON with HTTP 200 status code.

**Example:**
```json
{
  "date": "2026-07-15",
  "location": "Kathmandu Nepal",
  ...
}
```

### Error Response

**Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

**HTTP Status Codes:**
| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid date (month=13, day=32) |
| 404 | Not Found | Location not found, endpoint not found |
| 503 | Service Unavailable | Predictor not loaded, data not available |
| 500 | Internal Server Error | Unexpected error during processing |

---

## Error Handling

### Common Errors

#### 1. Location Not Found
```json
{
  "detail": "Location 'invalid_location' not found. Available: kathmandu_nepal, newyork_usa"
}
```

**Solution:** Check `/api/locations` for valid location names

#### 2. Invalid Date
```json
{
  "detail": "Invalid date: month=13, day=32"
}
```

**Solution:** Use valid month (1-12) and day (1-31)

#### 3. Predictor Not Available
```json
{
  "detail": "Predictor not available: No processed data found"
}
```

**Solution:** Ensure data is processed (run `era5_processing.py`)

---

## Code Examples

### JavaScript (Fetch API)

```javascript
// Get prediction for July 15th in Kathmandu
async function getWeatherPrediction() {
  const response = await fetch(
    'http://localhost:8000/api/predict/7/15?location=kathmandu_nepal&window_days=7'
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  console.log('Weather prediction:', data);
  return data;
}

getWeatherPrediction()
  .then(data => {
    console.log(`Date: ${data.date}`);
    console.log(`Rain probability: ${data.rainfall.probability_percent}%`);
    console.log(`Expected temp: ${data.temperature.mean_avg_celsius}°C`);
  })
  .catch(error => console.error('Error:', error));
```

### JavaScript (Download JSON)

```javascript
// Download predictions for entire year
function downloadPredictions() {
  const url = 'http://localhost:8000/api/download/predictions?' +
    new URLSearchParams({
      location: 'kathmandu_nepal',
      start_date: '2025-01-01',
      end_date: '2025-12-31',
      save_to_file: 'true'
    });

  // Trigger download in browser
  window.open(url, '_blank');
}
```

### Python (requests)

```python
import requests

# Get weather prediction
def get_weather_prediction(month, day, location):
    url = f"http://localhost:8000/api/predict/{month}/{day}"
    params = {
        "location": location,
        "window_days": 7
    }

    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise error for bad status codes

    return response.json()

# Example usage
prediction = get_weather_prediction(7, 15, "kathmandu_nepal")
print(f"Date: {prediction['date']}")
print(f"Rain probability: {prediction['rainfall']['probability_percent']}%")
print(f"Expected temperature: {prediction['temperature']['mean_avg_celsius']}°C")
```

### Python (Download File)

```python
import requests

def download_predictions(location, start_date, end_date):
    url = "http://localhost:8000/api/download/predictions"
    params = {
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "save_to_file": "true"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    # Save to file
    filename = f"predictions_{location}_{start_date}_to_{end_date}.json"
    with open(filename, 'wb') as f:
        f.write(response.content)

    print(f"Downloaded: {filename}")

# Example usage
download_predictions("kathmandu_nepal", "2025-01-01", "2025-12-31")
```

### React Example

```jsx
import React, { useState, useEffect } from 'react';

function WeatherPrediction() {
  const [locations, setLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch available locations on mount
  useEffect(() => {
    fetch('http://localhost:8000/api/locations')
      .then(res => res.json())
      .then(data => {
        setLocations(data.locations);
        if (data.locations.length > 0) {
          setSelectedLocation(data.locations[0]);
        }
      });
  }, []);

  // Fetch prediction
  const fetchPrediction = async (month, day) => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/predict/${month}/${day}?location=${selectedLocation}`
      );
      const data = await response.json();
      setPrediction(data);
    } catch (error) {
      console.error('Error fetching prediction:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Weather Prediction</h1>

      <select
        value={selectedLocation}
        onChange={(e) => setSelectedLocation(e.target.value)}
      >
        {locations.map(loc => (
          <option key={loc} value={loc}>{loc}</option>
        ))}
      </select>

      <button onClick={() => fetchPrediction(7, 15)}>
        Get July 15 Prediction
      </button>

      {loading && <p>Loading...</p>}

      {prediction && (
        <div>
          <h2>Prediction for {prediction.date}</h2>
          <p>Location: {prediction.location}</p>
          <p>Rain Probability: {prediction.rainfall.probability_percent}%</p>
          <p>Expected Rainfall: {prediction.rainfall.expected_amount_mm} mm</p>
          <p>Temperature: {prediction.temperature.mean_avg_celsius}°C</p>
        </div>
      )}
    </div>
  );
}

export default WeatherPrediction;
```

### cURL Examples

```bash
# 1. Check API status
curl http://localhost:8000/api/status

# 2. Get available locations
curl http://localhost:8000/api/locations

# 3. Get weather prediction for July 15
curl "http://localhost:8000/api/predict/7/15?location=kathmandu_nepal"

# 4. Get monthly statistics for July
curl "http://localhost:8000/api/monthly/7?location=kathmandu_nepal"

# 5. Get annual calendar (1st and 15th of each month)
curl "http://localhost:8000/api/calendar?location=kathmandu_nepal&dates_per_month=2"

# 6. Download predictions as JSON file
curl "http://localhost:8000/api/download/predictions?location=kathmandu_nepal&start_date=2025-01-01&end_date=2025-12-31" \
  --output predictions.json

# 7. POST request with JSON body
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "month": 7,
    "day": 15,
    "location": "kathmandu_nepal",
    "window_days": 7
  }'
```

---

## Interactive API Documentation

The API includes built-in interactive documentation powered by FastAPI:

**Swagger UI:** `http://localhost:8000/docs`
- Try out all endpoints directly in your browser
- See request/response schemas
- Test with different parameters

**ReDoc:** `http://localhost:8000/redoc`
- Alternative documentation interface
- Better for reading/reference

---

## Best Practices

### 1. Location Validation
Always fetch available locations first before making prediction requests:

```javascript
const locations = await fetch('/api/locations').then(r => r.json());
// Use locations.locations array for dropdown/validation
```

### 2. Error Handling
Always handle errors gracefully:

```javascript
try {
  const response = await fetch('/api/predict/7/15?location=kathmandu_nepal');

  if (!response.ok) {
    const error = await response.json();
    console.error('API Error:', error.detail);
    return;
  }

  const data = await response.json();
  // Process data
} catch (error) {
  console.error('Network Error:', error);
}
```

### 3. Caching
Predictions for the same date don't change frequently. Consider caching:

```javascript
const cache = new Map();

async function getCachedPrediction(month, day, location) {
  const key = `${location}_${month}_${day}`;

  if (cache.has(key)) {
    return cache.get(key);
  }

  const data = await fetch(
    `/api/predict/${month}/${day}?location=${location}`
  ).then(r => r.json());

  cache.set(key, data);
  return data;
}
```

### 4. Date Formatting
Display dates clearly to users:

```javascript
const prediction = await getPrediction();

// Show both the prediction date and what it's based on
console.log(`Prediction for: ${prediction.date}`);
console.log(`Based on data from: ${prediction.based_on_data_range}`);
console.log(`Analyzed ${prediction.historical_years_analyzed} years`);
```

---

## FAQ

### Q: How accurate are the predictions?
A: Predictions are based on 35 years of historical ERA5 data (1990-2024). The `category_confidence` field indicates reliability (0-1 scale).

### Q: Can I get predictions for past dates?
A: Yes! The API will return the next future occurrence. If you want historical data for a past date, use the `recent_years` field in the response.

### Q: What's the difference between `date` and `month_day`?
A:
- `date`: Next future occurrence (e.g., "2026-07-15")
- `month_day`: Month-day only (e.g., "07-15")

### Q: How often is the data updated?
A: Historical data is static (1990-2024). When new years are added, reprocess the data and restart the API.

### Q: Can I add new locations?
A: Yes! Process data for new locations using `era5_processing.py`. The API auto-discovers new locations on startup.

### Q: What does `window_days` do?
A: Includes dates ±N days around the target date for more robust statistics. Default is 7 days.

---

## Support & Contributions

- **Issues:** Report bugs or request features via your team's issue tracker
- **Questions:** Contact the backend team
- **Documentation:** This guide is maintained in `API_GUIDE.md`

---

## Changelog

### Version 1.0.0 (October 2025)
- ✅ Initial release
- ✅ Multi-location support
- ✅ Future date predictions
- ✅ JSON download functionality
- ✅ Interactive API documentation

---

**Happy Coding! 🚀**
