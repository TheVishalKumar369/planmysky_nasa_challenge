import { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';

const UserDashboard = () => {
  const { token } = useContext(AuthContext);
  const [userEmail, setUserEmail] = useState(null);
  const [calendarConnected, setCalendarConnected] = useState(false);
  const [calendarEmail, setCalendarEmail] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }

    // Decode JWT to get user email
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      setUserEmail(payload.email);
    } catch (error) {
      console.error('Error decoding token:', error);
    }

    // Check if calendar is connected
    checkCalendarStatus();

    // Check URL for calendar connection success
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('calendar_connected') === 'true') {
      // Remove the query parameter
      window.history.replaceState({}, '', window.location.pathname);
      // Refresh calendar status
      setTimeout(() => {
        checkCalendarStatus();
      }, 500);
    }
  }, [token]);

  const checkCalendarStatus = async () => {
    try {
      // Extract user_id from token
      const payload = JSON.parse(atob(token.split('.')[1]));
      const userId = payload.email; // Using email as user_id

      const response = await fetch(
        `http://localhost:8000/api/calendar/auth/status?user_id=${userId}`
      );

      const data = await response.json();

      if (data.authenticated) {
        setCalendarConnected(true);
        setCalendarEmail(data.email || userId);
      } else {
        setCalendarConnected(false);
        setCalendarEmail(null);
      }
    } catch (error) {
      console.error('Error checking calendar status:', error);
      setCalendarConnected(false);
      setCalendarEmail(null);
    } finally {
      setLoading(false);
    }
  };

  const handleConnectCalendar = () => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const userId = payload.email;

      // Redirect to Google OAuth
      window.location.href = `http://localhost:8000/api/calendar/auth/initiate?user_id=${userId}`;
    } catch (error) {
      console.error('Error connecting calendar:', error);
    }
  };

  const handleDisconnectCalendar = async () => {
    if (!confirm('Are you sure you want to disconnect Google Calendar?')) {
      return;
    }

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const userId = payload.email;

      const response = await fetch(
        `http://localhost:8000/api/calendar/auth/revoke?user_id=${userId}`,
        {
          method: 'DELETE'
        }
      );

      if (response.ok) {
        setCalendarConnected(false);
        setCalendarEmail(null);
        alert('Google Calendar disconnected successfully!');
      } else {
        throw new Error('Failed to disconnect');
      }
    } catch (error) {
      console.error('Error disconnecting calendar:', error);
      alert('Failed to disconnect calendar');
    }
  };

  if (loading) {
    return (
      <div className="user-dashboard">
        <div className="dashboard-card">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!token) {
    return (
      <div className="user-dashboard">
        <div className="dashboard-card">
          <h3>👤 User Dashboard</h3>
          <p className="dashboard-message">
            Please log in to view your dashboard
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="user-dashboard">
      <div className="dashboard-card">
        <h3>👤 User Dashboard</h3>

        <div className="dashboard-section">
          <h4>Account Information</h4>
          <div className="info-row">
            <span className="info-label">Email:</span>
            <span className="info-value">{userEmail}</span>
          </div>
        </div>

        <div className="dashboard-divider"></div>

        <div className="dashboard-section">
          <h4>📅 Google Calendar Integration</h4>

          {calendarConnected ? (
            <div className="calendar-connected">
              <div className="status-badge success">
                ✓ Connected
              </div>
              <div className="info-row">
                <span className="info-label">Calendar Email:</span>
                <span className="info-value">{calendarEmail}</span>
              </div>
              <button
                className="disconnect-btn"
                onClick={handleDisconnectCalendar}
              >
                Disconnect Calendar
              </button>
            </div>
          ) : (
            <div className="calendar-disconnected">
              <div className="status-badge warning">
                ✗ Not Connected
              </div>
              <p className="calendar-info">
                Connect your Google Calendar to automatically add weather predictions to your events
              </p>
              <button
                className="connect-btn"
                onClick={handleConnectCalendar}
              >
                Connect Google Calendar
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserDashboard;
