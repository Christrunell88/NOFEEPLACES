import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './App';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Header Component with New PLACES Branding
// Enhanced Header Component with luxury styling
const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <header className="sticky top-0 z-50 glass-dark border-b border-white/10">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-3 animate-slide-right">
            <div className="w-12 h-12 flex items-center justify-center animate-float">
              <svg 
                viewBox="0 0 200 200" 
                className="w-10 h-10 text-amber-400 shadow-glow" 
                fill="currentColor" 
                stroke="currentColor" 
                strokeWidth="4"
              >
                <g transform="translate(50, 80)">
                  <path 
                    d="M20 40 Q15 35 15 30 Q15 25 20 20 Q25 15 35 15 Q40 15 45 20 Q50 15 60 15 Q70 15 75 20 Q80 25 80 30 Q80 35 75 40 L75 50 Q70 60 60 60 L40 60 Q30 60 25 50 Z" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="6"
                  />
                  <g transform="translate(25, -25)">
                    <path d="M10 25 L20 15 L30 25" fill="none" strokeWidth="4"/>
                    <rect x="15" y="20" width="10" height="15" fill="none" strokeWidth="4"/>
                    <rect x="18" y="28" width="4" height="7" fill="none" strokeWidth="2"/>
                  </g>
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
              <div className="text-2xl font-bold heading-luxury leading-tight">Places</div>
              <div className="text-xs text-accent font-semibold leading-tight -mt-1">No Fee</div>
            </div>
          </div>

          <nav className="hidden md:flex items-center space-x-8">
            <a href="/" className="text-slate-200 hover:text-amber-400 transition-colors font-medium hover-lift">Browse Apartments</a>
            <a href="#" className="text-slate-200 hover:text-amber-400 transition-colors font-medium hover-lift">Neighborhoods</a>
            <a href="#" className="text-slate-200 hover:text-amber-400 transition-colors font-medium hover-lift">No Fee Guide</a>
            <a href="/admin/appointments" className="text-slate-200 hover:text-amber-400 transition-colors font-medium hover-lift">Admin</a>
            
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <a href="/dashboard" className="text-slate-200 hover:text-amber-400 transition-colors font-medium hover-lift">Dashboard</a>
                <a href="/saved-searches" className="text-slate-200 hover:text-amber-400 transition-colors font-medium hover-lift">Saved Searches</a>
                <div className="relative group">
                  <button className="flex items-center space-x-2 text-slate-200 hover:text-amber-400 transition-colors">
                    <div className="w-8 h-8 gradient-gold rounded-full flex items-center justify-center animate-glow">
                      <span className="text-slate-800 text-sm font-semibold">
                        {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
                      </span>
                    </div>
                    <span className="font-medium">{user?.full_name?.split(' ')[0] || 'User'}</span>
                  </button>
                  <div className="absolute right-0 mt-2 w-48 glass-dark rounded-lg shadow-luxury border border-white/10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300">
                    <div className="py-2">
                      <a href="/dashboard" className="block px-4 py-2 text-sm text-slate-200 hover:text-amber-400 hover:bg-white/5 transition-colors">Dashboard</a>
                      <a href="/saved-searches" className="block px-4 py-2 text-sm text-slate-200 hover:text-amber-400 hover:bg-white/5 transition-colors">Saved Searches</a>
                      <button 
                        onClick={logout}
                        className="block w-full text-left px-4 py-2 text-sm text-slate-200 hover:text-amber-400 hover:bg-white/5 transition-colors"
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
                className="btn-primary text-sm px-6 py-2 animate-glow"
              >
                Sign In
              </button>
            )}
          </nav>

          <button 
            className="md:hidden text-slate-200 hover:text-amber-400 transition-colors"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>

        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-white/10 glass-dark animate-slide-up">
            <div className="flex flex-col space-y-4">
              <a href="/" className="text-slate-200 hover:text-amber-400 transition-colors font-medium">Browse Apartments</a>
              <a href="#" className="text-slate-200 hover:text-amber-400 transition-colors font-medium">Neighborhoods</a>
              <a href="/admin/appointments" className="text-slate-200 hover:text-amber-400 transition-colors font-medium">Admin</a>
              {isAuthenticated ? (
                <>
                  <a href="/dashboard" className="text-slate-200 hover:text-amber-400 transition-colors font-medium">Dashboard</a>
                  <a href="/saved-searches" className="text-slate-200 hover:text-amber-400 transition-colors font-medium">Saved Searches</a>
                  <button 
                    onClick={logout}
                    className="text-left text-slate-200 hover:text-amber-400 transition-colors font-medium"
                  >
                    Sign Out
                  </button>
                </>
              ) : (
                <button 
                  onClick={() => setShowAuthModal(true)}
                  className="btn-primary text-sm px-6 py-2 w-fit"
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
// Enhanced Hero Component with luxury styling
const Hero = ({ searchStats }) => {
  return (
    <section 
      className="hero-section relative bg-cover bg-center bg-no-repeat min-h-screen w-full flex items-center animate-slide-up"
      style={{
        backgroundImage: `linear-gradient(135deg, rgba(15, 23, 42, 0.85), rgba(30, 41, 59, 0.75)), url('https://images.unsplash.com/photo-1514565131-fce0801e5785?q=80&w=2070')`
      }}
    >
      <div className="absolute inset-0 bg-gradient-to-r from-black/20 via-transparent to-black/20"></div>
      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          <div className="animate-slide-up">
            <h1 className="text-6xl md:text-7xl font-bold mb-6 leading-tight heading-luxury">
              Find Your Perfect
              <span className="block gradient-text animate-glow">
                NYC Home
              </span>
            </h1>
            <p className="text-xl md:text-2xl mb-12 text-slate-300 max-w-3xl mx-auto leading-relaxed">
              Discover <span className="text-accent font-semibold">No Fee Apartments</span> across all five boroughs. 
              Save money and find your ideal home with the most trusted platform in NYC.
            </p>
            <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-6">
              <button 
                onClick={() => document.getElementById('search-section')?.scrollIntoView({behavior: 'smooth'})}
                className="btn-primary text-lg px-10 py-4 text-slate-800 font-bold hover-lift animate-glow"
              >
                Start Your Search
                <svg className="w-5 h-5 ml-2 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
              <button className="btn-secondary text-lg px-10 py-4 font-semibold hover-lift">
                View All Listings
                <svg className="w-5 h-5 ml-2 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

// Compact Search Component inspired by StreetEasy
const AdvancedSearchFilters = ({ filters, onFilterChange, onClearFilters, searchStats }) => {
  const neighborhoods = searchStats?.top_neighborhoods?.map(n => n._id) || [
    'Financial District', 'Midtown East', 'Brooklyn Heights', 'Long Island City', 
    'Upper East Side', 'Chelsea', 'SoHo', 'Williamsburg'
  ];

  const boroughs = ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island'];

  return (
    <section id="search-section" className="relative -mt-16 z-20 pb-8">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          {/* Compact Search Bar - StreetEasy Style */}
          <div className="glass-dark rounded-2xl p-4 shadow-luxury">
            <div className="flex flex-col lg:flex-row gap-3">
              {/* Main Search Input */}
              <div className="flex-1">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <svg className="h-5 w-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  <input
                    type="text"
                    placeholder="Search neighborhoods, addresses..."
                    className="input-luxury w-full pl-12 pr-4 py-3 text-base"
                    value={filters.search_term}
                    onChange={(e) => onFilterChange('search_term', e.target.value)}
                  />
                </div>
              </div>

              {/* Location Filter */}
              <div className="w-full lg:w-48">
                <select
                  className="input-luxury w-full py-3"
                  value={filters.borough}
                  onChange={(e) => onFilterChange('borough', e.target.value)}
                >
                  <option value="">All Boroughs</option>
                  {boroughs.map(borough => (
                    <option key={borough} value={borough}>{borough}</option>
                  ))}
                </select>
              </div>

              {/* Price Range */}
              <div className="flex gap-2 w-full lg:w-80">
                <input
                  type="number"
                  placeholder="Min"
                  className="input-luxury w-full py-3 text-center"
                  value={filters.min_price}
                  onChange={(e) => onFilterChange('min_price', e.target.value)}
                />
                <div className="flex items-center px-2">
                  <span className="text-slate-400">–</span>
                </div>
                <input
                  type="number"
                  placeholder="Max"
                  className="input-luxury w-full py-3 text-center"
                  value={filters.max_price}
                  onChange={(e) => onFilterChange('max_price', e.target.value)}
                />
              </div>

              {/* Bedrooms */}
              <div className="w-full lg:w-32">
                <select
                  className="input-luxury w-full py-3"
                  value={filters.bedrooms}
                  onChange={(e) => onFilterChange('bedrooms', e.target.value)}
                >
                  <option value="">Beds</option>
                  <option value="0">Studio</option>
                  <option value="1">1+</option>
                  <option value="2">2+</option>
                  <option value="3">3+</option>
                </select>
              </div>

              {/* Search Button */}
              <button className="btn-primary px-8 py-3 hover-lift animate-glow whitespace-nowrap">
                Search
                <svg className="w-4 h-4 ml-2 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </div>

            {/* Advanced Filters Toggle */}
            <div className="flex justify-between items-center mt-3 pt-3 border-t border-white/10">
              <div className="flex items-center space-x-4 text-sm">
                <button 
                  onClick={onClearFilters}
                  className="text-slate-400 hover:text-amber-400 transition-colors"
                >
                  Clear filters
                </button>
                <span className="text-slate-500">•</span>
                <span className="text-slate-400">
                  {searchStats?.total_apartments || '30'} apartments found
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-xs text-slate-500">Sort by:</span>
                <select className="bg-transparent text-amber-400 text-sm border-none focus:outline-none cursor-pointer">
                  <option value="newest">Newest</option>
                  <option value="price_low">Price: Low to High</option>
                  <option value="price_high">Price: High to Low</option>
                  <option value="size">Size</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

// Enhanced Apartment Card Component with luxury styling
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
    window.location.href = `/apartment/${apartment.id}`;
  };

  const handleCallAgent = (e) => {
    e.stopPropagation();
    if (apartment.contact_info?.phone) {
      window.open(`tel:${apartment.contact_info.phone}`, '_self');
    } else {
      alert('Contact information not available');
    }
  };

  const handleEmailAgent = (e) => {
    e.stopPropagation();
    if (apartment.contact_info?.email) {
      const subject = encodeURIComponent(`Inquiry about ${apartment.title} - ${apartment.address}`);
      const body = encodeURIComponent(`Hi Chris,

I'm interested in learning more about this apartment:

${apartment.title}
${apartment.address}
${apartment.bedrooms === 0 ? 'Studio' : apartment.bedrooms + ' bedroom'}, ${apartment.bathrooms} bathroom
$${apartment.price?.toLocaleString()}/month
${apartment.sqft} sq ft

Please let me know about availability and when I can schedule a viewing.

Thank you!`);
      
      window.open(`mailto:${apartment.contact_info.email}?subject=${subject}&body=${body}`, '_self');
    } else {
      alert('Contact information not available');
    }
  };

  return (
    <div className="card-luxury hover:shadow-glow transition-all duration-500 cursor-pointer group animate-slide-up">
      <div className="relative overflow-hidden rounded-2xl mb-4" onClick={handleViewDetails}>
        <div className="aspect-w-16 aspect-h-9 bg-gradient-to-br from-slate-200 to-slate-300">
          <img
            src={apartment.images?.[0] || apartment.image}
            alt={apartment.title}
            className={`w-full h-56 object-cover transition-all duration-500 group-hover:scale-110 ${
              isImageLoaded ? 'opacity-100' : 'opacity-0'
            }`}
            onLoad={() => setIsImageLoaded(true)}
          />
          {!isImageLoaded && (
            <div className="absolute inset-0 bg-gradient-to-br from-slate-200 to-slate-300 animate-pulse flex items-center justify-center">
              <svg className="w-12 h-12 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2-2z" />
              </svg>
            </div>
          )}
          
          {/* Gradient overlay for better text visibility */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        </div>
        
        {/* No Fee Badge */}
        <div className="absolute top-4 left-4">
          <span className="badge badge-success animate-glow">
            NO FEE
          </span>
        </div>
        
        {/* Favorite Button */}
        <div className="absolute top-4 right-4">
          <button 
            onClick={handleFavorite}
            className="glass p-3 rounded-full transition-all hover:scale-110 hover:shadow-glow"
          >
            <svg 
              className={`w-5 h-5 transition-colors ${
                isFavorited ? 'text-red-400 fill-current' : 'text-white hover:text-red-400'
              }`} 
              fill={isFavorited ? 'currentColor' : 'none'} 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </button>
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
      
      <div className="px-2">
        <div className="mb-3">
          <h3 className="text-xl font-bold text-slate-100 mb-2 line-clamp-2 group-hover:text-amber-400 transition-colors">
            {apartment.title}
          </h3>
          <p className="text-slate-400 text-sm flex items-center">
            <svg className="w-4 h-4 mr-2 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {apartment.address}
          </p>
        </div>
        
        {/* Property Details */}
        <div className="flex items-center justify-between mb-4 text-sm text-slate-300">
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <svg className="w-4 h-4 mr-1 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
              </svg>
              <span className="font-medium">
                {apartment.bedrooms === 0 ? 'Studio' : `${apartment.bedrooms} bed`}
              </span>
            </div>
            <div className="flex items-center">
              <svg className="w-4 h-4 mr-1 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
              </svg>
              <span className="font-medium">{apartment.bathrooms} bath</span>
            </div>
            <div className="flex items-center">
              <svg className="w-4 h-4 mr-1 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
              <span className="font-medium">{apartment.sqft} sq ft</span>
            </div>
          </div>
        </div>
        
        {/* Amenities */}
        <div className="flex flex-wrap gap-2 mb-4">
          {apartment.amenities?.slice(0, 3).map((amenity, index) => (
            <span key={index} className="bg-white/5 text-slate-300 px-3 py-1 rounded-full text-xs font-medium border border-white/10">
              {amenity}
            </span>
          ))}
          {apartment.amenities?.length > 3 && (
            <span className="bg-amber-500/20 text-amber-400 px-3 py-1 rounded-full text-xs font-medium border border-amber-500/30">
              +{apartment.amenities.length - 3} more
            </span>
          )}
        </div>
        
        {/* Action Bar */}
        <div className="flex justify-between items-center pt-4 border-t border-white/10">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
            <span className="text-sm text-green-400 font-medium">Available Now</span>
          </div>
          <div className="flex gap-2">
            <button 
              onClick={handleCallAgent}
              className="bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-500 transition-colors text-xs font-medium hover-lift flex items-center"
              title="Call Chris Trunell"
            >
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              Call
            </button>
            <button 
              onClick={handleEmailAgent}
              className="bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-500 transition-colors text-xs font-medium hover-lift flex items-center"
              title="Email chris@places.nyc"
            >
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              Email
            </button>
            <button 
              onClick={handleViewDetails}
              className="btn-primary text-xs px-3 py-2 hover-lift"
            >
              Details
              <svg className="w-3 h-3 ml-1 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </button>
          </div>
        </div>
      </div>
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

      alert('Appointment booked successfully! You will receive a confirmation email shortly.');
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to book appointment';
      alert(errorMessage);
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
    if (apartment?.contact_info?.email) {
      const subject = encodeURIComponent(`Inquiry about ${apartment.title} - ${apartment.address}`);
      const body = encodeURIComponent(`Hi ${apartment.contact_info.broker || 'there'},

I'm interested in learning more about the apartment at ${apartment.address}. 

Property Details:
- ${apartment.title}
- ${apartment.bedrooms === 0 ? 'Studio' : apartment.bedrooms + ' bedroom'}, ${apartment.bathrooms} bathroom
- $${apartment.price?.toLocaleString()}/month
- ${apartment.sqft} sq ft

Please let me know about availability and when I can schedule a viewing.

Thank you!`);
      
      window.open(`mailto:${apartment.contact_info.email}?subject=${subject}&body=${body}`, '_self');
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

      {/* Contact Modal */}
      {showContactModal && (
        <div className="fixed inset-0 bg-slate-900 bg-opacity-75 flex items-center justify-center z-50">
          <div className="glass-dark rounded-2xl p-6 max-w-md w-full mx-4 shadow-luxury">
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-lg font-semibold text-slate-100">Contact Information</h4>
              <button
                onClick={() => setShowContactModal(false)}
                className="text-slate-400 hover:text-slate-200 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {apartment?.contact_info && (
              <div className="space-y-4 mb-6">
                <div className="text-center p-4 glass rounded-lg">
                  <h5 className="font-semibold text-amber-400 mb-2">{apartment.contact_info.broker}</h5>
                  <div className="space-y-2">
                    <p className="text-slate-300">📞 {apartment.contact_info.phone}</p>
                    <p className="text-slate-300">📧 {apartment.contact_info.email}</p>
                  </div>
                </div>
                
                <div className="flex flex-col gap-3">
                  <button 
                    onClick={handleContactAgent}
                    className="btn-primary w-full py-2 text-sm hover-lift"
                  >
                    Call Now
                  </button>
                  <button 
                    onClick={handleEmailContact}
                    className="btn-secondary w-full py-2 text-sm hover-lift"
                  >
                    Send Email
                  </button>
                  <button 
                    onClick={() => setShowContactModal(false)}
                    className="text-slate-400 hover:text-slate-200 text-sm transition-colors"
                  >
                    Close
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
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
          <p>&copy; 2025 NoFeePlaces.com. All rights reserved. | Privacy Policy | Terms of Service</p>
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
  SavedSearches,
  CalendarBooking,
  AdminAppointments
};