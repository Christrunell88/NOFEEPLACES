import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export const VisitorAnalytics = () => {
  const [visitorData, setVisitorData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, today, week, month
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('timestamp'); // timestamp, page, ip
  const [sortOrder, setSortOrder] = useState('desc');

  useEffect(() => {
    fetchVisitorAnalytics();
  }, [filter, sortBy, sortOrder]);

  const fetchVisitorAnalytics = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('adminToken');
      const response = await axios.get(`${API}/api/admin/visitor-analytics`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { filter, sortBy, sortOrder }
      });
      
      if (response.data) {
        setVisitorData(response.data.visitors || []);
      }
    } catch (error) {
      console.error('Error fetching visitor analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDuration = (start, end) => {
    if (!start || !end) return 'N/A';
    const duration = new Date(end) - new Date(start);
    const minutes = Math.floor(duration / 60000);
    const seconds = Math.floor((duration % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
  };

  const getBrowserIcon = (browserInfo) => {
    if (!browserInfo || !browserInfo.browser) return '🌐';
    const browser = browserInfo.browser.toLowerCase();
    if (browser.includes('chrome')) return '🟢';
    if (browser.includes('safari')) return '🔵';
    if (browser.includes('firefox')) return '🟠';
    if (browser.includes('edge')) return '🔷';
    return '🌐';
  };

  const getDeviceIcon = (browserInfo) => {
    if (!browserInfo || !browserInfo.device) return '💻';
    const device = browserInfo.device.toLowerCase();
    if (device.includes('mobile')) return '📱';
    if (device.includes('tablet')) return '📱';
    return '💻';
  };

  const filteredData = visitorData.filter(visitor => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      (visitor.ip_address && visitor.ip_address.toLowerCase().includes(search)) ||
      (visitor.page && visitor.page.toLowerCase().includes(search)) ||
      (visitor.referrer && visitor.referrer.toLowerCase().includes(search))
    );
  });

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header & Filters */}
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Visitor Analytics</h2>
            <p className="text-gray-600 mt-1">{filteredData.length} total visitor sessions</p>
          </div>
          
          <button
            onClick={fetchVisitorAnalytics}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
          >
            <span>🔄</span> Refresh
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4">
          {/* Time Filter */}
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filter === 'all'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              All Time
            </button>
            <button
              onClick={() => setFilter('today')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filter === 'today'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Today
            </button>
            <button
              onClick={() => setFilter('week')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filter === 'week'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              This Week
            </button>
          </div>

          {/* Search */}
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search by IP, page, or referrer..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          {/* Sort */}
          <select
            value={`${sortBy}-${sortOrder}`}
            onChange={(e) => {
              const [field, order] = e.target.value.split('-');
              setSortBy(field);
              setSortOrder(order);
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
          >
            <option value="timestamp-desc">Latest First</option>
            <option value="timestamp-asc">Oldest First</option>
            <option value="page-asc">Page A-Z</option>
            <option value="ip-asc">IP Address</option>
          </select>
        </div>
      </div>

      {/* Visitor Table */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  IP Address
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Page
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Referrer
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Browser
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Device
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  OS
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredData.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-8 text-center text-gray-500">
                    No visitor data found
                  </td>
                </tr>
              ) : (
                filteredData.map((visitor, index) => (
                  <tr key={visitor.session_id || index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatTimestamp(visitor.timestamp)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-600">
                      {visitor.ip_address || 'N/A'}
                      {visitor.is_unique && (
                        <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                          New
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <div className="max-w-xs truncate" title={visitor.page}>
                        {visitor.page || '/'}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      <div className="max-w-xs truncate" title={visitor.referrer}>
                        {visitor.referrer_domain || visitor.referrer || 'Direct'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {getBrowserIcon(visitor.browser_info)} {visitor.browser_info?.browser || 'Unknown'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {getDeviceIcon(visitor.browser_info)} {visitor.browser_info?.device || 'Unknown'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {visitor.browser_info?.os || 'Unknown'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="text-sm font-medium text-gray-600 mb-2">Total Sessions</div>
          <div className="text-3xl font-bold text-gray-900">{filteredData.length}</div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="text-sm font-medium text-gray-600 mb-2">Unique Visitors</div>
          <div className="text-3xl font-bold text-gray-900">
            {filteredData.filter(v => v.is_unique).length}
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="text-sm font-medium text-gray-600 mb-2">Top Browser</div>
          <div className="text-xl font-bold text-gray-900">
            {(() => {
              const browsers = {};
              filteredData.forEach(v => {
                const browser = v.browser_info?.browser || 'Unknown';
                browsers[browser] = (browsers[browser] || 0) + 1;
              });
              const top = Object.entries(browsers).sort((a, b) => b[1] - a[1])[0];
              return top ? `${top[0]} (${top[1]})` : 'N/A';
            })()}
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="text-sm font-medium text-gray-600 mb-2">Top Device</div>
          <div className="text-xl font-bold text-gray-900">
            {(() => {
              const devices = {};
              filteredData.forEach(v => {
                const device = v.browser_info?.device || 'Unknown';
                devices[device] = (devices[device] || 0) + 1;
              });
              const top = Object.entries(devices).sort((a, b) => b[1] - a[1])[0];
              return top ? `${top[0]} (${top[1]})` : 'N/A';
            })()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VisitorAnalytics;
