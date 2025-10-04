# 🗺️ Simple Map Version - Console Output

Simplified version with just the interactive map. Results are logged to browser console.

## 📂 Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── MapContainer.jsx    ← OpenStreetMap component
│   ├── services/
│   │   └── weatherApi.js       ← API calls
│   ├── styles/
│   │   └── App.css             ← Minimal styles
│   ├── App.jsx                 ← Main app (console logging)
│   └── main.jsx                ← Entry point
└── package.json
```

## 🚀 Quick Start

```bash
# 1. Install
cd frontend
npm install

# 2. Start backend
cd ../backend/api
python weather_api.py

# 3. Start frontend
cd ../../frontend
npm run dev

# 4. Open http://localhost:3000
# 5. Open browser console (F12)
```

## 🎯 How It Works

1. **Click on map** 🗺️
   - Red marker appears at clicked location

2. **Backend finds nearest station** 📍
   - Blue marker appears at weather station
   - Blue circle shows coverage area

3. **Auto-fetches weather** 🌤️
   - Currently hardcoded to July 15
   - You can change this in `App.jsx` lines 32-33

4. **Results in console** 📊
   - Open F12 to see formatted weather data
   - Full prediction object included

## 📋 Console Output Example

```
📍 Location clicked: {lat: 27.7172, lng: 85.324}

✅ Nearest weather station found:
📊 Station details: {
  name: "sunsari_nepal",
  display_name: "Sunsari, Nepal",
  distance: "0.00 km",
  coverage: "55 km"
}

🌤️ Fetching weather prediction for 7/15...

✅ Weather Prediction Received:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Date: 2026-07-15
📍 Location: Sunsari, Nepal
🌦️ Category: Moderate Rain Expected
📊 Confidence: 73%

☔ Rain:
  - Probability: 73%
  - Expected: 12.5 mm

🌡️ Temperature:
  - Range: 24°C - 32°C
  - Average: 28.5°C

💨 Wind: 3.2 m/s
☁️ Cloud Cover: 65%

⚠️ Extreme Probabilities:
  - Temp > 30°C: 42%
  - Heavy Rain: 25%
  - High Wind: 15%

📚 Based on: 35 years
📊 Observations: 245
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Full prediction object: {...}
```

## 🔧 Customization

### Change Default Date

Edit `src/App.jsx` (lines 32-33):

```javascript
// Change from July 15 to any date
const month = 8;  // August
const day = 1;    // 1st
```

### Remove Auto-Fetch

If you want to manually trigger predictions later:

```javascript
// Comment out lines 31-66 in App.jsx
// Just log the location and station
console.log('Station found:', nearest);
```

### Change Map Center

Edit `src/components/MapContainer.jsx` (line 14):

```javascript
const defaultCenter = [40.7128, -74.0060]; // New York
```

## 🎨 Map Features

**Markers:**
- 🔴 Red = Clicked location
- 🔵 Blue = Nearest weather station

**Circle:**
- Shows coverage area of weather station
- Radius = station's coverage in km

**Controls:**
- Zoom: Mouse wheel or +/- buttons
- Pan: Click and drag

## 📊 Data Available in Console

From the prediction object, you can access:

```javascript
prediction.date                          // Future date (e.g., "2026-07-15")
prediction.location                      // Location name
prediction.weather_category              // Category (e.g., "Moderate Rain")
prediction.category_confidence           // 0-1 confidence score

prediction.rainfall.probability_percent  // 0-100
prediction.rainfall.expected_amount_mm   // mm of rain

prediction.temperature.mean_avg_celsius  // Average temp
prediction.temperature.expected_range    // {min, max}

prediction.wind.mean_speed_ms            // m/s
prediction.cloud_cover.mean_percent      // 0-100

prediction.extreme_probabilities         // Various thresholds
prediction.historical_years_analyzed     // Years of data
prediction.total_observations            // Number of observations
```

## 🔌 Next Steps for Custom UI

When you're ready to add your custom design:

1. **Keep the map** - `MapContainer.jsx` is ready to use
2. **Keep the API service** - `weatherApi.js` has all needed functions
3. **Modify App.jsx** - Replace console.log with your UI components

Example:

```javascript
// Instead of console.log
const prediction = await getWeatherPrediction(...);

// Call your custom UI function
showCustomWeatherPanel(prediction);
```

## 🎯 API Functions Available

From `weatherApi.js`:

```javascript
import {
  findNearestLocation,    // Find nearest station
  getWeatherPrediction,   // Get weather data
  getLocations,           // Get all stations
  getMonthlyStats         // Get monthly stats
} from './services/weatherApi';

// Usage:
const nearest = await findNearestLocation(lat, lng);
const weather = await getWeatherPrediction(month, day, locationName);
```

## 🐛 Troubleshooting

**No console output:**
- Press F12 to open browser console
- Check "Console" tab
- Refresh page

**API errors:**
- Make sure backend is running on port 8000
- Check: http://localhost:8000/api/status

**Map not loading:**
- Clear browser cache
- Check browser console for errors
- Verify Leaflet CSS is loaded

## 💡 Tips

**Better Console Viewing:**
- Right-click console → "Save as..."
- Copy logged objects for analysis
- Use console filters to show only errors

**Testing Different Locations:**
- Click around the map
- Each click auto-fetches weather
- Check console for results

**Performance:**
- First click may be slower (loading data)
- Subsequent clicks are faster (cached)

---

**Ready to add your custom UI? The map and API are ready! 🚀**
