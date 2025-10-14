import React, { useState, useEffect } from 'react';

const VisitorTracker = () => {
  const [stats, setStats] = useState({
    todayVisitors: 0,
    totalVisitors: 0,
    currentOnline: 0,
    topPages: [],
    recentVisitors: [],
    loading: true
  });

  useEffect(() => {
    fetchVisitorStats();
    const interval = setInterval(fetchVisitorStats, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchVisitorStats = async () => {
    try {
      const API_URL = process.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API_URL}/api/analytics/stats`);
      
      if (response.ok) {
        const data = await response.json();
        setStats(prev => ({...prev, ...data, loading: false}));
      }
    } catch (error) {
      console.error('Error fetching visitor stats:', error);
      setStats(prev => ({...prev, loading: false}));
    }
  };

  const trackVisit = async () => {
    try {
      const API_URL = process.env.REACT_APP_BACKEND_URL;
      
      // Get visitor info
      const visitorData = {
        page: window.location.pathname,
        referrer: document.referrer || 'direct',
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString(),
        sessionId: getSessionId(),
        fingerprint: await generateFingerprint()
      };

      await fetch(`${API_URL}/api/analytics/visit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(visitorData)
      });

      // Update local stats immediately
      setStats(prev => ({
        ...prev,
        todayVisitors: prev.todayVisitors + 1,
        totalVisitors: prev.totalVisitors + 1,
        currentOnline: prev.currentOnline + 1
      }));

    } catch (error) {
      console.error('Error tracking visit:', error);
    }
  };

  const getSessionId = () => {
    let sessionId = sessionStorage.getItem('visitor_session_id');
    if (!sessionId) {
      sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      sessionStorage.setItem('visitor_session_id', sessionId);
    }
    return sessionId;
  };

  const generateFingerprint = async () => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillText('NoFeePlaces visitor tracking', 2, 2);
    
    const fingerprint = {
      screen: `${screen.width}x${screen.height}`,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      language: navigator.language,
      platform: navigator.platform,
      canvas: canvas.toDataURL().slice(-50), // Last 50 chars of canvas fingerprint
      cookieEnabled: navigator.cookieEnabled,
      doNotTrack: navigator.doNotTrack
    };
    
    return btoa(JSON.stringify(fingerprint)).slice(-20);
  };

  // Track visit on component mount
  useEffect(() => {
    trackVisit();
  }, []);

  if (!window.location.search.includes('admin=true')) {
    return null; // Only show for admin users
  }

  return (
    <div className="fixed bottom-4 right-4 bg-white shadow-lg rounded-lg p-4 max-w-sm z-50 border border-gray-200">
      <div className="text-sm font-semibold text-gray-800 mb-2">
        📊 Live Visitor Stats
      </div>
      
      {stats.loading ? (
        <div className="text-xs text-gray-500">Loading...</div>
      ) : (
        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-600">Today:</span>
            <span className="font-medium text-blue-600">{stats.todayVisitors}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Total:</span>
            <span className="font-medium text-green-600">{stats.totalVisitors}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Online:</span>
            <span className="font-medium text-orange-600">{stats.currentOnline}</span>
          </div>
          
          {stats.topPages.length > 0 && (
            <div className="mt-3 pt-2 border-t border-gray-200">
              <div className="text-xs font-medium text-gray-700 mb-1">Top Pages:</div>
              {stats.topPages.slice(0, 3).map((page, index) => (
                <div key={index} className="text-xs text-gray-600 truncate">
                  {page.page} ({page.count})
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      
      <button 
        onClick={fetchVisitorStats}
        className="text-xs text-blue-500 hover:text-blue-700 mt-2"
      >
        🔄 Refresh
      </button>
    </div>
  );
};

export default VisitorTracker;