import React, { useState, useEffect } from 'react';
import { useAuth } from './auth';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const SavedSearchesPage = () => {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [searches, setSearches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      fetchSavedSearches();
    } else if (!authLoading && !isAuthenticated) {
      setLoading(false);
    }
  }, [isAuthenticated, authLoading]);

  const fetchSavedSearches = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/saved-searches`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setSearches(response.data.saved_searches || []);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching saved searches:', err);
      setError('Failed to load saved searches');
      setLoading(false);
    }
  };

  const handleDeleteSearch = async (searchId) => {
    if (!window.confirm('Delete this saved search?')) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/saved-searches/${searchId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setSearches(searches.filter(s => s.id !== searchId));
      showNotification('Saved search deleted', 'success');
    } catch (err) {
      console.error('Error deleting search:', err);
      showNotification('Failed to delete search', 'error');
    }
  };

  const handleToggleEmail = async (searchId, currentFrequency) => {
    const newFrequency = currentFrequency === 'weekly' ? 'never' : 'weekly';
    
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${API}/saved-searches/${searchId}?email_frequency=${newFrequency}`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      // Update local state
      setSearches(searches.map(s => 
        s.id === searchId ? { ...s, email_frequency: newFrequency } : s
      ));
      
      showNotification(
        newFrequency === 'weekly' ? 'Weekly email alerts enabled' : 'Email alerts disabled',
        'success'
      );
    } catch (err) {
      console.error('Error updating email frequency:', err);
      showNotification('Failed to update email alerts', 'error');
    }
  };

  const handleRunSearch = (filters) => {
    // Build query string from filters
    const params = new URLSearchParams();
    
    if (filters.borough) params.append('borough', filters.borough);
    if (filters.neighborhood) params.append('neighborhood', filters.neighborhood);
    if (filters.bedrooms !== undefined) params.append('bedrooms', filters.bedrooms);
    if (filters.min_price) params.append('min_price', filters.min_price);
    if (filters.max_price) params.append('max_price', filters.max_price);
    
    navigate(`/?${params.toString()}`);
  };

  const showNotification = (message, type) => {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg text-white z-50 ${
      type === 'success' ? 'bg-green-500' : 'bg-red-500'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 3000);
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <div className="text-6xl mb-4">🔔</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Never Miss New Listings
          </h2>
          <p className="text-gray-600 mb-6">
            Save your searches and get weekly email alerts when new apartments match your criteria.
          </p>
          <Link
            to="/"
            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Sign In to Continue
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Saved Searches
              </h1>
              <p className="text-gray-600">
                {searches.length} {searches.length === 1 ? 'search' : 'searches'} saved
              </p>
            </div>
            <Link
              to="/"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Browse Apartments
            </Link>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        {searches.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <div className="text-6xl mb-4">🔍</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              No saved searches yet
            </h2>
            <p className="text-gray-600 mb-6">
              Browse apartments and click "Save this search" to get weekly email alerts
            </p>
            <Link
              to="/"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Start Searching
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {searches.map((search) => (
              <div
                key={search.id}
                className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-gray-900 mb-2">
                      {search.search_name}
                    </h3>
                    
                    {/* Search Criteria */}
                    <div className="flex flex-wrap gap-2 mb-3">
                      {search.filters.bedrooms !== undefined && (
                        <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                          {search.filters.bedrooms === 0 ? 'Studio' : `${search.filters.bedrooms} Bed`}
                        </span>
                      )}
                      {search.filters.borough && (
                        <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                          {search.filters.borough}
                        </span>
                      )}
                      {search.filters.neighborhood && (
                        <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm">
                          {search.filters.neighborhood}
                        </span>
                      )}
                      {(search.filters.min_price || search.filters.max_price) && (
                        <span className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm">
                          {search.filters.min_price && `$${parseInt(search.filters.min_price).toLocaleString()}`}
                          {search.filters.min_price && search.filters.max_price && ' - '}
                          {search.filters.max_price && `$${parseInt(search.filters.max_price).toLocaleString()}`}
                        </span>
                      )}
                    </div>

                    {/* New Listings Badge */}
                    {search.new_listings_count > 0 && (
                      <div className="inline-flex items-center gap-2 px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-semibold mb-3">
                        <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                        {search.new_listings_count} new {search.new_listings_count === 1 ? 'listing' : 'listings'}
                      </div>
                    )}

                    {/* Email Alert Status */}
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      <span>
                        {search.email_frequency === 'weekly' ? 'Weekly email alerts enabled' : 'Email alerts disabled'}
                      </span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-col gap-2 ml-4">
                    <button
                      onClick={() => handleRunSearch(search.filters)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium whitespace-nowrap"
                    >
                      View Listings
                    </button>
                    
                    <button
                      onClick={() => handleToggleEmail(search.id, search.email_frequency)}
                      className={`px-4 py-2 rounded-lg transition-colors text-sm font-medium whitespace-nowrap ${
                        search.email_frequency === 'weekly'
                          ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                          : 'bg-green-100 text-green-700 hover:bg-green-200'
                      }`}
                    >
                      {search.email_frequency === 'weekly' ? 'Disable Alerts' : 'Enable Alerts'}
                    </button>
                    
                    <button
                      onClick={() => handleDeleteSearch(search.id)}
                      className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-sm font-medium whitespace-nowrap"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SavedSearchesPage;
