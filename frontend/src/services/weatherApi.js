import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Get API status and available locations
export const getStatus = async () => {
  const response = await api.get('/api/status');
  return response.data;
};

// Get all available locations
export const getLocations = async () => {
  const response = await api.get('/api/locations');
  return response.data;
};

// Get weather prediction for a specific date and location
export const getWeatherPrediction = async (month, day, location, windowDays = 7) => {
  const response = await api.get(`/api/predict/${month}/${day}`, {
    params: { location, window_days: windowDays }
  });
  return response.data;
};

// Get monthly statistics
export const getMonthlyStats = async (month, location) => {
  const response = await api.get(`/api/monthly/${month}`, {
    params: { location }
  });
  return response.data;
};

// Find nearest location to coordinates
export const findNearestLocation = async (lat, lon) => {
  try {
    const locationsData = await getLocations();
    const locations = locationsData.locations;

    if (!locations || locations.length === 0) {
      throw new Error('No locations available');
    }

    // Calculate distance to each location
    const distances = locations.map(loc => ({
      ...loc,
      distance: calculateDistance(lat, lon, loc.latitude, loc.longitude)
    }));

    // Sort by distance and return nearest
    distances.sort((a, b) => a.distance - b.distance);

    return distances[0];
  } catch (error) {
    console.error('Error finding nearest location:', error);
    throw error;
  }
};

// Haversine formula to calculate distance between two points
const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371; // Earth's radius in km
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c;

  return distance;
};

const toRad = (value) => {
  return value * Math.PI / 180;
};

export default api;
