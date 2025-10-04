import React, { useRef, useEffect } from 'react';
import { MapContainer as LeafletMap, TileLayer, Marker, Circle, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// World view center and zoom
const DEFAULT_CENTER = [20, 0];
const DEFAULT_ZOOM = 2;

// Custom icon for clicked location (red)
const clickedIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Custom icon for nearest location (blue)
const stationIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Component to handle map clicks
function MapClickHandler({ onLocationSelect }) {
  useMapEvents({
    click: (e) => {
      const { lat, lng } = e.latlng;
      onLocationSelect({ lat, lng });
    },
  });

  return null;
}

const MapContainer = ({ onLocationSelect, selectedLocation, nearestLocation }) => {
  const mapRef = useRef(null);

  useEffect(() => {
    console.log('MapContainer mounted');

    // Keyboard shortcuts for zoom
    const handleKeyPress = (e) => {
      if (!mapRef.current) return;

      // Check if user is typing in an input field
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return;
      }

      if (e.key === '+' || e.key === '=') {
        e.preventDefault();
        mapRef.current.zoomIn();
      } else if (e.key === '-' || e.key === '_') {
        e.preventDefault();
        mapRef.current.zoomOut();
      }
    };

    window.addEventListener('keydown', handleKeyPress);

    return () => {
      console.log('MapContainer unmounting');
      window.removeEventListener('keydown', handleKeyPress);
    };
  }, []);

  // Zoom to location when selected
  useEffect(() => {
    if (selectedLocation && mapRef.current) {
      mapRef.current.setView([selectedLocation.lat, selectedLocation.lng], 6, {
        animate: true,
        duration: 0.5
      });
    }
  }, [selectedLocation]);

  const handleZoomIn = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (mapRef.current) {
      mapRef.current.zoomIn();
    }
  };

  const handleZoomOut = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (mapRef.current) {
      mapRef.current.zoomOut();
    }
  };

  const handleResetView = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (mapRef.current) {
      mapRef.current.setView(DEFAULT_CENTER, DEFAULT_ZOOM);
    }
  };

  const handleLocateMe = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (mapRef.current) {
      mapRef.current.locate({ setView: true, maxZoom: 10 });
    }
  };

  // Check if nearestLocation has valid coordinates
  const hasValidCoordinates = nearestLocation &&
    typeof nearestLocation.latitude === 'number' &&
    typeof nearestLocation.longitude === 'number' &&
    !isNaN(nearestLocation.latitude) &&
    !isNaN(nearestLocation.longitude);

  return (
    <div style={{ height: '100vh', width: '100%', position: 'relative', background: '#aad3df' }}>
      <LeafletMap
        ref={mapRef}
        center={DEFAULT_CENTER}
        zoom={DEFAULT_ZOOM}
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%', zIndex: 1 }}
        zoomControl={false}
        minZoom={2}
        maxZoom={8}
        worldCopyJump={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
        />

        <MapClickHandler onLocationSelect={onLocationSelect} />

        {selectedLocation && (
          <Marker
            position={[selectedLocation.lat, selectedLocation.lng]}
            icon={clickedIcon}
          />
        )}

        {/* Only render blue marker if we have valid coordinates */}
        {hasValidCoordinates && (
          <>
            <Marker
              position={[nearestLocation.latitude, nearestLocation.longitude]}
              icon={stationIcon}
            />

            {/* Coverage area circle */}
            {nearestLocation.coverage_km && (
              <Circle
                center={[nearestLocation.latitude, nearestLocation.longitude]}
                radius={nearestLocation.coverage_km * 1000}
                pathOptions={{
                  fillColor: '#667eea',
                  fillOpacity: 0.1,
                  color: '#667eea',
                  weight: 2,
                }}
              />
            )}
          </>
        )}
      </LeafletMap>

      {/* Custom Map Controls */}
      <div className="map-controls">
        <button
          onClick={handleZoomIn}
          onTouchStart={handleZoomIn}
          title="Zoom In (Press +)"
          className="map-control-btn"
          type="button"
        >
          +
        </button>
        <button
          onClick={handleZoomOut}
          onTouchStart={handleZoomOut}
          title="Zoom Out (Press -)"
          className="map-control-btn"
          type="button"
        >
          −
        </button>
        <button
          onClick={handleResetView}
          onTouchStart={handleResetView}
          title="Reset to World View"
          className="map-control-btn"
          type="button"
        >
          🌍
        </button>
        <button
          onClick={handleLocateMe}
          onTouchStart={handleLocateMe}
          title="Find My Location"
          className="map-control-btn"
          type="button"
        >
          📍
        </button>
      </div>

      {/* Map legend */}
      <div className="map-legend">
        <div className="legend-item">
          <span className="legend-marker red">🔴</span>
          <span>Clicked Location</span>
        </div>
        {hasValidCoordinates && (
          <div className="legend-item">
            <span className="legend-marker blue">🔵</span>
            <span>Weather Station</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default MapContainer;
