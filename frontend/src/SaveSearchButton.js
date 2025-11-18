import React, { useState } from 'react';
import { useAuth } from './auth';
import axios from 'axios';
import { trackSaveSearch } from './analytics';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const SaveSearchButton = ({ filters }) => {
  const { isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(false);

  const generateSearchName = () => {
    const parts = [];
    
    if (filters.bedrooms !== undefined && filters.bedrooms !== '') {
      parts.push(filters.bedrooms === 0 || filters.bedrooms === '0' ? 'Studio' : `${filters.bedrooms}BR`);
    }
    
    if (filters.borough) {
      parts.push(`in ${filters.borough}`);
    } else if (filters.neighborhood) {
      parts.push(`in ${filters.neighborhood}`);
    }
    
    if (filters.min_price && filters.max_price) {
      parts.push(`$${parseInt(filters.min_price).toLocaleString()}-$${parseInt(filters.max_price).toLocaleString()}`);
    } else if (filters.min_price) {
      parts.push(`$${parseInt(filters.min_price).toLocaleString()}+`);
    } else if (filters.max_price) {
      parts.push(`under $${parseInt(filters.max_price).toLocaleString()}`);
    }
    
    return parts.length > 0 ? parts.join(' ') : 'Custom Search';
  };

  const handleSaveSearch = async () => {
    if (!isAuthenticated) {
      window.dispatchEvent(new CustomEvent('openAuthModal'));
      return;
    }

    // Check if there are any filters applied
    const hasFilters = Object.values(filters).some(val => 
      val !== undefined && val !== '' && val !== null
    );

    if (!hasFilters) {
      showNotification('Please apply some filters before saving', 'warning');
      return;
    }

    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const searchName = generateSearchName();
      
      const response = await axios.post(
        `${API}/saved-searches/create`,
        {
          search_name: searchName,
          filters: filters,
          email_frequency: 'weekly'
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.data.success) {
        showNotification(`Search saved: ${searchName}`, 'success');
      }
    } catch (err) {
      console.error('Error saving search:', err);
      const errorMsg = err.response?.data?.detail || 'Failed to save search';
      showNotification(errorMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (message, type) => {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg text-white z-50 transform transition-all duration-300 ${
      type === 'success' ? 'bg-green-500' :
      type === 'warning' ? 'bg-orange-500' :
      'bg-red-500'
    }`;
    toast.textContent = message;
    toast.style.opacity = '0';
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.style.opacity = '1';
    }, 10);
    
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 300);
    }, 3000);
  };

  return (
    <button
      onClick={handleSaveSearch}
      disabled={loading}
      className="flex items-center gap-2 px-4 py-2 bg-white border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
      title="Save this search and get weekly email alerts"
    >
      {loading ? (
        <>
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>Saving...</span>
        </>
      ) : (
        <>
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <span>Save Search</span>
        </>
      )}
    </button>
  );
};

export default SaveSearchButton;
