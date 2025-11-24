import React, { useState, useEffect, createContext, useContext } from 'react';
import axios from 'axios';

// Dynamic Backend URL Detection
const getBackendURL = () => {
  // Priority order for backend URL detection
  
  // 1. Environment variable
  if (process.env.REACT_APP_BACKEND_URL) {
    console.log('[Auth] Using env backend URL:', process.env.REACT_APP_BACKEND_URL);
    return process.env.REACT_APP_BACKEND_URL;
  }
  
  // 2. Same origin (production default)
  if (window.location.hostname === 'nofeeplaces.com' || 
      window.location.hostname === 'www.nofeeplaces.com') {
    const sameOrigin = window.location.origin;
    console.log('[Auth] Using same origin for production:', sameOrigin);
    return sameOrigin;
  }
  
  // 3. Localhost development
  if (window.location.hostname === 'localhost' || 
      window.location.hostname === '127.0.0.1') {
    console.log('[Auth] Using localhost backend');
    return 'http://localhost:8001';
  }
  
  // 4. Preview/staging - use same origin
  const origin = window.location.origin;
  console.log('[Auth] Using current origin:', origin);
  return origin;
};

const API_BASE = getBackendURL();
const API = `${API_BASE}/api`;

console.log('[Auth] Initialized with API:', API);

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const RobustAuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Configure axios with current token
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Fetch user data with token
  const fetchUser = async () => {
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      console.log('[Auth] Fetching user data from:', `${API}/auth/me`);
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      console.log('[Auth] User data fetched successfully:', response.data.email);
      setUser(response.data);
      setError(null);
    } catch (error) {
      console.error('[Auth] Failed to fetch user:', error.response?.status, error.message);
      
      // Only logout on authentication errors, not network errors
      if (error.response && (error.response.status === 401 || error.response.status === 403)) {
        console.log('[Auth] Token invalid, logging out');
        logout();
      } else {
        console.log('[Auth] Network error, keeping token');
        setError('Network error - please check your connection');
      }
    } finally {
      setLoading(false);
    }
  };

  // Initialize auth on mount
  useEffect(() => {
    console.log('[Auth] Initializing auth provider');
    fetchUser();
  }, []);

  // Login with email and password
  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('[Auth] Attempting login for:', email);
      console.log('[Auth] Login URL:', `${API}/auth/login`);
      
      const response = await axios.post(`${API}/auth/login`, {
        email: email.trim().toLowerCase(),
        password: password
      });

      console.log('[Auth] Login successful, token received');
      
      const { access_token, user: userData } = response.data;
      
      // Save token
      localStorage.setItem('token', access_token);
      setToken(access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Set user data
      setUser(userData);
      setError(null);
      setLoading(false);
      
      return { success: true, user: userData };
    } catch (error) {
      console.error('[Auth] Login failed:', error.response?.data || error.message);
      
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message ||
                          error.message ||
                          'Login failed. Please check your credentials.';
      
      setError(errorMessage);
      setLoading(false);
      
      return { 
        success: false, 
        error: errorMessage,
        details: {
          status: error.response?.status,
          apiUrl: `${API}/auth/login`,
          originalError: error.message
        }
      };
    }
  };

  // Register new user
  const register = async (email, password, fullName) => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('[Auth] Attempting registration for:', email);
      
      const response = await axios.post(`${API}/auth/register`, {
        email: email.trim().toLowerCase(),
        password: password,
        full_name: fullName
      });

      console.log('[Auth] Registration successful');
      
      const { access_token, user: userData } = response.data;
      
      // Save token
      localStorage.setItem('token', access_token);
      setToken(access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Set user data
      setUser(userData);
      setError(null);
      setLoading(false);
      
      return { success: true, user: userData };
    } catch (error) {
      console.error('[Auth] Registration failed:', error.response?.data || error.message);
      
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message ||
                          'Registration failed. Please try again.';
      
      setError(errorMessage);
      setLoading(false);
      
      return { success: false, error: errorMessage };
    }
  };

  // Logout
  const logout = () => {
    console.log('[Auth] Logging out');
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setError(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  // Google login (simplified)
  const loginWithGoogle = async (googleToken) => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('[Auth] Attempting Google login');
      
      const response = await axios.post(`${API}/auth/google`, {
        token: googleToken
      });

      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      setUser(userData);
      setError(null);
      setLoading(false);
      
      return { success: true, user: userData };
    } catch (error) {
      console.error('[Auth] Google login failed:', error);
      
      const errorMessage = error.response?.data?.detail || 'Google login failed';
      setError(errorMessage);
      setLoading(false);
      
      return { success: false, error: errorMessage };
    }
  };

  const value = {
    user,
    login,
    register,
    logout,
    loginWithGoogle,
    loading,
    error,
    isAuthenticated: !!user && !loading,
    hasToken: !!token,
    apiUrl: API
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default RobustAuthProvider;
