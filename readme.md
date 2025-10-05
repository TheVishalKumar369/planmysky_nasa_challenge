# PlanMySky 🌤️

**Tagline:** *Empowering outdoor planning with historical weather probabilities and community insights.*

---

## 🌍 Overview

PlanMySky is a **web-based platform** that combines historical NASA weather data with probability modeling to help users make informed decisions about outdoor activities. Unlike traditional forecasts that only predict a few days ahead, PlanMySky calculates **empirical probabilities** for weather conditions based on **30+ years of historical data**, allowing users to plan months or even a year in advance.

The platform features an **interactive map interface**, **real-time community hub**, **comprehensive weather visualizations**, and **social engagement tools** to enhance weather planning with human insights.

---

## 🎯 Core Problem Being Solved

**Traditional weather forecasts have limitations:**
- Only accurate for 7-10 days ahead
- Can't help with long-term planning (weddings, events, trips)
- Don't provide historical probability insights
- Lack community-driven context

**PlanMySky solves this by:**
- ✅ Providing **historical probability patterns** for any future date
- ✅ Analyzing **30+ years** of NASA ERA5 data (1990-2024)
- ✅ Offering **statistical confidence levels** based on historical trends
- ✅ Adding **community insights** - what are real people experiencing right now?
- ✅ Enabling **smart planning** for outdoor events months in advance

**Example Use Cases:**
- Planning a wedding 6 months from now? Check historical weather probabilities for that date.
- Organizing an outdoor festival? See what the weather was typically like on similar dates.
- Traveling next year? Know the historical rain probability and temperature ranges.

---

## ✨ Key Features

### 1. **Interactive Map Interface** 🗺️

**Modern, User-Friendly Design:**
- **Click anywhere** on the world map to get weather predictions
- **Search functionality** for specific locations by name
- **Visual markers** showing:
  - Selected location (blue pin)
  - Nearest weather station (red circle with coverage radius)
  - Distance calculation from clicked point to station
- **Real-time feedback** with smooth animations
- **Coverage area visualization** showing weather station radius

**Powered by:**
- Leaflet.js for interactive maps
- OpenStreetMap tiles
- Custom React components for seamless integration

### 2. **Historical Weather Predictions** 🌦️

**Probability-Based Analysis:**
- Select **any future date** using an intuitive date picker
- Get predictions based on **30+ years** of historical patterns (1990-2024)
- **Date window matching:** Uses ±7 days around target date for better statistics

**Statistical Insights Include:**
- **Rainfall Probability:** Percentage chance of rain and expected amount (mm)
- **Temperature Ranges:** Min/max/average with percentiles (10th, 25th, 75th, 90th)
- **Wind Statistics:** Mean wind speed and extreme wind probabilities
- **Cloud Cover:** Average cloud percentage
- **Extreme Weather Probabilities:**
  - Temperature above 30°C
  - Heavy rain (>10mm)
  - High wind (>5m/s)

**Confidence Scoring:**
- Based on data availability and historical variability
- Recent 5-year trends comparison
- Number of historical observations used

### 3. **Weather Visualizations** 📊

**Interactive Charts & Graphs:**
- **Rainfall Probability Chart:** Bar chart showing daily rain likelihood
- **Temperature Range Chart:** Visual representation of min/max/average temperatures
- **Wind Speed Chart:** Historical wind patterns
- **Statistical Tables:** Detailed breakdowns with percentiles
- **Recent Years Comparison:** See trends from last 5 years

**Export Capabilities:**
- **Download as JSON:** Raw data for further analysis
- **Download as PNG:** High-quality chart images for presentations
- All charts exportable individually or together

### 4. **Community Hub** 💬 **(NEW!)**

**Real-Time Weather Sharing:**

**Post Messages:**
- Share current weather experiences from your location
- Username and location tagging
- Up to 500 characters per message
- Automatic timestamps
- Optional GPS coordinates

**React to Posts:**
- 👍 **Like** - General approval
- ☀️ **Sunny** - Beautiful weather report
- 🌧 **Rain** - Rainy conditions
- 💨 **Wind** - Windy weather

**Reaction Features:**
- One reaction per user per message
- Click to toggle on/off
- Real-time count updates
- Persistent storage in database

**Community Statistics Dashboard:**
- Total messages count
- Activity in last 24 hours
- Total reactions across all posts
- **Top Active Locations** - Interactive pie chart
- Location breakdown with message counts
- **Auto-refresh** every 30 seconds

**Message Management:**
- Delete your own posts
- View all community messages with pagination
- Filter by location (planned feature)

### 5. **Google Calendar Integration** 📅

**Seamless Event Planning:**
- OAuth 2.0 authentication for secure access
- View your Google Calendar events
- Add weather-based events directly from predictions
- Sync planned outdoor activities
- Smart recommendations based on historical weather

**Features:**
- Secure token storage
- Auto-refresh tokens
- Calendar event creation with weather context

### 6. **Social Features** 👥

**Weather Survey System:**
- Share your outdoor activity plans
- Vote on weather-related polls
- See community trends and preferences
- Aggregated social insights alongside predictions

**User Dashboard:**
- Personal profile management
- View your weather history
- Track your calendar integrations
- Manage account settings

### 7. **User Authentication** 🔐

**Secure Access:**
- JWT-based authentication
- User registration and login
- Protected routes for personalized features
- Secure password handling
- Session management

---

## 🏗️ Architecture & Tech Stack

### **Frontend**

**Framework & Libraries:**
- **React 18.2** - Modern UI library with hooks
- **Vite** - Fast build tool and dev server
- **Leaflet** - Interactive map rendering
- **React-Leaflet** - React bindings for Leaflet
- **Recharts** - Data visualization and charts
- **Axios** - HTTP client for API calls
- **HTML2Canvas** - Export charts as images
- **Date-fns** - Date manipulation and formatting

**Design Philosophy:**
- Clean, intuitive interface
- Mobile-responsive design
- Fast load times
- Smooth animations
- Accessibility-focused

**Key Components:**
- `MapContainer.jsx` - Interactive map interface
- `ResultsPanel.jsx` - Main results display with tabs
- `WeatherPredictionTab.jsx` - Probability charts and statistics
- `WeatherStatsTab.jsx` - Detailed weather breakdown
- `MiniPosts.jsx` - Community message feed
- `LocalTrends.jsx` - Community statistics dashboard
- `DatePicker.jsx` - Custom date selection
- `SearchBar.jsx` - Location search functionality
- `HamburgerMenu.jsx` - Navigation and settings

### **Backend**

**Framework:**
- **FastAPI** - Modern Python web framework
  - Async/await support
  - Automatic API documentation
  - High performance
  - Type hints and validation

**Core Libraries:**
- **Motor** - Async MongoDB driver
- **PyMongo** - MongoDB integration
- **Pydantic** - Data validation and serialization
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computations
- **PyArrow** - Parquet file handling
- **Python-dotenv** - Environment variable management

**Authentication & OAuth:**
- **PyJWT** - JWT token generation/validation
- **Google Auth Libraries** - OAuth 2.0 flow
- **Google API Python Client** - Calendar API integration

**API Endpoints:**

**Weather Prediction Endpoints:**
```
GET  /api/status                              # API status and available locations
GET  /api/locations                           # List all locations with metadata
GET  /api/predict/{month}/{day}               # Get weather prediction
POST /api/predict                             # Get prediction (POST method)
GET  /api/monthly/{month}                     # Monthly statistics
GET  /api/calendar                            # Annual calendar predictions
GET  /api/download/predictions                # Download predictions as JSON
```

**Community Hub Endpoints:**
```
GET    /api/community/messages                # Get messages (paginated)
POST   /api/community/messages                # Create new message
POST   /api/community/reactions               # Add/update/remove reaction
GET    /api/community/messages/{id}           # Get specific message
DELETE /api/community/messages/{id}           # Delete message (owner only)
GET    /api/community/stats                   # Community statistics
```

**Authentication Endpoints:**
```
POST /api/auth/register                       # User registration
POST /api/auth/login                          # User login
GET  /api/auth/me                             # Get current user info
```

**Google Calendar Endpoints:**
```
GET  /api/calendar/auth                       # Initiate OAuth flow
GET  /api/calendar/auth/callback              # OAuth callback
GET  /api/calendar/events                     # Get calendar events
POST /api/calendar/events                     # Create calendar event
```

**Survey Endpoints:**
```
POST /api/survey/submit                       # Submit weather survey
GET  /api/survey/results                      # Get survey results
```

### **Database**

**MongoDB Atlas:**
- Cloud-hosted NoSQL database
- Free tier available (M0 - 512MB)
- Async operations for better performance

**Collections:**

**`users` Collection:**
```javascript
{
  _id: ObjectId,
  username: String,
  email: String,
  password_hash: String,
  created_at: DateTime,
  preferences: Object
}
```

**`community_messages` Collection:**
```javascript
{
  _id: ObjectId,
  username: String,
  location: String,
  text: String,              // Max 500 characters
  latitude: Float,           // Optional
  longitude: Float,          // Optional
  timestamp: ISODateTime
}
```

**`message_reactions` Collection:**
```javascript
{
  _id: ObjectId,
  message_id: String,        // Reference to message
  user_identifier: String,   // Username or session ID
  reaction_type: String,     // "like", "sun", "rain", "wind"
  timestamp: ISODateTime
}
```

---

## 📊 Data Sources & Methodology

### **Data Sources**

**Primary Dataset: NASA ERA5 Reanalysis Data**

**Important Note:** We initially planned to use **MERRA-2** dataset but **shifted to ERA5** in the final implementation due to:
- ✅ Better spatial resolution
- ✅ More complete temporal coverage
- ✅ Higher accuracy for surface variables
- ✅ Better documented API access
- ✅ More suitable for historical pattern analysis

**ERA5 Dataset Details:**
- **Provider:** European Centre for Medium-Range Weather Forecasts (ECMWF) via NASA
- **Time Period:** 1990-2024 (30+ years)
- **Resolution:** Daily statistics aggregated from hourly data
- **Format:** Parquet files for efficient storage and querying
- **Coverage:** Global, with specific location-based extracts

**Variables Collected:**
- **Temperature:**
  - 2m temperature (°C)
  - Daily minimum temperature
  - Daily maximum temperature
  - Daily mean temperature

- **Precipitation:**
  - Total precipitation (mm/day)
  - Precipitation intensity
  - Rain/snow differentiation

- **Wind:**
  - 10m wind speed (m/s)
  - 100m wind speed
  - Wind gust peaks

- **Atmospheric:**
  - Cloud cover (%)
  - Surface pressure (hPa)
  - Specific humidity
  - Relative humidity

**Spatial Coverage:**
- Multiple global locations available
- Current locations:
  - Kathmandu, Nepal
  - Bangalore, India
  - (Expandable to any location)

### **Data Processing Pipeline**

**1. Data Acquisition:**
```
NASA GES DISC → ERA5 Hourly Data → API Query by Lat/Lon
```

**2. Preprocessing:**
- Aggregate hourly data to daily statistics
- Standardize units (°C, mm/day, m/s)
- Handle missing values (interpolation where appropriate)
- Quality control checks

**3. Storage:**
- Store as Parquet files for efficiency
- Organize by location
- Include metadata (lat/lon, coverage area, date range)

**4. Metadata Structure:**
```json
{
  "location_name": "Kathmandu, Nepal",
  "latitude": 27.7172,
  "longitude": 85.3240,
  "coverage_km": 55,
  "coverage_area": {
    "lat_min": 27.2,
    "lat_max": 28.2,
    "lon_min": 84.8,
    "lon_max": 85.8
  },
  "start_date": "1990-01-01",
  "end_date": "2024-12-31",
  "data_variables": ["temp", "precip", "wind", "cloud_cover"],
  "total_days": 12784
}
```

### **Prediction Methodology**

**Empirical Probability Calculation:**

```
P(event) = (Number of historical occurrences) / (Total years of data)
```

**Date Window Matching:**
- For a target date (e.g., July 15, 2025)
- Extract all historical data within ±7 days (July 8-22)
- Across all available years (1990-2024)
- Provides ~450-500 data points for robust statistics

**Statistical Measures:**
- **Mean, Median** - Central tendency
- **Percentiles** - 10th, 25th, 75th, 90th
- **Min/Max** - Extreme values observed
- **Standard Deviation** - Variability measure
- **Probability** - Empirical frequency of events

**Weather Categorization Algorithm:**
```python
if rainfall > 1mm and cloud_cover > 70:
    category = "Rainy"
elif cloud_cover > 80:
    category = "Cloudy"
elif cloud_cover > 40:
    category = "Partly Cloudy"
else:
    category = "Sunny/Clear"
```

**Confidence Scoring:**
- Based on data completeness (% of available years)
- Historical variability (low variability = high confidence)
- Recent trend consistency

---

## 📁 Project Structure

```
PlanMySky/
│
├── frontend/                           # React frontend application
│   ├── src/
│   │   ├── components/
│   │   │   ├── MapContainer.jsx        # Interactive Leaflet map
│   │   │   ├── ResultsPanel.jsx        # Main results panel with tabs
│   │   │   ├── WeatherPredictionTab.jsx # Probability charts
│   │   │   ├── WeatherStatsTab.jsx     # Detailed statistics
│   │   │   ├── MiniPosts.jsx           # Community messages
│   │   │   ├── LocalTrends.jsx         # Community stats
│   │   │   ├── DatePicker.jsx          # Date selection
│   │   │   ├── SearchBar.jsx           # Location search
│   │   │   ├── HamburgerMenu.jsx       # Navigation menu
│   │   │   ├── UserDashboard.jsx       # User profile
│   │   │   └── WeatherSurvey.jsx       # Survey component
│   │   │
│   │   ├── services/
│   │   │   ├── weatherApi.js           # Weather API client
│   │   │   ├── communityApi.js         # Community API client
│   │   │   └── calendarApi.js          # Calendar API client
│   │   │
│   │   ├── contexts/
│   │   │   └── AuthContext.jsx         # Authentication context
│   │   │
│   │   ├── styles/
│   │   │   └── App.css                 # Main styles
│   │   │
│   │   ├── App.jsx                     # Main app component
│   │   └── main.jsx                    # Entry point
│   │
│   ├── public/                         # Static assets
│   ├── package.json                    # Dependencies
│   ├── vite.config.js                  # Vite configuration
│   └── index.html                      # HTML template
│
├── backend/
│   ├── api/
│   │   ├── weather_api.py              # Main FastAPI application
│   │   ├── community_routes.py         # Community hub endpoints
│   │   ├── auth_routes.py              # Authentication endpoints
│   │   ├── survey_routes.py            # Survey endpoints
│   │   ├── google_calendar.py          # Calendar integration
│   │   ├── database.py                 # MongoDB connection
│   │   └── index.py                    # Entry point
│   │
│   ├── requirements.txt                # Python dependencies
│   └── .env                            # Environment variables
│
├── src/
│   └── modeling/
│       └── historical_pattern_predictor.py  # Core prediction engine
│
├── data/
│   ├── raw/                            # Raw NASA ERA5 data
│   │   ├── kathmandu_nepal/
│   │   │   ├── metadata.json           # Location metadata
│   │   │   └── raw_data_files/
│   │   │
│   │   └── banglore_india/
│   │       ├── metadata.json
│   │       └── raw_data_files/
│   │
│   ├── processed/                      # Processed Parquet files
│   │   ├── kathmandu_nepal/
│   │   │   └── era5_processed_1990_2024.parquet
│   │   │
│   │   └── banglore_india/
│   │       └── era5_processed_1990_2024.parquet
│   │
│   └── tokens/                         # OAuth tokens (auto-generated)
│       └── user_*.json
│
├── scripts/                            # Utility scripts
│   ├── data_download.py                # Download ERA5 data
│   ├── data_preprocessing.py           # Process raw data
│   └── location_setup.py               # Setup new location
│
├── tests/                              # Test files
│   ├── test_api.py
│   ├── test_predictions.py
│   └── test_community.py
│
├── .gitignore
├── README.md                           # This file
└── package.json                        # Root package.json
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 16+ and npm
- **Python** 3.9+
- **MongoDB** Atlas account (free tier)
- **Git**

### Installation Steps

#### 1. Clone Repository

```bash
git clone https://github.com/TheVishalKumar369/PlanMySky.git
cd PlanMySky
```

#### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create .env file with following variables:
# MONGO_URI=your-mongodb-connection-string
# JWT_SECRET_KEY=your-random-secret-key
# GOOGLE_CLIENT_ID=your-google-client-id (optional)
# GOOGLE_CLIENT_SECRET=your-google-secret (optional)

# Start backend server
cd api
python weather_api.py
```

Backend runs at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

#### 3. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: `http://localhost:5173`

#### 4. MongoDB Setup

1. Create account at [MongoDB Atlas](https://mongodb.com/cloud/atlas)
2. Create free M0 cluster
3. Create database user
4. Whitelist IP: `0.0.0.0/0`
5. Get connection string
6. Add to backend `.env` file

---

## 🎨 User Interface Design

### **Design Principles**

- **Simplicity First:** Clean, uncluttered interface
- **Mobile Responsive:** Works on all screen sizes
- **Fast & Smooth:** Optimized animations and transitions
- **Intuitive Navigation:** Logical flow from map → results → details
- **Accessible:** ARIA labels, keyboard navigation

### **Layout Structure**

**Main Screen:**
```
┌─────────────────────────────────────────┐
│  [Search Bar]         [≡ Menu]          │
├─────────────────────────────────────────┤
│                                         │
│                                         │
│        Interactive Map                  │
│        (Click anywhere)                 │
│                                         │
│                                         │
├─────────────────────────────────────────┤
│  [Date Picker]                          │
└─────────────────────────────────────────┘
```

**Results Panel (Slides in from right):**
```
┌─────────────────────────────┐
│  PlanMySky    [📥] [📊] [✕] │
├─────────────────────────────┤
│  [Date Picker]              │
├─────────────────────────────┤
│  Selected Location: ...     │
│  Weather Station: ...       │
├─────────────────────────────┤
│ [Weather] [Stats] [Connect] │
├─────────────────────────────┤
│                             │
│   Tab Content Area          │
│   (Charts, Stats, or        │
│    Community Hub)           │
│                             │
└─────────────────────────────┘
```

### **Tab Organization**

**Weather Probability Tab:**
- Rainfall probability chart
- Temperature range visualization
- Wind speed statistics
- Weather category with confidence score
- Export buttons

**Weather Stats Tab:**
- Detailed statistical breakdown
- Percentile tables
- Extreme weather probabilities
- Recent years comparison
- Historical observations count

**Weather Connect Tab (Community Hub):**
- Community message feed
- "New Post" button
- Message reactions
- Community statistics dashboard
- Location trends chart

**Social Tab:**
- User dashboard (if logged in)
- Weather surveys
- Activity preferences
- Poll results

---

## 🌟 Additional Features

### **Smart Recommendations**
- Composite activity score based on multiple weather variables
- Best day suggestions for outdoor activities
- Risk assessment for weather-sensitive events

### **Data Export**
- Download predictions as JSON
- Export charts as PNG images
- Batch download for date ranges
- Custom data formatting options

### **Location Management**
- Nearest weather station finder
- Coverage area visualization
- Distance calculations
- Multi-location comparison (planned)

### **Notification System** (Planned)
- Weather alerts for saved dates
- Community activity notifications
- Calendar event reminders

---

## 📖 API Documentation

Full interactive API documentation available at: `http://localhost:8000/docs`

Includes:
- Request/response schemas
- Example requests
- Try-it-out functionality
- Authentication details
- Error codes and handling

---

## 🤝 Contributing

Contributions welcome! Areas for contribution:
- Add more locations
- Improve prediction algorithms
- Enhance UI/UX
- Add new visualization types
- Optimize performance
- Write tests
- Documentation improvements

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👥 Team

**Project:** PlanMySky
**Lead Developer(Backend, Social Feature, Calendar Integration, Model Design, Data Acquisition and processing):** [Pancha Narayan Sahu(Vishal Kumar)](https://github.com/TheVishalKumar369)
**Contact:** panchanarayansahu00@gmail.com
**Full Stack Developer(with a focus on Frontend & Deployment):** [Vansh Kumar](https://github.com/VanshWebDev)
**Contact:** vanshvanshkumar39@gmail.com
**Full Stack Developer(Social Feature, Team Management, Documentation):** [Abdullah Khetran](https://github.com/AbdullahKhetran)
**Contact:** khetranabdullah@gmail.com
**Team Management and Presentation** [Abdul Rehman](https://github.com/abdulrehman-work)

---

## 🙏 Acknowledgments

- **NASA** for ERA5 historical weather data
- **ECMWF** for ERA5 reanalysis dataset
- **OpenStreetMap** contributors for map tiles
- **FastAPI** and **React** communities
- **MongoDB Atlas** for database hosting

---

## 📚 References

- [NASA GES DISC](https://disc.gsfc.nasa.gov/)
- [ERA5 Documentation](https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Leaflet.js](https://leafletjs.com/)

---

**Made with ❤️ for better weather planning**

*Last Updated: October 2025*
