import React, { useState, useCallback, useRef } from 'react';
import MapContainer from './components/MapContainer';
import ResultsPanel from './components/ResultsPanel';
import SearchBar from './components/SearchBar';
import HamburgerMenu from './components/HamburgerMenu';
import { findNearestLocation, getWeatherPrediction } from './services/weatherApi';
import './styles/App.css';

function App() {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [nearestLocation, setNearestLocation] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const isProcessingRef = useRef(false);

  const handleLocationSelect = useCallback(async ({ lat, lng }) => {
    // Prevent multiple simultaneous requests
    if (isProcessingRef.current) {
      console.log('⏳ Previous request still processing...');
      return;
    }

    isProcessingRef.current = true;

    console.log('📍 Location clicked:', { lat, lng });

    // Update location immediately (no async here)
    setSelectedLocation({ lat, lng });

    try {
      const nearest = await findNearestLocation(lat, lng);

      // Update nearest location
      setNearestLocation(nearest);

      console.log('✅ Nearest weather station found:', nearest);
      console.log('📊 Station details:', {
        name: nearest.name,
        display_name: nearest.display_name,
        distance: `${nearest.distance?.toFixed(2)} km`,
        coverage: `${nearest.coverage_km} km`,
        coordinates: {
          lat: nearest.latitude,
          lng: nearest.longitude
        }
      });

      // Auto-fetch weather for current date (example: July 15)
      const month = 7;
      const day = 15;

      console.log(`🌤️ Fetching weather prediction for ${month}/${day}...`);

      const prediction = await getWeatherPrediction(month, day, nearest.name, 7);

      console.log('✅ Weather Prediction Received:');
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.log('📅 Date:', prediction.date);
      console.log('📍 Location:', prediction.location);
      console.log('🌦️ Category:', prediction.weather_category);
      console.log('📊 Confidence:', `${(prediction.category_confidence * 100).toFixed(0)}%`);
      console.log('');
      console.log('☔ Rain:');
      console.log('  - Probability:', `${prediction.rainfall?.probability_percent}%`);
      console.log('  - Expected:', `${prediction.rainfall?.expected_amount_mm} mm`);
      console.log('');
      console.log('🌡️ Temperature:');
      console.log('  - Range:', `${prediction.temperature?.expected_range?.min}°C - ${prediction.temperature?.expected_range?.max}°C`);
      console.log('  - Average:', `${prediction.temperature?.mean_avg_celsius}°C`);
      console.log('');
      console.log('💨 Wind:', `${prediction.wind?.mean_speed_ms} m/s`);
      console.log('☁️ Cloud Cover:', `${prediction.cloud_cover?.mean_percent}%`);
      console.log('');
      console.log('⚠️ Extreme Probabilities:');
      console.log('  - Temp > 30°C:', `${(prediction.extreme_probabilities?.temp_above_30C * 100).toFixed(0)}%`);
      console.log('  - Heavy Rain:', `${(prediction.extreme_probabilities?.heavy_rain_above_10mm * 100).toFixed(0)}%`);
      console.log('  - High Wind:', `${(prediction.extreme_probabilities?.high_wind_above_5ms * 100).toFixed(0)}%`);
      console.log('');
      console.log('📚 Based on:', `${prediction.historical_years_analyzed} years`);
      console.log('📊 Observations:', prediction.total_observations);
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.log('');
      console.log('💡 Full prediction object:', prediction);

      // Store weather data and open panel
      setWeatherData(prediction);
      setIsPanelOpen(true);

    } catch (err) {
      console.error('❌ Error:', err.message);
      if (err.response?.data) {
        console.error('Backend error:', err.response.data);
      }
    } finally {
      isProcessingRef.current = false;
    }
  }, []); // Empty dependencies - function never changes

  const handleClosePanel = () => {
    setIsPanelOpen(false);
  };

  return (
    <div className="app">
      <MapContainer
        onLocationSelect={handleLocationSelect}
        selectedLocation={selectedLocation}
        nearestLocation={nearestLocation}
      />

      <SearchBar
        isPanelOpen={isPanelOpen}
        onLocationSelect={handleLocationSelect}
      />

      <ResultsPanel
        isOpen={isPanelOpen}
        onClose={handleClosePanel}
        weatherData={weatherData}
        locationData={{
          clicked: selectedLocation,
          nearest: nearestLocation
        }}
      />

      <HamburgerMenu />

      {/* Minimal instruction overlay */}
      {!isPanelOpen && (
        <div className="instruction-overlay">
          <p>🗺️ Click anywhere on the map or search for a location</p>
          <p style={{ fontSize: '12px', opacity: 0.8 }}>Weather results will appear in the side panel</p>
        </div>
      )}
    </div>
  );
}

export default App;
