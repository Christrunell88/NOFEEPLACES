import React, { useState, useEffect } from 'react';
import { useAuth } from './auth';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const FavoriteButton = ({ apartmentId, size = 'md', showToast = true }) => {
  const { isAuthenticated } = useAuth();
  const [isFavorite, setIsFavorite] = useState(false);
  const [loading, setLoading] = useState(false);
  const [favoritesCount, setFavoritesCount] = useState(0);

  useEffect(() => {
    if (isAuthenticated) {
      checkFavoriteStatus();
    }
  }, [apartmentId, isAuthenticated]);

  const checkFavoriteStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/favorites/check/${apartmentId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setIsFavorite(response.data.is_favorite);
    } catch (err) {
      console.error('Error checking favorite status:', err);
    }
  };

  const toggleFavorite = async (e) => {
    e.stopPropagation(); // Prevent triggering parent click events
    
    if (!isAuthenticated) {
      // Trigger auth modal
      window.dispatchEvent(new CustomEvent('openAuthModal'));
      return;
    }

    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      
      if (isFavorite) {
        // Remove from favorites
        const response = await axios.delete(`${API}/favorites/remove/${apartmentId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        setIsFavorite(false);
        setFavoritesCount(response.data.favorites_count);
        
        if (showToast) {
          showNotification('Removed from favorites', 'success');
        }
      } else {
        // Add to favorites
        const response = await axios.post(
          `${API}/favorites/add`,
          { apartment_id: apartmentId },
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
        
        if (response.data.favorites_count >= 25 && !isFavorite) {
          showNotification('You\'ve reached the maximum of 25 favorites', 'warning');
        } else {
          setIsFavorite(true);
          setFavoritesCount(response.data.favorites_count);
          
          if (showToast) {
            showNotification('Saved to favorites', 'success');
          }
        }
      }
    } catch (err) {
      console.error('Error toggling favorite:', err);
      const errorMsg = err.response?.data?.detail || 'Failed to update favorites';
      showNotification(errorMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (message, type) => {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg text-white z-50 transform transition-all duration-300 ${
      type === 'success' ? 'bg-green-500' :
      type === 'warning' ? 'bg-orange-500' :
      'bg-red-500'
    }`;
    toast.textContent = message;
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-20px)';
    
    document.body.appendChild(toast);
    
    // Fade in
    setTimeout(() => {
      toast.style.opacity = '1';
      toast.style.transform = 'translateY(0)';
    }, 10);
    
    // Fade out and remove
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-20px)';
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 300);
    }, 3000);
  };

  // Size classes
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12'
  };

  const iconSizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  };

  return (
    <button
      onClick={toggleFavorite}
      disabled={loading}
      className={`${sizeClasses[size]} flex items-center justify-center bg-white rounded-full shadow-lg hover:scale-110 transition-transform disabled:opacity-50 disabled:cursor-not-allowed ${
        isFavorite ? 'hover:bg-red-50' : 'hover:bg-gray-50'
      }`}
      title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
      aria-label={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
    >
      {loading ? (
        <svg className={`${iconSizes[size]} animate-spin text-gray-400`} viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      ) : (
        <svg 
          className={`${iconSizes[size]} ${isFavorite ? 'text-red-500' : 'text-gray-400'}`}
          fill={isFavorite ? 'currentColor' : 'none'}
          stroke="currentColor"
          strokeWidth={isFavorite ? 0 : 2}
          viewBox="0 0 20 20"
        >
          <path 
            fillRule="evenodd" 
            d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" 
            clipRule="evenodd" 
          />
        </svg>
      )}
    </button>
  );
};

export default FavoriteButton;
