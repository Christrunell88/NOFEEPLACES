import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  const API_URL = process.env.REACT_APP_BACKEND_URL || '';
  const API = `${API_URL}/api`;

  // Configure axios with current token
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Fetch current user on mount
  useEffect(() => {
    const fetchUser = async () => {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(`${API}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setUser(response.data);
      } catch (error) {
        console.error('Failed to fetch user:', error);
        // Clear invalid token
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          setToken(null);
          delete axios.defaults.headers.common['Authorization'];
        }
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [token, API]);

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, {
        email: email.trim().toLowerCase(),
        password
      });

      const { access_token, user: userData } = response.data;

      // Save token
      localStorage.setItem('token', access_token);
      setToken(access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      // Set user
      setUser(userData);

      return { success: true, user: userData };
    } catch (error) {
      console.error('Login error:', error);
      const errorMessage = error.response?.data?.detail || 'Login failed. Please check your credentials.';
      return { success: false, error: errorMessage };
    }
  };

  const register = async (email, password, fullName) => {
    try {
      const response = await axios.post(`${API}/auth/register`, {
        email: email.trim().toLowerCase(),
        password,
        full_name: fullName
      });

      const { access_token, user: userData } = response.data;

      // Save token
      localStorage.setItem('token', access_token);
      setToken(access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      // Set user
      setUser(userData);

      return { success: true, user: userData };
    } catch (error) {
      console.error('Registration error:', error);
      const errorMessage = error.response?.data?.detail || 'Registration failed. Please try again.';
      return { success: false, error: errorMessage };
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
