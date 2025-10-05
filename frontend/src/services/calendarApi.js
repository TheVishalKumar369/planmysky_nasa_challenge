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
 * Opens Google consent screen in popup window
 */
export const initiateGoogleAuth = async () => {
  const userId = getUserId();

  try {
    const response = await fetch(`${API_BASE}/auth/initiate?user_id=${userId}`);
    const data = await response.json();

    if (data.auth_url) {
      // Open OAuth consent screen in popup
      const width = 600;
      const height = 700;
      const left = window.screen.width / 2 - width / 2;
      const top = window.screen.height / 2 - height / 2;

      const popup = window.open(
        data.auth_url,
        'Google Calendar Authorization',
        `width=${width},height=${height},left=${left},top=${top},toolbar=no,menubar=no`
      );

      // Listen for messages from callback page
      return new Promise((resolve, reject) => {
        const messageHandler = (event) => {
          // Verify message origin
          if (event.origin !== window.location.origin) return;

          if (event.data.type === 'oauth_success') {
            window.removeEventListener('message', messageHandler);
            resolve(true);
          } else if (event.data.type === 'oauth_error') {
            window.removeEventListener('message', messageHandler);
            reject(new Error(event.data.error || 'Authentication failed'));
          }
        };

        window.addEventListener('message', messageHandler);

        // Also check if popup was closed manually
        const checkInterval = setInterval(() => {
          if (popup.closed) {
            clearInterval(checkInterval);
            window.removeEventListener('message', messageHandler);
            // Give a moment for message to arrive
            setTimeout(() => {
              checkAuthStatus().then(isAuth => {
                if (isAuth) {
                  resolve(true);
                } else {
                  reject(new Error('Authentication was cancelled'));
                }
              });
            }, 500);
          }
        }, 500);

        // Timeout after 5 minutes
        setTimeout(() => {
          clearInterval(checkInterval);
          window.removeEventListener('message', messageHandler);
          if (!popup.closed) {
            popup.close();
          }
          reject(new Error('Authentication timeout'));
        }, 5 * 60 * 1000);
      });
    } else {
      throw new Error('Failed to get authorization URL');
    }
  } catch (error) {
    console.error('Error initiating OAuth:', error);
    throw error;
  }
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
