import React, { useState, useContext } from 'react';
import WeatherPredictionTab from './WeatherPredictionTab';
import WeatherStatsTab from './WeatherStatsTab';
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import MiniPosts from './MiniPosts';
import LocalTrends from './LocalTrends';
import UserDashboard from './UserDashboard';
import WeatherSurvey from './WeatherSurvey';
import { AuthContext } from '../contexts/AuthContext';


const ResultsPanel = ({ isOpen, onClose, weatherData, locationData }) => {
  const { token } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('probability');
  const [selectedOption, setSelectedOption] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  // dummy data: todo
  const [pollResults, setPollResults] = useState([
    { name: "Stay home", value: 40 },
    { name: "Go out anyway", value: 35 },
    { name: "Work outdoors", value: 25 },
  ]);

  if (!isOpen) return null;

    const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

  const handleVote = () => {
    if (!selectedOption) return;

    // update poll results locally
    setPollResults((prev) =>
      prev.map((item) =>
        item.name === selectedOption
          ? { ...item, value: item.value + 1 }
          : item
      )
    );
    setSubmitted(true);
  };

  return (
    <div
      className={`results-panel ${isOpen ? 'open' : ''}`}
    >
      {/* Header with close button */}
      <div className="panel-header draggable-header">
        <h2>PlanMySky</h2>
        <button className="close-btn" onClick={onClose} title="Close Panel">
          ✕
        </button>
      </div>

      {/* Location Info */}
      {locationData && (
        <div className="location-info">
          <p>
            <strong>Selected Location:</strong> {locationData.clicked.lat.toFixed(4)}, {locationData.clicked.lng.toFixed(4)}
          </p>
          {locationData.nearest && (
            <p>
              <strong>Weather Station:</strong> {locationData.nearest.display_name || locationData.nearest.name}
              <span className="distance"> ({locationData.nearest.distance})</span>
            </p>
          )}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button
          className={`tab-btn ${activeTab === 'probability' ? 'active' : ''}`}
          onClick={() => setActiveTab('probability')}
        >
          Weather Probability
        </button>
        <button
          className={`tab-btn ${activeTab === 'stats' ? 'active' : ''}`}
          onClick={() => setActiveTab('stats')}
        >
          Weather Stats
        </button>
        <button
          className={`tab-btn ${activeTab === 'connect' ? 'active' : ''}`}
          onClick={() => setActiveTab('connect')}
        >
          Weather Connect
        </button>
        <button
          className={`tab-btn ${activeTab === 'social' ? 'active' : ''}`}
          onClick={() => setActiveTab('social')}
        >
          Social
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'probability' && (
          <WeatherPredictionTab weatherData={weatherData} locationData={locationData} />
        )}

        {activeTab === 'stats' && (
          <WeatherStatsTab weatherData={weatherData} locationData={locationData} />
        )}


        {activeTab === "connect" && (
          <div>
            <MiniPosts />
            <LocalTrends />
          </div>
        )}

        {activeTab === 'social' && (
          <>
            {token && <UserDashboard />}
            <WeatherSurvey weatherData={weatherData} locationData={locationData} />
          </>
        )}
      </div>
    </div>
  );
};

export default ResultsPanel;
