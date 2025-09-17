import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuth } from './App';
import { Link, useNavigate } from 'react-router-dom';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

// Header Dropdown Icons Component
const HeaderDropdownIcons = () => {
  const [expandedDropdown, setExpandedDropdown] = useState(null);
  const dropdownRef = useRef(null);

  const toggleDropdown = (dropdown) => {
    setExpandedDropdown(expandedDropdown === dropdown ? null : dropdown);
  };

  // Helper functions for color classes - Refined Dark Theme
  const getActiveClasses = (color) => {
    const colorClasses = {
      blue: 'bg-purple-900/40 text-purple-300 shadow-lg',
      green: 'bg-orange-900/40 text-orange-300 shadow-lg',
      purple: 'bg-purple-900/40 text-purple-300 shadow-lg',
      orange: 'bg-orange-900/40 text-orange-300 shadow-lg'
    };
    return colorClasses[color];
  };

  const getHoverClasses = (color) => {
    const colorClasses = {
      blue: 'text-gray-400 hover:bg-purple-900/20 hover:text-purple-300',
      green: 'text-gray-400 hover:bg-orange-900/20 hover:text-orange-300',
      purple: 'text-gray-400 hover:bg-purple-900/20 hover:text-purple-300',
      orange: 'text-gray-400 hover:bg-orange-900/20 hover:text-orange-300'
    };
    return colorClasses[color];
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setExpandedDropdown(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const dropdownItems = [
    {
      id: 'noBrokerFee',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      ),
      tooltip: 'No Broker Fee Apartments',
      color: 'blue',
      content: (
        <div className="p-4">
          <h4 className="font-semibold text-white mb-2">No Broker Fee Apartments NYC</h4>
          <p className="text-gray-300 text-sm mb-3">
            Discover over 1,000 <strong className="text-purple-300">no fee apartments NYC</strong> and save up to $3,000+ in broker fees.
          </p>
          <h5 className="font-medium text-gray-200 text-xs mb-1">Top NYC No Fee Neighborhoods:</h5>
          <ul className="text-gray-300 text-xs space-y-1">
            <li>• <strong className="text-orange-400">Manhattan:</strong> Chelsea, Midtown West, Financial District</li>
            <li>• <strong className="text-orange-400">Brooklyn:</strong> Williamsburg, DUMBO, Park Slope</li>
            <li>• <strong className="text-orange-400">Queens:</strong> Long Island City, Astoria, Forest Hills</li>
          </ul>
        </div>
      )
    },
    {
      id: 'whyChoose',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      tooltip: 'Why NoFeePlaces.com?',
      color: 'green',
      content: (
        <div className="p-4">
          <h4 className="font-semibold text-gray-900 mb-2">Why NoFeePlaces.com?</h4>
          <p className="text-gray-700 text-sm mb-3">
            NYC's #1 platform for <strong>no fee places NYC</strong> rentals.
          </p>
          <h5 className="font-medium text-gray-900 text-xs mb-1">Our Guarantee:</h5>
          <ul className="text-gray-700 text-xs space-y-1">
            <li>• 100% verified no fee rentals NYC listings</li>
            <li>• Direct communication with property owners</li>
            <li>• Expert NYC rental guidance from Office</li>
            <li>• Same-day apartment viewings available</li>
          </ul>
        </div>
      )
    },
    {
      id: 'marketInsights',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      tooltip: 'NYC Rental Market 2025',
      color: 'purple',
      content: (
        <div className="p-4">
          <h4 className="font-semibold text-gray-900 mb-2">NYC Rental Market 2025</h4>
          <p className="text-gray-700 text-sm mb-3">
            The 2025 NYC rental market shows increasing demand for <strong>no broker fee apartments NYC</strong>.
          </p>
          <h5 className="font-medium text-gray-900 text-xs mb-1">Average Rent Ranges (No Fee):</h5>
          <ul className="text-gray-700 text-xs space-y-1">
            <li>• Manhattan: $2,800 - $8,500/month</li>
            <li>• Brooklyn: $2,200 - $5,500/month</li>
            <li>• Queens: $1,900 - $4,200/month</li>
          </ul>
        </div>
      )
    },
    {
      id: 'contact',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4-8 9-8s9 3.582 9 8z" />
        </svg>
      ),
      tooltip: 'Get Expert Help Today',
      color: 'orange',
      content: (
        <div className="p-4">
          <h4 className="font-semibold text-gray-900 mb-2">Get Expert Help Today</h4>
          <p className="text-gray-700 text-sm mb-3">
            Contact our NYC rental office for personalized assistance.
          </p>
          <h5 className="font-medium text-gray-900 text-xs mb-1">Contact Information:</h5>
          <ul className="text-gray-700 text-xs space-y-1">
            <li>• Phone: (646) 408-8048</li>
            <li>• Email: placesfirm@gmail.com</li>
            <li>• Response Time: Under 2 hours</li>
          </ul>
        </div>
      )
    }
  ];

  return (
    <div className="relative" ref={dropdownRef}>
      <div className="flex items-center space-x-2">
        {dropdownItems.map((item) => (
          <div key={item.id} className="relative group">
            <button
              onClick={() => toggleDropdown(item.id)}
              className={`p-2 rounded-lg transition-all duration-200 transform hover:scale-105 ${
                expandedDropdown === item.id
                  ? getActiveClasses(item.color)
                  : getHoverClasses(item.color)
              }`}
            >
              {item.icon}
            </button>
            
            {/* Tooltip */}
            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
              {item.tooltip}
            </div>
          </div>
        ))}
      </div>

      {/* Dropdown Content */}
      {expandedDropdown && (
        <div className="absolute top-full right-0 mt-2 w-80 bg-gray-900 rounded-lg shadow-2xl border border-gray-700 z-50 backdrop-blur-md">
          {dropdownItems.find(item => item.id === expandedDropdown)?.content}
        </div>
      )}
    </div>
  );
};

// Header Component with New PLACES Branding
// Professional Header Component
const Header = ({ isAuthenticated, user, logout, setShowAuthModal }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  return (
    <header className="sticky top-0 bg-black/95 backdrop-blur-md border-b border-gray-800 z-50 shadow-2xl">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            {/* Sleek Custom Logo Design */}
            <div className="relative logo-glow">
        {/* Logo Icon - Modern Building Design */}
              <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-orange-500 rounded-lg flex items-center justify-center shadow-lg transform rotate-3 group-hover:rotate-0 transition-all duration-300 group-hover:scale-105">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
            </div>
            
            {/* Logo Text */}
            <div className="flex flex-col">
              <div className="flex items-center space-x-1">
                <span className="text-xl md:text-2xl font-bold bg-gradient-to-r from-purple-400 to-yellow-400 bg-clip-text text-transparent tracking-tight">No Fee</span>
                <span className="text-base md:text-lg font-semibold text-orange-500 group-hover:text-orange-400 transition-colors">Places</span>
              </div>
              <div className="text-xs text-gray-400 -mt-1 tracking-wide">NYC RENTALS</div>
            </div>
          </Link>

          {/* Center - Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
            <HeaderDropdownIcons />
            <Link 
              to="/blog" 
              className="text-gray-300 hover:text-white font-medium transition-colors hover:bg-purple-900/20 px-3 py-2 rounded-lg"
            >
              Blog
            </Link>
          </div>

          {/* Desktop & Mobile Authentication Buttons */}
          <div className="flex items-center space-x-3">
            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-3 text-gray-300 hover:text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-black rounded-lg px-3 py-2 transition-colors"
                >
                  <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                    {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
                  </div>
                  <span className="hidden md:block font-medium">{user?.full_name || 'User'}</span>
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* User Dropdown Menu */}
                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-gray-900 rounded-lg shadow-2xl py-2 z-50 border border-gray-700">
                    <Link to="/dashboard" className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white transition-colors">Dashboard</Link>
                    <Link to="/favorites" className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white transition-colors">Favorites</Link>
                    <Link to="/saved-searches" className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white transition-colors">Saved Searches</Link>
                    <hr className="my-2 border-gray-700" />
                    <button 
                      onClick={logout}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
                    >
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <>
                {/* Try for Free Button */}
                <button
                  onClick={() => {
                    // Direct Google sign-in for Try for Free
                    window.location.href = `${BACKEND_URL}/api/auth/google/login`;
                  }}
                  className="px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-500 text-white rounded-lg hover:from-green-700 hover:to-emerald-600 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 font-medium flex items-center space-x-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span className="hidden sm:inline">Try for Free</span>
                  <span className="sm:hidden">Free</span>
                </button>
                
                {/* Sign In Button */}
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="px-4 py-2 bg-gradient-to-r from-purple-600 to-yellow-500 text-white rounded-lg hover:from-purple-700 hover:to-yellow-600 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 font-medium"
                >
                  <span className="hidden sm:inline">Sign In / Sign Up</span>
                  <span className="sm:hidden">Sign In</span>
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

// Professional Hero Section with Image Carousel Background
const Hero = () => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [imageError, setImageError] = useState(false);

  // Hero background images - your uploaded images
  const heroImages = [
    'https://i.imgur.com/VpubAMl.jpg', // Cozy apartment workspace image
    'https://i.imgur.com/VBLFllY.jpg'  // NYC skyline window view image
  ];

  // Auto-advance carousel every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prevIndex) => 
        prevIndex === heroImages.length - 1 ? 0 : prevIndex + 1
      );
    }, 5000); // Change image every 5 seconds

    return () => clearInterval(interval);
  }, [heroImages.length]);

  const handleImageError = () => {
    setImageError(true);
    console.log('Image failed to load, using fallback');
  };

  const goToImage = (index) => {
    setCurrentImageIndex(index);
  };

  const goToPrevious = () => {
    setCurrentImageIndex(currentImageIndex === 0 ? heroImages.length - 1 : currentImageIndex - 1);
  };

  const goToNext = () => {
    setCurrentImageIndex(currentImageIndex === heroImages.length - 1 ? 0 : currentImageIndex + 1);
  };

  return (
    <section 
      className="relative py-20 md:py-32 lg:py-40"
      style={{
        width: '100vw',
        marginLeft: 'calc(-50vw + 50%)',
        position: 'relative',
        overflow: 'hidden'
      }}
      role="banner"
      aria-label="NYC no fee apartments hero section"
    >
      {/* Image Carousel Background Container - NO container class here */}
      <div 
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          width: '100vw',
          height: '100%',
          overflow: 'hidden',
          zIndex: 0
        }}
      >
        {/* Background Images */}
        {heroImages.map((image, index) => (
          <div
            key={index}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              backgroundImage: `url('${image}')`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              backgroundRepeat: 'no-repeat',
              opacity: index === currentImageIndex ? 1 : 0,
              transition: 'opacity 1s ease-in-out',
              zIndex: index === currentImageIndex ? 1 : 0
            }}
            onError={handleImageError}
          />
        ))}

        {/* Navigation Arrows */}
        <button
          onClick={goToPrevious}
          className="absolute left-4 top-1/2 transform -translate-y-1/2 z-30 bg-black bg-opacity-50 hover:bg-opacity-75 text-white p-3 rounded-full transition-all duration-300 hover:scale-110"
          aria-label="Previous image"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        <button
          onClick={goToNext}
          className="absolute right-4 top-1/2 transform -translate-y-1/2 z-30 bg-black bg-opacity-50 hover:bg-opacity-75 text-white p-3 rounded-full transition-all duration-300 hover:scale-110"
          aria-label="Next image"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>

        {/* Carousel Indicators */}
        <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 flex space-x-2 z-30">
          {heroImages.map((_, index) => (
            <button
              key={index}
              onClick={() => goToImage(index)}
              className={`w-3 h-3 rounded-full transition-all duration-300 ${
                index === currentImageIndex
                  ? 'bg-white shadow-lg scale-125'
                  : 'bg-white bg-opacity-50 hover:bg-opacity-75'
              }`}
              aria-label={`Go to image ${index + 1}`}
            />
          ))}
        </div>
      </div>

      {/* Dark overlay for text readability */}
      <div 
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          width: '100%',
          height: '100%',
          backgroundColor: 'rgba(0, 0, 0, 0.4)',
          zIndex: 2
        }}
      ></div>

      {/* Text Content Container - container class ONLY here */}
      <div className="container mx-auto px-4 md:px-6 relative z-10">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="hero-title text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-8 drop-shadow-2xl leading-tight">
            No Fee Apartments in NYC
          </h1>
          <p className="text-xl md:text-2xl text-white mb-8 drop-shadow-lg opacity-90 max-w-2xl mx-auto leading-relaxed">
            Discover luxury rentals with zero broker fees. Save thousands on your next NYC apartment.
          </p>
        </div>
      </div>
    </section>
  );
};

// SEO Content Section Component - Removed per user request
const SEOContentSection = () => {
  return null; // This section has been removed to declutter the interface
};

// Professional Search Filters Component
const AdvancedSearchFilters = ({ filters, onFilterChange, apartmentCount }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleFilterChange = (key, value) => {
    onFilterChange(key, value);
  };

  return (
    <div className="bg-gray-900 border-b border-gray-700 sticky top-16 z-40">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between mb-4">
          <div></div> {/* Empty div for spacing */}   
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-purple-400 hover:text-purple-300 font-medium text-sm flex items-center"
          >
            {isExpanded ? 'Hide Filters' : 'Show Filters'}
            <svg 
              className={`w-4 h-4 ml-1 transition-transform ${isExpanded ? 'rotate-180' : ''}`} 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>

        {/* Quick Filters - Always Visible - Sleek & Compact */}
        <div className="flex flex-wrap gap-2 items-center">
          {/* General Search Input */}
          <div className="flex items-center space-x-2">
            <label className="text-xs font-medium text-gray-400">Search:</label>
            <input
              type="text"
              placeholder="Search apartments..."
              value={filters.search_term || ''}
              onChange={(e) => handleFilterChange('search_term', e.target.value)}
              className="bg-gray-800 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-200 placeholder-gray-500 focus:ring-1 focus:ring-purple-500 focus:border-purple-500 outline-none w-40"
            />
          </div>

          <div className="flex items-center space-x-2">
            <label className="text-xs font-medium text-gray-400">Neighborhood:</label>
            <input
              type="text"
              placeholder="Enter neighborhood"
              value={filters.neighborhood || ''}
              onChange={(e) => handleFilterChange('neighborhood', e.target.value)}
              className="bg-gray-800 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-200 placeholder-gray-500 focus:ring-1 focus:ring-purple-500 focus:border-purple-500 outline-none w-32"
            />
          </div>

          <div className="flex items-center space-x-2">
            <label className="text-xs font-medium text-gray-400">Max Price:</label>
            <select
              value={filters.max_price || ''}
              onChange={(e) => handleFilterChange('max_price', e.target.value)}
              className="bg-gray-800 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-200 focus:ring-1 focus:ring-purple-500 focus:border-purple-500 outline-none"
            >
              <option value="">Any Price</option>
              <option value="3000">Up to $3,000</option>
              <option value="4000">Up to $4,000</option>
              <option value="5000">Up to $5,000</option>
              <option value="6000">Up to $6,000</option>
              <option value="8000">Up to $8,000</option>
              <option value="10000">Up to $10,000</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <label className="text-xs font-medium text-gray-400">Bedrooms:</label>
            <select
              value={filters.bedrooms || ''}
              onChange={(e) => handleFilterChange('bedrooms', e.target.value)}
              className="bg-gray-800 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-200 focus:ring-1 focus:ring-purple-500 focus:border-purple-500 outline-none"
            >
              <option value="">Any</option>
              <option value="0">Studio</option>
              <option value="1">1 Bedroom</option>
              <option value="2">2+ Bedrooms</option>
            </select>
          </div>
        </div>

        {/* Expanded Filters - Sleek & Compact */}
        {isExpanded && (
          <div className="mt-3 pt-3 border-t border-gray-700 grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">Borough</label>
              <select
                value={filters.borough || ''}
                onChange={(e) => handleFilterChange('borough', e.target.value)}
                className="w-full bg-gray-800 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-200 focus:ring-1 focus:ring-purple-500 focus:border-purple-500 outline-none"
              >
                <option value="">All Boroughs</option>
                <option value="Manhattan">Manhattan</option>
                <option value="Brooklyn">Brooklyn</option>
                <option value="Queens">Queens</option>
                <option value="Bronx">Bronx</option>
                <option value="Staten Island">Staten Island</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">Bathrooms</label>
              <select
                value={filters.bathrooms || ''}
                onChange={(e) => handleFilterChange('bathrooms', e.target.value)}
                className="w-full bg-gray-800 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-200 focus:ring-1 focus:ring-purple-500 focus:border-purple-500 outline-none"
              >
                <option value="">Any</option>
                <option value="1">1+ Bathroom</option>
                <option value="2">2+ Bathrooms</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">Sort By</label>
              <select
                value={filters.sort_by || ''}
                onChange={(e) => handleFilterChange('sort_by', e.target.value)}
                className="w-full bg-gray-800 border border-gray-600 rounded-md px-2 py-1.5 text-xs text-gray-200 focus:ring-1 focus:ring-purple-500 focus:border-purple-500 outline-none"
              >
                <option value="">Default</option>
                <option value="price_asc">Price: Low to High</option>
                <option value="price_desc">Price: High to Low</option>
                <option value="bedrooms_asc">Bedrooms: Low to High</option>
                <option value="bedrooms_desc">Bedrooms: High to Low</option>
              </select>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Enhanced Error Handling Component
const ErrorBoundary = ({ children, fallback }) => {
  const [hasError, setHasError] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const handleError = (error) => {
      setHasError(true);
      setError(error);
      console.error('ErrorBoundary caught an error:', error);
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', (event) => {
      handleError(event.reason);
    });

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleError);
    };
  }, []);

  if (hasError) {
    if (fallback) {
      return fallback(error, () => {
        setHasError(false);
        setError(null);
      });
    }
    
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full text-center">
          <div className="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-slate-800 mb-2">Something went wrong</h2>
          <p className="text-slate-600 mb-4">We're sorry, but an unexpected error occurred. Please try refreshing the page.</p>
          <button 
            onClick={() => window.location.reload()}
            className="btn-primary px-6 py-3"
          >
            Refresh Page
          </button>
        </div>
      </div>
    );
  }

  return children;
};

// Toast Notification Component
const Toast = ({ message, type = 'info', isVisible, onClose }) => {
  useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(() => {
        onClose();
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [isVisible, onClose]);

  if (!isVisible) return null;

  const icons = {
    success: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
      </svg>
    ),
    error: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
      </svg>
    ),
    warning: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    info: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  };

  const colors = {
    success: 'bg-green-500 text-white',
    error: 'bg-red-500 text-white',
    warning: 'bg-yellow-500 text-black',
    info: 'bg-blue-500 text-white'
  };

  return (
    <div className={`fixed top-4 right-4 z-50 flex items-center px-4 py-3 rounded-lg shadow-luxury animate-slide-up ${colors[type]}`}>
      <div className="mr-3">
        {icons[type]}
      </div>
      <p className="font-medium">{message}</p>
      <button 
        onClick={onClose}
        className="ml-4 hover:opacity-70 transition-opacity"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
};

// Toast Context for global toast management
const ToastContext = React.createContext();

export const useToast = () => {
  const context = React.useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = (message, type = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const value = {
    addToast,
    success: (message) => addToast(message, 'success'),
    error: (message) => addToast(message, 'error'),
    warning: (message) => addToast(message, 'warning'),
    info: (message) => addToast(message, 'info')
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      {toasts.map(toast => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          isVisible={true}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </ToastContext.Provider>
  );
};

// Lazy Loading Image Component with Optimization
const LazyImage = ({ src, alt, className, ...props }) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const [error, setError] = useState(false);
  const imgRef = useRef();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      {
        threshold: 0.1,
        rootMargin: '50px'
      }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, []);

  const handleLoad = () => {
    setIsLoaded(true);
    setError(false);
  };

  const handleError = () => {
    setError(true);
    setIsLoaded(false);
  };

  return (
    <div ref={imgRef} className={`relative ${className || ''}`} {...props}>
      {/* Loading placeholder */}
      {(!isLoaded || !isInView) && !error && (
        <div className="absolute inset-0 bg-gradient-to-br from-slate-200 to-slate-300 animate-pulse flex items-center justify-center">
          <svg className="w-12 h-12 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2-2z" />
          </svg>
        </div>
      )}
      
      {/* Error placeholder */}
      {error && (
        <div className="absolute inset-0 bg-gradient-to-br from-slate-300 to-slate-400 flex items-center justify-center">
          <svg className="w-12 h-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      )}

      {/* Actual image */}
      {isInView && (
        <img
          src={src}
          alt={alt}
          onLoad={handleLoad}
          onError={handleError}
          className={`transition-opacity duration-500 ${
            isLoaded ? 'opacity-100' : 'opacity-0'
          } ${className || ''}`}
          loading="lazy"
          {...props}
        />
      )}
    </div>
  );
};

// Email Contact Modal Component
const EmailContactModal = ({ isOpen, onClose, apartment }) => {
  const [emailData, setEmailData] = useState({
    name: '',
    email: '',
    phone: '',
    message: `Hi, I'm interested in learning more about ${apartment?.title || 'this apartment'}.`
  });
  const [sending, setSending] = useState(false);
  const [success, setSuccess] = useState(false);

  // Handle click outside to close modal
  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  // Handle escape key to close modal
  useEffect(() => {
    const handleEscapeKey = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscapeKey);
      return () => document.removeEventListener('keydown', handleEscapeKey);
    }
  }, [isOpen, onClose]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSending(true);

    try {
      const response = await axios.post(`${API}/contact/apartment`, {
        apartment_id: apartment.id,
        apartment_title: apartment.title,
        apartment_address: apartment.address,
        apartment_price: apartment.price,
        ...emailData
      });

      if (response.status === 200) {
        setSuccess(true);
        setTimeout(() => {
          setSuccess(false);
          onClose();
          setEmailData({
            name: '',
            email: '',
            phone: '',
            message: `Hi, I'm interested in learning more about ${apartment?.title || 'this apartment'}.`
          });
        }, 2000);
      }
    } catch (error) {
      console.error('Failed to send email:', error);
      alert('Failed to send message. Please try again.');
    } finally {
      setSending(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={handleOverlayClick}
    >
      <div 
        className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-lg transform transition-all duration-200 scale-100"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Contact Agent</h3>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {success ? (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h4 className="text-lg font-semibold text-gray-900 mb-2">Message Sent!</h4>
            <p className="text-gray-600">Our licensed agent will get back to you within 24 hours.</p>
          </div>
        ) : (
          <>
            <div className="mb-4 p-3 bg-gray-50 rounded-lg">
              <h4 className="font-semibold text-gray-900">{apartment?.title}</h4>
              <p className="text-sm text-gray-600">{apartment?.address}</p>
              <p className="text-sm font-semibold text-gray-900">${apartment?.price?.toLocaleString()}/month</p>
            </div>

            {/* Contact Information Display Only */}
            <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <h5 className="font-medium text-blue-900 mb-2">You can also reach us at:</h5>
              <div className="flex flex-col space-y-2 text-sm">
                <div className="flex items-center">
                  <svg className="w-4 h-4 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  <span className="text-blue-800 font-medium">(646) 408-8048</span>
                </div>
                <div className="flex items-center">
                  <svg className="w-4 h-4 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 7.89a2 2 0 002.83 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <span className="text-blue-800 font-medium">placesfirm@gmail.com</span>
                </div>
              </div>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Your Name</label>
                  <input
                    type="text"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
                    value={emailData.name}
                    onChange={(e) => setEmailData(prev => ({...prev, name: e.target.value}))}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                  <input
                    type="email"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
                    value={emailData.email}
                    onChange={(e) => setEmailData(prev => ({...prev, email: e.target.value}))}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                  <input
                    type="tel"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
                    value={emailData.phone}
                    onChange={(e) => setEmailData(prev => ({...prev, phone: e.target.value}))}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
                  <textarea
                    rows={4}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
                    value={emailData.message}
                    onChange={(e) => setEmailData(prev => ({...prev, message: e.target.value}))}
                  />
                </div>
              </div>

              <div className="mt-6 flex space-x-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={sending}
                  className="flex-1 bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 disabled:bg-orange-400 transition-colors"
                >
                  {sending ? 'Sending...' : 'Send Message'}
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
};

// Enhanced Apartment Card Component with luxury styling
// Image Carousel Component for Apartment Cards
const ImageCarousel = ({ images = [], alt = '', className = '' }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  
  if (!images || images.length === 0) {
    return (
      <LazyImage
        src="https://images.unsplash.com/photo-1555636222-cae831e670b3"
        alt={alt}
        className={className}
      />
    );
  }

  const nextImage = (e) => {
    e.stopPropagation();
    setCurrentIndex((prev) => (prev + 1) % images.length);
  };

  const prevImage = (e) => {
    e.stopPropagation();
    setCurrentIndex((prev) => (prev - 1 + images.length) % images.length);
  };

  const goToImage = (index, e) => {
    e.stopPropagation();
    setCurrentIndex(index);
  };

  return (
    <div className="relative group">
      <LazyImage
        src={images[currentIndex]}
        alt={alt}
        className={className}
      />
      
      {/* Navigation arrows - show on hover */}
      {images.length > 1 && (
        <>
          <button
            onClick={prevImage}
            className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-60 hover:bg-opacity-80 text-white rounded-full p-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 shadow-lg"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button
            onClick={nextImage}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-60 hover:bg-opacity-80 text-white rounded-full p-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 shadow-lg"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </>
      )}
      
      {/* Image dots indicator */}
      {images.length > 1 && (
        <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 flex space-x-1">
          {images.map((_, index) => (
            <button
              key={index}
              onClick={(e) => goToImage(index, e)}
              className={`w-2 h-2 rounded-full transition-all duration-200 ${
                index === currentIndex 
                  ? 'bg-white' 
                  : 'bg-white bg-opacity-50 hover:bg-opacity-75'
              }`}
            />
          ))}
        </div>
      )}
      
      {/* Image counter */}
      {images.length > 1 && (
        <div className="absolute top-3 left-3 bg-black bg-opacity-60 text-white text-xs px-2 py-1 rounded">
          {currentIndex + 1} / {images.length}
        </div>
      )}
    </div>
  );
};

const ApartmentCard = ({ apartment, setShowAuthModal }) => {
  const [isFavorited, setIsFavorited] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();

  // SEO Enhancement: Generate structured data for each apartment
  const generateStructuredData = (apartment) => {
    return {
      "@context": "https://schema.org",
      "@type": "RentAction",
      "object": {
        "@type": "Apartment",
        "name": apartment.title,
        "address": {
          "@type": "PostalAddress",
          "streetAddress": apartment.address,
          "addressLocality": apartment.neighborhood,
          "addressRegion": apartment.borough,
          "addressCountry": "US"
        },
        "numberOfRooms": apartment.bedrooms,
        "floorSize": {
          "@type": "QuantitativeValue",
          "value": apartment.sqft,
          "unitText": "SQF"
        },
        "amenityFeature": apartment.amenities?.map(amenity => ({
          "@type": "LocationFeatureSpecification",
          "name": amenity
        })) || []
      },
      "price": {
        "@type": "MonetaryAmount",
        "value": apartment.price,
        "currency": "USD"
      },
      "priceSpecification": {
        "@type": "RentPrice",
        "price": apartment.price,
        "priceCurrency": "USD",
        "unitCode": "MON"
      }
    };
  };

  // Check if apartment is in user's favorites on mount
  useEffect(() => {
    const checkFavoriteStatus = async () => {
      if (isAuthenticated && user) {
        try {
          const response = await axios.get(`${API}/users/favorites`);
          const userFavorites = response.data;
          setIsFavorited(userFavorites.some(fav => fav.id === apartment.id));
        } catch (error) {
          console.error('Failed to check favorite status:', error);
        }
      }
    };

    checkFavoriteStatus();
  }, [apartment.id, isAuthenticated, user]);

  const handleFavorite = async (e) => {
    e.stopPropagation();
    if (!isAuthenticated) {
      alert('Please sign in to save favorites');
      return;
    }

    try {
      if (isFavorited) {
        await axios.delete(`${API}/users/favorites/${apartment.id}`);
        setIsFavorited(false);
      } else {
        await axios.post(`${API}/users/favorites/${apartment.id}`);
        setIsFavorited(true);
      }
    } catch (error) {
      console.error('Failed to update favorite:', error);
      alert('Failed to update favorite. Please try again.');
    }
  };

  const handleViewDetails = () => {
    navigate(`/apartment/${apartment.id}`);
  };

  return (
    <div className="bg-gray-900 rounded-lg shadow-xl hover:shadow-2xl transition-all duration-300 overflow-hidden border border-gray-700 hover:border-purple-500/50 transform hover:-translate-y-1">
      <div className="relative cursor-pointer" onClick={handleViewDetails}>
        <ImageCarousel
          images={apartment.images || [apartment.image]}
          alt={apartment.title}
          className="w-full h-48 object-cover hover:opacity-95 transition-opacity duration-200"
        />
        
        {/* No Fee Badge */}
        <div className="absolute top-3 right-3 z-10">
          <span className="bg-orange-500 text-white text-xs font-bold px-2 py-1 rounded shadow-lg">
            NO FEE
          </span>
        </div>
        
        {/* Favorite Button */}
        <div className="absolute top-3 right-16 z-10">
          <button 
            onClick={handleFavorite}
            className="bg-black/70 backdrop-blur-sm hover:bg-black/80 p-2 rounded-full shadow-lg transition-all"
          >
            <svg 
              className={`w-5 h-5 ${
                isFavorited ? 'text-red-500 fill-current' : 'text-gray-400 hover:text-red-500'
              }`} 
              fill={isFavorited ? 'currentColor' : 'none'} 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </button>
        </div>

        {/* Price */}
        <div className="absolute bottom-3 right-3">
          <div className="bg-black/80 backdrop-blur-sm px-3 py-1 rounded shadow-lg border border-gray-600">
            <span className="text-lg font-bold text-orange-500">
              ${apartment.price?.toLocaleString() || apartment.price}
            </span>
            <span className="text-gray-300 text-sm">/mo</span>
          </div>
        </div>
      </div>

      <div className="p-4">
        <h3 className="text-lg font-semibold text-white mb-2 line-clamp-2">{apartment.title}</h3>
        <p className="text-gray-300 text-sm mb-3 flex items-center">
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {/* Always show full address */}
            {apartment.address}
          </span>
        </p>

        {/* Property Details */}
        <div className="flex items-center justify-between text-sm text-gray-300 mb-4">
          <span className="font-medium">
            {apartment.bedrooms === 0 ? 'Studio' : `${apartment.bedrooms} bed`}
          </span>
          <span className="font-medium">{apartment.bathrooms} bath</span>
          <span className="font-medium">{apartment.sqft} sq ft</span>
        </div>

        {/* Status */}
        <div className="flex items-center mb-4">
          <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
          <span className="text-sm font-medium text-green-700">Available Now</span>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row justify-between items-stretch sm:items-center pt-3 border-t border-gray-200 gap-3 sm:gap-0">
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => window.open(`tel:646-408-8048`, '_self')}
              className="flex items-center justify-center bg-gray-700 text-gray-300 px-3 py-2 rounded transition-all duration-300 hover:bg-gray-600 hover:text-white hover:shadow-lg hover:shadow-blue-500/30 hover:scale-105 text-sm font-medium border border-gray-600 hover:border-gray-500 group"
            >
              <svg className="w-4 h-4 mr-1 transition-all duration-300 group-hover:scale-110 group-hover:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              <span className="transition-all duration-300 group-hover:text-blue-400">Call</span>
            </button>
            <button
              onClick={() => setShowEmailModal(true)}
              className="flex items-center justify-center bg-gray-700 text-gray-300 px-3 py-2 rounded transition-all duration-300 hover:bg-gray-600 hover:text-white hover:shadow-lg hover:shadow-green-500/30 hover:scale-105 text-sm font-medium border border-gray-600 hover:border-gray-500 group"
            >
              <svg className="w-4 h-4 mr-1 transition-all duration-300 group-hover:scale-110 group-hover:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 7.89a2 2 0 002.83 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <span className="transition-all duration-300 group-hover:text-green-400">Email</span>
            </button>
          </div>
        </div>
      </div>

      {/* Email Contact Modal */}
      <EmailContactModal 
        isOpen={showEmailModal}
        onClose={() => setShowEmailModal(false)}
        apartment={apartment}
      />
    </div>
  );
};

// Compact Calendar Booking Component
const CalendarBooking = ({ apartmentId, onBookingComplete }) => {
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedTime, setSelectedTime] = useState('');
  const [availableSlots, setAvailableSlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showBookingForm, setShowBookingForm] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [bookingData, setBookingData] = useState({
    visitor_name: '',
    visitor_email: '',
    visitor_phone: '',
    notes: ''
  });
  const toast = useToast && useToast();

  // Compact calendar date generation with error handling
  const getDaysInMonth = (date) => {
    try {
      if (!date || !(date instanceof Date)) {
        date = new Date(); // Fallback to current date
      }
      
      const year = date.getFullYear();
      const month = date.getMonth();
      const firstDay = new Date(year, month, 1);
      const lastDay = new Date(year, month + 1, 0);
      const startDate = new Date(firstDay);
      startDate.setDate(startDate.getDate() - firstDay.getDay()); // Start from Sunday
      
      const days = [];
      const currentDate = new Date(startDate);
      
      // Generate 35 days (5 weeks) for more compact calendar grid
      for (let i = 0; i < 35; i++) {
        const day = new Date(currentDate);
        const isCurrentMonth = day.getMonth() === month;
        const isToday = day.toDateString() === new Date().toDateString();
        const isPast = day < new Date().setHours(0, 0, 0, 0);
        const isSelected = selectedDate && selectedDate instanceof Date && day.toDateString() === selectedDate.toDateString();
        
        days.push({
          date: day,
          dayNumber: day.getDate(), // This should always be a number
          isCurrentMonth,
          isToday,
          isPast,
          isSelected,
          dateString: day.toISOString().split('T')[0]
        });
        
        currentDate.setDate(currentDate.getDate() + 1);
      }
      
      return days;
    } catch (error) {
      console.error('Error generating calendar days:', error);
      return []; // Return empty array on error
    }
  };

  const monthNames = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
  ];

  const weekDays = ["S", "M", "T", "W", "T", "F", "S"];

  // Navigate months
  const previousMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1));
  };

  // Fetch available time slots when date changes
  useEffect(() => {
    if (selectedDate) {
      fetchAvailableSlots();
    }
  }, [selectedDate]);

  const fetchAvailableSlots = async () => {
    if (!selectedDate || !(selectedDate instanceof Date)) {
      console.error('Invalid selectedDate for fetching slots');
      return;
    }
    
    setLoading(true);
    try {
      const dateString = selectedDate.toISOString().split('T')[0];
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/apartments/${apartmentId}/available-slots?date=${dateString}`);
      setAvailableSlots(response.data.available_slots || []);
    } catch (error) {
      console.error('Error fetching available slots:', error);
      // Mock available slots for demo
      setAvailableSlots(['10:00 AM', '2:00 PM', '4:00 PM', '6:00 PM']);
    } finally {
      setLoading(false);
    }
  };

  const handleDateSelect = (day) => {
    if (day.isPast || !day.isCurrentMonth) return;
    setSelectedDate(day.date);
    setSelectedTime(''); // Reset time selection
  };

  const handleTimeSelect = (time) => {
    setSelectedTime(time);
    setShowBookingForm(true);
  };

  const handleBookingSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const API = (process.env.REACT_APP_BACKEND_URL || '') + '/api';
      
      const appointmentData = {
        apartment_id: apartmentId,
        date: selectedDate.toISOString().split('T')[0],
        time: selectedTime,
        visitor_name: bookingData.visitor_name,
        visitor_email: bookingData.visitor_email,
        visitor_phone: bookingData.visitor_phone,
        notes: bookingData.notes,
        status: 'scheduled'
      };

      const response = await axios.post(`${API}/appointments`, appointmentData);
      
      // Reset form and close modal
      setBookingData({
        visitor_name: '',
        visitor_email: '',
        visitor_phone: '',
        notes: ''
      });
      setShowBookingForm(false);
      setSelectedDate(null);
      setSelectedTime('');

      // Show success message
      toast && toast.success('Appointment booked successfully!');
      
      if (onBookingComplete) {
        onBookingComplete(response.data);
      }
    } catch (error) {
      console.error('Booking error:', error);
      toast && toast.error(error.response?.data?.detail || 'Failed to book appointment');
    } finally {
      setLoading(false);
    }
  };

  const days = getDaysInMonth(currentMonth) || []; // Ensure we always have an array

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 border border-gray-700">
      <h3 className="text-lg font-semibold text-gray-200 mb-4 flex items-center">
        <div className="w-6 h-6 bg-purple-600/20 rounded-lg flex items-center justify-center mr-2">
          <svg className="w-3 h-3 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        Schedule Viewing
      </h3>

      {/* Compact Calendar Header */}
      <div className="flex items-center justify-between mb-3">
        <button
          onClick={previousMonth}
          className="p-1.5 hover:bg-gray-700 rounded-lg transition-colors"
        >
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        
        <h4 className="text-sm font-medium text-gray-300">
          {currentMonth && currentMonth instanceof Date 
            ? `${monthNames[currentMonth.getMonth()] || 'Unknown'} ${currentMonth.getFullYear() || 'Unknown'}`
            : 'Calendar'
          }
        </h4>
        
        <button
          onClick={nextMonth}
          className="p-1.5 hover:bg-gray-700 rounded-lg transition-colors"
        >
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      {/* Compact Week Day Headers */}
      <div className="grid grid-cols-7 gap-1 mb-2">
        {weekDays.map(day => (
          <div key={day} className="text-center py-1 text-xs font-medium text-gray-500">
            {day}
          </div>
        ))}
      </div>

      {/* Compact Calendar Grid */}
      <div className="grid grid-cols-7 gap-1 mb-4">
        {days && days.length > 0 ? days.map((day, index) => (
          <button
            key={index}
            onClick={() => handleDateSelect(day)}
            disabled={day.isPast || !day.isCurrentMonth}
            className={`
              h-8 w-full text-xs rounded-md transition-all duration-200
              ${day.isCurrentMonth 
                ? day.isPast
                  ? 'text-gray-600 cursor-not-allowed'
                  : day.isSelected
                    ? 'bg-purple-600 text-white shadow-lg'
                    : day.isToday
                      ? 'bg-purple-600/20 text-purple-400 font-bold hover:bg-purple-600/30'
                      : 'text-gray-400 hover:bg-gray-700 hover:text-gray-200'
                : 'text-gray-600'
              }
            `}
          >
            {day.dayNumber || ''}
          </button>
        )) : (
          <div className="col-span-7 text-center text-gray-500 py-4">
            Loading calendar...
          </div>
        )}
      </div>

      {/* Selected Date Display - Compact */}
      {selectedDate && selectedDate instanceof Date && (
        <div className="mb-3 p-2 bg-purple-600/10 rounded-lg border border-purple-600/20">
          <p className="text-purple-400 text-xs text-center font-medium">
            {selectedDate.toLocaleDateString('en-US', { 
              weekday: 'short', 
              month: 'short', 
              day: 'numeric' 
            })}
          </p>
        </div>
      )}

      {/* Compact Time Selection */}
      {selectedDate && selectedDate instanceof Date && (
        <div className="mb-4">
          <label className="block text-xs font-medium text-gray-400 mb-2">Available Times</label>
          {loading ? (
            <div className="flex items-center justify-center py-4">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-purple-600"></div>
              <span className="ml-2 text-gray-400 text-xs">Loading...</span>
            </div>
          ) : availableSlots.length > 0 ? (
            <div className="grid grid-cols-2 gap-2">
              {availableSlots.map(slot => (
                <button
                  key={slot}
                  onClick={() => handleTimeSelect(slot)}
                  className={`
                    py-2 px-3 rounded-lg text-xs font-medium transition-all duration-200
                    ${selectedTime === slot
                      ? 'bg-purple-600 text-white shadow-lg'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600 hover:text-white'
                    }
                  `}
                >
                  {slot}
                </button>
              ))}
            </div>
          ) : (
            <div className="text-center py-4 text-gray-500">
              <div className="text-xs">No slots available</div>
            </div>
          )}
        </div>
      )}

      {/* Compact Booking Form */}
      {showBookingForm && (
        <div className="border-t border-gray-700 pt-4">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Contact Details</h4>
          <form onSubmit={handleBookingSubmit} className="space-y-3">
            <div>
              <input
                type="text"
                required
                value={bookingData.visitor_name}
                onChange={(e) => setBookingData({...bookingData, visitor_name: e.target.value})}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-gray-200 placeholder-gray-500 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors text-sm"
                placeholder="Your full name"
              />
            </div>
            <div className="grid grid-cols-1 gap-3">
              <input
                type="email"
                required
                value={bookingData.visitor_email}
                onChange={(e) => setBookingData({...bookingData, visitor_email: e.target.value})}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-gray-200 placeholder-gray-500 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors text-sm"
                placeholder="Your email"
              />
            </div>
            <div>
              <input
                type="tel"
                required
                value={bookingData.visitor_phone}
                onChange={(e) => setBookingData({...bookingData, visitor_phone: e.target.value})}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-gray-200 placeholder-gray-500 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors text-sm"
                placeholder="Your phone"
              />
            </div>
            <div>
              <textarea
                value={bookingData.notes}
                onChange={(e) => setBookingData({...bookingData, notes: e.target.value})}
                rows={2}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-gray-200 placeholder-gray-500 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors resize-none text-sm"
                placeholder="Any notes (optional)"
              />
            </div>
            <div className="flex gap-2 pt-2">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-purple-700 focus:ring-2 focus:ring-purple-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Booking...
                  </span>
                ) : 'Book Tour'}
              </button>
              <button
                type="button"
                onClick={() => setShowBookingForm(false)}
                className="px-4 py-2 border border-gray-600 text-gray-400 rounded-lg font-medium hover:bg-gray-700 transition-colors text-sm"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

// Admin Dashboard for Managing Appointments
const AdminAppointments = () => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({
    status: '',
    date_from: '',
    date_to: '',
    apartment_id: ''
  });
  const [apartments, setApartments] = useState([]);

  useEffect(() => {
    fetchAppointments();
    fetchApartments();
  }, [filter]);

  const fetchAppointments = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      Object.entries(filter).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      params.append('limit', '100');

      const response = await axios.get(`${API}/appointments?${params.toString()}`);
      setAppointments(response.data);
    } catch (error) {
      console.error('Error fetching appointments:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchApartments = async () => {
    try {
      const response = await axios.get(`${API}/apartments?limit=200`);
      setApartments(response.data.apartments || response.data);
    } catch (error) {
      console.error('Error fetching apartments:', error);
    }
  };

  const updateAppointmentStatus = async (appointmentId, status) => {
    try {
      await axios.put(`${API}/appointments/${appointmentId}`, { status });
      fetchAppointments(); // Refresh the list
      alert(`Appointment ${status} successfully`);
    } catch (error) {
      alert('Error updating appointment status');
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      confirmed: 'bg-green-100 text-green-800',
      completed: 'bg-blue-100 text-blue-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    
    return `px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-800'}`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getApartmentTitle = (apartmentId) => {
    const apartment = apartments.find(apt => apt.id === apartmentId);
    return apartment ? apartment.title : 'Unknown Apartment';
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-800 mb-2">Appointment Management</h1>
          <p className="text-slate-600">View and manage all apartment viewing appointments.</p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6 border border-slate-200">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Status</label>
              <select
                value={filter.status}
                onChange={(e) => setFilter(prev => ({...prev, status: e.target.value}))}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="confirmed">Confirmed</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">From Date</label>
              <input
                type="date"
                value={filter.date_from}
                onChange={(e) => setFilter(prev => ({...prev, date_from: e.target.value}))}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">To Date</label>
              <input
                type="date"
                value={filter.date_to}
                onChange={(e) => setFilter(prev => ({...prev, date_to: e.target.value}))}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Apartment</label>
              <select
                value={filter.apartment_id}
                onChange={(e) => setFilter(prev => ({...prev, apartment_id: e.target.value}))}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500"
              >
                <option value="">All Apartments</option>
                {apartments.map(apt => (
                  <option key={apt.id} value={apt.id}>
                    {apt.title.substring(0, 50)}...
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="mt-4 flex gap-2">
            <button
              onClick={() => setFilter({status: '', date_from: '', date_to: '', apartment_id: ''})}
              className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50"
            >
              Clear Filters
            </button>
          </div>
        </div>

        {/* Appointments List */}
        <div className="bg-white rounded-lg shadow-md border border-slate-200">
          <div className="p-6 border-b border-slate-200">
            <h2 className="text-lg font-semibold text-slate-800">
              Appointments ({appointments.length})
            </h2>
          </div>
          
          {appointments.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Visitor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Apartment
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Date & Time
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Contact
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-200">
                  {appointments.map((appointment) => (
                    <tr key={appointment.id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-slate-900">
                            {appointment.visitor_name}
                          </div>
                          {appointment.notes && (
                            <div className="text-sm text-slate-500">
                              "{appointment.notes}"
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-slate-900 max-w-xs">
                          {getApartmentTitle(appointment.apartment_id)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-slate-900">
                          {formatDate(appointment.appointment_date)}
                        </div>
                        <div className="text-sm text-slate-500">
                          {appointment.appointment_time}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-slate-900">
                          {appointment.visitor_email}
                        </div>
                        <div className="text-sm text-slate-500">
                          {appointment.visitor_phone}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={getStatusBadge(appointment.status)}>
                          {appointment.status.charAt(0).toUpperCase() + appointment.status.slice(1)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {appointment.status === 'pending' && (
                          <div className="flex gap-2">
                            <button
                              onClick={() => updateAppointmentStatus(appointment.id, 'confirmed')}
                              className="bg-green-600 text-white px-3 py-1 rounded text-xs hover:bg-green-700"
                            >
                              Confirm
                            </button>
                            <button
                              onClick={() => updateAppointmentStatus(appointment.id, 'cancelled')}
                              className="bg-red-600 text-white px-3 py-1 rounded text-xs hover:bg-red-700"
                            >
                              Cancel
                            </button>
                          </div>
                        )}
                        {appointment.status === 'confirmed' && (
                          <button
                            onClick={() => updateAppointmentStatus(appointment.id, 'completed')}
                            className="bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700"
                          >
                            Mark Complete
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-12 text-center">
              <svg className="w-16 h-16 mx-auto text-slate-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <h3 className="text-lg font-semibold text-slate-800 mb-2">No appointments found</h3>
              <p className="text-slate-600">No appointments match your current filters.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Enhanced Authentication Modal with Social Login Options
const AuthModal = ({ onClose }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    fullName: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login, register } = useAuth();

  // Initialize social login systems
  useEffect(() => {
    // Check what authentication providers are available
    const checkAuthProviders = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/providers/status`);
        if (response.ok) {
          const providers = await response.json();
          console.log('Available auth providers:', providers);
          
          // Initialize Google (Emergent Auth) - no client-side setup needed
          if (providers.google) {
            console.log('Google authentication available via Emergent Auth');
          }
          
          // Initialize Facebook SDK if enabled
          if (providers.facebook && typeof window !== 'undefined' && !window.fbAsyncInit) {
            window.fbAsyncInit = function() {
              window.FB.init({
                appId: 'your-facebook-app-id', // Will be configured when credentials are provided
                cookie: true,
                xfbml: true,
                version: 'v18.0'
              });
            };
          }
          
          // Initialize Apple Sign In if enabled
          if (providers.apple && typeof window !== 'undefined' && window.AppleID) {
            try {
              window.AppleID.auth.init({
                clientId: 'your-apple-service-id', // Will be configured when credentials are provided
                scope: 'name email',
                redirectURI: window.location.origin + '/auth/apple/callback',
                usePopup: false // Use redirect flow for production
              });
            } catch (error) {
              console.log('Apple Sign In initialization failed:', error);
            }
          }
        }
      } catch (error) {
        console.error('Failed to check auth providers:', error);
      }
    };
    
    checkAuthProviders();
  }, []);

  // Handle Emergent Google Authentication
  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Redirect to Emergent Auth for Google
      window.location.href = `${process.env.REACT_APP_BACKEND_URL}/api/auth/google/login`;
      
    } catch (error) {
      console.error('Google login error:', error);
      setError('Google sign-in failed. Please try again.');
      setLoading(false);
    }
  };

  // Handle session ID from URL (for Emergent Auth callback)
  useEffect(() => {
    const handleEmergentCallback = async () => {
      const urlParams = new URLSearchParams(window.location.hash.substring(1));
      const sessionId = urlParams.get('session_id');
      
      if (sessionId) {
        try {
          setLoading(true);
          
          // Clear the session_id from URL
          window.history.replaceState({}, document.title, window.location.pathname);
          
          // Authenticate with our backend using the session ID
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/google/callback`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ session_id: sessionId, provider: 'google' })
          });
          
          if (response.ok) {
            const authData = await response.json();
            
            // Store tokens
            localStorage.setItem('access_token', authData.access_token);
            localStorage.setItem('refresh_token', authData.refresh_token);
            
            // Update auth context
            if (login) {
              await login(authData.user.email, 'social-auth-token');
            }
            
            setError('Google sign-in successful! Welcome to NoFeePlaces!');
            setTimeout(() => onClose(), 1500);
            
          } else {
            const errorData = await response.json();
            setError(`Authentication failed: ${errorData.detail || 'Unknown error'}`);
          }
        } catch (error) {
          console.error('Emergent auth callback error:', error);
          setError('Authentication failed. Please try again.');
        } finally {
          setLoading(false);
        }
      }
    };
    
    handleEmergentCallback();
  }, []);

  // Handle Facebook OAuth response
  const handleFacebookLogin = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Redirect to Facebook OAuth
      window.location.href = `${process.env.REACT_APP_BACKEND_URL}/api/auth/facebook/login`;
      
    } catch (error) {
      console.error('Facebook login error:', error);
      setError('Facebook sign-in failed. Please try again.');
      setLoading(false);
    }
  };

  // Handle Apple Sign In
  const handleAppleLogin = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Redirect to Apple OAuth
      window.location.href = `${process.env.REACT_APP_BACKEND_URL}/api/auth/apple/login`;
      
    } catch (error) {
      console.error('Apple login error:', error);
      setError('Apple sign-in failed. Please try again.');
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      let result;
      if (isLogin) {
        result = await login(formData.email, formData.password);
      } else {
        result = await register(formData.email, formData.password, formData.fullName);
      }

      if (result.success) {
        onClose();
      } else {
        setError(result.error);
      }
    } catch (error) {
      setError('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-lg p-8 max-w-md w-full mx-4 shadow-2xl border border-gray-700">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-orange-400 bg-clip-text text-transparent">
            {isLogin ? 'Sign In to Places' : 'Join Places'}
          </h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-gray-300"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Social Login Options */}
        <div className="mb-6">
          <div className="grid grid-cols-1 gap-3">
            <button
              onClick={handleGoogleLogin}
              className="w-full flex items-center justify-center px-4 py-3 border border-gray-600 rounded-lg hover:bg-gray-800 transition-colors text-white"
            >
              <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Continue with Google
            </button>

            <button
              onClick={handleFacebookLogin}
              className="w-full flex items-center justify-center px-4 py-3 border border-gray-600 rounded-lg hover:bg-gray-800 transition-colors text-white"
            >
              <svg className="w-5 h-5 mr-3" fill="#1877F2" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              Continue with Facebook
            </button>

            <button
              onClick={handleAppleLogin}
              className="w-full flex items-center justify-center px-4 py-3 border border-gray-600 rounded-lg hover:bg-gray-800 transition-colors text-white"
            >
              <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
              </svg>
              Continue with Apple
            </button>
          </div>

          <div className="flex items-center my-6">
            <div className="flex-1 border-t border-gray-600"></div>
            <span className="px-4 text-gray-400 text-sm">or continue with email</span>
            <div className="flex-1 border-t border-gray-600"></div>
          </div>
        </div>

        {error && (
          <div className="bg-red-900/20 border border-red-500/50 text-red-300 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-300 mb-2">Full Name</label>
              <input
                type="text"
                required
                className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none text-white"
                value={formData.fullName}
                onChange={(e) => setFormData(prev => ({...prev, fullName: e.target.value}))}
              />
            </div>
          )}

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
            <input
              type="email"
              required
              placeholder="your.email@example.com"
              className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none text-white placeholder-gray-400"
              value={formData.email}
              onChange={(e) => setFormData(prev => ({...prev, email: e.target.value}))}
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
            <input
              type="password"
              required
              placeholder="Enter your password"
              className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none text-white placeholder-gray-400"
              value={formData.password}
              onChange={(e) => setFormData(prev => ({...prev, password: e.target.value}))}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-purple-600 to-orange-500 text-white py-3 px-4 rounded-lg hover:from-purple-700 hover:to-orange-600 disabled:opacity-50 transition-all font-medium shadow-lg"
          >
            {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        <div className="text-center mt-6">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-orange-400 hover:text-orange-300 text-sm font-medium"
          >
            {isLogin ? "Don't have an account? Join Places" : "Already have an account? Sign in"}
          </button>
        </div>

        <div className="text-center mt-4">
          <p className="text-xs text-gray-400">
            By continuing, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </div>
    </div>
  );
};

// User Dashboard Component
const UserDashboard = ({ user }) => {
  const [favorites, setFavorites] = useState([]);
  const [savedSearches, setSavedSearches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const [favoritesRes, searchesRes] = await Promise.all([
        axios.get(`${API}/users/favorites`),
        axios.get(`${API}/users/saved-searches`)
      ]);
      
      setFavorites(favoritesRes.data);
      setSavedSearches(searchesRes.data);
    } catch (error) {
      console.error('Failed to fetch user data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-800 mb-2">Welcome to PLACES, {user.full_name}!</h1>
          <p className="text-slate-600">Manage your saved apartments and search preferences.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Favorites Section */}
          <div className="bg-white rounded-lg shadow-md p-6 border border-slate-200">
            <h2 className="text-xl font-bold text-slate-800 mb-4">Favorite Apartments ({favorites.length})</h2>
            {favorites.length > 0 ? (
              <div className="space-y-4">
                {favorites.slice(0, 3).map(apartment => (
                  <div key={apartment.id} className="flex items-center space-x-4 p-3 border border-slate-200 rounded-lg">
                    <img 
                      src={apartment.images?.[0] || apartment.image} 
                      alt={apartment.title}
                      className="w-16 h-16 object-cover rounded"
                    />
                    <div className="flex-1">
                      <h3 className="font-semibold text-slate-800">{apartment.title}</h3>
                      <p className="text-sm text-slate-600">{apartment.address}</p>
                      <p className="text-lg font-bold text-amber-600">${apartment.price?.toLocaleString()}</p>
                    </div>
                  </div>
                ))}
                {favorites.length > 3 && (
                  <p className="text-center text-slate-600">+{favorites.length - 3} more favorites</p>
                )}
              </div>
            ) : (
              <p className="text-slate-600">No favorite apartments yet. Start browsing to save your favorites!</p>
            )}
          </div>

          {/* Saved Searches Section */}
          <div className="bg-white rounded-lg shadow-md p-6 border border-slate-200">
            <h2 className="text-xl font-bold text-slate-800 mb-4">Saved Searches ({savedSearches.length})</h2>
            {savedSearches.length > 0 ? (
              <div className="space-y-4">
                {savedSearches.slice(0, 3).map(search => (
                  <div key={search.id} className="p-3 border border-slate-200 rounded-lg">
                    <h3 className="font-semibold text-slate-800">{search.name}</h3>
                    <p className="text-sm text-slate-600">
                      {search.filters.min_price && `$${search.filters.min_price}+`}
                      {search.filters.bedrooms && ` • ${search.filters.bedrooms} bed`}
                      {search.filters.neighborhood && ` • ${search.filters.neighborhood}`}
                    </p>
                    <p className="text-xs text-slate-500">Alert: {search.alert_frequency}</p>
                  </div>
                ))}
                {savedSearches.length > 3 && (
                  <p className="text-center text-slate-600">+{savedSearches.length - 3} more searches</p>
                )}
              </div>
            ) : (
              <p className="text-slate-600">No saved searches yet. Create searches to get notified of new listings!</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Apartment Details Component
const ApartmentDetails = ({ apartmentId }) => {
  const [apartment, setApartment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [showContactModal, setShowContactModal] = useState(false);

  useEffect(() => {
    fetchApartmentDetails();
  }, [apartmentId]);

  const fetchApartmentDetails = async () => {
    try {
      const response = await axios.get(`${API}/apartments/${apartmentId}`);
      setApartment(response.data);
    } catch (error) {
      console.error('Failed to fetch apartment details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleContactAgent = () => {
    // Always use your phone number
    window.open(`tel:646-408-8048`, '_self');
  };

  const handleScheduleTour = () => {
    // Scroll to the calendar booking section
    const calendarSection = document.getElementById('calendar-booking');
    if (calendarSection) {
      calendarSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleEmailContact = () => {
    setShowContactModal(true);
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!apartment) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-slate-800 mb-2">Apartment Not Found</h2>
          <p className="text-slate-600">The apartment you're looking for doesn't exist.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-md overflow-hidden border border-slate-200">
          {/* Image Gallery */}
          <div className="relative h-96">
            <img 
              src={apartment.images?.[currentImageIndex] || apartment.image}
              alt={apartment.title}
              className="w-full h-full object-cover"
            />
            {apartment.images && apartment.images.length > 1 && (
              <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
                {apartment.images.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentImageIndex(index)}
                    className={`w-3 h-3 rounded-full ${
                      index === currentImageIndex ? 'bg-white' : 'bg-white bg-opacity-50'
                    }`}
                  />
                ))}
              </div>
            )}
          </div>

          <div className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Apartment Info */}
              <div>
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h1 className="text-3xl font-bold text-slate-800 mb-2">{apartment.title}</h1>
                    <p className="text-slate-600 mb-2">{apartment.address}</p>
                    <div className="flex items-center space-x-2">
                      <span className="bg-green-500 text-white px-3 py-1 rounded-full text-sm font-semibold">
                        No Fee
                      </span>
                      <span className="text-2xl font-bold text-amber-600">
                        ${apartment.price?.toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="text-center p-4 bg-slate-50 rounded-lg">
                    <div className="text-2xl font-bold text-slate-800">
                      {apartment.bedrooms === 0 ? 'Studio' : apartment.bedrooms}
                    </div>
                    <div className="text-sm text-slate-600">Bedrooms</div>
                  </div>
                  <div className="text-center p-4 bg-slate-50 rounded-lg">
                    <div className="text-2xl font-bold text-slate-800">{apartment.bathrooms}</div>
                    <div className="text-sm text-slate-600">Bathrooms</div>
                  </div>
                  <div className="text-center p-4 bg-slate-50 rounded-lg">
                    <div className="text-2xl font-bold text-slate-800">{apartment.sqft}</div>
                    <div className="text-sm text-slate-600">Sq Ft</div>
                  </div>
                </div>

                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-slate-800 mb-3">Description</h3>
                  <p className="text-slate-600 leading-relaxed">{apartment.description}</p>
                </div>

                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-slate-800 mb-3">Amenities</h3>
                  <div className="flex flex-wrap gap-2">
                    {apartment.amenities?.map((amenity, index) => (
                      <span key={index} className="bg-amber-100 text-amber-800 px-3 py-1 rounded-full text-sm">
                        {amenity}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Contact Info - Always show your contact details */}
              <div>
                <div className="bg-slate-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-slate-800 mb-4">Contact Information</h3>
                  
                  <div className="space-y-3 mb-6">
                    <div className="flex items-center">
                      <svg className="w-5 h-5 text-slate-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                      <span className="text-slate-700">(646) 408-8048</span>
                    </div>
                    
                    <div className="flex items-center">
                      <svg className="w-5 h-5 text-slate-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      <span className="text-slate-700">placesfirm@gmail.com</span>
                    </div>

                    <div className="flex items-center">
                      <svg className="w-5 h-5 text-slate-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                      <span className="text-slate-700">Licensed Agent</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 gap-3">
                    {/* Primary Action - Call Button */}
                    <button 
                      onClick={handleContactAgent}
                      className="flex items-center justify-center w-full bg-gray-700 hover:bg-gray-600 text-gray-300 hover:text-white py-4 px-6 rounded-xl font-semibold border border-gray-600 hover:border-gray-500 transition-all duration-300 transform hover:scale-105 hover:shadow-xl hover:shadow-blue-500/30 group"
                    >
                      <svg className="w-5 h-5 mr-3 transition-all duration-300 group-hover:scale-110 group-hover:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                      <span className="transition-all duration-300 group-hover:text-blue-400">Call Agent Now</span>
                    </button>

                    {/* Secondary Actions Grid */}
                    <div className="grid grid-cols-2 gap-3">
                      {/* Email Button */}
                      <button 
                        onClick={() => setShowContactModal(true)}
                        className="flex items-center justify-center bg-gray-700 hover:bg-gray-600 text-gray-300 hover:text-white py-3 px-4 rounded-lg font-medium border border-gray-600 hover:border-gray-500 transition-all duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-green-500/30 group"
                      >
                        <svg className="w-4 h-4 mr-2 transition-all duration-300 group-hover:scale-110 group-hover:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 7.89a2 2 0 002.83 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        <span className="transition-all duration-300 group-hover:text-green-400">Email</span>
                      </button>

                      {/* Schedule Tour Button */}
                      <button 
                        onClick={handleScheduleTour}
                        className="flex items-center justify-center bg-emerald-600 hover:bg-emerald-700 text-white py-3 px-4 rounded-lg font-medium shadow-md hover:shadow-lg transition-all duration-200 transform hover:scale-105"
                      >
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <span className="hidden sm:inline">Schedule</span>
                        <span className="sm:hidden">Tour</span>
                      </button>
                    </div>

                    {/* Quick Actions */}
                    <div className="flex items-center justify-center space-x-6 pt-2">
                      <button 
                        onClick={() => window.open(`sms:646-408-8048`, '_self')}
                        className="flex items-center text-gray-600 hover:text-blue-600 transition-colors"
                      >
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                        <span className="text-sm font-medium">Text</span>
                      </button>
                      
                      <button 
                        onClick={() => {
                          navigator.share && navigator.share({
                            title: apartment.title,
                            text: `Check out this apartment: ${apartment.title}`,
                            url: window.location.href
                          }).catch(console.error);
                        }}
                        className="flex items-center text-gray-600 hover:text-blue-600 transition-colors"
                      >
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                        </svg>
                        <span className="text-sm font-medium">Share</span>
                      </button>
                    </div>
                  </div>

                  <div className="mt-6 pt-6 border-t border-slate-200">
                    <p className="text-sm text-slate-600 mt-1">
                      <strong>Neighborhood:</strong> {apartment.neighborhood}, {apartment.borough}
                    </p>
                  </div>
                </div>
              </div>

              {/* Calendar Booking Section */}
              <div id="calendar-booking" className="col-span-2 mt-8">
                <CalendarBooking 
                  apartmentId={apartment.id}
                  onBookingComplete={(booking) => {
                    console.log('Booking completed:', booking);
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Email Contact Modal */}
      <EmailContactModal 
        isOpen={showContactModal}
        onClose={() => setShowContactModal(false)}
        apartment={apartment}
      />
    </div>
  );
};

// Other components remain similar but with updated color scheme...
const SavedSearches = () => {
  const [savedSearches, setSavedSearches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSavedSearches();
  }, []);

  const fetchSavedSearches = async () => {
    try {
      const response = await axios.get(`${API}/users/saved-searches`);
      setSavedSearches(response.data);
    } catch (error) {
      console.error('Failed to fetch saved searches:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteSearch = async (searchId) => {
    try {
      await axios.delete(`${API}/users/saved-searches/${searchId}`);
      setSavedSearches(prev => prev.filter(search => search.id !== searchId));
    } catch (error) {
      console.error('Failed to delete search:', error);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-slate-800 mb-8">Saved Searches</h1>
        
        {savedSearches.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {savedSearches.map(search => (
              <div key={search.id} className="bg-white rounded-lg shadow-md p-6 border border-slate-200">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-semibold text-slate-800">{search.name}</h3>
                  <button
                    onClick={() => deleteSearch(search.id)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
                
                <div className="space-y-2 text-sm text-slate-600 mb-4">
                  {search.filters.min_price && (
                    <p>Min Price: ${search.filters.min_price.toLocaleString()}</p>
                  )}
                  {search.filters.max_price && (
                    <p>Max Price: ${search.filters.max_price.toLocaleString()}</p>
                  )}
                  {search.filters.bedrooms !== null && (
                    <p>Bedrooms: {search.filters.bedrooms === 0 ? 'Studio' : search.filters.bedrooms}</p>
                  )}
                  {search.filters.neighborhood && (
                    <p>Neighborhood: {search.filters.neighborhood}</p>
                  )}
                  {search.filters.borough && (
                    <p>Borough: {search.filters.borough}</p>
                  )}
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-xs text-slate-500">
                    Alert: {search.alert_frequency}
                  </span>
                  <button className="bg-amber-600 text-slate-800 px-4 py-2 rounded-lg hover:bg-amber-500 transition-colors text-sm font-semibold">
                    Run Search
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <h2 className="text-xl font-semibold text-slate-800 mb-2">No saved searches yet</h2>
            <p className="text-slate-600 mb-4">Create and save searches to get notified when new apartments match your criteria.</p>
            <a 
              href="/"
              className="bg-amber-600 text-slate-800 px-6 py-3 rounded-lg hover:bg-amber-500 transition-colors font-semibold"
            >
              Start Searching
            </a>
          </div>
        )}
      </div>
    </div>
  );
};

// Enhanced Map View Component  
const MapView = ({ apartments }) => {
  return (
    <div className="bg-slate-200 h-96 rounded-lg flex items-center justify-center relative">
      <div className="text-center">
        <svg className="w-16 h-16 mx-auto text-slate-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <p className="text-slate-600">Interactive map with {apartments.length} apartments coming soon!</p>
        <p className="text-sm text-slate-500 mt-2">Integration with Google Maps or Mapbox will show apartment locations</p>
      </div>
    </div>
  );
};

// Loading Spinner Component
const LoadingSpinner = () => {
  return (
    <div className="flex justify-center items-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
    </div>
  );
};

// Clean Footer Component - Essentials Only
const Footer = () => {
  return (
    <footer className="bg-slate-800 text-amber-100">
      <div className="container mx-auto px-4 py-8">
        {/* Main Footer Content */}
        <div className="flex flex-col md:flex-row justify-between items-center space-y-6 md:space-y-0">
          
          {/* Left: Logo & Description */}
          <div className="text-center md:text-left">
            <div className="flex items-center justify-center md:justify-start space-x-3 mb-3">
              <div className="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <div>
                <div className="text-lg font-bold text-amber-100">No Fee Places</div>
                <div className="text-xs text-amber-200 -mt-1">NYC RENTALS</div>
              </div>
            </div>
            <p className="text-sm text-amber-200 max-w-sm">
              Your trusted source for <strong>no broker fee apartments NYC</strong>
            </p>
          </div>

          {/* Center: Essential Contact */}
          <div className="text-center">
            <div className="space-y-2 text-sm text-amber-200">
              <div className="flex items-center justify-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <span>placesfirm@gmail.com</span>
              </div>
              <div className="flex items-center justify-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                <span>(646) 408-8048</span>
              </div>
            </div>
          </div>

          {/* Right: Social Media */}
          <div className="text-center">
            <div className="text-sm text-amber-200 mb-3">Follow Us</div>
            <div className="flex justify-center space-x-4">
              {/* Facebook */}
              <a 
                href="https://www.facebook.com/NoFeePlacesNYC" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-amber-200 hover:text-amber-100 transition-colors transform hover:scale-110"
                aria-label="Follow us on Facebook"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
              </a>
              
              {/* Instagram */}
              <a 
                href="https://www.instagram.com/nofeeplaces" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-amber-200 hover:text-amber-100 transition-colors transform hover:scale-110"
                aria-label="Follow us on Instagram"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 6.62 5.367 11.987 11.988 11.987c6.62 0 11.987-5.367 11.987-11.987C24.014 5.367 18.637.001 12.017.001zM8.449 16.988c-1.297 0-2.448-.73-3.016-1.8L4.27 17.94l-1.027-.585 1.162-2.753C4.164 14.22 4 13.637 4 13.017c0-2.29 1.86-4.149 4.149-4.149 2.29 0 4.149 1.86 4.149 4.149 0 2.29-1.86 4.149-4.149 4.149-.62 0-1.203-.164-1.585-.405L3.811 19.514l-.585-1.027 2.753-1.162c-1.07-.568-1.8-1.719-1.8-3.016 0-1.88 1.528-3.408 3.408-3.408s3.408 1.528 3.408 3.408c0 1.297-.73 2.448-1.8 3.016l2.753 1.162-.585 1.027-2.753-1.162c-.382.241-.965.405-1.585.405-.62 0-1.203-.164-1.585-.405l-2.753 1.162-.585-1.027 2.753-1.162c-1.07-.568-1.8-1.719-1.8-3.016 0-1.88 1.528-3.408 3.408-3.408s3.408 1.528 3.408 3.408-.73 2.448-1.8 3.016l2.753 1.162-.585 1.027-2.753-1.162c-.382.241-.965.405-1.585.405z"/>
                </svg>
              </a>
              
              {/* Twitter/X */}
              <a 
                href="https://twitter.com/NoFeePlacesNYC" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-amber-200 hover:text-amber-100 transition-colors transform hover:scale-110"
                aria-label="Follow us on Twitter"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                </svg>
              </a>
              
              {/* LinkedIn */}
              <a 
                href="https://www.linkedin.com/company/nofeeplaces" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-amber-200 hover:text-amber-100 transition-colors transform hover:scale-110"
                aria-label="Connect with us on LinkedIn"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
              </a>
              
              {/* YouTube */}
              <a 
                href="https://www.youtube.com/@NoFeePlacesNYC" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-amber-200 hover:text-amber-100 transition-colors transform hover:scale-110"
                aria-label="Subscribe to our YouTube channel"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.30 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>

        {/* SEO Links Section - Enhanced */}
        <div className="border-t border-slate-700 mt-6 pt-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center md:text-left mb-4">
            {/* Popular Searches */}
            <div>
              <h4 className="text-amber-200 font-semibold text-sm mb-2">Popular NYC Areas</h4>
              <ul className="space-y-1 text-xs">
                <li><a href="/manhattan-no-fee-apartments" className="text-gray-300 hover:text-amber-200 transition-colors">Manhattan No Fee</a></li>
                <li><a href="/brooklyn-no-fee-rentals" className="text-gray-300 hover:text-amber-200 transition-colors">Brooklyn No Fee</a></li>
                <li><a href="/queens-zero-fee-apartments" className="text-gray-300 hover:text-amber-200 transition-colors">Queens No Fee</a></li>
                <li><a href="/upper-east-side-no-fee" className="text-gray-300 hover:text-amber-200 transition-colors">Upper East Side</a></li>
              </ul>
            </div>
            
            {/* Apartment Types */}
            <div>
              <h4 className="text-amber-200 font-semibold text-sm mb-2">Apartment Types</h4>
              <ul className="space-y-1 text-xs">
                <li><a href="/studio-no-fee-apartments-nyc" className="text-gray-300 hover:text-amber-200 transition-colors">Studio No Fee</a></li>
                <li><a href="/1-bedroom-no-fee-apartments" className="text-gray-300 hover:text-amber-200 transition-colors">1 Bedroom No Fee</a></li>
                <li><a href="/2-bedroom-no-fee-apartments" className="text-gray-300 hover:text-amber-200 transition-colors">2 Bedroom No Fee</a></li>
                <li><a href="/luxury-no-fee-apartments-nyc" className="text-gray-300 hover:text-amber-200 transition-colors">Luxury No Fee</a></li>
              </ul>
            </div>
            
            {/* Resources */}
            <div>
              <h4 className="text-amber-200 font-semibold text-sm mb-2">Resources</h4>
              <ul className="space-y-1 text-xs">
                <li><a href="/complete-guide-no-fee-apartments-nyc" className="text-gray-300 hover:text-amber-200 transition-colors">Complete Guide NYC 2025</a></li>
                <li><a href="/how-to-find-no-fee-apartments" className="text-gray-300 hover:text-amber-200 transition-colors">How to Find No Fee</a></li>
                <li><a href="/nyc-rental-tips" className="text-gray-300 hover:text-amber-200 transition-colors">NYC Rental Tips</a></li>
                <li><a href="/broker-fee-calculator" className="text-gray-300 hover:text-amber-200 transition-colors">Fee Calculator</a></li>
              </ul>
            </div>
          </div>
        </div>

        {/* Bottom: Copyright & Legal Disclaimer */}
        <div className="border-t border-slate-700 mt-6 pt-4 text-center">
          <p className="text-sm text-amber-200 mb-3">
            &copy; 2025 NoFeePlaces.com. All rights reserved.
          </p>
          
          {/* Legal Disclaimer */}
          <div className="text-xs text-amber-300 leading-relaxed max-w-4xl mx-auto">
            <p className="mb-2">
              <strong>Legal Disclaimer:</strong> NoFeePlaces.com serves as a platform connecting prospective tenants with no-fee apartment listings in New York City. 
              All property information, including but not limited to rental prices, availability, specifications, and images, is provided by third-party property owners, 
              management companies, or listing agents and is subject to change without notice.
            </p>
            <p className="mb-2">
              We make no representations or warranties regarding the accuracy, completeness, or reliability of any listing information. 
              Prospective tenants are advised to independently verify all details directly with property owners or authorized agents before making any rental decisions. 
              NoFeePlaces.com is not responsible for any errors, omissions, or misrepresentations in listings, nor for any transactions between tenants and property owners.
            </p>
            <p>
              By using this website, you acknowledge that NoFeePlaces.com acts solely as an information platform and assumes no liability for rental agreements, 
              property conditions, or disputes arising from rental transactions. All rental agreements are between tenants and property owners/agents directly.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

// Enhanced AI Chatbot Component with Context Awareness
const AIChatbot = ({ apartmentId = null, apartment = null }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [apartmentContext, setApartmentContext] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Fetch apartment details for context if apartmentId is provided
  useEffect(() => {
    const fetchApartmentContext = async () => {
      if (apartmentId && !apartment) {
        try {
          const response = await axios.get(`${API}/apartments/${apartmentId}`);
          setApartmentContext(response.data);
        } catch (error) {
          console.error('Failed to fetch apartment context:', error);
        }
      } else if (apartment) {
        setApartmentContext(apartment);
      }
    };

    fetchApartmentContext();
  }, [apartmentId, apartment]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');

    // Add user message to chat
    setMessages(prev => [...prev, { 
      type: 'user', 
      content: userMessage, 
      timestamp: new Date() 
    }]);

    setIsLoading(true);

    try {
      // Create enhanced context for AI
      let contextInfo = "You are an AI assistant for NoFeePlaces.com, a no-fee apartment rental platform in NYC. You help users with apartment searches, rental information, and scheduling viewings. ";
      
      if (apartmentContext) {
        contextInfo += `\n\nCurrent apartment context: ${apartmentContext.title} at ${apartmentContext.address}, ${apartmentContext.bedrooms === 0 ? 'Studio' : apartmentContext.bedrooms + ' bedroom'} for $${apartmentContext.price}/month. Amenities: ${apartmentContext.amenities?.join(', ') || 'N/A'}. Contact: Licensed Agent at (646) 408-8048 or placesfirm@gmail.com.`;
      }
      
      contextInfo += "\n\nAlways be helpful, professional, and encouraging. If asked about specific apartments not in context, suggest they browse our full listings at nofeeplaces.com or contact our licensed agent directly.";

      const response = await axios.post(`${API}/chat`, {
        message: userMessage,
        session_id: sessionId,
        context: contextInfo
      });

      // Store session ID for conversation continuity
      if (response.data.session_id && !sessionId) {
        setSessionId(response.data.session_id);
      }

      // Add AI response to chat
      setMessages(prev => [...prev, { 
        type: 'ai', 
        content: response.data.response, 
        timestamp: new Date() 
      }]);

    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        type: 'ai', 
        content: 'Sorry, I\'m having trouble connecting right now. Please try calling our licensed agent at (646) 408-8048 for immediate assistance with your rental needs.', 
        timestamp: new Date() 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
    if (!isOpen && messages.length === 0) {
      // Add welcome message when first opened with apartment context
      let welcomeMessage = "Hi! I'm your NoFeePlaces.com assistant. I can help with questions about our no-fee apartments, application process, and scheduling viewings.";
      
      if (apartmentContext) {
        welcomeMessage = `Hi! I see you're looking at ${apartmentContext.title}. I'm here to help answer questions about this apartment and our no-fee rental process. What would you like to know?`;
      } else {
        welcomeMessage += " How can I assist you today?";
      }
      
      setMessages([{
        type: 'ai',
        content: welcomeMessage,
        timestamp: new Date()
      }]);
    }
  };

  return (
    <>
      {/* Chat Toggle Button - Smaller size with blue theme */}
      <div className="fixed bottom-16 right-6 z-[60]">
        <button
          onClick={toggleChat}
          className={`w-16 h-16 rounded-full shadow-2xl hover:shadow-3xl transition-all duration-300 flex items-center justify-center ${
            isOpen 
              ? 'bg-red-500 hover:bg-red-600' 
              : 'bg-blue-500 hover:bg-blue-600 animate-pulse'
          }`}
          style={{ boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)' }}
          aria-label="Open AI Assistant chat"
        >
          {isOpen ? (
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          )}
        </button>
        
        {/* Help text bubble when closed - smaller and blue themed */}
        {!isOpen && (
          <div className="absolute bottom-full right-2 mb-2 bg-blue-500 text-white px-3 py-1.5 rounded-lg text-xs whitespace-nowrap animate-bounce shadow-lg font-medium">
            AI Assistant
          </div>
        )}
      </div>

      {/* Chat Window - Yellow Theme */}
      {isOpen && (
        <div className="fixed bottom-48 right-8 w-96 h-[500px] bg-white rounded-2xl shadow-xl border border-gray-200 z-50 flex flex-col">
          {/* Chat Header - Blue Theme */}
          <div className="flex items-center justify-between p-4 bg-blue-500 rounded-t-2xl">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">AI Assistant</h3>
                <p className="text-xs text-blue-100">Ask me anything about rentals</p>
              </div>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
            {messages.map((message, index) => (
              <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs px-4 py-2 rounded-2xl ${
                  message.type === 'user' 
                    ? 'bg-orange-500 text-white' 
                    : 'bg-white border border-gray-200 text-gray-800 shadow-sm'
                }`}>
                  <p className="text-sm">{message.content}</p>
                  <p className="text-xs opacity-70 mt-1">
                    {message.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                  </p>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 px-4 py-2 rounded-2xl shadow-sm">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-orange-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-orange-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-orange-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input */}
          <div className="p-4 border-t border-gray-200 bg-white rounded-b-2xl">
            <div className="flex space-x-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about apartments, applications, viewings..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none text-sm"
                disabled={isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || isLoading}
                className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

// Favorites Management Page
const FavoritesPage = () => {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedForComparison, setSelectedForComparison] = useState([]);
  const [showComparison, setShowComparison] = useState(false);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      fetchFavorites();
    }
  }, [isAuthenticated]);

  const fetchFavorites = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/users/favorites`);
      setFavorites(response.data);
      setError(null);
    } catch (error) {
      console.error('Failed to fetch favorites:', error);
      setError('Failed to load favorites');
    } finally {
      setLoading(false);
    }
  };

  const removeFavorite = async (apartmentId) => {
    try {
      await axios.delete(`${API}/users/favorites/${apartmentId}`);
      setFavorites(prev => prev.filter(apt => apt.id !== apartmentId));
      
      // Remove from comparison selection if it was selected
      setSelectedForComparison(prev => prev.filter(id => id !== apartmentId));
    } catch (error) {
      console.error('Failed to remove favorite:', error);
      alert('Failed to remove favorite');
    }
  };

  const toggleComparisonSelection = (apartmentId) => {
    setSelectedForComparison(prev => {
      if (prev.includes(apartmentId)) {
        return prev.filter(id => id !== apartmentId);
      } else if (prev.length < 3) { // Limit to 3 apartments for comparison
        return [...prev, apartmentId];
      } else {
        alert('You can compare up to 3 apartments at a time');
        return prev;
      }
    });
  };

  const startComparison = () => {
    if (selectedForComparison.length < 2) {
      alert('Please select at least 2 apartments to compare');
      return;
    }
    setShowComparison(true);
  };

  const getSelectedApartments = () => {
    return favorites.filter(apt => selectedForComparison.includes(apt.id));
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-slate-800 mb-4">Please Sign In</h2>
          <p className="text-slate-600">You need to be signed in to view your favorites.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <div className="container mx-auto px-4 py-8">
          <div className="flex justify-center items-center h-64">
            <LoadingSpinner />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-800 mb-2">My Favorites</h1>
            <p className="text-slate-600">{favorites.length} saved apartments</p>
          </div>
          
          {selectedForComparison.length > 0 && (
            <div className="flex items-center space-x-4">
              <span className="text-sm text-slate-600">
                {selectedForComparison.length} selected for comparison
              </span>
              <button
                onClick={startComparison}
                disabled={selectedForComparison.length < 2}
                className="btn-primary px-4 py-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Compare Selected
              </button>
              <button
                onClick={() => setSelectedForComparison([])}
                className="text-slate-500 hover:text-slate-700 text-sm"
              >
                Clear Selection
              </button>
            </div>
          )}
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {favorites.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 bg-slate-200 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-slate-800 mb-2">No favorites yet</h3>
            <p className="text-slate-600 mb-4">Start browsing apartments to save your favorites!</p>
            <Link
              to="/"
              className="btn-primary px-6 py-3 inline-block"
            >
              Browse Apartments
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {favorites.map(apartment => (
              <div key={apartment.id} className="relative">
                <div className={`card-luxury transition-all duration-300 ${
                  selectedForComparison.includes(apartment.id) 
                    ? 'ring-2 ring-amber-400 shadow-lg scale-105' 
                    : ''
                }`}>
                  {/* Comparison Checkbox */}
                  <div className="absolute top-4 left-4 z-10">
                    <label className="flex items-center space-x-2 glass-dark p-2 rounded-lg cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedForComparison.includes(apartment.id)}
                        onChange={() => toggleComparisonSelection(apartment.id)}
                        className="w-4 h-4 text-amber-600 bg-transparent border-amber-400 rounded focus:ring-amber-500 focus:ring-2"
                      />
                      <span className="text-xs text-slate-200 font-medium">Compare</span>
                    </label>
                  </div>

                  {/* Remove Favorite Button */}
                  <div className="absolute top-4 right-4 z-10">
                    <button
                      onClick={() => removeFavorite(apartment.id)}
                      className="glass p-2 rounded-full transition-all hover:scale-110 hover:shadow-glow text-red-400 hover:text-red-300"
                      title="Remove from favorites"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                      </svg>
                    </button>
                  </div>

                  {/* Apartment Card Content */}
                  <div className="relative overflow-hidden rounded-2xl mb-4">
                    <LazyImage
                      src={apartment.images?.[0] || apartment.image}
                      alt={apartment.title}
                      className="w-full h-56 object-cover"
                    />
                    
                    {/* No Fee Badge */}
                    <div className="absolute bottom-4 left-4">
                      <span className="badge badge-success animate-glow">NO FEE</span>
                    </div>
                    
                    {/* Price Tag */}
                    <div className="absolute bottom-4 right-4">
                      <div className="glass-dark px-4 py-2 rounded-lg">
                        <span className="text-2xl font-bold gradient-text">
                          ${apartment.price?.toLocaleString() || apartment.price}
                        </span>
                        <span className="text-slate-300 text-sm ml-1">/mo</span>
                      </div>
                    </div>
                  </div>

                  <div className="px-4 pb-4">
                    <h3 className="text-xl font-bold text-slate-100 mb-2">{apartment.title}</h3>
                    <p className="text-slate-400 text-sm mb-3 flex items-center">
                      <svg className="w-4 h-4 mr-2 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {apartment.address}
                    </p>

                    {/* Property Details */}
                    <div className="flex items-center justify-between mb-4 text-sm text-slate-300">
                      <div className="flex items-center space-x-4">
                        <span className="font-medium">
                          {apartment.bedrooms === 0 ? 'Studio' : `${apartment.bedrooms} bed`}
                        </span>
                        <span className="font-medium">{apartment.bathrooms} bath</span>
                        <span className="font-medium">{apartment.sqft} sq ft</span>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex justify-between items-center pt-4 border-t border-white/10">
                      <div className="flex gap-2">
                        <button
                          onClick={() => window.open(`tel:646-408-8048`, '_self')}
                          className="bg-gray-700 text-gray-300 px-3 py-2 rounded-lg hover:bg-gray-600 hover:text-white transition-all duration-300 text-xs font-medium border border-gray-600 hover:border-gray-500 hover:shadow-lg hover:shadow-blue-500/30 hover:scale-105 transform group flex items-center"
                        >
                          <svg className="w-3 h-3 mr-1 transition-all duration-300 group-hover:scale-110 group-hover:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                          </svg>
                          <span className="transition-all duration-300 group-hover:text-blue-400">Call</span>
                        </button>
                        <button
                          onClick={() => navigate(`/apartment/${apartment.id}`)}
                          className="btn-primary text-xs px-3 py-2 hover-lift"
                        >
                          View Details
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Apartment Comparison Modal */}
        {showComparison && (
          <ApartmentComparison 
            apartments={getSelectedApartments()}
            onClose={() => setShowComparison(false)}
          />
        )}
      </div>
    </div>
  );
};

// Apartment Comparison Component
const ApartmentComparison = ({ apartments, onClose }) => {
  const navigate = useNavigate();
  const features = [
    { key: 'price', label: 'Monthly Rent', format: (val) => `$${val?.toLocaleString()}` },
    { key: 'bedrooms', label: 'Bedrooms', format: (val) => val === 0 ? 'Studio' : val },
    { key: 'bathrooms', label: 'Bathrooms', format: (val) => val },
    { key: 'sqft', label: 'Square Feet', format: (val) => `${val} sq ft` },
    { key: 'neighborhood', label: 'Neighborhood', format: (val) => val },
    { key: 'borough', label: 'Borough', format: (val) => val }
  ];

  const compareFeature = (feature, apartments) => {
    const values = apartments.map(apt => apt[feature]);
    
    if (feature === 'price' || feature === 'sqft') {
      const minVal = Math.min(...values);
      const maxVal = Math.max(...values);
      
      return values.map(val => ({
        value: val,
        isBest: feature === 'price' ? val === minVal : val === maxVal,
        isWorst: feature === 'price' ? val === maxVal : val === minVal
      }));
    }
    
    return values.map(val => ({ value: val, isBest: false, isWorst: false }));
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="glass-dark rounded-2xl max-w-6xl w-full max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-white/10">
          <h2 className="text-2xl font-bold text-slate-100">Apartment Comparison</h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Apartment Images */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-6">
          {apartments.map((apartment, index) => (
            <div key={apartment.id} className="text-center">
              <div className="relative mb-4">
                <LazyImage
                  src={apartment.images?.[0] || apartment.image}
                  alt={apartment.title}
                  className="w-full h-48 object-cover rounded-lg"
                />
                <div className="absolute top-2 left-2">
                  <span className="badge badge-success">NO FEE</span>
                </div>
              </div>
              <h3 className="text-lg font-bold text-slate-100 mb-1">{apartment.title}</h3>
              <p className="text-sm text-slate-400">{apartment.address}</p>
            </div>
          ))}
        </div>

        {/* Comparison Table */}
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr>
                  <th className="text-left text-slate-300 font-medium py-3 px-4">Feature</th>
                  {apartments.map((apartment, index) => (
                    <th key={apartment.id} className="text-center text-slate-300 font-medium py-3 px-4">
                      Apartment {index + 1}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {features.map((feature) => {
                  const comparisonResults = compareFeature(feature.key, apartments);
                  
                  return (
                    <tr key={feature.key} className="border-t border-white/10">
                      <td className="py-4 px-4 text-slate-200 font-medium">{feature.label}</td>
                      {comparisonResults.map((result, index) => (
                        <td key={index} className="py-4 px-4 text-center">
                          <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                            result.isBest 
                              ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                              : result.isWorst 
                                ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                                : 'bg-slate-500/20 text-slate-300 border border-slate-500/30'
                          }`}>
                            {feature.format(result.value)}
                          </span>
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Amenities Comparison */}
          <div className="mt-8">
            <h4 className="text-lg font-bold text-slate-200 mb-4">Amenities</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {apartments.map((apartment, index) => (
                <div key={apartment.id}>
                  <h5 className="text-md font-semibold text-slate-300 mb-2">Apartment {index + 1}</h5>
                  <div className="flex flex-wrap gap-2">
                    {apartment.amenities?.map((amenity, amenityIndex) => (
                      <span key={amenityIndex} className="bg-white/10 text-slate-300 px-2 py-1 rounded-full text-xs font-medium">
                        {amenity}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-center space-x-4 mt-8 pt-6 border-t border-white/10">
            {apartments.map((apartment) => (
              <button
                key={apartment.id}
                onClick={() => navigate(`/apartment/${apartment.id}`)}
                className="btn-primary px-6 py-3 hover-lift"
              >
                View {apartment.title.split(' ')[0]} Details
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Complete Guide Component (for separate page)
const CompleteGuideNoFeeApartments = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">Complete Guide to No Fee Apartments NYC 2025</h1>
            <button
              onClick={() => window.history.back()}
              className="text-gray-500 hover:text-gray-700 text-sm"
            >
              ← Back to Listings
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          
          {/* Introduction */}
          <div className="bg-white rounded-lg shadow-sm p-8 mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">
              The Ultimate Guide to Finding No Fee Apartments in NYC
            </h2>
            <p className="text-lg text-gray-700 leading-relaxed mb-6">
              Navigate New York City's competitive rental market without paying expensive broker fees. 
              This comprehensive guide reveals insider strategies, market insights, and actionable tips 
              to secure your dream <strong>no fee apartment NYC</strong> while saving thousands of dollars.
            </p>
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
              <p className="text-blue-800 font-semibold">
                💰 Average Savings: $3,000 - $8,000 per lease by choosing no fee apartments
              </p>
            </div>
          </div>

          {/* What Are No Fee Apartments */}
          <div className="bg-white rounded-lg shadow-sm p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">What Are No Fee Apartments NYC?</h2>
            
            <p className="text-gray-700 leading-relaxed mb-6">
              <strong>No fee apartments NYC</strong> are rental properties where tenants pay zero broker fees. 
              Unlike traditional NYC rentals that charge 12-15% of annual rent as broker fees ($3,000-$8,000+), 
              <strong>no broker fee apartments NYC</strong> allow direct leasing with property owners or management companies.
            </p>

            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">Traditional Rental Process</h3>
                <div className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-red-100 text-red-600 rounded-full flex items-center justify-center text-sm font-bold">1</div>
                    <p className="text-gray-700">Find apartment through broker</p>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-red-100 text-red-600 rounded-full flex items-center justify-center text-sm font-bold">2</div>
                    <p className="text-gray-700">Pay 12-15% broker fee ($3,000-$8,000+)</p>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-red-100 text-red-600 rounded-full flex items-center justify-center text-sm font-bold">3</div>
                    <p className="text-gray-700">Limited direct communication with landlord</p>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">No Fee Rental Process</h3>
                <div className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-bold">1</div>
                    <p className="text-gray-700">Find apartment directly from owner/management</p>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-bold">2</div>
                    <p className="text-gray-700">Pay $0 in broker fees - Save thousands!</p>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-bold">3</div>
                    <p className="text-gray-700">Direct relationship with property management</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Contact CTA */}
          <div className="bg-blue-600 text-white rounded-lg p-8 text-center">
            <h2 className="text-2xl font-bold mb-4">Ready to Find Your No Fee Apartment?</h2>
            <p className="text-lg mb-6">
              Get expert guidance from our office, NYC's leading no fee apartment specialists.
            </p>
            <div className="space-y-4">
              <div className="flex justify-center space-x-6 text-lg">
                <div>📞 (646) 408-8048</div>
                <div>📧 placesfirm@gmail.com</div>
              </div>
              <button
                onClick={() => window.location.href = '/'}
                className="bg-white text-blue-600 px-8 py-3 rounded-lg hover:bg-gray-100 transition-colors duration-200 font-semibold"
              >
                Browse Available Apartments
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export const Components = {
  Header,
  Hero,
  SEOContentSection,
  AdvancedSearchFilters,
  ApartmentCard,
  MapView,
  Footer,
  LoadingSpinner,
  AuthModal,
  UserDashboard,
  ApartmentDetails,
  SavedSearches,
  CalendarBooking,
  AdminAppointments,
  AIChatbot,
  FavoritesPage,
  ApartmentComparison,
  LazyImage,
  ErrorBoundary,
  Toast,
  ToastProvider,
  useToast,
  EmailContactModal,
  CompleteGuideNoFeeApartments
};


// =============================================
// BLOG COMPONENTS
// =============================================

// Blog List Component
const BlogList = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPosts, setTotalPosts] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [categories, setCategories] = useState([]);

  const API = (process.env.REACT_APP_BACKEND_URL || '') + '/api';

  useEffect(() => {
    fetchPosts();
    fetchCategories();
  }, [page, selectedCategory]);

  const fetchPosts = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '9'
      });
      
      if (selectedCategory) {
        params.append('category', selectedCategory);
      }

      const response = await axios.get(`${API}/blog?${params}`);
      
      if (page === 1) {
        setPosts(response.data.posts);
      } else {
        setPosts(prev => [...prev, ...response.data.posts]);
      }
      
      setTotalPosts(response.data.total);
      setHasMore(response.data.has_more);
    } catch (error) {
      console.error('Error fetching blog posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/blog/categories/list`);
      setCategories(response.data.categories);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleCategoryFilter = (category) => {
    setSelectedCategory(category);
    setPage(1);
    setPosts([]);
  };

  const loadMore = () => {
    setPage(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-900 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Blog Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
            NYC Rental <span className="gradient-text">Insights</span>
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Your ultimate guide to no-fee apartments, neighborhood insights, and NYC rental market trends
          </p>
        </div>

        {/* Category Filter */}
        <div className="mb-12">
          <div className="flex flex-wrap justify-center gap-4">
            <button
              onClick={() => handleCategoryFilter('')}
              className={`px-6 py-3 rounded-full text-sm font-medium transition-all ${
                selectedCategory === '' 
                  ? 'bg-purple-600 text-white shadow-lg' 
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              All Posts
            </button>
            {categories.map(category => (
              <button
                key={category}
                onClick={() => handleCategoryFilter(category)}
                className={`px-6 py-3 rounded-full text-sm font-medium transition-all ${
                  selectedCategory === category 
                    ? 'bg-purple-600 text-white shadow-lg' 
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {/* Blog Posts Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          {posts.map(post => (
            <article key={post.id} className="bg-gray-800 rounded-2xl overflow-hidden shadow-xl hover:shadow-2xl transition-all duration-300 hover:transform hover:scale-105">
              {post.featured_image && (
                <div className="h-48 overflow-hidden">
                  <img 
                    src={post.featured_image} 
                    alt={post.title}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}
              
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <span className="px-3 py-1 bg-purple-600/20 text-purple-400 rounded-full text-xs font-medium">
                    {post.category}
                  </span>
                  <span className="text-gray-400 text-sm">
                    {post.read_time} min read
                  </span>
                </div>
                
                <h2 className="text-xl font-bold text-white mb-3 hover:text-purple-400 transition-colors">
                  <a href={`/blog/${post.slug}`}>
                    {post.title}
                  </a>
                </h2>
                
                <p className="text-gray-300 text-sm mb-4 line-clamp-3">
                  {post.excerpt}
                </p>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
                      <span className="text-white text-xs font-bold">NF</span>
                    </div>
                    <div>
                      <p className="text-white text-sm font-medium">{post.author}</p>
                      <p className="text-gray-400 text-xs">{formatDate(post.published_at)}</p>
                    </div>
                  </div>
                  
                  <a 
                    href={`/blog/${post.slug}`}
                    className="text-purple-400 hover:text-purple-300 font-medium text-sm flex items-center"
                  >
                    Read More
                    <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </a>
                </div>
              </div>
            </article>
          ))}
        </div>

        {/* Load More Button */}
        {hasMore && (
          <div className="text-center">
            <button
              onClick={loadMore}
              disabled={loading}
              className="px-8 py-4 bg-purple-600 text-white rounded-xl font-medium hover:bg-purple-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Loading...' : 'Load More Posts'}
            </button>
          </div>
        )}

        {/* Blog Stats */}
        <div className="mt-16 text-center">
          <p className="text-gray-400">
            Showing {posts.length} of {totalPosts} posts
          </p>
        </div>
      </div>
    </div>
  );
};

// Blog Post Detail Component
const BlogPost = ({ slug }) => {
  const [post, setPost] = useState(null);
  const [relatedPosts, setRelatedPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  const API = (process.env.REACT_APP_BACKEND_URL || '') + '/api';

  useEffect(() => {
    if (slug) {
      fetchPost();
      fetchRelatedPosts();
    }
  }, [slug]);

  const fetchPost = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/blog/${slug}`);
      setPost(response.data);
    } catch (error) {
      console.error('Error fetching blog post:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRelatedPosts = async () => {
    try {
      const response = await axios.get(`${API}/blog/related/${slug}`);
      setRelatedPosts(response.data);
    } catch (error) {
      console.error('Error fetching related posts:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (!post) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-4">Post Not Found</h1>
          <p className="text-gray-400 mb-8">The blog post you're looking for doesn't exist.</p>
          <a href="/blog" className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
            Back to Blog
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-purple-900 via-blue-900 to-purple-900 py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <span className="px-4 py-2 bg-purple-600/20 text-purple-400 rounded-full text-sm font-medium mb-6 inline-block">
              {post.category}
            </span>
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
              {post.title}
            </h1>
            <div className="flex items-center justify-center space-x-6 text-gray-300">
              <div className="flex items-center space-x-2">
                <div className="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-bold">NF</span>
                </div>
                <span>{post.author}</span>
              </div>
              <span>•</span>
              <span>{formatDate(post.published_at)}</span>
              <span>•</span>
              <span>{post.read_time} min read</span>
            </div>
          </div>
        </div>
      </div>

      {/* Article Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <article className="prose prose-lg prose-invert max-w-none">
          <div 
            dangerouslySetInnerHTML={{ __html: post.content }}
            className="text-gray-300 leading-relaxed"
          />
        </article>

        {/* Tags */}
        {post.tags && post.tags.length > 0 && (
          <div className="mt-12 pt-8 border-t border-gray-800">
            <h3 className="text-white font-medium mb-4">Tags:</h3>
            <div className="flex flex-wrap gap-2">
              {post.tags.map(tag => (
                <span 
                  key={tag}
                  className="px-3 py-1 bg-gray-800 text-gray-300 rounded-full text-sm"
                >
                  #{tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Related Posts */}
        {relatedPosts.length > 0 && (
          <div className="mt-16">
            <h3 className="text-2xl font-bold text-white mb-8">Related Articles</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {relatedPosts.map(relatedPost => (
                <article key={relatedPost.id} className="bg-gray-800 rounded-xl p-6 hover:bg-gray-750 transition-colors">
                  <span className="px-3 py-1 bg-purple-600/20 text-purple-400 rounded-full text-xs font-medium mb-3 inline-block">
                    {relatedPost.category}
                  </span>
                  <h4 className="text-white font-bold mb-2 hover:text-purple-400">
                    <a href={`/blog/${relatedPost.slug}`}>
                      {relatedPost.title}
                    </a>
                  </h4>
                  <p className="text-gray-400 text-sm mb-4">
                    {relatedPost.excerpt}
                  </p>
                  <a 
                    href={`/blog/${relatedPost.slug}`}
                    className="text-purple-400 hover:text-purple-300 text-sm font-medium"
                  >
                    Read More →
                  </a>
                </article>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export {
  Header,
  Hero,
  SEOContentSection,
  AdvancedSearchFilters,
  ApartmentCard,
  ImageCarousel,
  MapView,
  Footer,
  LoadingSpinner,
  AuthModal,
  UserDashboard,
  ApartmentDetails,
  SavedSearches,
  CalendarBooking,
  AdminAppointments,
  AIChatbot,
  FavoritesPage,
  ApartmentComparison,
  LazyImage,
  ErrorBoundary,
  Toast,
  EmailContactModal,
  CompleteGuideNoFeeApartments,
  BlogList,
  BlogPost
};
