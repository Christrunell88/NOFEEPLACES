/**
 * Advanced Analytics Dashboard for NoFeePlaces.com
 * Real-time visitor tracking and comprehensive analytics
 */

import React, { useState, useEffect } from 'react';

export const AnalyticsDashboard = () => {
  const [stats, setStats] = useState({
    todayVisitors: 0,
    todayUniqueVisitors: 0,
    totalVisitors: 0,
    currentOnline: 0,
    topPages: [],
    recentVisitors: [],
    weeklyTrend: [],
    trafficSources: [],
    browserStats: [],
    loading: true,
    last_updated: null
  });

  const [autoRefresh, setAutoRefresh] = useState(true);
  
  const gaTrackingId = 'G-XMDGXKJJ8M';

  useEffect(() => {
    fetchStats();
    
    let interval;
    if (autoRefresh) {
      interval = setInterval(fetchStats, 30000); // Auto-refresh every 30 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const fetchStats = async () => {
    try {
      const API_URL = process.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API_URL}/api/analytics/stats`);
      
      if (response.ok) {
        const data = await response.json();
        setStats(prev => ({...prev, ...data, loading: false}));
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setStats(prev => ({
        ...prev, 
        loading: false,
        error: `Failed to load analytics: ${error.message}`
      }));
    }
  };
  
  // Check access permissions  
  const hasAccess = window.location.search.includes('admin=true') || 
                   window.location.pathname.includes('/admin') ||
                   localStorage.getItem('admin_access') === 'true';

  if (!hasAccess) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-800 mb-4">Access Restricted</h1>
          <p className="text-gray-600">Add ?admin=true to the URL to access analytics</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">NoFeePlaces Analytics</h1>
              <p className="text-gray-600 mt-2">Real-time website analytics and visitor tracking</p>
            </div>
            <div className="flex items-center space-x-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-600">Auto-refresh</span>
              </label>
              <button
                onClick={fetchStats}
                className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm"
              >
                🔄 Refresh
              </button>
            </div>
          </div>
          {stats.last_updated && (
            <p className="text-xs text-gray-500 mt-2">
              Last updated: {new Date(stats.last_updated).toLocaleString()}
            </p>
          )}
        </div>

        {stats.loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-xl text-gray-600">Loading analytics...</div>
          </div>
        ) : stats.error ? (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <strong>Error:</strong> {stats.error}
            <div className="mt-2 text-sm">
              <p>Google Analytics ID: {gaTrackingId} ✅</p>
              <p>Make sure backend analytics service is running</p>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-600">Today's Visitors</p>
                    <p className="text-2xl font-bold text-blue-600">{stats.todayVisitors}</p>
                    {stats.todayUniqueVisitors !== undefined && (
                      <p className="text-xs text-gray-500">{stats.todayUniqueVisitors} unique</p>
                    )}
                  </div>
                  <div className="text-blue-500 text-2xl">👥</div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-600">Total Visitors</p>
                    <p className="text-2xl font-bold text-green-600">{stats.totalVisitors}</p>
                  </div>
                  <div className="text-green-500 text-2xl">📈</div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-600">Currently Online</p>
                    <p className="text-2xl font-bold text-orange-600">{stats.currentOnline}</p>
                    <p className="text-xs text-gray-500">last 5 minutes</p>
                  </div>
                  <div className="text-orange-500 text-2xl">🟢</div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-600">GA4 Status</p>
                    <p className="text-lg font-bold text-purple-600">Active</p>
                    <p className="text-xs text-gray-500">{gaTrackingId}</p>
                  </div>
                  <div className="text-purple-500 text-2xl">⚡</div>
                </div>
              </div>
            </div>

            {/* Top Pages and Recent Visitors */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">📄 Top Pages Today</h2>
                {stats.topPages.length > 0 ? (
                  <div className="space-y-3">
                    {stats.topPages.map((page, index) => (
                      <div key={index} className="flex justify-between items-center">
                        <span className="text-sm text-gray-600 truncate flex-1 mr-2">
                          {page.page === '/' ? 'Homepage' : page.page}
                        </span>
                        <span className="text-sm font-medium text-blue-600">{page.count} views</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No page data available yet</p>
                )}
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">🕒 Recent Activity</h2>
                {stats.recentVisitors.length > 0 ? (
                  <div className="space-y-3">
                    {stats.recentVisitors.slice(0, 8).map((visitor, index) => (
                      <div key={index} className="text-sm">
                        <div className="flex justify-between items-start">
                          <span className="text-gray-600 truncate flex-1">
                            {visitor.page === '/' ? 'Homepage' : visitor.page}
                          </span>
                          <span className="text-xs text-gray-400 ml-2">
                            {new Date(visitor.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="text-xs text-gray-400">
                          from {visitor.referrer} • {visitor.browser}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">Waiting for visitor data...</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalyticsDashboard;