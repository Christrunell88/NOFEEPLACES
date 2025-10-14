/**
 * Landlord Listing Management Components
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

// Add New Listing Component
export const AddListing = () => {
  const { landlordId } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    address: '',
    neighborhood: '',
    borough: 'Manhattan',
    price: '',
    bedrooms: 1,
    bathrooms: 1,
    square_feet: '',
    amenities: [],
    available_date: '',
    lease_terms: '12 months minimum',
    pet_policy: 'No pets',
    utilities_included: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/api/landlord/listings/submit?landlord_id=${landlordId}`, formData);
      
      if (response.data) {
        setSuccess(true);
        setTimeout(() => {
          navigate(`/landlord/dashboard/${landlordId}`);
        }, 2000);
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to submit listing');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'price' || name === 'bedrooms' || name === 'bathrooms' || name === 'square_feet' 
        ? (value === '' ? '' : Number(value)) 
        : value
    }));
  };

  const handleAmenityChange = (amenity) => {
    setFormData(prev => ({
      ...prev,
      amenities: prev.amenities.includes(amenity)
        ? prev.amenities.filter(a => a !== amenity)
        : [...prev.amenities, amenity]
    }));
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <div className="text-green-500 text-6xl mb-4">✅</div>
          <h2 className="text-2xl font-bold mb-2">Listing Added Successfully!</h2>
          <p className="text-gray-600">Your apartment listing is now live on NoFeePlaces.com</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold">Add New Listing</h1>
            <button
              onClick={() => navigate(`/landlord/dashboard/${landlordId}`)}
              className="text-gray-600 hover:text-gray-800"
            >
              ← Back to Dashboard
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        <div className="bg-white rounded-lg shadow p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Listing Title *
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  required
                  placeholder="e.g., Modern 2BR in Midtown - No Fee"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Monthly Rent *
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-2 text-gray-500">$</span>
                  <input
                    type="number"
                    name="price"
                    value={formData.price}
                    onChange={handleChange}
                    required
                    placeholder="3500"
                    className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
                  />
                </div>
              </div>
            </div>

            {/* Address */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Address *
              </label>
              <input
                type="text"
                name="address"
                value={formData.address}
                onChange={handleChange}
                required
                placeholder="123 Main Street, New York, NY 10001"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
              />
            </div>

            {/* Location Details */}
            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Neighborhood *
                </label>
                <input
                  type="text"
                  name="neighborhood"
                  value={formData.neighborhood}
                  onChange={handleChange}
                  required
                  placeholder="Midtown"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Borough *
                </label>
                <select
                  name="borough"
                  value={formData.borough}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="Manhattan">Manhattan</option>
                  <option value="Brooklyn">Brooklyn</option>
                  <option value="Queens">Queens</option>
                  <option value="Bronx">Bronx</option>
                  <option value="Staten Island">Staten Island</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Available Date *
                </label>
                <input
                  type="date"
                  name="available_date"
                  value={formData.available_date}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
                />
              </div>
            </div>

            {/* Property Details */}
            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Bedrooms *
                </label>
                <select
                  name="bedrooms"
                  value={formData.bedrooms}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value={0}>Studio</option>
                  <option value={1}>1 Bedroom</option>
                  <option value={2}>2 Bedrooms</option>
                  <option value={3}>3 Bedrooms</option>
                  <option value={4}>4+ Bedrooms</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Bathrooms *
                </label>
                <select
                  name="bathrooms"
                  value={formData.bathrooms}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value={1}>1 Bathroom</option>
                  <option value={1.5}>1.5 Bathrooms</option>
                  <option value={2}>2 Bathrooms</option>
                  <option value={2.5}>2.5 Bathrooms</option>
                  <option value={3}>3+ Bathrooms</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Square Feet
                </label>
                <input
                  type="number"
                  name="square_feet"
                  value={formData.square_feet}
                  onChange={handleChange}
                  placeholder="800"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
                />
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description *
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                required
                rows={4}
                placeholder="Describe your apartment's features, location benefits, and what makes it special..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
              />
            </div>

            {/* Amenities */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Amenities
              </label>
              <div className="grid md:grid-cols-3 gap-2">
                {['Doorman', 'Elevator', 'Gym', 'Rooftop', 'Laundry', 'Dishwasher', 'Air Conditioning', 'Hardwood Floors', 'Pet Friendly', 'Parking', 'Balcony', 'In-Unit Washer/Dryer'].map(amenity => (
                  <label key={amenity} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={formData.amenities.includes(amenity)}
                      onChange={() => handleAmenityChange(amenity)}
                      className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                    />
                    <span className="text-sm">{amenity}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Terms */}
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Lease Terms
                </label>
                <select
                  name="lease_terms"
                  value={formData.lease_terms}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="12 months minimum">12 months minimum</option>
                  <option value="6 months minimum">6 months minimum</option>
                  <option value="Month to month">Month to month</option>
                  <option value="Flexible terms">Flexible terms</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Pet Policy
                </label>
                <select
                  name="pet_policy"
                  value={formData.pet_policy}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="No pets">No pets</option>
                  <option value="Cats allowed">Cats allowed</option>
                  <option value="Small dogs allowed">Small dogs allowed</option>
                  <option value="All pets welcome">All pets welcome</option>
                  <option value="Case by case">Case by case</option>
                </select>
              </div>
            </div>

            {/* Submit */}
            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={() => navigate(`/landlord/dashboard/${landlordId}`)}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 transition-colors"
              >
                {loading ? 'Adding Listing...' : 'Add Listing'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// View All Listings Component
export const ViewListings = () => {
  const { landlordId } = useParams();
  const navigate = useNavigate();
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchListings();
  }, [landlordId]);

  const fetchListings = async () => {
    try {
      const response = await axios.get(`${API}/api/landlord/listings/${landlordId}`);
      setListings(response.data.listings || []);
    } catch (error) {
      setError('Failed to load listings');
      console.error('Error fetching listings:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleListingStatus = async (listingId, currentStatus) => {
    try {
      await axios.patch(`${API}/api/landlord/listings/${listingId}/status`, {
        available: !currentStatus
      });
      fetchListings(); // Refresh the list
    } catch (error) {
      console.error('Error toggling status:', error);
    }
  };

  if (loading) return <div className="p-8">Loading listings...</div>;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Your Listings</h1>
              <p className="text-gray-600">{listings.length} total listings</p>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={() => navigate(`/landlord/dashboard/${landlordId}`)}
                className="text-gray-600 hover:text-gray-800"
              >
                ← Back to Dashboard
              </button>
              <button
                onClick={() => navigate(`/landlord/add-listing/${landlordId}`)}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
              >
                + Add New Listing
              </button>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        <div className="space-y-4">
          {listings.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-8 text-center">
              <div className="text-gray-400 text-4xl mb-4">🏠</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No listings yet</h3>
              <p className="text-gray-600 mb-4">Start by adding your first apartment listing</p>
              <button
                onClick={() => navigate(`/landlord/add-listing/${landlordId}`)}
                className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors"
              >
                Add Your First Listing
              </button>
            </div>
          ) : (
            listings.map((listing) => (
              <div key={listing.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold">{listing.title}</h3>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        listing.available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {listing.available ? 'Active' : 'Inactive'}
                      </span>
                      {listing.featured && (
                        <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-medium">
                          Featured
                        </span>
                      )}
                    </div>
                    <p className="text-gray-600 mb-2">{listing.address}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>${listing.price?.toLocaleString()}/month</span>
                      <span>{listing.bedrooms === 0 ? 'Studio' : `${listing.bedrooms} BR`}</span>
                      <span>{listing.bathrooms} BA</span>
                      {listing.square_feet && <span>{listing.square_feet} sq ft</span>}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 ml-4">
                    <div className="text-center">
                      <div className="text-lg font-bold text-blue-600">{listing.view_count || 0}</div>
                      <div className="text-xs text-gray-500">Views</div>
                    </div>
                    <div className="text-center ml-4">
                      <div className="text-lg font-bold text-green-600">{listing.inquiry_count || 0}</div>
                      <div className="text-xs text-gray-500">Inquiries</div>
                    </div>
                    <button
                      onClick={() => toggleListingStatus(listing.id, listing.available)}
                      className={`px-3 py-1 rounded text-sm font-medium ml-4 ${
                        listing.available 
                          ? 'bg-red-100 text-red-700 hover:bg-red-200'
                          : 'bg-green-100 text-green-700 hover:bg-green-200'
                      } transition-colors`}
                    >
                      {listing.available ? 'Deactivate' : 'Activate'}
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default {
  AddListing,
  ViewListings
};