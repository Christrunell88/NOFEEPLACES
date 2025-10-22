import React, { useState, useEffect } from "react";
import "./App.css";
import './accessibility.css';
import { BrowserRouter, Routes, Route, Navigate, useParams } from "react-router-dom";
import axios from "axios";
import * as Components from './components';
import { AuthProvider, useAuth } from './auth';
import { 
  trackPageView, 
  trackApartmentSearch, 
  trackFilterUsage, 
  trackListingImpression,
  trackPerformanceMetric,
  trackVisitorArrival
} from './analytics';
import { OrganizationSchema } from './StructuredData';
import BoroughPage from './BoroughPage';
import { 
  LandlordPricing, 
  LandlordRegistration, 
  LandlordDashboard, 
  PaymentSuccess 
} from './LandlordPortal';
import { 
  LandlordLogin, 
  DemoLandlordAccess 
} from './LandlordAuth';
import { 
  AddListing, 
  ViewListings 
} from './LandlordListings';
import { FeaturedApartments } from './missing-components';
import SEOAffordableSection from './SEOAffordableSection';
import VisitorTracker from './VisitorTracker';
import { AnalyticsDashboard } from './AnalyticsDashboard';
import TenantListingPage from './TenantListing';
import TenantBrowsePage from './TenantBrowse';
import CategoryPage from './CategoryPage';
import FloatingFeedbackButton from './FloatingFeedbackButton';
import { AboutUsPage, WhyNoFeePage, ContactUsPage, LetsTalkPage } from './StaticPages';
import ConversionOptimizedHome from './ConversionOptimizedHome';
import ConversionHero from './ConversionHero';
import AdminLogin from './AdminLogin';
import AdminDashboard from './AdminDashboard';
import LeadGenChatbot from './LeadGenChatbot';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const { 
  Header, 
  Hero, 
  AdvancedSearchFilters, 
  ApartmentCard, 
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
  ToastProvider,
  ErrorBoundary,
  CompleteGuideNoFeeApartments,
  BlogList,
  BlogPost,
  NewsletterPage
} = Components;

const Home = () => {
  const [apartments, setApartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchFilters, setSearchFilters] = useState({
    search: '',
    min_price: '',
    max_price: '',
    bedrooms: '',
    neighborhood: '',
    borough: ''
  });
  const [sortBy, setSortBy] = useState('price');  // New: sorting field
  const [sortOrder, setSortOrder] = useState('asc');  // New: sorting order
  const [viewMode, setViewMode] = useState('list');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalApartments, setTotalApartments] = useState(0);
  const [searchStats, setSearchStats] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const { isAuthenticated, user, logout } = useAuth();

  // Debug: Log what isAuthenticated returns in the main component
  console.log('Main App Debug:', { isAuthenticated, user });

  // SEO Enhancement: Dynamic page title and meta updates
  useEffect(() => {
    // Update page title based on search results
    if (typeof window !== 'undefined') {
      const baseTitle = "No Fee Apartments NYC 2025 | Zero Broker Fee Rentals";
      let dynamicTitle = baseTitle;
      
      if (searchFilters.neighborhood) {
        dynamicTitle = `No Fee Apartments ${searchFilters.neighborhood} NYC | ${baseTitle}`;
      }
      if (searchFilters.borough) {
        dynamicTitle = `${searchFilters.borough} No Fee Apartments NYC | ${baseTitle}`;
      }
      if (totalApartments > 0) {
        dynamicTitle = `${totalApartments} ${dynamicTitle}`;
      }
      
      document.title = dynamicTitle;
      
      // Update meta description dynamically
      const metaDesc = document.querySelector('meta[name="description"]');
      if (metaDesc) {
        let description = `Find luxury no fee apartments NYC 2025 with zero broker fees. Browse ${totalApartments || 1000}+ verified`;
        if (searchFilters.neighborhood) description += ` ${searchFilters.neighborhood}`;
        if (searchFilters.borough) description += ` ${searchFilters.borough}`;
        description += ` no broker fee rentals directly from property owners. Save $3,000+ on NYC apartments.`;
        metaDesc.setAttribute('content', description);
      }
    }
  }, [searchFilters, totalApartments]);

  useEffect(() => {
    fetchApartments();
    fetchSearchStats();
  }, [searchFilters, currentPage, sortBy, sortOrder]);  // Added sortBy and sortOrder dependencies

  // Listen for neighborhood search events from SEO section
  useEffect(() => {
    const handleNeighborhoodSearch = (event) => {
      const { borough, minPrice } = event.detail;
      
      // Update search filters with borough and minimum price
      setSearchFilters(prev => ({
        ...prev,
        search: borough, // Search for the borough name
        minPrice: minPrice.toString(), // Set minimum price filter
        maxPrice: '', // Clear max price to show all apartments above min price
      }));
      
      // Reset to first page
      setCurrentPage(1);
    };

    window.addEventListener('neighborhoodSearch', handleNeighborhoodSearch);
    
    return () => {
      window.removeEventListener('neighborhoodSearch', handleNeighborhoodSearch);
    };
  }, []);

  // Listen for auth modal open events from other components
  useEffect(() => {
    const handleOpenAuthModal = () => {
      setShowAuthModal(true);
    };

    window.addEventListener('openAuthModal', handleOpenAuthModal);
    
    return () => {
      window.removeEventListener('openAuthModal', handleOpenAuthModal);
    };
  }, []);

  // Track visitor arrival on initial load
  useEffect(() => {
    trackVisitorArrival();
  }, []); // Empty dependency array means this runs once on mount

  const fetchApartments = async () => {
    setLoading(true);
    const searchStartTime = performance.now();
    
    try {
      const params = new URLSearchParams();
      
      Object.entries(searchFilters).forEach(([key, value]) => {
        if (value !== '' && value !== null && value !== undefined) {
          params.append(key, value);
        }
      });
      
      params.append('page', currentPage);
      params.append('limit', 50); // Reduced to prevent server errors
      params.append('sort_by', sortBy);  // Add sorting parameters
      params.append('sort_order', sortOrder);

      const response = await axios.get(`${API}/apartments?${params}`);
      setApartments(response.data.apartments);
      setTotalApartments(response.data.total);
      
      // Track search performance and results
      const searchTime = performance.now() - searchStartTime;
      trackPerformanceMetric('apartment_search_time', Math.round(searchTime));
      
      // Track search event if filters are applied
      const hasActiveFilters = Object.values(searchFilters).some(value => value !== '' && value !== null);
      if (hasActiveFilters) {
        trackApartmentSearch(searchFilters);
      }
      
      // Track listing impressions
      if (response.data.apartments?.length > 0) {
        const listContext = hasActiveFilters ? 'search_results' : 'browse_all';
        trackListingImpression(response.data.apartments, listContext);
      }
      
    } catch (error) {
      console.error('Failed to fetch apartments:', error);
      setApartments([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchSearchStats = async () => {
    try {
      const response = await axios.get(`${API}/apartments/search/stats`);
      setSearchStats(response.data);
    } catch (error) {
      console.error('Failed to fetch search stats:', error);
    }
  };

  const handleFilterChange = (key, value) => {
    setSearchFilters(prev => ({
      ...prev,
      [key]: value
    }));
    setCurrentPage(1);
    
    // Track filter usage
    if (value !== '' && value !== null && value !== undefined) {
      trackFilterUsage(key, value);
    }
  };

  const clearFilters = () => {
    setSearchFilters({
      search: '',
      min_price: '',
      max_price: '',
      bedrooms: '',
      neighborhood: '',
      borough: ''
    });
    setCurrentPage(1);
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Organization JSON-LD Schema for Homepage */}
      <OrganizationSchema />
      
      {/* Skip Navigation Links */}
      <a 
        href="#main-content" 
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-blue-600 text-white px-4 py-2 rounded-lg z-50 focus:outline-none focus:ring-2 focus:ring-blue-300"
      >
        Skip to main content
      </a>
      <a 
        href="#navigation-menu" 
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-32 bg-blue-600 text-white px-4 py-2 rounded-lg z-50 focus:outline-none focus:ring-2 focus:ring-blue-300"
      >
        Skip to navigation
      </a>
      
      <Header 
        isAuthenticated={isAuthenticated}
        user={user}
        logout={logout}
        setShowAuthModal={setShowAuthModal}
      />
      <Hero setShowAuthModal={setShowAuthModal} />
      
      {/* CATEGORY BUTTONS - MOVED UP FOR PROMINENCE */}
      <section className="bg-gradient-to-b from-slate-50 to-white py-16">
        <div className="container mx-auto px-4 md:px-6">
          <div className="text-center mb-10">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-3">Find Your Perfect Apartment</h2>
            <p className="text-lg text-gray-600">Browse by category to discover apartments that match your budget and lifestyle</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
            {/* Best Value Button */}
            <a
              href="/apartments/best-value"
              className="group relative bg-gradient-to-br from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 rounded-2xl p-8 transition-all duration-300 hover:shadow-2xl hover:scale-105 text-center overflow-hidden border border-indigo-500/20"
            >
              <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-10 transition-opacity"></div>
              <div className="relative z-10">
                <div className="text-5xl mb-4">⭐</div>
                <h3 className="text-2xl font-bold text-white mb-2">Best Value</h3>
                <p className="text-indigo-100 text-sm mb-3">Top Deals</p>
                <div className="text-3xl font-bold text-white mb-3">5 Apartments</div>
                <p className="text-xs text-indigo-100">Luxury amenities at great prices</p>
                <div className="mt-4 inline-block bg-white/20 backdrop-blur-sm px-4 py-1 rounded-full text-white text-xs font-semibold">
                  Top 20% Value
                </div>
              </div>
            </a>
            
            {/* Budget Button */}
            <a
              href="/apartments/budget"
              className="group relative bg-gradient-to-br from-emerald-700 to-emerald-800 hover:from-emerald-800 hover:to-emerald-900 rounded-2xl p-8 transition-all duration-300 hover:shadow-2xl hover:scale-105 text-center overflow-hidden border border-emerald-600/20"
            >
              <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-10 transition-opacity"></div>
              <div className="relative z-10">
                <div className="text-5xl mb-4">💰</div>
                <h3 className="text-2xl font-bold text-white mb-2">Budget</h3>
                <p className="text-emerald-100 text-sm mb-3">Under $4,500/mo</p>
                <div className="text-3xl font-bold text-white mb-3">129 Apartments</div>
                <p className="text-xs text-emerald-100">Perfect for budget-conscious renters</p>
                <div className="mt-4 inline-block bg-white/20 backdrop-blur-sm px-4 py-1 rounded-full text-white text-xs font-semibold">
                  Most Popular
                </div>
              </div>
            </a>

            {/* Smart Button */}
            <a
              href="/apartments/smart"
              className="group relative bg-gradient-to-br from-blue-700 to-blue-800 hover:from-blue-800 hover:to-blue-900 rounded-2xl p-8 transition-all duration-300 hover:shadow-2xl hover:scale-105 text-center overflow-hidden border border-blue-600/20"
            >
              <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-10 transition-opacity"></div>
              <div className="relative z-10">
                <div className="text-5xl mb-4">🎯</div>
                <h3 className="text-2xl font-bold text-white mb-2">Smart</h3>
                <p className="text-blue-100 text-sm mb-3">$4,500 - $6,500/mo</p>
                <div className="text-3xl font-bold text-white mb-3">69 Apartments</div>
                <p className="text-xs text-blue-100">Best value at fair prices</p>
                <div className="mt-4 inline-block bg-white/20 backdrop-blur-sm px-4 py-1 rounded-full text-white text-xs font-semibold">
                  Sweet Spot
                </div>
              </div>
            </a>

            {/* Sky's the Limit Button */}
            <a
              href="/apartments/luxury"
              className="group relative bg-gradient-to-br from-slate-700 to-slate-800 hover:from-slate-800 hover:to-slate-900 rounded-2xl p-8 transition-all duration-300 hover:shadow-2xl hover:scale-105 text-center overflow-hidden border border-slate-600/20"
            >
              <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-10 transition-opacity"></div>
              <div className="relative z-10">
                <div className="text-5xl mb-4">✨</div>
                <h3 className="text-2xl font-bold text-white mb-2">Sky's the Limit</h3>
                <p className="text-slate-100 text-sm mb-3">Over $6,500/mo</p>
                <div className="text-3xl font-bold text-white mb-3">22 Apartments</div>
                <p className="text-xs text-slate-100">Premium luxury living</p>
                <div className="mt-4 inline-block bg-white/20 backdrop-blur-sm px-4 py-1 rounded-full text-white text-xs font-semibold">
                  Ultra Luxury
                </div>
              </div>
            </a>
          </div>
        </div>
      </section>
      
      <SEOAffordableSection />
      
      {/* Featured Apartments Section Removed - Units moved to category pages */}
      
      {/* Newsletter Section Removed - SEO preserved */}
      
      <AdvancedSearchFilters 
        filters={searchFilters} 
        onFilterChange={handleFilterChange}
        apartmentCount={totalApartments}
      />
      
      <main id="main-content" className="main-content container mx-auto px-4 md:px-6 py-6 md:py-8">
        {/* Sorting Controls */}
        <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-4 p-4 bg-slate-800 rounded-lg border border-slate-700">
          <div className="flex items-center space-x-3 mb-3 md:mb-0">
            <span className="text-slate-300 font-medium text-sm md:text-base">Sort by:</span>
            <select 
              value={sortBy}
              onChange={(e) => {
                setSortBy(e.target.value);
                setCurrentPage(1); // Reset to first page on sort change
              }}
              className="px-3 py-2 bg-slate-700 text-white rounded-lg border border-slate-600 focus:outline-none focus:ring-2 focus:ring-mint-500 text-sm md:text-base"
            >
              <option value="price">Price</option>
              <option value="bedrooms">Bedrooms</option>
              <option value="created_at">Newest First</option>
            </select>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="text-slate-300 text-sm md:text-base">Order:</span>
            <button 
              onClick={() => {
                setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
                setCurrentPage(1); // Reset to first page on order change
              }}
              className="flex items-center space-x-2 px-4 py-2 bg-mint-600 hover:bg-mint-500 text-white rounded-lg transition-colors font-medium text-sm md:text-base"
            >
              <span>{sortOrder === 'asc' ? 'Low to High' : 'High to Low'}</span>
              <svg 
                className={`w-4 h-4 transition-transform ${sortOrder === 'desc' ? 'rotate-180' : ''}`}
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
            </button>
          </div>
        </div>
        
        <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-4 md:mb-6 gap-4">
          <h2 className="text-xl md:text-2xl font-bold bg-gradient-to-r from-purple-400 to-orange-400 bg-clip-text text-transparent">
            {loading ? 'Searching No Fee Apartments NYC...' : 'No Fee Apartments NYC 2025 | Zero Broker Fee Rentals'}
          </h2>
          <div className="flex space-x-2">
            <button 
              onClick={() => setViewMode('list')}
              className={`px-3 md:px-4 py-2 rounded-lg transition-colors text-sm md:text-base ${
                viewMode === 'list' 
                ? 'bg-purple-600 text-white shadow-lg' 
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-600'
              }`}
            >
              List View
            </button>
            <button 
              onClick={() => setViewMode('map')}
              className={`px-3 md:px-4 py-2 rounded-lg transition-colors text-sm md:text-base ${
                viewMode === 'map' 
                ? 'bg-purple-600 text-white shadow-lg' 
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-600'
              }`}
            >
              Map View
            </button>
          </div>
        </div>

        {loading ? (
          <LoadingSpinner />
        ) : viewMode === 'list' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
            {apartments.map(apartment => (
              <ApartmentCard 
                key={apartment.id} 
                apartment={apartment} 
                setShowAuthModal={setShowAuthModal}
              />
            ))}
          </div>
        ) : (
          <MapView apartments={apartments} />
        )}

        {!loading && apartments.length === 0 && (
          <div className="text-center py-12">
            <div className="max-w-md mx-auto">
              <div className="w-16 h-16 mx-auto mb-4 bg-slate-200 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-slate-800 mb-2">No apartments found</h3>
              <p className="text-slate-600 mb-4">Try adjusting your search filters to see more results.</p>
              <button 
                onClick={clearFilters}
                className="px-4 py-2 bg-amber-600 text-slate-800 rounded-lg hover:bg-amber-500 transition-colors font-semibold"
              >
                Clear Filters
              </button>
            </div>
          </div>
        )}

        {/* Pagination */}
        {!loading && apartments.length > 0 && (
          <div className="flex justify-center mt-8">
            <div className="flex space-x-2">
              <button
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 bg-amber-600 text-slate-800 rounded-lg hover:bg-amber-500 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors font-semibold"
              >
                Previous
              </button>
              <span className="px-4 py-2 bg-slate-100 rounded-lg flex items-center">
                Page {currentPage}
              </span>
              <button
                onClick={() => setCurrentPage(prev => prev + 1)}
                disabled={apartments.length < 100}
                className="px-4 py-2 bg-amber-600 text-slate-800 rounded-lg hover:bg-amber-500 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors font-semibold"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </main>

      <Footer />

      {/* Authentication Modal */}
      {showAuthModal && (
        <AuthModal onClose={() => setShowAuthModal(false)} />
      )}
    </div>
  );
};

const ApartmentDetailsPage = () => {
  const apartmentId = window.location.pathname.split('/').pop();
  return <ApartmentDetails apartmentId={apartmentId} />;
};

const DashboardPage = () => {
  const { user, isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return <UserDashboard user={user} />;
};

const SavedSearchesPage = () => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return <SavedSearches />;
};

const FavoritesPageRoute = () => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return <FavoritesPage />;
};

const AdminAppointmentsPage = () => {
  // For now, no authentication check - but you can add admin role check here
  return <AdminAppointments />;
};

// Complete Guide Page Component
const CompleteGuidePage = () => {
  return <CompleteGuideNoFeeApartments />;
};

// Blog Pages
const BlogListPage = () => (
  <div>
    <Header />
    <BlogList />
    <Footer />
  </div>
);

const BlogPostPage = () => {
  const { slug } = useParams();
  
  return (
    <div>
      {/* Skip Link for Screen Readers */}
      <a 
        href="#main-content" 
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-blue-600 text-white px-4 py-2 rounded-lg z-50 focus:outline-none focus:ring-2 focus:ring-blue-300"
      >
        Skip to main content
      </a>
      
      <Header />
      <BlogPost slug={slug} />
      <Footer />
    </div>
  );
};

function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <AuthProvider>
          <div className="App">
            <BrowserRouter>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/apartment/:id" element={<ApartmentDetailsPage />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/favorites" element={<FavoritesPageRoute />} />
                <Route path="/saved-searches" element={<SavedSearchesPage />} />
                <Route path="/admin/appointments" element={<AdminAppointmentsPage />} />
                <Route path="/complete-guide-no-fee-apartments-nyc" element={<CompleteGuidePage />} />
                <Route path="/blog" element={<BlogListPage />} />
                <Route path="/blog/:slug" element={<BlogPostPage />} />
                <Route path="/newsletter" element={<NewsletterPage />} />
                
                {/* Landlord Portal Routes */}
                <Route path="/landlord" element={<LandlordPricing />} />
                <Route path="/landlord/pricing" element={<LandlordPricing />} />
                <Route path="/landlord/register" element={<LandlordRegistration />} />
                <Route path="/landlord/login" element={<LandlordLogin />} />
                <Route path="/landlord/demo" element={<DemoLandlordAccess />} />
                <Route path="/landlord/dashboard/:landlordId" element={<LandlordDashboard />} />
                <Route path="/landlord/add-listing/:landlordId" element={<AddListing />} />
                <Route path="/landlord/listings/:landlordId" element={<ViewListings />} />
                <Route path="/landlord/success" element={<PaymentSuccess />} />
                <Route path="/landlord/cancel" element={<LandlordPricing />} />
                
                {/* Tenant Listing Routes */}
                <Route path="/tenant/list-apartment" element={<TenantListingPage />} />
                <Route path="/tenant/browse" element={<TenantBrowsePage />} />
                
                {/* Analytics Dashboard */}
                <Route path="/analytics" element={<AnalyticsDashboard />} />
                
                {/* Admin Panel */}
                <Route path="/admin" element={<AdminLogin />} />
                <Route path="/admin/dashboard" element={<AdminDashboard />} />
                
                {/* Price Category Pages */}
                <Route path="/apartments/:category" element={<CategoryPage />} />
                
                {/* Borough/City Pages - SEO Optimized */}
                <Route path="/manhattan" element={<BoroughPage />} />
                <Route path="/brooklyn" element={<BoroughPage />} />
                <Route path="/queens" element={<BoroughPage />} />
                <Route path="/bronx" element={<BoroughPage />} />
                
                {/* Static Pages */}
                <Route path="/about" element={<AboutUsPage />} />
                <Route path="/why-no-fee" element={<WhyNoFeePage />} />
                <Route path="/contact" element={<ContactUsPage />} />
                <Route path="/lets-talk" element={<LetsTalkPage />} />
              </Routes>
              
              {/* Consolidated Chatbot with Lead Gen + Feedback */}
              <LeadGenChatbot />
              <VisitorTracker />
              
              {/* Newsletter functionality temporarily removed */}
            </BrowserRouter>
          </div>
        </AuthProvider>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;// Cache-busting version: 2.0.1
const CACHE_VERSION = '2.0.1';
