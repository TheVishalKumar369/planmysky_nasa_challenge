import React, { useState, useEffect, useRef } from 'react';

const SearchBar = ({ isPanelOpen, onLocationSelect }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [locations, setLocations] = useState([]);
  const [filteredLocations, setFilteredLocations] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const searchRef = useRef(null);

  // Fetch available locations on mount
  useEffect(() => {
    const fetchLocations = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/locations');
        const data = await response.json();
        setLocations(data.locations || []);
      } catch (error) {
        console.error('Error fetching locations:', error);
      }
    };

    fetchLocations();
  }, []);

  // Filter locations based on search term
  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredLocations([]);
      setShowSuggestions(false);
      return;
    }

    const searchLower = searchTerm.toLowerCase();
    const filtered = locations.filter(loc => {
      const displayName = loc.display_name?.toLowerCase() || '';
      const name = loc.name?.toLowerCase() || '';
      return displayName.includes(searchLower) || name.includes(searchLower);
    });

    setFilteredLocations(filtered);
    setShowSuggestions(filtered.length > 0);
    setSelectedIndex(-1);
  }, [searchTerm, locations]);

  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleLocationClick = (location) => {
    setSearchTerm(location.display_name || location.name);
    setShowSuggestions(false);

    // Navigate to location
    if (location.latitude && location.longitude) {
      onLocationSelect({
        lat: location.latitude,
        lng: location.longitude
      });
    }
  };

  const handleKeyDown = (e) => {
    if (!showSuggestions) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev =>
          prev < filteredLocations.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && filteredLocations[selectedIndex]) {
          handleLocationClick(filteredLocations[selectedIndex]);
        } else if (filteredLocations.length === 1) {
          handleLocationClick(filteredLocations[0]);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        break;
      default:
        break;
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (filteredLocations.length > 0) {
      handleLocationClick(filteredLocations[0]);
    }
  };

  return (
    <div
      ref={searchRef}
      className={`search-bar ${isPanelOpen ? 'panel-open' : ''}`}
    >
      <form onSubmit={handleSubmit}>
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            value={searchTerm}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onFocus={() => searchTerm && setShowSuggestions(filteredLocations.length > 0)}
            placeholder="Search location..."
            className="search-input"
          />
          {searchTerm && (
            <button
              type="button"
              className="search-clear"
              onClick={() => {
                setSearchTerm('');
                setShowSuggestions(false);
              }}
            >
              ✕
            </button>
          )}
        </div>
      </form>

      {showSuggestions && (
        <div className="search-suggestions">
          {filteredLocations.map((location, index) => (
            <div
              key={location.name}
              className={`suggestion-item ${index === selectedIndex ? 'selected' : ''}`}
              onClick={() => handleLocationClick(location)}
              onMouseEnter={() => setSelectedIndex(index)}
            >
              <div className="suggestion-main">
                <span className="suggestion-icon">📍</span>
                <span className="suggestion-name">
                  {location.display_name || location.name}
                </span>
              </div>
              <div className="suggestion-meta">
                <span className="suggestion-coords">
                  {location.latitude?.toFixed(2)}, {location.longitude?.toFixed(2)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchBar;
