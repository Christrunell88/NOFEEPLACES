import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { Components } from './components';
// Marketing components will be re-added once properly integrated

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

  // Debug: Log authentication state
  console.log('Auth Debug:', { user, isAuthenticated: !!user, loading, token });

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

  // Debug: Log what isAuthenticated returns in the main component
  console.log('Main App Debug:', { isAuthenticated, user });

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
            {loading ? 'Searching No Fee Apartments NYC...' : isAuthenticated ? 'No Broker Fee Apartments NYC Available' : (
              <span className="font-philosopher text-2xl md:text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Free Sign Up for Full Address!
              </span>
            )}
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
          <div className="space-y-8">
            {/* Categorize apartments by price */}
            {(() => {
              const valueApartments = apartments.filter(apt => apt.price < 3400);
              const savvyApartments = apartments.filter(apt => apt.price >= 3400 && apt.price <= 7000);
              const luxuryApartments = apartments.filter(apt => apt.price > 7000);

              return (
                <>
                  {/* Value Category */}
                  {valueApartments.length > 0 && (
                    <div className="mb-8">
                      <div className="flex items-center mb-6">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                            </svg>
                          </div>
                          <div>
                            <h2 className="text-2xl font-bold text-gray-900">💰 Value</h2>
                            <p className="text-gray-600">Under $3,400/month • {valueApartments.length} apartment{valueApartments.length !== 1 ? 's' : ''}</p>
                          </div>
                        </div>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
                        {valueApartments.map(apartment => (
                          <ApartmentCard 
                            key={apartment.id} 
                            apartment={apartment} 
                            setShowAuthModal={setShowAuthModal}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Savvy Category */}
                  {savvyApartments.length > 0 && (
                    <div className="mb-8">
                      <div className="flex items-center mb-6">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.071 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                            </svg>
                          </div>
                          <div>
                            <h2 className="text-2xl font-bold text-gray-900">🎯 Savvy</h2>
                            <p className="text-gray-600">$3,450 - $7,000/month • {savvyApartments.length} apartment{savvyApartments.length !== 1 ? 's' : ''}</p>
                          </div>
                        </div>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
                        {savvyApartments.map(apartment => (
                          <ApartmentCard 
                            key={apartment.id} 
                            apartment={apartment} 
                            setShowAuthModal={setShowAuthModal}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Luxury Category */}
                  {luxuryApartments.length > 0 && (
                    <div className="mb-8">
                      <div className="flex items-center mb-6">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                            </svg>
                          </div>
                          <div>
                            <h2 className="text-2xl font-bold text-gray-900">✨ Luxury</h2>
                            <p className="text-gray-600">Over $7,001/month • {luxuryApartments.length} apartment{luxuryApartments.length !== 1 ? 's' : ''}</p>
                          </div>
                        </div>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
                        {luxuryApartments.map(apartment => (
                          <ApartmentCard 
                            key={apartment.id} 
                            apartment={apartment} 
                            setShowAuthModal={setShowAuthModal}
                          />
                        ))}
                      </div>
                    </div>
                  )}
                </>
              );
            })()}
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
              
              {/* Marketing Components - Coming Soon */}
              <div className="fixed bottom-6 right-6 z-50">
                <a
                  href="tel:646-408-8048"
                  className="bg-green-600 text-white p-3 rounded-full shadow-lg hover:bg-green-700 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                  aria-label="Call for help"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                </a>
              </div>
            </BrowserRouter>
          </div>
        </AuthProvider>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;