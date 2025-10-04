# PlanMySky Frontend - React + OpenStreetMap

Interactive weather prediction interface with **FREE** OpenStreetMap (no API key required!).

## 🚀 Features

- **Interactive Maps** - Full-screen map background using OpenStreetMap
- **100% FREE** - No API keys, no credit card required!
- **Click to Select Location** - Click anywhere on the map to get weather predictions
- **Nearest Weather Station** - Automatically finds the closest data point
- **Historical Predictions** - Based on 30+ years of NASA satellite data
- **Beautiful UI** - Modern, responsive design with smooth animations
- **Real-time API Integration** - Connects to FastAPI backend

## 📋 Prerequisites

1. **Node.js** (v16 or higher)
2. **Backend API** running at `http://localhost:8000`
3. ✅ **No API keys needed!**

## 🔧 Setup Instructions

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

### Step 2: Configure Environment (Optional)

Create a `.env` file (only if your backend runs on a different port):

```bash
cp .env.example .env
```

Edit `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### Step 3: Start the Backend API

In a separate terminal:

```bash
cd backend/api
python weather_api.py
```

The backend should be running at `http://localhost:8000`

### Step 4: Start the Frontend

```bash
npm run dev
```

The app will open at `http://localhost:3000`

## 🎯 How to Use

1. **Click on the Map** - Click anywhere on the map to select a location
2. **View Nearest Station** - The app will show:
   - **Red marker** = Your clicked location
   - **Blue marker** = Nearest weather data point
   - **Blue circle** = Coverage area
3. **Select a Date** - Choose a month and day from the dropdowns
4. **Get Prediction** - Click "Get Weather Prediction" to see results
5. **View Results** - Weather prediction appears in a panel on the right

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── MapContainer.jsx       # OpenStreetMap component
│   │   ├── ControlPanel.jsx       # Left sidebar with controls
│   │   ├── DateSelector.jsx       # Month/day picker
│   │   └── WeatherResults.jsx     # Results display panel
│   ├── services/
│   │   └── weatherApi.js          # API calls to backend
│   ├── styles/
│   │   └── App.css                # Global styles + Leaflet
│   ├── App.jsx                    # Main app component
│   └── main.jsx                   # Entry point
├── index.html                     # HTML template
├── vite.config.js                 # Vite configuration
├── package.json                   # Dependencies
└── .env (optional)                # Environment variables
```

## 🗺️ About OpenStreetMap

**OpenStreetMap** is a free, open-source alternative to Google Maps:

- ✅ **100% Free** - No API keys, no limits, no credit card
- ✅ **Open Source** - Community-maintained map data
- ✅ **Full Features** - Markers, circles, popups, etc.
- ✅ **Global Coverage** - Works worldwide
- ✅ **Privacy-Friendly** - No tracking

**Powered by:**
- [Leaflet](https://leafletjs.com/) - Interactive map library
- [React-Leaflet](https://react-leaflet.js.org/) - React components for Leaflet
- [OpenStreetMap](https://www.openstreetmap.org/) - Map tiles

## 🔌 API Integration

The frontend connects to these backend endpoints:

- `GET /api/locations` - Get available weather stations
- `GET /api/predict/{month}/{day}?location={name}` - Get weather prediction
- `GET /api/status` - Check API health

### Example API Call

```javascript
import { getWeatherPrediction, findNearestLocation } from './services/weatherApi';

// Find nearest location to clicked coordinates
const nearest = await findNearestLocation(27.7172, 85.3240);

// Get prediction
const prediction = await getWeatherPrediction(7, 15, nearest.name, 7);
```

## 🎨 Map Features

### Markers

- **Red Marker** 🔴 - Your clicked location
- **Blue Marker** 🔵 - Nearest weather station

### Coverage Circle

- Shows the area covered by the weather station data
- Configurable radius (55-500 km depending on location)
- Semi-transparent blue overlay

### Map Controls

- **Zoom** - Use + / - buttons or scroll wheel
- **Pan** - Click and drag to move around
- **Attribution** - Required OpenStreetMap credit (bottom right)

## 🐛 Troubleshooting

### Issue: Map doesn't load

**Solution:** Check browser console (F12) for errors. Ensure:
```bash
npm install  # Install dependencies
npm run dev  # Start dev server
```

### Issue: "Cannot connect to API"

**Solution:** Make sure the backend is running:

```bash
cd backend/api
python weather_api.py
```

Test: Open `http://localhost:8000/api/status` in browser

### Issue: "No locations available"

**Solution:** You need processed weather data:

```bash
# Download data
cd src/acquisition
python era5_acquisition.py

# Process data
cd ../preprocessing
python era5_processing.py

# Restart backend
cd ../../backend/api
python weather_api.py
```

### Issue: Markers don't appear

**Solution:** This is usually a Leaflet CSS issue. Make sure `App.css` imports Leaflet CSS:
```css
@import 'leaflet/dist/leaflet.css';
```

## 🎨 Customization

### Change Default Map Center

Edit `src/components/MapContainer.jsx`:

```javascript
const defaultCenter = [40.7128, -74.0060]; // New York
const defaultZoom = 10;
```

### Change Map Style

Replace OpenStreetMap with other free tile providers:

```javascript
// Dark mode
<TileLayer
  url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
/>

// Satellite (Esri)
<TileLayer
  url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
  attribution='Tiles &copy; Esri'
/>

// Terrain
<TileLayer
  url="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
  attribution='Map data: &copy; OpenStreetMap contributors, SRTM | Map style: &copy; OpenTopoMap'
/>
```

### Change Colors

Edit component files:
```javascript
background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
```

## 📱 Responsive Design

The app is fully responsive:
- **Desktop:** Side-by-side panels
- **Tablet:** Stacked panels
- **Mobile:** Bottom sheet results

## 🚢 Production Build

```bash
npm run build
```

This creates an optimized production build in the `dist/` folder.

To preview the production build:

```bash
npm run preview
```

## 🌍 Alternative Map Providers (All Free!)

If you want different map styles:

1. **Carto** - Clean, minimal design
2. **Esri** - Satellite imagery
3. **OpenTopoMap** - Topographic maps
4. **Stamen** - Artistic, watercolor maps

All are free and don't require API keys!

## 🔐 Security Notes

- **No API keys to protect** - OpenStreetMap is completely open
- **CORS** - Backend has CORS enabled for development
- **Environment variables** - Only needed for backend URL (if different)

## 🔄 Backend Configuration

If your backend runs on a different port, update `.env`:

```env
VITE_API_BASE_URL=http://localhost:8080
```

Or use the Vite proxy (already configured in `vite.config.js`):

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  }
}
```

## 📊 Technologies Used

- **React 18** - UI framework
- **Vite** - Build tool (fast!)
- **Leaflet** - Map library
- **React-Leaflet** - React wrapper for Leaflet
- **Axios** - HTTP client
- **OpenStreetMap** - Free map tiles

## ✅ Testing Checklist

- [ ] Map loads successfully
- [ ] Click on map shows red marker
- [ ] Blue marker shows nearest weather station
- [ ] Coverage circle appears around station
- [ ] Date selectors work
- [ ] "Get Weather Prediction" button enabled after selecting location
- [ ] Results panel appears on right side
- [ ] Can close results panel with X button
- [ ] Loading spinner appears during API calls

## 🎓 Learning Resources

- [React Docs](https://react.dev/)
- [Leaflet Documentation](https://leafletjs.com/)
- [React-Leaflet Docs](https://react-leaflet.js.org/)
- [OpenStreetMap](https://www.openstreetmap.org/)
- [Vite Guide](https://vitejs.dev/guide/)

## 🆚 Why OpenStreetMap vs Google Maps?

| Feature | OpenStreetMap | Google Maps |
|---------|---------------|-------------|
| Cost | 100% Free | Requires credit card |
| API Key | Not needed | Required |
| Usage Limits | None | $200 credit/month |
| Privacy | Open source | Tracks users |
| Setup Time | 2 minutes | 15+ minutes |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - See main project README

## 📞 Support

For issues or questions:
- Check existing GitHub issues
- Create a new issue with details
- Contact: panchanarayansahu00@gmail.com

---

**Made with ❤️ for NASA Space Apps Challenge**

**No credit card required! 🎉**
