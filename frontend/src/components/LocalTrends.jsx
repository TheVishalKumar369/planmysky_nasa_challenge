import React, { useState, useEffect } from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { getCommunityStats } from "../services/communityApi";

const COLORS = ["#82ca9d", "#8884d8", "#ff7f50", "#ffc658", "#ff8042"];

const LocalTrends = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
    // Refresh stats every 30 seconds
    const interval = setInterval(loadStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    try {
      const data = await getCommunityStats();
      setStats(data);
    } catch (err) {
      console.error('Error loading community stats:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="local-trends">
        <h3>📊 Community Stats</h3>
        <p style={{ textAlign: 'center', padding: '20px' }}>Loading stats...</p>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="local-trends">
        <h3>📊 Community Stats</h3>
        <p style={{ textAlign: 'center', padding: '20px', color: '#666' }}>
          Stats unavailable
        </p>
      </div>
    );
  }

  // Prepare data for chart
  const locationData = stats.top_locations.map(loc => ({
    name: loc.location,
    value: loc.count
  }));

  return (
    <div className="local-trends">
      <h3>📊 Community Stats</h3>
      <p>Real-time community activity</p>

      {/* Stats Overview */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '10px',
        marginBottom: '20px'
      }}>
        <div style={{
          background: '#e3f2fd',
          padding: '15px',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1976d2' }}>
            {stats.total_messages}
          </div>
          <div style={{ fontSize: '12px', color: '#666' }}>Total Messages</div>
        </div>

        <div style={{
          background: '#f3e5f5',
          padding: '15px',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#7b1fa2' }}>
            {stats.recent_messages_24h}
          </div>
          <div style={{ fontSize: '12px', color: '#666' }}>Last 24 Hours</div>
        </div>

        <div style={{
          background: '#fff3e0',
          padding: '15px',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f57c00' }}>
            {stats.total_reactions}
          </div>
          <div style={{ fontSize: '12px', color: '#666' }}>Total Reactions</div>
        </div>

        <div style={{
          background: '#e8f5e9',
          padding: '15px',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#388e3c' }}>
            {stats.top_locations.length}
          </div>
          <div style={{ fontSize: '12px', color: '#666' }}>Active Locations</div>
        </div>
      </div>

      {/* Top Locations Chart */}
      {locationData.length > 0 && (
        <>
          <h4>🌍 Top Active Locations</h4>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={locationData}
                  dataKey="value"
                  nameKey="name"
                  outerRadius={100}
                  fill="#8884d8"
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                >
                  {locationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Location List */}
          <div className="reports-section">
            <h4>📍 Location Breakdown</h4>
            <ul className="reports-list">
              {stats.top_locations.map((location, index) => (
                <li key={index}>
                  <strong>{location.location}:</strong> {location.count} {location.count === 1 ? 'message' : 'messages'}
                </li>
              ))}
            </ul>
          </div>
        </>
      )}

      {locationData.length === 0 && (
        <div style={{ textAlign: 'center', padding: '20px', color: '#666' }}>
          <p>No location data available yet. Start sharing!</p>
        </div>
      )}
    </div>
  );
};

export default LocalTrends;
