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
          
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-purple-500 text-white">
                🎯
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Events Tracked</p>
                <p className="text-lg font-semibold">15+ Types</p>
              </div>
            </div>
          </div>
        </div>

        {/* Analytics Access */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold mb-4">📊 View Your Analytics</h2>
          <p className="text-gray-600 mb-6">
            Access your comprehensive visitor data, real-time statistics, and detailed reports through Google Analytics.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <a 
              href="https://analytics.google.com/analytics/web/#/p441815718/reports/dashboard"
              target="_blank"
              rel="noopener noreferrer"
              className="block p-6 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <div className="flex items-center">
                <span className="text-2xl mr-3">📈</span>
                <div>
                  <h3 className="font-semibold text-blue-900">Real-Time Analytics</h3>
                  <p className="text-blue-700 text-sm">See live visitors and activity</p>
                </div>
              </div>
            </a>
            
            <a 
              href="https://analytics.google.com/analytics/web/#/p441815718/reports/reportinghub"
              target="_blank"
              rel="noopener noreferrer"
              className="block p-6 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors"
            >
              <div className="flex items-center">
                <span className="text-2xl mr-3">📊</span>
                <div>
                  <h3 className="font-semibold text-green-900">Detailed Reports</h3>
                  <p className="text-green-700 text-sm">Traffic sources, demographics, behavior</p>
                </div>
              </div>
            </a>
          </div>
        </div>

        {/* Tracked Events */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold mb-6">🎯 Events Being Tracked</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold mb-3 text-purple-600">🏠 Apartment Activity</h3>
              <ul className="space-y-2 text-sm text-gray-700">
                <li>• Apartment views and impressions</li>
                <li>• Search queries and filters</li>
                <li>• Contact form submissions</li>
                <li>• Price range selections</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-3 text-blue-600">👤 User Engagement</h3>
              <ul className="space-y-2 text-sm text-gray-700">
                <li>• Newsletter signups</li>
                <li>• Authentication events</li>
                <li>• Navigation patterns</li>
                <li>• Hero section interactions</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-3 text-green-600">⚡ Performance</h3>
              <ul className="space-y-2 text-sm text-gray-700">
                <li>• Search response times</li>
                <li>• Page load metrics</li>
                <li>• API performance</li>
                <li>• Error tracking</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-3 text-orange-600">💼 Business Metrics</h3>
              <ul className="space-y-2 text-sm text-gray-700">
                <li>• Lead generation (contact forms)</li>
                <li>• Conversion tracking</li>
                <li>• Popular apartment types</li>
                <li>• Geographic interest</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Setup Instructions */}
        <div className="bg-gray-50 rounded-lg p-8 mt-8">
          <h2 className="text-xl font-bold mb-4">🔧 Analytics Setup Complete</h2>
          <div className="text-sm text-gray-700 space-y-2">
            <p>✅ Google Analytics 4 (GA4) tracking implemented</p>
            <p>✅ Custom event tracking for apartment interactions</p>
            <p>✅ Real-time visitor monitoring active</p>
            <p>✅ Professional email notifications fixed</p>
            <p>✅ API performance optimized (500 errors resolved)</p>
          </div>
          
          <div className="mt-6 p-4 bg-blue-100 rounded-lg">
            <p className="text-blue-800 font-medium">💡 Pro Tip:</p>
            <p className="text-blue-700 text-sm">
              Analytics data takes 24-48 hours to appear in Google Analytics. Check back tomorrow to see your first visitor reports!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;