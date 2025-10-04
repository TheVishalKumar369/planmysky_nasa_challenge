import React, { useState } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths } from 'date-fns';

const DatePicker = ({ selectedDate, onDateSelect }) => {
  const [currentMonth, setCurrentMonth] = useState(selectedDate);
  const [isOpen, setIsOpen] = useState(false);

  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);
  const daysInMonth = eachDayOfInterval({ start: monthStart, end: monthEnd });

  // Get starting day of week (0 = Sunday)
  const startingDayOfWeek = monthStart.getDay();

  const previousMonth = () => {
    setCurrentMonth(subMonths(currentMonth, 1));
  };

  const nextMonth = () => {
    setCurrentMonth(addMonths(currentMonth, 1));
  };

  const handleDateSelect = (date) => {
    onDateSelect(date);
    setIsOpen(false);
  };

  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div className="custom-date-picker">
      <label className="date-picker-label">Select Prediction Date</label>

      {/* Selected Date Display */}
      <button
        className="date-display-button"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="date-display-content">
          <span className="date-icon">📅</span>
          <div className="date-text">
            <span className="date-main">{format(selectedDate, 'MMMM dd, yyyy')}</span>
            <span className="date-sub">{format(selectedDate, 'EEEE')}</span>
          </div>
        </div>
        <span className={`chevron ${isOpen ? 'up' : 'down'}`}>▼</span>
      </button>

      {/* Calendar Popup */}
      {isOpen && (
        <div className="calendar-popup">
          {/* Calendar Header */}
          <div className="calendar-header">
            <button className="calendar-nav-btn" onClick={previousMonth}>
              ◀
            </button>
            <div className="calendar-month-year">
              {format(currentMonth, 'MMMM yyyy')}
            </div>
            <button className="calendar-nav-btn" onClick={nextMonth}>
              ▶
            </button>
          </div>

          {/* Weekday Labels */}
          <div className="calendar-weekdays">
            {weekDays.map(day => (
              <div key={day} className="calendar-weekday">
                {day}
              </div>
            ))}
          </div>

          {/* Calendar Grid */}
          <div className="calendar-grid">
            {/* Empty cells for days before month starts */}
            {Array.from({ length: startingDayOfWeek }).map((_, index) => (
              <div key={`empty-${index}`} className="calendar-day empty"></div>
            ))}

            {/* Actual days */}
            {daysInMonth.map(day => {
              const isSelected = isSameDay(day, selectedDate);
              const isToday = isSameDay(day, new Date());

              return (
                <button
                  key={day.toString()}
                  className={`calendar-day ${isSelected ? 'selected' : ''} ${isToday ? 'today' : ''}`}
                  onClick={() => handleDateSelect(day)}
                >
                  {format(day, 'd')}
                </button>
              );
            })}
          </div>

          {/* Quick Select Buttons */}
          <div className="calendar-quick-select">
            <button
              className="quick-select-btn"
              onClick={() => handleDateSelect(new Date())}
            >
              Today
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DatePicker;
