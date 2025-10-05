import React, { useState, useRef, useEffect, useContext } from 'react';
import Signup from './SignUp';
import Login from './LogIn';
import { AuthContext } from "../contexts/AuthContext";
import PrivacyPolicy from './PrivacyPolicy';
import Terms from './Terms';

const HamburgerMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const [showSignup, setShowSignup] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [showPrivacy, setShowPrivacy] = useState(false);
  const [showTerms, setShowTerms] = useState(false);

  const { token, logout } = useContext(AuthContext);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleMenuItemClick = (action) => {
    console.log(`Menu action: ${action}`);

    if (action === "signup") {
      setShowSignup(true);
      setShowLogin(false);
    } else if (action === "login") {
      setShowLogin(true);
      setShowSignup(false);
    } else if (action === "logout") {
      logout();
    } else if (action === "privacy") {
      setShowPrivacy(true);
    } else if (action === "terms") {
      setShowTerms(true);
    }

    setIsOpen(false);
  };


  return (
    <div ref={menuRef} className="hamburger-menu-container">
      {/* Hamburger Button */}
      <button
        className={`hamburger-button ${isOpen ? 'open' : ''}`}
        onClick={toggleMenu}
        aria-label="Menu"
      >
        <span className="hamburger-line"></span>
        <span className="hamburger-line"></span>
        <span className="hamburger-line"></span>
      </button>

      {/* Menu Dropdown */}
      {isOpen && (
        <div className="hamburger-dropdown">
          <div className="menu-section">
            {!token ? (
              <>
                <button className="menu-item" onClick={() => handleMenuItemClick("signup")}>
                  <span className="menu-icon">👤</span>
                  <span className="menu-text">Sign Up</span>
                </button>
                <button className="menu-item" onClick={() => handleMenuItemClick("login")}>
                  <span className="menu-icon">🔐</span>
                  <span className="menu-text">Login</span>
                </button>
              </>
            ) : (
              <button className="menu-item" onClick={() => handleMenuItemClick("logout")}>
                <span className="menu-icon">🚪</span>
                <span className="menu-text">Logout</span>
              </button>
            )}
          </div>

          <div className="menu-divider"></div>

          <div className="menu-section">
            <a
              href="https://github.com/TheVishalkumar369/PlanMySky"
              target="_blank"
              rel="noopener noreferrer"
              className="menu-item"
            >
              <span className="menu-icon">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
                </svg>
              </span>
              <span className="menu-text">View on GitHub</span>
            </a>
            <div className="menu-item menu-info">
              <span className="menu-icon">🚀</span>
              <span className="menu-text">Made with ❤️ for NASA Space Apps</span>
            </div>
          </div>

          <div className="menu-divider"></div>

          <div className="menu-section">
            <button
              className="menu-item menu-small"
              onClick={() => handleMenuItemClick('privacy')}
            >
              <span className="menu-text">Privacy Policy</span>
            </button>
            <button
              className="menu-item menu-small"
              onClick={() => handleMenuItemClick('terms')}
            >
              <span className="menu-text">Terms & Conditions</span>
            </button>
          </div>
        </div>
      )}

      {/* Signup Popup */}
      {showSignup && (
        <div className="popup-overlay">
          <div className="popup-content auth-modal">
            <button className="close-btn" onClick={() => setShowSignup(false)}>&times;</button>
            <Signup onSuccess={() => setShowSignup(false)} />
          </div>
        </div>
      )}

      {/* Login Popup */}
      {showLogin && (
        <div className="popup-overlay">
          <div className="popup-content auth-modal">
            <button className="close-btn" onClick={() => setShowLogin(false)}>&times;</button>
            <Login onSuccess={() => setShowLogin(false)} />
          </div>
        </div>
      )}

      {/* Privacy Policy Modal */}
      {showPrivacy && (
        <div className="popup-overlay">
          <div className="popup-content privacy-modal">
            <button className="close-btn" onClick={() => setShowPrivacy(false)}>
              &times;
            </button>
            <PrivacyPolicy />
          </div>
        </div>
      )}

      {/* Terms & Conditions Modal */}
      {showTerms && (
        <div className="popup-overlay">
          <div className="popup-content privacy-modal">
            <button className="close-btn" onClick={() => setShowTerms(false)}>
              &times;
            </button>
            <Terms/>
          </div>
        </div>
      )}


    </div>
  );
};

export default HamburgerMenu;
