import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const WeatherStatsTab = ({ weatherData, locationData }) => {
  const [monthlyStats, setMonthlyStats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (locationData?.nearest?.name) {
      fetchAnnualStats();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [locationData?.nearest?.name]);

  const fetchAnnualStats = async () => {
    try {
      setLoading(true);
      const stats = [];

      // Fetch stats for all 12 months
      for (let month = 1; month <= 12; month++) {
        const response = await fetch(
          `http://localhost:8000/api/monthly/${month}?location=${locationData.nearest.name}`
        );
        if (response.ok) {
          const data = await response.json();
          stats.push(data);
        }
      }

      setMonthlyStats(stats);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching annual stats:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <p className="loading">Loading comprehensive weather statistics...</p>;
  }

  if (!monthlyStats.length) {
    return <p className="loading">No statistical data available</p>;
  }

  // Prepare chart data
  const temperatureData = monthlyStats.map(m => ({
    month: m.month_name?.substring(0, 3),
    avgTemp: m.temperature?.average_mean_celsius,
    minTemp: m.temperature?.average_min_celsius,
    maxTemp: m.temperature?.average_max_celsius,
  }));

  const rainfallData = monthlyStats.map(m => ({
    month: m.month_name?.substring(0, 3),
    rainfall: m.rainfall?.average_monthly_total_mm,
    rainyDays: m.rainfall?.rainy_days_percent,
  }));

  const windCloudData = monthlyStats.map(m => ({
    month: m.month_name?.substring(0, 3),
    wind: m.wind?.average_speed_ms,
    cloud: m.cloud_cover?.average_percent,
  }));

  // Climate summary
  const annualAvgTemp = (monthlyStats.reduce((sum, m) => sum + (m.temperature?.average_mean_celsius || 0), 0) / 12).toFixed(1);
  const annualRainfall = monthlyStats.reduce((sum, m) => sum + (m.rainfall?.average_monthly_total_mm || 0), 0).toFixed(0);
  const hottestMonth = monthlyStats.reduce((max, m) =>
    (m.temperature?.average_max_celsius || 0) > (max.temperature?.average_max_celsius || 0) ? m : max
  );
  const coldestMonth = monthlyStats.reduce((min, m) =>
    (m.temperature?.average_min_celsius || 999) < (min.temperature?.average_min_celsius || 999) ? m : min
  );
  const wettest = monthlyStats.reduce((max, m) =>
    (m.rainfall?.average_monthly_total_mm || 0) > (max.rainfall?.average_monthly_total_mm || 0) ? m : max
  );

  return (
    <div className="weather-stats-content">
      {/* Climate Summary Cards */}
      <div className="stats-overview">
        <h3>Climate Overview</h3>
        <div className="summary-grid">
          <div className="summary-card">
            <div className="summary-icon">🌡️</div>
            <div className="summary-info">
              <span className="summary-label">Annual Avg Temp</span>
              <span className="summary-value">{annualAvgTemp}°C</span>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon">💧</div>
            <div className="summary-info">
              <span className="summary-label">Annual Rainfall</span>
              <span className="summary-value">{annualRainfall} mm</span>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon">🔥</div>
            <div className="summary-info">
              <span className="summary-label">Hottest Month</span>
              <span className="summary-value">{hottestMonth.month_name}</span>
              <span className="summary-sub">{hottestMonth.temperature?.average_max_celsius}°C</span>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon">❄️</div>
            <div className="summary-info">
              <span className="summary-label">Coldest Month</span>
              <span className="summary-value">{coldestMonth.month_name}</span>
              <span className="summary-sub">{coldestMonth.temperature?.average_min_celsius}°C</span>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon">☔</div>
            <div className="summary-info">
              <span className="summary-label">Wettest Month</span>
              <span className="summary-value">{wettest.month_name}</span>
              <span className="summary-sub">{wettest.rainfall?.average_monthly_total_mm} mm</span>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon">📊</div>
            <div className="summary-info">
              <span className="summary-label">Data Coverage</span>
              <span className="summary-value">{monthlyStats[0]?.years_covered} years</span>
            </div>
          </div>
        </div>
      </div>

      {/* Annual Temperature Cycle */}
      <div className="chart-section">
        <h3>📈 Annual Temperature Cycle</h3>
        <p className="chart-description">Average, minimum, and maximum temperatures throughout the year</p>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={temperatureData}>
            <defs>
              <linearGradient id="tempMaxGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ff6b6b" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#ff6b6b" stopOpacity={0.1}/>
              </linearGradient>
              <linearGradient id="tempMinGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#4dabf7" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#4dabf7" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey="month" stroke="#86868b" style={{ fontSize: '12px' }} />
            <YAxis stroke="#86868b" style={{ fontSize: '12px' }} label={{ value: '°C', angle: -90, position: 'insideLeft' }} />
            <Tooltip
              contentStyle={{
                background: 'rgba(255, 255, 255, 0.95)',
                border: '0.5px solid rgba(0, 0, 0, 0.1)',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
              }}
            />
            <Legend />
            <Area type="monotone" dataKey="maxTemp" stroke="#ff6b6b" fillOpacity={1} fill="url(#tempMaxGradient)" name="Max Temp" />
            <Area type="monotone" dataKey="avgTemp" stroke="#ffa94d" fillOpacity={0.6} fill="#ffa94d" name="Avg Temp" />
            <Area type="monotone" dataKey="minTemp" stroke="#4dabf7" fillOpacity={1} fill="url(#tempMinGradient)" name="Min Temp" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Monthly Rainfall Pattern */}
      <div className="chart-section">
        <h3>💧 Monthly Rainfall Distribution</h3>
        <p className="chart-description">Average monthly precipitation and rainy day frequency</p>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={rainfallData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey="month" stroke="#86868b" style={{ fontSize: '12px' }} />
            <YAxis yAxisId="left" stroke="#86868b" style={{ fontSize: '12px' }} label={{ value: 'mm', angle: -90, position: 'insideLeft' }} />
            <YAxis yAxisId="right" orientation="right" stroke="#86868b" style={{ fontSize: '12px' }} label={{ value: '%', angle: 90, position: 'insideRight' }} />
            <Tooltip
              contentStyle={{
                background: 'rgba(255, 255, 255, 0.95)',
                border: '0.5px solid rgba(0, 0, 0, 0.1)',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
              }}
            />
            <Legend />
            <Bar yAxisId="left" dataKey="rainfall" fill="#4dabf7" name="Rainfall (mm)" radius={[8, 8, 0, 0]} />
            <Line yAxisId="right" type="monotone" dataKey="rainyDays" stroke="#228be6" strokeWidth={2} name="Rainy Days (%)" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Wind & Cloud Cover */}
      <div className="chart-section">
        <h3>💨 Wind Speed & Cloud Cover</h3>
        <p className="chart-description">Average wind speed and cloud coverage patterns</p>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={windCloudData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey="month" stroke="#86868b" style={{ fontSize: '12px' }} />
            <YAxis yAxisId="left" stroke="#86868b" style={{ fontSize: '12px' }} label={{ value: 'm/s', angle: -90, position: 'insideLeft' }} />
            <YAxis yAxisId="right" orientation="right" stroke="#86868b" style={{ fontSize: '12px' }} label={{ value: '%', angle: 90, position: 'insideRight' }} />
            <Tooltip
              contentStyle={{
                background: 'rgba(255, 255, 255, 0.95)',
                border: '0.5px solid rgba(0, 0, 0, 0.1)',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
              }}
            />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="wind" stroke="#51cf66" strokeWidth={2} dot={{ fill: '#51cf66', r: 4 }} name="Wind Speed (m/s)" />
            <Line yAxisId="right" type="monotone" dataKey="cloud" stroke="#868e96" strokeWidth={2} dot={{ fill: '#868e96', r: 4 }} name="Cloud Cover (%)" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Monthly Details Table */}
      <div className="monthly-details-section">
        <h3>📅 Monthly Statistics Breakdown</h3>
        <div className="monthly-table-wrapper">
          <table className="monthly-table">
            <thead>
              <tr>
                <th>Month</th>
                <th>Avg Temp (°C)</th>
                <th>Rainfall (mm)</th>
                <th>Rainy Days</th>
                <th>Wind (m/s)</th>
                <th>Cloud (%)</th>
              </tr>
            </thead>
            <tbody>
              {monthlyStats.map((month, idx) => (
                <tr key={idx}>
                  <td className="month-name">{month.month_name}</td>
                  <td>{month.temperature?.average_mean_celsius}°C</td>
                  <td>{month.rainfall?.average_monthly_total_mm} mm</td>
                  <td>{month.rainfall?.rainy_days_percent}%</td>
                  <td>{month.wind?.average_speed_ms} m/s</td>
                  <td>{month.cloud_cover?.average_percent}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Data Source */}
      <div className="data-source-info">
        <p>📊 Based on {monthlyStats[0]?.years_covered} years of historical ERA5 reanalysis data</p>
        <p>🔢 Total days analyzed: {monthlyStats.reduce((sum, m) => sum + (m.total_days || 0), 0).toLocaleString()}</p>
      </div>
    </div>
  );
};

export default WeatherStatsTab;
