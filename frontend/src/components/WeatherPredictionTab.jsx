import React, { useState, useEffect } from 'react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format, addDays } from 'date-fns';
import DatePicker from './DatePicker';
import { checkAuthStatus, initiateGoogleAuth, createCalendarEvent } from '../services/calendarApi';

const WeatherPredictionTab = ({ weatherData, locationData }) => {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [isCalendarAuth, setIsCalendarAuth] = useState(false);
  const [isAddingToCalendar, setIsAddingToCalendar] = useState(false);
  const [calendarMessage, setCalendarMessage] = useState(null);

  // Check auth status on mount
  useEffect(() => {
    checkAuthStatus().then(setIsCalendarAuth);
  }, []);

  const handleAddToCalendar = async () => {
    try {
      setIsAddingToCalendar(true);
      setCalendarMessage(null);

      // Check if authenticated
      if (!isCalendarAuth) {
        // Initiate OAuth flow
        setCalendarMessage({ type: 'info', text: 'Opening Google authorization...' });
        await initiateGoogleAuth();
        setIsCalendarAuth(true);
        setCalendarMessage({ type: 'success', text: 'Authorization successful!' });
      }

      // Create calendar event
      setCalendarMessage({ type: 'info', text: 'Adding event to calendar...' });
      const result = await createCalendarEvent(weatherData, locationData, format(selectedDate, 'yyyy-MM-dd'));

      setCalendarMessage({
        type: 'success',
        text: 'Event added to Google Calendar!',
        link: result.event_link
      });

      // Clear message after 5 seconds
      setTimeout(() => setCalendarMessage(null), 5000);
    } catch (error) {
      console.error('Calendar error:', error);

      if (error.message === 'NOT_AUTHENTICATED') {
        setIsCalendarAuth(false);
        setCalendarMessage({ type: 'error', text: 'Please authorize Google Calendar access' });
      } else if (error.message.includes('cancelled')) {
        setCalendarMessage({ type: 'warning', text: 'Authorization cancelled' });
      } else {
        setCalendarMessage({ type: 'error', text: 'Failed to add event. Please try again.' });
      }

      setTimeout(() => setCalendarMessage(null), 5000);
    } finally {
      setIsAddingToCalendar(false);
    }
  };

  if (!weatherData) {
    return <p className="loading">Loading weather prediction data...</p>;
  }

  // Generate 7-day forecast data (mock for now - will be replaced with real API calls)
  const generate7DayData = () => {
    const data = [];
    for (let i = 0; i < 7; i++) {
      const date = addDays(selectedDate, i);
      data.push({
        date: format(date, 'MMM dd'),
        shortDate: format(date, 'EEE'),
        temp: weatherData.temperature?.mean_avg_celsius + (Math.random() * 4 - 2),
        rain: weatherData.rainfall?.probability_percent + (Math.random() * 20 - 10),
        wind: weatherData.wind?.mean_speed_ms + (Math.random() * 2 - 1),
      });
    }
    return data;
  };

  const weekData = generate7DayData();

  // Get weather icon based on conditions
  const getWeatherIcon = () => {
    const category = weatherData.weather_category?.toLowerCase() || '';
    if (category.includes('rain')) return '🌧️';
    if (category.includes('cloud')) return '☁️';
    if (category.includes('clear')) return '☀️';
    return '🌤️';
  };

  return (
    <div className="weather-prediction-content">
      {/* Custom Date Picker */}
      <DatePicker
        selectedDate={selectedDate}
        onDateSelect={setSelectedDate}
      />

      {/* Add to Calendar Button */}
      <div className="calendar-action-section">
        <button
          className="add-to-calendar-btn"
          onClick={handleAddToCalendar}
          disabled={isAddingToCalendar}
        >
          {isAddingToCalendar ? (
            <>
              <span className="btn-spinner"></span>
              <span>Adding...</span>
            </>
          ) : (
            <>
              <span className="calendar-icon">📅</span>
              <span>Add to Google Calendar</span>
            </>
          )}
        </button>

        {calendarMessage && (
          <div className={`calendar-message ${calendarMessage.type}`}>
            <span>{calendarMessage.text}</span>
            {calendarMessage.link && (
              <a href={calendarMessage.link} target="_blank" rel="noopener noreferrer">
                View Event
              </a>
            )}
          </div>
        )}
      </div>

      {/* Current Day Weather Card */}
      <div className="weather-card">
        <div className="weather-card-header">
          <div className="weather-icon-large">{getWeatherIcon()}</div>
          <div className="weather-main-info">
            <h4>{format(selectedDate, 'EEEE, MMMM dd')}</h4>
            <div className="temperature-display">
              {weatherData.temperature?.mean_avg_celsius?.toFixed(1)}°C
            </div>
            <p className="weather-category">{weatherData.weather_category}</p>
          </div>
        </div>

        <div className="weather-details-grid">
          <div className="weather-detail-item">
            <span className="detail-icon">💧</span>
            <div className="detail-info">
              <span className="detail-label">Rainfall</span>
              <span className="detail-value">{weatherData.rainfall?.probability_percent}%</span>
              <span className="detail-sub">{weatherData.rainfall?.expected_amount_mm} mm</span>
            </div>
          </div>

          <div className="weather-detail-item">
            <span className="detail-icon">🌡️</span>
            <div className="detail-info">
              <span className="detail-label">Temp Range</span>
              <span className="detail-value">
                {weatherData.temperature?.expected_range?.min}° - {weatherData.temperature?.expected_range?.max}°
              </span>
            </div>
          </div>

          <div className="weather-detail-item">
            <span className="detail-icon">💨</span>
            <div className="detail-info">
              <span className="detail-label">Wind Speed</span>
              <span className="detail-value">{weatherData.wind?.mean_speed_ms?.toFixed(1)} m/s</span>
            </div>
          </div>

          <div className="weather-detail-item">
            <span className="detail-icon">☁️</span>
            <div className="detail-info">
              <span className="detail-label">Cloud Cover</span>
              <span className="detail-value">{weatherData.cloud_cover?.mean_percent}%</span>
            </div>
          </div>
        </div>

        <div className="confidence-indicator">
          <span className="confidence-label">Prediction Confidence</span>
          <div className="confidence-bar">
            <div
              className="confidence-fill"
              style={{ width: `${(weatherData.category_confidence * 100).toFixed(0)}%` }}
            ></div>
          </div>
          <span className="confidence-value">{(weatherData.category_confidence * 100).toFixed(0)}%</span>
        </div>
      </div>

      {/* 7-Day Forecast */}
      <div className="forecast-section">
        <h3>7-Day Forecast</h3>
        <div className="forecast-cards">
          {weekData.map((day, index) => (
            <div key={index} className={`forecast-card ${index === 0 ? 'active' : ''}`}>
              <div className="forecast-day">{day.shortDate}</div>
              <div className="forecast-icon">{index === 0 ? getWeatherIcon() : '🌤️'}</div>
              <div className="forecast-temp">{day.temp.toFixed(0)}°</div>
              <div className="forecast-rain">{day.rain.toFixed(0)}%</div>
            </div>
          ))}
        </div>
      </div>

      {/* Temperature Chart */}
      <div className="chart-section">
        <h3>Temperature Trend</h3>
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={weekData}>
            <defs>
              <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ff6b6b" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#ff6b6b" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey="shortDate" stroke="#86868b" style={{ fontSize: '12px' }} />
            <YAxis stroke="#86868b" style={{ fontSize: '12px' }} />
            <Tooltip
              contentStyle={{
                background: 'rgba(255, 255, 255, 0.95)',
                border: '0.5px solid rgba(0, 0, 0, 0.1)',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
              }}
            />
            <Area type="monotone" dataKey="temp" stroke="#ff6b6b" fillOpacity={1} fill="url(#tempGradient)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Rainfall Chart */}
      <div className="chart-section">
        <h3>Rainfall Probability</h3>
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={weekData}>
            <defs>
              <linearGradient id="rainGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#4dabf7" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#4dabf7" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey="shortDate" stroke="#86868b" style={{ fontSize: '12px' }} />
            <YAxis stroke="#86868b" style={{ fontSize: '12px' }} />
            <Tooltip
              contentStyle={{
                background: 'rgba(255, 255, 255, 0.95)',
                border: '0.5px solid rgba(0, 0, 0, 0.1)',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
              }}
            />
            <Area type="monotone" dataKey="rain" stroke="#4dabf7" fillOpacity={1} fill="url(#rainGradient)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Wind Speed Chart */}
      <div className="chart-section">
        <h3>Wind Speed</h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={weekData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey="shortDate" stroke="#86868b" style={{ fontSize: '12px' }} />
            <YAxis stroke="#86868b" style={{ fontSize: '12px' }} />
            <Tooltip
              contentStyle={{
                background: 'rgba(255, 255, 255, 0.95)',
                border: '0.5px solid rgba(0, 0, 0, 0.1)',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
              }}
            />
            <Line type="monotone" dataKey="wind" stroke="#51cf66" strokeWidth={2} dot={{ fill: '#51cf66', r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Data Source Info */}
      <div className="data-source-info">
        <p>📊 Based on {weatherData.historical_years_analyzed} years of historical data</p>
        <p>🔢 {weatherData.total_observations} observations analyzed</p>
      </div>
    </div>
  );
};

export default WeatherPredictionTab;
