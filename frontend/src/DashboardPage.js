import React, { useState, useEffect } from 'react';
import { useAuth } from './RobustAuth';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { ApartmentDetailsModal } from './components';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const DashboardPage = () => {
  const { isAuthenticated, user, loading: authLoading } = useAuth();
  const [dashboardData, setDashboardData] = useState({
    favorites: [],
    savedSearches: [],
    upcomingShowings: [],
    stats: {
      favoritesCount: 0,
      savedSearchesCount: 0,
      showingsCount: 0
    }
  });
  const [loading, setLoading] = useState(true);
  const [selectedApartment, setSelectedApartment] = useState(null);

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      fetchDashboardData();
    } else if (!authLoading && !isAuthenticated) {
      setLoading(false);
    }
  }, [isAuthenticated, authLoading]);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { 'Authorization': `Bearer ${token}` };

      // Fetch all dashboard data in parallel
      const [favoritesRes, searchesRes] = await Promise.all([
        axios.get(`${API}/favorites`, { headers }),
        axios.get(`${API}/saved-searches`, { headers })
      ]);

      setDashboardData({
        favorites: favoritesRes.data.favorites?.slice(0, 6) || [],
        savedSearches: searchesRes.data.saved_searches?.slice(0, 3) || [],
        upcomingShowings: [], // TODO: Add showings endpoint
        stats: {
          favoritesCount: favoritesRes.data.total || 0,
          savedSearchesCount: searchesRes.data.total || 0,
          showingsCount: 0
        }
      });

      setLoading(false);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setLoading(false);
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
          <div className="text-6xl mb-4">🏠</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Your Personal Dashboard
          </h2>
          <p className="text-gray-600 mb-6">
            Sign in to access your favorites, saved searches, and scheduled showings.
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
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold mb-2">
            Welcome back, {user?.full_name || user?.email?.split('@')[0]}!
          </h1>
          <p className="text-blue-100">
            Here's your apartment search activity
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Link
            to="/favorites"
            className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 border-l-4 border-red-500"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm mb-1">Saved Apartments</p>
                <p className="text-3xl font-bold text-gray-900">
                  {dashboardData.stats.favoritesCount}
                </p>
                {dashboardData.stats.favoritesCount >= 25 && (
                  <p className="text-xs text-orange-600 mt-1">Max reached</p>
                )}
              </div>
              <div className="text-red-500">
                <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
          </Link>

          <Link
            to="/saved-searches"
            className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 border-l-4 border-blue-500"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm mb-1">Saved Searches</p>
                <p className="text-3xl font-bold text-gray-900">
                  {dashboardData.stats.savedSearchesCount}
                </p>
              </div>
              <div className="text-blue-500">
                <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
              </div>
            </div>
          </Link>

          <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm mb-1">Upcoming Showings</p>
                <p className="text-3xl font-bold text-gray-900">
                  {dashboardData.stats.showingsCount}
                </p>
              </div>
              <div className="text-green-500">
                <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <Link
              to="/"
              className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <div>
                <p className="font-semibold text-gray-900">Browse Apartments</p>
                <p className="text-sm text-gray-600">Find your next home</p>
              </div>
            </Link>

            <Link
              to="/list"
              className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <div>
                <p className="font-semibold text-gray-900">List an Apartment</p>
                <p className="text-sm text-gray-600">Sublet or transfer lease</p>
              </div>
            </Link>

            <Link
              to="/favorites"
              className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <svg className="w-8 h-8 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="font-semibold text-gray-900">View Favorites</p>
                <p className="text-sm text-gray-600">{dashboardData.stats.favoritesCount} saved</p>
              </div>
            </Link>
          </div>
        </div>

        {/* Saved Apartments Preview */}
        {dashboardData.favorites.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Saved Apartments</h2>
              <Link
                to="/favorites"
                className="text-blue-600 hover:text-blue-700 font-medium text-sm"
              >
                View All ({dashboardData.stats.favoritesCount})
              </Link>
            </div>

            <div className="grid md:grid-cols-3 gap-4">
              {dashboardData.favorites.map((apartment) => (
                <div
                  key={apartment.id}
                  onClick={() => setSelectedApartment(apartment)}
                  className="border rounded-lg overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
                >
                  <div className="h-32 overflow-hidden">
                    <img
                      src={apartment.images?.[0] || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400'}
                      alt={apartment.title}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="p-3">
                    <p className="font-semibold text-gray-900 text-sm mb-1">
                      {apartment.bedrooms === 0 ? 'Studio' : `${apartment.bedrooms}BR`} in {apartment.neighborhood}
                    </p>
                    <p className="text-lg font-bold text-blue-600">
                      ${apartment.price?.toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Saved Searches */}
        {dashboardData.savedSearches.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Saved Searches</h2>
              <Link
                to="/saved-searches"
                className="text-blue-600 hover:text-blue-700 font-medium text-sm"
              >
                Manage All ({dashboardData.stats.savedSearchesCount})
              </Link>
            </div>

            <div className="space-y-3">
              {dashboardData.savedSearches.map((search) => (
                <div
                  key={search.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div>
                    <p className="font-semibold text-gray-900">{search.search_name}</p>
                    <p className="text-sm text-gray-600">
                      {search.email_frequency === 'weekly' ? 'Weekly alerts enabled' : 'Alerts disabled'}
                    </p>
                  </div>
                  {search.new_listings_count > 0 && (
                    <div className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm font-semibold">
                      {search.new_listings_count} new
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {dashboardData.favorites.length === 0 && dashboardData.savedSearches.length === 0 && (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <div className="text-6xl mb-4">🚀</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              Start Your Apartment Search
            </h2>
            <p className="text-gray-600 mb-6">
              Browse no-fee apartments, save your favorites, and set up search alerts
            </p>
            <Link
              to="/"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Browse Apartments
            </Link>
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

export default DashboardPage;
