# 🔗 Frontend-Backend Integration Guide

Complete guide for connecting React frontend with FastAPI backend.

## 🏗️ Architecture Overview

```
User clicks on Google Map
        ↓
Frontend captures lat/lng coordinates
        ↓
Find nearest weather station (from /api/locations)
        ↓
User selects date (month + day)
        ↓
API call: GET /api/predict/{month}/{day}?location={name}
        ↓
Backend processes with HistoricalWeatherPredictor
        ↓
Returns probability data
        ↓
Frontend displays results in panel
```

## 📊 Data Flow

### 1. Location Selection

**Frontend:**
```javascript
// User clicks map at (27.7172, 85.3240)
const clickedLocation = { lat: 27.7172, lng: 85.3240 };

// Find nearest weather station
const nearest = await findNearestLocation(lat, lng);
// Returns: { name: "sunsari_nepal", latitude: 27.7172, longitude: 85.3240, distance: 0.5 }
```

**Backend Endpoint:**
```
GET /api/locations
```

**Response:**
```json
{
  "locations": [
    {
      "name": "sunsari_nepal",
      "display_name": "Sunsari, Nepal",
      "latitude": 27.7172,
      "longitude": 85.3240,
      "coverage_km": 55,
      "data_start": "1990-01-01",
      "data_end": "2024-12-31"
    }
  ],
  "total": 1
}
```

### 2. Weather Prediction Request

**Frontend:**
```javascript
const prediction = await getWeatherPrediction(
  7,              // month (July)
  15,             // day
  "sunsari_nepal", // location name
  7               // window_days
);
```

**Backend Endpoint:**
```
GET /api/predict/7/15?location=sunsari_nepal&window_days=7
```

**Backend Processing:**
1. Load predictor for `sunsari_nepal`
2. Query historical data for all July 15th dates (1990-2024)
3. Calculate statistics:
   - Rainfall probability
   - Temperature ranges
   - Wind speeds
   - Cloud cover
   - Extreme weather probabilities
4. Return aggregated prediction

**Response:**
```json
{
  "date": "2026-07-15",
  "month_day": "07-15",
  "location": "Sunsari, Nepal",
  "prediction_type": "historical_pattern",
  "based_on_data_range": "1990-2024",
  "historical_years_analyzed": 35,
  "total_observations": 245,
  "weather_category": "Moderate Rain Expected",
  "category_confidence": 0.73,
  "rainfall": {
    "probability_percent": 73,
    "expected_amount_mm": 12.5,
    "probability_light_rain": 0.45,
    "probability_moderate_rain": 0.28,
    "probability_heavy_rain": 0.12
  },
  "temperature": {
    "mean_avg_celsius": 28.5,
    "expected_range": {
      "min": 24,
      "max": 32
    }
  },
  "wind": {
    "mean_speed_ms": 3.2
  },
  "cloud_cover": {
    "mean_percent": 65
  },
  "extreme_probabilities": {
    "temp_above_30C": 0.42,
    "heavy_rain_above_10mm": 0.25,
    "high_wind_above_5ms": 0.15
  }
}
```

### 3. Display Results

**Frontend:**
```javascript
// WeatherResults component receives data
<WeatherResults data={prediction} location={nearestLocation} />

// Displays:
// - Date: "Jul 15, 2026"
// - Location: "Sunsari, Nepal (0.5 km away)"
// - Weather Category: "Moderate Rain Expected" (73% confidence)
// - Rain: 73% probability, 12.5 mm expected
// - Temperature: 24-32°C
// - Wind: 3.2 m/s
// - Cloud: 65%
// - Alerts: High temperature, Heavy rain warnings
```

## 🔄 Complete Request Flow Example

### Scenario: User in Kathmandu wants weather for August 1st

```javascript
// Step 1: User clicks on Kathmandu (27.7172, 85.3240)
handleMapClick({ lat: 27.7172, lng: 85.3240 });

// Step 2: Frontend finds nearest location
const locations = await fetch('/api/locations').then(r => r.json());
// Calculate distances using Haversine formula
const nearest = findClosest(27.7172, 85.3240, locations.locations);
// Result: "kathmandu_nepal" at 0.2 km distance

// Step 3: User selects August 1st
setMonth(8);
setDay(1);

// Step 4: User clicks "Get Weather Prediction"
const prediction = await fetch(
  '/api/predict/8/1?location=kathmandu_nepal&window_days=7'
).then(r => r.json());

// Step 5: Display results
setWeatherData(prediction);
setShowResults(true);
```

## 🛠️ API Integration Code

### weatherApi.js Service

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' }
});

// Get all available locations
export const getLocations = async () => {
  const response = await api.get('/api/locations');
  return response.data;
};

// Find nearest location to coordinates
export const findNearestLocation = async (lat, lon) => {
  const { locations } = await getLocations();

  // Calculate distance to each location
  const withDistances = locations.map(loc => ({
    ...loc,
    distance: calculateDistance(lat, lon, loc.latitude, loc.longitude)
  }));

  // Return nearest
  return withDistances.sort((a, b) => a.distance - b.distance)[0];
};

// Get weather prediction
export const getWeatherPrediction = async (month, day, location, windowDays = 7) => {
  const response = await api.get(`/api/predict/${month}/${day}`, {
    params: { location, window_days: windowDays }
  });
  return response.data;
};

// Haversine formula for distance
const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371; // Earth radius in km
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);

  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
            Math.sin(dLon/2) * Math.sin(dLon/2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
};

const toRad = (deg) => deg * Math.PI / 180;
```

## 🎯 Error Handling

### Frontend Error Handling

```javascript
try {
  const prediction = await getWeatherPrediction(month, day, location);
  setWeatherData(prediction);
} catch (error) {
  if (error.response?.status === 404) {
    setError('Location not found. Please select a different location.');
  } else if (error.response?.status === 503) {
    setError('Weather service unavailable. Please try again later.');
  } else {
    setError(error.response?.data?.detail || 'Failed to get prediction');
  }
}
```

### Backend Error Responses

```python
# Location not found
raise HTTPException(
    status_code=404,
    detail=f"Location '{location}' not found. Available: {', '.join(available_locations)}"
)

# Invalid date
raise HTTPException(
    status_code=400,
    detail=f"Invalid date: month={month}, day={day}"
)

# Predictor not loaded
raise HTTPException(
    status_code=503,
    detail="Predictor not available: No processed data found"
)
```

## 🔍 Testing the Integration

### 1. Test Backend

```bash
# Start backend
cd backend/api
python weather_api.py

# Test in browser
http://localhost:8000/api/status
http://localhost:8000/api/locations
http://localhost:8000/api/predict/7/15?location=sunsari_nepal
```

### 2. Test Frontend

```bash
# Start frontend
cd frontend
npm run dev

# Open browser
http://localhost:3000
```

### 3. Integration Test Checklist

- [ ] Backend `/api/status` returns 200 OK
- [ ] Backend `/api/locations` returns location list
- [ ] Frontend loads Google Maps
- [ ] Clicking map makes API call to `/api/locations`
- [ ] Nearest location marker appears on map
- [ ] Coverage circle visible around location
- [ ] Date selector enables after location selected
- [ ] Prediction button makes correct API call
- [ ] Results panel displays prediction data
- [ ] All weather metrics display correctly
- [ ] Close button works
- [ ] Loading spinner appears during requests

## 🐛 Common Integration Issues

### Issue: CORS Error

**Symptom:** Console shows "CORS policy blocked"

**Solution:** Backend CORS is already configured, but verify:

```python
# backend/api/weather_api.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: 404 Not Found on API calls

**Symptom:** Network tab shows 404 for `/api/predict/...`

**Solution:** Check:
1. Backend is running: `http://localhost:8000`
2. Frontend `.env` has correct URL: `VITE_API_BASE_URL=http://localhost:8000`
3. API endpoint exists in backend

### Issue: Location not found

**Symptom:** Error: "Location 'xxx' not found"

**Solution:**
1. Check available locations: `GET /api/locations`
2. Ensure data is processed: `cd src/preprocessing && python era5_processing.py`
3. Restart backend to reload locations

### Issue: No data in response

**Symptom:** Prediction returns but fields are empty/undefined

**Solution:**
1. Check backend logs for errors
2. Verify data file exists: `data/processed/{location}/`
3. Test backend directly: `curl http://localhost:8000/api/predict/7/15?location=sunsari_nepal`

## 📡 Network Inspection

### Chrome DevTools

1. Open DevTools (F12)
2. Go to Network tab
3. Click on map, select date, get prediction
4. Inspect requests:

**GET /api/locations**
```
Status: 200 OK
Response Time: ~50ms
Size: 1.2 KB
```

**GET /api/predict/7/15?location=sunsari_nepal&window_days=7**
```
Status: 200 OK
Response Time: ~200ms
Size: 3.5 KB
Payload: { date: "2026-07-15", ... }
```

## 🚀 Performance Optimization

### Frontend
- Debounce map clicks
- Cache location data
- Lazy load results component
- Use React.memo for components

### Backend
- Pre-load all predictors on startup ✅ (already done)
- Cache predictions in memory
- Use Parquet for faster data loading ✅ (already done)

## 🔐 Production Configuration

### Frontend .env.production

```env
VITE_GOOGLE_MAPS_API_KEY=your_production_key
VITE_API_BASE_URL=https://api.planmysky.com
```

### Backend CORS Update

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://planmysky.com",
        "https://www.planmysky.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Data Validation

### Frontend validates:
- Month: 1-12
- Day: 1-31 (adjusted for month)
- Location selected before prediction

### Backend validates:
- Valid date (datetime check)
- Location exists in available_locations
- Predictor loaded successfully

## ✅ Success Criteria

Integration is successful when:

1. ✅ Click map → See location marker
2. ✅ See nearest station marker + coverage circle
3. ✅ Select date → Button enables
4. ✅ Click button → Loading spinner appears
5. ✅ Results panel slides in from right
6. ✅ All weather data displays correctly
7. ✅ Close button works
8. ✅ Can select new location and repeat

## 🎓 Next Steps

- Add location search bar
- Save favorite locations
- Compare multiple dates
- Export predictions to PDF
- Add historical charts
- Mobile app version

---

**Integration Complete! 🎉**

For issues, check:
- Backend logs: Terminal running `weather_api.py`
- Frontend console: Browser DevTools (F12)
- Network tab: Inspect API calls
