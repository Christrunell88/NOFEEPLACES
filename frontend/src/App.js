import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { Components } from './components';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      await fetchUser();
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  };

  const register = async (email, password, fullName) => {
    try {
      const response = await axios.post(`${API}/auth/register`, {
        email,
        password,
        full_name: fullName
      });
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      await fetchUser();
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Registration failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading,
    isAuthenticated: !!user
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

const { 
  Header, 
  Hero, 
  SEOContentSection,
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
  CompleteGuideNoFeeApartments
} = Components;

const Home = () => {
  const [apartments, setApartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchFilters, setSearchFilters] = useState({
    min_price: '',
    max_price: '',
    bedrooms: '',
    neighborhood: '',
    borough: '',
    search_term: ''
  });
  const [viewMode, setViewMode] = useState('list');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalApartments, setTotalApartments] = useState(0);
  const [searchStats, setSearchStats] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const { isAuthenticated, user, logout } = useAuth();

  useEffect(() => {
    fetchApartments();
    fetchSearchStats();
  }, [searchFilters, currentPage]);

  const fetchApartments = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      
      Object.entries(searchFilters).forEach(([key, value]) => {
        if (value !== '' && value !== null && value !== undefined) {
          params.append(key, value);
        }
      });
      
      params.append('page', currentPage);
      params.append('limit', 100);

      const response = await axios.get(`${API}/apartments?${params}`);
      setApartments(response.data);
      setTotalApartments(response.data.length);
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
  };

  const clearFilters = () => {
    setSearchFilters({
      min_price: '',
      max_price: '',
      bedrooms: '',
      neighborhood: '',
      borough: '',
      search_term: ''
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
      <SEOContentSection />
      <AdvancedSearchFilters 
        filters={searchFilters} 
        onFilterChange={handleFilterChange}
        apartmentCount={totalApartments}
      />
      
      <main className="main-content container mx-auto px-4 md:px-6 py-6 md:py-8">
        <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-4 md:mb-6 gap-4">
          <h2 className="text-xl md:text-2xl font-bold text-slate-800">
            {loading ? 'Searching No Fee Apartments NYC...' : isAuthenticated ? `${totalApartments} No Broker Fee Apartments NYC Available` : 'Sign Up for Full Address and Schedule a Tour!'}
          </h2>
          <div className="flex space-x-2">
            <button 
              onClick={() => setViewMode('list')}
              className={`px-3 md:px-4 py-2 rounded-lg transition-colors text-sm md:text-base ${
                viewMode === 'list' 
                ? 'bg-amber-600 text-slate-800' 
                : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
              }`}
            >
              List View
            </button>
            <button 
              onClick={() => setViewMode('map')}
              className={`px-3 md:px-4 py-2 rounded-lg transition-colors text-sm md:text-base ${
                viewMode === 'map' 
                ? 'bg-amber-600 text-slate-800' 
                : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
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
              </Routes>
              
              {/* AI Chatbot - Available on all pages */}
              <AIChatbot />
            </BrowserRouter>
          </div>
        </AuthProvider>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;