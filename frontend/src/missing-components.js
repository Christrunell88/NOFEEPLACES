import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import axios from 'axios';
import { ApartmentDetailsModal } from './components';
import { useAuth } from './auth';
import { 
  trackContactForm, 
  trackHeroAction, 
  trackNewsletterSignup, 
  trackUserAuthentication,
  trackPageView 
} from './analytics';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

// Hero Component with Image Carousel
export const Hero = () => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const heroImages = [
    // Woman in modern apartment - living room
    'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=1200&h=600&fit=crop&auto=format&v=3',
    // Woman in Brooklyn apartment - lifestyle shot
    'https://images.unsplash.com/photo-1618219908412-a29a1bb7b86e?w=1200&h=600&fit=crop&auto=format&v=3',
    // Woman in apartment - relaxing scene
    'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1200&h=600&fit=crop&auto=format&v=3'
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prev) => (prev + 1) % heroImages.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const scrollToListings = () => {
    trackHeroAction('scroll', 'Browse Apartments');
    window.scrollTo({ top: 1200, behavior: 'smooth' });
  };

  return (
    <section className="relative h-96 overflow-hidden">
      {/* Background Image Carousel */}
      <div className="absolute inset-0">
        {heroImages.map((image, index) => (
          <div
            key={index}
            className={`absolute inset-0 transition-opacity duration-1000 ${
              index === currentImageIndex ? 'opacity-100' : 'opacity-0'
            }`}
          >
            <img
              src={image}
              alt={`NYC Apartment ${index + 1}`}
              className="w-full h-full object-cover"
            />
          </div>
        ))}
      </div>
      
      {/* Dark Overlay */}
      <div className="absolute inset-0 bg-black bg-opacity-50"></div>
      
      {/* Content */}
      <div className="relative z-10 flex items-center justify-center h-full">
        <div className="text-center text-white px-4 max-w-3xl">
          <h1 className="text-5xl md:text-6xl font-bold mb-8 leading-tight">
            Find Your Perfect NYC Apartment
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-blue-100 font-light">
            No broker fees. No hidden costs.
          </p>
          <button 
            onClick={scrollToListings}
            className="bg-blue-600 text-white px-10 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors shadow-xl"
          >
            Start Your Search
          </button>
        </div>
      </div>
      
      {/* Image Indicators */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
        {heroImages.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentImageIndex(index)}
            className={`w-3 h-3 rounded-full transition-colors ${
              index === currentImageIndex ? 'bg-yellow-400' : 'bg-white bg-opacity-50'
            }`}
          />
        ))}
      </div>
    </section>
  );
};

// Featured Apartments Preview Section
export const FeaturedApartments = () => {
  const [featuredApartments, setFeaturedApartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedApartment, setSelectedApartment] = useState(null);

  useEffect(() => {
    const fetchFeaturedApartments = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/api/apartments?limit=6&featured=true`);
        if (response.data && response.data.apartments) {
          setFeaturedApartments(response.data.apartments);
        }
      } catch (error) {
        console.error('Error fetching featured apartments:', error);
        // Fallback to regular apartments if featured fails
        try {
          const fallbackResponse = await axios.get(`${BACKEND_URL}/api/apartments?limit=6`);
          if (fallbackResponse.data && fallbackResponse.data.apartments) {
            setFeaturedApartments(fallbackResponse.data.apartments);
          }
        } catch (fallbackError) {
          console.error('Error fetching fallback apartments:', fallbackError);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchFeaturedApartments();
  }, []);

  if (loading) {
    return (
      <section className="py-12 bg-slate-50">
        <div className="container mx-auto px-4">
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-12 bg-slate-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-slate-800 mb-2">
            Available Now
          </h2>
          <p className="text-slate-600">No fees. No waiting. Move in today.</p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto mb-8">
          {featuredApartments.slice(0, 6).map((apartment, index) => (
            <div 
              key={apartment.id} 
              className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden group cursor-pointer"
              onClick={() => window.scrollTo({ top: 1200, behavior: 'smooth' })}
            >
              <div className="relative h-48 overflow-hidden">
                <img
                  src={apartment.images && apartment.images[0] ? apartment.images[0] : 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&h=600&fit=crop'}
                  alt={apartment.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute top-3 right-3 flex gap-2">
                  <span className="bg-orange-500 text-white px-2 py-1 rounded-full text-xs font-semibold">
                    NO FEE
                  </span>
                </div>
              </div>
              
              <div className="p-5">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-semibold text-lg text-slate-800 line-clamp-1">
                      {apartment.bedrooms === 0 ? 'Studio' : `${apartment.bedrooms}BR`} in {apartment.neighborhood || 'NYC'}
                    </h3>
                    <p className="text-slate-600 text-sm">{apartment.location}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-slate-800">
                      ${apartment.price?.toLocaleString()}
                    </div>
                    <div className="text-xs text-slate-500">/month</div>
                  </div>
                </div>
                
                <div className="flex items-center gap-4 text-sm text-slate-600 mb-3">
                  {apartment.bedrooms !== undefined && (
                    <span>{apartment.bedrooms === 0 ? 'Studio' : `${apartment.bedrooms} bed`}</span>
                  )}
                  {apartment.bathrooms && (
                    <span>{apartment.bathrooms} bath</span>
                  )}
                  {apartment.sqft && (
                    <span>{apartment.sqft} sqft</span>
                  )}
                </div>
                
                <button 
                  onClick={() => setSelectedApartment(apartment)}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg font-medium transition-colors"
                >
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
        
        <div className="text-center">
          <button 
            onClick={() => window.scrollTo({ top: 1200, behavior: 'smooth' })}
            className="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-900 text-white px-8 py-3 rounded-lg font-semibold transition-colors"
          >
            <span>View All {featuredApartments.length}+ Apartments</span>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </button>
        </div>
      </div>
      
      {/* Apartment Details Modal */}
      {selectedApartment && (
        <ApartmentDetailsModal 
          apartment={selectedApartment}
          onClose={() => setSelectedApartment(null)}
        />
      )}
    </section>
  );
};

// Compact Search Box (Zillow-style)
export const AdvancedSearchFilters = ({ filters, onFilterChange, apartmentCount }) => {
  return (
    <div className="bg-white shadow-sm border-b py-4">
      <div className="container mx-auto px-4">
        {/* Main Search Bar */}
        <div className="flex flex-col md:flex-row items-center gap-3 max-w-5xl mx-auto">
          {/* Location Search */}
          <div className="flex-1 relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              placeholder="Enter an address, neighborhood, city, or ZIP code"
              value={filters.search || ''}
              onChange={(e) => onFilterChange('search', e.target.value)}
              style={{ color: '#1f2937', fontSize: '16px' }}
              className="w-full pl-10 pr-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 bg-white"
            />
          </div>

          {/* Price Range */}
          <div className="flex items-center gap-3">
            <div className="text-center">
              <label className="block text-sm font-medium text-gray-700 mb-1">Min Price</label>
              <select
                value={filters.min_price || ''}
                onChange={(e) => onFilterChange('min_price', e.target.value)}
                className="px-3 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-base bg-white min-w-[110px] text-gray-900"
              >
                <option value="">Any Min</option>
                <option value="1000">$1,000</option>
                <option value="2000">$2,000</option>
                <option value="3000">$3,000</option>
                <option value="4000">$4,000</option>
                <option value="5000">$5,000</option>
                <option value="7500">$7,500</option>
                <option value="10000">$10,000</option>
              </select>
            </div>
            
            <div className="text-center">
              <label className="block text-sm font-medium text-gray-700 mb-1">Max Price</label>
              <select
                value={filters.max_price || ''}
                onChange={(e) => onFilterChange('max_price', e.target.value)}
                className="px-3 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-base bg-white min-w-[110px] text-gray-900"
              >
                <option value="">Any Max</option>
                <option value="3000">$3,000</option>
                <option value="4000">$4,000</option>
                <option value="5000">$5,000</option>
                <option value="7500">$7,500</option>
                <option value="10000">$10,000</option>
                <option value="15000">$15,000</option>
                <option value="25000">$25,000+</option>
              </select>
            </div>
          </div>

          {/* Bedrooms */}
          <div className="text-center">
            <label className="block text-sm font-medium text-gray-700 mb-1">Bedrooms</label>
            <select
              value={filters.bedrooms || ''}
              onChange={(e) => onFilterChange('bedrooms', e.target.value)}
              className="px-3 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-base bg-white min-w-[120px] text-gray-900"
            >
              <option value="">Any Beds</option>
              <option value="0">Studio</option>
              <option value="1">1 Bedroom</option>
              <option value="2">2 Bedrooms</option>
              <option value="3">3 Bedrooms</option>
              <option value="4">4+ Bedrooms</option>
            </select>
          </div>

          {/* Search Button */}
          <button 
            onClick={() => {
              // Search is handled automatically by React state changes
              console.log('Search clicked with filters:', filters);
            }}
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors whitespace-nowrap text-base"
          >
            🔍 Search
          </button>
        </div>

        {/* Results Count */}
        <div className="mt-4 text-center">
          <p className="text-base text-gray-700">
            <span className="font-bold text-blue-600">{apartmentCount}</span> no fee apartments found
          </p>
        </div>
      </div>
    </div>
  );
};

// Map View Component
export const MapView = ({ apartments }) => {
  return (
    <div className="h-96 bg-gray-200 rounded-lg flex items-center justify-center">
      <div className="text-center">
        <div className="text-4xl mb-4">🗺️</div>
        <h3 className="text-xl font-semibold text-gray-700 mb-2">Map View</h3>
        <p className="text-gray-600">
          Showing {apartments.length} apartments on map
        </p>
        <p className="text-sm text-gray-500 mt-2">
          Interactive map coming soon
        </p>
      </div>
    </div>
  );
};

// Footer Component
export const Footer = () => {
  return (
    <footer className="bg-black text-white py-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-yellow-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">🏢</span>
              </div>
              <div>
                <div className="font-bold text-lg">
                  No Fee <span className="text-yellow-400">Places</span>
                </div>
              </div>
            </div>
            <p className="text-gray-400">
              Find your perfect NYC apartment without broker fees.
            </p>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li><Link to="/" className="text-gray-400 hover:text-white">Home</Link></li>
              <li><Link to="/apartments" className="text-gray-400 hover:text-white">Apartments</Link></li>
              <li><Link to="/blog" className="text-gray-400 hover:text-white">Blog</Link></li>
              <li><Link to="/tenant/browse" className="text-gray-400 hover:text-white">Browse Listings</Link></li>
              <li><Link to="/tenant/list-apartment" className="text-gray-400 hover:text-white">List Your Place</Link></li>
              <li><Link to="/landlord/login" className="text-gray-400 hover:text-white">Owner Portal</Link></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Neighborhoods</h3>
            <ul className="space-y-2">
              <li><span className="text-gray-400">Manhattan</span></li>
              <li><span className="text-gray-400">Brooklyn</span></li>
              <li><span className="text-gray-400">Queens</span></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Contact</h3>
            <ul className="space-y-2">
              <li><span className="text-gray-400">support@nofeeplaces.com</span></li>
              <li><span className="text-gray-400">(646) 408-8048</span></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-800 mt-8 pt-8 text-center">
          <p className="text-gray-400">
            © 2025 NoFeePlaces.com. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

// Loading Spinner
export const LoadingSpinner = () => {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
    </div>
  );
};

// Import SocialAuth component
import SocialAuthButtons from './SocialAuth';

// Auth Modal with Social Login
export const AuthModal = ({ onClose }) => {
  const [showSocialAuth, setShowSocialAuth] = useState(true);
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
      if (isLogin) {
        const result = await login(formData.email, formData.password);
        if (result.success) {
          onClose();
        } else {
          setError(result.error);
        }
      } else {
        const result = await register(formData.email, formData.password, formData.fullName);
        if (result.success) {
          onClose();
        } else {
          setError(result.error);
        }
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSocialSuccess = (user) => {
    console.log('Social auth success:', user);
    onClose();
  };

  const handleSocialError = (error) => {
    setError(error);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            {showSocialAuth ? 'Sign In' : (isLogin ? 'Sign In' : 'Sign Up')}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg">
            {error}
          </div>
        )}

        {showSocialAuth ? (
          <div>
            <SocialAuthButtons 
              onSuccess={handleSocialSuccess}
              onError={handleSocialError}
              onClose={onClose}
            />
            
            <div className="mt-6 text-center">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">Or continue with email</span>
                </div>
              </div>
              
              <button
                onClick={() => setShowSocialAuth(false)}
                className="mt-4 w-full text-center text-blue-600 hover:text-blue-800 font-medium"
              >
                Use Email & Password
              </button>
            </div>
          </div>
        ) : (
          <div>
            <form onSubmit={handleSubmit} className="space-y-4">
              {!isLogin && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.fullName}
                    onChange={(e) => setFormData(prev => ({ ...prev, fullName: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              )}
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                  style={{ color: '#1f2937', fontSize: '16px' }}
                  className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-gray-900 bg-white"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  required
                  value={formData.password}
                  onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Sign Up')}
              </button>
            </form>

            <div className="mt-4 text-center">
              <button
                onClick={() => setIsLogin(!isLogin)}
                className="text-purple-600 hover:text-purple-800"
              >
                {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
              </button>
            </div>

            <div className="mt-4 text-center">
              <button
                onClick={() => setShowSocialAuth(true)}
                className="text-blue-600 hover:text-blue-800 text-sm"
              >
                ← Back to social login options
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Placeholder components for the remaining missing components
export const UserDashboard = ({ user }) => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold mb-6">Welcome, {user?.full_name || 'User'}!</h1>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Your Favorites</h2>
        <p className="text-gray-600">View your saved apartments</p>
      </div>
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Saved Searches</h2>
        <p className="text-gray-600">Manage your search preferences</p>
      </div>
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
        <p className="text-gray-600">Track your apartment views</p>
      </div>
    </div>
  </div>
);

export const SavedSearches = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold mb-6">Saved Searches</h1>
    <div className="bg-white rounded-lg shadow-lg p-6">
      <p className="text-gray-600">Your saved searches will appear here.</p>
    </div>
  </div>
);

export const AdminAppointments = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold mb-6">Admin Appointments</h1>
    <div className="bg-white rounded-lg shadow-lg p-6">
      <p className="text-gray-600">Appointment management dashboard.</p>
    </div>
  </div>
);

export const AIChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-4 right-4 bg-purple-600 text-white rounded-full w-12 h-12 flex items-center justify-center hover:bg-purple-700 transition-colors z-40"
      >
        💬
      </button>
      
      {isOpen && (
        <div className="fixed bottom-20 right-4 bg-white rounded-lg shadow-xl w-80 h-96 z-50 border">
          <div className="bg-purple-600 text-white p-4 rounded-t-lg">
            <div className="flex justify-between items-center">
              <h3 className="font-semibold">AI Assistant</h3>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white hover:text-gray-200"
              >
                ×
              </button>
            </div>
          </div>
          <div className="p-4 h-80 flex items-center justify-center">
            <p className="text-gray-600 text-center">
              AI chatbot coming soon! <br />
              Get help finding your perfect apartment.
            </p>
          </div>
        </div>
      )}
    </>
  );
};

export const FavoritesPage = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold mb-6">Your Favorites</h1>
    <div className="bg-white rounded-lg shadow-lg p-6">
      <p className="text-gray-600">Your favorite apartments will appear here.</p>
    </div>
  </div>
);

export const ApartmentComparison = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold mb-6">Compare Apartments</h1>
    <div className="bg-white rounded-lg shadow-lg p-6">
      <p className="text-gray-600">Compare selected apartments side by side.</p>
    </div>
  </div>
);

export const ToastProvider = ({ children }) => {
  return <div>{children}</div>;
};

export const ErrorBoundary = ({ children }) => {
  return <div>{children}</div>;
};

export const CompleteGuideNoFeeApartments = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-4xl font-bold mb-6">Complete Guide to No Fee Apartments in NYC</h1>
    <div className="prose max-w-none">
      <p className="text-lg text-gray-600 mb-6">
        Your comprehensive guide to finding and securing no fee apartments in New York City.
      </p>
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-semibold mb-4">What are No Fee Apartments?</h2>
        <p className="text-gray-600 mb-4">
          No fee apartments are rental properties where the landlord or building owner pays the broker commission instead of the tenant.
        </p>
        <h2 className="text-2xl font-semibold mb-4">Benefits of No Fee Apartments</h2>
        <ul className="list-disc list-inside text-gray-600 space-y-2">
          <li>Save thousands of dollars in broker fees</li>
          <li>Lower upfront costs when moving</li>
          <li>More money available for security deposits and moving expenses</li>
        </ul>
      </div>
    </div>
  </div>
);

export const BlogList = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBlogPosts();
  }, []);

  const fetchBlogPosts = async () => {
    try {
      const response = await axios.get(`${API}/blog`);
      setPosts(response.data.posts || []);
    } catch (error) {
      console.error('Failed to fetch blog posts:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8 text-center">NYC Apartment Blog</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {posts.map(post => (
          <Link
            key={post.id}
            to={`/blog/${post.slug}`}
            className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
          >
            {post.featured_image && (
              <img
                src={post.featured_image}
                alt={post.title}
                className="w-full h-48 object-cover"
              />
            )}
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-2 hover:text-purple-600">
                {post.title}
              </h2>
              <p className="text-gray-600 mb-4 line-clamp-3">
                {post.excerpt}
              </p>
              <div className="text-sm text-gray-500">
                {new Date(post.created_at).toLocaleDateString()}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export const BlogPost = ({ slug }) => {
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const { slug: routeSlug } = useParams();
  
  // Use slug from props or route params
  const actualSlug = slug || routeSlug;

  useEffect(() => {
    if (actualSlug) {
      fetchBlogPost();
    }
  }, [actualSlug]);

  const fetchBlogPost = async () => {
    try {
      const response = await axios.get(`${API}/blog/${actualSlug}`);
      setPost(response.data);
    } catch (error) {
      console.error('Failed to fetch blog post:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!post) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">Post Not Found</h1>
        <p className="text-gray-600">The blog post you're looking for doesn't exist.</p>
      </div>
    );
  }

  return (
    <article className="container mx-auto px-4 py-8 max-w-4xl">
      {post.featured_image && (
        <img
          src={post.featured_image}
          alt={post.title}
          className="w-full h-64 object-cover rounded-lg mb-8"
        />
      )}
      
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">{post.title}</h1>
        <div className="flex items-center space-x-4 text-gray-600">
          <span>By {post.author}</span>
          <span>•</span>
          <span>{new Date(post.created_at).toLocaleDateString()}</span>
          <span>•</span>
          <span>{post.category}</span>
        </div>
      </header>

      <div 
        className="prose max-w-none"
        dangerouslySetInnerHTML={{ __html: post.content }}
      />
    </article>
  );
};

// Email Contact Modal
export const EmailContactModal = ({ apartment, onClose }) => {
  const { isAuthenticated } = useAuth();
  
  // Use neighborhood for non-authenticated users, full address for authenticated users
  const locationInfo = isAuthenticated 
    ? (apartment.address || apartment.location)
    : (apartment.neighborhood || apartment.location?.split(',')[0] || 'this property');

  const [formData, setFormData] = useState({
    senderName: '',
    senderEmail: '',
    senderPhone: '',
    message: `Hi, I'm interested in the apartment in ${locationInfo}. Please provide more information about availability and scheduling a viewing.`,
    subject: apartment ? `Interest in ${apartment.title}` : 'Inquiry from NoFeePlaces.com'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState({ type: '', message: '' });

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setStatus({ type: '', message: '' });

    try {
      const API_URL = process.env.REACT_APP_BACKEND_URL || 'https://rentalnobroker.preview.emergentagent.com';
      
      // Prepare apartment details for email
      const apartmentDetails = apartment ? {
        title: apartment.title,
        neighborhood: apartment.neighborhood,
        price: apartment.price,
        bedrooms: apartment.bedrooms
      } : null;

      // Prepare email data
      const emailData = {
        to: 'placesfirm@gmail.com',
        subject: formData.subject,
        sender_name: formData.senderName,
        sender_email: formData.senderEmail,
        sender_phone: formData.senderPhone,
        message: formData.message,
        apartment_details: apartmentDetails
      };

      const response = await axios.post(`${API_URL}/api/send-contact-email`, emailData);

      setStatus({ 
        type: 'success', 
        message: 'Your message has been sent successfully! We\'ll get back to you soon.' 
      });

      // Track successful contact form submission
      try {
        trackContactForm(formData, apartment);
      } catch (trackError) {
        console.log('Analytics tracking failed:', trackError);
      }

      // Reset form after successful submission
      setTimeout(() => {
        onClose();
      }, 2000);

    } catch (error) {
      console.error('Error sending email:', error);
      setStatus({ 
        type: 'error', 
        message: error.response?.data?.detail || 'Failed to send message. Please try again.' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            Send Message
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        {apartment && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-800 mb-2">About this listing:</h3>
            <p className="text-sm text-gray-600">{apartment.title}</p>
            {apartment.neighborhood && (
              <p className="text-sm text-gray-500">{apartment.neighborhood}</p>
            )}
            {apartment.price && (
              <p className="text-sm font-medium text-green-600">${apartment.price}/month</p>
            )}
          </div>
        )}

        {status.message && (
          <div className={`mb-4 p-3 rounded-lg text-sm ${
            status.type === 'success' 
              ? 'bg-green-50 border border-green-200 text-green-700' 
              : 'bg-red-50 border border-red-200 text-red-700'
          }`}>
            {status.message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Name *
            </label>
            <input
              type="text"
              name="senderName"
              required
              value={formData.senderName}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your full name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Email *
            </label>
            <input
              type="email"
              name="senderEmail"
              required
              value={formData.senderEmail}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="your.email@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Phone Number
            </label>
            <input
              type="tel"
              name="senderPhone"
              value={formData.senderPhone}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="(555) 123-4567"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subject
            </label>
            <input
              type="text"
              name="subject"
              value={formData.subject}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Message *
            </label>
            <textarea
              name="message"
              required
              rows="4"
              value={formData.message}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Please enter your message here..."
            />
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-600 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Sending...' : 'Send Message'}
            </button>
          </div>
        </form>

        <div className="mt-4 text-xs text-gray-500 text-center">
          <p>
            Message will be sent to placesfirm@gmail.com
          </p>
        </div>
      </div>
    </div>
  );
};