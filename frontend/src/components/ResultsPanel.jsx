import React, { useState } from 'react';
import WeatherPredictionTab from './WeatherPredictionTab';
import WeatherStatsTab from './WeatherStatsTab';

const ResultsPanel = ({ isOpen, onClose, weatherData, locationData }) => {
  const [activeTab, setActiveTab] = useState('probability');

  if (!isOpen) return null;

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
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'probability' && (
          <WeatherPredictionTab weatherData={weatherData} />
        )}

        {activeTab === 'stats' && (
          <WeatherStatsTab weatherData={weatherData} locationData={locationData} />
        )}

        {activeTab === 'connect' && (
          <div className="tab-panel">
            <h3>Weather Connect</h3>
            <div className="data-content">
              <p>Weather connection and integration data will be displayed here.</p>
              {weatherData && (
                <pre>{JSON.stringify(weatherData, null, 2)}</pre>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsPanel;
