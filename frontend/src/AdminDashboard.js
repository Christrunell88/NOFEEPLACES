import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import VisitorAnalytics from './VisitorAnalytics';

const API = process.env.REACT_APP_BACKEND_URL || '';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState(null);
  const [apartments, setApartments] = useState([]);
  const [users, setUsers] = useState([]);
  const [feedback, setFeedback] = useState([]);
  const [newsletter, setNewsletter] = useState([]);
  const [editingApartment, setEditingApartment] = useState(null);
  
  // New listing form state
  const [uploadedImages, setUploadedImages] = useState([]);
  const [uploadingImages, setUploadingImages] = useState(false);
  const [creatingListing, setCreatingListing] = useState(false);
  const [newListing, setNewListing] = useState({
    title: '',
    address: '',
    neighborhood: '',
    borough: '',
    price: '',
    bedrooms: '',
    bathrooms: '',
    sqft: '',
    description: '',
    available: true
  });
  
  const navigate = useNavigate();

  // Check admin authentication
  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    if (!token) {
      navigate('/admin');
    } else {
      loadAnalytics();
    }
  }, [navigate]);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('admin_token');
    return {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    };
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_email');
    navigate('/admin');
  };

  const loadAnalytics = async () => {
    try {
      const response = await axios.get(`${API}/api/admin/analytics`, getAuthHeaders());
      setAnalytics(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load analytics:', error);
      if (error.response?.status === 401) {
        handleLogout();
      }
    }
  };

  const loadApartments = async () => {
    try {
      const response = await axios.get(`${API}/api/admin/apartments?limit=100`, getAuthHeaders());
      setApartments(response.data.apartments);
    } catch (error) {
      console.error('Failed to load apartments:', error);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await axios.get(`${API}/api/admin/users?limit=100`, getAuthHeaders());
      setUsers(response.data.users);
    } catch (error) {
      console.error('Failed to load users:', error);
    }
  };

  const loadFeedback = async () => {
    try {
      const response = await axios.get(`${API}/api/admin/feedback?limit=50`, getAuthHeaders());
      setFeedback(response.data.feedback);
    } catch (error) {
      console.error('Failed to load feedback:', error);
    }
  };

  const loadNewsletter = async () => {
    try {
      const response = await axios.get(`${API}/api/admin/newsletter?limit=100`, getAuthHeaders());
      setNewsletter(response.data.subscribers);
    } catch (error) {
      console.error('Failed to load newsletter:', error);
    }
  };

  const handleDeleteApartment = async (apartmentId) => {
    if (!window.confirm('Are you sure you want to delete this apartment?')) {
      return;
    }

    try {
      await axios.delete(`${API}/api/admin/apartments/${apartmentId}`, getAuthHeaders());
      loadApartments();
      alert('Apartment deleted successfully');
    } catch (error) {
      console.error('Failed to delete apartment:', error);
      alert('Failed to delete apartment');
    }
  };

  const handleUpdateApartment = async (apartmentId, updates) => {
    try {
      await axios.put(`${API}/api/admin/apartments/${apartmentId}`, updates, getAuthHeaders());
      loadApartments();
      setEditingApartment(null);
      alert('Apartment updated successfully');
    } catch (error) {
      console.error('Failed to update apartment:', error);
      alert('Failed to update apartment');
    }
  };

  const handleImageUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    setUploadingImages(true);
    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      const token = localStorage.getItem('admin_token');
      const response = await axios.post(
        `${API}/api/admin/upload-images`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`
            // Don't set Content-Type - let axios set it with boundary
          }
        }
      );

      if (response.data.success) {
        setUploadedImages([...uploadedImages, ...response.data.image_urls]);
        alert(`${response.data.image_urls.length} images uploaded successfully!`);
      }
    } catch (error) {
      console.error('Image upload error:', error);
      alert(`Failed to upload images: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploadingImages(false);
    }
  };

  const handleRemoveImage = (indexToRemove) => {
    setUploadedImages(uploadedImages.filter((_, index) => index !== indexToRemove));
  };

  const handleCreateListing = async (e) => {
    e.preventDefault();
    
    if (uploadedImages.length === 0) {
      alert('Please upload at least one image');
      return;
    }

    setCreatingListing(true);
    try {
      const listingData = {
        ...newListing,
        images: uploadedImages,
        price: parseFloat(newListing.price),
        bedrooms: parseInt(newListing.bedrooms),
        bathrooms: parseFloat(newListing.bathrooms),
        sqft: newListing.sqft ? parseInt(newListing.sqft) : null
      };

      const response = await axios.post(
        `${API}/api/admin/create-listing`,
        listingData,
        getAuthHeaders()
      );

      if (response.data.success) {
        alert('Listing created successfully!');
        // Reset form
        setNewListing({
          title: '',
          address: '',
          neighborhood: '',
          borough: '',
          price: '',
          bedrooms: '',
          bathrooms: '',
          sqft: '',
          description: '',
          available: true
        });
        setUploadedImages([]);
        // Reload apartments
        loadApartments();
        // Switch to apartments tab
        setActiveTab('apartments');
      }
    } catch (error) {
      console.error('Create listing error:', error);
      alert('Failed to create listing. Please try again.');
    } finally {
      setCreatingListing(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'apartments' && apartments.length === 0) {
      loadApartments();
    } else if (activeTab === 'users' && users.length === 0) {
      loadUsers();
    } else if (activeTab === 'feedback' && feedback.length === 0) {
      loadFeedback();
    } else if (activeTab === 'newsletter' && newsletter.length === 0) {
      loadNewsletter();
    }
  }, [activeTab]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">NoFeePlaces Admin Dashboard</h1>
              <p className="text-purple-100 text-sm mt-1">
                👋 Welcome, {localStorage.getItem('admin_email')}
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => navigate('/')}
                className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition"
              >
                View Site
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-500 hover:bg-red-600 rounded-lg transition"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-1 overflow-x-auto">
            {['overview', 'apartments', 'add-listing', 'moderation', 'visitors', 'users', 'feedback', 'newsletter'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-4 font-medium text-sm whitespace-nowrap transition border-b-2 ${
                  activeTab === tab
                    ? 'border-purple-600 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Overview Tab */}
        {activeTab === 'overview' && analytics && (
          <div>
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Dashboard Overview</h2>
            
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500 font-medium">Total Apartments</p>
                    <p className="text-3xl font-bold text-gray-800 mt-1">
                      {analytics.stats.total_apartments}
                    </p>
                    <p className="text-sm text-green-600 mt-2">
                      {analytics.stats.available_apartments} available
                    </p>
                  </div>
                  <div className="bg-purple-100 rounded-full p-3">
                    <span className="text-3xl">🏠</span>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500 font-medium">Registered Users</p>
                    <p className="text-3xl font-bold text-gray-800 mt-1">
                      {analytics.stats.total_users}
                    </p>
                  </div>
                  <div className="bg-blue-100 rounded-full p-3">
                    <span className="text-3xl">👥</span>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500 font-medium">Total Visitors</p>
                    <p className="text-3xl font-bold text-gray-800 mt-1">
                      {analytics.stats.total_visitors}
                    </p>
                  </div>
                  <div className="bg-green-100 rounded-full p-3">
                    <span className="text-3xl">📊</span>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500 font-medium">Feedback</p>
                    <p className="text-3xl font-bold text-gray-800 mt-1">
                      {analytics.stats.total_feedback}
                    </p>
                  </div>
                  <div className="bg-yellow-100 rounded-full p-3">
                    <span className="text-3xl">💬</span>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500 font-medium">Newsletter</p>
                    <p className="text-3xl font-bold text-gray-800 mt-1">
                      {analytics.stats.total_newsletter_subscribers}
                    </p>
                  </div>
                  <div className="bg-pink-100 rounded-full p-3">
                    <span className="text-3xl">📧</span>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500 font-medium">Avg Price</p>
                    <p className="text-3xl font-bold text-gray-800 mt-1">
                      ${analytics.price_stats.average_price.toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500 mt-2">
                      ${analytics.price_stats.min_price.toLocaleString()} - ${analytics.price_stats.max_price.toLocaleString()}
                    </p>
                  </div>
                  <div className="bg-orange-100 rounded-full p-3">
                    <span className="text-3xl">💰</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
                <h3 className="text-lg font-bold text-gray-800 mb-4">Recent Users</h3>
                <div className="space-y-3">
                  {analytics.recent_activity.recent_users.slice(0, 5).map((user, idx) => (
                    <div key={idx} className="flex items-center justify-between py-2 border-b border-gray-100">
                      <div>
                        <p className="font-medium text-gray-800">{user.email}</p>
                        <p className="text-xs text-gray-500">{user.provider}</p>
                      </div>
                      <p className="text-xs text-gray-400">
                        {new Date(user.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
                <h3 className="text-lg font-bold text-gray-800 mb-4">Recent Feedback</h3>
                <div className="space-y-3">
                  {analytics.recent_activity.recent_feedback.slice(0, 5).map((fb, idx) => (
                    <div key={idx} className="flex items-center justify-between py-2 border-b border-gray-100">
                      <div>
                        <p className="font-medium text-gray-800">{fb.title}</p>
                        <p className="text-xs text-gray-500">{fb.type}</p>
                      </div>
                      <p className="text-xs text-gray-400">
                        {new Date(fb.timestamp).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Apartments Tab */}
        {activeTab === 'apartments' && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-800">Apartment Listings ({apartments.length})</h2>
              <button
                onClick={loadApartments}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
              >
                🔄 Refresh
              </button>
            </div>

            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Beds</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {apartments.map((apt) => (
                      <tr key={apt.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div className="text-sm font-medium text-gray-900">{apt.title}</div>
                          <div className="text-xs text-gray-500">{apt.id.slice(0, 8)}...</div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">
                          {apt.neighborhood}, {apt.borough}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                          ${apt.price?.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">
                          {apt.bedrooms === 0 ? 'Studio' : `${apt.bedrooms} BR`}
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                            apt.available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {apt.available ? 'Available' : 'Unavailable'}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm">
                          <div className="flex gap-2">
                            <button
                              onClick={() => window.open(`/apartment/${apt.id}`, '_blank')}
                              className="text-blue-600 hover:text-blue-800 font-medium"
                            >
                              View
                            </button>
                            <button
                              onClick={() => handleDeleteApartment(apt.id)}
                              className="text-red-600 hover:text-red-800 font-medium"
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Add Listing Tab */}
        {activeTab === 'add-listing' && (
          <div>
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Add New Apartment Listing</h2>

            <form onSubmit={handleCreateListing} className="space-y-6">
              {/* Image Upload Section */}
              <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
                <h3 className="text-lg font-bold text-gray-800 mb-4">📸 Upload Images</h3>
                
                <div className="mb-4">
                  <label className="block w-full">
                    <div className="border-2 border-dashed border-purple-300 rounded-lg p-8 text-center hover:border-purple-500 transition cursor-pointer">
                      <div className="text-purple-600 mb-2">
                        <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                      </div>
                      <p className="text-gray-600 font-medium mb-1">Click to upload images</p>
                      <p className="text-gray-400 text-sm">or drag and drop</p>
                      <p className="text-gray-400 text-xs mt-2">PNG, JPG, WEBP up to 10MB each</p>
                    </div>
                    <input
                      type="file"
                      multiple
                      accept="image/*"
                      onChange={handleImageUpload}
                      disabled={uploadingImages}
                      className="hidden"
                    />
                  </label>
                  {uploadingImages && (
                    <p className="text-purple-600 text-sm mt-2 text-center">Uploading images...</p>
                  )}
                </div>

                {/* Image Preview Grid */}
                {uploadedImages.length > 0 && (
                  <div>
                    <p className="text-sm text-gray-600 mb-3">Uploaded Images ({uploadedImages.length})</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {uploadedImages.map((imageUrl, index) => (
                        <div key={index} className="relative group">
                          <img
                            src={`${API}${imageUrl}`}
                            alt={`Upload ${index + 1}`}
                            className="w-full h-32 object-cover rounded-lg border border-gray-200"
                          />
                          <button
                            type="button"
                            onClick={() => handleRemoveImage(index)}
                            className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Listing Details Form */}
              <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
                <h3 className="text-lg font-bold text-gray-800 mb-4">📝 Listing Details</h3>

                <div className="grid md:grid-cols-2 gap-6">
                  {/* Title */}
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Listing Title *
                    </label>
                    <input
                      type="text"
                      required
                      value={newListing.title}
                      onChange={(e) => setNewListing({...newListing, title: e.target.value})}
                      placeholder="e.g., Studio at Mercedes House"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-gray-900 bg-white"
                    />
                  </div>

                  {/* Address */}
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Full Address *
                    </label>
                    <input
                      type="text"
                      required
                      value={newListing.address}
                      onChange={(e) => setNewListing({...newListing, address: e.target.value})}
                      placeholder="e.g., 550 W 54th St, New York, NY 10019"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-gray-900 bg-white"
                    />
                  </div>

                  {/* Neighborhood */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Neighborhood *
                    </label>
                    <input
                      type="text"
                      required
                      value={newListing.neighborhood}
                      onChange={(e) => setNewListing({...newListing, neighborhood: e.target.value})}
                      placeholder="e.g., Hell's Kitchen"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-gray-900 bg-white"
                    />
                  </div>

                  {/* Borough */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Borough *
                    </label>
                    <select
                      required
                      value={newListing.borough}
                      onChange={(e) => setNewListing({...newListing, borough: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-gray-900 bg-white"
                    >
                      <option value="">Select Borough</option>
                      <option value="Manhattan">Manhattan</option>
                      <option value="Brooklyn">Brooklyn</option>
                      <option value="Queens">Queens</option>
                      <option value="Bronx">Bronx</option>
                      <option value="Staten Island">Staten Island</option>
                    </select>
                  </div>

                  {/* Price */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Monthly Rent ($) *
                    </label>
                    <input
                      type="number"
                      required
                      value={newListing.price}
                      onChange={(e) => setNewListing({...newListing, price: e.target.value})}
                      placeholder="e.g., 2500"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-gray-900 bg-white"
                    />
                  </div>

                  {/* Bedrooms */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Bedrooms *
                    </label>
                    <select
                      required
                      value={newListing.bedrooms}
                      onChange={(e) => setNewListing({...newListing, bedrooms: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-gray-900 bg-white"
                    >
                      <option value="">Select</option>
                      <option value="0">Studio</option>
                      <option value="1">1 Bedroom</option>
                      <option value="2">2 Bedrooms</option>
                      <option value="3">3 Bedrooms</option>
                      <option value="4">4+ Bedrooms</option>
                    </select>
                  </div>

                  {/* Bathrooms */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Bathrooms *
                    </label>
                    <input
                      type="number"
                      step="0.5"
                      required
                      value={newListing.bathrooms}
                      onChange={(e) => setNewListing({...newListing, bathrooms: e.target.value})}
                      placeholder="e.g., 1 or 1.5"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-gray-900 bg-white"
                    />
                  </div>

                  {/* Square Feet */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Square Feet (optional)
                    </label>
                    <input
                      type="number"
                      value={newListing.sqft}
                      onChange={(e) => setNewListing({...newListing, sqft: e.target.value})}
                      placeholder="e.g., 650"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-gray-900 bg-white"
                    />
                  </div>

                  {/* Description */}
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description
                    </label>
                    <textarea
                      rows={4}
                      value={newListing.description}
                      onChange={(e) => setNewListing({...newListing, description: e.target.value})}
                      placeholder="Describe the apartment, amenities, location highlights..."
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-gray-900 bg-white"
                    />
                  </div>

                  {/* Available */}
                  <div className="md:col-span-2">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={newListing.available}
                        onChange={(e) => setNewListing({...newListing, available: e.target.checked})}
                        className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                      />
                      <span className="ml-2 text-sm font-medium text-gray-700">
                        Mark as Available for Rent
                      </span>
                    </label>
                  </div>
                </div>

                {/* Submit Button */}
                <div className="mt-6 flex gap-4">
                  <button
                    type="submit"
                    disabled={creatingListing || uploadedImages.length === 0}
                    className="flex-1 bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {creatingListing ? 'Creating Listing...' : '✨ Create Listing'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      if (window.confirm('Are you sure? All unsaved changes will be lost.')) {
                        setNewListing({
                          title: '',
                          address: '',
                          neighborhood: '',
                          borough: '',
                          price: '',
                          bedrooms: '',
                          bathrooms: '',
                          sqft: '',
                          description: '',
                          available: true
                        });
                        setUploadedImages([]);
                      }
                    }}
                    className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition"
                  >
                    Reset
                  </button>
                </div>
              </div>
            </form>
          </div>
        )}

        {/* Users Tab */}
        {/* Visitors Tab */}
        {activeTab === 'visitors' && (
          <VisitorAnalytics />
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-800">Registered Users ({users.length})</h2>
              <button
                onClick={loadUsers}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
              >
                🔄 Refresh
              </button>
            </div>

            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provider</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Joined</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {users.map((user) => (
                      <tr key={user.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm font-medium text-gray-900">
                          {user.email}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">
                          {user.full_name || '-'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-semibold">
                            {user.provider}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {new Date(user.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                            user.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {user.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Feedback Tab */}
        {activeTab === 'feedback' && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-800">User Feedback ({feedback.length})</h2>
              <button
                onClick={loadFeedback}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
              >
                🔄 Refresh
              </button>
            </div>

            <div className="space-y-4">
              {feedback.map((fb) => (
                <div key={fb.id} className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          fb.type === 'bug' ? 'bg-red-100 text-red-800' :
                          fb.type === 'feature' ? 'bg-blue-100 text-blue-800' :
                          fb.type === 'improvement' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {fb.type}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          fb.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                          fb.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {fb.priority} priority
                        </span>
                      </div>
                      <h3 className="text-lg font-bold text-gray-800">{fb.title}</h3>
                      <p className="text-gray-600 mt-2">{fb.description}</p>
                      <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                        <span>📧 {fb.email}</span>
                        <span>📍 {fb.page}</span>
                        <span>🕐 {new Date(fb.timestamp).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Newsletter Tab */}
        {activeTab === 'newsletter' && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-800">Newsletter Subscribers ({newsletter.length})</h2>
              <button
                onClick={loadNewsletter}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
              >
                🔄 Refresh
              </button>
            </div>

            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Source</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Subscribed</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {newsletter.map((sub) => (
                      <tr key={sub.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm font-medium text-gray-900">
                          {sub.email}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">
                          {sub.name || '-'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {sub.source || 'website'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {new Date(sub.subscribed_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                            sub.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {sub.is_active ? 'Active' : 'Unsubscribed'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
