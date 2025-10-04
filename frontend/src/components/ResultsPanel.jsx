import React, { useState } from 'react';
import WeatherPredictionTab from './WeatherPredictionTab';
import WeatherStatsTab from './WeatherStatsTab';
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import MiniPosts from './MiniPosts';
import LocalTrends from './LocalTrends';


const ResultsPanel = ({ isOpen, onClose, weatherData, locationData }) => {
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

        {/* {activeTab === 'connect' && (
          <div className="tab-panel">
            <h3>Weather Connect</h3>
            <div className="data-content">
              <p>Weather connection and integration data will be displayed here.</p>
              {weatherData && (
                <pre>{JSON.stringify(weatherData, null, 2)}</pre>
              )}
            </div>
          </div>
        )} */}

        {activeTab === "connect" && (
          <div>
            <MiniPosts />
            <LocalTrends />
          </div>
        )}

        {activeTab === 'social' && (
          <div className="tab-panel">
            <h3>🌦 Social Poll</h3>
            <div className="data-content">
              {!submitted ? (
                <>
                  <p><strong>Question:</strong> What are you planning today if it rains?</p>
                  <div className="poll-options">
                    {pollResults.map((option) => (
                      <label key={option.name} style={{ display: "block", margin: "5px 0" }}>
                        <input
                          type="radio"
                          name="poll"
                          value={option.name}
                          onChange={() => setSelectedOption(option.name)}
                        />
                        {option.name}
                      </label>
                    ))}
                  </div>
                  <button className="poll-btn" onClick={handleVote}>
                    Submit
                  </button>
                </>
              ) : (
                <>
                  <h4>Community Results:</h4>               
                  
                  <PieChart width={300} height={250}>
                    <Pie
                      data={pollResults}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      // label
                    >
                      {pollResults.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                
                  <p>✅ You voted: <strong>{selectedOption}</strong></p>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsPanel;
