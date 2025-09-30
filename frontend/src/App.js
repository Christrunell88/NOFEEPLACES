import React, { useState, useEffect } from "react";
import "./App.css";
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

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const { 
  Header, 
  Hero, 
  FeaturedApartments,
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
  }, [searchFilters, currentPage]);

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
      <Header 
        isAuthenticated={isAuthenticated}
        user={user}
        logout={logout}
        setShowAuthModal={setShowAuthModal}
      />
      <Hero />
      <FeaturedApartments />
      
      {/* Newsletter Section Removed - SEO preserved */}
      
      <AdvancedSearchFilters 
        filters={searchFilters} 
        onFilterChange={handleFilterChange}
        apartmentCount={totalApartments}
      />
      
      <main className="main-content container mx-auto px-4 md:px-6 py-6 md:py-8">
        <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-4 md:mb-6 gap-4">
          <h1 className="text-xl md:text-2xl font-bold bg-gradient-to-r from-purple-400 to-orange-400 bg-clip-text text-transparent">
            {loading ? 'Searching No Fee Apartments NYC...' : 'No Fee Apartments NYC 2025 | Zero Broker Fee Rentals'}
          </h1>
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
              </Routes>
              
              {/* AI Chatbot - Available on all pages */}
              <AIChatbot />
              
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
