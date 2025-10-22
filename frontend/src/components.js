import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from './auth';
import { trackApartmentView, trackContactForm, trackHeroAction, trackNavigationClick } from './analytics';
import HamburgerMenu from './HamburgerMenu';
import { HeaderWordMark } from './WordMark';
import { ListingMetaTags } from './MetaTags';
import { RealEstateListingSchema } from './StructuredData';
import ScheduleShowingModal from './ScheduleShowingModal';

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
  EmailContactModal,
  ShowYourPlaceModal
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
  ApartmentDetailsModal,
  ShowYourPlaceModal
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
        <button onClick={onClose} className="ml-4 text-white hover:text-gray-200" aria-label="Close notification">
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
          aria-label="Close newsletter signup popup"
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

// Header Component (professional design with refined styling)
export const Header = () => {
  const { isAuthenticated, user } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showPlaceModal, setShowPlaceModal] = useState(false);
  const [pendingListingAction, setPendingListingAction] = useState(false);

  // Handle opening listing modal after authentication
  React.useEffect(() => {
    if (isAuthenticated && pendingListingAction) {
      setShowPlaceModal(true);
      setPendingListingAction(false);
    }
  }, [isAuthenticated, pendingListingAction]);

  const handleShowYourPlace = () => {
    if (!isAuthenticated) {
      setPendingListingAction(true);
      setShowAuthModal(true);
    } else {
      setShowPlaceModal(true);
    }
  };

  const handleAuthModalClose = () => {
    setShowAuthModal(false);
    // Don't reset pendingListingAction here - let useEffect handle it
  };

  return (
    <header className="bg-gradient-to-r from-slate-900 via-gray-900 to-slate-900 text-white shadow-2xl sticky top-0 z-40 border-b border-slate-700">
      <nav className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Left Side: Elegant Wordmark */}
          <HeaderWordMark />

          {/* Center - Show Your Place Button */}
          <div className="flex-1 flex justify-center">
            <button
              onClick={handleShowYourPlace}
              className="group relative px-3 py-2 md:px-8 md:py-3 bg-white hover:bg-gradient-to-r hover:from-emerald-400 hover:to-teal-500 text-gray-900 hover:text-white rounded-full transition-all duration-300 font-bold shadow-2xl hover:shadow-emerald-500/50 text-xs md:text-sm border-2 border-emerald-400 hover:border-emerald-300 transform hover:scale-105"
            >
              <div className="flex items-center space-x-1 md:space-x-2">
                <svg className="w-4 h-4 md:w-5 md:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span className="hidden xs:inline">Show Your Place</span>
                <span className="xs:hidden">List</span>
              </div>
              <div className="absolute inset-0 rounded-full bg-emerald-400 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
            </button>
          </div>

          {/* Right Side: Professional Authentication & Menu */}
          <div className="flex items-center space-x-4">
            {/* Removed redundant "Get Started" button - Hero has CTAs */}
            
            {/* Professional User Avatar */}
            {isAuthenticated && (
              <div className="flex items-center space-x-3 mr-2 bg-slate-800 rounded-lg px-3 py-2 border border-slate-600">
                <div className="w-8 h-8 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center text-white font-bold text-sm shadow-md">
                  {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
                </div>
                <div className="hidden sm:block">
                  <div className="text-sm font-semibold text-white">{user?.full_name || 'User'}</div>
                  <div className="text-xs text-gray-400">Member</div>
                </div>
              </div>
            )}

            {/* Professional Hamburger Menu */}
            <HamburgerMenu />
          </div>
        </div>
      </nav>

      {/* Auth Modal */}
      {showAuthModal && <AuthModal onClose={handleAuthModalClose} />}
      
      {/* Show Your Place Modal */}
      {showPlaceModal && <ShowYourPlaceModal onClose={() => setShowPlaceModal(false)} />}
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
  const [showScheduleModal, setShowScheduleModal] = useState(false);

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

  // Reset image index when apartment changes
  useEffect(() => {
    setCurrentImageIndex(0);
  }, [apartment?.id]);

  const handleNextImage = (e) => {
    e.stopPropagation();
    if (!apartment.images || apartment.images.length === 0) return;
    
    setCurrentImageIndex((prev) => {
      const maxIndex = apartment.images.length - 1;
      return prev >= maxIndex ? 0 : prev + 1;
    });
  };

  const handlePrevImage = (e) => {
    e.stopPropagation();
    if (!apartment.images || apartment.images.length === 0) return;
    
    setCurrentImageIndex((prev) => {
      const maxIndex = apartment.images.length - 1;
      return prev <= 0 ? maxIndex : prev - 1;
    });
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

  // Safely get current image with bounds checking
  const safeImageIndex = apartment.images && apartment.images.length > 0 
    ? Math.min(currentImageIndex, apartment.images.length - 1)
    : 0;
  const currentImage = (apartment.images && apartment.images.length > 0)
    ? apartment.images[safeImageIndex]
    : '/api/placeholder/400/300';
  const imageCount = apartment.images?.length || 0;

  return (
    <>
      <script type="application/ld+json">
        {JSON.stringify(structuredData)}
      </script>
      
      <div className="bg-white rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 overflow-hidden border border-gray-100">
        {/* Image Section - Clickable */}
        <div 
          className="relative h-64 bg-gray-200 overflow-hidden cursor-pointer group"
          onClick={() => setShowDetailsModal(true)}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              setShowDetailsModal(true);
            }
          }}
          aria-label={`View details for ${apartment.title}`}
        >
          {!imageError ? (
            <img
              src={currentImage}
              alt={apartment.title}
              className="w-full h-full object-cover transition-all duration-300 group-hover:scale-105"
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
          
          {/* Hover Overlay with "View Details" hint */}
          <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-300 flex items-center justify-center">
            <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 text-white font-medium text-lg">
              <span className="bg-teal-500 px-4 py-2 rounded-lg shadow-lg">View Details</span>
            </div>
          </div>

          {/* Image Navigation */}
          {imageCount > 1 && (
            <>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handlePrevImage();
                }}
                className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-opacity-75 transition-opacity z-10"
                aria-label="Previous image"
              >
                ‹
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleNextImage();
                }}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-opacity-75 transition-opacity z-10"
                aria-label="Next image"
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
            onClick={(e) => {
              e.stopPropagation();
              handleFavorite();
            }}
            className={`absolute top-2 right-32 w-8 h-8 rounded-full flex items-center justify-center transition-colors z-10 ${
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
                  <span className="font-medium">{parseInt(apartment.bathrooms)}</span>
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

          {/* Action Button */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowScheduleModal(true);
            }}
            className="w-full bg-gradient-to-r from-purple-600 to-purple-700 text-white py-2.5 px-4 rounded-lg hover:from-purple-700 hover:to-purple-800 transition-all font-medium text-sm flex items-center justify-center space-x-2"
          >
            <span>📅</span>
            <span>Schedule Showing</span>
          </button>
        </div>
      </div>

      {/* Contact Modal */}
      {showContactModal && (
        <EmailContactModal
          apartment={apartment}
          onClose={() => setShowContactModal(false)}
        />
      )}
      
      {/* Schedule Showing Modal */}
      {showScheduleModal && (
        <ScheduleShowingModal
          apartment={apartment}
          onClose={() => setShowScheduleModal(false)}
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
                  aria-label="Previous apartment image"
                >
                  ‹
                </button>
                <button
                  onClick={() => setCurrentImageIndex(prev => prev === apartment.images.length - 1 ? 0 : prev + 1)}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full w-10 h-10 flex items-center justify-center hover:bg-opacity-75"
                  aria-label="Next apartment image"
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
              <h2 className="text-3xl font-bold text-slate-800 mb-2">{apartment.title}</h2>
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
                  <div className="text-2xl font-bold text-slate-800">{parseInt(apartment.bathrooms)}</div>
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

          {/* Contact Information */}
          <div className="bg-purple-50 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-purple-800 mb-4">📞 Contact Information</h3>
            <div className="space-y-3 mb-4">
              <div className="flex items-center">
                <span className="text-purple-600 mr-3 text-lg">📧</span>
                <div>
                  <div className="text-sm text-gray-600">Email</div>
                  <a 
                    href={`mailto:${apartment.contact_email || 'placesfirm@gmail.com'}`}
                    className="font-medium text-purple-700 hover:text-purple-900"
                  >
                    {apartment.contact_email || 'placesfirm@gmail.com'}
                  </a>
                </div>
              </div>
              <div className="flex items-center">
                <span className="text-purple-600 mr-3 text-lg">📱</span>
                <div>
                  <div className="text-sm text-gray-600">Phone</div>
                  <a 
                    href={`tel:${apartment.contact_phone || '+1-646-408-8048'}`}
                    className="font-medium text-purple-700 hover:text-purple-900"
                  >
                    {apartment.contact_phone || '+1-646-408-8048'}
                  </a>
                </div>
              </div>
              <div className="flex items-center">
                <span className="text-purple-600 mr-3 text-lg">🏢</span>
                <div>
                  <div className="text-sm text-gray-600">Company</div>
                  <span className="font-medium text-gray-800">NoFeePlaces LLC</span>
                </div>
              </div>
            </div>
            <button
              onClick={() => setShowContactModal(true)}
              className="w-full bg-purple-600 text-white py-3 px-6 rounded-lg hover:bg-purple-700 transition-colors font-semibold"
            >
              📧 Send Message About This Apartment
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

  // Reset image index when apartment changes
  React.useEffect(() => {
    setCurrentImageIndex(0);
  }, [apartment?.id]);

  // Safe image navigation with proper bounds checking
  const handleNextImage = () => {
    if (!apartment.images || apartment.images.length === 0) return;
    
    setCurrentImageIndex((prev) => {
      const maxIndex = apartment.images.length - 1;
      return prev >= maxIndex ? 0 : prev + 1;
    });
  };

  const handlePrevImage = () => {
    if (!apartment.images || apartment.images.length === 0) return;
    
    setCurrentImageIndex((prev) => {
      const maxIndex = apartment.images.length - 1;
      return prev <= 0 ? maxIndex : prev - 1;
    });
  };

  return (
    <>
      {/* Dynamic Meta Tags for SEO */}
      <ListingMetaTags apartment={apartment} />
      
      {/* JSON-LD Structured Data for Rich Snippets */}
      <RealEstateListingSchema apartment={apartment} />
      
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
      <div 
        className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-800">{apartment.title}</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
            aria-label="Close apartment details"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Image Gallery */}
          <div className="relative h-96 bg-gray-200 rounded-lg overflow-hidden mb-6">
            <img
              src={
                (apartment.images && apartment.images.length > 0) 
                  ? apartment.images[Math.min(currentImageIndex, apartment.images.length - 1)]
                  : '/api/placeholder/800/400'
              }
              alt={apartment.title}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = '/api/placeholder/800/400';
              }}
            />
            
            {/* Image Navigation */}
            {apartment.images && apartment.images.length > 1 && (
              <>
                <button
                  onClick={handlePrevImage}
                  className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full w-10 h-10 flex items-center justify-center hover:bg-opacity-70"
                  aria-label="Previous image in gallery"
                >
                  ←
                </button>
                <button
                  onClick={handleNextImage}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white rounded-full w-10 h-10 flex items-center justify-center hover:bg-opacity-70"
                  aria-label="Next image in gallery"
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
              {/* Contact Information */}
              <div className="bg-purple-50 p-4 rounded-lg mb-6">
                <h3 className="text-lg font-semibold mb-3 text-purple-800">📞 Contact Information</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center">
                    <span className="text-purple-600 mr-2">📧</span>
                    <a 
                      href={`mailto:${apartment.contact_email || 'placesfirm@gmail.com'}`}
                      className="font-medium text-purple-700 hover:text-purple-900 hover:underline"
                      onClick={(e) => e.stopPropagation()}
                    >
                      {apartment.contact_email || 'placesfirm@gmail.com'}
                    </a>
                  </div>
                  <div className="flex items-center">
                    <span className="text-purple-600 mr-2">📱</span>
                    <a 
                      href={`tel:${apartment.contact_phone || '+1-646-408-8048'}`}
                      className="font-medium text-purple-700 hover:text-purple-900 hover:underline"
                      onClick={(e) => e.stopPropagation()}
                    >
                      {apartment.contact_phone || '+1-646-408-8048'}
                    </a>
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
                  className="w-full bg-teal-500 text-white py-3 px-4 rounded-lg hover:bg-teal-600 transition-colors font-semibold"
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
    </>
  );
};

// Continue with other components...
// (Rest of the components remain the same but with newsletter CTAs integrated where appropriate)