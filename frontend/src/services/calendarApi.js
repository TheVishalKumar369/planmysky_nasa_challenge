/**
 * Google Calendar API Integration
 * Handles OAuth flow and event creation
 */

const API_BASE = 'http://localhost:8000/api/calendar';

/**
 * Generate a unique user ID (in production, use actual user authentication)
 */
export const getUserId = () => {
  let userId = localStorage.getItem('planmysky_user_id');

  if (!userId) {
    userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('planmysky_user_id', userId);
  }

  return userId;
};

/**
 * Check if user is authenticated with Google Calendar
 */
export const checkAuthStatus = async () => {
  const userId = getUserId();

  try {
    // Add timeout to prevent hanging
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout

    const response = await fetch(`${API_BASE}/auth/status?user_id=${userId}`, {
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      console.warn('Auth status check failed:', response.status);
      return false;
    }

    const data = await response.json();
    return data.authenticated;
  } catch (error) {
    if (error.name === 'AbortError') {
      console.warn('Auth status check timed out');
    } else {
      console.error('Error checking auth status:', error);
    }
    return false;
  }
};

/**
 * Initiate Google OAuth flow
 * Redirects to Google consent screen in current window
 */
export const initiateGoogleAuth = () => {
  const userId = getUserId();

  // Store the current location to return after OAuth
  localStorage.setItem('planmysky_pre_oauth_path', window.location.pathname + window.location.search);

  // Directly redirect to backend OAuth initiate endpoint
  // Backend will redirect to Google, then back to our callback
  window.location.href = `${API_BASE}/auth/initiate?user_id=${userId}`;
};

/**
 * Create calendar event with weather prediction
 */
export const createCalendarEvent = async (weatherData, locationData, selectedDate) => {
  const userId = getUserId();

  // Check authentication first
  const isAuthenticated = await checkAuthStatus();
  if (!isAuthenticated) {
    throw new Error('NOT_AUTHENTICATED');
  }

  try {
    const response = await fetch(`${API_BASE}/create-event`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        location_name: locationData.nearest?.display_name || locationData.nearest?.name || 'Unknown Location',
        location_coords: {
          lat: locationData.clicked?.lat || locationData.nearest?.latitude,
          lng: locationData.clicked?.lng || locationData.nearest?.longitude
        },
        date: selectedDate || new Date().toISOString().split('T')[0],
        weather_data: weatherData
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create calendar event');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error creating calendar event:', error);
    throw error;
  }
};

/**
 * Revoke Google Calendar access
 */
export const revokeCalendarAccess = async () => {
  const userId = getUserId();

  try {
    const response = await fetch(`${API_BASE}/auth/revoke?user_id=${userId}`, {
      method: 'DELETE'
    });
    const data = await response.json();
    return data.success;
  } catch (error) {
    console.error('Error revoking access:', error);
    return false;
  }
};

/**
 * Listen for OAuth callback (called from redirect page)
 */
export const handleOAuthCallback = () => {
  const urlParams = new URLSearchParams(window.location.search);
  const authSuccess = urlParams.get('calendar_auth');

  if (authSuccess === 'success') {
    // Clean URL
    window.history.replaceState({}, document.title, window.location.pathname);
    return true;
  }

  return false;
};
