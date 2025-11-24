import React, { useState, useEffect } from "react";
import "./App.css";
import './accessibility.css';
import { BrowserRouter, Routes, Route, Navigate, useParams } from "react-router-dom";
import axios from "axios";
import * as Components from './components';
import { AuthProvider, useAuth } from './auth';
import { RobustAuthProvider } from './RobustAuth';
import BulletproofAuthModal from './BulletproofAuthModal';
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
import VisitorTracker from './VisitorTracker';
import { AnalyticsDashboard } from './AnalyticsDashboard';
import TenantListingPage from './TenantListing';
import TenantBrowsePage from './TenantBrowse';
import CategoryPage from './CategoryPage';
import { AboutUsPage, WhyNoFeePage, ContactUsPage, LetsTalkPage } from './StaticPages';
import ConversionOptimizedHome from './ConversionOptimizedHome';
import ConversionHero from './ConversionHero';
import AdminLogin from './AdminLogin';
import AdminDashboard from './AdminDashboard';
import LeadGenChatbot from './LeadGenChatbot';
import { BrowseByNeighborhood, BoroughQuickLinks, RecentlyAdded, QuickFilters, SortOptions } from './BrowseSections';
import FavoritesPage from './FavoritesPage';
import SavedSearchesPage from './SavedSearchesPage';
import DashboardPage from './DashboardPage';
import SaveSearchButton from './SaveSearchButton';
import { LocalBusinessSchema, WebSiteSchema } from './AdvancedSchema';
import { RentCalculator, SavingsCalculator, FAQPage } from './SEOTools';

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
  const [selectedAmenities, setSelectedAmenities] = useState([]); // New: amenities filter
  const [sortBy, setSortBy] = useState('price');  // New: sorting field
  const [sortOrder, setSortOrder] = useState('asc');  // New: sorting order
  const [viewMode, setViewMode] = useState('list');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalApartments, setTotalApartments] = useState(0);
  const [searchStats, setSearchStats] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [neighborhoods, setNeighborhoods] = useState([]); // New: neighborhoods list
  const [recentlyAdded, setRecentlyAdded] = useState([]); // New: recently added apartments
  const [selectedApartment, setSelectedApartment] = useState(null); // For modal
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
  }, [searchFilters, currentPage, sortBy, sortOrder, selectedAmenities]);  // Added selectedAmenities dependency

  // Fetch neighborhoods and recently added on mount
  useEffect(() => {
    fetchNeighborhoods();
    fetchRecentlyAdded();
  }, []);

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
      
      // Add amenities filter if selected
      if (selectedAmenities.length > 0) {
        params.append('amenities', selectedAmenities.join(','));
      }
      
      params.append('page', currentPage);
      params.append('limit', 100); // Increased to show more apartments per page
      params.append('sort_by', sortBy);  // Add sorting parameters
      params.append('sort_order', sortOrder);

      const response = await axios.get(`${API}/apartments?${params}`);
      setApartments(response.data.apartments);
      setTotalApartments(response.data.total);
      
      // Track search performance and results
      const searchTime = performance.now() - searchStartTime;
      trackPerformanceMetric('apartment_search_time', Math.round(searchTime));
      
      // Track search event if filters are applied
      const hasActiveFilters = Object.values(searchFilters).some(value => value !== '' && value !== null) || selectedAmenities.length > 0;
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

  const fetchNeighborhoods = async () => {
    try {
      const response = await axios.get(`${API}/apartments/browse/neighborhoods`);
      setNeighborhoods(response.data.neighborhoods || []);
    } catch (error) {
      console.error('Failed to fetch neighborhoods:', error);
    }
  };

  const fetchRecentlyAdded = async () => {
    try {
      const response = await axios.get(`${API}/apartments/browse/recently-added?limit=8`);
      setRecentlyAdded(response.data.apartments || []);
    } catch (error) {
      console.error('Failed to fetch recently added:', error);
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

  const toggleAmenity = (amenity) => {
    setSelectedAmenities(prev => {
      if (prev.includes(amenity)) {
        return prev.filter(a => a !== amenity);
      } else {
        return [...prev, amenity];
      }
    });
    setCurrentPage(1);
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
    setSelectedAmenities([]);
    setSortBy('price');
    setSortOrder('asc');
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
      <Hero setShowAuthModal={setShowAuthModal} totalApartments={totalApartments} />
      
      {/* BOROUGH QUICK LINKS */}
      {searchStats?.boroughs && (
        <BoroughQuickLinks
          boroughs={searchStats.boroughs}
          onBoroughClick={(borough) => {
            handleFilterChange('borough', borough);
            window.scrollTo({ top: 800, behavior: 'smooth' });
          }}
        />
      )}
      
      {/* RECENTLY ADDED SECTION */}
      {recentlyAdded.length > 0 && (
        <RecentlyAdded
          apartments={recentlyAdded}
          onApartmentClick={(apartment) => {
            setSelectedApartment(apartment);
          }}
        />
      )}
      
      {/* BROWSE BY NEIGHBORHOOD */}
      {neighborhoods.length > 0 && (
        <BrowseByNeighborhood
          neighborhoods={neighborhoods}
          onNeighborhoodClick={(neighborhood) => {
            handleFilterChange('neighborhood', neighborhood);
            window.scrollTo({ top: 1000, behavior: 'smooth' });
          }}
        />
      )}
      
      {/* CATEGORY BUTTONS - MINIMALIST DESIGN */}
      <section className="bg-white py-16">
        <div className="container mx-auto px-4 md:px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-semibold text-gray-900 mb-3">Find Your Perfect Apartment</h2>
            <p className="text-lg text-gray-600">Browse by category to discover apartments that match your budget and lifestyle</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-7xl mx-auto">
            {/* Best Value */}
            <a
              href="/apartments/best-value"
              className="group bg-white hover:bg-gray-50 border border-gray-200 rounded-lg p-6 transition-all duration-200 hover:border-gray-300 hover:shadow-sm"
            >
              <div className="text-center">
                <h3 className="text-xl font-semibold text-gray-900 mb-1">Best Value</h3>
                <p className="text-sm text-gray-500 mb-3">Top Deals</p>
                <div className="text-3xl font-bold text-gray-900 mb-2">5</div>
                <p className="text-xs text-gray-600">Luxury amenities at great prices</p>
              </div>
            </a>
            
            {/* Budget */}
            <a
              href="/apartments/budget"
              className="group bg-white hover:bg-gray-50 border border-gray-200 rounded-lg p-6 transition-all duration-200 hover:border-gray-300 hover:shadow-sm"
            >
              <div className="text-center">
                <h3 className="text-xl font-semibold text-gray-900 mb-1">Budget</h3>
                <p className="text-sm text-gray-500 mb-3">Under $4,500/mo</p>
                <div className="text-3xl font-bold text-gray-900 mb-2">129</div>
                <p className="text-xs text-gray-600">Perfect for budget-conscious renters</p>
              </div>
            </a>

            {/* Smart */}
            <a
              href="/apartments/smart"
              className="group bg-white hover:bg-gray-50 border border-gray-200 rounded-lg p-6 transition-all duration-200 hover:border-gray-300 hover:shadow-sm"
            >
              <div className="text-center">
                <h3 className="text-xl font-semibold text-gray-900 mb-1">Smart</h3>
                <p className="text-sm text-gray-500 mb-3">$4,500 - $6,500/mo</p>
                <div className="text-3xl font-bold text-gray-900 mb-2">69</div>
                <p className="text-xs text-gray-600">Best value at fair prices</p>
              </div>
            </a>

            {/* Sky's the Limit */}
            <a
              href="/apartments/luxury"
              className="group bg-white hover:bg-gray-50 border border-gray-200 rounded-lg p-6 transition-all duration-200 hover:border-gray-300 hover:shadow-sm"
            >
              <div className="text-center">
                <h3 className="text-xl font-semibold text-gray-900 mb-1">Luxury</h3>
                <p className="text-sm text-gray-500 mb-3">Over $6,500/mo</p>
                <div className="text-3xl font-bold text-gray-900 mb-2">22</div>
                <p className="text-xs text-gray-600">Premium luxury living</p>
              </div>
            </a>
          </div>
        </div>
      </section>
      
      {/* Featured Apartments Section Removed - Units moved to category pages */}
      
      {/* Newsletter Section Removed - SEO preserved */}
      
      <AdvancedSearchFilters 
        filters={searchFilters} 
        onFilterChange={handleFilterChange}
        apartmentCount={totalApartments}
      />
      
      {/* QUICK FILTERS */}
      <QuickFilters 
        selectedAmenities={selectedAmenities}
        onToggleAmenity={toggleAmenity}
      />
      
      <main id="main-content" className="main-content container mx-auto px-4 md:px-6 py-6 md:py-8">
        {/* Enhanced Sorting Controls */}
        <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-6 gap-4">
          <div className="flex-1">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">
              {loading ? 'Searching apartments...' : `${totalApartments} No Fee Apartments`}
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Zero broker fees • Save $3,000+ on your next rental
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Save Search Button */}
            <SaveSearchButton filters={searchFilters} />
            <SortOptions
              sortBy={sortBy}
              sortOrder={sortOrder}
              onSortChange={(field, order) => {
                setSortBy(field);
                setSortOrder(order);
                setCurrentPage(1);
              }}
            />
            
            <div className="flex space-x-2">
              <button 
                onClick={() => setViewMode('list')}
                className={`px-4 py-2 rounded-lg transition-colors text-sm font-medium ${
                  viewMode === 'list' 
                  ? 'bg-emerald-600 text-white shadow-sm' 
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                List
              </button>
              <button 
                onClick={() => setViewMode('map')}
                className={`px-4 py-2 rounded-lg transition-colors text-sm font-medium ${
                  viewMode === 'map' 
                  ? 'bg-emerald-600 text-white shadow-sm' 
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                Map
              </button>
            </div>
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

      {/* Newsletter Signup Section */}
      <section className="bg-gradient-to-r from-purple-600 to-blue-600 py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              📬 Stay Updated on NYC No-Fee Apartments
            </h2>
            <p className="text-white/90 mb-6">
              Get weekly listings, market insights, and apartment hunting tips delivered to your inbox.
            </p>
            <Components.NewsletterSignup source="homepage_footer" size="large" />
          </div>
        </div>
      </section>

      <Footer />

      {/* Authentication Modal - Bulletproof Version */}
      {showAuthModal && (
        <BulletproofAuthModal onClose={() => setShowAuthModal(false)} />
      )}
      
      {/* Apartment Details Modal */}
      {selectedApartment && (
        <ApartmentDetailsModal
          apartment={selectedApartment}
          onClose={() => setSelectedApartment(null)}
        />
      )}
    </div>
  );
};

const ApartmentDetailsPage = () => {
  const apartmentId = window.location.pathname.split('/').pop();
  return <ApartmentDetails apartmentId={apartmentId} />;
};

// Dashboard, SavedSearches, and Favorites pages are imported directly
// They handle authentication internally

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
                <Route path="/favorites" element={<FavoritesPage />} />
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
                <Route path="/list" element={<TenantListingPage />} />
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
                
                {/* SEO Tools & Resources */}
                <Route path="/rent-calculator" element={<RentCalculator />} />
                <Route path="/savings-calculator" element={<SavingsCalculator />} />
                <Route path="/faq" element={<FAQPage />} />
              </Routes>
              
              {/* Global Schema Markup */}
              <LocalBusinessSchema />
              <WebSiteSchema />
              
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
