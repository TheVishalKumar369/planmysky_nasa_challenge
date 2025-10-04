# 🚀 Quick Start Guide - PlanMySky Frontend (FREE!)

Get your React + OpenStreetMap frontend running in **3 EASY STEPS**!

## ✨ What's New?

- ✅ **100% FREE** - No API keys needed!
- ✅ **No Credit Card** - OpenStreetMap is completely free
- ✅ **2-Minute Setup** - Just install and run!

---

## ⚡ Quick Setup

### 1️⃣ Install Dependencies

```bash
cd frontend
npm install
```

**That's it for configuration!** No API keys, no registration, nothing!

### 2️⃣ Start Backend API

**Terminal 1:**
```bash
cd backend/api
python weather_api.py
```

Should see:
```
PlanMySky Weather API
Starting server...
API Documentation: http://localhost:8000/docs
✓ Loaded predictor for sunsari_nepal
✓ Ready! All 1 location(s) loaded
```

### 3️⃣ Start Frontend

**Terminal 2:**
```bash
cd frontend
npm run dev
```

Should see:
```
VITE ready in 500 ms
➜  Local:   http://localhost:3000/
```

### 4️⃣ Open App

Open browser: **http://localhost:3000**

🎉 **You should see an interactive map!**

---

## 🎯 How to Use

1. **Click on Map** 🗺️
   - Click anywhere on the world map
   - Red marker appears at clicked location

2. **See Nearest Station** 📍
   - Blue marker shows nearest weather data point
   - Blue circle shows coverage area (radius in km)

3. **Pick Date** 📅
   - Select month and day from dropdowns

4. **Get Prediction** 🌤️
   - Click "Get Weather Prediction" button
   - Loading spinner appears

5. **View Results** 📊
   - Results panel slides in from right
   - Shows detailed weather prediction

6. **Try Again** 🔄
   - Click X to close results
   - Click new location on map
   - Select different date

---

## ✅ Quick Test

After starting the app:

- [ ] Map loads and shows the world
- [ ] Can zoom in/out with mouse wheel
- [ ] Can drag to pan the map
- [ ] Click shows red marker
- [ ] Blue marker appears nearby
- [ ] Coverage circle visible
- [ ] Date dropdowns work
- [ ] Prediction button works
- [ ] Results panel appears

---

## 🗺️ Map Features

### What You'll See:

**Red Marker (🔴)**
- Your clicked location
- Exact coordinates you selected

**Blue Marker (🔵)**
- Nearest weather station
- Has historical data available

**Blue Circle**
- Coverage area of weather station
- Typically 55-222 km radius

**Map Controls**
- `+` / `-` buttons to zoom
- Drag to pan around
- Mouse wheel to zoom

---

## 🐛 Common Issues

### Map is blank/white

**Check:**
```bash
# Make sure you installed dependencies
npm install

# Restart dev server
npm run dev
```

**Browser console (F12):**
- Look for red errors
- Most common: CSS not loaded

**Fix:** Clear browser cache (Ctrl+Shift+Delete)

### "Cannot connect to API"

**Check backend is running:**
```bash
# Terminal 1 should show:
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test backend directly:**
- Open: http://localhost:8000/api/status
- Should return JSON with status

**Fix:** Restart backend:
```bash
cd backend/api
python weather_api.py
```

### "No locations available"

**You need weather data!**

```bash
# 1. Download data
cd src/acquisition
python era5_acquisition.py
# Enter: Sunsari, Nepal
# Coordinates: 27.7172, 85.3240
# Coverage: 1 (55 km)
# Years: 2020-2024 (for quick test)

# 2. Process data
cd ../preprocessing
python era5_processing.py
# Select: sunsari_nepal
# Process all years

# 3. Restart backend
cd ../../backend/api
python weather_api.py
```

### Markers don't show

**This is a Leaflet CSS issue:**

1. Check `src/styles/App.css` has:
```css
@import 'leaflet/dist/leaflet.css';
```

2. Restart dev server:
```bash
npm run dev
```

---

## 📂 What Got Installed?

```bash
npm install
```

Installs these packages:

- **react** - UI framework
- **react-leaflet** - Map components
- **leaflet** - Map library
- **axios** - API calls
- **vite** - Build tool

**Total size:** ~150 MB (includes node_modules)

**No API keys. No registration. No credit card. 🎉**

---

## 🎨 Try Different Map Styles

Edit `src/components/MapContainer.jsx`:

### Dark Mode Map:
```javascript
<TileLayer
  url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
  attribution='&copy; OpenStreetMap &copy; CARTO'
/>
```

### Satellite View:
```javascript
<TileLayer
  url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
  attribution='Tiles &copy; Esri'
/>
```

### Terrain Map:
```javascript
<TileLayer
  url="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
  attribution='&copy; OpenStreetMap contributors, SRTM | OpenTopoMap'
/>
```

All are **FREE!** Just change the URL and restart.

---

## 🔍 Debugging Tips

### Check Browser Console (F12)

**No errors** = Everything working ✅

**Common errors:**

```
Failed to fetch /api/locations
→ Backend not running

Unexpected token < in JSON
→ Backend returned HTML instead of JSON (check backend logs)

Network error
→ CORS issue or backend offline
```

### Check Network Tab (F12 → Network)

Click on map → Should see:

```
GET /api/locations → 200 OK
```

Select date → Click button → Should see:

```
GET /api/predict/7/15?location=sunsari_nepal → 200 OK
```

---

## 📊 File Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── MapContainer.jsx     ← Map with OpenStreetMap
│   │   ├── ControlPanel.jsx     ← Left sidebar
│   │   ├── DateSelector.jsx     ← Date picker
│   │   └── WeatherResults.jsx   ← Results panel
│   ├── services/
│   │   └── weatherApi.js        ← API integration
│   ├── styles/
│   │   └── App.css              ← Styles + Leaflet CSS
│   ├── App.jsx                  ← Main app
│   └── main.jsx                 ← Entry point
├── package.json                 ← Dependencies
├── vite.config.js              ← Build config
└── index.html                   ← HTML template
```

---

## 🚀 Next Steps

Once the app is running:

1. ✅ Test with your local area
2. ✅ Try different dates (monsoon season vs dry season)
3. ✅ Check results accuracy
4. ✅ Customize colors/styling
5. ✅ Add more locations to backend

---

## 🆚 Google Maps vs OpenStreetMap

We switched to **OpenStreetMap** because:

| Feature | Google Maps | OpenStreetMap |
|---------|-------------|---------------|
| **Cost** | $$ (credit card required) | **FREE!** |
| **API Key** | Required | **None needed** |
| **Setup Time** | 15+ minutes | **2 minutes** |
| **Limits** | $200/month credit | **Unlimited** |
| **Privacy** | Tracks users | **No tracking** |

**OpenStreetMap = Perfect for students & open source projects!**

---

## 💡 Pro Tips

### Faster Testing

Start both backend and frontend at once:

**Windows (PowerShell):**
```powershell
# Terminal 1
cd backend/api; python weather_api.py

# Terminal 2
cd frontend; npm run dev
```

**Linux/Mac:**
```bash
# Use tmux or screen for multiple terminals
```

### Quick Restart

If something breaks:

```bash
# Stop everything (Ctrl+C in both terminals)
# Then restart:

# Terminal 1
cd backend/api && python weather_api.py

# Terminal 2
cd frontend && npm run dev
```

### Clear Cache

If map looks weird:

1. **Browser cache:** Ctrl+Shift+Delete → Clear cached images
2. **Node modules:** `rm -rf node_modules && npm install`
3. **Vite cache:** Delete `node_modules/.vite`

---

## ✨ Success Criteria

You're ready when:

- ✅ Map loads without errors
- ✅ Can click and see markers
- ✅ Date selection works
- ✅ Predictions display correctly
- ✅ No console errors (F12)

---

## 📞 Need Help?

**Still stuck?**

1. Check `frontend/README.md` for detailed docs
2. Check GitHub Issues
3. Ask in project discussions
4. Email: panchanarayansahu00@gmail.com

**Include:**
- Screenshot of error
- Browser console output (F12)
- Steps you tried

---

## 🎉 You're Done!

**Congratulations!** You now have a fully functional weather prediction app with:

- ✅ Interactive world map
- ✅ Click-to-predict functionality
- ✅ Beautiful UI
- ✅ Real-time API integration
- ✅ **No cost, no API keys, no hassle!**

**Happy coding! 🚀**

---

**Made with ❤️ for NASA Space Apps Challenge**
