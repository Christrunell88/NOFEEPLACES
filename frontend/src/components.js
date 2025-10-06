import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from './auth';
import { trackApartmentView, trackContactForm, trackHeroAction, trackNavigationClick } from './analytics';

// Import all missing components
import {
  Hero,
  FeaturedApartments,
  AdvancedSearchFilters,
  MapView,
  Footer,
  LoadingSpinner,
  AuthModal,
  UserDashboard,
  SavedSearches,
  AdminAppointments,
  AIChatbot,
  FavoritesPage,
  ApartmentComparison,
  ToastProvider,
  ErrorBoundary,
  CompleteGuideNoFeeApartments,
  BlogList,
  BlogPost,
  EmailContactModal
} from './missing-components';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

// Helper function to determine what address to show based on authentication
const getDisplayAddress = (apartment, isAuthenticated) => {
  if (isAuthenticated) {
    // Show full address for authenticated users
    return apartment.address || apartment.location || 'Address not available';
  } else {
    // Show only neighborhood for non-authenticated users
    return apartment.neighborhood || apartment.borough || 'Neighborhood not available';
  }
};

// Re-export all imported components
export {
  Hero,
  FeaturedApartments,
  AdvancedSearchFilters,
  MapView,
  Footer,
  LoadingSpinner,
  AuthModal,
  UserDashboard,
  SavedSearches,
  AdminAppointments,
  AIChatbot,
  FavoritesPage,
  ApartmentComparison,
  ToastProvider,
  ErrorBoundary,
  CompleteGuideNoFeeApartments,
  BlogList,
  BlogPost,
  EmailContactModal,
  ApartmentDetailsModal
};

// Toast notification component
export const Toast = ({ message, type = 'success', onClose, duration = 5000 }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [onClose, duration]);

  const bgColor = type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500';

  return (
    <div className={`fixed top-4 right-4 ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg z-50 transform transition-all duration-300`}>
      <div className="flex items-center justify-between">
        <span>{message}</span>
        <button onClick={onClose} className="ml-4 text-white hover:text-gray-200">
          ×
        </button>
      </div>
    </div>
  );
};

// Newsletter Signup Components
export const NewsletterSignup = ({ source = "website", size = "default", className = "" }) => {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubscribe = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const response = await axios.post(`${API}/newsletter/subscribe`, {
        email,
        full_name: name,
        source,
        preferences: {
          weekly_digest: true,
          new_listings: true,
          market_reports: true,
          tips_guides: true
        }
      });

      setSuccess(true);
      setMessage('🎉 Successfully subscribed! Check your email for a welcome message.');
      setEmail('');
      setName('');
    } catch (error) {
      setMessage('❌ Subscription failed. Please try again.');
      setSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  const isCompact = size === "compact";
  const isLarge = size === "large";

  return (
    <div className={`newsletter-signup ${className}`}>
      {!isCompact && (
        <div className="mb-4">
          <h3 className={`font-bold ${isLarge ? 'text-2xl' : 'text-lg'} text-gray-800 mb-2`}>
            📧 Get NYC's Best No Fee Apartments First
          </h3>
          <p className={`text-gray-600 ${isLarge ? 'text-base' : 'text-sm'}`}>
            Join 1,000+ smart renters who get new listings, market insights, and exclusive deals.
          </p>
        </div>
      )}

      <form onSubmit={handleSubscribe} className={`space-y-${isCompact ? '2' : '3'}`}>
        {!isCompact && (
          <input
            type="text"
            placeholder="Your name (optional)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className={`w-full px-4 py-${isLarge ? '3' : '2'} border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent`}
          />
        )}
        
        <div className={`flex ${isCompact ? 'flex-row space-x-2' : 'flex-col sm:flex-row sm:space-x-2 sm:space-y-0 space-y-2'}`}>
          <input
            type="email"
            placeholder="Enter your email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onFocus={(e) => e.target.style.outline = '2px solid #8b5cf6'}
            onBlur={(e) => e.target.style.outline = 'none'}
            required
            autoComplete="email"
            style={{
              WebkitAppearance: 'none',
              MozAppearance: 'textfield'
            }}
            className={`flex-1 px-4 ${isLarge ? 'py-3' : 'py-2'} border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 focus:outline-none transition-all`}
          />
          <button
            type="submit"
            disabled={loading || !email.trim()}
            className={`${isCompact ? 'px-4' : 'px-6'} ${isLarge ? 'py-3' : 'py-2'} bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-pink-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl ${isCompact ? 'whitespace-nowrap' : ''}`}
          >
            {loading ? '⏳ Subscribing...' : '📧 Subscribe'}
          </button>
        </div>
        
        {!isCompact && (
          <div className="flex items-center space-x-4 text-xs text-gray-500">
            <div className="flex items-center space-x-1">
              <span>✅</span>
              <span>New Listings</span>
            </div>
            <div className="flex items-center space-x-1">
              <span>✅</span>
              <span>Market Reports</span>
            </div>
            <div className="flex items-center space-x-1">
              <span>✅</span>
              <span>No Spam</span>
            </div>
            <div className="flex items-center space-x-1">
              <span>✅</span>
              <span>Unsubscribe Anytime</span>
            </div>
          </div>
        )}
      </form>

      {message && (
        <div className={`mt-3 p-3 rounded-lg text-sm ${success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {message}
        </div>
      )}
    </div>
  );
};

// Exit Intent Newsletter Popup
export const NewsletterExitPopup = () => {
  const [showPopup, setShowPopup] = useState(false);
  const [hasShown, setHasShown] = useState(false);

  useEffect(() => {
    const handleMouseLeave = (e) => {
      if (e.clientY <= 0 && !hasShown) {
        setShowPopup(true);
        setHasShown(true);
      }
    };

    document.addEventListener('mouseleave', handleMouseLeave);
    
    // Also show after 30 seconds if user hasn't left
    const timer = setTimeout(() => {
      if (!hasShown) {
        setShowPopup(true);
        setHasShown(true);
      }
    }, 30000);

    return () => {
      document.removeEventListener('mouseleave', handleMouseLeave);
      clearTimeout(timer);
    };
  }, [hasShown]);

  if (!showPopup) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-8 relative">
        <button
          onClick={() => setShowPopup(false)}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-2xl"
        >
          ×
        </button>
        
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Wait! Don't Miss Out! 🏙️</h2>
          <p className="text-gray-600">
            Join 1,000+ smart renters getting exclusive access to NYC's best no fee apartments
          </p>
        </div>

        <NewsletterSignup 
          source="exit_intent" 
          size="compact"
          className="newsletter-exit-popup"
        />

        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            Get weekly listings • Market reports • Zero spam • Unsubscribe anytime
          </p>
        </div>
      </div>
    </div>
  );
};

// Lead Magnet Component
export const LeadMagnet = ({ title, description, downloadUrl, source }) => {
  return (
    <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-6 border border-purple-200">
      <div className="text-center mb-4">
        <div className="text-4xl mb-2">📋</div>
        <h3 className="text-xl font-bold text-gray-800 mb-2">{title}</h3>
        <p className="text-gray-600 text-sm">{description}</p>
      </div>
      
      <NewsletterSignup 
        source={source}
        size="compact"
        className="lead-magnet-signup"
      />
      
      <div className="mt-4 text-center text-xs text-gray-500">
        Download link will be sent to your email immediately
      </div>
    </div>
  );
};

// Header Component (updated to include newsletter)
export const Header = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);

  return (
    <header className="bg-black text-white shadow-2xl sticky top-0 z-40">
      <nav className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Left Side: Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-slate-700 to-slate-900 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">🏢</span>
            </div>
            <div>
              <div className="font-bold text-xl text-white">
                NoFee<span className="text-blue-400">Places</span>
              </div>
              <div className="text-xs text-gray-400">NYC No-Fee Rentals</div>
            </div>
          </Link>

          {/* Center Navigation */}
          <div className="hidden lg:flex items-center space-x-8">
            <Link 
              to="/blog" 
              className="text-gray-300 hover:text-blue-400 transition-colors font-medium"
              onClick={() => trackNavigationClick('Blog', '/blog')}
            >
              Guides
            </Link>
            <Link 
              to="/tenant/list-apartment" 
              className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 shadow-md hover:shadow-lg"
              onClick={() => trackNavigationClick('List Your Place', '/tenant/list-apartment')}
            >
              List Your Place
            </Link>
          </div>

          {/* Right Side: Authentication */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-2 text-gray-300 hover:text-white focus:outline-none rounded-lg px-3 py-2 transition-colors"
                >
                  <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                    {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
                  </div>
                  <span className="hidden md:block font-medium">{user?.full_name || 'User'}</span>
                </button>

                {/* User Dropdown Menu */}
                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-gray-900 rounded-lg shadow-2xl py-2 z-50 border border-gray-700">
                    <Link to="/dashboard" className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white transition-colors">Dashboard</Link>
                    <Link to="/favorites" className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white transition-colors">Favorites</Link>
                    <Link to="/tenant/list-apartment" className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white transition-colors">Post Listing</Link>
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
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="hidden md:block text-gray-300 hover:text-blue-400 transition-colors font-medium"
                >
                  Sign In
                </button>
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg transition-all duration-200 font-semibold shadow-md hover:shadow-lg"
                >
                  Try for Free
                </button>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Auth Modal */}
      {showAuthModal && <AuthModal onClose={() => setShowAuthModal(false)} />}
    </header>
  );
};

// Newsletter Page Component
export const NewsletterPage = () => {
  const [stats, setStats] = useState({});

  useEffect(() => {
    fetchNewsletterStats();
  }, []);

  const fetchNewsletterStats = async () => {
    try {
      const response = await axios.get(`${API}/newsletter/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch newsletter stats:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      <div className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-800 mb-6">
            📧 NYC's Premier No Fee Apartment Newsletter
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Join thousands of smart renters who get exclusive access to NYC's best no fee apartments, 
            market insights, and money-saving tips delivered straight to their inbox.
          </p>
          
          <div className="bg-white rounded-2xl shadow-xl p-8 max-w-2xl mx-auto">
            <NewsletterSignup source="newsletter_page" size="large" />
          </div>
        </div>

        {/* Benefits Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          <div className="bg-white rounded-xl p-6 shadow-lg">
            <div className="text-4xl mb-4">🏠</div>
            <h3 className="text-xl font-bold mb-2">New Listings</h3>
            <p className="text-gray-600">Get notified about new no fee apartments as soon as they're available</p>
          </div>
          
          <div className="bg-white rounded-xl p-6 shadow-lg">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-bold mb-2">Market Reports</h3>
            <p className="text-gray-600">Weekly insights on rental trends, pricing changes, and neighborhood updates</p>
          </div>
          
          <div className="bg-white rounded-xl p-6 shadow-lg">
            <div className="text-4xl mb-4">💡</div>
            <h3 className="text-xl font-bold mb-2">Expert Tips</h3>
            <p className="text-gray-600">Insider strategies for apartment hunting, negotiating rent, and avoiding scams</p>
          </div>
          
          <div className="bg-white rounded-xl p-6 shadow-lg">
            <div className="text-4xl mb-4">🎁</div>
            <h3 className="text-xl font-bold mb-2">Exclusive Deals</h3>
            <p className="text-gray-600">Special promotions, free months, and subscriber-only apartment previews</p>
          </div>
        </div>

        {/* Lead Magnets */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <LeadMagnet 
            title="Ultimate NYC Apartment Hunting Guide"
            description="50+ page comprehensive guide with checklists, tips, and insider secrets"
            downloadUrl="/downloads/nyc-apartment-guide.pdf"
            source="lead_magnet_guide"
          />
          
          <LeadMagnet 
            title="No Fee Apartment Checklist"
            description="Step-by-step checklist to find and secure your perfect no fee apartment"
            downloadUrl="/downloads/no-fee-checklist.pdf"
            source="lead_magnet_checklist"
          />
          
          <LeadMagnet 
            title="NYC Neighborhood Comparison"
            description="Detailed breakdown of costs, commute times, and amenities by neighborhood"
            downloadUrl="/downloads/neighborhood-comparison.pdf"
            source="lead_magnet_comparison"
          />
        </div>

        {/* Statistics */}
        {stats.total_subscribers && (
          <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
            <h2 className="text-3xl font-bold text-gray-800 mb-8">Join Our Growing Community</h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div>
                <div className="text-4xl font-bold text-purple-600">{stats.total_subscribers}+</div>
                <div className="text-gray-600">Newsletter Subscribers</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-purple-600">335+</div>
                <div className="text-gray-600">No Fee Apartments</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-purple-600">$8K+</div>
                <div className="text-gray-600">Average Savings</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Rest of your existing components remain the same...
// (I'll include the key components but truncate for brevity)

// Apartment Card Component (updated with newsletter CTA)
export const ApartmentCard = ({ apartment, onFavorite, onContact }) => {
  const { isAuthenticated, user } = useAuth();
  const [imageError, setImageError] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isFavorited, setIsFavorited] = useState(false);
  const [showContactModal, setShowContactModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  // Import analytics tracking
  // Track apartment view when card is visible
  useEffect(() => {
    if (apartment) {
      trackApartmentView(apartment);
      
      // Also track for landlord analytics if apartment has landlord_id
      if (apartment.landlord_id) {
        trackApartmentViewForLandlord(apartment.id);
      }
    }
  }, [apartment]);

  const trackApartmentViewForLandlord = async (apartmentId) => {
    try {
      const API = process.env.REACT_APP_BACKEND_URL;
      await fetch(`${API}/api/landlord/apartment/${apartmentId}/view`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (error) {
      console.log('View tracking failed:', error);
    }
  };

  // Create JSON-LD structured data for each apartment
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "Apartment",
    "name": apartment.title,
    "address": {
      "@type": "PostalAddress",
      "streetAddress": isAuthenticated ? apartment.address : apartment.neighborhood,
      "addressLocality": apartment.neighborhood,
      "addressRegion": apartment.borough,
      "addressCountry": "US"
    },
    "offers": {
      "@type": "Offer",
      "price": apartment.price,
      "priceCurrency": "USD",
      "availability": "https://schema.org/InStock"
    },
    "floorSize": {
      "@type": "QuantitativeValue",
      "value": apartment.sqft,
      "unitCode": "SQF"
    },
    "numberOfRooms": apartment.bedrooms,
    "amenityFeature": apartment.amenities?.map(amenity => ({
      "@type": "LocationFeatureSpecification",
      "name": amenity
    }))
  };

  useEffect(() => {
    // Check if apartment is in user's favorites on mount
    if (isAuthenticated && user?.favorite_apartments?.includes(apartment.id)) {
      setIsFavorited(true);
    }
  }, [isAuthenticated, user, apartment.id]);

  const handleNextImage = (e) => {
    e.stopPropagation();
    setCurrentImageIndex((prev) => 
      prev === (apartment.images?.length || 1) - 1 ? 0 : prev + 1
    );
  };

  const handlePrevImage = (e) => {
    e.stopPropagation();
    setCurrentImageIndex((prev) => 
      prev === 0 ? (apartment.images?.length || 1) - 1 : prev - 1
    );
  };

  const handleFavorite = async (e) => {
    e.stopPropagation();
    if (!isAuthenticated) {
      alert('Please sign in to save favorites');
      return;
    }
    
    try {
      const response = await axios.post(`${API}/favorites/toggle`, {
        apartment_id: apartment.id
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('authToken')}` }
      });
      
      setIsFavorited(!isFavorited);
      onFavorite && onFavorite(apartment.id, !isFavorited);
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  const currentImage = apartment.images?.[currentImageIndex] || '/api/placeholder/400/300';
  const imageCount = apartment.images?.length || 0;

  return (
    <>
      <script type="application/ld+json">
        {JSON.stringify(structuredData)}
      </script>
      
      <div className="bg-white rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 overflow-hidden border border-gray-100">
        {/* Image Section */}
        <div className="relative h-64 bg-gray-200 overflow-hidden">
          {!imageError ? (
            <img
              src={currentImage}
              alt={apartment.title}
              className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
              onError={() => setImageError(true)}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gray-100">
              <div className="text-center text-gray-400">
                <div className="text-4xl mb-2">🏢</div>
                <div className="text-sm">No Image Available</div>
              </div>
            </div>
          )}

          {/* Image Navigation */}
          {imageCount > 1 && (
            <>
              <button
                onClick={handlePrevImage}
                className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-opacity-75 transition-opacity"
              >
                ‹
              </button>
              <button
                onClick={handleNextImage}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-opacity-75 transition-opacity"
              >
                ›
              </button>
              <div className="absolute top-2 left-2 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-sm">
                {currentImageIndex + 1}/{imageCount}
              </div>
            </>
          )}

          {/* NO FEE Badge */}
          <div className="absolute top-2 right-2 bg-orange-500 text-white px-3 py-1 rounded-full text-sm font-semibold">
            NO FEE
          </div>

          {/* Favorite Button */}
          <button
            onClick={handleFavorite}
            className={`absolute top-2 right-32 w-8 h-8 rounded-full flex items-center justify-center transition-colors ${
              isFavorited 
                ? 'bg-red-500 text-white' 
                : 'bg-white text-gray-400 hover:text-red-500'
            }`}
          >
            ♥
          </button>
        </div>

        {/* Content Section */}
        <div className="p-6">
          <h3 className="text-xl font-semibold text-slate-800 mb-2 line-clamp-2">
            {apartment.title}
          </h3>

          <p className="text-gray-300 text-sm mb-3 flex items-center">
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {/* Show address based on authentication status */}
              {getDisplayAddress(apartment, isAuthenticated)}
              {!isAuthenticated && (
                <span className="ml-2 text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded-full">
                  Sign in for full address
                </span>
              )}
            </span>
          </p>

          <div className="flex items-center justify-between mb-4">
            <div className="text-2xl font-bold text-amber-600">
              ${apartment.price?.toLocaleString()}<span className="text-sm text-gray-500">/mo</span>
            </div>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              {apartment.bedrooms && (
                <span className="flex items-center">
                  <span className="font-medium">{apartment.bedrooms}</span>
                  <span className="ml-1">bed</span>
                </span>
              )}
              {apartment.bathrooms && (
                <span className="flex items-center">
                  <span className="font-medium">{apartment.bathrooms}</span>
                  <span className="ml-1">bath</span>
                </span>
              )}
              {apartment.sqft && (
                <span className="flex items-center">
                  <span className="font-medium">{apartment.sqft}</span>
                  <span className="ml-1">sq ft</span>
                </span>
              )}
            </div>
          </div>

          {/* Amenities */}
          {apartment.amenities?.length > 0 && (
            <div className="mb-4">
              <div className="flex flex-wrap gap-2">
                {apartment.amenities.slice(0, 3).map((amenity, index) => (
                  <span key={index} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                    {amenity}
                  </span>
                ))}
                {apartment.amenities.length > 3 && (
                  <span className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">
                    +{apartment.amenities.length - 3} more
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-2">
            <button
              onClick={() => setShowContactModal(true)}
              className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors font-medium"
            >
              📧 Contact
            </button>
            <button
              onClick={() => setShowDetailsModal(true)}
              className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              🏠 View Details
            </button>
          </div>
        </div>
      </div>

      {/* Contact Modal */}
      {showContactModal && (
        <EmailContactModal
          apartment={apartment}
          onClose={() => setShowContactModal(false)}
        />
      )}
      
      {/* Apartment Details Modal */}
      {showDetailsModal && (
        <ApartmentDetailsModal 
          apartment={apartment}
          onClose={() => setShowDetailsModal(false)}
        />
      )}
    </>
  );
};

// ApartmentDetails Component
export const ApartmentDetails = ({ apartmentId }) => {
  const [apartment, setApartment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [showContactModal, setShowContactModal] = useState(false);
  const { isAuthenticated } = useAuth();

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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (!apartment) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Apartment Not Found</h2>
          <p className="text-gray-600">The apartment you're looking for doesn't exist or has been removed.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="grid lg:grid-cols-2 gap-8">
        {/* Image Gallery */}
        <div className="space-y-4">
          <div className="relative h-96 bg-gray-200 rounded-xl overflow-hidden">
            <img
              src={apartment.images?.[currentImageIndex] || '/api/placeholder/600/400'}
              alt={apartment.title}
              className="w-full h-full object-cover"
            />
            {apartment.images?.length > 1 && (
              <>
                <button
                  onClick={() => setCurrentImageIndex(prev => prev === 0 ? apartment.images.length - 1 : prev - 1)}
                  className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full w-10 h-10 flex items-center justify-center hover:bg-opacity-75"
                >
                  ‹
                </button>
                <button
                  onClick={() => setCurrentImageIndex(prev => prev === apartment.images.length - 1 ? 0 : prev + 1)}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full w-10 h-10 flex items-center justify-center hover:bg-opacity-75"
                >
                  ›
                </button>
              </>
            )}
          </div>
          
          {/* Thumbnail Gallery */}
          {apartment.images?.length > 1 && (
            <div className="grid grid-cols-4 gap-2">
              {apartment.images.map((image, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentImageIndex(index)}
                  className={`relative h-20 rounded-lg overflow-hidden ${
                    currentImageIndex === index ? 'ring-2 ring-purple-600' : ''
                  }`}
                >
                  <img
                    src={image}
                    alt={`${apartment.title} ${index + 1}`}
                    className="w-full h-full object-cover"
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Apartment Details */}
        <div className="space-y-6">
          <div>
            <div className="flex gap-2 mb-4">
              <div className="bg-orange-500 text-white px-3 py-1 rounded-full text-sm font-semibold">
                NO FEE
              </div>
              <div className="bg-orange-500 text-white px-3 py-1 rounded-full text-sm font-semibold">
                NO FEE
              </div>
            </div>
            
            <div>
              <h1 className="text-3xl font-bold text-slate-800 mb-2">{apartment.title}</h1>
              <p className="text-slate-600 mb-2">
                {getDisplayAddress(apartment, isAuthenticated)}
                {!isAuthenticated && (
                  <span className="ml-2 text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded-full">
                    Sign in for full address
                  </span>
                )}
              </p>
              <div className="text-3xl font-bold text-amber-600 mb-4">
                ${apartment.price?.toLocaleString()}<span className="text-lg text-gray-500">/month</span>
              </div>
            </div>

            {/* Apartment Stats */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              {apartment.bedrooms && (
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-slate-800">{apartment.bedrooms}</div>
                  <div className="text-sm text-gray-600">Bedrooms</div>
                </div>
              )}
              {apartment.bathrooms && (
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-slate-800">{apartment.bathrooms}</div>
                  <div className="text-sm text-gray-600">Bathrooms</div>
                </div>
              )}
              {apartment.sqft && (
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-slate-800">{apartment.sqft}</div>
                  <div className="text-sm text-gray-600">Sq Ft</div>
                </div>
              )}
            </div>
          </div>

          {/* Description */}
          <div>
            <h3 className="text-xl font-semibold text-slate-800 mb-3">Description</h3>
            <p className="text-gray-600 leading-relaxed">{apartment.description}</p>
          </div>

          {/* Amenities */}
          {apartment.amenities?.length > 0 && (
            <div>
              <h3 className="text-xl font-semibold text-slate-800 mb-3">Amenities</h3>
              <div className="grid grid-cols-2 gap-2">
                {apartment.amenities.map((amenity, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <span className="text-green-600">✓</span>
                    <span className="text-gray-700">{amenity}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Contact Section */}
          <div className="bg-purple-50 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-slate-800 mb-4">Interested in this apartment?</h3>
            <p className="text-gray-600 mb-4">
              Contact us to schedule a viewing or get more information about this no fee apartment.
            </p>
            <button
              onClick={() => setShowContactModal(true)}
              className="w-full bg-purple-600 text-white py-3 px-6 rounded-lg hover:bg-purple-700 transition-colors font-semibold"
            >
              📧 Contact About This Apartment
            </button>
          </div>

          {/* Newsletter CTA for non-authenticated users */}
          {!isAuthenticated && (
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-200">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Want More Apartments Like This?</h3>
              <p className="text-gray-600 mb-4">
                Get instant alerts for similar no fee apartments and never miss a great deal.
              </p>
              <NewsletterSignup 
                source="apartment_details_cta"
                size="compact"
              />
            </div>
          )}
        </div>
      </div>

      {/* Contact Modal */}
      {showContactModal && (
        <EmailContactModal
          apartment={apartment}
          onClose={() => setShowContactModal(false)}
        />
      )}
    </div>
  );
};

// Apartment Details Modal Component
const ApartmentDetailsModal = ({ apartment, onClose }) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [showContactModal, setShowContactModal] = useState(false);
  const { isAuthenticated } = useAuth();

  // Use neighborhood for non-authenticated users, full address for authenticated users
  const locationInfo = isAuthenticated 
    ? (apartment.address || apartment.location)
    : (apartment.neighborhood || apartment.location?.split(',')[0] || 'this property');

  const handleNextImage = () => {
    setCurrentImageIndex((prev) => 
      prev === (apartment.images?.length || 1) - 1 ? 0 : prev + 1
    );
  };

  const handlePrevImage = () => {
    setCurrentImageIndex((prev) => 
      prev === 0 ? (apartment.images?.length || 1) - 1 : prev - 1
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-800">{apartment.title}</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Image Gallery */}
          <div className="relative h-96 bg-gray-200 rounded-lg overflow-hidden mb-6">
            <img
              src={apartment.images?.[currentImageIndex] || '/api/placeholder/800/400'}
              alt={apartment.title}
              className="w-full h-full object-cover"
            />
            
            {/* Image Navigation */}
            {apartment.images && apartment.images.length > 1 && (
              <>
                <button
                  onClick={handlePrevImage}
                  className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full w-10 h-10 flex items-center justify-center hover:bg-opacity-70"
                >
                  ←
                </button>
                <button
                  onClick={handleNextImage}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full w-10 h-10 flex items-center justify-center hover:bg-opacity-70"
                >
                  →
                </button>
                
                {/* Image Counter */}
                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black bg-opacity-50 text-white px-3 py-1 rounded-full text-sm">
                  {currentImageIndex + 1} / {apartment.images.length}
                </div>
              </>
            )}
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Left Column - Details */}
            <div>
              {/* Price and Badges */}
              <div className="flex items-center justify-between mb-4">
                <div className="text-3xl font-bold text-green-600">
                  ${apartment.price?.toLocaleString()}/month
                </div>
                <div className="flex gap-2">
                  <span className="bg-green-500 text-white px-3 py-1 rounded-full text-sm font-semibold">
                    ✓ VERIFIED
                  </span>
                  <span className="bg-orange-500 text-white px-3 py-1 rounded-full text-sm font-semibold">
                    NO FEE
                  </span>
                </div>
              </div>

              {/* Basic Info */}
              <div className="grid grid-cols-3 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
                <div className="text-center">
                  <div className="text-xl font-bold text-gray-800">
                    {apartment.bedrooms === 0 ? 'Studio' : `${apartment.bedrooms}`}
                  </div>
                  <div className="text-sm text-gray-600">
                    {apartment.bedrooms === 0 ? '' : 'Bedrooms'}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-xl font-bold text-gray-800">{apartment.bathrooms}</div>
                  <div className="text-sm text-gray-600">Bathrooms</div>
                </div>
                <div className="text-center">
                  <div className="text-xl font-bold text-gray-800">{apartment.sqft}</div>
                  <div className="text-sm text-gray-600">Sq Ft</div>
                </div>
              </div>

              {/* Location */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2">📍 Location</h3>
                <p className="text-gray-700">{apartment.address || apartment.location}</p>
                <p className="text-gray-600">{apartment.neighborhood}</p>
              </div>

              {/* Description */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2">📝 Description</h3>
                <p className="text-gray-700">{apartment.description}</p>
              </div>

              {/* Amenities */}
              {apartment.amenities && apartment.amenities.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-2">✨ Amenities</h3>
                  <div className="grid grid-cols-2 gap-2">
                    {apartment.amenities.map((amenity, index) => (
                      <div key={index} className="flex items-center text-gray-700">
                        <span className="text-green-500 mr-2">✓</span>
                        {amenity}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right Column - Additional Info */}
            <div>
              {/* Lease Information */}
              <div className="bg-blue-50 p-4 rounded-lg mb-6">
                <h3 className="text-lg font-semibold mb-3 text-blue-800">📋 Lease Information</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Lease Terms:</span>
                    <span className="font-medium">{apartment.lease_terms || '12 months'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Pet Policy:</span>
                    <span className="font-medium">{apartment.pet_policy || 'Ask landlord'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Utilities:</span>
                    <span className="font-medium">{apartment.utilities || 'Not specified'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Security Deposit:</span>
                    <span className="font-medium">{apartment.deposit || '1-2 months rent'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Move-in Date:</span>
                    <span className="font-medium">{apartment.move_in_date || 'Flexible'}</span>
                  </div>
                </div>
              </div>

              {/* Contact Information */}
              <div className="bg-purple-50 p-4 rounded-lg mb-6">
                <h3 className="text-lg font-semibold mb-3 text-purple-800">📞 Contact Information</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center">
                    <span className="text-purple-600 mr-2">📧</span>
                    <span className="font-medium">{apartment.contact_email}</span>
                  </div>
                  <div className="flex items-center">
                    <span className="text-purple-600 mr-2">📱</span>
                    <span className="font-medium">{apartment.contact_phone}</span>
                  </div>
                  <div className="flex items-center">
                    <span className="text-purple-600 mr-2">🏢</span>
                    <span className="font-medium">NoFeePlaces LLC</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-3">
                <button
                  onClick={() => setShowContactModal(true)}
                  className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg hover:bg-purple-700 transition-colors font-semibold text-lg"
                >
                  📧 Send Email Inquiry
                </button>
                <button
                  onClick={() => window.open(`tel:${apartment.contact_phone}`)}
                  className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-semibold"
                >
                  📞 Call Now
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Contact Modal */}
        {showContactModal && (
          <EmailContactModal
            apartment={apartment}
            onClose={() => setShowContactModal(false)}
          />
        )}
      </div>
    </div>
  );
};

// Continue with other components...
// (Rest of the components remain the same but with newsletter CTAs integrated where appropriate)