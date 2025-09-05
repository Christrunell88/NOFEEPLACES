import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuth } from './App';
import { Link, useNavigate } from 'react-router-dom';
// Analytics and marketing components will be imported when needed

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Header Component with New PLACES Branding and SEO Navigation
// Professional Header Component
const Header = ({ isAuthenticated, user, logout, setShowAuthModal }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [expandedSections, setExpandedSections] = useState({});

  const toggleSection = (sectionKey) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionKey]: !prev[sectionKey]
    }));
  };

  return (
    <header className="sticky top-0 bg-white border-b border-gray-200 z-50 shadow-sm">
      {/* Main Header Bar */}
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            {/* Cool Custom Logo Design */}
            <div className="relative logo-glow">
              {/* Logo Icon - Modern Building/Key Design */}
              <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg flex items-center justify-center shadow-lg transform rotate-3 group-hover:rotate-0 transition-all duration-300 group-hover:scale-105">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
            </div>
            
            {/* Logo Text */}
            <div className="flex flex-col">
              <div className="flex items-center space-x-1">
                <span className="text-xl md:text-2xl font-bold text-gray-900 tracking-tight group-hover:text-gray-800 transition-colors">No Fee</span>
                <span className="text-base md:text-lg font-semibold text-orange-500 group-hover:text-orange-600 transition-colors">Places</span>
              </div>
              <span className="text-xs text-gray-500 font-medium tracking-wide -mt-1 group-hover:text-gray-600 transition-colors hidden sm:block">NYC RENTALS</span>
            </div>
          </Link>

          {/* Desktop & Mobile Action Buttons */}
          <div className="flex items-center space-x-3">
            {/* Get Free Guide Button - Desktop */}
            <button
              onClick={() => {
                // Will implement lead magnet modal
                const modal = document.createElement('div');
                modal.className = 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4';
                modal.innerHTML = `
                  <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
                    <div class="text-center">
                      <h2 class="text-2xl font-bold mb-4">🎉 Coming Soon!</h2>
                      <p class="text-gray-600 mb-4">Our comprehensive NYC Apartment Guide with 50+ no-fee contacts will be available soon.</p>
                      <p class="text-gray-600 mb-6">For now, call us directly for personalized help finding your perfect no-fee apartment!</p>
                      <a href="tel:646-408-8048" class="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors mr-3">📞 Call (646) 408-8048</a>
                      <button onclick="this.closest('.fixed').remove()" class="bg-gray-300 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-400 transition-colors">Close</button>
                    </div>
                  </div>
                `;
                document.body.appendChild(modal);
                modal.addEventListener('click', (e) => {
                  if (e.target === modal) modal.remove();
                });
              }}
              className="hidden lg:flex items-center bg-gradient-to-r from-orange-500 to-red-500 text-white px-4 py-2 rounded-lg text-sm font-bold hover:from-orange-600 hover:to-red-600 transform hover:scale-105 transition-all duration-300 shadow-md hover:shadow-lg hover:shadow-orange-500/20 active:scale-95"
            >
              <span className="flex items-center">
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                Free Guide
              </span>
            </button>

            {/* Get Free Guide Button - Mobile (Icon only) */}
            <button
              onClick={() => {
                const modal = document.createElement('div');
                modal.className = 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4';
                modal.innerHTML = `
                  <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
                    <div class="text-center">
                      <h2 class="text-2xl font-bold mb-4">🎉 Coming Soon!</h2>
                      <p class="text-gray-600 mb-4">Our comprehensive NYC Apartment Guide with 50+ no-fee contacts will be available soon.</p>
                      <p class="text-gray-600 mb-6">For now, call us directly for personalized help!</p>
                      <a href="tel:646-408-8048" class="bg-green-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-green-700 transition-colors mr-2 text-sm">📞 Call</a>
                      <button onclick="this.closest('.fixed').remove()" class="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg font-semibold hover:bg-gray-400 transition-colors text-sm">Close</button>
                    </div>
                  </div>
                `;
                document.body.appendChild(modal);
                modal.addEventListener('click', (e) => {
                  if (e.target === modal) modal.remove();
                });
              }}
              className="lg:hidden flex items-center justify-center bg-gradient-to-r from-orange-500 to-red-500 text-white p-2 rounded-lg hover:from-orange-600 hover:to-red-600 transform hover:scale-105 transition-all duration-300 shadow-md hover:shadow-lg hover:shadow-orange-500/20 active:scale-95"
              title="Get Free NYC Apartment Guide"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </button>

            {/* Sign In/Sign Up Button */}
            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-3 text-gray-700 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 rounded-lg px-3 py-2 transition-all duration-300 hover:bg-gray-50 hover:shadow-md transform hover:scale-105"
                >
                  <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                    {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
                  </div>
                  <span className="hidden md:block font-medium">{user?.full_name || 'User'}</span>
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* User Dropdown Menu */}
                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-2 z-50 border border-gray-200">
                    <Link to="/dashboard" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">Dashboard</Link>
                    <Link to="/favorites" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">Favorites</Link>
                    <Link to="/saved-searches" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">Saved Searches</Link>
                    <hr className="my-2 border-gray-200" />
                    <button 
                      onClick={logout}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <button 
                onClick={() => setShowAuthModal(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 md:px-6 md:py-2.5 rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 hover:shadow-lg shadow-md text-sm md:text-base hover:shadow-blue-500/20 active:scale-95"
              >
                <span className="flex items-center">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013 3v1" />
                  </svg>
                  <span className="hidden sm:inline">Sign In / Sign Up</span>
                  <span className="sm:hidden">Sign In</span>
                </span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* SEO Navigation Bar - Compact */}
      <div className="bg-gray-50 border-t border-gray-100">
        <div className="container mx-auto px-4 py-1.5">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-1">
            {/* No Broker Fee Apartments */}
            <div className="relative">
              <button
                onClick={() => toggleSection('noBrokerFee')}
                className="w-full p-1.5 text-left text-xs font-medium text-gray-700 hover:text-blue-600 transition-all duration-300 flex items-center justify-between hover:bg-blue-50 rounded-md transform hover:scale-105"
                title="No Fee NYC"
              >
                <span className="flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                  </svg>
                  No Fee
                </span>
                <svg className={`w-2.5 h-2.5 transition-transform ${expandedSections.noBrokerFee ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {expandedSections.noBrokerFee && (
                <div className="absolute top-full left-0 mt-1 w-80 bg-white rounded-lg shadow-lg border border-gray-200 p-4 z-50">
                  <p className="text-gray-700 text-sm mb-3">
                    Discover over 1,000 <strong>no fee apartments NYC</strong> and save up to $3,000+ in broker fees. Our verified 
                    <strong>NYC apartments no broker fee</strong> listings come directly from property owners.
                  </p>
                  <h4 className="font-semibold text-gray-900 mb-2 text-sm">Top NYC No Fee Neighborhoods:</h4>
                  <ul className="text-gray-700 text-xs space-y-1">
                    <li>• <strong>Manhattan:</strong> UES, Chelsea, Midtown West, Financial District</li>
                    <li>• <strong>Brooklyn:</strong> Williamsburg, DUMBO, Park Slope, Heights</li>
                    <li>• <strong>Queens:</strong> LIC, Astoria, Forest Hills, Ridgewood</li>
                  </ul>
                </div>
              )}
            </div>

            {/* Why Choose Us */}
            <div className="relative">
              <button
                onClick={() => toggleSection('whyChoose')}
                className="w-full p-1.5 text-left text-xs font-medium text-gray-700 hover:text-green-600 transition-all duration-300 flex items-center justify-between hover:bg-green-50 rounded-md transform hover:scale-105"
                title="Why Us?"
              >
                <span className="flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Why Us
                </span>
                <svg className={`w-2.5 h-2.5 transition-transform ${expandedSections.whyChoose ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {expandedSections.whyChoose && (
                <div className="absolute top-full left-0 mt-1 w-80 bg-white rounded-lg shadow-lg border border-gray-200 p-4 z-50">
                  <p className="text-gray-700 text-sm mb-3">
                    <strong>NoFeePlaces.com</strong> is NYC's #1 platform for <strong>no fee places NYC</strong> rentals. 
                    We specialize exclusively in <strong>New York no fee apartments</strong>.
                  </p>
                  <h4 className="font-semibold text-gray-900 mb-2 text-sm">Our Guarantee:</h4>
                  <ul className="text-gray-700 text-xs space-y-1">
                    <li>• 100% verified <strong>no fee rentals NYC</strong> listings</li>
                    <li>• Direct communication with property owners</li>
                    <li>• Expert NYC rental guidance from Chris Trunell</li>
                    <li>• Same-day apartment viewings available</li>
                  </ul>
                </div>
              )}
            </div>

            {/* Market Insights */}
            <div className="relative">
              <button
                onClick={() => toggleSection('marketInsights')}
                className="w-full p-1.5 text-left text-xs font-medium text-gray-700 hover:text-purple-600 transition-all duration-300 flex items-center justify-between hover:bg-purple-50 rounded-md transform hover:scale-105"
              >
                <span>Market 2025</span>
                <svg className={`w-2.5 h-2.5 transition-transform ${expandedSections.marketInsights ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {expandedSections.marketInsights && (
                <div className="absolute top-full left-0 mt-1 w-80 bg-white rounded-lg shadow-lg border border-gray-200 p-4 z-50">
                  <p className="text-gray-700 text-sm mb-3">
                    The 2025 NYC rental market shows increasing demand for <strong>no broker fee apartments NYC</strong>. 
                    Traditional broker fees range from 12-15% of annual rent.
                  </p>
                  <h4 className="font-semibold text-gray-900 mb-2 text-sm">Average Rent Ranges (No Fee):</h4>
                  <ul className="text-gray-700 text-xs space-y-1">
                    <li>• Manhattan: $2,800 - $8,500/month</li>
                    <li>• Brooklyn: $2,200 - $5,500/month</li>
                    <li>• Queens: $1,900 - $4,200/month</li>
                  </ul>
                </div>
              )}
            </div>

            {/* Contact & Expert Help */}
            <div className="relative">
              <button
                onClick={() => toggleSection('contact')}
                className="w-full p-1.5 text-left text-xs font-medium text-gray-700 hover:text-orange-600 transition-all duration-300 flex items-center justify-between hover:bg-orange-50 rounded-md transform hover:scale-105"
              >
                <span>Contact</span>
                <svg className={`w-2.5 h-2.5 transition-transform ${expandedSections.contact ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {expandedSections.contact && (
                <div className="absolute top-full right-0 mt-1 w-80 bg-white rounded-lg shadow-lg border border-gray-200 p-4 z-50">
                  <p className="text-gray-700 text-sm mb-3">
                    Ready to find your perfect <strong>no broker fee apartment NYC</strong>? Contact our NYC rental expert 
                    Chris Trunell for personalized assistance.
                  </p>
                  <h4 className="font-semibold text-gray-900 mb-2 text-sm">Contact Information:</h4>
                  <ul className="text-gray-700 text-xs space-y-1">
                    <li>• Phone: (646) 408-8048</li>
                    <li>• Email: chris@places.nyc</li>
                    <li>• Response Time: Under 2 hours</li>
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

// Professional Hero Section
const Hero = () => {
  return (
    <>
      <section 
        className="relative py-20 md:py-32 lg:py-40 overflow-hidden"
        style={{
          backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), url('https://images.pexels.com/photos/28426361/pexels-photo-28426361.jpeg?auto=compress&cs=tinysrgb&w=2340&h=1560')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center center',
          backgroundRepeat: 'no-repeat'
        }}
      >
        <div className="container mx-auto px-4 md:px-6 text-center relative z-10 h-full flex flex-col justify-center">
          <div>
            <h1 className="font-philosopher text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-8 drop-shadow-lg leading-tight">
              No Fee Apartments in NYC
            </h1>
          </div>
        </div>
      </section>
    </>
  );
};

// Simplified SEO Content Section - Just the main heading and CTA
const SEOContentSection = () => {
  const { isAuthenticated } = useAuth();

  return (
    <section className="bg-white py-6 md:py-8">
      <div className="container mx-auto px-4 md:px-6">
        <div className="max-w-6xl mx-auto text-center">
          <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold text-gray-900 mb-4 md:mb-6">
            {isAuthenticated ? 'Find Your Perfect No Fee Apartment in New York City 2025' : (
              <span className="font-philosopher text-gray-900">
                Browse No Fee Apartments NYC
              </span>
            )}
          </h2>
        </div>
      </div>
    </section>
  );
};

// Professional Search Filters Component
const AdvancedSearchFilters = ({ filters, onFilterChange, apartmentCount }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleFilterChange = (key, value) => {
    onFilterChange(key, value);
  };

  return (
    <div className="bg-white border-b border-gray-200 sticky top-16 z-40">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-center mb-4">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-blue-600 hover:text-blue-700 font-medium text-sm flex items-center transition-all duration-300 hover:bg-blue-50 px-3 py-2 rounded-lg transform hover:scale-105"
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

        {/* Quick Filters - Always Visible and Centered */}
        <div className="flex flex-wrap gap-3 items-center justify-center">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Location:</label>
            <input
              type="text"
              placeholder="Enter neighborhood"
              value={filters.neighborhood || ''}
              onChange={(e) => handleFilterChange('neighborhood', e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
          </div>

          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Max Price:</label>
            <select
              value={filters.max_price || ''}
              onChange={(e) => handleFilterChange('max_price', e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
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
            <label className="text-sm font-medium text-gray-700">Bedrooms:</label>
            <select
              value={filters.bedrooms || ''}
              onChange={(e) => handleFilterChange('bedrooms', e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              <option value="">Any</option>
              <option value="0">Studio</option>
              <option value="1">1 Bedroom</option>
              <option value="2">2+ Bedrooms</option>
            </select>
          </div>
        </div>

        {/* Expanded Filters */}
        {isExpanded && (
          <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Borough</label>
              <select
                value={filters.borough || ''}
                onChange={(e) => handleFilterChange('borough', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
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
              <label className="block text-sm font-medium text-gray-700 mb-2">Bathrooms</label>
              <select
                value={filters.bathrooms || ''}
                onChange={(e) => handleFilterChange('bathrooms', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="">Any</option>
                <option value="1">1+ Bathroom</option>
                <option value="2">2+ Bathrooms</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
              <select
                value={filters.sort_by || ''}
                onChange={(e) => handleFilterChange('sort_by', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
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
            className="btn-primary px-6 py-3 transition-all duration-300 transform hover:scale-105 hover:shadow-lg active:scale-95"
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
        className="ml-4 hover:opacity-70 transition-all duration-300 transform hover:scale-110 active:scale-95"
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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-lg">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Contact Agent</h3>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-all duration-300 transform hover:scale-110 hover:bg-gray-100 p-1 rounded active:scale-95"
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
            <p className="text-gray-600">Chris will get back to you within 24 hours.</p>
          </div>
        ) : (
          <>
            <div className="mb-4 p-3 bg-gray-50 rounded-lg">
              <h4 className="font-semibold text-gray-900">{apartment?.title}</h4>
              <p className="text-sm text-gray-600">{apartment?.address}</p>
              <p className="text-sm font-semibold text-gray-900">${apartment?.price?.toLocaleString()}/month</p>
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
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all duration-300 transform hover:scale-105 hover:shadow-md active:scale-95"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={sending}
                  className="flex-1 bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 disabled:bg-orange-400 transition-all duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-orange-500/20 active:scale-95"
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
            className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-60 hover:bg-opacity-80 text-white rounded-full p-2 opacity-0 group-hover:opacity-100 transition-all duration-300 shadow-lg hover:scale-110 active:scale-95"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button
            onClick={nextImage}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-60 hover:bg-opacity-80 text-white rounded-full p-2 opacity-0 group-hover:opacity-100 transition-all duration-300 shadow-lg hover:scale-110 active:scale-95"
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
              className={`w-2 h-2 rounded-full transition-all duration-300 hover:scale-125 active:scale-95 ${
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
  const [showSocialShare, setShowSocialShare] = useState(false);

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
    // Analytics tracking will be added back later
    navigate(`/apartment/${apartment.id}`);
  };

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 overflow-hidden border border-gray-200">
      <div className="relative cursor-pointer" onClick={handleViewDetails}>
        <ImageCarousel
          images={apartment.images || [apartment.image]}
          alt={apartment.title}
          className="w-full h-48 object-cover hover:opacity-95 transition-opacity duration-200"
        />
        
        {/* No Fee Badge */}
        <div className="absolute top-3 right-3 z-10">
          <span className="bg-green-600 text-white text-xs font-medium px-2 py-1 rounded shadow-lg">
            NO FEE
          </span>
        </div>
        
        {/* Favorite Button */}
        <div className="absolute top-3 right-16 z-10">
          <button 
            onClick={handleFavorite}
            className="bg-white bg-opacity-90 hover:bg-opacity-100 p-2 rounded-full shadow-md transition-all duration-300 transform hover:scale-110 hover:shadow-lg active:scale-95"
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
          <div className="bg-white bg-opacity-95 px-3 py-1 rounded shadow-md">
            <span className="text-lg font-bold text-gray-900">
              ${apartment.price?.toLocaleString() || apartment.price}
            </span>
            <span className="text-gray-600 text-sm">/mo</span>
          </div>
        </div>
      </div>

      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">{apartment.title}</h3>
        <p className="text-gray-600 text-sm mb-3 flex items-center justify-between">
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {/* Address - show full address if authenticated, otherwise show neighborhood */}
            {isAuthenticated ? apartment.address : `${apartment.neighborhood}, ${apartment.borough}`}
          </span>
        </p>

        {/* Property Details */}
        <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
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
          <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
            {isAuthenticated ? (
              <>
                <button
                  onClick={() => window.open(`tel:${apartment.contact_info?.phone}`, '_self')}
                  className="flex items-center justify-center bg-green-600 text-white px-3 py-2 rounded hover:bg-green-700 transition-all duration-300 text-sm font-medium transform hover:scale-105 hover:shadow-lg hover:shadow-green-500/20 active:scale-95"
                >
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  Call
                </button>
                <button
                  onClick={() => setShowEmailModal(true)}
                  className="flex items-center justify-center bg-green-600 text-white px-3 py-2 rounded hover:bg-green-700 transition-all duration-300 text-sm font-medium transform hover:scale-105 hover:shadow-lg hover:shadow-green-500/20 active:scale-95"
                >
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 7.89a1 1 0 001.42 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Email
                </button>
              </>
            ) : (
              <button
                onClick={() => setShowAuthModal(true)}
                className="flex items-center justify-center bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-all duration-300 text-sm font-medium w-full transform hover:scale-105 hover:shadow-lg hover:shadow-blue-500/20 active:scale-95"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v-2l-4-4L7.257 8.743A6 6 0 0117 9z" />
                </svg>
                Sign Up for Full Address
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Social Share Section - Placeholder for now */}
      <div className="border-t pt-3 mt-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">Share this apartment:</span>
            <a 
              href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(window.location.origin + '/apartment/' + apartment.id)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-700 transition-all duration-300 transform hover:scale-110 hover:bg-blue-50 px-2 py-1 rounded active:scale-95"
            >
              📘 Facebook
            </a>
            <a 
              href={`https://twitter.com/intent/tweet?url=${encodeURIComponent(window.location.origin + '/apartment/' + apartment.id)}&text=Check out this ${apartment.bedrooms}BR in ${apartment.neighborhood} - No Broker Fees!`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-500 transition-all duration-300 transform hover:scale-110 hover:bg-blue-50 px-2 py-1 rounded active:scale-95"
            >
              🐦 Twitter
            </a>
            <a 
              href={`https://wa.me/?text=Check out this ${apartment.bedrooms}BR in ${apartment.neighborhood} - No Broker Fees! ${window.location.origin}/apartment/${apartment.id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-green-600 hover:text-green-700 transition-all duration-300 transform hover:scale-110 hover:bg-green-50 px-2 py-1 rounded active:scale-95"
            >
              💬 WhatsApp
            </a>
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

// Modern Calendar Booking Component
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

  // Modern calendar date generation
  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay()); // Start from Sunday
    
    const days = [];
    const currentDate = new Date(startDate);
    
    // Generate 42 days (6 weeks) for consistent calendar grid
    for (let i = 0; i < 42; i++) {
      const day = new Date(currentDate);
      const isCurrentMonth = day.getMonth() === month;
      const isToday = day.toDateString() === new Date().toDateString();
      const isPast = day < new Date().setHours(0, 0, 0, 0);
      const isSelected = selectedDate && day.toDateString() === selectedDate.toDateString();
      
      days.push({
        date: day,
        dayNumber: day.getDate(),
        isCurrentMonth,
        isToday,
        isPast,
        isSelected,
        dateString: day.toISOString().split('T')[0]
      });
      
      currentDate.setDate(currentDate.getDate() + 1);
    }
    
    return days;
  };

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  const weekDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

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
    setLoading(true);
    try {
      const dateString = selectedDate.toISOString().split('T')[0];
      const response = await axios.get(`${API}/apartments/${apartmentId}/available-slots?date=${dateString}`);
      setAvailableSlots(response.data.available_slots);
    } catch (error) {
      console.error('Error fetching available slots:', error);
      setAvailableSlots([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDateSelect = (day) => {
    if (day.isPast || !day.isCurrentMonth) return;
    setSelectedDate(day.date);
    setSelectedTime('');
    setShowBookingForm(false);
  };

  const handleTimeSelect = (time) => {
    setSelectedTime(time);
    setShowBookingForm(true);
  };

  const handleBookingSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const appointmentData = {
        apartment_id: apartmentId,
        appointment_date: selectedDate.toISOString().split('T')[0],
        appointment_time: selectedTime,
        ...bookingData
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
      
      if (onBookingComplete) {
        onBookingComplete(response.data);
      }

      // Show success notification
      if (toast) {
        toast.success('Appointment scheduled! Calendar invite sent to your email and our agent.');
      } else {
        alert('Appointment scheduled! Calendar invite sent to your email and our agent.');
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to book appointment';
      
      // Show error notification
      if (toast) {
        toast.error(errorMessage);
      } else {
        alert(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const days = getDaysInMonth(currentMonth);

  return (
    <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-lg">
      <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
        <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center mr-3">
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        Schedule Your Viewing
      </h3>

      {/* Modern Calendar Header */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={previousMonth}
          className="p-2 hover:bg-gray-100 rounded-xl transition-all duration-300 transform hover:scale-110 hover:shadow-md active:scale-95"
        >
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        
        <h4 className="text-xl font-semibold text-gray-900">
          {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
        </h4>
        
        <button
          onClick={nextMonth}
          className="p-2 hover:bg-gray-100 rounded-xl transition-all duration-300 transform hover:scale-110 hover:shadow-md active:scale-95"
        >
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      {/* Week Day Headers */}
      <div className="grid grid-cols-7 gap-1 mb-2">
        {weekDays.map(day => (
          <div key={day} className="text-center py-2 text-sm font-medium text-gray-500">
            {day}
          </div>
        ))}
      </div>

      {/* Modern Calendar Grid */}
      <div className="grid grid-cols-7 gap-1 mb-6">
        {days.map((day, index) => (
          <button
            key={index}
            onClick={() => handleDateSelect(day)}
            disabled={day.isPast || !day.isCurrentMonth}
            className={`
              h-12 w-full text-sm rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-md active:scale-95
              ${day.isCurrentMonth 
                ? day.isPast
                  ? 'text-gray-300 cursor-not-allowed'
                  : day.isSelected
                    ? 'bg-blue-600 text-white shadow-lg transform scale-105'
                    : day.isToday
                      ? 'bg-blue-100 text-blue-800 font-bold hover:bg-blue-200 hover:shadow-blue-200/50'
                      : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900 hover:shadow-gray-200/50'
                : 'text-gray-300'
              }
            `}
          >
            {day.dayNumber}
          </button>
        ))}
      </div>

      {/* Selected Date Display */}
      {selectedDate && (
        <div className="mb-6 p-4 bg-blue-50 rounded-xl border border-blue-200">
          <p className="text-blue-800 font-medium text-center">
            Selected: {selectedDate.toLocaleDateString('en-US', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </p>
        </div>
      )}

      {/* Time Selection */}
      {selectedDate && (
        <div className="mb-6">
          <label className="block text-sm font-semibold text-gray-700 mb-3">Available Times</label>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-2 text-gray-600">Loading available times...</span>
            </div>
          ) : availableSlots.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {availableSlots.map(slot => (
                <button
                  key={slot}
                  onClick={() => handleTimeSelect(slot)}
                  className={`
                    py-3 px-4 rounded-xl text-sm font-medium transition-all duration-300 hover:shadow-md active:scale-95
                    ${selectedTime === slot
                      ? 'bg-blue-600 text-white shadow-lg transform scale-105'
                      : 'bg-gray-50 text-gray-700 hover:bg-blue-50 hover:text-blue-700 hover:scale-105 hover:shadow-blue-200/50'
                    }
                  `}
                >
                  {slot}
                </button>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              No available slots for this date
            </div>
          )}
        </div>
      )}

      {/* Modern Booking Form */}
      {showBookingForm && (
        <div className="border-t border-gray-200 pt-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Booking Details</h4>
          <form onSubmit={handleBookingSubmit} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                <input
                  type="text"
                  required
                  value={bookingData.visitor_name}
                  onChange={(e) => setBookingData({...bookingData, visitor_name: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  placeholder="Enter your full name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
                <input
                  type="email"
                  required
                  value={bookingData.visitor_email}
                  onChange={(e) => setBookingData({...bookingData, visitor_email: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  placeholder="Enter your email"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
              <input
                type="tel"
                required
                value={bookingData.visitor_phone}
                onChange={(e) => setBookingData({...bookingData, visitor_phone: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                placeholder="Enter your phone number"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Notes (Optional)</label>
              <textarea
                value={bookingData.notes}
                onChange={(e) => setBookingData({...bookingData, notes: e.target.value})}
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-none"
                placeholder="Any specific requirements or questions..."
              />
            </div>
            <div className="flex gap-3 pt-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-xl font-semibold hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-blue-500/20 transform hover:scale-105 active:scale-95"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Booking...
                  </span>
                ) : 'Confirm Booking'}
              </button>
              <button
                type="button"
                onClick={() => setShowBookingForm(false)}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-all duration-300 transform hover:scale-105 hover:shadow-md active:scale-95"
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
      const response = await axios.get(`${API}/apartments?limit=100`);
      setApartments(response.data);
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
              className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-all duration-300 transform hover:scale-105 hover:shadow-md active:scale-95"
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
                              className="bg-green-600 text-white px-3 py-1 rounded text-xs hover:bg-green-700 transition-all duration-300 transform hover:scale-105 hover:shadow-md hover:shadow-green-500/20 active:scale-95"
                            >
                              Confirm
                            </button>
                            <button
                              onClick={() => updateAppointmentStatus(appointment.id, 'cancelled')}
                              className="bg-red-600 text-white px-3 py-1 rounded text-xs hover:bg-red-700 transition-all duration-300 transform hover:scale-105 hover:shadow-md hover:shadow-red-500/20 active:scale-95"
                            >
                              Cancel
                            </button>
                          </div>
                        )}
                        {appointment.status === 'confirmed' && (
                          <button
                            onClick={() => updateAppointmentStatus(appointment.id, 'completed')}
                            className="bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700 transition-all duration-300 transform hover:scale-105 hover:shadow-md hover:shadow-blue-500/20 active:scale-95"
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

// Authentication Modal Component with PLACES styling
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
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 shadow-lg">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            {isLogin ? 'Sign In to Places' : 'Join Places'}
          </h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-all duration-300 transform hover:scale-110 hover:bg-gray-100 p-1 rounded active:scale-95"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
              <input
                type="text"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
                value={formData.fullName}
                onChange={(e) => setFormData(prev => ({...prev, fullName: e.target.value}))}
              />
            </div>
          )}

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
            <input
              type="email"
              required
              placeholder="your.email@example.com"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
              value={formData.email}
              onChange={(e) => setFormData(prev => ({...prev, email: e.target.value}))}
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <input
              type="password"
              required
              placeholder="Enter your password"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none"
              value={formData.password}
              onChange={(e) => setFormData(prev => ({...prev, password: e.target.value}))}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-orange-500 text-white py-2 px-4 rounded-lg hover:bg-orange-600 disabled:bg-orange-400 transition-all duration-300 font-medium transform hover:scale-105 hover:shadow-lg hover:shadow-orange-500/20 active:scale-95"
          >
            {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        <div className="text-center mt-6">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-orange-500 hover:text-orange-600 text-sm font-medium transition-all duration-300 hover:bg-orange-50 px-3 py-2 rounded-lg transform hover:scale-105 active:scale-95"
          >
            {isLogin ? "Don't have an account? Join Places" : "Already have an account? Sign in"}
          </button>
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
    if (apartment?.contact_info?.phone) {
      // Open phone dialer
      window.open(`tel:${apartment.contact_info.phone}`, '_self');
    } else {
      setShowContactModal(true);
    }
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

              {/* Contact Info */}
              <div>
                <div className="bg-slate-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-slate-800 mb-4">Contact Information</h3>
                  
                  {apartment.contact_info && (
                    <div className="space-y-3 mb-6">
                      {apartment.contact_info.phone && (
                        <div className="flex items-center">
                          <svg className="w-5 h-5 text-slate-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                          </svg>
                          <span className="text-slate-700">{apartment.contact_info.phone}</span>
                        </div>
                      )}
                      
                      {apartment.contact_info.email && (
                        <div className="flex items-center">
                          <svg className="w-5 h-5 text-slate-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          </svg>
                          <span className="text-slate-700">{apartment.contact_info.email}</span>
                        </div>
                      )}

                      {apartment.contact_info.broker && (
                        <div className="flex items-center">
                          <svg className="w-5 h-5 text-slate-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                          </svg>
                          <span className="text-slate-700">{apartment.contact_info.broker}</span>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="grid grid-cols-1 gap-3">
                    {/* Primary Action - Call Button */}
                    <button 
                      onClick={handleContactAgent}
                      className="flex items-center justify-center w-full bg-blue-600 hover:bg-blue-700 text-white py-4 px-6 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
                    >
                      <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                      Call Agent Now
                    </button>

                    {/* Secondary Actions Grid */}
                    <div className="grid grid-cols-2 gap-3">
                      {/* Email Button */}
                      <button 
                        onClick={handleEmailContact}
                        className="flex items-center justify-center bg-indigo-600 hover:bg-indigo-700 text-white py-3 px-4 rounded-lg font-medium shadow-md hover:shadow-lg transition-all duration-200 transform hover:scale-105"
                      >
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        <span className="hidden sm:inline">Send Email</span>
                        <span className="sm:hidden">Email</span>
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
                        onClick={() => window.open(`sms:${apartment.contact_info?.phone}`, '_self')}
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
                <span>placesnyc88@gmail.com</span>
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
        contextInfo += `\n\nCurrent apartment context: ${apartmentContext.title} at ${apartmentContext.address}, ${apartmentContext.bedrooms === 0 ? 'Studio' : apartmentContext.bedrooms + ' bedroom'} for $${apartmentContext.price}/month. Amenities: ${apartmentContext.amenities?.join(', ') || 'N/A'}. Contact: Chris Trunell at (646) 408-8048 or placesnyc88@gmail.com.`;
      }
      
      contextInfo += "\n\nAlways be helpful, professional, and encouraging. If asked about specific apartments not in context, suggest they browse our full listings at nofeeplaces.com or contact Chris directly.";

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
        content: 'Sorry, I\'m having trouble connecting right now. Please try calling Chris at (646) 408-8048 for immediate assistance with your rental needs.', 
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

  const handleQuickPrompt = (promptText) => {
    if (isLoading) return;
    
    setInputMessage(promptText);
    
    // Add user message to chat
    setMessages(prev => [...prev, { 
      type: 'user', 
      content: promptText, 
      timestamp: new Date() 
    }]);

    setIsLoading(true);

    // Send the prompt message
    const sendQuickPrompt = async () => {
      try {
        // Create enhanced context for AI
        let contextInfo = "You are an AI assistant for NoFeePlaces.com, a no-fee apartment rental platform in NYC. You help users with apartment searches, rental information, and scheduling viewings. ";
        
        if (apartmentContext) {
          contextInfo += `\n\nCurrent apartment context: ${apartmentContext.title} at ${apartmentContext.address}, ${apartmentContext.bedrooms === 0 ? 'Studio' : apartmentContext.bedrooms + ' bedroom'} for $${apartmentContext.price}/month. Amenities: ${apartmentContext.amenities?.join(', ') || 'N/A'}. Contact: Chris Trunell at (646) 408-8048 or placesnyc88@gmail.com.`;
        } else {
          contextInfo += "\n\nGeneral assistance context: NoFeePlaces.com offers no-fee apartments across NYC (Manhattan, Brooklyn, Queens). Contact Chris Trunell at (646) 408-8048 or placesnyc88@gmail.com for personalized help.";
        }

        const response = await axios.post(`${API}/chat`, {
          message: promptText,
          context: contextInfo,
          sessionId: sessionId
        });

        if (response.data.sessionId && !sessionId) {
          setSessionId(response.data.sessionId);
        }

        // Add AI response to chat
        setMessages(prev => [...prev, { 
          type: 'ai', 
          content: response.data.response, 
          timestamp: new Date() 
        }]);

      } catch (error) {
        console.error('Error in quick prompt:', error);
        setMessages(prev => [...prev, { 
          type: 'ai', 
          content: "I'm having trouble connecting right now. Please call Chris directly at (646) 408-8048 for immediate assistance with your apartment search!", 
          timestamp: new Date() 
        }]);
      } finally {
        setIsLoading(false);
        setInputMessage('');
      }
    };

    sendQuickPrompt();
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
      {/* Chat Toggle Button - Orange and Prominent */}
      <div className="fixed bottom-20 right-8 z-[60]">
        <button
          onClick={toggleChat}
          className={`rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center transform hover:scale-110 active:scale-95 ${
            isOpen 
              ? 'w-16 h-16 bg-gray-500 hover:bg-gray-600' 
              : 'w-24 h-24 bg-orange-500 hover:bg-orange-600 animate-pulse'
          }`}
          style={{ boxShadow: isOpen ? '0 4px 15px rgba(0, 0, 0, 0.2)' : '0 10px 30px rgba(0, 0, 0, 0.3)' }}
        >
          {isOpen ? (
            <div className="flex flex-col items-center justify-center">
              <svg className="w-4 h-4 text-white mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
              <span className="text-xs text-white font-medium">Close</span>
            </div>
          ) : (
            <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          )}
        </button>
        
        {/* Help text bubble when closed */}
        {!isOpen && (
          <div className="absolute bottom-full right-2 mb-3 bg-orange-500 text-white px-4 py-2 rounded-lg text-sm whitespace-nowrap animate-bounce shadow-lg">
            Ask me anything!
          </div>
        )}
      </div>

      {/* Chat Window - Orange Theme */}
      {isOpen && (
        <div className="fixed bottom-48 right-8 w-96 h-[500px] bg-white rounded-2xl shadow-xl border border-gray-200 z-50 flex flex-col">
          {/* Chat Header */}
          <div className="flex items-center justify-between p-4 bg-orange-500 rounded-t-2xl">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-orange-600 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">Places Assistant</h3>
                <p className="text-xs text-orange-100">Ask me anything about rentals</p>
              </div>
            </div>
            
            {/* Subtle Close Button */}
            <button
              onClick={toggleChat}
              className="text-white hover:text-orange-200 transition-all duration-300 px-2 py-1 rounded text-xs font-medium hover:bg-orange-600 hover:bg-opacity-30 transform hover:scale-105 active:scale-95"
              aria-label="Close chat"
            >
              Close
            </button>
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
                    <div className="w-2 h-2 bg-orange-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-orange-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-orange-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompt Buttons */}
          {messages.length === 0 && (
            <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
              <p className="text-xs text-gray-600 mb-2">Quick questions:</p>
              <div className="grid grid-cols-1 gap-1">
                <button
                  onClick={() => handleQuickPrompt("Help me with the leasing process - what documents do I need?")}
                  className="text-left text-xs bg-white hover:bg-orange-50 text-gray-700 hover:text-orange-600 px-3 py-2 rounded-lg border hover:border-orange-200 transition-all duration-300 transform hover:scale-105 hover:shadow-md active:scale-95"
                  disabled={isLoading}
                >
                  📋 Leasing Process
                </button>
                <button
                  onClick={() => handleQuickPrompt("What should I know about moving into a no-fee apartment?")}
                  className="text-left text-xs bg-white hover:bg-orange-50 text-gray-700 hover:text-orange-600 px-3 py-2 rounded-lg border hover:border-orange-200 transition-all duration-300 transform hover:scale-105 hover:shadow-md active:scale-95"
                  disabled={isLoading}
                >
                  📦 Moving In Tips
                </button>
                <button
                  onClick={() => handleQuickPrompt("Walk me through the lease signing process for NYC apartments")}
                  className="text-left text-xs bg-white hover:bg-orange-50 text-gray-700 hover:text-orange-600 px-3 py-2 rounded-lg border hover:border-orange-200 transition-all duration-300 transform hover:scale-105 hover:shadow-md active:scale-95"
                  disabled={isLoading}
                >
                  ✍️ Lease Signing
                </button>
                <button
                  onClick={() => handleQuickPrompt("Show me the best no-fee apartment deals available right now")}
                  className="text-left text-xs bg-white hover:bg-orange-50 text-gray-700 hover:text-orange-600 px-3 py-2 rounded-lg border hover:border-orange-200 transition-all duration-300 transform hover:scale-105 hover:shadow-md active:scale-95"
                  disabled={isLoading}
                >
                  💰 Best Deals
                </button>
                <button
                  onClick={() => handleQuickPrompt("I'm looking for luxury no-fee apartments in NYC - what options do you have?")}
                  className="text-left text-xs bg-white hover:bg-orange-50 text-gray-700 hover:text-orange-600 px-3 py-2 rounded-lg border hover:border-orange-200 transition-all duration-300 transform hover:scale-105 hover:shadow-md active:scale-95"
                  disabled={isLoading}
                >
                  ✨ Luxury No Fee
                </button>
              </div>
            </div>
          )}

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
                className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg text-sm transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 hover:shadow-lg hover:shadow-orange-500/20 active:scale-95"
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
                className="btn-primary px-4 py-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 hover:shadow-lg active:scale-95"
              >
                Compare Selected
              </button>
              <button
                onClick={() => setSelectedForComparison([])}
                className="text-slate-500 hover:text-slate-700 text-sm transition-all duration-300 hover:bg-slate-100 px-3 py-2 rounded-lg transform hover:scale-105 active:scale-95"
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
                          onClick={() => window.open(`tel:${apartment.contact_info?.phone}`, '_self')}
                          className="bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-500 transition-colors text-xs font-medium hover-lift flex items-center"
                        >
                          <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                          </svg>
                          Call
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
              Get expert guidance from Chris Trunell, NYC's leading no fee apartment specialist.
            </p>
            <div className="space-y-4">
              <div className="flex justify-center space-x-6 text-lg">
                <div>📞 (646) 408-8048</div>
                <div>📧 chris@places.nyc</div>
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
  AdminAppointments,
  AIChatbot,
  FavoritesPage,
  ApartmentComparison,
  ErrorBoundary,
  LazyImage,
  EmailContactModal,
  CompleteGuideNoFeeApartments
};
