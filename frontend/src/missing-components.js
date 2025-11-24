import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import axios from 'axios';
import { ApartmentDetailsModal } from './components';
import { useAuth } from './RobustAuth';
import { FooterWordMark } from './WordMark';
import FeedbackModal from './FeedbackModal';
import { 
  trackContactForm, 
  trackHeroAction, 
  trackNewsletterSignup, 
  trackUserAuthentication,
  trackPageView 
} from './analytics';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

// Hero Component with Elegant Apartment Carousel and Condensed CTAs
export const Hero = ({ setShowAuthModal, totalApartments = 70 }) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const heroImages = [
    {
      url: 'https://images.unsplash.com/photo-1607147728511-570d2aff5487?auto=format&fit=crop&w=1200&h=600&q=85',
      alt: 'Young independent professional woman in urban NYC setting',
      style: 'Urban Professional'
    },
    {
      url: 'https://images.unsplash.com/photo-1607147728331-ecf4ff0bd437?auto=format&fit=crop&w=1200&h=600&q=85',
      alt: 'Attractive smart millennial finding her dream NYC apartment',
      style: 'Modern Apartment Hunter'
    },
    {
      url: 'https://images.unsplash.com/photo-1731273613974-4906a0bce337?auto=format&fit=crop&w=1200&h=600&q=85',
      alt: 'Confident independent young professional ready for NYC living',
      style: 'NYC Success'
    },
    {
      url: 'https://images.unsplash.com/photo-1626976270409-e03cdcfd5f87?auto=format&fit=crop&w=1200&h=600&q=85',
      alt: 'Young healthy professional woman in stylish apartment',
      style: 'Apartment Living'
    },
    {
      url: 'https://images.pexels.com/photos/4559748/pexels-photo-4559748.jpeg?auto=compress&cs=tinysrgb&w=1200&h=600&fit=crop',
      alt: 'Smart sexy young professional navigating NYC lifestyle',
      style: 'NYC Lifestyle'
    },
    {
      url: 'https://images.pexels.com/photos/7464198/pexels-photo-7464198.jpeg?auto=compress&cs=tinysrgb&w=1200&h=600&fit=crop',
      alt: 'Independent young person enjoying modern NYC apartment',
      style: 'No-Fee Living'
    }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prev) => (prev + 1) % heroImages.length);
    }, 5000); // 5 seconds per image for elegant pacing
    return () => clearInterval(interval);
  }, [heroImages.length]);

  const goToImage = (index) => {
    setCurrentImageIndex(index);
    trackHeroAction('carousel_navigation', `Image ${index + 1} - ${heroImages[index].style}`);
  };

  return (
    <section className="relative h-[500px] overflow-hidden">
      {/* Background Image Carousel */}
      <div className="absolute inset-0">
        {heroImages.map((image, index) => (
          <div
            key={index}
            className={`absolute inset-0 transition-opacity duration-1000 ease-in-out ${
              index === currentImageIndex ? 'opacity-100' : 'opacity-0'
            }`}
            style={{
              backgroundImage: `url(${image.url})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center'
            }}
          />
        ))}
      </div>
      
      {/* Elegant overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-black/30 via-black/20 to-black/30"></div>
      
      {/* Content with Condensed CTAs */}
      <div className="relative z-10 flex items-center justify-center h-full">
        <div className="text-center text-white px-4 max-w-4xl">
          {/* Main Headline */}
          <h1 className="text-3xl md:text-5xl font-bold mb-4 leading-tight">
            <span className="block">Find NYC Apartments</span>
            <span className="block text-emerald-400">With Zero Fees</span>
          </h1>
          
          {/* Condensed Value Prop */}
          <p className="text-lg md:text-xl mb-8 text-white font-light opacity-90 max-w-2xl mx-auto">
            {totalApartments}+ verified no-fee apartments • Save $3,000+ on broker fees
          </p>
        </div>
      </div>
      
      {/* Elegant Carousel Indicators */}
      <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 flex space-x-3 z-20">
        {heroImages.map((image, index) => (
          <button
            key={index}
            onClick={() => goToImage(index)}
            className={`group relative transition-all duration-300 z-20 ${
              index === currentImageIndex ? 'scale-110' : 'hover:scale-105'
            }`}
            aria-label={`View ${image.style} apartment`}
          >
            <div className={`w-3 h-3 rounded-full transition-all duration-300 ${
              index === currentImageIndex 
                ? 'bg-white shadow-lg' 
                : 'bg-white bg-opacity-60 hover:bg-opacity-80'
            }`} />
          </button>
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
  const { isAuthenticated } = useAuth();

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
              className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden group"
            >
              <div 
                className="relative h-48 overflow-hidden cursor-pointer"
                onClick={() => setSelectedApartment(apartment)}
              >
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
                
                {/* Hover Overlay with "View Details" hint */}
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-300 flex items-center justify-center">
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 text-white font-medium">
                    <span className="bg-teal-500 px-3 py-2 rounded-lg shadow-lg text-sm">View Details</span>
                  </div>
                </div>
              </div>
              
              <div className="p-5">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-semibold text-lg text-slate-800 line-clamp-1">
                      {apartment.bedrooms === 0 ? 'Studio' : `${apartment.bedrooms}BR`} in {apartment.neighborhood || 'NYC'}
                    </h3>
                    <p className="text-slate-600 text-sm">
                      {isAuthenticated 
                        ? (apartment.location || apartment.address || `${apartment.neighborhood}, ${apartment.borough}`)
                        : (apartment.neighborhood && apartment.borough ? `${apartment.neighborhood}, ${apartment.borough}` : apartment.neighborhood || apartment.borough || 'NYC')
                      }
                    </p>
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
                    <span>{parseInt(apartment.bathrooms)} bath</span>
                  )}
                  {apartment.sqft && (
                    <span>{apartment.sqft} sqft</span>
                  )}
                </div>
                
                {/* Clean card bottom - click image to view details */}
              </div>
            </div>
          ))}
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
            className="bg-teal-500 hover:bg-teal-600 text-white px-8 py-3 rounded-lg font-semibold transition-colors whitespace-nowrap text-base"
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
  const [showFeedbackModal, setShowFeedbackModal] = React.useState(false);

  return (
    <>
      <footer className="bg-black text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="mb-4">
                <FooterWordMark 
                  linkTo="/"
                  tagline="ZERO BROKER FEES • NYC RENTALS"
                />
              </div>
              <p className="text-gray-400">
                Find your perfect NYC apartment without broker fees. Professional platform connecting renters with verified no-fee properties.
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
                <li><span className="text-gray-400">placesfirm@gmail.com</span></li>
                <li><span className="text-gray-400">(646) 408-8048</span></li>
                <li>
                  <button 
                    onClick={() => setShowFeedbackModal(true)}
                    className="text-gray-400 hover:text-white underline"
                  >
                    Send Feedback
                  </button>
                </li>
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

      {/* Feedback Modal */}
      {showFeedbackModal && (
        <FeedbackModal 
          isOpen={showFeedbackModal}
          onClose={() => setShowFeedbackModal(false)}
        />
      )}
    </>
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

// Import BulletproofAuthModal component
import BulletproofAuthModal from './BulletproofAuthModal';

// Auth Modal - Simple Email/Password Authentication
export const AuthModal = ({ onClose }) => {
  return <BulletproofAuthModal onClose={onClose} />;
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
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      text: "👋 Hi! I'm NoFeeBot, your AI assistant for finding no-fee apartments in NYC. How can I help you today?",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  const API_URL = process.env.REACT_APP_BACKEND_URL;

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    
    // Add user message to chat
    const newUserMessage = {
      type: 'user',
      text: userMessage,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/chat`, {
        message: userMessage,
        session_id: sessionId
      });

      // Update session ID if it's the first message
      if (!sessionId) {
        setSessionId(response.data.session_id);
      }

      // Add bot response to chat
      const botMessage = {
        type: 'bot',
        text: response.data.response,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        type: 'bot',
        text: "I apologize, but I'm experiencing technical difficulties. Please try again or contact us at placesfirm@gmail.com for assistance.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
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

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-4 left-4 bg-teal-500 text-white rounded-full w-16 h-16 flex items-center justify-center hover:bg-teal-600 transition-all duration-300 z-[9999] shadow-lg hover:shadow-xl transform hover:scale-105"
        aria-label="Open AI Assistant"
      >
        <span className="text-2xl">🤖</span>
      </button>
      
      {isOpen && (
        <div className="fixed bottom-24 left-4 bg-white rounded-lg shadow-xl w-96 h-[500px] z-[9999] border flex flex-col">
          {/* Header */}
          <div className="bg-teal-500 text-white p-4 rounded-t-lg flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <span className="text-xl">🤖</span>
              <div>
                <h3 className="font-semibold">NoFeeBot</h3>
                <p className="text-xs text-teal-100">AI Apartment Assistant</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:text-gray-200 text-xl font-bold"
            >
              ×
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs px-3 py-2 rounded-lg text-sm ${
                    message.type === 'user'
                      ? 'bg-teal-500 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.text}</p>
                  <p className={`text-xs mt-1 ${
                    message.type === 'user' ? 'text-teal-100' : 'text-gray-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-800 px-3 py-2 rounded-lg text-sm">
                  <div className="flex items-center space-x-1">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-teal-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-teal-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-teal-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-xs text-gray-500 ml-2">NoFeeBot is typing...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="border-t p-4">
            <div className="flex space-x-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about NYC apartments..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent text-sm"
                disabled={isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || isLoading}
                className="bg-teal-500 text-white px-4 py-2 rounded-lg hover:bg-teal-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span className="text-sm">📤</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

// FavoritesPage moved to separate file: /app/frontend/src/FavoritesPage.js

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
      const API_URL = process.env.REACT_APP_BACKEND_URL;
      
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
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
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
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
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
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
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
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
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
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
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
              className="flex-1 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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

// Show Your Place Modal Component
export const ShowYourPlaceModal = ({ onClose }) => {
  const [formData, setFormData] = useState({
    title: '',
    address: '',
    neighborhood: '',
    borough: '',
    price: '',
    bedrooms: '',
    bathrooms: '',
    sqft: '',
    description: '',
    amenities: '',
    contact_email: '',
    contact_phone: '',
    lease_terms: '',
    move_in_date: '',
    pet_policy: '',
    utilities: ''
  });
  const [images, setImages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState({ type: '', message: '' });
  const [currentStep, setCurrentStep] = useState(1);

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files);
    if (files.length + images.length > 10) {
      setStatus({ type: 'error', message: 'Maximum 10 images allowed' });
      return;
    }

    files.forEach(file => {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        setStatus({ type: 'error', message: 'Each image must be under 5MB' });
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        setImages(prev => [...prev, {
          file,
          preview: e.target.result,
          name: file.name
        }]);
      };
      reader.readAsDataURL(file);
    });
  };

  const removeImage = (index) => {
    setImages(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setStatus({ type: '', message: '' });

    try {
      const API_URL = process.env.REACT_APP_BACKEND_URL;
      
      // Create FormData for file upload
      const submitData = new FormData();
      
      // Add form fields
      Object.keys(formData).forEach(key => {
        if (formData[key]) {
          submitData.append(key, formData[key]);
        }
      });

      // Add images
      images.forEach((image, index) => {
        submitData.append(`images`, image.file);
      });

      const response = await axios.post(`${API_URL}/api/landlord/submit-listing`, submitData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setStatus({ 
        type: 'success', 
        message: 'Your listing has been submitted successfully! We\'ll review it and get back to you within 24 hours.' 
      });

      // Reset form after successful submission
      setTimeout(() => {
        onClose();
      }, 3000);

    } catch (error) {
      console.error('Error submitting listing:', error);
      setStatus({ 
        type: 'error', 
        message: error.response?.data?.detail || 'Failed to submit listing. Please try again.' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  const nextStep = () => {
    if (currentStep < 3) setCurrentStep(currentStep + 1);
  };

  const prevStep = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <div>
            <h2 className="text-3xl font-bold text-gray-800">Show Your Place</h2>
            <p className="text-gray-600 mt-1">List your no-fee apartment and reach thousands of renters</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
            aria-label="Close listing form"
          >
            ×
          </button>
        </div>

        {/* Progress Steps */}
        <div className="px-6 py-4 bg-gray-50">
          <div className="flex items-center justify-center space-x-4">
            {[1, 2, 3].map((step) => (
              <div key={step} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                  currentStep >= step 
                    ? 'bg-emerald-500 text-white' 
                    : 'bg-gray-300 text-gray-600'
                }`}>
                  {step}
                </div>
                <span className={`ml-2 text-sm ${
                  currentStep >= step ? 'text-emerald-600 font-medium' : 'text-gray-500'
                }`}>
                  {step === 1 ? 'Basic Info' : step === 2 ? 'Details & Photos' : 'Contact & Submit'}
                </span>
                {step < 3 && <div className="w-8 h-0.5 bg-gray-300 mx-4"></div>}
              </div>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {status.message && (
            <div className={`mb-6 p-4 rounded-lg text-sm ${
              status.type === 'success' 
                ? 'bg-green-50 border border-green-200 text-green-700' 
                : 'bg-red-50 border border-red-200 text-red-700'
            }`}>
              {status.message}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Step 1: Basic Information */}
            {currentStep === 1 && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">Basic Information</h3>
                
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Listing Title *
                    </label>
                    <input
                      type="text"
                      name="title"
                      required
                      value={formData.title}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                      placeholder="e.g., Beautiful 2BR in Manhattan"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Monthly Rent *
                    </label>
                    <input
                      type="number"
                      name="price"
                      required
                      value={formData.price}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                      placeholder="3500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Address *
                  </label>
                  <input
                    type="text"
                    name="address"
                    required
                    value={formData.address}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    placeholder="123 Main Street, New York, NY 10001"
                  />
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Neighborhood *
                    </label>
                    <input
                      type="text"
                      name="neighborhood"
                      required
                      value={formData.neighborhood}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                      placeholder="e.g., Upper East Side"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Borough *
                    </label>
                    <select
                      name="borough"
                      required
                      value={formData.borough}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    >
                      <option value="">Select Borough</option>
                      <option value="Manhattan">Manhattan</option>
                      <option value="Brooklyn">Brooklyn</option>
                      <option value="Queens">Queens</option>
                      <option value="Bronx">Bronx</option>
                      <option value="Staten Island">Staten Island</option>
                    </select>
                  </div>
                </div>

                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Bedrooms *
                    </label>
                    <select
                      name="bedrooms"
                      required
                      value={formData.bedrooms}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    >
                      <option value="">Select</option>
                      <option value="0">Studio</option>
                      <option value="1">1 Bedroom</option>
                      <option value="2">2 Bedrooms</option>
                      <option value="3">3 Bedrooms</option>
                      <option value="4">4+ Bedrooms</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Bathrooms *
                    </label>
                    <select
                      name="bathrooms"
                      required
                      value={formData.bathrooms}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    >
                      <option value="">Select</option>
                      <option value="1">1 Bathroom</option>
                      <option value="1.5">1.5 Bathrooms</option>
                      <option value="2">2 Bathrooms</option>
                      <option value="2.5">2.5 Bathrooms</option>
                      <option value="3">3+ Bathrooms</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Square Feet
                    </label>
                    <input
                      type="number"
                      name="sqft"
                      value={formData.sqft}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                      placeholder="800"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Step 2: Details & Photos */}
            {currentStep === 2 && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">Details & Photos</h3>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description *
                  </label>
                  <textarea
                    name="description"
                    required
                    rows="4"
                    value={formData.description}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    placeholder="Describe your apartment, its features, and what makes it special..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Amenities
                  </label>
                  <textarea
                    name="amenities"
                    rows="3"
                    value={formData.amenities}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    placeholder="List amenities separated by commas (e.g., Dishwasher, Laundry in unit, Gym, Doorman)"
                  />
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Move-in Date
                    </label>
                    <input
                      type="date"
                      name="move_in_date"
                      value={formData.move_in_date}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Lease Terms
                    </label>
                    <select
                      name="lease_terms"
                      value={formData.lease_terms}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    >
                      <option value="">Select</option>
                      <option value="12 months">12 months</option>
                      <option value="24 months">24 months</option>
                      <option value="Flexible">Flexible</option>
                    </select>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Pet Policy
                    </label>
                    <select
                      name="pet_policy"
                      value={formData.pet_policy}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    >
                      <option value="">Select</option>
                      <option value="Pets allowed">Pets allowed</option>
                      <option value="No pets">No pets</option>
                      <option value="Cats only">Cats only</option>
                      <option value="Dogs only">Dogs only</option>
                      <option value="Case by case">Case by case</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Utilities
                    </label>
                    <input
                      type="text"
                      name="utilities"
                      value={formData.utilities}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                      placeholder="e.g., Heat & hot water included"
                    />
                  </div>
                </div>

                {/* Photo Upload */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Photos (Up to 10 images, 5MB each)
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                    <input
                      type="file"
                      multiple
                      accept="image/*"
                      onChange={handleImageUpload}
                      className="hidden"
                      id="image-upload"
                    />
                    <label htmlFor="image-upload" className="cursor-pointer">
                      <div className="text-4xl text-gray-400 mb-2">📷</div>
                      <p className="text-gray-600">Click to upload photos</p>
                      <p className="text-sm text-gray-500 mt-1">JPG, PNG, or GIF up to 5MB each</p>
                    </label>
                  </div>

                  {/* Image Previews */}
                  {images.length > 0 && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                      {images.map((image, index) => (
                        <div key={index} className="relative">
                          <img
                            src={image.preview}
                            alt={`Preview ${index + 1}`}
                            className="w-full h-24 object-cover rounded-lg"
                          />
                          <button
                            type="button"
                            onClick={() => removeImage(index)}
                            className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm hover:bg-red-600"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Step 3: Contact & Submit */}
            {currentStep === 3 && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">Contact Information</h3>
                
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Contact Email *
                    </label>
                    <input
                      type="email"
                      name="contact_email"
                      required
                      value={formData.contact_email}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                      placeholder="your.email@example.com"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Contact Phone *
                    </label>
                    <input
                      type="tel"
                      name="contact_phone"
                      required
                      value={formData.contact_phone}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                      placeholder="(555) 123-4567"
                    />
                  </div>
                </div>

                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                  <h4 className="font-semibold text-amber-800 mb-2">📋 Listing Review Process</h4>
                  <ul className="text-sm text-emerald-700 space-y-1">
                    <li>• Your listing will be reviewed within 24 hours</li>
                    <li>• We'll verify the no-fee status and property details</li>
                    <li>• Once approved, your listing will go live on our platform</li>
                    <li>• You'll receive inquiries directly via email and phone</li>
                  </ul>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-800 mb-2">💰 No Fee Guarantee</h4>
                  <p className="text-sm text-blue-700">
                    By submitting this listing, you confirm that this is a genuine no-fee apartment where 
                    tenants will not be charged any broker fees or finder's fees.
                  </p>
                </div>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-200">
              <div>
                {currentStep > 1 && (
                  <button
                    type="button"
                    onClick={prevStep}
                    className="px-6 py-3 text-gray-600 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    ← Previous
                  </button>
                )}
              </div>

              <div>
                {currentStep < 3 ? (
                  <button
                    type="button"
                    onClick={nextStep}
                    className="px-8 py-3 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors font-semibold"
                  >
                    Next Step →
                  </button>
                ) : (
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="px-8 py-3 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? 'Submitting...' : '🚀 Submit Listing'}
                  </button>
                )}
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
