/**
 * Landlord Authentication Components
 * Provides login/register flow for landlord portal
 */

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

// Landlord Login Component
export const LandlordLogin = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Demo account quick access
  const useDemoAccount = () => {
    setFormData({
      email: 'demo@nofeeplaces.com',
      password: 'demo123'
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // For demo purposes, check if it's the demo account
      if (formData.email === 'demo@nofeeplaces.com') {
        // Redirect to demo dashboard
        navigate('/landlord/dashboard/demo-landlord-2025');
        return;
      }

      // For real accounts, you would make an API call here
      const response = await axios.post(`${API}/api/landlord/login`, formData);
      
      if (response.data.success) {
        // Store auth token and redirect
        localStorage.setItem('landlord_token', response.data.token);
        navigate(`/landlord/dashboard/${response.data.landlord_id}`);
      } else {
        setError('Invalid email or password');
      }
    } catch (error) {
      if (error.response?.status === 404) {
        setError('Account not found. Please register first.');
      } else {
        setError('Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Landlord Portal Login
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Access your property management dashboard
          </p>
        </div>

        {/* Demo Account Quick Access */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-blue-400 text-xl">🎭</span>
            </div>
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-blue-800">
                Demo Account Available
              </h3>
              <p className="text-xs text-blue-700 mt-1">
                Try the landlord portal with sample data
              </p>
            </div>
            <button
              onClick={useDemoAccount}
              className="ml-4 bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors"
            >
              Use Demo
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email" className="sr-only">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-purple-500 focus:border-purple-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
                value={formData.email}
                onChange={handleChange}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-purple-500 focus:border-purple-500 focus:z-10 sm:text-sm"
                placeholder="Password"
                value={formData.password}
                onChange={handleChange}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:bg-gray-400 transition-colors"
            >
              {loading ? 'Signing In...' : 'Sign In'}
            </button>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Don't have an account?{' '}
              <Link to="/landlord/register" className="font-medium text-purple-600 hover:text-purple-500">
                Start your free trial
              </Link>
            </p>
          </div>
        </form>

        {/* Demo Credentials Display */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mt-6">
          <h3 className="text-sm font-medium text-gray-800 mb-2">Demo Credentials:</h3>
          <div className="text-xs text-gray-600 space-y-1">
            <div><strong>Email:</strong> demo@nofeeplaces.com</div>
            <div><strong>Password:</strong> demo123</div>
            <div className="text-green-600 mt-2">
              ✓ Portfolio Plan ($99/month)
              <br />✓ 3 Active Listings 
              <br />✓ 3 Tenant Inquiries
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Quick Demo Access Component (for easy demo setup)
export const DemoLandlordAccess = () => {
  const navigate = useNavigate();

  const accessDemo = () => {
    navigate('/landlord/dashboard/demo-landlord-2025');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-lg w-full">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            🏢 Landlord Portal Demo
          </h1>
          <p className="text-gray-600 mb-8">
            Experience the complete property management dashboard with sample data from Manhattan Properties LLC.
          </p>

          <div className="bg-gray-50 rounded-lg p-6 mb-8">
            <h3 className="font-semibold text-gray-800 mb-3">Demo Account Includes:</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                <span>Portfolio Plan</span>
              </div>
              <div className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                <span>3 Active Listings</span>
              </div>
              <div className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                <span>Real Inquiries</span>
              </div>
              <div className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                <span>Analytics Dashboard</span>
              </div>
            </div>
          </div>

          <button
            onClick={accessDemo}
            className="w-full bg-purple-600 text-white py-3 px-6 rounded-lg hover:bg-purple-700 transition-colors font-semibold text-lg"
          >
            🚀 Access Demo Dashboard
          </button>

          <p className="text-xs text-gray-500 mt-4">
            Perfect for presentations to property management companies
          </p>
        </div>
      </div>
    </div>
  );
};

export default {
  LandlordLogin,
  DemoLandlordAccess
};