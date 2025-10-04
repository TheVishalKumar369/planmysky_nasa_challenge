# PlanMySky 🌤️

**Tagline:** *Empowering outdoor planning with historical weather probabilities and community insights.*

---

## Overview

PlanMySky is a **web-based platform** that combines historical NASA weather data, probability modeling, and social insights to help users make informed decisions about outdoor activities. Unlike traditional forecasts, PlanMySky calculates **empirical probabilities** for weather conditions based on decades of historical data, allowing users to plan months in advance.  

The platform also includes **interactive visualizations, social trends**, and optional extensions like calendar integration and notifications.  

---

## Key Features

1. **Probability Engine (Core)**  
   - Computes the likelihood of weather conditions (rain, temperature extremes, wind, air quality, etc.) for a chosen location and date.
   - Uses historical NASA Earth observation datasets (MERRA-2, Data Rods, GPM, etc.) over 20–30+ years.
   - Offers statistical outputs: empirical probabilities, percentiles, confidence intervals, and trend analysis.

2. **User Dashboard**  
   - Interactive map for selecting locations (Leaflet / CesiumJS).  
   - Graphs and visualizations for probability distributions and historical trends (Plotly / D3.js).  
   - Export functionality (CSV/JSON) for selected data.

3. **Social Layer**  
   - Users can indicate whether they plan to go outdoors or stay indoors.  
   - Aggregated social trends displayed alongside historical probabilities to add a human context to planning.

4. **Extensions (Optional)**  
   - Google Calendar integration for adding planned outdoor events.  
   - Notifications via SMS or email (Twilio / Firebase).  
   - Smart recommendations based on multi-variable scores.

---

## Data Acquisition

**Primary Data Sources:**  
- **GES DISC OPeNDAP (Hyrax):** Temperature, wind, humidity, and other reanalysis variables.  
- **Data Rods for Hydrology:** Rainfall, soil moisture, evapotranspiration.  
- **GPM (Global Precipitation Measurement):** High-resolution precipitation data.  
- **Worldview / MODIS:** Optional imagery overlays.  
- **Earthdata Search / Giovanni:** Dataset discovery and exploration.

**Acquisition Process:**  
1. Query datasets by latitude, longitude, and time range using APIs or OPeNDAP.  
2. Extract required variables for each calendar day across 20–30+ years.  
3. Preprocess:
   - Standardize units (°C, mm/day, m/s).  
   - Aggregate sub-daily data to daily statistics.  
   - Handle missing values (interpolation or marking as missing).  
   - Align seasonal data for probability calculations.  
4. Store processed data locally (CSV/Parquet) or in a lightweight database for caching.

---

## Probability Calculations

- **Empirical Probability:**  
  \[
  \hat{P} = \frac{\text{Number of years condition exceeded threshold}}{\text{Total years of data}}
  \]

- **Percentiles & Thresholds:** Provides median, 25th, 75th, and 90th percentiles.  
- **Trend Analysis:** Linear regression or Mann–Kendall test to detect changing likelihoods.  
- **Confidence Intervals:** Bootstrapping over historical years.  
- **Composite Activity Score:** Weighted multi-variable score for outdoor suitability.

---

## Validation & Verification

- **Sanity Checks:** Compare probability outputs against historical frequency.  
- **Cross-Dataset Comparison:** Use multiple NASA datasets to ensure consistency.  
- **Holdout Testing:** Reserve recent years to check calculation consistency.  
- **Visual Inspection:** Histograms, KDE plots, and threshold overlays.  

---

## Tech Stack

- **Frontend:** React + Leaflet / CesiumJS + Plotly / D3.js  
- **Backend:** Python + FastAPI + Pandas / xarray / NumPy  
- **Database:** SQLite (optional) for caching + social data  
- **Notifications & Calendar:** Twilio / Firebase + Google Calendar API  
- **Version Control:** GitHub (feature branches + dev/main workflow)

---

## GitHub Structure

PlanMySky/
│── README.md
│── requirements.txt
│── package.json
│── .github/
│── data/
│ ├── raw/
│ ├── processed/
│ └── metadata/
│── backend/
│ ├── models/
│ ├── api/
│ └── utils/
│── frontend/
│ ├── components/
│ ├── pages/
│ └── assets/
│── tests/
└── scripts/



**Branching Workflow:**  
- `main`: Stable, production-ready code  
- `dev`: Active development  
- `feature/...`: Specific features (e.g., `feature/data-ingestion`)  
- `bugfix/...`, `hotfix/...` as needed  

**Collaboration:**  
- **Issues:** Track tasks or bugs  
- **Discussions:** Brainstorming, UX ideas, feature proposals  
- **Projects / Kanban board:** Track workflow `To Do → In Progress → Done`

---

## Future Extensions

- More variables (air quality, extreme indices, soil moisture).  
- AI-driven recommendations (best day for activity based on multiple factors).  
- Mobile wrapper / PWA for push notifications.  
- Social network layer with location-based weather planning trends.

---

## References & Resources

- [GES DISC OPeNDAP Server](https://disc.gsfc.nasa.gov/datasets)  
- [Giovanni](https://giovanni.gsfc.nasa.gov/giovanni/)  
- [Data Rods for Hydrology](https://hydrology.gsfc.nasa.gov/data_rods/)  
- [Worldview](https://worldview.earthdata.nasa.gov/)  
- [Earthdata Search](https://search.earthdata.nasa.gov/)  

---

## License
MIT License

---

## Contact
**Project:** PlanMySky  
**GitHub:** [[@thevishalkumar369](https://github.com/TheVishalKumar369/)]  
**Email:** [panchanarayansahu00@gmail.com]
