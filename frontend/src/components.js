import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './App';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Header Component with New PLACES Branding
const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <header className="bg-slate-800 shadow-sm border-b border-slate-700">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-3">
            {/* PLACES Logo */}
            <div className="w-10 h-10 bg-slate-700 rounded-lg flex items-center justify-center p-2">
              <svg viewBox="0 0 100 100" className="w-full h-full text-amber-100" fill="currentColor">
                <path d="M20 85 L25 80 L35 80 L35 70 L45 70 L45 60 L55 60 L55 70 L65 70 L65 80 L75 80 L80 85 L20 85 Z" stroke="currentColor" strokeWidth="2" fill="none"/>
                <rect x="40" y="40" width="20" height="20" rx="2" fill="currentColor"/>
                <rect x="45" y="45" width="4" height="4" fill="rgb(71 85 105)"/>
                <rect x="51" y="45" width="4" height="4" fill="rgb(71 85 105)"/>
                <rect x="45" y="51" width="4" height="4" fill="rgb(71 85 105)"/>
                <rect x="51" y="51" width="4" height="4" fill="rgb(71 85 105)"/>
                <path d="M25 50 L35 40 L45 50 L50 45 L55 50 L45 60 L35 50 Z" fill="currentColor"/>
                <rect x="37" y="52" width="6" height="4" fill="rgb(71 85 105)"/>
              </svg>
            </div>
            <div>
              <span className="text-2xl font-bold text-amber-100">PLACES</span>
              <div className="text-xs text-amber-200 -mt-1">NYC No Fee Apartments</div>
            </div>
          </div>

          <nav className="hidden md:flex items-center space-x-8">
            <a href="/" className="text-amber-100 hover:text-amber-200 transition-colors">Browse Apartments</a>
            <a href="#" className="text-amber-100 hover:text-amber-200 transition-colors">Neighborhoods</a>
            <a href="#" className="text-amber-100 hover:text-amber-200 transition-colors">No Fee Guide</a>
            
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <a href="/dashboard" className="text-amber-100 hover:text-amber-200 transition-colors">Dashboard</a>
                <a href="/saved-searches" className="text-amber-100 hover:text-amber-200 transition-colors">Saved Searches</a>
                <div className="relative group">
                  <button className="flex items-center space-x-2 text-amber-100 hover:text-amber-200 transition-colors">
                    <div className="w-8 h-8 bg-amber-600 rounded-full flex items-center justify-center">
                      <span className="text-slate-800 text-sm font-semibold">
                        {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
                      </span>
                    </div>
                    <span>{user?.full_name?.split(' ')[0] || 'User'}</span>
                  </button>
                  <div className="absolute right-0 mt-2 w-48 bg-slate-800 rounded-md shadow-lg border border-slate-700 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                    <div className="py-1">
                      <a href="/dashboard" className="block px-4 py-2 text-sm text-amber-100 hover:bg-slate-700">Dashboard</a>
                      <a href="/saved-searches" className="block px-4 py-2 text-sm text-amber-100 hover:bg-slate-700">Saved Searches</a>
                      <button 
                        onClick={logout}
                        className="block w-full text-left px-4 py-2 text-sm text-amber-100 hover:bg-slate-700"
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
                className="bg-amber-600 text-slate-800 px-4 py-2 rounded-lg hover:bg-amber-500 transition-colors font-semibold"
              >
                Sign In
              </button>
            )}
          </nav>

          <button 
            className="md:hidden text-amber-100"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>

        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-slate-700">
            <div className="flex flex-col space-y-4">
              <a href="/" className="text-amber-100 hover:text-amber-200 transition-colors">Browse Apartments</a>
              <a href="#" className="text-amber-100 hover:text-amber-200 transition-colors">Neighborhoods</a>
              {isAuthenticated ? (
                <>
                  <a href="/dashboard" className="text-amber-100 hover:text-amber-200 transition-colors">Dashboard</a>
                  <a href="/saved-searches" className="text-amber-100 hover:text-amber-200 transition-colors">Saved Searches</a>
                  <button 
                    onClick={logout}
                    className="text-left text-amber-100 hover:text-amber-200 transition-colors"
                  >
                    Sign Out
                  </button>
                </>
              ) : (
                <button 
                  onClick={() => setShowAuthModal(true)}
                  className="bg-amber-600 text-slate-800 px-4 py-2 rounded-lg hover:bg-amber-500 transition-colors w-fit font-semibold"
                >
                  Sign In
                </button>
              )}
            </div>
          </div>
        )}
      </div>
      
      {showAuthModal && <AuthModal onClose={() => setShowAuthModal(false)} />}
    </header>
  );
};

// Enhanced Hero Component with PLACES Branding
const Hero = ({ searchStats }) => {
  return (
    <section 
      className="relative bg-cover bg-center bg-no-repeat h-96"
      style={{
        backgroundImage: `linear-gradient(rgba(30, 41, 59, 0.8), rgba(30, 41, 59, 0.8)), url('https://images.unsplash.com/photo-1514565131-fce0801e5785')`
      }}
    >
      <div className="container mx-auto px-4 h-full flex items-center">
        <div className="max-w-2xl text-amber-100">
          <h1 className="text-5xl font-bold mb-4 leading-tight">
            Find Your Perfect Place in NYC
          </h1>
          <p className="text-xl mb-8 text-amber-200">
            Discover thousands of broker fee-free apartments across all five boroughs. 
            Save money and find your ideal home with PLACES.
          </p>
          <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
            <button 
              onClick={() => document.getElementById('search-section')?.scrollIntoView({behavior: 'smooth'})}
              className="bg-amber-600 text-slate-800 px-8 py-3 rounded-lg hover:bg-amber-500 transition-colors font-semibold"
            >
              Start Searching
            </button>
            <button className="bg-transparent border-2 border-amber-100 text-amber-100 px-8 py-3 rounded-lg hover:bg-amber-100 hover:text-slate-800 transition-colors font-semibold">
              Learn More
            </button>
          </div>
        </div>
      </div>
      
      {/* Enhanced Stats overlay with PLACES colors */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-r from-slate-800 to-slate-700 text-amber-100 py-4">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-3 text-center">
            <div>
              <div className="text-2xl font-bold text-amber-200">{searchStats?.total_apartments || '3'}+</div>
              <div className="text-sm text-amber-300">No Fee Apartments</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-amber-200">100%</div>
              <div className="text-sm text-amber-300">Verified Listings</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-amber-200">
                ${searchStats?.price_stats?.avg_price ? Math.round(searchStats.price_stats.avg_price / 1000) + 'K' : '4K'}
              </div>
              <div className="text-sm text-amber-300">Avg. Savings</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

// Advanced Search Filters Component with PLACES styling
const AdvancedSearchFilters = ({ filters, onFilterChange, onClearFilters, searchStats }) => {
  const neighborhoods = searchStats?.top_neighborhoods?.map(n => n._id) || [
    'Financial District', 'Midtown East', 'Brooklyn Heights', 'Long Island City', 
    'Upper East Side', 'Chelsea', 'SoHo', 'Williamsburg'
  ];

  const boroughs = ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island'];

  return (
    <section id="search-section" className="bg-slate-800 border-b border-slate-700 py-6">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div className="lg:col-span-2">
            <label className="block text-sm font-medium text-amber-200 mb-2">Search Location</label>
            <input
              type="text"
              placeholder="Search by address, neighborhood..."
              className="w-full px-3 py-2 border border-slate-600 bg-slate-700 text-amber-100 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent placeholder-amber-300"
              value={filters.search_term}
              onChange={(e) => onFilterChange('search_term', e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-amber-200 mb-2">Borough</label>
            <select
              className="w-full px-3 py-2 border border-slate-600 bg-slate-700 text-amber-100 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              value={filters.borough}
              onChange={(e) => onFilterChange('borough', e.target.value)}
            >
              <option value="">All Boroughs</option>
              {boroughs.map(borough => (
                <option key={borough} value={borough}>{borough}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-amber-200 mb-2">Neighborhood</label>
            <select
              className="w-full px-3 py-2 border border-slate-600 bg-slate-700 text-amber-100 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              value={filters.neighborhood}
              onChange={(e) => onFilterChange('neighborhood', e.target.value)}
            >
              <option value="">All Areas</option>
              {neighborhoods.map(neighborhood => (
                <option key={neighborhood} value={neighborhood}>{neighborhood}</option>
              ))}
            </select>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-amber-200 mb-2">Min Price</label>
            <input
              type="number"
              placeholder="$2,000"
              className="w-full px-3 py-2 border border-slate-600 bg-slate-700 text-amber-100 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent placeholder-amber-300"
              value={filters.min_price}
              onChange={(e) => onFilterChange('min_price', e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-amber-200 mb-2">Max Price</label>
            <input
              type="number"
              placeholder="$5,000"
              className="w-full px-3 py-2 border border-slate-600 bg-slate-700 text-amber-100 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent placeholder-amber-300"
              value={filters.max_price}
              onChange={(e) => onFilterChange('max_price', e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-amber-200 mb-2">Bedrooms</label>
            <select
              className="w-full px-3 py-2 border border-slate-600 bg-slate-700 text-amber-100 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              value={filters.bedrooms}
              onChange={(e) => onFilterChange('bedrooms', e.target.value)}
            >
              <option value="">Any</option>
              <option value="0">Studio</option>
              <option value="1">1 BR</option>
              <option value="2">2 BR</option>
              <option value="3">3 BR</option>
              <option value="4">4+ BR</option>
            </select>
          </div>
          
          <div className="flex items-end">
            <button 
              onClick={onClearFilters}
              className="w-full bg-slate-600 text-amber-100 px-4 py-2 rounded-lg hover:bg-slate-500 transition-colors"
            >
              Clear All
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

// Enhanced Apartment Card Component with PLACES styling
const ApartmentCard = ({ apartment }) => {
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  const [isFavorited, setIsFavorited] = useState(false);
  const { isAuthenticated } = useAuth();

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
    }
  };

  const handleViewDetails = () => {
    window.open(`/apartment/${apartment.id}`, '_blank');
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300 cursor-pointer border border-slate-200">
      <div className="relative" onClick={handleViewDetails}>
        <div className="aspect-w-16 aspect-h-9 bg-gray-200">
          <img
            src={apartment.images?.[0] || apartment.image}
            alt={apartment.title}
            className={`w-full h-48 object-cover transition-opacity duration-300 ${
              isImageLoaded ? 'opacity-100' : 'opacity-0'
            }`}
            onLoad={() => setIsImageLoaded(true)}
          />
          {!isImageLoaded && (
            <div className="absolute inset-0 bg-gray-200 animate-pulse flex items-center justify-center">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          )}
        </div>
        
        <div className="absolute top-3 left-3">
          <span className="bg-green-500 text-white px-2 py-1 rounded-full text-xs font-semibold">
            No Fee
          </span>
        </div>
        
        <div className="absolute top-3 right-3">
          <button 
            onClick={handleFavorite}
            className="bg-white bg-opacity-80 hover:bg-opacity-100 p-2 rounded-full transition-all"
          >
            <svg 
              className={`w-5 h-5 ${isFavorited ? 'text-red-500 fill-current' : 'text-gray-600 hover:text-red-500'}`} 
              fill={isFavorited ? 'currentColor' : 'none'} 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </button>
        </div>
      </div>
      
      <div className="p-4">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-lg font-semibold text-slate-800 line-clamp-2">
            {apartment.title}
          </h3>
          <span className="text-xl font-bold text-amber-600 ml-2">
            ${apartment.price?.toLocaleString() || apartment.price}
          </span>
        </div>
        
        <p className="text-slate-600 text-sm mb-3">
          {apartment.address}
        </p>
        
        <div className="flex items-center space-x-4 text-sm text-slate-500 mb-3">
          <div className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
            </svg>
            {apartment.bedrooms === 0 ? 'Studio' : `${apartment.bedrooms} bed`}
          </div>
          <div className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
            </svg>
            {apartment.bathrooms} bath
          </div>
          <div className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
            </svg>
            {apartment.sqft} sq ft
          </div>
        </div>
        
        <div className="flex flex-wrap gap-1 mb-3">
          {apartment.amenities?.slice(0, 3).map((amenity, index) => (
            <span key={index} className="bg-slate-100 text-slate-600 px-2 py-1 rounded-full text-xs">
              {amenity}
            </span>
          ))}
          {apartment.amenities?.length > 3 && (
            <span className="bg-slate-100 text-slate-600 px-2 py-1 rounded-full text-xs">
              +{apartment.amenities.length - 3} more
            </span>
          )}
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-green-600 font-medium">
            {apartment.available_date ? new Date(apartment.available_date).toLocaleDateString() : 'Available Now'}
          </span>
          <button 
            onClick={handleViewDetails}
            className="bg-amber-600 text-slate-800 px-4 py-2 rounded-lg hover:bg-amber-500 transition-colors text-sm font-medium"
          >
            View Details
          </button>
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
    <div className="fixed inset-0 bg-slate-900 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-slate-800">
            {isLogin ? 'Sign In to PLACES' : 'Join PLACES'}
          </h2>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600"
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
              <label className="block text-sm font-medium text-slate-700 mb-2">Full Name</label>
              <input
                type="text"
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                value={formData.fullName}
                onChange={(e) => setFormData(prev => ({...prev, fullName: e.target.value}))}
              />
            </div>
          )}

          <div className="mb-4">
            <label className="block text-sm font-medium text-slate-700 mb-2">Email</label>
            <input
              type="email"
              required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              value={formData.email}
              onChange={(e) => setFormData(prev => ({...prev, email: e.target.value}))}
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-slate-700 mb-2">Password</label>
            <input
              type="password"
              required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              value={formData.password}
              onChange={(e) => setFormData(prev => ({...prev, password: e.target.value}))}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-amber-600 text-slate-800 py-2 px-4 rounded-lg hover:bg-amber-500 disabled:bg-amber-400 transition-colors font-semibold"
          >
            {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        <div className="text-center mt-4">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-amber-600 hover:text-amber-800 text-sm"
          >
            {isLogin ? "Don't have an account? Join PLACES" : "Already have an account? Sign in"}
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
                    <button className="w-full bg-amber-600 text-slate-800 py-3 px-4 rounded-lg hover:bg-amber-500 transition-colors font-semibold">
                      Contact Agent
                    </button>
                    <button className="w-full bg-slate-200 text-slate-700 py-3 px-4 rounded-lg hover:bg-slate-300 transition-colors font-semibold">
                      Schedule Tour
                    </button>
                  </div>

                  <div className="mt-6 pt-6 border-t border-slate-200">
                    <p className="text-sm text-slate-600">
                      <strong>Available:</strong> {new Date(apartment.available_date).toLocaleDateString()}
                    </p>
                    <p className="text-sm text-slate-600 mt-1">
                      <strong>Neighborhood:</strong> {apartment.neighborhood}, {apartment.borough}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
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
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-slate-700 rounded-lg flex items-center justify-center p-2">
                <svg viewBox="0 0 100 100" className="w-full h-full text-amber-100" fill="currentColor">
                  <path d="M20 85 L25 80 L35 80 L35 70 L45 70 L45 60 L55 60 L55 70 L65 70 L65 80 L75 80 L80 85 L20 85 Z" stroke="currentColor" strokeWidth="2" fill="none"/>
                  <rect x="40" y="40" width="20" height="20" rx="2" fill="currentColor"/>
                  <rect x="45" y="45" width="4" height="4" fill="rgb(71 85 105)"/>
                  <rect x="51" y="45" width="4" height="4" fill="rgb(71 85 105)"/>
                  <rect x="45" y="51" width="4" height="4" fill="rgb(71 85 105)"/>
                  <rect x="51" y="51" width="4" height="4" fill="rgb(71 85 105)"/>
                  <path d="M25 50 L35 40 L45 50 L50 45 L55 50 L45 60 L35 50 Z" fill="currentColor"/>
                  <rect x="37" y="52" width="6" height="4" fill="rgb(71 85 105)"/>
                </svg>
              </div>
              <div>
                <span className="text-xl font-bold">PLACES</span>
                <div className="text-xs text-amber-200 -mt-1">NYC No Fee Apartments</div>
              </div>
            </div>
            <p className="text-amber-200 mb-4">
              Your trusted partner for finding no-fee apartments in New York City. 
              Save thousands on broker fees with our verified listings.
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
                info@places.nyc
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
        
        <div className="border-t border-slate-700 mt-8 pt-8 text-center text-amber-200">
          <p>&copy; 2025 PLACES. All rights reserved. | Privacy Policy | Terms of Service</p>
        </div>
      </div>
    </footer>
  );
};

// Export all components
export const Components = {
  Header,
  Hero,
  AdvancedSearchFilters,
  ApartmentCard,
  MapView,
  LoadingSpinner,
  Footer,
  AuthModal,
  UserDashboard,
  ApartmentDetails,
  SavedSearches
};