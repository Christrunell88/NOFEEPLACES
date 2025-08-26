import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuth } from './App';
import { Link, useNavigate } from 'react-router-dom';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Header Component with New PLACES Branding
// Professional Header Component
const Header = ({ isAuthenticated, user, logout, setShowAuthModal }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 bg-white border-b border-gray-200 z-50 shadow-sm">
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
                <span className="text-2xl font-bold text-gray-900 tracking-tight group-hover:text-gray-800 transition-colors">No Fee</span>
                <span className="text-lg font-semibold text-orange-500 group-hover:text-orange-600 transition-colors">Places</span>
              </div>
              <span className="text-xs text-gray-500 font-medium tracking-wide -mt-1 group-hover:text-gray-600 transition-colors">NYC RENTALS</span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <Link to="/dashboard" className="text-gray-600 hover:text-gray-900 transition-colors font-medium">Dashboard</Link>
                <Link to="/favorites" className="text-gray-600 hover:text-gray-900 transition-colors font-medium">Favorites</Link>
                <Link to="/saved-searches" className="text-gray-600 hover:text-gray-900 transition-colors font-medium">Saved Searches</Link>
                <div className="relative group">
                  <button className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors">
                    <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                      {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
                    </div>
                    <span className="font-medium">{user?.full_name?.split(' ')[0] || 'User'}</span>
                  </button>
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                    <div className="py-2">
                      <Link to="/dashboard" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">Dashboard</Link>
                      <Link to="/favorites" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">Favorites</Link>
                      <Link to="/saved-searches" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">Saved Searches</Link>
                      <button 
                        onClick={logout}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                      >
                        Sign Out
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <button 
                onClick={() => setShowAuthModal(true)}
                className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors font-medium"
              >
                Sign In
              </button>
            )}
          </nav>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 text-gray-600 hover:text-gray-900"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 py-4">
            <div className="flex flex-col space-y-3">
              {isAuthenticated ? (
                <>
                  <Link to="/dashboard" className="text-gray-600 hover:text-gray-900 transition-colors font-medium">Dashboard</Link>
                  <Link to="/favorites" className="text-gray-600 hover:text-gray-900 transition-colors font-medium">Favorites</Link>
                  <Link to="/saved-searches" className="text-gray-600 hover:text-gray-900 transition-colors font-medium">Saved Searches</Link>
                  <button 
                    onClick={logout}
                    className="text-left text-gray-600 hover:text-gray-900 transition-colors font-medium"
                  >
                    Sign Out
                  </button>
                </>
              ) : (
                <button 
                  onClick={() => setShowAuthModal(true)}
                  className="bg-orange-500 text-white px-4 py-2 rounded-lg w-fit font-medium"
                >
                  Sign In
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

// Professional Hero Section
const Hero = ({ onSearchSubmit }) => {
  const [searchLocation, setSearchLocation] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (onSearchSubmit) {
      onSearchSubmit({ location: searchLocation });
    }
  };

  return (
    <section 
      className="relative py-32 md:py-40 overflow-hidden"
      style={{
        backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.3)), url('https://images.pexels.com/photos/28426361/pexels-photo-28426361.jpeg?auto=compress&cs=tinysrgb&w=2340&h=1560')`,
        backgroundSize: 'cover',
        backgroundPosition: 'center center',
        backgroundRepeat: 'no-repeat'
      }}
    >
      <div className="container mx-auto px-4 text-center relative z-10 h-full flex flex-col justify-center">
        <div className="mb-20">
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 drop-shadow-lg">
            No Fee Apartments in NYC
          </h1>
          <p className="text-xl md:text-2xl text-white max-w-3xl mx-auto drop-shadow-md leading-relaxed">
            Discover luxury <strong>no broker fee apartments NYC</strong> across Manhattan, Brooklyn, and Queens. 
            Browse exclusive <strong>no fee rentals NYC</strong> directly from property owners and management companies.
          </p>
        </div>

        {/* Search Bar - Positioned Lower */}
        <div className="max-w-2xl mx-auto">
          <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-4 p-6 bg-white/95 backdrop-blur-sm rounded-xl shadow-2xl border border-white/20">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search no fee apartments by neighborhood, address, or subway stop..."
                value={searchLocation}
                onChange={(e) => setSearchLocation(e.target.value)}
                className="w-full px-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-lg"
              />
            </div>
            <button
              type="submit"
              className="bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 transition-all duration-200 font-semibold whitespace-nowrap shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              Search Apartments
            </button>
          </form>
        </div>
      </div>
    </section>
  );
};

// SEO Content Section Component
const SEOContentSection = () => {
  return (
    <section className="bg-white py-16">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-8">
            Find Your Perfect No Fee Apartment in New York City
          </h2>
          
          <div className="grid md:grid-cols-2 gap-8 text-left">
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">No Broker Fee Apartments NYC</h3>
              <p className="text-gray-700 leading-relaxed mb-6">
                Skip the broker fees and save thousands on your next apartment rental. Our platform connects you directly 
                with <strong>NYC apartments no broker fee</strong> from verified property owners and management companies 
                across all five boroughs.
              </p>
              
              <h4 className="text-lg font-semibold text-gray-900 mb-3">Popular Neighborhoods:</h4>
              <ul className="text-gray-700 space-y-2">
                <li>• Manhattan: Upper East Side, Chelsea, Midtown West, Financial District</li>
                <li>• Brooklyn: Williamsburg, DUMBO, Park Slope, Bedford-Stuyvesant</li>
                <li>• Queens: Long Island City, Astoria, Forest Hills, Ridgewood</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Why Choose No Fee Places NYC?</h3>
              <p className="text-gray-700 leading-relaxed mb-6">
                <strong>No fee places NYC</strong> specializes in <strong>New York no fee apartments</strong> that 
                eliminate expensive broker fees. Every listing is verified, and our expert team helps you secure 
                your dream apartment without the traditional NYC rental hassles.
              </p>
              
              <h4 className="text-lg font-semibold text-gray-900 mb-3">Our Promise:</h4>
              <ul className="text-gray-700 space-y-2">
                <li>• 100% verified <strong>no fee rentals NYC</strong></li>
                <li>• Direct contact with property owners</li>
                <li>• Expert guidance from Chris Trunell</li>
                <li>• Same-day apartment viewings available</li>
                <li>• No hidden fees or surprise charges</li>
              </ul>
            </div>
          </div>
          
          <div className="mt-12 p-6 bg-blue-50 rounded-lg">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Ready to Find Your No Fee Apartment?</h3>
            <p className="text-gray-700 mb-4">
              Browse our exclusive collection of <strong>no broker fee apartments NYC</strong> and schedule viewings today. 
              Contact our expert agent Chris Trunell at (646) 408-8048 or placesnyc88@gmail.com for personalized assistance.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

// Professional Search Filters Component
const AdvancedSearchFilters = ({ filters, onFilterChange, apartmentCount }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleFilterChange = (key, value) => {
    onFilterChange({
      ...filters,
      [key]: value
    });
  };

  return (
    <div className="bg-white border-b border-gray-200 sticky top-16 z-40">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            {apartmentCount || 0} No Fee Apartments Available
          </h2>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-blue-600 hover:text-blue-700 font-medium text-sm flex items-center"
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

        {/* Quick Filters - Always Visible */}
        <div className="flex flex-wrap gap-3 items-center">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Location:</label>
            <input
              type="text"
              placeholder="Enter neighborhood"
              value={filters.location || ''}
              onChange={(e) => handleFilterChange('location', e.target.value)}
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
const ApartmentCard = ({ apartment }) => {
  const [isFavorited, setIsFavorited] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();

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
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 overflow-hidden border border-gray-200">
      <div className="relative">
        <LazyImage
          src={apartment.images?.[0] || apartment.image}
          alt={apartment.title}
          className="w-full h-48 object-cover"
        />
        
        {/* No Fee Badge */}
        <div className="absolute top-3 left-3">
          <span className="bg-green-600 text-white text-xs font-medium px-2 py-1 rounded">
            NO FEE
          </span>
        </div>
        
        {/* Favorite Button */}
        <div className="absolute top-3 right-3">
          <button 
            onClick={handleFavorite}
            className="bg-white bg-opacity-90 hover:bg-opacity-100 p-2 rounded-full shadow-md transition-all"
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
        <p className="text-gray-600 text-sm mb-3 flex items-center">
          <svg className="w-4 h-4 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          {/* Address - only show if user is authenticated */}
          {isAuthenticated ? apartment.address : `${apartment.neighborhood}, ${apartment.borough}`}
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
        <div className="flex justify-between items-center pt-3 border-t border-gray-200">
          <div className="flex space-x-2">
            <button
              onClick={() => window.open(`tel:${apartment.contact_info?.phone}`, '_self')}
              className="flex items-center bg-green-600 text-white px-3 py-2 rounded hover:bg-green-700 transition-colors text-sm font-medium"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              Call
            </button>
            <button
              onClick={() => setShowEmailModal(true)}
              className="flex items-center bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 7.89a1 1 0 001.42 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              Email
            </button>
          </div>
          <button
            onClick={handleViewDetails}
            className="text-gray-600 hover:text-gray-900 text-sm font-medium border border-gray-300 px-3 py-2 rounded hover:border-gray-400 transition-colors"
          >
            Details
          </button>
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

// Calendar Booking Component
const CalendarBooking = ({ apartmentId, onBookingComplete }) => {
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [availableSlots, setAvailableSlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showBookingForm, setShowBookingForm] = useState(false);
  const [bookingData, setBookingData] = useState({
    visitor_name: '',
    visitor_email: '',
    visitor_phone: '',
    notes: ''
  });
  const toast = useToast && useToast();

  // Generate next 30 days for date selection
  const generateDateOptions = () => {
    const dates = [];
    const today = new Date();
    for (let i = 0; i < 30; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      dates.push({
        value: date.toISOString().split('T')[0],
        label: date.toLocaleDateString('en-US', { 
          weekday: 'short', 
          month: 'short', 
          day: 'numeric' 
        })
      });
    }
    return dates;
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
      const response = await axios.get(`${API}/apartments/${apartmentId}/available-slots?date=${selectedDate}`);
      setAvailableSlots(response.data.available_slots);
    } catch (error) {
      console.error('Error fetching available slots:', error);
      setAvailableSlots([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (date) => {
    setSelectedDate(date);
    setSelectedTime('');
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
        appointment_date: selectedDate,
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
      setSelectedDate('');
      setSelectedTime('');
      
      if (onBookingComplete) {
        onBookingComplete(response.data);
      }

      // Show success notification
      if (toast) {
        toast.success('Appointment booked successfully! You will receive a confirmation email shortly.');
      } else {
        alert('Appointment booked successfully! You will receive a confirmation email shortly.');
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

  return (
    <div className="bg-slate-50 rounded-lg p-6 border border-slate-200">
      <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center">
        <svg className="w-5 h-5 mr-2 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        Schedule a Viewing
      </h3>

      {/* Date Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-slate-700 mb-2">Select Date</label>
        <select
          value={selectedDate}
          onChange={(e) => handleDateChange(e.target.value)}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
        >
          <option value="">Choose a date...</option>
          {generateDateOptions().map(date => (
            <option key={date.value} value={date.value}>{date.label}</option>
          ))}
        </select>
      </div>

      {/* Time Selection */}
      {selectedDate && (
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-2">Available Times (10 AM - 7 PM)</label>
          {loading ? (
            <div className="flex justify-center py-4">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-amber-600"></div>
            </div>
          ) : availableSlots.length > 0 ? (
            <div className="grid grid-cols-3 gap-2">
              {availableSlots.map(slot => (
                <button
                  key={slot}
                  onClick={() => handleTimeSelect(slot)}
                  className="px-3 py-2 text-sm border border-slate-300 rounded-lg hover:bg-amber-50 hover:border-amber-300 focus:ring-2 focus:ring-amber-500 transition-colors"
                >
                  {slot}
                </button>
              ))}
            </div>
          ) : (
            <p className="text-slate-500 text-sm">No available time slots for this date.</p>
          )}
        </div>
      )}

      {/* Booking Form Modal */}
      {showBookingForm && (
        <div className="fixed inset-0 bg-slate-900 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-lg font-semibold text-slate-800">Book Appointment</h4>
              <button
                onClick={() => setShowBookingForm(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="mb-4 p-3 bg-amber-50 rounded-lg">
              <p className="text-sm text-slate-700">
                <strong>Date:</strong> {new Date(selectedDate).toLocaleDateString()}<br />
                <strong>Time:</strong> {selectedTime}
              </p>
            </div>

            <form onSubmit={handleBookingSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">Full Name</label>
                <input
                  type="text"
                  required
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  value={bookingData.visitor_name}
                  onChange={(e) => setBookingData(prev => ({...prev, visitor_name: e.target.value}))}
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">Email</label>
                <input
                  type="email"
                  required
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  value={bookingData.visitor_email}
                  onChange={(e) => setBookingData(prev => ({...prev, visitor_email: e.target.value}))}
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">Phone Number</label>
                <input
                  type="tel"
                  required
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  value={bookingData.visitor_phone}
                  onChange={(e) => setBookingData(prev => ({...prev, visitor_phone: e.target.value}))}
                />
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-slate-700 mb-2">Additional Notes (Optional)</label>
                <textarea
                  rows="3"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                  value={bookingData.notes}
                  onChange={(e) => setBookingData(prev => ({...prev, notes: e.target.value}))}
                  placeholder="Any specific requirements or questions..."
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowBookingForm(false)}
                  className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-amber-600 text-slate-800 py-2 px-4 rounded-lg hover:bg-amber-500 disabled:bg-amber-400 transition-colors font-semibold"
                >
                  {loading ? 'Booking...' : 'Confirm Booking'}
                </button>
              </div>
            </form>
          </div>
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
            className="text-gray-400 hover:text-gray-600"
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
            className="w-full bg-orange-500 text-white py-2 px-4 rounded-lg hover:bg-orange-600 disabled:bg-orange-400 transition-colors font-medium"
          >
            {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        <div className="text-center mt-6">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-orange-500 hover:text-orange-600 text-sm font-medium"
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

                  <div className="space-y-3">
                    <button 
                      onClick={handleContactAgent}
                      className="btn-primary w-full py-3 px-4 font-semibold hover-lift animate-glow"
                    >
                      <svg className="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                      Call Agent
                    </button>
                    <button 
                      onClick={handleScheduleTour}
                      className="btn-secondary w-full py-3 px-4 font-semibold hover-lift"
                    >
                      <svg className="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      Schedule Tour
                    </button>
                    <button 
                      onClick={handleEmailContact}
                      className="w-full text-slate-300 hover:text-amber-400 py-2 text-sm font-medium transition-colors hover-lift"
                    >
                      <svg className="w-4 h-4 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      Send Email Inquiry
                    </button>
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

// Enhanced Footer Component with PLACES styling
const Footer = () => {
  return (
    <footer className="bg-slate-800 text-amber-100">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-12 h-12 flex items-center justify-center">
                {/* Using same SVG logo design */}
                <svg 
                  viewBox="0 0 200 200" 
                  className="w-10 h-10 text-amber-100" 
                  fill="currentColor" 
                  stroke="currentColor" 
                  strokeWidth="4"
                >
                  {/* Hand holding buildings - based on your logo */}
                  <g transform="translate(50, 80)">
                    {/* Hand outline */}
                    <path 
                      d="M20 40 Q15 35 15 30 Q15 25 20 20 Q25 15 35 15 Q40 15 45 20 Q50 15 60 15 Q70 15 75 20 Q80 25 80 30 Q80 35 75 40 L75 50 Q70 60 60 60 L40 60 Q30 60 25 50 Z" 
                      fill="none" 
                      stroke="currentColor" 
                      strokeWidth="6"
                    />
                    
                    {/* House */}
                    <g transform="translate(25, -25)">
                      <path d="M10 25 L20 15 L30 25" fill="none" strokeWidth="4"/>
                      <rect x="15" y="20" width="10" height="15" fill="none" strokeWidth="4"/>
                      <rect x="18" y="28" width="4" height="7" fill="none" strokeWidth="2"/>
                    </g>
                    
                    {/* Building */}
                    <g transform="translate(45, -35)">
                      <rect x="0" y="10" width="15" height="25" fill="none" strokeWidth="4"/>
                      <rect x="3" y="13" width="2" height="2" fill="currentColor"/>
                      <rect x="7" y="13" width="2" height="2" fill="currentColor"/>
                      <rect x="11" y="13" width="2" height="2" fill="currentColor"/>
                      <rect x="3" y="17" width="2" height="2" fill="currentColor"/>
                      <rect x="7" y="17" width="2" height="2" fill="currentColor"/>
                      <rect x="11" y="17" width="2" height="2" fill="currentColor"/>
                      <rect x="3" y="21" width="2" height="2" fill="currentColor"/>
                      <rect x="7" y="21" width="2" height="2" fill="currentColor"/>
                      <rect x="11" y="21" width="2" height="2" fill="currentColor"/>
                      <rect x="3" y="25" width="2" height="2" fill="currentColor"/>
                      <rect x="7" y="25" width="2" height="2" fill="currentColor"/>
                      <rect x="11" y="25" width="2" height="2" fill="currentColor"/>
                    </g>
                  </g>
                </svg>
              </div>
              <div className="text-left">
                <div className="text-xl font-bold text-amber-100 leading-tight">Places</div>
                <div className="text-xs text-amber-200 leading-tight -mt-1">No Fee</div>
              </div>
            </div>
            <p className="text-amber-200 mb-4">
              Your trusted partner for finding no-fee apartments in New York City. 
              Save thousands on broker fees with NoFeePlaces.com.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-amber-200 hover:text-amber-100 transition-colors">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/>
                </svg>
              </a>
              <a href="#" className="text-amber-200 hover:text-amber-100 transition-colors">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M22.46 6c-.77.35-1.6.58-2.46.69.88-.53 1.56-1.37 1.88-2.38-.83.5-1.75.85-2.72 1.05C18.37 4.5 17.26 4 16 4c-2.35 0-4.27 1.92-4.27 4.29 0 .34.04.67.11.98C8.28 9.09 5.11 7.38 3 4.79c-.37.63-.58 1.37-.58 2.15 0 1.49.75 2.81 1.91 3.56-.71 0-1.37-.2-1.95-.5v.03c0 2.08 1.48 3.82 3.44 4.21a4.22 4.22 0 0 1-1.93.07 4.28 4.28 0 0 0 4 2.98 8.521 8.521 0 0 1-5.33 1.84c-.34 0-.68-.02-1.02-.06C3.44 20.29 5.7 21 8.12 21 16 21 20.33 14.46 20.33 8.79c0-.19 0-.37-.01-.56.84-.6 1.56-1.36 2.14-2.23z"/>
                </svg>
              </a>
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-4 text-amber-100">Quick Links</h3>
            <ul className="space-y-2">
              <li><a href="/" className="text-amber-200 hover:text-amber-100 transition-colors">Browse Apartments</a></li>
              <li><a href="#" className="text-amber-200 hover:text-amber-100 transition-colors">No Fee Guide</a></li>
              <li><a href="#" className="text-amber-200 hover:text-amber-100 transition-colors">Neighborhoods</a></li>
              <li><a href="/dashboard" className="text-amber-200 hover:text-amber-100 transition-colors">Dashboard</a></li>
              <li><a href="/saved-searches" className="text-amber-200 hover:text-amber-100 transition-colors">Saved Searches</a></li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-4 text-amber-100">No Fee Apartments by Borough</h3>
            <ul className="space-y-2">
              <li><a href="#" className="text-amber-200 hover:text-amber-100 transition-colors">No Fee Apartments Manhattan</a></li>
              <li><a href="#" className="text-amber-200 hover:text-amber-100 transition-colors">No Fee Apartments Brooklyn</a></li>
              <li><a href="#" className="text-amber-200 hover:text-amber-100 transition-colors">No Fee Apartments Queens</a></li>
              <li><a href="#" className="text-amber-200 hover:text-amber-100 transition-colors">No Fee Apartments Bronx</a></li>
              <li><a href="#" className="text-amber-200 hover:text-amber-100 transition-colors">NYC No Broker Fee Rentals</a></li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-4 text-amber-100">Contact</h3>
            <ul className="space-y-2 text-amber-200">
              <li className="flex items-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                placesnyc88@gmail.com
              </li>
              <li className="flex items-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                (646) 408-8048
              </li>
              <li className="flex items-start">
                <svg className="w-4 h-4 mr-2 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                New York, NY
              </li>
            </ul>
          </div>
        </div>
            <p className="text-amber-200 mb-4">
              Your trusted partner for finding no-fee apartments in New York City. 
              Save thousands on broker fees with NoFeePlaces.com.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-amber-200 hover:text-amber-100 transition-colors">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/>
                </svg>
              </a>
              <a href="#" className="text-amber-200 hover:text-amber-100 transition-colors">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M22.46 6c-.77.35-1.6.58-2.46.69.88-.53 1.56-1.37 1.88-2.38-.83.5-1.75.85-2.72 1.05C18.37 4.5 17.26 4 16 4c-2.35 0-4.27 1.92-4.27 4.29 0 .34.04.67.11.98C8.28 9.09 5.11 7.38 3 4.79c-.37.63-.58 1.37-.58 2.15 0 1.49.75 2.81 1.91 3.56-.71 0-1.37-.2-1.95-.5v.03c0 2.08 1.48 3.82 3.44 4.21a4.22 4.22 0 0 1-1.93.07 4.28 4.28 0 0 0 4 2.98 8.521 8.521 0 0 1-5.33 1.84c-.34 0-.68-.02-1.02-.06C3.44 20.29 5.7 21 8.12 21 16 21 20.33 14.46 20.33 8.79c0-.19 0-.37-.01-.56.84-.6 1.56-1.36 2.14-2.23z"/>
                </svg>
              </a>
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-4 text-amber-100">Quick Links</h3>
            <ul className="space-y-2">
              <li><a href="/" className="text-amber-200 hover:text-amber-100 transition-colors">Browse Apartments</a></li>
              <li><a href="#" className="text-amber-200 hover:text-amber-100 transition-colors">No Fee Guide</a></li>
              <li><a href="#" className="text-amber-200 hover:text-amber-100 transition-colors">Neighborhoods</a></li>
              <li><a href="/dashboard" className="text-amber-200 hover:text-amber-100 transition-colors">Dashboard</a></li>
              <li><a href="/saved-searches" className="text-amber-200 hover:text-amber-100 transition-colors">Saved Searches</a></li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-4 text-amber-100">Popular Areas</h3>
            <ul className="space-y-2">
              <li><a href="#" className="text-amber-200 hover:text-amber-100 transition-colors">Manhattan</a></li>
              <li><a href="#" className="text-amber-200 hover:text-amber-100 transition-colors">Brooklyn</a></li>
              <li><a href="#" className="text-amber-200 hover:text-amber-100 transition-colors">Queens</a></li>
              <li><a href="#" className="text-amber-200 hover:text-amber-100 transition-colors">Bronx</a></li>
              <li><a href="#" className="text-amber-200 hover:text-amber-100 transition-colors">Staten Island</a></li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-4 text-amber-100">Contact</h3>
            <ul className="space-y-2 text-amber-200">
              <li className="flex items-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                placesnyc88@gmail.com
              </li>
              <li className="flex items-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                (646) 408-8048
              </li>
              <li className="flex items-start">
                <svg className="w-4 h-4 mr-2 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                New York, NY
              </li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-slate-700 mt-8 pt-8">
          <div className="text-center text-amber-200 mb-4">
            <p className="mb-2">
              <strong>No Fee Places NYC</strong> - Your trusted source for <strong>no broker fee apartments NYC</strong>
            </p>
            <p className="text-sm">
              Specializing in <strong>no fee rentals NYC</strong>, <strong>NYC apartments no broker fee</strong>, and <strong>New York no fee apartments</strong> across Manhattan, Brooklyn, and Queens.
            </p>
          </div>
          <div className="text-center text-amber-200 text-sm">
            <p>&copy; 2025 NoFeePlaces.com. All rights reserved. | <a href="#" className="hover:text-amber-100">Privacy Policy</a> | <a href="#" className="hover:text-amber-100">Terms of Service</a></p>
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
          className={`w-24 h-24 rounded-full shadow-2xl hover:shadow-3xl transition-all duration-300 flex items-center justify-center ${
            isOpen 
              ? 'bg-red-500 hover:bg-red-600' 
              : 'bg-orange-500 hover:bg-orange-600 animate-pulse'
          }`}
          style={{ boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)' }}
        >
          {isOpen ? (
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
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
                className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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

// Export all components
export const Components = {
  Header,
  Hero,
  SEOContentSection,
  AdvancedSearchFilters,
  ApartmentCard,
  MapView,
  LoadingSpinner,
  Footer,
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
  EmailContactModal
};