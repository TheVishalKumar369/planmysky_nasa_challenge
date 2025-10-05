import React, { useState, useContext, useRef } from 'react';
import WeatherPredictionTab from './WeatherPredictionTab';
import WeatherStatsTab from './WeatherStatsTab';
import DatePicker from './DatePicker';
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import MiniPosts from './MiniPosts';
import LocalTrends from './LocalTrends';
import UserDashboard from './UserDashboard';
import WeatherSurvey from './WeatherSurvey';
import { AuthContext } from '../contexts/AuthContext';
import html2canvas from 'html2canvas';


const ResultsPanel = ({ isOpen, onClose, weatherData, locationData, selectedDate, onDateChange }) => {
  const { token } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('probability');
  const [selectedOption, setSelectedOption] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const tabContentRef = useRef(null);

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

  // Download weather data as JSON
  const handleDownloadJSON = () => {
    if (!weatherData || !locationData) {
      alert('No weather data available to download');
      return;
    }

    const dataToDownload = {
      location: {
        selected: locationData.clicked,
        weatherStation: locationData.nearest
      },
      weatherPrediction: weatherData,
      downloadedAt: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(dataToDownload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;

    const locationName = locationData.nearest?.name || 'unknown';
    const date = weatherData.date || new Date().toISOString().split('T')[0];
    link.download = `weather-data-${locationName}-${date}.json`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Download charts as images (only chart elements, not entire tab)
  const handleDownloadChart = async () => {
    if (!tabContentRef.current) {
      alert('No content available to download');
      return;
    }

    try {
      // Find all chart sections in the current tab
      const chartSections = tabContentRef.current.querySelectorAll('.chart-section');

      if (chartSections.length === 0) {
        alert('No charts found in current tab');
        return;
      }

      const locationName = locationData?.nearest?.name || 'unknown';
      const date = new Date().toISOString().split('T')[0];

      // If only one chart, download it directly
      if (chartSections.length === 1) {
        const canvas = await html2canvas(chartSections[0], {
          backgroundColor: '#ffffff',
          scale: 2,
          logging: false,
          useCORS: true
        });

        const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `weather-chart-${activeTab}-${locationName}-${date}.png`;

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      } else {
        // Multiple charts - download all as separate files
        for (let i = 0; i < chartSections.length; i++) {
          const canvas = await html2canvas(chartSections[i], {
            backgroundColor: '#ffffff',
            scale: 2,
            logging: false,
            useCORS: true
          });

          const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;

          // Get chart title from h3 element
          const chartTitle = chartSections[i].querySelector('h3')?.textContent.toLowerCase().replace(/[^a-z0-9]+/g, '-') || `chart-${i + 1}`;
          link.download = `weather-${chartTitle}-${locationName}-${date}.png`;

          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          URL.revokeObjectURL(url);

          // Small delay between downloads to avoid browser blocking
          if (i < chartSections.length - 1) {
            await new Promise(resolve => setTimeout(resolve, 300));
          }
        }

        alert(`${chartSections.length} charts downloaded successfully!`);
      }
    } catch (error) {
      console.error('Error downloading chart:', error);
      alert('Failed to download charts. Please try again.');
    }
  };

  return (
    <div
      className={`results-panel ${isOpen ? 'open' : ''}`}
    >
      {/* Header with close button */}
      <div className="panel-header draggable-header">
        <h2>PlanMySky</h2>
        <div className="header-actions">
          <button className="download-btn" onClick={handleDownloadJSON} title="Download Data as JSON">
            📥 JSON
          </button>
          <button className="download-btn" onClick={handleDownloadChart} title="Download Chart as Image">
            📊 PNG
          </button>
          <button className="close-btn" onClick={onClose} title="Close Panel">
            ✕
          </button>
        </div>
      </div>

      {/* Date Picker inside panel */}
      {selectedDate && onDateChange && (
        <div className="panel-date-picker">
          <DatePicker
            selectedDate={selectedDate}
            onDateSelect={onDateChange}
          />
        </div>
      )}

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
      <div className="tab-content" ref={tabContentRef}>
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
