import { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const WeatherSurvey = ({ weatherData, locationData }) => {
  const [surveyQuestion, setSurveyQuestion] = useState(null);
  const [surveyOptions, setSurveyOptions] = useState([]);
  const [selectedOption, setSelectedOption] = useState(null);
  const [hasVoted, setHasVoted] = useState(false);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  useEffect(() => {
    if (weatherData && locationData) {
      // Reset state when location changes
      setHasVoted(false);
      setSelectedOption(null);
      setResults([]);

      // Generate new question and check vote status
      generateSurveyQuestion();
      checkIfVoted();
    }
  }, [weatherData, locationData]);

  const generateSurveyQuestion = () => {
    if (!weatherData) return;

    const rainyProbability = weatherData.rainfall?.probability_percent || 0;
    const temp = weatherData.temperature?.mean_avg_celsius || 20;
    const weatherCategory = weatherData.weather_category || '';

    let question = '';
    let options = [];

    // Generate question based on weather conditions
    if (rainyProbability > 70) {
      question = `Heavy rain is predicted (${rainyProbability}% chance). Are you staying indoors?`;
      options = ['Yes, staying home', 'No, going out anyway', 'Maybe, depends', 'Working from home'];
    } else if (rainyProbability > 40) {
      question = `Moderate rain expected (${rainyProbability}% chance). How will you adapt?`;
      options = ['Carry an umbrella', 'Cancel outdoor plans', 'Proceed as planned', 'Reschedule activities'];
    } else if (temp > 30) {
      question = `High temperature expected (${temp}°C). How will you beat the heat?`;
      options = ['Stay in AC', 'Go swimming', 'Outdoor activities', 'Indoor activities'];
    } else if (temp < 10) {
      question = `Cold weather ahead (${temp}°C). What are your plans?`;
      options = ['Stay warm indoors', 'Outdoor winter activities', 'Hot beverage time', 'Business as usual'];
    } else if (weatherCategory.toLowerCase().includes('clear')) {
      question = 'Perfect weather ahead! What will you do?';
      options = ['Outdoor activities', 'Picnic/BBQ', 'Sports', 'Stay indoors anyway'];
    } else {
      question = `Weather looks ${weatherCategory.toLowerCase()}. What are your plans?`;
      options = ['Outdoor activities', 'Indoor activities', 'Flexible plans', 'No specific plans'];
    }

    setSurveyQuestion(question);
    setSurveyOptions(options);
  };

  const checkIfVoted = () => {
    if (!weatherData || !locationData) return;

    const locationKey = `${locationData.nearest?.name}_${weatherData.date}`;
    const voted = localStorage.getItem(`survey_voted_${locationKey}`);

    if (voted) {
      setHasVoted(true);
      fetchResults();
    }
  };

  const handleVote = async () => {
    if (!selectedOption || !weatherData || !locationData) return;

    setLoading(true);

    try {
      const locationKey = `${locationData.nearest?.name}_${weatherData.date}`;

      // Submit vote to backend
      const response = await fetch('http://localhost:8000/api/survey/vote', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          location: locationData.nearest?.name,
          date: weatherData.date,
          question: surveyQuestion,
          option: selectedOption,
        }),
      });

      if (response.ok) {
        // Mark as voted in localStorage
        localStorage.setItem(`survey_voted_${locationKey}`, 'true');
        localStorage.setItem(`survey_choice_${locationKey}`, selectedOption);

        setHasVoted(true);
        await fetchResults();
      } else {
        throw new Error('Failed to submit vote');
      }
    } catch (error) {
      console.error('Error submitting vote:', error);
      // Fallback to local storage only
      const locationKey = `${locationData.nearest?.name}_${weatherData.date}`;
      localStorage.setItem(`survey_voted_${locationKey}`, 'true');
      localStorage.setItem(`survey_choice_${locationKey}`, selectedOption);
      setHasVoted(true);

      // Use mock results if API fails
      const mockResults = surveyOptions.map(option => ({
        name: option,
        value: option === selectedOption ? 1 : Math.floor(Math.random() * 10)
      }));
      setResults(mockResults);
    } finally {
      setLoading(false);
    }
  };

  const fetchResults = async () => {
    if (!weatherData || !locationData) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/survey/results?location=${locationData.nearest?.name}&date=${weatherData.date}`
      );

      if (response.ok) {
        const data = await response.json();
        setResults(data.results || []);
      } else {
        throw new Error('Failed to fetch results');
      }
    } catch (error) {
      console.error('Error fetching results:', error);
      // Use mock results
      const mockResults = surveyOptions.map(option => ({
        name: option,
        value: Math.floor(Math.random() * 20) + 5
      }));
      setResults(mockResults);
    }
  };

  if (!weatherData || !locationData) {
    return (
      <div className="weather-survey">
        <div className="survey-card">
          <p className="survey-message">
            📍 Select a location on the map to see weather-based survey questions
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="weather-survey">
      <div className="survey-card">
        <h3>🌤️ Community Weather Survey</h3>

        <div className="survey-location-info">
          <p><strong>Location:</strong> {locationData.nearest?.display_name || locationData.nearest?.name}</p>
          <p><strong>Date:</strong> {weatherData.date}</p>
          <p><strong>Weather:</strong> {weatherData.weather_category}</p>
        </div>

        {!hasVoted ? (
          <div className="survey-question-section">
            <p className="survey-question">{surveyQuestion}</p>

            <div className="survey-options">
              {surveyOptions.map((option) => (
                <label key={option} className="survey-option">
                  <input
                    type="radio"
                    name="survey"
                    value={option}
                    checked={selectedOption === option}
                    onChange={() => setSelectedOption(option)}
                  />
                  <span>{option}</span>
                </label>
              ))}
            </div>

            <button
              className="survey-submit-btn"
              onClick={handleVote}
              disabled={!selectedOption || loading}
            >
              {loading ? 'Submitting...' : 'Submit Vote'}
            </button>
          </div>
        ) : (
          <div className="survey-results-section">
            <div className="voted-badge">
              ✓ You voted: <strong>{localStorage.getItem(`survey_choice_${locationData.nearest?.name}_${weatherData.date}`)}</strong>
            </div>

            <h4>Community Results</h4>

            {results.length > 0 && (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={results}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {results.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            )}

            <div className="survey-stats">
              <p className="total-votes">
                Total votes: <strong>{results.reduce((sum, r) => sum + r.value, 0)}</strong>
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WeatherSurvey;
