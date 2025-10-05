import { useState, useEffect } from 'react';
import {
  LineChart, Line, AreaChart, Area, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ZAxis
} from 'recharts';

const YearlyDataView = ({ locationData }) => {
  const [yearlyData, setYearlyData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMonth, setSelectedMonth] = useState(null);

  const currentYear = new Date().getFullYear();
  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  useEffect(() => {
    if (locationData?.nearest?.name) {
      fetchYearlyData();
    }
  }, [locationData?.nearest?.name]);

  const fetchYearlyData = async () => {
    try {
      setLoading(true);
      const allDays = [];

      // Fetch data for every day of current year
      for (let month = 1; month <= 12; month++) {
        const daysInMonth = new Date(currentYear, month, 0).getDate();

        for (let day = 1; day <= daysInMonth; day++) {
          try {
            const response = await fetch(
              `http://localhost:8000/api/predict/${month}/${day}?location=${locationData.nearest.name}&window_days=3`
            );

            if (response.ok) {
              const data = await response.json();
              allDays.push({
                date: `${month}/${day}`,
                dateObj: new Date(currentYear, month - 1, day),
                month: month,
                monthName: monthNames[month - 1],
                day: day,
                temp: data.temperature?.mean_avg_celsius,
                tempMin: data.temperature?.expected_range?.min,
                tempMax: data.temperature?.expected_range?.max,
                rainfall: data.rainfall?.expected_amount_mm,
                rainfallProb: data.rainfall?.probability_percent,
                wind: data.wind?.mean_speed_ms,
                cloud: data.cloud_cover?.mean_percent,
                category: data.weather_category,
              });
            }
          } catch (err) {
            console.error(`Error fetching ${month}/${day}:`, err);
          }
        }
      }

      setYearlyData(allDays);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching yearly data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="yearly-data-view">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading complete year data... ({yearlyData.length}/365 days)</p>
        </div>
      </div>
    );
  }

  if (!yearlyData.length) {
    return <p className="loading">No yearly data available</p>;
  }

  // Filter data by selected month if any
  const displayData = selectedMonth
    ? yearlyData.filter(d => d.month === selectedMonth)
    : yearlyData;

  // Calculate statistics
  const avgTemp = (displayData.reduce((sum, d) => sum + (d.temp || 0), 0) / displayData.length).toFixed(1);
  const totalRainfall = displayData.reduce((sum, d) => sum + (d.rainfall || 0), 0).toFixed(0);
  const maxTemp = Math.max(...displayData.map(d => d.tempMax || 0)).toFixed(1);
  const minTemp = Math.min(...displayData.map(d => d.tempMin || 999)).toFixed(1);

  // Prepare heatmap data for temperature
  const heatmapData = yearlyData.map(d => ({
    month: d.month,
    day: d.day,
    temp: d.temp,
    value: d.temp,
  }));

  return (
    <div className="yearly-data-view">
      <div className="yearly-header">
        <h2>📊 Complete {currentYear} Weather Analysis</h2>
        <p className="yearly-subtitle">
          Based on {yearlyData.length} days of historical pattern data for {locationData.nearest?.display_name}
        </p>
      </div>

      {/* Month Filter */}
      <div className="month-filter">
        <button
          className={`month-btn ${!selectedMonth ? 'active' : ''}`}
          onClick={() => setSelectedMonth(null)}
        >
          All Year
        </button>
        {monthNames.map((name, idx) => (
          <button
            key={idx}
            className={`month-btn ${selectedMonth === idx + 1 ? 'active' : ''}`}
            onClick={() => setSelectedMonth(idx + 1)}
          >
            {name}
          </button>
        ))}
      </div>

      {/* Key Statistics */}
      <div className="yearly-stats-grid">
        <div className="stat-card">
          <div className="stat-icon">🌡️</div>
          <div className="stat-content">
            <span className="stat-label">Average Temperature</span>
            <span className="stat-value">{avgTemp}°C</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🔥</div>
          <div className="stat-content">
            <span className="stat-label">Highest Expected</span>
            <span className="stat-value">{maxTemp}°C</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">❄️</div>
          <div className="stat-content">
            <span className="stat-label">Lowest Expected</span>
            <span className="stat-value">{minTemp}°C</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">💧</div>
          <div className="stat-content">
            <span className="stat-label">Total Rainfall</span>
            <span className="stat-value">{totalRainfall} mm</span>
          </div>
        </div>
      </div>

      {/* Daily Temperature Variation */}
      <div className="chart-section">
        <h3>📈 Daily Temperature Pattern</h3>
        <p className="chart-description">
          {selectedMonth ? `${monthNames[selectedMonth - 1]} daily temperatures` : 'Complete year temperature variation'}
        </p>
        <ResponsiveContainer width="100%" height={350}>
          <AreaChart data={displayData}>
            <defs>
              <linearGradient id="tempArea" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ff6b6b" stopOpacity={0.6}/>
                <stop offset="95%" stopColor="#ff6b6b" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis
              dataKey="date"
              stroke="#86868b"
              style={{ fontSize: '11px' }}
              interval={selectedMonth ? 2 : 30}
            />
            <YAxis stroke="#86868b" style={{ fontSize: '12px' }} />
            <Tooltip
              contentStyle={{
                background: 'rgba(255, 255, 255, 0.95)',
                border: '0.5px solid rgba(0, 0, 0, 0.1)',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
              }}
            />
            <Legend />
            <Area type="monotone" dataKey="tempMax" stroke="#ff6b6b" fill="url(#tempArea)" name="Max Temp (°C)" />
            <Area type="monotone" dataKey="temp" stroke="#ffa94d" fill="none" strokeWidth={2} name="Avg Temp (°C)" />
            <Area type="monotone" dataKey="tempMin" stroke="#4dabf7" fill="none" strokeWidth={2} name="Min Temp (°C)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Rainfall Pattern */}
      <div className="chart-section">
        <h3>💧 Daily Rainfall Pattern</h3>
        <p className="chart-description">
          Expected rainfall amounts and probability throughout the {selectedMonth ? 'month' : 'year'}
        </p>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={displayData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis
              dataKey="date"
              stroke="#86868b"
              style={{ fontSize: '11px' }}
              interval={selectedMonth ? 2 : 30}
            />
            <YAxis yAxisId="left" stroke="#86868b" style={{ fontSize: '12px' }} />
            <YAxis yAxisId="right" orientation="right" stroke="#86868b" style={{ fontSize: '12px' }} />
            <Tooltip
              contentStyle={{
                background: 'rgba(255, 255, 255, 0.95)',
                border: '0.5px solid rgba(0, 0, 0, 0.1)',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
              }}
            />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="rainfall" stroke="#4dabf7" strokeWidth={2} dot={false} name="Rainfall (mm)" />
            <Line yAxisId="right" type="monotone" dataKey="rainfallProb" stroke="#228be6" strokeWidth={2} dot={false} strokeDasharray="5 5" name="Probability (%)" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Weather Correlation Scatter */}
      <div className="chart-section">
        <h3>🔍 Temperature vs Rainfall Correlation</h3>
        <p className="chart-description">Relationship between temperature and rainfall patterns</p>
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey="temp" name="Temperature" unit="°C" stroke="#86868b" />
            <YAxis dataKey="rainfall" name="Rainfall" unit="mm" stroke="#86868b" />
            <ZAxis dataKey="rainfallProb" range={[50, 400]} />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              contentStyle={{
                background: 'rgba(255, 255, 255, 0.95)',
                border: '0.5px solid rgba(0, 0, 0, 0.1)',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
              }}
            />
            <Legend />
            <Scatter name="Days" data={displayData} fill="#8884d8" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Monthly Breakdown Table */}
      {!selectedMonth && (
        <div className="monthly-breakdown-section">
          <h3>📅 Monthly Summary</h3>
          <div className="monthly-breakdown-grid">
            {monthNames.map((name, idx) => {
              const monthData = yearlyData.filter(d => d.month === idx + 1);
              const monthAvgTemp = (monthData.reduce((sum, d) => sum + (d.temp || 0), 0) / monthData.length).toFixed(1);
              const monthRainfall = monthData.reduce((sum, d) => sum + (d.rainfall || 0), 0).toFixed(0);

              return (
                <div key={idx} className="month-summary-card" onClick={() => setSelectedMonth(idx + 1)}>
                  <h4>{name}</h4>
                  <div className="month-summary-stats">
                    <span>🌡️ {monthAvgTemp}°C</span>
                    <span>💧 {monthRainfall}mm</span>
                    <span>📊 {monthData.length} days</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Data Notes */}
      <div className="data-notes">
        <p>📌 All data represents historical weather patterns aggregated from 1990-2024</p>
        <p>🔮 Future date predictions are based on historical trends for that specific day across all years</p>
        <p>📊 Click on individual months to view detailed daily breakdowns</p>
      </div>
    </div>
  );
};

export default YearlyDataView;
