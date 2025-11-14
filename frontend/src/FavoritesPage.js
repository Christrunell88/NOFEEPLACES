import React, { useState, useEffect } from 'react';
import { useAuth } from './auth';
import axios from 'axios';
import { ApartmentDetailsModal } from './components';
import { Link } from 'react-router-dom';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const FavoritesPage = () => {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedApartment, setSelectedApartment] = useState(null);

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      fetchFavorites();
    } else if (!authLoading && !isAuthenticated) {
      setLoading(false);
    }
  }, [isAuthenticated, authLoading]);

  const fetchFavorites = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/favorites`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setFavorites(response.data.favorites || []);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching favorites:', err);
      setError('Failed to load favorites');
      setLoading(false);
    }
  };

  const handleRemoveFavorite = async (apartmentId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/favorites/remove/${apartmentId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      // Remove from local state
      setFavorites(favorites.filter(apt => apt.id !== apartmentId));
    } catch (err) {
      console.error('Error removing favorite:', err);
      alert('Failed to remove favorite. Please try again.');
    }
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
          <div className="text-6xl mb-4">💙</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Save Your Favorite Apartments
          </h2>
          <p className="text-gray-600 mb-6">
            Sign in to save apartments and access them anytime, anywhere.
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

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md w-full">
          <p className="text-red-700">{error}</p>
          <button
            onClick={fetchFavorites}
            className="mt-4 text-red-600 hover:text-red-700 font-medium"
          >
            Try Again
          </button>
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
                My Favorites
              </h1>
              <p className="text-gray-600">
                {favorites.length} {favorites.length === 1 ? 'apartment' : 'apartments'} saved {favorites.length >= 25 && <span className="text-orange-600 font-semibold">(Max: 25)</span>}
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
        {favorites.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <div className="text-6xl mb-4">🏠</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              No saved apartments yet
            </h2>
            <p className="text-gray-600 mb-6">
              Start browsing and click the heart icon on apartments you like
            </p>
            <Link
              to="/"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Browse Apartments
            </Link>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {favorites.map((apartment) => (
              <div
                key={apartment.id}
                className="bg-white rounded-lg shadow-sm hover:shadow-lg transition-shadow overflow-hidden group"
              >
                {/* Image */}
                <div 
                  className="relative h-48 overflow-hidden cursor-pointer"
                  onClick={() => setSelectedApartment(apartment)}
                >
                  <img
                    src={apartment.images && apartment.images[0] ? apartment.images[0] : 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&h=600&fit=crop'}
                    alt={apartment.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  
                  {/* Remove button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (window.confirm('Remove this apartment from favorites?')) {
                        handleRemoveFavorite(apartment.id);
                      }
                    }}
                    className="absolute top-3 right-3 bg-white rounded-full p-2 shadow-lg hover:bg-red-50 transition-colors z-10"
                    title="Remove from favorites"
                  >
                    <svg className="w-6 h-6 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                    </svg>
                  </button>
                  
                  {/* NO FEE badge */}
                  <div className="absolute top-3 left-3">
                    <span className="bg-orange-500 text-white px-2 py-1 rounded-full text-xs font-semibold">
                      NO FEE
                    </span>
                  </div>
                </div>

                {/* Details */}
                <div className="p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-semibold text-lg text-gray-800 line-clamp-1">
                        {apartment.bedrooms === 0 ? 'Studio' : `${apartment.bedrooms}BR`} in {apartment.neighborhood || 'NYC'}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {apartment.neighborhood}, {apartment.borough}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-gray-900">
                        ${apartment.price?.toLocaleString()}
                      </div>
                      <div className="text-xs text-gray-500">/month</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                    {apartment.bedrooms !== undefined && (
                      <span>{apartment.bedrooms === 0 ? 'Studio' : `${apartment.bedrooms} bed`}</span>
                    )}
                    {apartment.bathrooms && (
                      <span>{parseInt(apartment.bathrooms)} bath</span>
                    )}
                    {apartment.sqft && (
                      <span>{apartment.sqft} sqft</span>
                    )}
                  </div>

                  <button
                    onClick={() => setSelectedApartment(apartment)}
                    className="w-full bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

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

export default FavoritesPage;
