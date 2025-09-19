import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // Dummy state for user authentication
  // Replace this with a real authentication state from your app's context or Redux store
  const [isLoggedIn, setIsLoggedIn] = useState(true);
  const [userProfile, setUserProfile] = useState({
    name: 'John Doe',
    avatar: 'JD',
  });

  // Handle logout
  const handleLogout = () => {
    // Perform actual logout logic (clear tokens, reset state, etc.)
    setIsLoggedIn(false);
    navigate('/');
    setIsMenuOpen(false);
  };

  // Function to handle smooth scrolling
  const scrollToSection = (sectionId) => {
    if (location.pathname !== '/') {
      navigate('/');
      setTimeout(() => {
        scrollToSectionElement(sectionId);
      }, 100);
      return;
    }

    scrollToSectionElement(sectionId);
    setIsMenuOpen(false);
  };

  // Helper function to scroll to section with proper offset
  const scrollToSectionElement = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      const navbarHeight = 64;
      const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
      const elementHeight = element.offsetHeight;
      const viewportHeight = window.innerHeight;

      let scrollPosition;

      if (elementHeight < viewportHeight - navbarHeight) {
        scrollPosition = elementPosition - (viewportHeight - elementHeight) / 2;
      } else {
        scrollPosition = elementPosition - navbarHeight - 32;
      }

      window.scrollTo({
        top: Math.max(0, Math.round(scrollPosition)),
        behavior: 'smooth'
      });
    }
  };

  // Function to handle home navigation
  const handleHomeClick = (e) => {
    if (location.pathname === '/') {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    setIsMenuOpen(false);
  };

  return (
    <nav className="bg-card border-b border-border shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link
              to="/"
              className="flex-shrink-0 flex items-center"
              onClick={handleHomeClick}
            >
              <span className="text-primary text-2xl font-bold">PactAI</span>
            </Link>
          </div>

          {/* Centered Navigation Links - Desktop */}
          <div className="hidden md:flex items-center absolute left-1/2 transform -translate-x-1/2 space-x-8 mt-4">
            <Link
              to="/"
              className="text-foreground hover:text-primary transition-colors duration-300"
              onClick={handleHomeClick}
            >
              Home
            </Link>
            <button
              onClick={() => scrollToSection('pdf-summarizer')}
              className="text-foreground hover:text-primary transition-colors duration-300"
            >
              How It Works
            </button>
            <button
              onClick={() => scrollToSection('why-choose-us')}
              className="text-foreground hover:text-primary transition-colors duration-300"
            >
              Why Choose Us
            </button>
          </div>

          {/* Right Side Items - Desktop */}
          <div className="hidden md:flex items-center space-x-4">
            {isLoggedIn ? (
              // Logged-in view
              <>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-r from-primary to-accent flex items-center justify-center text-white font-semibold text-sm">
                    {userProfile.avatar}
                  </div>
                  <span className="font-medium text-foreground">{userProfile.name}</span>
                </div>
                {/* Updated logout button color */}
                <button
                  onClick={handleLogout}
                  className="inline-flex items-center justify-center px-6 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-md hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:-translate-y-0.5"
                >
                  Logout
                </button>
              </>
            ) : (
              // Not logged-in view
              <>
                <Link to="/login" className="text-foreground hover:text-primary transition-colors duration-300">
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="inline-flex items-center justify-center px-6 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-md hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:-translate-y-0.5"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center space-x-2">
            {isLoggedIn ? (
              // Logged-in view for mobile
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-primary to-accent flex items-center justify-center text-white font-semibold text-sm">
                  {userProfile.avatar}
                </div>
                <button
                  onClick={handleLogout}
                  className="p-2 rounded-md text-foreground hover:bg-border transition-colors"
                >
                  Logout
                </button>
              </div>
            ) : (
              // Not logged-in view for mobile
              <div className="flex items-center space-x-2">
                <Link to="/login" className="text-foreground hover:text-primary transition-colors duration-300">
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="px-4 py-2 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg transition-all duration-300 hover:from-blue-700 hover:to-purple-700"
                >
                  Sign Up
                </Link>
              </div>
            )}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-foreground hover:text-primary focus:outline-none"
              aria-label="Toggle menu"
            >
              <svg
                className="h-6 w-6"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                {isMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-card border-t border-border">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <Link
              to="/"
              className="block px-3 py-2 rounded-md text-base font-medium text-foreground hover:text-primary hover:bg-secondary transition-colors duration-300"
              onClick={handleHomeClick}
            >
              Home
            </Link>
            <button
              onClick={() => scrollToSection('pdf-summarizer')}
              className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-foreground hover:text-primary hover:bg-secondary transition-colors duration-300"
            >
              How It Works
            </button>
            <button
              onClick={() => scrollToSection('why-choose-us')}
              className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-foreground hover:text-primary hover:bg-secondary transition-colors duration-300"
            >
              Why Choose Us
            </button>
            {isLoggedIn ? (
              <button
                onClick={handleLogout}
                className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-foreground hover:text-primary hover:bg-secondary transition-colors duration-300"
              >
                Logout
              </button>
            ) : (
              <>
                <Link
                  to="/login"
                  className="block px-3 py-2 rounded-md text-base font-medium text-foreground hover:text-primary hover:bg-secondary transition-colors duration-300"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="block px-3 py-2 rounded-md text-base font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transition-all duration-300"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;